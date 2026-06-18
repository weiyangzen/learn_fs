# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/umsch_mm_4_0_api_def.h

## Purpose

This header defines the host-driver-to-firmware API ABI for UMSCH MM 4.0, the micro-scheduler used for multimedia/video-processing queues. It describes fixed-size command frames, command opcodes, scheduling/logging enums, queue and hardware-resource payloads, completion-fence fields, and packed wire layouts consumed through a ring or command buffer shared with firmware. It is ABI-heavy and contains no function bodies.

## Important APIs, Types, and Constants

- Packing and frame sizing:
  - `#pragma pack(push, 4)` makes the command structures 4-byte packed for firmware ABI compatibility.
  - `UMSCH_API_VERSION = 1`.
  - `API_FRAME_SIZE_IN_DWORDS = 64`, so each API frame is 256 bytes.
  - Each `UMSCHAPI__...` command union contains a structured view and `uint32_t max_dwords_in_api[API_FRAME_SIZE_IN_DWORDS]` to force frame-sized storage.
  - `static_assert(sizeof(union UMSCHAPI__SET_HW_RESOURCES) <= API_FRAME_SIZE_IN_DWORDS * sizeof(uint32_t))` checks one large command fits the frame.
- Queueing/log constants:
  - `API_NUMBER_OF_COMMAND_MAX = 32` for a secondary command queue used to avoid scheduler-context command overwrite during interrupt bursts.
  - `UMSCH_INSTANCE_DB_OFFSET_MAX = 16`.
  - `UMSCH_MAX_HWIP_SEGMENT = 8`.
- API typing:
  - `enum UMSCH_API_TYPE` currently defines scheduler commands as type `1`.
  - `union UMSCH_API_HEADER` packs `type:4`, `opcode:8`, `dwsize:8`, and `reserved:12` into `u32All`.
  - `enum UMSCH_API_OPCODE` covers `SET_HW_RSRC`, `SET_SCHEDULING_CONFIG`, `ADD_QUEUE`, `REMOVE_QUEUE`, `PERFORM_YIELD`, `SUSPEND`, `RESUME`, `RESET`, `SET_LOG_BUFFER`, `CHANGE_CONTEXT_PRIORITY`, `QUERY_SCHEDULER_STATUS`, and `UPDATE_AFFINITY`.
- Scheduling and engine enums:
  - `UMSCH_AMD_PRIORITY_LEVEL`: idle, normal, focus, realtime.
  - `UMSCH_ENGINE_TYPE`: VCN0, VCN1, combined VCN, VPE.
  - `UMSCH_RESUME_OPTION`: context resume or engine schedule resume.
  - `UMSCH_RESET_OPTION`: hang detect plus reset or detect only.
  - `VM_HUB_TYPE`: GC or MM hub.
- Logging ABI:
  - `UMSCH_MS_LOG_CONTEXT_STATE` and `UMSCH_MS_LOG_OPERATION` define scheduler log states/events.
  - `UMSCH_LOG_ENTRY_HEADER`, `UMSCH_LOG_ENTRY_DATA`, and `UMSCH_LOG_BUFFER` define a variable-length GPU-visible log buffer with a single-entry flexible-array-style tail.
- Core payloads:
  - `UMSCH_API_STATUS` contains a completion fence GPU address and value.
  - `UMSCHAPI__SET_HW_RESOURCES` advertises VMID masks, engine masks, HQD masks, scheduler context pointer, MMHUB/OSSSYS base/version arrays, VCN/VPE versions, status fence, and capability flags such as `disable_reset`, `disable_umsch_log`, and VCN enablement.
  - `UMSCHAPI__SET_SCHEDULING_CONFIG` provides per-priority grace periods, process quanta, same-level grace periods, and normal-yield percentage.
  - `UMSCHAPI__ADD_QUEUE` supplies process VA/PT base, process/context CSA addresses and quanta, priority, doorbells, affinity, MQD address, context/queue handles, engine type, VM control, suspend/collaboration flags, completion status, and CSA array indexes.
  - `REMOVE_QUEUE`, `PERFORM_YIELD`, `SUSPEND`, `RESUME`, `RESET`, `SET_LOGGING_BUFFER`, `UPDATE_AFFINITY`, `CHANGE_CONTEXT_PRIORITY_LEVEL`, and `QUERY_UMSCH_STATUS` are narrow command payloads with a header, operation-specific fields, and `UMSCH_API_STATUS`.

## Control Flow

The header encodes a command protocol rather than local control flow. The expected runtime sequence is:

1. Driver allocates a 64-dword API frame and fills `UMSCH_API_HEADER` with scheduler type, opcode, and dword size.
2. Driver writes the opcode-specific union fields, including GPU addresses, doorbell offsets, queue handles, engine type, priorities, and optional completion fence information.
3. Driver submits the frame to the UMSCH MM firmware through its API/ring mechanism.
4. Firmware parses `header.type` and `header.opcode`, consumes the fixed ABI layout, performs scheduling or queue state changes, writes completion fences/status/log entries, and may signal interrupts.

The log-buffer structures model another flow: firmware advances `first_free_entry_index` and `wraparound_count`, writes timestamped entries with an operation type, and uses the union payload to describe context state transitions or queue work/wait events.

## State and Persistence Behavior

The header itself owns no state, but it defines persistent shared state formats:

- API frames are transient command records, but their completion fences persist until observed by the host.
- `UMSCHAPI__SET_HW_RESOURCES` seeds firmware-global scheduler state such as VMID availability, engine/HQD masks, MMHUB/OSSSYS base addresses, scheduler context memory, and feature flags.
- `UMSCHAPI__ADD_QUEUE` and `REMOVE_QUEUE` mutate firmware queue/context state keyed by `h_context`, `h_queue`, doorbell offsets, MQD address, and CSA pointers.
- Suspend/resume/reset commands alter queue execution state and may update suspend or API completion fences.
- The log buffer is persistent GPU-visible diagnostic memory with wraparound semantics.
- `#pragma pack(push, 4)` makes layout persistence explicit: field offsets and sizes are part of the firmware contract.

## Dependencies and Integration Points

The file expects fixed-width integer types and `bool` to be available before or through the including context. It integrates with AMDGPU multimedia scheduler code that allocates frames, programs UMSCH firmware rings, manages VCN/VPE queues, maps doorbells, initializes MMHUB/OSSSYS addresses, and handles firmware completion fences/log buffers. It also integrates with MQD definitions, GPU memory managers, interrupt handling, reset/hang-detection paths, and debug tooling that decodes UMSCH logs.

## Risks

- ABI layout drift is the largest risk. Packing, enum size assumptions, bitfield allocation order, and union sizes must match firmware exactly.
- Only `UMSCHAPI__SET_HW_RESOURCES` has an explicit `static_assert`; other command unions rely on the common 64-dword backing array but are not individually asserted for semantic field fit or expected offsets.
- Bitfields in `UMSCH_API_HEADER`, `UMSCH_AFFINITY`, and the flags inside `SET_HW_RESOURCES` rely on compiler layout conventions. This is common in kernel/hardware headers but still a portability risk.
- `dwsize` is only 8 bits, so callers must keep command sizes within 255 dwords; the ABI uses 64 dwords by design.
- GPU address fields are raw `uint64_t`; invalid alignment, address space, lifetime, or VMID selection can produce firmware faults rather than C-level errors.
- The log buffer uses `entries[1]` as a variable-length tail pattern. Allocation and bounds management must be done by consumers.
- Normal-yield percentage documents a valid range of 0 to 50, but the header does not enforce it.
- Queue limits such as `MAX_VCN_QUEUES`, `MAX_VPE_QUEUES`, and `MAX_QUEUES_IN_A_CONTEXT` are compile-time constants that must stay synchronized with firmware capabilities.

## Test Signals

- Build-time signal: compile all UMSCH MM users with structure packing enabled and no missing fixed-width/bool definitions.
- ABI tests should assert `sizeof` and key `offsetof` values for each command union and log struct against firmware headers.
- Firmware integration tests should exercise set-hardware-resources, add/remove queue, suspend/resume, reset, priority change, affinity update, log buffer setup, and status query commands.
- Completion-fence tests should verify firmware writes the requested value to `api_completion_fence_addr`.
- Stress tests with multiple interrupts should validate the `API_NUMBER_OF_COMMAND_MAX` queueing intent and absence of command overwrite.
- Log-buffer tests should validate wraparound, operation decoding, and interrupt-entry signaling.
