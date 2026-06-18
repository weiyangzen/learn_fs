# Research: subset-b-003504

Grouped research for AMD DRM include headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include`. Each section is source-tree-aligned and is intended to be split into its mapped per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc_v1_0_enum.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc_v1_0_enum.h

## Purpose

This header is a very small SOC v1.0 register-value vocabulary header. It defines symbolic values for memory type selection and shader memory alignment mode fields used by AMD GPU register programming code. It has no executable code; its value is in preserving exact numeric encodings expected by SOC v1.0 hardware and by any generated register programming paths that consume these enums.

## Important APIs, Types, and Constants

- `typedef enum MTYPE`: memory type encodings:
  - `MTYPE_NC = 0x0`
  - `MTYPE_RESERVED_1 = 0x1`
  - `MTYPE_RW = 0x2`
  - `MTYPE_UC = 0x3`
- `typedef enum SH_MEM_ALIGNMENT_MODE`: shader memory alignment encodings:
  - `SH_MEM_ALIGNMENT_MODE_DWORD = 0x0`
  - `SH_MEM_ALIGNMENT_MODE_UNALIGNED = 0x1`
- The include guard is `__SOC_V1_0_ENUM_H__`.

## Control Flow

There is no runtime control flow. Including this file only introduces enum tags and typedef names into the translation unit. Consumers choose enum constants while building register values or hardware-facing command/configuration structures.

## State and Persistence Behavior

The header owns no mutable state and performs no persistence. The constants may become persistent indirectly when written into GPU registers, firmware-visible buffers, saved queue descriptors, or command streams by downstream driver code. Any ABI or hardware compatibility comes from the stable numeric enum values, not from state in this file.

## Dependencies and Integration Points

The file has no explicit includes. It relies on C enum semantics and can be included by low-level AMDGPU register programming code. Integration points are likely SOC v1.0 hardware init/configuration code, shader memory configuration code, and any packet or register builders that need human-readable names for memory/cache behavior.

## Risks

- The numeric values are hardware ABI. Renumbering or reusing the reserved slot can silently program incorrect memory/cache behavior.
- The enum names are generic (`MTYPE`, `SH_MEM_ALIGNMENT_MODE`) and may collide if included with other generated register headers that use the same global names.
- There are no compile-time assertions connecting these values to register field widths; consumers must mask/shift them correctly.
- `MTYPE_RESERVED_1` should remain reserved unless hardware documentation and all consumers are updated.

## Test Signals

- Compile coverage from AMDGPU translation units that include this header is the main signal.
- Register programming tests or hardware bring-up logs should confirm expected cache/memory type behavior for SOC v1.0 paths.
- Static checks can compare the enum values against generated register documentation or golden headers.
- Runtime failures would likely appear as GPU faults, incorrect memory coherency, or shader memory access anomalies rather than local failures in this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc_v1_0_enum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc_v1_0_ih_clientid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc_v1_0_ih_clientid.h

## Purpose

This header defines SOC v1.0 interrupt handler client IDs for AMD GPU interrupt source decoding. It maps hardware client-id numbers from interrupt ring entries to symbolic names and declares `soc_v1_0_ih_clientid_name[]`, a string table expected to be defined elsewhere for logging and diagnostics.

## Important APIs, Types, and Constants

- `extern const char *soc_v1_0_ih_clientid_name[]`: name lookup table for client IDs. The table definition must be sized and indexed consistently with this enum.
- `enum soc_v1_0_ih_clientid`: sparse hardware client IDs:
  - `SOC_V1_0_IH_CLIENTID_IH = 0x00`
  - `ATHUB = 0x02`, `BIF = 0x03`, `RLC = 0x07`, `GFX = 0x0a`, `IMU = 0x0b`
  - media/thermal/memory clients including `VCN1 = 0x0e`, `THM = 0x0f`, `VCN = 0x10`, `VMC = 0x12`
  - command/GC/fabric/power clients including `GRBM_CP = 0x14`, `GC_AID = 0x15`, `ROM_SMUIO = 0x16`, `DF = 0x17`, `PWR = 0x19`, `LSDMA = 0x1a`, `GC_UTCL2 = 0x1b`, `nHT = 0x1c`, `MP0 = 0x1e`, `MP1 = 0x1f`
  - `SOC_V1_0_IH_CLIENTID_MAX` follows the largest assigned ID and will evaluate to `0x20`.
- The include guard is `__SOC_V1_0_IH_CLIENTID_H__`.

## Control Flow

There is no executable control flow in the header. Runtime control flow occurs in consumers: interrupt decoding reads a client-id field from an interrupt vector, compares or switches on the enum value, and may use `soc_v1_0_ih_clientid_name[client_id]` for traces or error messages.

## State and Persistence Behavior

The header has no mutable state. The external name array is read-only string data owned by another translation unit. Interrupt client IDs are transient hardware event metadata, although logs, traces, and error reports can persist decoded names or raw IDs.

## Dependencies and Integration Points

The file has no explicit includes. It integrates with the AMDGPU interrupt handler path, SOC v1.0 interrupt vector parsing, trace/debug printing, and any code that dispatches behavior based on interrupt client. The sparse enum values imply table consumers must tolerate holes in the ID space or provide placeholder names for unassigned IDs.

## Risks

- Array indexing is the main risk. Because IDs are sparse, `soc_v1_0_ih_clientid_name[]` must have entries up to at least `SOC_V1_0_IH_CLIENTID_MAX - 1`, including placeholders for gaps.
- `SOC_V1_0_IH_CLIENTID_MAX` is not a count of explicitly listed clients; it is one past the highest numeric ID. Code that iterates all enum names must account for gaps.
- The `0X1c` spelling for `SOC_V1_0_IH_CLIENTID_nHT` is valid C but visually inconsistent; mechanical parsers expecting lowercase `0x` could trip.
- Incorrect client ID mapping can route interrupts to the wrong handler or make diagnostics misleading.

## Test Signals

- Compile/link checks should catch a missing definition of `soc_v1_0_ih_clientid_name[]` only when a referencing object is linked.
- Unit or debug tests can verify that the name table has a non-null entry for each defined enum constant and safe placeholders for gaps.
- Hardware interrupt tests should confirm that IH, GFX, VCN, VMC, MP0/MP1, and power events decode to expected clients.
- Trace logs from interrupt storms or GPU reset paths can expose out-of-range or unnamed client IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc_v1_0_ih_clientid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/umsch_mm_4_0_api_def.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/umsch_mm_4_0_api_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v10_structs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v10_structs.h

## Purpose

This header defines GFX10 hardware queue and context-save memory layouts used by AMDGPU. It exposes fixed dword-ordered structures for graphics MQDs, SDMA MQDs, compute MQDs, and GFX metadata used for CE/DE indirect-buffer preemption state. These structures mirror GPU firmware/hardware save areas rather than implementing algorithms.

## Important APIs, Types, and Structures

- `struct v10_gfx_mqd`: 512 dwords of graphics MQD state. Important clusters include:
  - queue disable and base/VMID fields around offsets 106 and 128-145.
  - HQD queue state such as active, VMID, priority, quantum, ring base, read/write pointers, doorbell control, HQD control, mapped state, queue-manager control, HQ status/control, and MQD control.
  - performance/stat counters for primitives, shader thread trace, pixel/primitive/vertex/geometry/hull/domain/compute invocation counters.
  - stream-out filled sizes, DMA max size/instance counts, base IB address fields, shader resource registers, and large depth-buffer occlusion counter blocks.
  - the structure ends at reserved dword 511.
- `struct v10_sdma_mqd`: SDMA queue descriptor with ring-buffer control/base/read/write pointers, polling and report addresses, IB control/base/size, skip/context/doorbell/status/watermark fields, CSA address, preempt/dummy registers, AQL control, mid-command data registers, and driver-internal `sdma_engine_id`/`sdma_queue_id` in the final two dwords.
- `struct v10_compute_mqd`: 512 dwords of compute queue state. Important clusters include:
  - dispatch dimensions, starts, thread counts, program/TBA/TMA addresses, program resources, VMID, resource limits, static thread management, temp-ring size, restart coordinates, thread-trace enable, dispatch IDs, relaunch, and wave restore.
  - 16 compute user-data registers.
  - query/connect/save/restore timestamps and read indices.
  - GDS and context save addresses/masks.
  - HQD persistent state, pipe/queue priority, PQ base/read/write pointers, doorbell control, IB control, dequeue/semaphore/message/atomic fields, scheduler/status/control, EOP ring, context-save layout, GDS resource state, error, AQL control, suspend offsets, IQ timer packet fields, set-resource packet fields, queue doorbell IDs, and reserved padding through dword 511.
- `struct v10_ce_ib_state`: 10-dword constant-engine IB save area for non-chained and chained IB fields.
- `struct v10_de_ib_state`: 27-dword draw-engine IB save area with completion/status, chain addresses/sizes, preamble ranges, draw/dispatch indirect bases, GDS backup, index base, and sample control.
- `struct v10_gfx_meta_data`: 4 KiB metadata block containing CE payload, reserved padding, DE payload, preempted PFP IB base address, and trailing reserved padding.

## Control Flow

There is no local control flow. Runtime flow is structural:

1. Driver or firmware allocates MQD/context-save memory with the required size and alignment for the engine generation.
2. Initialization code fills selected fields and leaves reserved fields zeroed or firmware-owned.
3. Hardware/firmware consumes these layouts to schedule, save, restore, preempt, and resume graphics, compute, and SDMA queues.
4. On context save or preemption, hardware/firmware updates pointer, timestamp, counter, and metadata fields that the driver may later inspect or reuse.

The GFX metadata structures describe CE/DE IB save/restore flow: non-chained and chained IB addresses, offsets, preamble ranges, and indirect base state are captured so a preempted graphics workload can resume correctly.

## State and Persistence Behavior

These structures are persistent GPU-visible state blocks. They may live in VRAM, GTT, or firmware-managed memory and outlive individual command submissions. The many `reserved_*` dwords are part of the persisted ABI and preserve exact offsets for hardware and future fields. The final SDMA engine/queue IDs are explicitly driver-internal repurposing of otherwise reserved space. Queue pointers, doorbells, context-save addresses, counters, timestamps, EOP information, and metadata fields are all stateful across scheduling events, preemption, suspend/resume, and reset recovery.

## Dependencies and Integration Points

The header relies on `uint32_t` being available from the including context. It integrates with AMDGPU GFX10 queue setup, KFD compute queue management, SDMA queue initialization, MQD allocation, context save/restore, GPU reset, preemption, performance counter capture, shader thread tracing, and debug dump code. It is closely related to register definitions and packet builders that know the meaning of the individual CP, SQ, VGT, DB, and SDMA fields.

## Risks

- Field order and dword offsets are hardware ABI. Reordering, type-size changes, or removing reserved fields can break queue scheduling or context restore.
- There are no `static_assert(sizeof(...))` or `offsetof` checks in this header, so layout validation depends on consumers or external tests.
- The structures use hundreds of plain `uint32_t` fields instead of typed substructures; incorrect writes can compile but corrupt hardware state.
- The SDMA structure uses final reserved positions for driver-internal IDs. Any future hardware use of those positions would need coordinated migration.
- GFX metadata comments specify 4 KiB and 64-byte alignment requirements, but the header cannot enforce allocation alignment.
- Many fields are split low/high address pairs. Consumers must compose/decompose GPU addresses consistently and honor alignment requirements.
- Reserved fields should be zeroed unless explicitly owned by firmware/hardware; stale data can be interpreted by newer firmware.

## Test Signals

- Compile-time ABI tests should assert `sizeof(struct v10_gfx_mqd) == 512 * 4`, `sizeof(struct v10_compute_mqd) == 512 * 4`, expected SDMA size, and `sizeof(struct v10_gfx_meta_data) == 4096`.
- `offsetof` tests for key fields such as `disable_queue`, `cp_mqd_base_addr`, HQD pointer/doorbell fields, `sdma_engine_id`, `sdma_queue_id`, and compute `queue_doorbell_id*` should match hardware documentation.
- Runtime queue tests should cover graphics queue creation, compute dispatch, SDMA copy, preemption, suspend/resume, reset recovery, and context-save restoration on GFX10 devices.
- Debug dumps of MQDs should decode expected nonzero fields after queue activity and remain stable across suspend/resume.
- Memory sanitization tests should ensure reserved dwords are initialized to zero before firmware sees the block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v10_structs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v11_structs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v11_structs.h

## Purpose

This header defines GFX11 hardware queue descriptor layouts for AMDGPU. Like the GFX10 header, it models firmware/hardware ABI state rather than executable logic, but it updates the graphics, SDMA, and compute MQD layouts for the GFX11 generation. New fields cover shadow/GDS/firmware work areas, checksums/query state, control buffers, fences, GWS values, expanded SDMA mid-command/debug state, and GFX11 compute dispatch/control fields.

## Important APIs, Types, and Structures

- `struct v11_gfx_mqd`: 512 dwords of graphics MQD state. Compared with GFX10, early dwords include `shadow_base_*`, `gds_bkup_base_*`, `fw_work_area_base_*`, `shadow_initialized`, and `ib_vmid`. Other notable clusters:
  - checksum and MQD query fields around offsets 84-95.
  - `control_buf_addr_*` at offsets 104-105, queue disable at 106, and the familiar CP graphics HQD cluster at 128-162.
  - primitive counters, shader thread trace fields, graphics invocation counters, stream-out filled sizes, DMA limits, base IB address fields, shader resource fields, and depth-buffer occlusion counters.
  - `fence_address_lo/hi` at final offsets 510-511.
- `struct v11_sdma_mqd`: SDMA queue descriptor with offset comments. It includes ring base/read/write pointers, report addresses, IB controls, skip/context/doorbell fields, CSA address, scheduler control, preempt and ring-buffer preempt fields, AQL/minor-pointer update fields, mid-command data 0-10, mid-command control, F32 debug registers, reserved space, and driver-internal `sdma_engine_id`/`sdma_queue_id`.
- `struct v11_compute_mqd`: 512 dwords of compute state. Important clusters include:
  - dispatch dimensions, starts, thread counts, program address, dispatch packet address, dispatch scratch base, program resources, VMID, resource limits, static thread management SE0-SE7, request control, user accumulators, program resource 3, DDID index, shader checksum, dispatch interleave, relaunch, and wave restore.
  - 16 compute user-data registers and compute invocation counters.
  - MQD query/connect/save/restore timestamp fields and read indices.
  - GDS/context save state, PQ execution and packet status, HQD state, EOP/context-save state, AQL and queue pointer fields.
  - IQ timer packet and set-resource packet storage, 16 queue doorbell IDs, control-buffer address/write/drop pointers/entry count, draw-ring address, fence address, and 64 GWS value dwords at the end.

## Control Flow

There is no direct control flow. Runtime behavior follows the queue lifecycle:

1. Driver code allocates and initializes GFX11 MQD memory for graphics, SDMA, or compute queues.
2. Hardware/firmware reads fixed offsets to configure rings, doorbells, VMIDs, priorities, context-save areas, and dispatch metadata.
3. During scheduling, preemption, query, or reset, firmware updates timestamp, pointer, status, fence, control-buffer, and GWS fields.
4. Driver debug, reset, and queue-management paths inspect or rewrite these layouts to resume work or diagnose failures.

The layout extends GFX10 flows with GFX11-specific shadow/control-buffer and fence/GWS state that makes queue restore and synchronization more explicit.

## State and Persistence Behavior

The structures define persistent GPU-visible queue state. Address pairs, read/write pointers, doorbell controls, VMIDs, priorities, context-save base addresses, EOP state, control buffers, query timestamps, and fence/GWS values persist across queue scheduling events. Reserved dwords are also persistent ABI padding and must be preserved or zeroed according to the owning path. The final SDMA `sdma_engine_id` and `sdma_queue_id` are driver-internal state stored inside the descriptor.

## Dependencies and Integration Points

The header relies on `uint32_t` being available in the including context. It integrates with AMDGPU GFX11 graphics queue management, compute/KFD queue creation, SDMA queue setup, firmware scheduling, GDS/GWS handling, context save/restore, preemption, GPU reset recovery, shader tracing, queue debug dumps, and hardware counter collection. It shares naming and layout patterns with `v10_structs.h` but must be selected by generation-specific code, not treated as interchangeable with GFX10.

## Risks

- GFX11 offsets are ABI-critical. The added early fields in `v11_gfx_mqd` and compute fields mean reuse of GFX10 initialization logic without generation guards can write the wrong dwords.
- The header has no `static_assert` or `offsetof` checks to verify the documented offset comments.
- Some SDMA offset comments around reserved fields appear inconsistent (`reserved_71` onward restarts decimal offset comments briefly), so comments should not be the sole source of truth for generated checks.
- Driver-internal SDMA engine/queue IDs occupy repurposed reserved dwords; this depends on firmware not using those slots.
- Many address fields are low/high pairs; misprogramming address halves can corrupt queue state or fault firmware.
- Fence, control-buffer, and GWS fields add synchronization and state-restoration surface; stale values after reset or descriptor reuse can cause subtle queue behavior.
- Reserved fields and generation-specific additions must be zeroed or initialized exactly as firmware expects.

## Test Signals

- ABI tests should assert `sizeof(struct v11_gfx_mqd) == 512 * 4`, `sizeof(struct v11_compute_mqd) == 512 * 4`, expected SDMA size, and key offsets for `shadow_base_lo`, `checksum_lo`, `control_buf_addr_lo`, `disable_queue`, `cp_mqd_base_addr`, graphics `fence_address_lo`, compute `queue_doorbell_id0`, control-buffer fields, compute `fence_address_lo`, and GWS values.
- Runtime tests on GFX11 hardware should cover graphics and compute queue creation, SDMA copy queues, preemption, suspend/resume, reset recovery, queue fences, GWS usage, and control-buffer operation.
- Debug dumps should show generation-correct field interpretation and avoid treating GFX11 MQDs as GFX10 layouts.
- Stress tests should cover descriptor reuse after reset and verify stale fence/GWS/control-buffer fields do not leak into new queues.
- Static analysis can compare offset comments to compiler `offsetof` output to catch drift or comment mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/v11_structs.h -->
