# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002592`: lines 1-2531, `Docs/researches/chunks/subset-b-002592_research.md`
- `subset-b-002593`: lines 2532-4996, `Docs/researches/chunks/subset-b-002593_research.md`
- `subset-b-002594`: lines 4997-7586, `Docs/researches/chunks/subset-b-002594_research.md`
- `subset-b-002595`: lines 7587-10032, `Docs/researches/chunks/subset-b-002595_research.md`
- `subset-b-002596`: lines 10033-12490, `Docs/researches/chunks/subset-b-002596_research.md`
- `subset-b-002597`: lines 12491-15118, `Docs/researches/chunks/subset-b-002597_research.md`
- `subset-b-002598`: lines 15119-17740, `Docs/researches/chunks/subset-b-002598_research.md`
- `subset-b-002599`: lines 17741-20296, `Docs/researches/chunks/subset-b-002599_research.md`
- `subset-b-002600`: lines 20297-22799, `Docs/researches/chunks/subset-b-002600_research.md`
- `subset-b-002601`: lines 22800-25181, `Docs/researches/chunks/subset-b-002601_research.md`
- `subset-b-002602`: lines 25182-27636, `Docs/researches/chunks/subset-b-002602_research.md`
- `subset-b-002603`: lines 27637-30183, `Docs/researches/chunks/subset-b-002603_research.md`
- `subset-b-002604`: lines 30184-32568, `Docs/researches/chunks/subset-b-002604_research.md`
- `subset-b-002605`: lines 32569-34980, `Docs/researches/chunks/subset-b-002605_research.md`
- `subset-b-002606`: lines 34981-37627, `Docs/researches/chunks/subset-b-002606_research.md`
- `subset-b-002607`: lines 37628-40016, `Docs/researches/chunks/subset-b-002607_research.md`
- `subset-b-002608`: lines 40017-42372, `Docs/researches/chunks/subset-b-002608_research.md`
- `subset-b-002609`: lines 42373-44638, `Docs/researches/chunks/subset-b-002609_research.md`

## Chunk Research

### subset-b-002592: lines 1-2531

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 1-2531

## Scope

This chunk covers the beginning of the generated GC 12.1.0 AMDGPU shift/mask header. It starts with the file license and include guard, then enters the `CHIP_XCD_gfxip_xcc_gfx_cpwd_sdma_sdmadec` address block. The covered register families are all for SDMA0 and include:

- SDMA engine public/core control, revision, timestamp, power, cache, status, freeze, watchdog, queue-status, atomic, DCC, clock-gating, error-log, RAS, poison, and diagnostics registers.
- UTCL1 warmup, control, watermarks, timeout, page, cache, read/write status, invalidation, and read/write XNACK fault reporting registers.
- SR-IOV and virtualization-visible status fields such as GPU IOV violation logs, invalid-address source, queue ID/status fields, VF/VFID fields, and SDMA queue status.
- Per-queue SDMA0 ring, indirect-buffer, doorbell, context-save, scheduling, preemption, AQL, context-switch, mid-command, utilization, MQD, and context-status fields.
- Complete per-queue field sets for queues 0 through 5, plus the beginning of queue 6 through `SDMA0_SDMA_QUEUE6_SCHEDULE_CNTL__LOCAL_ID__SHIFT`. The range ends inside the queue 6 schedule-control field list; the remaining queue 6 schedule-control masks and later queue 6 fields belong to the next chunk.

The file is generated hardware register metadata. This chunk defines only C preprocessor constants. It contains no functions, structs, variables, storage allocation, or executable control flow.

## Purpose

The purpose of this header section is to provide the bitfield half of the MMIO ABI between AMDGPU/KFD SDMA code and GC 12.1.0 hardware. For each hardware register field, the generator emits the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when composing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask used to isolate the field.

The sibling `gc_12_1_0_offset.h` header supplies register offsets such as `regSDMA0_SDMA_QUEUE0_RB_CNTL`; this header supplies the field layouts for those offsets. Driver code consumes these definitions through direct shifts, `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, and related SOC15 register helpers.

Observed integration points in this tree include `amdgpu/sdma_v7_1.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/mes_v12_1.c`, `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, `amdkfd/kfd_mqd_manager_v12_1.c`, `amdkfd/kfd_device_queue_manager_v12_1.c`, `amdgpu/gfxhub_v12_1.c`, `amdgpu/imu_v12_1.c`, and `amdgpu/soc_v1_0.c`, all of which include `gc/gc_12_1_0_sh_mask.h`. The most direct consumers for this chunk are SDMA v7.1 ring setup, KFD SDMA MQD construction, SDMA page-fault/XNACK diagnostics, and KFD queue register programming.

## Important Macro Families

### SDMA0 Engine Control and Status

The first part of the chunk describes global SDMA0 engine registers:

- `SDMA0_SDMA_DEC_START`, `SDMA0_SDMA_MCU_MISC_CNTL`, `SDMA0_SDMA_UCODE_REV`, and global timestamp low/high registers expose firmware start, MCU wakeup, firmware revision components, and engine time counters.
- `SDMA0_SDMA_POWER_CNTL`, `SDMA0_SDMA_CNTL`, `SDMA0_SDMA_CNTL1`, `SDMA0_SDMA_CHICKEN_BITS`, and `SDMA0_SDMA_CHICKEN_BITS_2` define low-speed enablement, data/fence swapping, trap and interrupt enables, preemption behavior, PIO acknowledgements, CP/MES synchronization, page fault/null/retry interrupts, FIFO/watermark behavior, debug modes, and assorted clock-gating override controls.
- `SDMA0_SDMA_CACHE_CNTL`, `SDMA0_SDMA_CRD_CNTL`, and `SDMA0_SDMA_MEMHUB_CNTL` define cache temporal hints, read/write scope, request credit limits, and speculative data-read behavior.
- `SDMA0_SDMA_STATUS_REG` through `SDMA0_SDMA_STATUS8_REG` expose idle state, ring-buffer and indirect-buffer command activity, fetch/core/interrupt idleness, context emptiness, microcode-init completion, copy-engine FIFO state, secure-interrupt state, firmware stack overflow, previous VM command, queue match/interrupt queue ID, outstanding reads/writes/TLBI/GCR/UTCL2 requests, active queue ID, SR-IOV wait/execute state, XNACK summary bits, queue ring-enable state, write-pointer poll exceptions, thread instruction pointers, request drops, and context-switch load conditions.

These definitions are mostly consumed by bring-up, reset, hang diagnosis, and interrupt/error reporting paths. Some fields are configuration bits written by the driver; others are read-only status bits latched by hardware.

### Freeze, Watchdog, Scheduling, and Engine Diagnostics

The chunk includes freeze and watchdog controls:

- `SDMA0_SDMA_FREEZE`, `SDMA0_SDMA_EXTERNAL_FROZEN`, and `SDMA0_SDMA_FREEZE_TRIGGER` expose core freeze state, MCU freeze state, IMU FSM state, external freeze threshold, and command-style core freeze trigger.
- `SDMA0_SDMA_PROCESS_QUANTUM0/1`, `SDMA0_SDMA_GLOBAL_QUANTUM`, `SDMA0_SDMA_QUEUE_STATUS0/1`, `SDMA0_SDMA_QUEUE_RESET_REQ`, and `SDMA0_SDMA_QUEUE_DEQUEUE_REQUEST` describe per-process quanta, global focus/normal quanta, queue status nybbles for queues 0-9, and per-queue reset/dequeue request bits.
- `SDMA0_SDMA_WATCHDOG_CNTL` provides queue-hang and command-timeout counters.
- `SDMA0_SDMA_ERROR_LOG`, public dummy registers, `SDMA0_SDMA_MCU_COUNTER`, `SDMA0_SDMA_TIMESTAMP_CNTL`, and scratch RAM address/data registers expose debug and capture state.

These fields are tied to scheduler fairness, queue recovery, preemption, and hang triage. Reset/dequeue/freeze bits are control surfaces; status and timestamp fields are observation surfaces.

### UTCL1, Address Translation, and XNACK

The UTCL1 group is central to memory translation behavior for SDMA:

- `SDMA0_SDMA_UTCL1_WARMUPL2_CNTL` controls L2 warmup enablement, interval, granularity, and step count.
- `SDMA0_SDMA_UTCL1_CNTL` defines redo delay, page-wait delay, response mode, forced invalidation, heavy invalidation requests, execute-permission controls, invalidation-ack delay, and L2 request credits.
- `SDMA0_SDMA_UTCL1_WATERMK`, `SDMA0_SDMA_UTCL1_TIMEOUT`, and `SDMA0_SDMA_UTCL1_PAGE` cover request/page FIFO watermarks, XNACK retry limits, invalid-address reporting mode, request type, MTYPE/no-PTE override, snoop/IO controls, L2 policy, broadcast, and physical-address mode.
- `SDMA0_SDMA_UTCL1_CACHE_CNTL` includes XNACK redo timer count, MTYPE no-PTE override, invalidate IC/GU bits, fragment-limit mode, force snoop, and strict permission.
- `SDMA0_SDMA_UTCL1_RD_STATUS` and `SDMA0_SDMA_UTCL1_WR_STATUS` report read/write path FIFO empty/full state and L2/request idleness.
- `SDMA0_SDMA_UTCL1_INV0/1/2` describe invalidation-busy state, GPUVM fragment size, VMID, mode, high/low VMID fields, tags, invalidation type, invalidation address low bits, and CPF flush metadata.
- `SDMA0_SDMA_UTCL1_RD_XNACK0/1` and `SDMA0_SDMA_UTCL1_WR_XNACK0/1` expose read/write fault address, VMID, fault/null/timeout vectors, and fault/null/timeout flags.

In `amdgpu/sdma_v7_1.c`, SDMA v7.1 code programs `SDMA0_SDMA_UTCL1_CNTL` response mode and redo delay, updates `SDMA0_SDMA_UTCL1_PAGE`, writes `SDMA0_SDMA_UTCL1_TIMEOUT`, and lists UTCL1 status/XNACK registers for diagnostics. Incorrect masks here can directly affect retry behavior, page-fault reporting, permission checks, and queue recovery.

### Atomic, DCC, RAS, Poison, and Virtualization Signals

The chunk defines lower-level error, reliability, and virtualization fields:

- `SDMA0_SDMA_ATOMIC_CNTL`, `SDMA0_SDMA_ATOMIC_PERMS_CNTL`, and atomic preop low/high registers define atomic retry and PCIe atomic support controls plus pre-operation data.
- `SDMA0_SDMA_DCC_CNTL` controls DCC bypass and per-slice no-PTE read/write compression override/enable bits.
- `SDMA0_SDMA_GPU_IOV_VIOLATION_LOG`, `SDMA0_SDMA_GPU_IOV_VIOLATION_LOG2`, `SDMA0_SDMA_INVALID_ADDR_LO/HI`, and `SDMA0_SDMA_INVALID_ADDR_SOURCE` describe violation status, multiple-violation status, address, write operation, VF/VFID, initiator ID, invalid address value, source ID, VMID, and virtualization source.
- `SDMA0_SDMA_RAS_STATUS` and `SDMA0_SDMA_POISON_INFO` expose ECC/parity sources, SRAM/bus status, VMID, VFID, and VF state for reliability diagnostics.
- `SDMA0_SDMA_CLOCK_GATING_STATUS`, `SDMA0_SDMA_RLC_CGCG_CTRL`, and clock-gating override fields report and control clock-gating integration with RLC.

These fields are largely status or policy-control integration points for SR-IOV, RAS, and power management. Driver users must preserve privilege and ownership assumptions around VF/PF attribution and avoid treating diagnostic status fields as ordinary queue configuration.

### SDMA Queue Ring and IB Layout

The per-queue sections start at `SDMA0_SDMA_QUEUE0_RB_CNTL` and repeat for queues 0-5, with queue 6 partially included. Each full queue block has a consistent shape:

- Ring-buffer control: `RB_ENABLE`, `RB_SIZE`, write-pointer polling, endian/swap controls, MCU write-pointer polling, read-pointer writeback enable/swap/timer, privilege, and ring VMID.
- Ring-buffer base/read/write pointer registers: base low/high, read pointer low/high, write pointer low/high, and read-pointer writeback address low/high.
- Indirect-buffer control and pointers: `IB_ENABLE`, `IB_SWAP_ENABLE`, `SWITCH_INSIDE_IB`, command VMID, IB privilege, IB read pointer, current offset, base low/high, and size.
- Doorbell handling: doorbell enable/captured bits, doorbell log BE error and captured data, and doorbell offset.
- Context-save address low/high, schedule control, IB-sub-remain, preempt, dummy, and write-pointer polling address registers.

`amdgpu/sdma_v7_1.c` uses queue 0 field names with per-instance and per-queue offset arithmetic. For example, it reads and writes `regSDMA0_SDMA_QUEUE0_RB_CNTL`, clears or sets `RB_ENABLE`, sets `RB_SIZE`, `RB_SWAP_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `WPTR_POLL_ENABLE`, `MCU_WPTR_POLL_ENABLE`, and `RB_PRIV`, then writes the result back through SOC15 helpers. KFD code in `kfd_mqd_manager_v12_1.c` directly composes SDMA MQD register values using `SDMA0_SDMA_QUEUE0_RB_CNTL__RB_SIZE__SHIFT`, `RB_VMID__SHIFT`, `RPTR_WRITEBACK_ENABLE__SHIFT`, `RPTR_WRITEBACK_TIMER__SHIFT`, and `MCU_WPTR_POLL_ENABLE__SHIFT`.

Because later queues use the same field layout with queue-numbered macro names, code often programs a base queue register and computes offsets for other queues rather than spelling every queue-specific macro in executable code.

### AQL, Context Switching, Mid-Command, Utilization, and MQD State

Each complete queue block also contains:

- `RB_AQL_CNTL` fields for AQL enablement, packet size, packet step, mid-command preemption enablement, mid-command data restore, and overlap enablement.
- `MINOR_PTR_UPDATE` enable bits.
- `CONTEXT_SWITCH_STATUS` exception and preemption fields: RB preempt status, VM hole, page exception, command timeout, queue hang, doorbell error, SRAM ECC, DRAM ECC, and write-pointer-less-than-read-pointer exception.
- `MIDCMD_CNTL` fields for data valid, copy mode, split state, and allow-preempt, plus eleven `MIDCMD_DATA*` 32-bit payload registers.
- `UTILIZATION_LO/HI` counters and `WAIT_UNSATISFIED_THD` threshold.
- `MQD_BASE_ADDR_LO/HI`, `MQD_CONTROL__VMID`, and `CONTEXT_STATUS` fields for selected/use-IB/idle/expired/exception/ctxsw-able/VF status/privilege violation/preempt disable/RPTR writeback idle/WPTR update pending/WPTR update fail count.

These macros describe persistent hardware-visible queue state. The SDMA queue manager and KFD MQD manager use them to initialize queue descriptors, enable rings, poll status, and diagnose faulting queues.

## Control Flow and State Behavior

There is no software control flow in this header. All behavior is compile-time substitution of numeric constants into driver code. Runtime behavior appears in the callers that include the header.

The state represented by this chunk is hardware state:

- Engine state includes SDMA enablement, firmware revision, timestamps, power, clock-gating, cache/scope policy, interrupt enables, freeze status, watchdog counters, credits, and error status.
- Translation state includes UTCL1 retry/response policy, page policy, invalidation state, fault addresses, VMID/VFID attribution, and read/write XNACK summaries.
- Queue state includes ring base/pointers, IB base/pointers/size, doorbell offsets/logs, CSA addresses, scheduling identifiers, AQL mode, preemption state, context status, mid-command save/restore payload, utilization counters, MQD base/control, and per-queue exception bits.

Some fields are durable configuration until reprogrammed or reset, such as ring base, ring size, VMID, doorbell offset, cache policy, and UTCL1 response mode. Some fields are status snapshots or sticky error indicators, such as RAS, poison, invalid-address, XNACK, queue exception, doorbell captured, and FIFO empty/full bits. Some are command-style fields, such as queue reset, dequeue request, freeze trigger, timestamp capture, invalidation bits, and preempt bits. The header does not encode sequencing; callers must follow SDMA v7.1 and hardware rules for ordering, polling, barriers, and timeouts.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `gc_12_1_0_offset.h` supplies the register address constants paired with these masks and shifts.
- SOC15 register helper macros use the `REGISTER, FIELD` naming convention to find `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.
- SDMA v7.1 code uses `sdma_v7_1_get_reg_offset()` to map `SDMA0` base registers across SDMA instances and queues.

Important integration points in this source tree include:

- `amdgpu/sdma_v7_1.c`: direct SDMA ring start/stop/setup, UTCL1 programming, XNACK/status debug register listing, queue enablement, and doorbell/ring pointer handling.
- `amdkfd/kfd_mqd_manager_v12_1.c`: SDMA MQD initialization with queue 0 ring-control shifts for queue size, VMID, read-pointer writeback, timer, and MCU write-pointer polling.
- `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`: KFD-facing SDMA register address computation for queue registers using `regSDMA0_SDMA_QUEUE0_RB_CNTL` and queue spacing.
- `amdkfd/kfd_device_queue_manager_v12_1.c`, `amdgpu/mes_v12_1.c`, and `amdgpu/gfx_v12_1.c`: broader GC 12.1.0 queue, MES, and graphics initialization code that includes the same mask header.
- `amdgpu/gfxhub_v12_1.c`, `amdgpu/imu_v12_1.c`, and `amdgpu/soc_v1_0.c`: platform and hub code paths that include the header for GC 12.1.0 register definitions.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can modify adjacent hardware fields, causing SDMA hangs, bad ring sizes, incorrect VMIDs, lost interrupts, broken doorbells, wrong retry behavior, or corrupted fault attribution.
- The queue blocks are highly repetitive. Mechanical generation or manual review errors can be missed because queue 0-6 names differ only by queue number while field layouts are nearly identical.
- The chunk ends mid-register at queue 6 schedule control. Any final merged report must stitch this document to the next chunk before drawing conclusions about full queue 6 coverage.
- Direct shift composition in KFD MQD setup bypasses `REG_SET_FIELD`; if a field width or shift changes, compile still succeeds but queue descriptors may be malformed.
- UTCL1/XNACK fields are tied to memory fault handling. Wrong retry limits, response mode, invalidation control, or fault-vector masks can hide page faults, cause retries to timeout incorrectly, or break GPUVM fault recovery.
- Doorbell and ring pointer fields are synchronization-sensitive. Incorrect offsets, swap settings, polling addresses, or read-pointer writeback settings can make queues appear idle, stuck, or overrun.
- Privilege and virtualization fields must preserve isolation. VF/VFID, violation-log, invalid-address source, RB/IB privilege, and context-status bits must be decoded with the correct PF/VF context.
- Status bits should not be treated as configuration. Many fields are read-only, sticky, command-like, or hardware-cleared; writing them with generic read/modify/write patterns can be unsafe unless the owning driver path documents that behavior.

## Test and Validation Signals

Useful validation is mostly build, boot, queue, and fault-path coverage:

- Compile AMDGPU and KFD code paths that include `gc/gc_12_1_0_sh_mask.h`; this catches missing or renamed register fields.
- Exercise SDMA v7.1 ring bring-up and teardown. Look for correct `RB_ENABLE` transitions, ring size programming, pointer writeback, write-pointer polling, doorbell offset programming, and queue idle status.
- Run KFD SDMA queue creation/destruction tests that build MQDs through `kfd_mqd_manager_v12_1.c`, validating queue size, VMID, RPTR writeback, and MCU WPTR polling fields.
- Trigger SDMA memory fault/XNACK paths and confirm `UTCL1_RD_XNACK*`, `UTCL1_WR_XNACK*`, invalid-address, VMID/VFID, and page/null/timeout flags decode correctly.
- Validate suspend/resume, GPU reset, and hang recovery paths that use queue reset/dequeue, freeze, watchdog, context-switch status, and queue exception fields.
- Run SR-IOV or virtualization diagnostics where available, checking violation logs, VF/VFID attribution, queue status, and privilege violation reporting.
- Exercise RAS/poison diagnostics and confirm ECC/parity, poison VMID/VFID, and bus/SRAM status fields are reported without false positives.
- Compare generated masks against AMD register specifications or known-good generated headers during ASIC header updates, with special attention to repetitive queue blocks and the queue 6 boundary between chunks.

### subset-b-002593: lines 2532-4996

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 2532-4996

## Scope

This chunk covers a generated AMD GC 12.1.0 shift/mask header segment for SDMA register fields. It contains preprocessor constants only: field `__SHIFT` values and `_MASK` values used by AMDGPU and AMDKFD code to compose and decode 32-bit hardware register values.

The requested range contains 2,133 `#define` entries: 1,070 shift macros and 1,063 mask macros. The count is intentionally unbalanced because the chunk begins inside `SDMA0_SDMA_QUEUE6_SCHEDULE_CNTL` and ends inside `SDMA1_SDMA_QUEUE0_RB_CNTL`. Adjacent chunks are needed to complete those two register field families.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU DRM graphics metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 graphics-core registers. This chunk focuses on the SDMA hardware engines, especially queue programming, context save/restore metadata, virtual-function controls, performance counters, clock/power controls, translation/cache status, reset/dequeue request bits, RAS/poison reporting, and the beginning of the second SDMA engine queue layout.

Driver code pairs these macros with offsets from `gc_12_1_0_offset.h` and uses helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 read/write helpers, and KFD MQD setup code to program or inspect SDMA rings without hard-coding bit positions.

The covered register groups are:

- Tail of `SDMA0_SDMA_QUEUE6`: schedule quantum masks, indirect-buffer subremain, preempt request, dummy registers, write-pointer poll address, AQL control, minor pointer update, context-switch exception status, mid-command preempt state/data, utilization counters, MQD base/control, and context status.
- Complete `SDMA0_SDMA_QUEUE7`, `SDMA0_SDMA_QUEUE8`, and `SDMA0_SDMA_QUEUE9` queue field layouts: ring-buffer control/base/rptr/wptr, writeback addresses, indirect-buffer control/base/size/offset, doorbell enable/log/offset, context-save area address, schedule IDs/quantum, AQL control, mid-command state, utilization, MQD base/control, and context status.
- `CHIP_XCD_gfxip_xcc_gfx_cpwd_sdma_sdmahypdec` fields for SDMA0 VM context registers, active function ID, virtual reset request, context-register type bitmaps, public-register type bitmaps, VM command control, MCU control, and instruction-cache base/operation controls.
- `sdmapspdec`, `sdmaperfsdec`, `sdmaperfddec`, and `sdmapwrdec` blocks for reset-address offset, performance counter selection/config/result, perf counter low/high result registers, and SDMA0 MGCG clock-gating soft overrides.
- Beginning of `CHIP_XCD_gfxip_xcc_gfx_cpwd_sdma_sdmadec:1`, defining SDMA1 global controls/status: microcode revision, global timestamp, power/control, chicken bits, cache control, fetched rptr/IB offsets, status registers, process quantum, watchdog, queue status, atomic controls, DCC, UTCL1 controls/status/XNACK, error logging, virtualization violation logs, TLBI/GCR credits, invalid address capture, clock-gating status, queue reset/dequeue requests, RAS/poison fields, MemHub controls, and the first mask for `SDMA1_SDMA_QUEUE0_RB_CNTL`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for isolating or preserving that field.
- Register comments such as `//SDMA0_SDMA_QUEUE7_RB_CNTL` and address-block comments such as `// addressBlock: CHIP_XCD_gfxip_xcc_gfx_cpwd_sdma_sdmadec:1` preserve the hardware grouping from the register database.
- Consumers usually pair these field definitions with `reg<REGISTER>` offsets from `gc_12_1_0_offset.h`.

Important field families in this chunk include:

- Queue ring control fields: `RB_ENABLE`, `RB_SIZE`, `WPTR_POLL_ENABLE`, byte-swap controls, read-pointer writeback enable/timer, `RB_PRIV`, and `RB_VMID`.
- Queue address and pointer fields: `RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, `RB_WPTR_HI`, `RB_RPTR_ADDR_LO/HI`, `RB_WPTR_POLL_ADDR_LO/HI`, `IB_BASE_LO/HI`, `IB_RPTR`, `IB_OFFSET`, `IB_SIZE`, `CSA_ADDR_LO/HI`, and `MQD_BASE_ADDR_LO/HI`.
- Queue scheduling and dispatch fields: `GLOBAL_ID`, `PROCESS_ID`, `LOCAL_ID`, `CONTEXT_QUANTUM`, `IB_PREEMPT`, `AQL_ENABLE`, `AQL_PACKET_SIZE`, `PACKET_STEP`, `MIDCMD_PREEMPT_ENABLE`, `MIDCMD_PREEMPT_DATA_RESTORE`, `OVERLAP_ENABLE`, and `MINOR_PTR_UPDATE`.
- Queue diagnostics: `CONTEXT_SWITCH_STATUS` exception bits for VM hole, page exception, command timeout, queue hang, doorbell error, SRAM/DRAM ECC, and write-pointer/read-pointer ordering; `CONTEXT_STATUS` bits for selected/use-IB/idle/expired/exception/context-switch-able/VF/private-violation/preempt-disable/writeback-idle/write-pointer-pending/fail-count.
- Mid-command state registers: `MIDCMD_CNTL` plus `MIDCMD_DATA0` through `MIDCMD_DATA10`, representing saved state used during preemption or split commands.
- SDMA0 hypervisor/virtualization metadata: `SDMA_VM_CTX_LO/HI`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, `VIRT_RESET_REQ`, context-register type bitmaps, and public-register type bitmaps.
- SDMA0/SDMA1 performance and power fields: perf counter selection/config/result, `GFX_ICG_SDMA_CTRL` MGCG soft overrides and hysteresis, SDMA1 clock-gating status, and RLC CGCG controls.
- SDMA1 global execution fields: `SDMA_CNTL` trap/swap/preempt/interrupt enables, `CHICKEN_BITS`, cache temporal/scope settings, status/idle/fetch bits, queue status, watchdog counts, global quantum, atomics, DCC, UTCL1 page/cache/XNACK controls, and queue reset/dequeue request bitmaps for queues 0-9.
- Reliability and fault fields: invalid address low/high/source, GPU IOV violation logs, interrupt status, RAS ECC/parity/VMID/VFID fields, poison info, page exception status, UTCL1/UTCL2 XNACK fault/null/timeout status, and queue write-pointer poll page exception bits.

## Control Flow

This header has no local runtime control flow. Its direct behavior is compile-time macro substitution.

The implied driver flow is:

1. GC 12.1.0 AMDGPU or AMDKFD code includes `gc_12_1_0_offset.h` and `gc_12_1_0_sh_mask.h`.
2. Code selects a register offset, often through SDMA queue stride helpers, and uses these shift/mask macros to compose a value.
3. AMDGPU writes or reads the register through SOC15/MMIO helpers, or stores the composed fields into an MQD structure consumed by hardware/firmware.
4. Runtime paths poll status fields, decode fault fields, or write request bits for preemption, queue reset, queue dequeue, clock gating, cache invalidation, or performance-counter capture.

Concrete include and use sites in this tree include `amdgpu/sdma_v7_1.c`, `amdkfd/kfd_mqd_manager_v12_1.c`, `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/gfxhub_v12_1.c`, `amdgpu/mes_v12_1.c`, `amdgpu/imu_v12_1.c`, and `amdgpu/soc_v1_0.c`. For example, SDMA setup code uses the queue ring-control fields to size rings, enable read-pointer writeback, configure write-pointer polling, program doorbells, and enable IB processing. KFD MQD code uses the same symbolic queue fields when constructing user-mode SDMA queue descriptors.

The generated header does not encode ordering requirements, access permissions, clear-on-read behavior, write-one-to-clear behavior, firmware ownership, or reset sequencing. Those rules come from the hardware programming guide and the AMDGPU/AMDKFD code that consumes these definitions.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible SDMA state:

- Queue register fields configure persistent ring state until reset or explicit reprogramming: ring base, size, read/write pointers, writeback locations, doorbell mapping, IB state, AQL packet handling, MQD base, schedule identity, and VMID ownership.
- Context state fields expose or control save/restore behavior for preemption and context switching. `MIDCMD_*`, `CSA_ADDR_*`, `CONTEXT_STATUS`, and `CONTEXT_SWITCH_STATUS` are sensitive to queue preemption, timeouts, hangs, and error recovery.
- VM and virtualization fields track VM context addresses/control, active VF/PF identity, virtual reset requests, IOV violation logs, invalid address capture, VMID/VFID attribution, and PF/VF-visible state.
- Performance and utilization fields expose counters and selections. They are live telemetry and may be reset, frozen, multiplexed, or sampled by driver and profiling code.
- Power and clock-gating fields configure MGCG/CGCG behavior and report clock-gating state. These values can be reinitialized across GPU reset, suspend/resume, or power-management transitions.
- Fault, poison, RAS, XNACK, page exception, and invalid-address fields capture reliability and memory-translation events. Some of these may be latched or clear-on-read/write, but that is not visible from this generated header.
- Queue reset and dequeue request bitmaps are side-effect request registers. Writing one bit can affect the corresponding SDMA queue, so field correctness is critical.

Because this is a generated shift/mask file, it cannot show whether a register is read-only, write-only, privileged, shadowed, saved/restored by firmware, or safe for read-modify-write. Consumers must rely on higher-level driver code and hardware documentation.

## Dependencies And Integration Points

This chunk depends on synchronization with AMD's GC 12.1.0 register database and the companion generated files in the same directory, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h`, which provides the matching `reg*` offsets.
- Other GC 12.1.0 generated headers for defaults or packet/register metadata where present.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, and SOC15 offset helpers.

Primary integration points are:

- `amdgpu/sdma_v7_1.c`, which programs SDMA queue registers, ring pointers, IB state, doorbells, writeback addresses, preemption requests, and MQD fields.
- `amdkfd/kfd_mqd_manager_v12_1.c` and `amdkfd/kfd_device_queue_manager_v12_1.c`, which create and manage KFD user-mode queues using SDMA shift/mask definitions.
- `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, which computes SDMA register ranges and queue offsets for KFD integration.
- `amdgpu/gfx_v12_1.c`, `amdgpu/gfxhub_v12_1.c`, `amdgpu/mes_v12_1.c`, `amdgpu/imu_v12_1.c`, and `amdgpu/soc_v1_0.c`, which include the GC 12.1.0 field namespace for graphics, memory hub, firmware, and SOC initialization paths.
- Hardware diagnostics, debugfs, RAS, SR-IOV, and reset paths that decode SDMA status, RAS, IOV, invalid-address, clock-gating, and queue status fields.

## Risks And Edge Cases

- Generated-data drift is the main risk. A wrong shift or mask can compile cleanly while setting the wrong hardware bits.
- The chunk starts and ends inside register families. `SDMA0_SDMA_QUEUE6_SCHEDULE_CNTL` is missing its early shifts in this chunk, and `SDMA1_SDMA_QUEUE0_RB_CNTL` is missing most masks in this chunk. The final per-file report must merge adjacent chunks before making whole-register completeness claims.
- Queue field families are repetitive and stride-sensitive. Copy/paste or generator errors in queues 7-9 can break only higher-numbered queues, which may be less exercised than queue 0.
- Queue state is liveness-critical. Incorrect ring enable, size, pointer, writeback, IB, AQL, doorbell, MQD, or VMID fields can cause hangs, missed fences, bad preemption, lost work, or failed reset recovery.
- Doorbell and write-pointer polling fields are security- and isolation-sensitive because they bridge CPU-visible memory, MMIO state, and queue ownership.
- VM/VF/PF attribution fields are virtualization-sensitive. Wrong `VMID`, `VFID`, `VF`, `PF`, active-function, or IOV violation masks can misattribute faults or weaken SR-IOV isolation.
- Some status/fault/RAS fields may be latched or have side effects on access. This header cannot distinguish ordinary status bits from clear-on-read or write-one-to-clear fields.
- Clock-gating and chicken-bit fields can create intermittent failures under power-management transitions rather than immediate boot failures.
- Performance counter fields are multiplexed and mode-sensitive. Incorrect counter selection or mode masks can silently corrupt profiling data.
- Reserved-bit masks are present in several registers. Read-modify-write code must preserve reserved fields unless hardware documentation says otherwise.

## Test Signals

Useful validation should combine static generated-data checks, build coverage, and hardware/runtime testing:

- Build AMDGPU and AMDKFD with GC 12.1.0 support. Missing or renamed macros should surface in `sdma_v7_1.c`, KFD MQD/queue-manager code, and GC 12.1.0 include users.
- Mechanically diff this range against AMD's authoritative GC 12.1.0 register database and verify both shift values and masks.
- Verify shift/mask pairing for complete registers in the chunk, while allowing the known boundary exceptions for `SDMA0_SDMA_QUEUE6_SCHEDULE_CNTL` and `SDMA1_SDMA_QUEUE0_RB_CNTL`.
- Cross-check repeated SDMA queue families for queues 7, 8, and 9 against queue 0/1 layout expectations and against the companion offset header stride.
- Run SDMA ring tests for queue enable/disable, IB execution, write-pointer polling, read-pointer writeback, doorbells, fences, and preemption.
- Exercise KFD SDMA queue creation and teardown with multiple processes/VMIDs. Watch for stuck queues, dequeue/reset timeouts, incorrect doorbell offsets, and MQD field mismatches.
- Run GPU reset, suspend/resume, and queue preemption tests. Relevant signals include clean context status, no persistent context-switch exception bits, and successful ring reinitialization.
- Run VM fault and XNACK scenarios where available. Check invalid address capture, VMID/VFID attribution, page exception status, and queue write-pointer poll page exception bits.
- Exercise SR-IOV/PF-VF paths if hardware/firmware support is available, especially active function ID, virtual reset request, IOV violation logs, and VF-attributed RAS/poison fields.
- Run RAS and poison injection or emulation tests where supported. Validate ECC/parity/poison status decoding and ensure error reporting points to the expected SDMA engine and VM/VF context.
- Use power-management and clock-gating tests around SDMA activity. Verify MGCG/CGCG status changes are plausible and no queue stalls appear during clock transitions.
- Use performance counter sampling under SDMA load. Confirm counters move plausibly and selected events/modes do not report impossible or stuck values.

## Cross-Chunk Notes

The previous chunk owns the beginning of `SDMA0_SDMA_QUEUE6` and the early `SDMA0_SDMA_QUEUE6_SCHEDULE_CNTL` field definitions. This chunk continues queue 6, fully covers queues 7-9, covers SDMA0 hypervisor/PSP/perf/power field groups, and starts the SDMA1 global block. The next chunk must complete `SDMA1_SDMA_QUEUE0_RB_CNTL` and continue the SDMA1 queue field families.

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002593_research.md`; whole-file research for `gc_12_1_0_sh_mask.h` should be produced later by merging all chunk documents for the source file.

### subset-b-002594: lines 4997-7586

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 4997-7586

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `__MASK` value used by AMDGPU register helpers to compose or decode 32-bit register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the middle of `SDMA1_SDMA_QUEUE0_RB_CNTL`, immediately after the queue-0 `RB_ENABLE` mask, and continue through the rest of SDMA1 queue 0 plus complete replicated SDMA1 queue definitions for queues 1 through 9. The chunk then enters `CHIP_XCD_gfxip_xcc_gfx_cpwd_sdma_sdmahypdec:1`, defining SDMA1 virtualization/context register fields, context/public register classification bitmaps, and ending in the `SDMA1_SDMA_PUB_REG_TYPE1` shift-only portion at `SDMA_DCC_CNTL`.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP. It is not Ceph filesystem logic.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 registers. Driver code pairs these macros with register addresses from the matching `gc_12_1_0_offset.h` header and uses field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to avoid open-coded bit positions.

This chunk is centered on SDMA1 queue and virtualization metadata:

- SDMA1 queue ring buffer control fields for ring enable, ring size, write-pointer polling, byte swapping, MCU write-pointer polling, read-pointer writeback, privilege, and VMID assignment.
- Queue base, read pointer, write pointer, read-pointer writeback address, indirect-buffer control/base/size, doorbell, context-save-area address, scheduling, preemption, write-pointer polling, AQL, context switch, mid-command, utilization, MQD, and context status fields.
- Replicated queue field groups for queues 0 through 9. Queue 0 starts partially in this chunk; queues 1 through 9 are complete within the range.
- SDMA1 hypervisor/context fields for VM context address, active virtual function identity, VM context privilege/VMID/memory type, and virtual reset requests.
- Register type bitmap fields that classify which SDMA queue/public registers belong to context or public register save/restore groups.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion offset header as `regSDMA1_*` macros.
- AMDGPU consumers use these through field packing/extraction helpers, MMIO accessors, indexed register access, queue MQD programming, suspend/resume save-restore logic, debug dumps, reset paths, and virtualization code.

The main macro families in this slice are:

- `SDMA1_SDMA_QUEUE{0..9}_RB_CNTL`: queue ring setup. Fields include `RB_ENABLE`, `RB_SIZE`, `WPTR_POLL_ENABLE`, `RB_SWAP_ENABLE`, `WPTR_POLL_SWAP_ENABLE`, `MCU_WPTR_POLL_ENABLE`, `RPTR_WRITEBACK_ENABLE`, `RPTR_WRITEBACK_SWAP_ENABLE`, `RPTR_WRITEBACK_TIMER`, `RB_PRIV`, and `RB_VMID`. For queue 0, this chunk includes masks but the first shifts are in the previous chunk.
- `SDMA1_SDMA_QUEUE{0..9}_RB_BASE`, `RB_BASE_HI`, `RB_RPTR`, `RB_RPTR_HI`, `RB_WPTR`, and `RB_WPTR_HI`: low/high ring base and pointer fields. Most are full 32-bit data or offset fields.
- `SDMA1_SDMA_QUEUE{0..9}_RB_RPTR_ADDR_LO/HI` and `RB_WPTR_POLL_ADDR_LO/HI`: memory addresses used for read-pointer writeback and write-pointer polling. Low parts use an address shift of 2 with `0xFFFFFFFC` alignment masks.
- `SDMA1_SDMA_QUEUE{0..9}_IB_CNTL`, `IB_RPTR`, `IB_OFFSET`, `IB_BASE_LO/HI`, and `IB_SIZE`: indirect-buffer enable, byte swapping, inside-IB switching, command VMID, privilege, pointer, base, and size fields.
- `SDMA1_SDMA_QUEUE{0..9}_DOORBELL`, `DOORBELL_LOG`, and `DOORBELL_OFFSET`: doorbell enable/capture, logged doorbell data/error, and offset fields.
- `SDMA1_SDMA_QUEUE{0..9}_CSA_ADDR_LO/HI`: context-save-area address fields.
- `SDMA1_SDMA_QUEUE{0..9}_SCHEDULE_CNTL`: global, process, local, and context-quantum scheduling selectors.
- `SDMA1_SDMA_QUEUE{0..9}_IB_SUB_REMAIN`, `PREEMPT`, `DUMMY_REG`, and `MINOR_PTR_UPDATE`: remaining IB sub-size, IB preemption, scratch/dummy data, and minor pointer update enable.
- `SDMA1_SDMA_QUEUE{0..9}_RB_AQL_CNTL`: AQL mode, packet size, packet step, mid-command preempt, data restore, and overlap enable fields.
- `SDMA1_SDMA_QUEUE{0..9}_CONTEXT_SWITCH_STATUS`: queue exception/status bits for RB preempt, VM hole, page fault, command timeout, queue hang, doorbell error, SRAM ECC, DRAM ECC, and write-pointer less than read-pointer conditions.
- `SDMA1_SDMA_QUEUE{0..9}_MIDCMD_CNTL` and `MIDCMD_DATA0..10`: mid-command preemption state and captured command data.
- `SDMA1_SDMA_QUEUE{0..9}_UTILIZATION_LO/HI`, `WAIT_UNSATISFIED_THD`, `MQD_BASE_ADDR_LO/HI`, `MQD_CONTROL`, and `CONTEXT_STATUS`: utilization counters, wait threshold, MQD address/control, and selected/use-IB/idle/expired/valid/error/exception/wait-for-idle/ready state.
- `SDMA1_SDMA_VM_CTX_LO/HI`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, and `VIRT_RESET_REQ`: hypervisor/virtualization context address, VF/PF identification, VMID and memory attributes, busy reporting, and reset request masks.
- `SDMA1_SDMA_CONTEXT_REG_TYPE0/1/2`: bitmap classification for context state. Type 0 covers queue-0 ring, IB, doorbell, scheduling, preempt, AQL, context switch, and mid-command control registers; type 1 covers mid-command data, utilization, MQD, context status, dummy registers, and reserved bits; type 2 is fully reserved in this chunk.
- `SDMA1_SDMA_PUB_REG_TYPE0` and partial `SDMA1_SDMA_PUB_REG_TYPE1`: bitmap classification for public SDMA registers such as decoder start, MCU control, ucode revision, timestamps, power/control/cache/chicken bits, read-pointer fetch, program/status/control/freezing/quantum/watchdog/queue-status/atomic/DCC registers.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 12.1.0 register headers for the active ASIC generation.
2. Use a queue and SDMA instance to select the matching `regSDMA1_SDMA_QUEUE*_...` address from `gc_12_1_0_offset.h`.
3. Read, construct, or update a 32-bit register value using the `__SHIFT` and `__MASK` pairs.
4. Program or decode queue ring state, IB state, doorbells, MQD pointers, context-save addresses, AQL/mid-command preemption state, context-switch status, or virtualization metadata.
5. Feed decoded state into queue bring-up, KFD/HQD dumping, suspend/resume, reset/recovery, SR-IOV virtualization, diagnostics, and performance/status reporting.

One direct integration point in this tree is `amdgpu_amdkfd_gfx_v12_1.c`, where `get_sdma_rlc_reg_offset()` uses `regSDMA1_SDMA_QUEUE0_RB_CNTL` as the base for SDMA1 queue register offset calculations and derives per-queue spacing from the queue-0 to queue-1 register address delta. The masks in this chunk describe the fields of those addressed queue registers after the address has been selected.

For queue programming, driver code typically disables or initializes the ring, writes base and pointer addresses, configures read-pointer writeback and optional write-pointer polling, sets doorbell offset/enable, configures IB/AQL behavior, writes MQD base/control state, and finally enables scheduling/ring execution. For diagnostics and recovery, code reads context status, context switch status, utilization, pointer, doorbell log, and mid-command data fields to determine whether the queue is idle, hung, faulted, preempted, or waiting on memory/doorbell state.

For virtualization/context management, hypervisor-aware paths use the VM context address/control, active function, and virtual reset fields to identify VF/PF ownership and manage SDMA context state. The context/public register type bitmaps are not queue controls themselves; they classify registers for save/restore, isolation, or virtualization handling.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

Queue ring, IB, doorbell, MQD, context-save, AQL, scheduling, and VMID fields are persistent queue state until the driver reprograms them, a context switch replaces them, or hardware reset clears them. Bad packing of low/high base addresses, pointer offsets, VMID, privilege, or doorbell offsets can make SDMA fetch commands from the wrong memory, write back pointers to the wrong location, signal the wrong queue, or execute work under the wrong memory context.

Context status, context switch status, utilization, doorbell log, and mid-command fields are live diagnostic or hardware-updated state. Some status bits may be sticky, latched, write-one-to-clear, or volatile according to hardware rules that are not encoded in this header. The masks only define bit positions.

`SDMA1_SDMA_VM_CTX_*`, `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, and `VIRT_RESET_REQ` describe virtualization state that affects PF/VF isolation, VMID selection, memory physical/type behavior, busy reporting, and reset routing. Incorrect writes can affect more than one queue because these are SDMA1 hypervisor/context registers rather than per-queue ring fields.

`SDMA1_SDMA_CONTEXT_REG_TYPE*` and `SDMA1_SDMA_PUB_REG_TYPE*` are bitmap descriptors used to classify register groups. Their state can affect save/restore or virtualization logic if programmed or interpreted by firmware/driver flows; reserved bits must be preserved or ignored according to the hardware contract.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` provides matching `regSDMA1_*` addresses. Queue 0 starts at `regSDMA1_SDMA_QUEUE0_RB_CNTL`, queue 1 starts at `regSDMA1_SDMA_QUEUE1_RB_CNTL`, and the hypervisor/context registers in this chunk are at the `0x58b*` offset range with base index 1.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12_1.c` uses SDMA0/SDMA1 queue register bases and per-queue spacing to dump or access SDMA HQD/RLC queue state for KFD.
- AMDGPU register helper macros and MMIO/indexed-register accessors provide the runtime mechanism for setting and extracting these fields.
- SDMA, KFD compute scheduling, HQD/MQD setup, doorbell management, queue preemption, reset/recovery, suspend/resume, SR-IOV virtualization, diagnostics, and performance/status paths rely on these bit assignments.

Integration points include queue ring allocation and enablement, read/write pointer handling, read-pointer writeback buffers, doorbell offset allocation, IB dispatch, AQL queues, mid-command preemption and restore, utilization accounting, queue context switching, MQD placement, VMID assignment, VF/PF attribution, virtual reset routing, and register save/restore classification.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading queue status.
- The chunk begins mid-register. The `SDMA1_SDMA_QUEUE0_RB_CNTL__RB_ENABLE` shift and mask are in the previous chunk, so final per-file reconciliation must merge adjacent chunks for complete queue-0 `RB_CNTL` coverage.
- The chunk ends mid-register family. `SDMA1_SDMA_PUB_REG_TYPE1` masks and later public register type fields continue after line 7586.
- Queue groups are repetitive but offset-sensitive. Assuming queue symmetry without using the generated offsets can target the wrong queue, especially when code computes per-queue spacing.
- Low address fields often require 4-byte alignment via `ADDR__SHIFT 0x2` and `0xFFFFFFFC` style masks. Packing raw byte addresses incorrectly can drop low bits or program an invalid address.
- `RB_VMID`, `CMD_VMID`, `MQD_CONTROL__VMID`, `RB_PRIV`, and `IB_PRIV` affect memory context and privilege. Incorrect values can cause VM faults, isolation failures, or work execution under the wrong address space.
- Doorbell fields have both enable/captured status and offset/log fields. Confusing offset units or stale captured/log bits can produce missed queue submissions or misleading fault attribution.
- Context switch status contains exception bits for VM hole, page fault, timeout, hang, doorbell error, ECC, and pointer ordering. These bits may need hardware-specific clearing and should not be treated as passive read-only metadata without checking the programming guide.
- Mid-command preemption fields and `MIDCMD_DATA0..10` capture in-flight command state. Writing or restoring them with stale data can corrupt resumed SDMA work.
- AQL and overlap/mid-command restore controls change queue execution semantics. Incorrect enablement can break compute queues that expect packetized AQL behavior or preemption restore support.
- Hypervisor fields are broader than one queue. `ACTIVE_FCN_ID`, `VM_CTX_CNTL`, and `VIRT_RESET_REQ` mistakes can affect PF/VF isolation and reset behavior.
- `CONTEXT_REG_TYPE*` and `PUB_REG_TYPE*` contain reserved fields. Full-register writes must preserve reserved bits unless a hardware-defined sequence says otherwise.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_sh_mask.h`, especially GC 12.1.0 SDMA, KFD, queue, doorbell, reset, virtualization, and diagnostics paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database to confirm every `__SHIFT` and `__MASK` value in lines 4997-7586.
- Cross-check that every register in this chunk has a matching `regSDMA1_*` address in `gc_12_1_0_offset.h`, and that queue-to-queue spacing remains consistent for queues 0 through 9.
- Static mask/shift sanity checks: masks should align with shifts, full-width fields should use `0xFFFFFFFFL`, aligned address fields should keep low-bit masks clear, and replicated queue families should remain structurally identical where intended.
- SDMA queue bring-up tests that program ring base, size, read/write pointers, read-pointer writeback, write-pointer polling, doorbells, IB controls, AQL controls, MQD base/control, and scheduling fields, then submit known copy/fill workloads.
- KFD/HQD dump tests that verify `amdgpu_amdkfd_gfx_v12_1.c` reads the expected SDMA1 queue registers and decodes queue state consistently across queue IDs.
- Fault-injection or recovery tests that exercise VM hole, page fault, command timeout, queue hang, doorbell error, ECC, write-pointer less-than-read-pointer, preemption, and context-status decode.
- Doorbell tests that validate offset programming, enable/capture behavior, logged data, and queue wakeup across SDMA1 queues.
- Preemption and context-switch tests that validate `IB_PREEMPT`, mid-command data capture/restore, `CONTEXT_STATUS`, and `CONTEXT_SWITCH_STATUS` transitions.
- Virtualization/SR-IOV tests that validate active VF/PF identification, VM context address/control, busy reporting, and virtual reset request behavior without cross-function leakage.
- Suspend/resume or GPU reset tests that verify context/public register type bitmaps select the right SDMA queue/public state for save/restore.
- Runtime warning signals include SDMA queues that fail to start, stale read/write pointers, doorbells that do not wake queues, repeated VM faults, incorrect VMID attribution, stuck preemption, false hang reports, corrupted resumed work after mid-command restore, or VF/PF reset leakage.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002594`. It covers lines 4997-7586 of `gc_12_1_0_sh_mask.h`. The final per-file research should merge this with the previous chunk for the start of `SDMA1_SDMA_QUEUE0_RB_CNTL` and with the next chunk for the remainder of `SDMA1_SDMA_PUB_REG_TYPE1` and later SDMA1 public/VM fields.

### subset-b-002595: lines 7587-10032

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 7587-10032

## Scope

This chunk is a middle slice of the generated AMD GC 12.1.0 shift/mask header. It contains C preprocessor constants only: each register field is represented by a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The slice starts inside `SDMA1_SDMA_PUB_REG_TYPE1`: the first visible line is the `SDMA_UTCL1_WARMUPL2_CNTL` shift field, while earlier fields for the same register live in the previous chunk. It then covers the rest of SDMA1 public, instruction-cache, performance-counter, and clock-gating fields; GRBM status/reset/error/virtualization fields; CP command processor status, queue, interrupt, debug, and violation fields; graphics pipeline/primitive assembler status and UTCL1 fields; and the beginning of the compute dispatch register block. The final visible line is only `COMPUTE_WAVE_RESTORE_ADDR_LO__ADDR__SHIFT`; its matching mask and the following compute relaunch fields are in the next chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for AMD graphics IP and is unrelated to Ceph filesystem client behavior.

## Purpose

`gc_12_1_0_sh_mask.h` is the bitfield contract for GC 12.1.0 registers. AMDGPU code combines these symbols with matching register offset macros to compose register writes and decode register reads without open-coded shifts and hex masks in driver logic.

This chunk specifically documents field layouts for:

- `SDMA1` public register type maps, VM/MCU/instruction-cache controls, SDMA performance counter selection/result registers, and SDMA medium-grain clock-gating override bits.
- GRBM control, status, per-shader-engine status, power request, soft reset, read/write/IOV error reporting, trap/fence/scratch registers, interrupt credits, UTCL2 invalidation ranges, clock-gating chicken bits, shader-array disable masks, and async VF violation data.
- CP/CPC/CPF status, busy, stalled, queue, ROQ/STQ/MEQ threshold and availability registers, interrupt debug status, debug-index/data windows, ring read pointer and write-pointer polling controls, context state, command-index/data windows, and private violation address reporting.
- PA/VGT/GE front-end fields, including FIFO depths, UTCL1 status/control, watchdog/distributor busy bits, graphics pipe control, geometry reset/debug toggles, front-end data errors, and shader-array disable masks.
- Compute dispatch state, including dispatch initiator flags, grid dimensions, starting coordinates, thread counts, program and scratch addresses, `COMPUTE_PGM_RSRC*` shader resource fields, VMID, resource limits, temporary ring size, restart coordinates, request-control throttles, user accumulators, checksum/DDID/interleave fields, XCC and threadgroup restart/chunk registers, CU destination/static-thread masks, user-data registers, and relaunch payload fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for a field.
- `REGISTER__FIELD_MASK` gives the unshifted bit mask occupying the register's field bits.
- Callers typically write values by masking and shifting through AMDGPU helper macros, then passing the composed value to SOC15/MMIO or command-packet register accessors using matching offset definitions from `gc_12_1_0_offset.h`.

Important visible macro families include:

- SDMA1 register grouping and control masks: `SDMA1_SDMA_PUB_REG_TYPE1..3`, `SDMA1_SDMA_VM_CNTL`, `SDMA1_SDMA_MCU_CNTL`, `SDMA1_SDMA_IC_BASE_{LO,HI,CNTL}`, `SDMA1_SDMA_IC_OP_CNTL`, and `SDMA1_SDMA_IC_CNTL`.
- SDMA1 performance controls: `SDMA1_SDMA_PERFCNT_PERFCOUNTER0..2_CFG`, `SDMA1_SDMA_PERFCNT_PERFCOUNTER_RSLT_CNTL`, `SDMA1_SDMA_PERFCNT_MISC_CNTL`, `SDMA1_SDMA_PERFCOUNTER0..5_SELECT`, matching `SELECT1` registers, and low/high result registers.
- GRBM fields: `GRBM_CNTL`, `GRBM_STATUS`, `GRBM_STATUS2`, `GRBM_STATUS3`, `GRBM_STATUS_SE0/SE1`, `GRBM_SOFT_RESET`, `GRBM_READ_ERROR`, `GRBM_READ_ERROR2`, `GRBM_WRITE_ERROR`, `GRBM_IOV_ERROR_FIFO`, `GRBM_INVALID_PIPE`, `GRBM_RSMU_READ_ERROR`, `GRBM_PWR_CNTL*`, `GRBM_FENCE_RANGE*`, `GRBM_CHICKEN_BITS*`, `GRBM_SCRATCH_REG0..7`, and `GRBM_INTF_CNTL`.
- CP fields: `CP_CPC_STATUS`, `CP_CPC_BUSY_STAT*`, `CP_CPC_STALLED_STAT1`, `CP_CPF_STATUS`, `CP_CPF_BUSY_STAT*`, `CP_CPF_STALLED_STAT1`, `CP_STALLED_STAT1..3`, `CP_BUSY_STAT`, `CP_STAT`, `CP_CSF_STAT`, `CP_CNTX_STAT`, `CP_ROQ*`, `CP_STQ*`, `CP_MEQ*`, `CP_INT_STAT_DEBUG`, `CP_DEBUG_*`, and `CP_PRIV_VIOLATION_ADDR*`.
- PA/GE/VGT fields: `VGT_DMA_DATA_FIFO_DEPTH`, `VGT_DMA_REQ_FIFO_DEPTH`, `VGT_DRAW_INIT_FIFO_DEPTH`, `IA_UTCL1_STATUS_2`, `WD_UTCL1_CNTL`, `WD_UTCL1_STATUS`, `IA_UTCL1_CNTL`, `IA_UTCL1_STATUS`, `GE_WD_CNTL_STATUS`, `GE_FED_STATUS`, `GE_PRIV_CONTROL`, `GE_STATUS`, `GFX_PIPE_CONTROL`, and `VGT_RESET_DEBUG`.
- Compute fields: `COMPUTE_DISPATCH_INITIATOR`, `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_NUM_THREAD_*`, `COMPUTE_PGM_*`, `COMPUTE_DISPATCH_*`, `COMPUTE_PGM_RSRC1/2/3`, `COMPUTE_VMID`, `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_TMPRING_SIZE`, `COMPUTE_RESTART_*`, `COMPUTE_REQ_CTRL`, `COMPUTE_USER_ACCUM_*`, `COMPUTE_DESTINATION_EN_SE0..3`, `COMPUTE_STATIC_THREAD_MGMT_SE0..8`, `COMPUTE_USER_DATA_0..31`, `COMPUTE_RELAUNCH`, `COMPUTE_RELAUNCH_STATE_PAYLOAD`, and the first field of `COMPUTE_WAVE_RESTORE_ADDR_LO`.

## Control Flow

This header has no runtime control flow. It contributes compile-time macro substitution only.

The implied driver flow is in AMDGPU consumers:

1. Select the GC 12.1.0 register family for the active ASIC/IP version.
2. Use an offset macro from the matching offset header to choose a register.
3. Use these shift/mask macros to insert or extract only the intended fields.
4. Read, write, poll, or packet-program the register through the appropriate SOC15, MMIO, command processor, debug, perf, or reset path.
5. Apply sequencing outside this header: idle checks before reset, safe windows before clock-gating writes, event selection before performance-counter enablement, queue setup before command processor polling, and dispatch packet/resource programming before compute launch.

For SDMA performance counters, the expected flow is to program select/config fields, clear counters, enable collection, run a workload, and read low/high result registers with the hardware's required latching rules. For GRBM and CP status fields, reset, hang-dump, debugfs, and scheduler paths read status/busy/stall bits to decide whether engines are idle, blocked, or faulted. For compute dispatch, firmware or command processor programming writes dimensions, addresses, resource limits, and launch/relaunch payloads as a coherent state bundle rather than as independent casual toggles.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe bit positions in GPU registers whose values are owned by hardware, firmware, and AMDGPU runtime code.

SDMA performance select/config registers persist as profiling setup until cleared, reprogrammed, reset, or power-gated. Result low/high fields expose accumulation state and may require a documented snapshot sequence to avoid torn 64-bit samples. `ENABLE`, `CLEAR`, trigger, compare, and saturate fields are command-like and can have side effects when written.

GRBM status registers expose live global and per-SE engine state, including busy, clean, pending, active, idle, and credit conditions. GRBM soft-reset fields are destructive control state for CP, RLC, UTCL2, GFX, CPF/CPC/CPG, CAC, CANE, EA, and SDMA engines. Error fields such as read/write/IOV/invalid-pipe/RSMU/async-VF registers may be sticky diagnostics and can encode requester IDs, VF/VFID, VMID, pipe, queue, SSRCID, address, TMZ, overflow, and valid bits.

CP/CPC/CPF status, busy, stalled, queue, and pointer fields represent live command processor state. Queue threshold and polling controls can affect command fetch behavior and scheduling latency. Debug index/data windows and command index/data windows are stateful access mechanisms: selecting an index and then reading or writing data has different semantics from reading a passive status register.

PA/VGT/GE and UTCL1 fields expose front-end pipeline state and virtual-memory fault/retry/PRT diagnostics. UTCL1 controls such as drop, bypass, invalidate, force snoop, fragment-limit, VMID reset, and MTYPE override can affect memory translation behavior and must be sequenced with TLB/cache policy.

Compute dispatch registers are launch state. Program address, scratch base, VMID, dimensions, thread counts, resource usage, LDS/scratch/user-SGPR configuration, CU targeting, user data, and relaunch payloads must remain mutually consistent for the lifetime of a dispatch or resume operation. Bad field composition can launch the wrong shader, use the wrong address space, corrupt scratch, over-allocate wave resources, misroute work to disabled CUs, or mis-restore waves.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register family remaining synchronized:

- `gc_12_1_0_offset.h` supplies the matching register offsets for the names whose fields are described here.
- Other generated GC 12.1.0 headers, such as default-value headers when present, must agree with these field names and masks.
- AMDGPU SOC15/MMIO helpers consume the composed register values.
- GFX, SDMA, CP, KFD/compute, reset, virtualization, power-management, perf counter, debugfs, hang-dump, interrupt, and memory-management paths consume the represented fields indirectly.

Important integration points include SDMA queue and performance monitoring, SDMA instruction-cache management, GRBM idle/reset/error reporting, SR-IOV and VF violation diagnostics, interrupt-credit management, UTCL2 invalidation range setup, CP queue and ring diagnostics, CP interrupt decoding, front-end geometry and IA/WD virtual-memory status, thread-trace/perf status, compute shader dispatch setup, and wave relaunch/restore support.

Because this is a shift/mask header, most correctness is relational. Every visible field must match the actual hardware register database, the same register's offset definition, any generated default, and the consumers' assumptions about access width, write-one-to-clear behavior, reserved bits, and sequencing. A field name or mask can be wrong while still compiling cleanly.

## Risks And Edge Cases

- Generated-header drift is the main risk. Incorrect shifts or masks silently encode the wrong bits into hardware registers or decode misleading status from hardware reads.
- The chunk begins and ends on partial registers. `SDMA1_SDMA_PUB_REG_TYPE1` is missing earlier shift definitions in this slice, and `COMPUTE_WAVE_RESTORE_ADDR_LO` is missing its mask in this slice. Whole-register conclusions must be deferred to the merged per-file report.
- Repetitive families are similar but not identical. SDMA perf counter config registers, select/select1 registers, GRBM status variants, CP queue status registers, UTCL1 IA/WD status registers, and compute SE/CU masks have different field widths and gaps that should not be inferred by symmetry alone.
- Low/high result and address pairs are vulnerable to torn reads or inconsistent writes if consumers ignore hardware latching, alignment, and ordering requirements.
- Full-register writes can clobber reserved fields. This is especially risky for clock-gating controls, chicken bits, debug/reset registers, and compute resource descriptors.
- Reset and power fields have side effects. `GRBM_SOFT_RESET`, `GRBM_PWR_CNTL*`, `GFX_PIPE_CONTROL`, `SDMA1_GFX_ICG_SDMA_CTRL`, and front-end disable/debug fields should only be written in hardware-defined safe windows.
- Error and violation fields are security-sensitive in virtualized environments. GRBM/CP private violations, async VF data, IOV FIFO entries, VFID/VMID/SSRCID values, and address fields may affect PF/VF attribution and isolation diagnostics.
- Debug index/data and command index/data pairs require selection state. Reading the data register without selecting the intended index can produce stale or unrelated data.
- Compute launch fields are tightly coupled. Address high masks, VMID width, resource limits, LDS size, SGPR/VGPR counts, scratch enablement, user data, CU targeting, and relaunch state must match compiler metadata and packet contents.
- UTCL1 status/control fields are live memory-translation diagnostics and controls. Fault/retry/PRT status can be transient or sticky, while invalidate/bypass/drop/snoop fields can change forward progress or fault behavior.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware/runtime behavior:

- Build coverage for AMDGPU files that include GC 12.1.0 register headers, especially SDMA, GFX, CP, compute/KFD, reset, virtualization, power-management, debugfs, and perf counter paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database for every `__SHIFT` and `_MASK` macro in lines 7587-10032.
- Cross-header checks that every register field here has a matching register offset in `gc_12_1_0_offset.h` and that any defaults in the generated family use the same field layout.
- Static consistency checks for repeated families: SDMA perf counter config/select/result patterns, low/high pairs, GRBM status and error field widths, CP queue pointer widths, UTCL1 IA/WD status equivalence, compute X/Y/Z thread-count layouts, and `COMPUTE_USER_DATA_0..31` full-width fields.
- Runtime SDMA perf tests that select events, clear and enable counters, run copy workloads, and verify low/high counter movement and saturation/trigger behavior.
- Reset and idle tests that poll GRBM/CP busy fields before and after engine reset, suspend/resume, GPU reset recovery, and clock-gating transitions.
- Virtualization tests that provoke or emulate privileged access violations and verify GRBM/CP VF/VFID/VMID/SSRCID/address decoding.
- CP scheduler and hang-dump tests that validate ROQ/STQ/MEQ pointer, threshold, busy, stalled, interrupt-debug, and private-violation decoding under known queue workloads.
- UTCL1 fault/retry/PRT tests for IA and WD paths, checking VMID/UTCL1ID/instance attribution and invalidate/drop/bypass sequencing.
- Compute dispatch tests that launch kernels with varying dimensions, partial threadgroups, scratch/LDS/VGPR/SGPR usage, user data, CU masks, W32/WGP modes, and relaunch/restore paths, then verify correct execution and coherent hang/debug dumps.
- Warning signals include nonsensical busy/stall state, counters stuck at zero under active workloads, hangs after clock-gating or reset changes, misattributed VF violations, invalid UTCL1 fault attribution, bad compute dispatch resource sizing, or register traces showing writes outside documented masks.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002595`. It covers lines 7587-10032 of `gc_12_1_0_sh_mask.h`. The final per-file report should merge it with adjacent chunks so `SDMA1_SDMA_PUB_REG_TYPE1` and `COMPUTE_WAVE_RESTORE_ADDR_LO` are represented as complete registers and so earlier/later GC 12.1.0 SDMA, GRBM, CP, PA, shader, and compute field families can be described at whole-file scope.

### subset-b-002596: lines 10033-12490

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 10033-12490

## Scope

This chunk covers lines 10033-12490 of the generated GC 12.1.0 register shift/mask header. It starts at the low word of `COMPUTE_WAVE_RESTORE_ADDR_LO`, continues through the GC CPWD CAC/EDC/throttle, GC EA CPWD, GCR, and CP decoder address blocks, and ends inside `CP_GFX_HQD_QUE_MGR_CONTROL`.

The slice contains 2,158 `#define` constants for 289 registers. It is a macro-only register metadata file: there are no functions, structs, enums, or executable algorithms in this range.

## Purpose

The header gives AMDGPU and KFD code the bit positions and masks needed to program GC 12.1 hardware registers without embedding numeric bitfields in driver logic. Each hardware field is represented as a `REGISTER__FIELD__SHIFT` and matching `REGISTER__FIELD_MASK` pair, consumed by helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15_PREREG`, and direct mask operations.

The covered range is behaviorally important because it describes command-processor queue state, interrupt enable/status fields, CP translation/cache fault reporting, graphics HQD/MQD ring state, and GC-wide current/activity/throttle controls. Incorrect constants here would not usually fail at type-check time; they would instead surface as misprogrammed MMIO/MQD words, wrong interrupt routing, queue hangs, bad power throttling, or misleading diagnostics.

## Important Definitions

- Compute relaunch tail: `COMPUTE_WAVE_RESTORE_ADDR_{LO,HI}`, `COMPUTE_RELAUNCH2`, `COMPUTE_RELAUNCH2_STATE_PAYLOAD`, `COMPUTE_DISPATCH_TUNNEL`, `COMPUTE_DISPATCH_END`, `COMPUTE_NOWHERE`, `SH_RESERVED_REG0/1`, and `COMPUTE_PREALLOC_CR_DB_BUFFER_SIZE`.
- GC CAC/EDC/throttle direct block: `GC_CAC_CTRL_1/2`, GC and SE aggregate counters, `GC_CAC_OVR_VAL_{LOWER,UPPER}`, `GC_EDC_CTRL`, `GC_EDC_STRETCH_CTRL`, EDC threshold and hysteresis registers, `GC_THROTTLE_CTRL{,1,2}`, EDC/PCC/PWRBRK/DIDT stall pattern registers, performance counters, status/overflow registers, clock monitor control, soft snapshot control, per-client CAC weights for CP, PMM, SDMA, CHC, RLC, GRBM, and GLARB, `XCD_TOTAL_CAC_AGGR_*`, `GC_EDC_WEIGHTED_DATA_MULTIPLIER`, and `GC_CAC_IND_INDEX/DATA`.
- GC EA CPWD block: `GC_EA_CPWD_VC_MAP`, SDP arbitration/priority/credit and reservation registers, request-control fields, link-manager misc/status, error status, backdoor command/data credit windows and write mirrors, invalid opcode logging, poison/parity error injection and logs, and `GC_EA_CPWD_SDP_ENABLE`.
- GCR block: `GCR_PIO_CNTL/DATA` and `GCR_NHTOE_CNTL/DATA`, including data-index, done/reset, response-tag, response-done, and ready fields.
- CP decoder and command-processor control: `CPC_INT_ADDR1`, CU mask address/control registers, `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, CPC interrupt address/info/PASID, `CP_VIRT_STATUS`, `CP_GFX_ERROR`, `CPG/CPC/CPF_UTCL1_CNTL`, ring-base/control/pointer registers, buffer-size masks, `GC_PRIV_MODE`, `CP_INT_CNTL`, `CP_INT_STATUS`, device ID, priorities, fatal errors, VMID fields, doorbell ranges, FED status, IB counters, `CP_INT_CNTL_RING0`, debug registers, F32 interrupt maps, `CP_PWR_CNTL`, ECC first-occurrence registers, `GB_EDC_MODE`, and PQ write-pointer polling.
- MEC/ME1 interrupt and scheduling fields: `CP_ME1_PIPE{0..3}_INT_CNTL`, matching `*_INT_STATUS`, `CP_ME1_INT_STAT_DEBUG`, `CP_GFX_QUEUE_INDEX`, `CC_GC_EDC_CONFIG`, ME1 pipe priority counters/priorities, firmware program-counter and interrupt-routine start registers, `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, IQ wait timers, VMID reset/preempt/status, suspend/resume context-save and stack fields, and DDID base/control/counter registers.
- Graphics HPD/HQD/MQD fields at the end: `CP_GFX_HPD_STATUS0`, `CP_GFX_HPD_CONTROL0`, OSPRE fence address/data registers, `CP_GFX_INDEX_MUTEX`, high program-counter/routine-start fields, `CP_GFX_MQD_BASE_ADDR{,_HI}`, `CP_GFX_HQD_ACTIVE`, VMID, priority, quantum, ring base/read/write pointers, RPTR writeback address, WPTR poll address, `CP_RB_DOORBELL_CONTROL`, `CP_GFX_HQD_CNTL`, `CP_GFX_HQD_DEQUEUE_REQUEST`, `CP_GFX_HQD_MAPPED`, and the beginning of `CP_GFX_HQD_QUE_MGR_CONTROL`.

## Control Flow

This chunk has no runtime control flow. Its effect is compile-time macro substitution into MMIO and MQD programming code.

Representative consumers in this tree include:

- `gfx_v12_1.c`, which includes `gc_12_1_0_sh_mask.h` and uses `CP_INT_CNTL_RING0` fields to enable or disable GUI idle, private-register, private-instruction, and user-trap related interrupts per XCC.
- `amdgpu_amdkfd_gfx_v12_1.c`, which includes this header for KFD-facing queue management and writes `regCPC_INT_CNTL` with `CP_INT_CNTL_RING0__TIME_STAMP_INT_ENABLE_MASK` and `CP_INT_CNTL_RING0__OPCODE_ERROR_INT_ENABLE_MASK`.
- `kfd_mqd_manager_v12_1.c`, which includes this header while constructing GC 12.1 KFD MQDs. This particular line range contributes graphics HQD/MQD and shared CP-style field definitions; adjacent lines in the same header cover the compute HQD fields used directly by the KFD MQD manager.
- `gfx_v12_0.c` uses the same style of `CP_RB_DOORBELL_CONTROL` and `CP_GFX_HQD_CNTL` field programming for graphics ring setup. GC 12.1 code follows the same helper conventions with 12.1 register names and XCC instance selection.
- `imu_v12_0.c` programs golden values for several `GC_EA_CPWD_*` registers. The masks in this chunk describe the layout of those CPWD SDP arbitration, credit, reserve, priority, misc, and enable values.

The runtime pattern is normally: choose the matching offset macro from `gc_12_1_0_offset.h`, read or initialize a 32-bit register value, use these field masks/shifts to compose or decode it, then write or inspect the MMIO register through SOC15 register helpers.

## State and Persistence

The header does not store state itself, but it describes persistent hardware state in GC MMIO registers and MQD-backed queue state.

Important state represented in this range includes:

- Compute relaunch state: wave restore address high/low words, relaunch payload flags, user accumulator payload slots, bulky/state/event flags, dispatch/end placeholders, and preallocated CR doorbell buffer size override fields.
- Power/current/throttle state: CAC enable windows, aggregate counters, software snapshots, override values, EDC enable/reset/throttle configuration, threshold and hysteresis counters, stretch/unstretch delays, EDC/PCC/PWRBRK/DIDT stall patterns, fixed-pattern counters, clock-monitor thresholds, CAC weights, and indirect CAC index/data state.
- GC EA CPWD fabric state: VC mapping, request priorities, tag/data credit pools, reservation distribution, request ordering/block-level overrides, link manager thresholds, error status, poison/parity injection controls, and invalid opcode logs.
- CP translation and fault state: CP graphics UTCL1 error bits, CPG/CPC/CPF UTCL1 controls for retry, invalidate, drop, snoop, permission override, and no-execute forcing, plus FED status fields carrying ring ID, VF ID, and PF/VF origin.
- Ring and queue state: RB base/control/read/write pointers, RPTR writeback address, WPTR poll address, VMID, process and HQD quantum, queue priority, active/mapped state, dequeue request state, queue manager controls, doorbell enable/offset/hit/drop fields, and graphics MQD base address plus application VMID.
- Interrupt state: global CP interrupt enable/status bits, ring0-specific enable/status bits, ME1 pipe interrupt enable/status mirrors, F32 interrupt cause bits, timestamp/opcode/privileged-access/error interrupt fields, and debug assertion status.
- Suspend/resume and DDID state: context-save base/size/control, stack and workgroup-state offsets, OS pipe masks, suspend/resume requests, DDID base/control, inflight count, write/read pointers, and delta report counters.

Because these fields drive real hardware latches, bad masks can persist until queue teardown, engine reset, or full GPU reset. Address fields with low-bit shifts, such as CP CU mask, HPD fence, MQD base, RPTR writeback, WPTR poll, and doorbell offsets, are especially sensitive to alignment and high/low word handling.

## Dependencies and Integration Points

This header is paired with `gc_12_1_0_offset.h`, which provides `reg*` addresses and base indices. The current file only provides field layouts. Consumers depend on the naming convention that expands `REG_SET_FIELD(value, CP_GFX_HQD_CNTL, RB_BUFSZ, x)` into `CP_GFX_HQD_CNTL__RB_BUFSZ__SHIFT` and `CP_GFX_HQD_CNTL__RB_BUFSZ_MASK`.

Integration points include:

- SOC15 register accessors: `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `WREG32_FIELD15_PREREG`, and direct `RREG32/WREG32` after XCC/SRBM selection.
- KFD queue setup and dump paths: KFD selects MEC/pipe/queue with SRBM helpers, initializes queue interrupts through CPC interrupt fields, dumps HQD register windows, and builds MQDs using field definitions from this header and adjacent ranges.
- Graphics ring setup: graphics ring code programs CP RB/HQD control, ring base/pointers, doorbell control, and interrupt control fields; these masks must stay synchronized with the hardware register spec and default-value headers.
- Power-management and firmware initialization: IMU/RLC golden-value paths touch `GC_EA_CPWD_*`; CAC/EDC/THROTTLE fields integrate with GC current/activity accounting and throttling logic.
- Virtualization and isolation paths: `CP_VIRT_STATUS`, FED status, VF/PF ID fields, VMID fields, PASID/bypass-PASID fields, privileged instruction/register interrupt bits, and TMZ/non-privileged queue fields all intersect with SR-IOV, KFD process isolation, and protected memory behavior.

## Risks

- Generated-header drift is the primary risk. If the register spec or offset header changes without matching mask regeneration, driver code can write syntactically valid values into wrong fields.
- Queue programming is fragile. Wrong `CP_GFX_HQD_CNTL`, ring pointer, MQD base, VMID, quantum, or doorbell masks can cause graphics queues to fail to start, consume the wrong ring memory, miss doorbells, or corrupt read/write pointer writeback.
- Interrupt masks are high-impact. A wrong `CP_INT_CNTL_RING0` or ME1 pipe interrupt bit can suppress real faults, generate interrupt storms, or route timestamp/opcode/private access events incorrectly.
- Fault and diagnostics fields are used after hangs. Misdecoding `CP_GFX_ERROR`, UTCL1 controls/errors, FED status, ECC first-occurrence, or F32 interrupt bits can point recovery/debugging at the wrong engine or VMID.
- Power throttling and CAC fields affect performance and stability. Incorrect EDC/PCC/PWRBRK/DIDT pattern or threshold fields could over-throttle, under-throttle, or report invalid activity/power counters.
- Security-sensitive bitfields include VMID, PASID, privileged access interrupts, VF/PF status, TMZ match/state, non-privileged queue state, and protection-related UTCL1 permission/no-execute overrides. Incorrect masks can weaken diagnostics or accidentally program queues into the wrong privilege or address context.
- This chunk ends mid-family at `CP_GFX_HQD_QUE_MGR_CONTROL`; the following chunk must be consulted for the remaining HQD IQ timer/status/control and later CP fields before making complete file-level claims.

## Test Signals

Useful validation signals are mostly build and hardware integration checks:

- Compile coverage for GC 12.1 AMDGPU/KFD files that include this header, especially `gfx_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `kfd_mqd_manager_v12_1.c`, `kfd_device_queue_manager_v12_1.c`, and `mes_v12_1.c`.
- GUI idle and fault interrupt tests should show `CP_INT_CNTL_RING0` updates taking effect per XCC, with timestamp, opcode error, privileged register, and privileged instruction interrupts arriving only when enabled.
- KFD queue creation and HQD dump should produce coherent queue VMID, priority, quantum, active/mapped/dequeue state, ring base/pointers, and doorbell control values.
- Graphics ring bring-up should successfully program RB/HQD control, RPTR/WPTR state, RPTR writeback, WPTR poll, and doorbell offsets without ring-test or fence timeout.
- Suspend/resume and preemption paths should preserve context-save base/size/control, suspend request/status, DDID counters, and HPD/OSPRE fence state.
- Fault injection or error reporting should decode `CP_GFX_ERROR`, CPG/CPC/CPF UTCL1 error/control, FED status, F32 interrupts, ECC first-occurrence, GC EA CPWD poison/parity logs, and invalid opcode fields consistently with hardware events.
- Power-management smoke tests should confirm CAC/EDC aggregate counters, throttle status, stall-pattern counters, and CAC indirect index/data accesses remain stable across clock/power transitions.

### subset-b-002597: lines 12491-15118

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 12491-15118

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask header segment. It contains preprocessor constants only: each `REGISTER__FIELD__SHIFT` macro gives a bit offset, and each `REGISTER__FIELD_MASK` macro gives the corresponding 32-bit field mask. The requested range contains 2,127 `#define` entries across 474 register-name groups.

The span begins mid-register at the final `CP_GFX_HQD_QUE_MGR_CONTROL__DISABLE_MAPPED_QUEUE_IDLE_MSG_MASK` define, then covers CP graphics HQD, CP DMA watchpoints, CP status/error, compute HQD/MQD, graphics context, PF/VF, PF-only, GCR, GFXU, CP DMA, draw/dispatch, coherency, GE/VGT, and the start of MES control/status masks. It ends at the `//CP_MES_IC_OP_CNTL` comment before that register's fields, so adjacent chunks are required for complete per-register and per-file coverage.

This source tree is under a local `ceph-client` mirror, but this file is AMDGPU DRM graphics hardware metadata. It has no Ceph or distributed filesystem behavior.

## Purpose

`gc_12_1_0_sh_mask.h` publishes bit layouts for GC 12.1.0 registers. AMDGPU, KFD, MES, GFXHUB, IMU, SDMA, and SOC code include this header together with `gc_12_1_0_offset.h` so they can compose register values, extract status bits, and keep ASIC-specific field positions out of hand-written driver logic.

This chunk's main purposes are:

- Describe queue-manager, HQD, MQD, doorbell, PQ/IB/IQ/EOP, dequeue, suspend, AQL, dispatch-id, kernel-dispatch, and GDS fields used by compute and graphics queue setup.
- Describe CP DMA watchpoint, DMA command, scratch, append/atomic, indirect-buffer, wait, coherency, fence, and pipeline-statistics fields used by command processor programming and diagnostics.
- Describe CP/CPF/CPG/CPC busy, UTCL1 fault/retry/PRT, fed-error, ring-buffer, SDMA arbitration, soft-reset, ME/MEC control, unmapped queue, PF-only DFY/HPD/GCR, and MES fields used for debug, reset, virtualization, and firmware control.
- Describe graphics context and draw-state fields for VGT/GE, including draw initiator, DMA/index type, shader stages, tessellation, streamout, primitive type, VRS, geometry throttling, user VGPRs, and primitive-id reset.
- Describe GFXU statistics, scratch, EOP done, append/atomic, metadata, indirect draw/dispatch, coherency destination, RLC perf counter, and GRBM index fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, callbacks, locks, allocations, or executable branches in this chunk. The exported interface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` is the left-shift count used when packing a field value into a register word or after masking/extracting a field.
- `REGISTER__FIELD_MASK` is the bit mask for the field in the register word.
- Address-block comments divide related register groups, including `CHIP_XCD_gfxip_xcc_gfx_cpwd_cpwd_cpphqddec`, `gfxdec0`, `pfvf_cpdec`, `pfvf_grbmdec`, `pfonly_cpdec`, `pfonly_cpphqddec`, `pfonly_gcrdec`, `gfxudec`, and `cprs64dec`.

Important register groups in this range include:

- Queue and descriptor state: `CP_GFX_HQD_IQ_TIMER`, `CP_GFX_HQD_HQ_STATUS0`, `CP_GFX_MQD_CONTROL`, `CP_HQD_ACTIVE`, `CP_HQD_VMID`, `CP_HQD_PERSISTENT_STATE`, `CP_HQD_PQ_CONTROL`, `CP_HQD_PQ_DOORBELL_CONTROL`, `CP_HQD_IB_CONTROL`, `CP_HQD_IQ_TIMER`, `CP_HQD_DEQUEUE_REQUEST`, `CP_HQD_DMA_OFFLOAD`, `CP_HQD_OFFLOAD`, `CP_HQD_HQ_SCHEDULER0`, `CP_HQD_HQ_STATUS0`, `CP_HQD_EOP_CONTROL`, `CP_HQD_CTX_SAVE_CONTROL`, `CP_HQD_ERROR`, `CP_HQD_AQL_CONTROL`, `CP_HQD_AQL_CONTROL_1`, and `CP_HQD_KD_CNTL`.
- Address and pointer fields for queue backing memory: `CP_MQD_BASE_ADDR`, `CP_HQD_PQ_BASE`, read/write pointer report and poll addresses, IB base, EOP base, context-save base, suspend offsets, DDID pointers, AQL dispatch IDs, KD base, EOP done addresses, pipe-stats addresses, append addresses, CP DMA source/destination/command-buffer addresses, IB/ST/DB bases and buffer sizes, metadata base, indirect draw/dispatch addresses, and index base.
- Watchpoint and status fields: four `CP_DMA_WATCH[0-3]` slots, `CP_DMA_WATCH_STAT`, `CP_PFP_JT_STAT`, `CP_MEC_JT_STAT`, busy hysteresis registers, CP fed-error address registers, doorbell clear/status, RCIU CAM phases, timestamp offsets, SDMA request arbitration, UTCL1 status registers, soft-reset fields, HPD UTCL1 error/status, HPD queue status, GCR command/status, and MES exception/control status.
- Graphics frontend fields: `VGT_DRAW_INITIATOR`, `VGT_DMA_INDEX_TYPE`, `VGT_EVENT_INITIATOR`, `VGT_SHADER_STAGES_EN`, `VGT_TF_PARAM`, `VGT_TESS_DISTRIBUTION`, `VGT_LS_HS_CONFIG`, `VGT_PRIMITIVE_TYPE`, `VGT_INDEX_TYPE`, `GE_MULTI_PRIM_IB_RESET_EN`, `GE_GS_THROTTLE`, `GE_CNTL`, `GE_STEREO_CNTL`, `GE_USER_VGPR_EN`, `VGT_PRIMITIVEID_EN`, `GE_VRS_RATE`, and geometry-shader fast-launch dimensions.
- Virtualization and privileged control fields: `CP_UNMAPPED_QUEUE0` through `CP_UNMAPPED_QUEUE63`, `CP_UNMAPPED_DOORBELL`, queue banks, `GRBM_GFX_CNTL`, `CP_DFY_*`, PF-only HPD status/ROQ offsets, and PF-only `GCR_*` controls.
- MES fields at the end of the chunk: program counter start, interrupt routine/vector addresses, `CP_MES_CNTL` reset/active/halt/step bits for four pipes, pipe priorities, interrupt enables/pending state, scratch index/data, instruction pointer, machine scratch/status/EPC/cause/bad-address/IP halves.

Concrete consumers in this source tree include `gfx_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `imu_v12_1.c`, `sdma_v7_1.c`, `soc_v1_0.c`, and KFD's `kfd_mqd_manager_v12_1.c`. For example, `kfd_mqd_manager_v12_1.c` packs MQD fields with `CP_HQD_AQL_CONTROL__CONTROL0__SHIFT`, `CP_HQD_PQ_CONTROL__RPTR_BLOCK_SIZE__SHIFT`, `CP_HQD_PQ_CONTROL__UNORD_DISPATCH_MASK`, `CP_HQD_PQ_DOORBELL_CONTROL__DOORBELL_OFFSET__SHIFT`, `CP_HQD_PQ_CONTROL__NO_UPDATE_RPTR_MASK`, `CP_HQD_PQ_CONTROL__SLOT_BASED_WPTR__SHIFT`, `CP_HQD_PQ_CONTROL__QUEUE_FULL_EN__SHIFT`, `CP_HQD_PQ_CONTROL__PRIV_STATE__SHIFT`, and `CP_HQD_PQ_CONTROL__KMD_QUEUE__SHIFT`.

## Control Flow

This header has no direct runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU/KFD consumers is:

1. Select the GC 12.1.0 register headers for the active ASIC.
2. Use a register offset macro from `gc_12_1_0_offset.h` and a shift/mask macro from this file.
3. Pack a register word with `FIELD_VALUE << REGISTER__FIELD__SHIFT`, apply `REGISTER__FIELD_MASK`, or extract a status value after an MMIO read.
4. Write, read, or emit the register through SOC15/MMIO helpers, KFD MQD memory layout, command processor packets, firmware interfaces, or reset/debug paths.
5. Higher-level code interprets acknowledgement, error, idle, queue-active, doorbell, pointer, interrupt, or fault fields according to the hardware programming sequence.

Typical sequences using this chunk include KFD MQD construction, HQD queue activation/deactivation, doorbell programming, AQL queue setup, CP/HQD dequeue and suspend/resume, CP DMA command construction, EOP/fence programming, coherency flush range setup, indirect draw/dispatch programming, graphics context emission, CP/ME/MEC/MES reset or halt/step control, and status/error polling. The header does not encode ordering, polling, privilege, read-only/write-one-to-clear, or reset sequencing rules; those live in the driver and hardware documentation.

## State And Persistence Behavior

The macros themselves store no state and persist nothing. They describe fields in hardware-visible state:

- HQD/MQD/PQ/IB/IQ/EOP fields describe live queue configuration and queue progress. Some values are initialized by software or by MQD memory, while others are advanced or latched by CP hardware.
- Doorbell, read/write pointer, dequeue, suspend, dispatch-id, AQL, and KD fields are queue-liveness state. They must be rebuilt or reconciled across queue teardown, process eviction, GPU reset, suspend/resume, and VM reset.
- `CP_HQD_PERSISTENT_STATE`, context-save, suspend, and restore-related fields describe state that bridges queue switches and preemption. Incorrect bits can break wave relaunch, saved control-stack state, or TMZ/QoS behavior.
- UTCL1, DMA watch, fed-error, HPD, GCR, MES exception, and CP error fields are diagnostic or fault state. They may be latched by hardware and may require specific clear or acknowledgement flows not represented in this header.
- Graphics context fields such as VGT/GE/draw/tessellation/index/primitive/streamout state persist until overwritten by command streams, context restore, reset, or power-management reinitialization.
- PF/VF and PF-only fields describe virtualization-visible and privileged state. The macro names do not by themselves enforce access policy.
- MES control, scratch, machine status, EPC, cause, bad-address, interrupt, and pipe-priority fields represent firmware execution state and are sensitive to firmware load, reset, halt/step, and interrupt sequencing.

Because the file is generated metadata, it cannot tell whether a field is read-only, write-only, volatile, clear-on-read, write-one-to-clear, shadowed in an MQD, or safe for read-modify-write. Consumers must follow the relevant GC 12.1.0 programming sequence.

## Dependencies And Integration Points

This chunk depends on AMD's authoritative GC 12.1.0 register database and must stay synchronized with companion generated headers in the same directory:

- `gc_12_1_0_offset.h` supplies the register offsets that pair with these field definitions.
- Other GC 12.1.0 headers supply enumerations or packet definitions used by the same driver code.
- AMDGPU SOC15 helpers and register access macros perform MMIO reads/writes using the offset header and field macros.
- KFD MQD and device-queue managers use the HQD/MQD/AQL/PQ/doorbell fields to build queue descriptors for user-mode compute queues.
- GFX ring, CP DMA, IB, fence, append/atomic, and draw/dispatch paths use the GFXU and CP command fields in this chunk.
- MES and CP firmware control code uses MES reset/active/halt/step, interrupt, scratch, and machine-status fields for firmware bring-up and diagnostics.
- GFXHUB/UTCL1/fault handling paths use the UTCL1 status/error fields and CP fed-error address fields for translation and fault analysis.
- SR-IOV and virtualization paths depend on PF/VF and PF-only naming boundaries for unmapped queues, doorbells, GRBM selection, HPD status, DFY, and GCR controls.

Integration is intentionally low-level. A macro typo, mask drift, or generation mismatch may still compile because these are untyped integer constants, but it can silently alter hardware programming.

## Risks And Edge Cases

- The range starts and ends mid-family. `CP_GFX_HQD_QUE_MGR_CONTROL` is inherited from the previous chunk, and `CP_MES_IC_OP_CNTL` fields are in the next chunk.
- Generated-header drift is the primary risk. Wrong shifts or masks compile cleanly and can program or decode the wrong hardware bits.
- Queue-control fields are high impact. Incorrect `CP_HQD_PQ_CONTROL`, doorbell, active, VMID, EOP, dequeue, AQL, or persistent-state masks can cause stuck queues, missed interrupts, broken preemption, bad MQD restore, or reset recovery failures.
- Address fields often have alignment-defined low bits and limited high-bit masks. Using the wrong mask can truncate addresses or allow invalid low bits in PQ/IB/EOP/context-save/append/DMA/metadata/indirect buffers.
- Some fields are security-sensitive: VMID, privilege, TMZ, scope/cache policy, PF/VF, GCR target disable, unmapped queue, and doorbell fields can affect isolation and memory visibility.
- Repeated families are copy-sensitive: `CP_DMA_WATCH0-3`, `CP_UNMAPPED_QUEUE0-63`, scratch registers, counter low/high pairs, CP DMA ME/PFP pairs, CP append aliases, and MES pipe priority/state fields must keep exact naming and bit layout.
- Aliases and spelling are part of the ABI-like generated namespace. For example, `CP_APPEND_DATA` and `CP_APPEND_DATA_LO` both exist, and `CP_SAMPLE_STATUS__Z_PASS_ACITVE` preserves the generated spelling.
- Status/error fields can be latched or access-sensitive. The header does not distinguish safe polling bits from bits that clear, trigger side effects, or require privileged access.
- Cross-generation similarity is risky. Older GC/GCA headers have similarly named masks but not always identical layouts, especially around HQD queue control, CP DMA command bits, and CP/ME/MES control.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime tests:

- Build AMDGPU with GC 12.1.0, KFD, MES, GFXHUB, SDMA, and SOC support enabled. Missing or renamed macros should fail in `gfx_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `sdma_v7_1.c`, and KFD queue-manager files.
- Mechanically compare this chunk against AMD's GC 12.1.0 register database and companion `gc_12_1_0_offset.h`. Validate both field masks and shift positions.
- Cross-check repeated families for consistency: DMA watch slots, HQD pointer/address pairs, EOP low/high pairs, counter low/high pairs, CP DMA ME/PFP command/address pairs, unmapped queues 0-63, scratch registers, and MES pipe fields.
- Run KFD compute queue creation, AQL dispatch, doorbell, preemption, eviction, restore, and teardown tests. Watch for stuck HQDs, dequeue timeouts, incorrect MQD fields, EOP pointer mismatches, and reset failures.
- Run graphics ring and CP DMA tests covering IB submission, indirect draw/dispatch, append/atomic operations, coherency flushes, fences, and pipeline statistics. Signals include forward ring progress, correct fence completion, no CP fatal errors, and plausible stats.
- Exercise GPU reset, suspend/resume, MES firmware load/reset, and CP/ME/MEC halt or step diagnostics. Relevant signals include expected active/reset bits, no stale firmware exception state, and successful post-reset queue reinitialization.
- Exercise VM fault, UTCL1 status, DMA watchpoint, fed-error, and HPD error paths where hardware is available. Validate captured VMID, queue ID, client, pipe, watch ID, address, and fault/retry/PRT IDs.
- Exercise SR-IOV/PF-VF scenarios for unmapped queue accounting, doorbell clearing, PF-only HPD/GCR/DFY access, and GRBM selection boundaries.
- Run graphics frontend workloads that stress tessellation, geometry, streamout, VRS, indexed/indirect draws, primitive restart, and multi-instance draws. Bad VGT/GE masks usually appear as draw corruption, hangs, or implausible counters.

## Cross-Chunk Notes

The previous chunk should document the beginning of `CP_GFX_HQD_QUE_MGR_CONTROL`; this chunk only contains its final `DISABLE_MAPPED_QUEUE_IDLE_MSG` mask. The next chunk should begin with the `CP_MES_IC_OP_CNTL` fields and continue the MES register block. The final per-file document should merge this report with adjacent chunks before making complete claims about the GC 12.1.0 shift/mask namespace.

### subset-b-002598: lines 15119-17740

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 15119-17740

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are represented by `__SHIFT` values and matching `__MASK` values for 32-bit register packing and decoding. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin inside the `CP_MES_IC_OP_CNTL` definition, covering MES instruction-cache operation bits after the preceding chunk's register comment. The body then covers MES and MEC RS64 command-processor state, a large banked GFX RS64 data-cache aperture region, CP/GFX/PFP/ME exception and interrupt status, CH and GLARB client arbitration/fabric controls, performance counter result and select registers, CP draw-window/perfmon controls, and RLC streaming performance monitor setup. The chunk ends mid-register at `RLC_SPM_ACCUM_STATUS`: it includes the status field shifts but not the corresponding masks, which are in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 registers. Driver code pairs these macros with register addresses from the matching offset header, and often with generated default/reset values, so AMDGPU code can compose register values without hard-coded bit positions. Consumers usually use helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` around these generated constants.

This chunk is centered on command processor RS64 state, client/fabric controls, and performance monitoring:

- `CP_MES_*` fields for MES instruction/data cache operations, CSR-style cycle/time/instret/ISA/vendor/hart/timer state, VMID/cache/scope policy, process quantum, doorbells, general-purpose registers, local/instruction/scratch apertures, performance selection, pending interrupt, exception status, interrupt payload registers 16 through 31, and metadata control.
- `CP_MEC_*` and `CP_MEC_RS64_*` fields for MEC RS64 program counter/vector setup, reset/active/halt/step controls, interrupt masks/status, instruction pointer, data-cache policy and invalidate completion, timer compare, GP registers, local/instruction/scratch apertures, performance selection, pending interrupt, exception status, and interrupt payload registers 16 through 31.
- `CP_CPC_IC_OP_CNTL` fields for command processor instruction-cache invalidation, priming, completion, invalidate-all, reset-error, and error reporting.
- `CP_GFX_RS64_*`, `CP_PFP_RS64_*`, and `CP_ME_RS64_*` fields for graphics command processor interrupts, cache controls, local/instruction/scratch apertures, exception status, perf controls, timer/MIP state, GP registers, instruction pointers, pending interrupts, and two banks of 16 GFX RS64 data-cache apertures.
- `CH*`, `CHA*`, and `CHI*` fields for CPWD channel arbitration, DRAM burst controls, client credits, free-delay tuning, repeater fine-grain clock-gating overrides, CHC buffering/credit controls, stall/busy status, and DCC error reporting.
- `GLARB*`, `GLARBA*`, `GLARBI*`, and `GLARBC*` fields for GLARB arbitration, memory burst behavior, NPS/target-disable mode, GLARBC credits, clock-gating overrides, buffer controls, CREST mode, status/error reporting, and DCC compression control.
- `CPG`, `CPC`, `CPF`, `GRBM`, `GE1`, `GE2_DIST`, `GC_EA_CPWD`, `CHC`, `GLARBA`, `GLARBC`, `RLC`, `GCR`, and `CHA` performance counter result registers and performance-counter select registers.
- `CP_PERFMON_CNTL`, latency-stat selectors, TC performance-counter window selectors, CP draw object/window fields, and RLC SPM ring, segment, mux select, user data, accumulator RAM, and accumulator status fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register-address symbols live in the companion GC 12.1.0 offset header with matching register names.
- AMDGPU code normally uses these through generated field helpers, MMIO read-modify-write helpers, command-packet register programming, debug/perf paths, and reset/recovery logic.

Notable macro families in this exact slice:

- `CP_MES_IC_OP_CNTL`, `CP_MES_DC_BASE_CNTL`, and `CP_MES_DC_OP_CNTL`: MES instruction/data cache controls. They expose invalidate, prime, primed, VMID, cache policy, scope, invalidate-complete, and bypass-all fields.
- `CP_MES_MCYCLE_*`, `CP_MES_MTIME_*`, `CP_MES_MINSTRET_*`, `CP_MES_MISA_*`, `CP_MES_MVENDORID_*`, `CP_MES_MARCHID_*`, `CP_MES_MIMPID_*`, `CP_MES_MHARTID_*`, and `CP_MES_MTIMECMP_*`: 64-bit CSR-style MES observability and timer registers represented as low/high 32-bit halves.
- `CP_MES_PROCESS_QUANTUM_PIPE0/1`: MES scheduling quantum fields, including duration, expired flag, scale, and enable.
- `CP_MES_DOORBELL_CONTROL1..6`: doorbell offset, enable, and hit fields for MES doorbell routing.
- `CP_MES_GP0..9_{LO,HI}` and `CP_MEC_GP0..9_{LO,HI}`: GP register views, with special fields such as `PG_VIRT_HALTED`, return-address high halves, read/write selector halves, and stack-pointer halves.
- `CP_MES_LOCAL_*` and `CP_MEC_LOCAL_*`: local, instruction, and scratch aperture base/mask/control fields. Low halves generally start at bit 16, high halves are 25-bit values, and aperture controls expose aperture, scope, and temporal fields where applicable.
- `CP_MES_RS64_EXCEPTION_STATUS`, `CP_MEC_RS64_EXCEPTION_STATUS`, `CP_PFP_RS64_EXCEPTION_STATUS`, and `CP_ME_RS64_EXCEPTION_STATUS`: RS64 exception decoding for illegal instruction, misaligned address, unaligned instruction, page fault, and instruction address.
- `CP_MEC_RS64_CNTL`: MEC pipe reset/active state, instruction-cache invalidate, halt, and step controls for four MEC pipes.
- `CP_CPC_IC_OP_CNTL`: CPC instruction-cache operation fields, including invalidate-all, prime-complete, reset-error, and error-status bits.
- `CP_GFX_RS64_DC_APERTURE0..15_{BASE,MASK,CNTL}0` and `CP_GFX_RS64_DC_APERTURE0..15_{BASE,MASK,CNTL}1`: two GFX RS64 data-cache aperture banks. Each aperture has base, mask, and control words; control fields include enable, no-cache, read/write permissions, non-volatile, and cache-policy bits.
- `CH_ARB_CTRL`, `CH_DRAM_BURST_*`, `CHA_CHC_CREDITS`, `CHA_CLIENT_FREE_DELAY`, `CHI_CHR_REP_FGCG_OVERRIDE`, `CHC_CTRL`, `CHC_STATUS`, and `CHC_STATUS2`: CPWD channel/fabric controls and diagnostics.
- `GLARB_ARB_CTRL`, `GLARB_DRAM_BURST_*`, `GLARBA_GLARBC_CREDITS`, `GLARBA_CLIENT_FREE_DELAY`, `GLARBI_GLARBR_REP_FGCG_OVERRIDE`, `GLARBC_CTRL`, `GLARBC_STATUS`, and `GLARBC_CTRL2`: GLARB/GLARBC arbitration, burst, credit, DCC, CREST, and status fields.
- `*_PERFCOUNTER*_LO/HI`: 32-bit low/high result halves for CPG, CPC, CPF, GRBM, GE1, GE2 distributed, GC EA CPWD, CHC, GLARBA, GLARBC, RLC, GCR, and CHA counters.
- `*_PERFCOUNTER*_SELECT` and `*_SELECT1`: event selection and counter mode fields. Common patterns include 10-bit `PERF_SEL` lanes, paired select registers for multiple events, `CNTR_MODE`, `PERF_MODE`, and `SPM_MODE` fields.
- `GRBM_PERFCOUNTER*_SELECT` and `_SELECT_HI`: GRBM select fields with many user-defined busy/clean masks across DB, CB, TA, SX, CP, RLC, TCP, SPI, UTCL2, and related blocks.
- `CP_PERFMON_CNTL`, `*_LATENCY_STATS_SELECT`, and `*_TC_PERF_COUNTER_WINDOW_SELECT`: global CP perfmon state, SPM perfmon state, sample enable, latency-stat index/clear/enable, and TC window index/always/enable fields.
- `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_*`, and `CP_DRAW_WINDOW_CNTL`: draw object counters and draw-window bounds/control fields.
- `RLC_SPM_*`: RLC streaming performance monitor control, ring base/size/pointers, segment thresholds, global/SE mux select address/data, SE user data words, accumulator data/SWA/control RAM addressing/data, control RAM offsets, and the start of accumulator status.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow is in AMDGPU consumers:

1. Select the GC 12.1.0 register headers for the active ASIC generation.
2. Choose the matching register address from `gc_12_1_0_offset.h`.
3. Read an existing register value, prepare an indexed/debug/perf access, or construct a command-packet/MMIO register write.
4. Use the `__SHIFT` and `__MASK` pairs to pack a field value or extract a status bitfield.
5. Apply the resulting value in command processor bring-up, queue scheduling, cache maintenance, interrupt/exception handling, aperture setup, client/fabric tuning, draw-window gating, perf counter programming, SPM setup, hang analysis, or reset/recovery.

For MES and MEC RS64 state, initialization and recovery paths program vectors, program counters, local/instruction/scratch aperture windows, VMID/cache policy, timer compare registers, doorbells, process quantum, interrupt enables, and pipe reset/halt/step controls before or during queue execution. Interrupt and hang-dump paths decode pending interrupts, exception status, instruction pointers, GP registers, CSR-style counters, and interrupt data words.

For GFX RS64 aperture state, consumers program base/mask/control triples for two banks of 16 data-cache apertures. Cache maintenance paths use instruction/data cache operation fields and may poll completion/status bits. The header does not encode the ordering, polling, privilege, or clear semantics required by hardware.

For CH/GLARB and performance monitoring, runtime setup code configures arbitration, burst, credit, DCC/compression, CREST, and clock-gating override fields, then diagnostics read status and counter fields. Perf code programs select registers, enables global perfmon/SPM state, optionally configures TC windows and latency-stat selectors, and reads low/high counter result halves. RLC SPM setup programs ring memory, mux selections, segment layout, accumulator RAMs, and status/overflow handling through fields defined here and in the following chunk.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU register fields whose state is owned by hardware, firmware, and AMDGPU runtime programming.

MES/MEC/GFX RS64 program-counter, vector, local/instruction/scratch aperture, VMID/cache policy, timer, doorbell, quantum, cache-operation, and aperture-control registers are persistent engine state until reprogrammed, reset, or power-cycled. Incorrect field packing can start firmware execution at the wrong address, leave a pipe halted or reset, send doorbells to the wrong queue, misconfigure process scheduling, deny firmware access to local memory, or apply the wrong cacheability policy.

Exception, pending-interrupt, interrupt-data, GP, MIP/timer, cycle/time/instret, and instruction-pointer registers are live diagnostic state. Some status bits may be sticky, latched, read-only, clear-on-write, or write-one-to-clear, but those semantics are not represented by the generated masks.

Data-cache aperture descriptors are stateful memory windows. Base/mask/control triples determine which address regions RS64 engines can read/write and how those accesses are cached. Misaligned bases, incorrect masks, stale permissions, or bad non-volatile/cache-policy bits can cause command processor faults, coherency bugs, unintended memory exposure, or silent performance regressions.

CH/GLARB controls persist as client/fabric policy. They affect arbitration, burst behavior, credits, repeater clock gating, DCC compression behavior, error detection/clearing, CREST mode, buffer depth, and request/data flow control. Full-register writes are risky because adjacent bits may be reserved, status-like, or side-effecting.

Performance counter and latency-stat result fields are hardware-updated state. Low/high counter pairs may require a documented latch/snapshot sequence to avoid torn 64-bit reads. `CP_PERFMON_CNTL` and SPM fields persist global measurement state, while RLC SPM ring base/size/pointers and mux/accumulator RAM fields describe memory-backed sample collection state that can outlive a single read.

The chunk boundary matters for `RLC_SPM_ACCUM_STATUS`: lines 17735-17740 define status field shifts for `NumbSamplesCompleted`, `AccumDone`, `SpmDone`, `AccumOverflow`, and `AccumArmed`, but the matching masks are outside this assigned range.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` provides matching register addresses.
- The matching generated default/reset header, when present for this register family, provides expected reset values for many fields.
- Common AMDGPU register helpers provide field packing/extraction and MMIO, indexed-register, or command-packet access mechanisms.
- AMDGPU GFX, CP, MES, MEC, KFD/compute scheduling, queue doorbell setup, firmware bring-up, reset/recovery, suspend/resume, SR-IOV/virtualization, debugfs, perf counter, SPM, and hang-dump paths rely on these bit assignments.

Integration points include MES/MEC firmware startup, RS64 exception reporting, CP instruction/data cache invalidation, process quantum and doorbell routing, local/instruction/scratch memory windows, GFX RS64 data-cache aperture programming, CH/GLARB fabric tuning, DCC/compression diagnostics, GRBM/CPG/CPC/CPF/GE/CH/GLARB counter programming, CP draw-window filtering, latency-stat collection, TC window selection, and RLC SPM ring/mux/accumulator configuration.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading status.
- This chunk starts inside `CP_MES_IC_OP_CNTL` and ends inside `RLC_SPM_ACCUM_STATUS`; adjacent chunks are required for complete register comments and the final status masks.
- MES, MEC, and GFX RS64 groups are similar but not interchangeable. Assuming symmetry can miss pipe counts, bank suffixes, cache-policy fields, scope fields, or engine-specific interrupt/exception meanings.
- Low/high address and counter halves are easy to misuse. Firmware vectors, GP registers carrying addresses, aperture bases/masks, ring bases, and 64-bit perf counters may have alignment, address-unit, or snapshot rules outside this header.
- Reset, halt, step, cache invalidate, bypass-all, DCC error-clear, perfmon state, sample-enable, latency clear, and SPM arm/status fields can have side effects. Debug tooling should avoid casual writes and preserve reserved bits.
- Doorbell and process-quantum fields affect scheduling. Incorrect offsets, enable bits, hit-bit handling, quantum duration, or scale can stall queues, target the wrong pipe, or distort preemption/fairness.
- Data-cache aperture permission/cacheability bits can affect isolation and correctness. Bad base/mask/control values can expose unintended memory, make required memory uncached, or fault RS64 firmware.
- CH/GLARB credit, burst, DCC, CREST, and clock-gating controls are dense mode registers. Incorrect packing can cause hangs, stalls, DCC errors, bandwidth regressions, or misleading performance data.
- Performance counter select registers encode multiple event lanes per register. Mixing `PERF_SEL`, `PERF_SEL1/2/3`, `CNTR_MODE`, `PERF_MODE`, and `SPM_MODE` fields can produce valid-looking but semantically wrong measurements.
- RLC SPM ring and accumulator fields involve memory-backed sampling. Wrong ring base/size/pointers, segment counts, mux selections, accumulator RAM addresses, or status interpretation can corrupt samples or hide overflow.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and hardware/runtime diagnostics:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_sh_mask.h`, especially GC 12.1.0 GFX, CP, MES, MEC, KFD/compute, reset, virtualization, debug, perf, and SPM paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that registers in this chunk have matching address macros in `gc_12_1_0_offset.h` and expected defaults in the matching default header where generated.
- Static sanity checks that masks align with shifts, full-width fields use `0xFFFFFFFFL`, low/high address halves retain expected widths, aperture families remain structurally consistent, and repeated perfcounter select layouts do not overlap unexpectedly.
- MES/MEC/GFX bring-up tests that validate RS64 vectors, program counters, local/instruction/scratch apertures, VMID/cache policy, pipe reset/halt/active transitions, process quantum, and doorbell behavior.
- Interrupt and exception tests that exercise pending-interrupt, interrupt-data, instruction-pointer, GP register, MIP/timer, and exception-status decode during injected faults, time interrupts, breakpoints, and recovery.
- Cache-operation tests that invalidate/prime CP instruction caches, invalidate data caches, exercise bypass-all behavior, and verify completion/status bits and post-operation coherency.
- Aperture tests that program GFX RS64 data-cache aperture banks with known base/mask/control values and verify intended read/write/cacheability behavior without unintended access.
- CH/GLARB stress tests that vary credits, burst controls, DCC compression/error handling, clock-gating overrides, CREST mode, and buffer depths under graphics/compute traffic while checking for stalls, hangs, DCC errors, or performance regressions.
- Perf counter tests that program CPG/CPC/CPF/GRBM/GE/CH/GLARB/RLC/GCR/CHA selects under controlled workloads, verify expected activity, and read low/high result halves using the required snapshot sequence.
- RLC SPM tests that configure ring base/size, write/read pointers, segment thresholds, mux selections, SE user data, accumulator RAMs, and status handling, then verify sample collection, done bits, armed state, and overflow reporting.
- Runtime warning signals include RS64 firmware startup failures, stuck MES/MEC/GFX pipes, invalid doorbell hits, repeated CP exceptions, stale cache contents after invalidation, CH/GLARB credit starvation, DCC error codes, perf counters stuck at zero, SPM ring pointer corruption, accumulator overflow, and GPU reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002598`. It covers lines 15119-17740 of `gc_12_1_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to recover the beginning of `CP_MES_IC_OP_CNTL` and the masks after `RLC_SPM_ACCUM_STATUS`.

### subset-b-002599: lines 17741-20296

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 17741-20296

## Purpose

This chunk is part of AMDGPU's generated GC 12.1.0 register field header. It contains C preprocessor constants for register bit shifts and masks, not executable code. Consumers pair these `*_SHIFT` and `*_MASK` definitions with register offsets from `gc_12_1_0_offset.h` and helper macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()` in `amdgpu.h` to program or decode memory-mapped GPU registers.

The span starts in the middle of `RLC_SPM_ACCUM_STATUS`, covers RLC streaming-performance-monitor, performance-counter, virtualization, clock/power, microcontroller memory, command-processor hypervisor, global-arbiter, shader-array disable, RLC firmware/control, RLC doorbell, UTCL1, SPP, residency-counter, and graphics interrupt-handler client register fields, and ends in the middle of `RLC_GFX_IH_CLIENT_SE_STAT_H`. Adjacent chunks are required to see the complete first and last registers.

## Important APIs, Types, And Macro Families

This header defines no functions, structs, classes, or runtime types. Its public interface is a generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit offset for `FIELD` within `REGISTER`.
- `REGISTER__FIELD_MASK`: bit mask for the same field.

The main consuming APIs are external:

- `REG_SET_FIELD(orig_val, reg, field, field_val)` token-pastes the generated shift and mask names to insert a field value.
- `REG_GET_FIELD(value, reg, field)` extracts a field from a register value.
- `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC_SHADOW_EX`, `WREG32_FIELD15_PREREG`, and related SOC15 helpers perform the actual MMIO accesses using `reg...` offset macros from the paired offset header.

Major register groups in this chunk:

- `RLC_SPM_ACCUM_*`, `RLC_SPM_*`, `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER*_SELECT`, `GCR_PERFCOUNTER*_SELECT*`, and `CHA_PERFCOUNTER*_SELECT*`: RLC SPM accumulation state, start/rearm/reset strobes, automatic accumulation/SPM modes, sample thresholds/counts, RSPM request/response op/data fields, pause/status bits, gfx clock counters, GTS trigger values, global user data, and performance-counter event selection.
- `XVMIN_XVMIN_WR_DATA`: generated field for a CPWD/GDFLL XVMIN write-data register.
- `RLC_GPU_IOV_*`, `RLC_FED_DRVR_STATUS`, `RLC_SDMA*_STATUS`, `RLC_SDMA*_BUSY_STATUS`, `RLC_HYP_SEMAPHORE_*`, and `RLC_IH_COOKIE*`: SR-IOV/hypervisor controls for VF enablement, command execution/status, function identifiers, VF/PF doorbell status set/clear/mask, SDMA save/restore/busy status, hypervisor semaphores, interrupt-cookie credit/reset, SMU/RLC responses, and virtual reset requests.
- `RLC_BUSY_CLK_CNTL`, `RLC_CLK_CNTL`, `GLARB_*`, `CH_*`, `GC_USER_*`: RLC clock-gating override/latency controls, global-arbiter/channel hashing and pipe steering, CAC selection, AID selection, and user-visible shader-array/HBM-disable masks.
- `CP_HYP_*`, `CP_PFP_*`, `CP_ME_*`, `CP_MEC*`, and `CP_MES_*` fields in the `cphypdec` block: command-processor context range, PFP/ME/MEC hypervisor and normal firmware-address/data registers, checksum/version fields, instruction-cache base/control/op controls, MES instruction/data bounds, and RS64 graphics/MEC base/bound registers.
- `GRBM_*` fields in the hypervisor GRBM block: shadow-register select/data and SE/SA remap controls, plus interrupt-cookie pointer fields.
- `RLC_CNTL`, `RLC_STAT`, `RLC_ACTIVE_MASK`, `RLC_GFX_SE_STATUS`, `RLC_GPM_TIMER_*`, `RLC_GPM_LEGACY_INT_*`, `RLC_INT_STAT`, `RLC_MGCG_CTRL`, and `RLC_MCA_*`: core RLC enable/step/cache/poison controls, busy flags, active shader-engine mask, thread timer programming/status/clear bits, interrupt status/clear fields, medium-grain clock-gating controls, and machine-check/RAS interrupt fields.
- `RLC_*CLOCK*`, `RLC_CAPTURE_GPU_CLOCK_COUNT*`, `RLC_CLK_COUNT_*`, and `RLC_GPU_CLOCK_32*`: GPU/reference clock counting, capture, status, and 32-bit clock selection registers.
- `RLC_UCODE_CNTL`, `RLC_GPM_*`, `RLC_LX6_*`, `RLC_SRM_*`, and `RLC_*UTCL1*`: RLC firmware loading/control, GPM thread reset/enable/priority/interrupt/CP-DMA-completion fields, LX6/GPM/SRM memory address/data windows, SRM command/indexed control/status fields, and UTCL1 control/status/error fields for LX6, GPM, SPM, SRM, DMA, and DLG paths.
- `RLC_RLCG_DOORBELL_*` and `RLC_RLCV_DOORBELL_*`: RLCG/RLCV doorbell range, enable, offset, FIFO/full/error/status, and four 64-bit data slots.
- `RLC_PG_*`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL*`, `RLC_DYN_PG_*`, `RLC_STATIC_PG_STATUS`, `RLC_AUTO_PG_CTRL`, `RLC_SERDES_*`: power-gating delays, dynamic/static power-gating status/request, always-on WGP masks, clock-gating/light-sleep controls, and SERDES indexed access control/status/data.
- `RLC_SPP_*`: shader profiler/performance-profile control, shader profile enablement by SIMD/WGP/SE, SSF capture/thresholds, inflight readback, global shader identifiers, status, private statistics, maximum levels, stall-state update, PBB information, and reset fields.
- `RLC_*RESIDENCY_*`: power, clock, deep-sleep, ultra-low-voltage, PCC, and general residency counter controls, event counters, and reference counters.
- `RLC_GFX_IH_*`: graphics interrupt-handler client masks, error-clear bits, halt control, arbiter granted-client status, and per-SE client buffer level/loading/protocol-error/overflow flags for SE0 through the partial SE5 fields included in this chunk.

## Control Flow

There is no local control flow because the file is only a macro database. The effective control flow is in AMDGPU users:

1. Include `gc_12_1_0_offset.h` and `gc_12_1_0_sh_mask.h`.
2. Read an MMIO register with a SOC15 helper or start from a literal/reset value.
3. Compose fields with `REG_SET_FIELD()` or direct `*_MASK` / `*_SHIFT` operations.
4. Write the register through `WREG32_SOC15()` or an RLC-shadowed/no-KIQ variant.
5. Poll status bits with `REG_GET_FIELD()` or mask tests when hardware exposes completion, busy, error, or acknowledgement flags.

Examples in this tree include `gfx_v12_1.c` enabling RLC GPM threads through `RLC_GPM_THREAD_ENABLE`, writing `RLC_CNTL__RLC_ENABLE_F32_MASK` to start RLC F32, clearing `RLC_CNTL.RLC_ENABLE_F32` to stop it, and reading `RLC_CNTL.RLC_ENABLE_F32` to report whether RLC is enabled. The same file updates SPM VMID through `RLC_SPM_MC_CNTL` and uses the same generated-header contract as this chunk's SPM and RLC fields.

## State And Persistence Behavior

The macros themselves are compile-time constants. The state they describe is hardware state held in GC 12.1.0 RLC, CP, GRBM, SPM, SPP, interrupt, and virtualization register files.

- Control bits such as RLC enable, RLC stepping, read-cache disable, clock-gating overrides, power-gating controls, SPP enablement, doorbell enablement, and IOV command execution persist until reset, power-management transitions, firmware reinitialization, or explicit driver writes.
- Status, busy, acknowledgement, interrupt, overflow, FIFO, residency, and performance-counter fields are updated by hardware and are commonly consumed by polling, diagnostics, interrupt handling, or performance tooling.
- Address/data windows for GPM, LX6, SRM, PFP, ME, MEC, MES, and RLCG firmware/scratch/memory regions are persistent register interfaces into firmware or microcontroller memory. Their values are meaningful only when used with the matching indexed register access protocol.
- Doorbell status/data fields and VF/PF function-selection fields are security- and isolation-sensitive because they affect SR-IOV scheduling, virtual resets, function ownership, and queue notification paths.
- SPM, SPP, residency, and clock counters are measurement state. They must be reset/armed/enabled in the correct order by driver or firmware code to avoid stale samples, overflows, or partial captures.

## Dependencies

This chunk depends on the paired generated offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h`; mask macros alone do not name MMIO addresses. It also depends on AMDGPU field helpers in `amdgpu.h` and SOC15 register access helpers for instance-aware GC register addressing.

Direct include sites for this GC 12.1.0 mask header include `gfx_v12_1.c`, `mes_v12_1.c`, `sdma_v7_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `imu_v12_1.c`, and `soc_v1_0.c`. Not every include site uses every register in this chunk, but all rely on the generated naming ABI remaining consistent across offset, mask, default, packet, firmware-loading, scheduler, and diagnostics code.

## Integration Points

- GFX/RLC bring-up: `gfx_v12_1.c` programs `RLC_CNTL` and `RLC_GPM_THREAD_ENABLE` during RLC autoload/start/stop and checks RLC enable state during runtime decisions.
- Performance and profiling: SPM accumulation, RSPM request/response, performance-counter selection, SPP capture/status, clock-count, and residency-counter fields integrate with GPU profiling, debugfs/perf paths, and firmware-mediated collection.
- SR-IOV and hypervisor operation: `RLC_GPU_IOV_*`, VF doorbell status/mask/set/clear, active function ID, virtual reset request, SDMA save/restore/busy status, CP hypervisor context range, and hypervisor firmware register windows support PF/VF isolation and virtualization scheduling.
- Firmware loading and microcontroller control: CP PFP/ME/MEC/MES, RLC GPM, LX6, and SRM address/data/checksum/version fields are used by firmware load, validation, reset, and indexed memory operations.
- Power and clock management: RLC clock-gating overrides, busy-clock latency, CGCG/CGLS, dynamic/static power gating, SERDES access, and residency counters integrate with runtime power-management and GPU reset/resume flows.
- Interrupt/error handling: RLC GPM legacy interrupt status/clear, CP-RLC interrupt status, RLC MCA/RAS controls, poison interrupt controls, IH cookie handling, and GFX IH client masks/statistics provide hooks for error reporting, interrupt routing, and buffer overflow/protocol-error diagnosis.
- Topology and resource discovery: GRBM SE/SA remapping, `GC_USER_*_DISABLE`, HBM disable, pipe steering, hash configuration, and active-mask fields affect how driver code interprets active shader arrays, memory channels, and graphics instances.

## Risks

- Incorrect shift or mask values silently corrupt hardware programming. `REG_SET_FIELD()` and `REG_GET_FIELD()` will compile as long as names exist, even if the bit layout does not match GC 12.1.0 hardware.
- This chunk has split-register boundaries: it starts after the first `RLC_SPM_ACCUM_STATUS` fields and ends before all `RLC_GFX_IH_CLIENT_SE_STAT_H` masks. The merge lane must combine adjacent chunks before treating either register as fully researched.
- Cross-generation similarity is risky. RLC/SPM/IOV/CP fields appear in many GC generations, but GC 12.1.0 changes field widths and reserved regions, such as active function ID and virtualization fields. Copying masks from GC 9/10/11 can program the wrong bits.
- Repeated families are prone to generator or review mistakes: SDMA0-7 status/busy registers, doorbell data slots, GPM timers, SRM indexed data lanes, UTCL1 error pairs, residency counter groups, and SE0-7 IH client status fields should remain internally consistent unless hardware documentation says otherwise.
- Security and isolation fields, including VF enable/mask, PF/VF status, virtual reset request, CP hypervisor ranges, doorbell controls, privilege/poison interrupt controls, and function identifiers, can cause cross-function leakage, lost interrupts, failed FLR, or PF/VF hangs if wrong.
- Counter/control sequencing matters. SPM/SPP/residency reset, arm, start, sample, overflow, and acknowledgement bits can produce misleading profiling data or stuck polling loops when written in the wrong order.
- RLC power/clock-gating and firmware-control registers are boot-critical. Bad masks can leave RLC halted, prevent firmware startup, break GPU reset/resume, or cause command submission timeouts.

## Test Signals

Useful validation is mostly build and hardware integration:

- GC 12.1.0 AMDGPU build coverage with all token-pasted `REG_SET_FIELD()` / `REG_GET_FIELD()` names resolving for `gfx_v12_1.c`, `mes_v12_1.c`, `sdma_v7_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `imu_v12_1.c`, and `soc_v1_0.c`.
- Boot on GC 12.1.0 hardware with successful RLC autoload, RLC F32 enable, CP/MES/MEC firmware loading, KIQ/MES queue bring-up, and no RLC/CP firmware checksum or halt errors.
- GPU reset, suspend/resume, and runtime power-management cycles without RLC stuck-busy, clock-gating, power-gating, or SERDES access timeouts.
- SR-IOV PF/VF validation covering VF enablement, active function switching, VF/PF doorbell status set/clear, virtual reset/FLR requests, SDMA status save/restore, and VM busy status reporting.
- Profiling workloads that exercise SPM accumulation, SPP capture, performance counters, clock counters, and residency counters, with sane sample counts, done/overflow/armed bits, and no unexpected aborts.
- Interrupt and RAS tests that exercise IH client masking/error clear, SE/SDMA/UTCL2/FED error paths, RLC GPM legacy interrupt clear/status, CP-RLC interrupt pending IDs, poison interrupt routing, and MCA/RAS controls.
- Register dump comparison against AMD-generated GC 12.1.0 headers or hardware specifications, especially for repeated SDMA, doorbell, timer, UTCL1, residency, and IH per-SE fields.

### subset-b-002600: lines 20297-22799

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 20297-22799

## Scope

This chunk covers generated shift and mask macros from the AMD GC 12.1.0 register mask header. The range starts in the tail of `RLC_GFX_IH_CLIENT_SE_STAT_H` mask definitions and ends inside the `GFX_IMU_SCRATCH_*` family at `GFX_IMU_SCRATCH_5`. The line boundaries are artificial, so adjacent chunks are required for the complete SE interrupt-client and IMU scratch-register families.

The covered range includes:

- RLC GFX interrupt-handler client status for SDMA, other/FED, UTCL2 22-beat status, and 22-beat arbiter grant status.
- RLC SPM indirect delay and block-enable mask address/data windows.
- RLC LX6 and XT core control/status, firmware status/version, core interrupt/fault/reset-vector, interrupt-vector force/clear/mux selection, doorbell monitor, XT doorbell range/control/status/data, and RLC memory light-sleep/deep-sleep controls.
- RLC safe-mode and command/message paths to RLCV, SMU, SRM/GPM, and IMU bootload state.
- The `CHIP_XCD_gfxip_xcc_gfx_cpwd_cpwd_rlcsdec` address block, including RLC_RLCS exception, fence, clock/deep-sleep, GPM status, bootload, interrupt, scratch/general, auxiliary, bootload-ID, GCR, UTCL2, IMU/RLC message, RAM, SDMA interrupt, memory-power, IH, FED, host-ack, and busy-handshake fields.
- The `CHIP_XCD_gfxip_xcc_gfx_cpwd_cpwd_pfvfdec_rlc` block, including PF/VF-safe RLC, SPM interrupt, CSIB, CP scheduler/EOF/spare interrupt, and VFI register-window fields.
- Power, PSP/security, CP PSP debug, and CH power/clock-gating blocks.
- The beginning of the `CHIP_XCD_gfxip_xcc_gfx_cpwd_gfx_imu_cpwd_gfx_imudec` block, covering `GFX_IMU_C2PMSG_0..47`, message flags, access-control registers, MP1/RLC mutexes, IMU/RLC command/data/status handshakes, SOC request window, VF control, and scratch registers `0..5`.

The chunk contains preprocessor constants only. It has no C functions, structs, variables, allocation, locking, or executable code.

## Purpose

This header section is the bitfield ABI between AMDGPU/KFD driver code and GC 12.1.0 graphics hardware. For each register field it defines the conventional generated names:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit field mask.

Driver code pairs these constants with matching address definitions from `gc_12_1_0_offset.h` and helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and `SOC15_REG_OFFSET`. The header itself does not describe sequencing, ownership, or reset values; those live in AMDGPU generation-specific code, firmware protocols, default headers, and hardware documentation.

## Important Macro Families

### RLC GFX IH, SPM, and Core-Debug Fields

The opening register families expose RLC-side interrupt-handler and streaming-performance-monitor status:

- `RLC_GFX_IH_CLIENT_SDMA_STAT` packs SDMA0 through SDMA3 buffer level, loading, protocol-error, overflow, and reserved bits into four 8-bit lanes.
- `RLC_GFX_IH_CLIENT_OTHER_STAT` reports UTCL2/PMM reserved state and FED buffer/error state.
- `RLC_GFX_IH_22BEAT_STAT` and `RLC_GFX_IH_ARBITER_STAT_22BEAT` expose UTCL2 22-beat buffer/error state plus current and last IH arbiter grants.
- `RLC_SPM_GLOBAL_DELAY_IND_*`, `RLC_SPM_SE_DELAY_IND_*`, `RLC_SPM_GLOBAL_BLK_EN_MASK_IND_*`, and `RLC_SPM_SE_BLK_EN_MASK_IND_*` are indirect address/data windows for SPM sampling delay and block-enable masks.

The `RLC_LX6_*` and `RLC_XT_*` groups expose firmware/core debug state. They include LX6 reset/runstall/debug enable, two-core busy and interrupt-pending status, full-width firmware status/version, XT wait/fatal/double-exception status, external interrupt and NMI bits, fault info, alternate reset vector, interrupt-vector force/clear bits for vector numbers 0 through 31, and mux selection fields. These are firmware-sensitive debug and control surfaces rather than ordinary queue programming fields.

`RLC_CPAXI_DOORBELL_MON_*` and `RLC_XT_DOORBELL_*` define a monitor and four data-bearing doorbell slots. `RLC_MEM_SLP_CNTL` controls RLC memory light-sleep/deep-sleep enablement, per-subblock overrides, busy override, and on/off delays.

### RLC Firmware, SMU, SRM, and IMU Bootload Handshakes

The chunk defines multiple command/message register layouts:

- `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, and `RLC_SAFE_MODE` share a `CMD`, 4-bit `MESSAGE`, and 4-bit `RESPONSE` layout.
- `RLC_RLCV_COMMAND`, `RLC_SMU_MESSAGE[_1/_2]`, `RLC_SMU_COMMAND`, and `RLC_SMU_ARGUMENT_1..5` provide command and argument payload fields.
- `RLC_SRM_GPM_COMMAND` carries operation, index-control, size, and start-offset fields, while `RLC_SRM_GPM_ABORT` exposes an abort bit.
- `RLC_IMU_BOOTLOAD_ADDR_HI/LO`, `RLC_IMU_BOOTLOAD_SIZE`, `RLC_IMU_MISC`, and `RLC_IMU_RESET_VECTOR` describe the RLC-to-IMU bootload address, size, throttle/early-MGCG options, and reset-vector exit fields.

These fields represent command protocols with hardware/firmware side effects. The masks are only the encoding layer; callers must still respect busy, response, and firmware ownership rules.

### RLC_RLCS Decode Block

The `RLC_RLCS` block is the largest portion of this chunk. It exposes the RLC slave/decode register surface used for firmware load, power management, diagnostics, interrupts, and fault handling.

Key groups include:

- `RLC_RLCS_EXCEPTION_REG_1..4` and `RLC_RLCS_AUXILIARY_REG_1..4`, with 18-bit register address fields.
- `RLC_RLCS_FENCE_CNTL`, `RLC_RLCS_CGCG_REQUEST`, and `RLC_RLCS_CGCG_STATUS`, controlling fence behavior and clock-gating request/status reporting.
- `RLC_RLCS_SOC_DS_CNTL`, `RLC_RLCS_GFX_DS_CNTL`, and `RLC_RLCS_GFX_DS_ALLOW_MASK_CNTL`, which gate deep-sleep allowance against RLC, CP, graphics power, non-3D power, IMU-disable, and SDMA0 through SDMA7 busy signals.
- `RLC_GPM_STAT`, `RLC_RLCS_GPM_STAT`, `RLC_RLCS_ABORTED_PD_SEQUENCE`, `RLC_RLCS_GPM_STAT_2`, `RLC_RLCS_GRBM_SOFT_RESET`, `RLC_RLCS_PG_CHANGE_STATUS`, and `RLC_RLCS_PG_CHANGE_READ`, which report RLC/GPM busy state, power/clock/light-sleep state, save/restore activity, WGP power transitions, aborted power-down, page/change events, and soft-reset state.
- `RLC_RLCS_IOV_CMD_STATUS`, `RLC_RLCS_IOV_CNTX_LOC_SIZE`, `RLC_RLCS_IOV_SCH_BLOCK`, and `RLC_RLCS_IOV_VM_BUSY_STATUS`, exposing SR-IOV command, context, scheduler, and VM-busy state.
- `RLC_RLCS_IH_SEMAPHORE`, `RLC_RLCS_IH_COOKIE_SEMAPHORE`, `RLC_RLCS_CP_INT_*`, `RLC_RLCS_SPM_INT_*`, and `RLC_RLCS_DSM_TRIG`, covering interrupt ownership, auto-ack/pending state, interrupt info payloads, and DSM trigger.
- `RLC_RLCS_BOOTLOAD_STATUS`, with fuse distribution, GFX init, GPM IRAM load/done, and `BOOTLOAD_COMPLETE` bits.
- `RLC_RLCS_GRBM_IDLE_BUSY_STAT`, `RLC_RLCS_GRBM_IDLE_BUSY_INT_CNTL`, and `RLC_RLCS_CMP_IDLE_CNTL`, which report/clear SDMA busy-change signals and compare-idle hysteresis state.
- `RLC_RLCS_GENERAL_0..16`, full-width scratch/data registers.
- `RLC_RLCS_BOOTLOAD_ID_STATUS1/2`, one-bit loaded indicators for bootload IDs 0 through 63.
- `RLC_RLCS_GCR_DATA_0..4` and `RLC_RLCS_GCR_STATUS`, carrying phase data/status.
- `RLC_RLCS_PERFMON_CLK_CNTL_UCODE`, `RLC_RLCS_UTCL2_CNTL`, and the IMU/RLC message data/control/cntl/status fields.
- `RLC_RLCS_IMU_RAM_*` and `RLC_RLCS_IMU_GFX_DOORBELL_FENCE`, exposing indexed IMU RAM address/data windows and doorbell-fence controls.
- `RLC_RLCS_SDMA_INT_CNTL_1/2`, `RLC_RLCS_SDMA_INT_STAT`, and `RLC_RLCS_SDMA_INT_INFO`, covering SDMA interrupt control and diagnostic payloads.
- `RLC_RLCS_GFX_MEM_POWER_CTRL_0..2` and `RLC_RLCS_IH_CTRL_1..3`/`RLC_RLCS_IH_STATUS`, describing graphics memory power control and IH control/status.
- `RLC_RLCS_FED_STATUS`, `RLC_RLCS_FED_RESP`, `RLC_RLCS_FED_INT_MASK`, `RLC_RLCS_MEM_FED`, `RLC_UTCL2_FED_STATUS_SNAP`, `RLC_SE0_FED_STATUS_SNAP`, `RLC_SE1_FED_STATUS_SNAP`, `RLC_CANE_FED_STATUS_SNAP`, `RLC_CONSOLIDATED_FED_STS`, and `RLC_HOST_FED_ACK`, which expose fatal-error-detection status, acknowledgements, masks, memory read/transaction errors, snapshots, consolidated status, and FLR-needed indication.
- `RLC_RLCS_SE_PWR_CTRL`, `RLC_RLCS_SB_RLC_ROM_STATUS`, `RLC_RLCS_SB_ROM_STATUS`, `RLC_RLCS_UTCL2_BUSY_CNTL`, and `RLC_RLCS_UTCL2_BUSY_STAT`, covering shader-engine power/reset control, ROM status, and UTCL2 busy request/ack handshake.

Observed integration in this tree includes `amdgpu/gfx_v12_1.c`, which reads `regRLC_RLCS_BOOTLOAD_STATUS` and checks `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`, and reads `regRLC_RLCS_FED_STATUS` to classify FED errors. Similar bootload polling exists in `gfx_v12_0.c` and older generation code.

### PF/VF RLC, SPM, CSIB, and VFI Fields

The `pfvfdec_rlc` block defines fields visible through the PF/VF RLC decode aperture:

- `RLC_SAFE_MODE` repeats the command/message/response safe-mode pattern.
- `RLC_SPM_SAMPLE_CNT`, `RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, `RLC_SPM_INT_STATUS`, and `RLC_SPM_INT_INFO_1/2` expose SPM sample count, memory-client attributes, interrupt enable/status, and interrupt payload/ID.
- `RLC_CSIB_ADDR_LO/HI` and `RLC_CSIB_LENGTH` describe a command/status buffer address and length.
- `RLC_CP_SCHEDULERS`, `RLC_CP_EOF_INT`, and `RLC_CP_EOF_INT_CNTL` expose CP scheduler IDs and EOF interrupt state/control.
- `RLC_SPARE_INT_0..2` and `RLC_RLCV_SPARE_INT_1` provide spare interrupt payload, processing, complete, or interrupt bits.
- `RLC_VFI_CMD`, `RLC_VFI_STAT`, `RLC_VFI_GRBM_GFX_INDEX`, `RLC_VFI_GRBM_GFX_CNTL`, `RLC_VFI_ADDR`, and `RLC_VFI_DATA` are full-width virtual-function interface command/status and indirect register windows.

These definitions are especially sensitive to virtualization context. The same bitfield name may be compiled into PF, VF, or reset/error paths, but valid access depends on the register aperture and firmware policy.

### Power, Security, PSP, and Clock-Gating Fields

The chunk then enters several smaller decode blocks:

- `GRBMX_GLARB_BUSY_MASK` and `CGTT_*_CLK_CTRL` define busy masks, clock on-delay/off-hysteresis, performance/debug enables, soft-stall overrides, and clock override bits for IA, WD, CP, CPF, CPC, RLC, GCR, GC CAC, GRBM, and related CPWD blocks.
- `GFX_ICG_*`, `GC_EA_CPWD_ICG_CTRL`, `CC_GC_HBM_DISABLE`, `GRBMX_LPDDR_DISABLE_0/1`, `GLARBI_GLARBR_MGCG_OVERRIDE`, `ICG_GLARBA_CTRL`, and `ICG_GLARBC_CLK_CTRL` describe internal clock-gating and memory-interface disable/override state.
- `GC_EA_CPWD_SDP_SECLEVEL_NONIO_MAP0..3`, `GC_EA_CPWD_SDP_ERR_CTRL`, `GRBM_SRCID_CAM_*`, `GRBM_IOV_*`, `GRBM_SEC_CNTL`, `GRBM_CAM_*`, `RLC_REG_SEC_INT_STATUS`, `RLC_FWL_FIRST_VIOL_ADDR[_HI]`, and `RLC_UTC_BYPASS_CNTL` define security/trust-level maps, SDP parity/error injection controls, GRBM source-ID and remap CAMs, IOV range controls, firewall violation counters/addresses, and UTC bypass bits for RLC subclients.
- `CP_MES_DM_INDEX_*`, `CP_MEC_DM_INDEX_*`, `CP_GFX_RS64_DM_INDEX_*`, `CPG_PSP_DEBUG`, and `CPC_PSP_DEBUG` expose PSP-side CP data-memory index windows and debug override bits for privilege, GPA, ucode VF, MTYPE/TMZ, and secure-register handling.
- `CHI_CHR_MGCG_OVERRIDE`, `ICG_CHA_CTRL`, and `ICG_CHC_CLK_CTRL` define CH/CHA/CHC medium-grain and internal clock-gating overrides.

These fields connect RLC/GC operation with power management, security isolation, PSP/debug policy, and clock-gating behavior. They should be treated as platform bring-up and recovery controls, not generic debug knobs.

### GFX IMU Mailbox and Handshake Fields

The final portion starts the GFX IMU decode block:

- `GFX_IMU_C2PMSG_0..47` are 48 full-width client-to-platform mailbox payload registers.
- `GFX_IMU_MSG_FLAGS` exposes full-width mailbox/status flags.
- `GFX_IMU_C2PMSG_ACCESS_CTRL0` carries 3-bit access fields for mailboxes 0 through 7; `GFX_IMU_C2PMSG_ACCESS_CTRL1` groups access for mailbox ranges 8-15, 16-23, 24-31, 32-39, and 40-47.
- `GFX_IMU_PWRMGT_IRQ_CTRL` exposes a power-management IRQ request bit, and `GFX_IMU_MP1_MUTEX` exposes a 2-bit MP1 mutex.
- `GFX_IMU_RLC_DATA_0..4`, `GFX_IMU_RLC_CMD`, `GFX_IMU_RLC_MUTEX`, and `GFX_IMU_RLC_MSG_STATUS` define the IMU-to-RLC message data/command/mutex/status path, including busy, error, message-done, change-toggle, and done-toggle bits.
- `RLC_GFX_IMU_DATA_0` and `RLC_GFX_IMU_CMD` are the reverse RLC-to-IMU command path.
- `GFX_IMU_RLC_STATUS` reports power-domain active and RLC-alive state.
- `GFX_IMU_STATUS` reports GFXOFF allowance, FA/DCS allowance, a disable-GFXCLK-DS bit, and several generated TBD fields.
- `GFX_IMU_SOC_DATA`, `GFX_IMU_SOC_ADDR`, and `GFX_IMU_SOC_REQ` define a SOC access request window with busy, read/write, and error bits.
- `GFX_IMU_VF_CTRL` carries VF enable, VFID, and QoS fields.
- `GFX_IMU_SCRATCH_0..5` are full-width scratch/data registers; the family continues in the next chunk.

Direct consumers found in the source tree include `amdgpu/imu_v12_0.c`, `amdgpu/imu_v12_1.c`, and older IMU paths that write `regGFX_IMU_C2PMSG_ACCESS_CTRL0/1`, use `GFX_IMU_C2PMSG_16`, and store/read IMU firmware version data through `GFX_IMU_SCRATCH_*` registers. `amdgpu/gfx_v11_0.c` reads `regGFX_IMU_SCRATCH_0` into `adev->gfx.imu_fw_version`, and the same IMU mailbox/access-control pattern carries into GC 12 code.

## Control Flow and State Behavior

This header has no runtime control flow. Its effect is compile-time: C code uses the generated constants to compose writes and decode reads of 32-bit MMIO registers.

The state described by the chunk is hardware and firmware state. Important state classes include:

- Live RLC/IH buffer levels, loading, protocol-error, overflow, arbiter grant, SDMA busy, FED error, and UTCL2 busy/request/ack status.
- RLC SPM delay, block-enable, memory-client attributes, sample count, interrupt status, and interrupt payload state.
- RLC LX6/XT firmware status, busy/pending state, interrupt vectors, fault info, doorbell data, and memory sleep controls.
- Command/mailbox state for RLCV, SMU, SRM/GPM, RLC/IMU, IMU/SOC, MP1, and PF/VF VFI paths.
- Bootload and firmware-load state, including `RLC_RLCS_BOOTLOAD_STATUS`, `RLC_RLCS_BOOTLOAD_ID_STATUS1/2`, IMU bootload address/size/reset-vector fields, and IMU scratch registers.
- Power, clock-gating, deep-sleep, GFXOFF allowance, memory-power, shader-engine reset/clock, and clock-override state.
- Security and virtualization state, including trust-level maps, GRBM CAM/remap state, IOV ranges, firewall violation counters, VF/VFID/QoS, and PSP debug override bits.

Many fields are sticky status, write-one-clear, strobe, busy/ack, or toggle-protocol bits. Examples include RLC safe-mode command/response, SRM abort, CP/SPM interrupt acknowledge, GRBM idle/busy interrupt clear, DSM trigger, FED acknowledgements, host FED ack, UTCL2 busy ack, IMU/RLC message done/change toggles, and SOC request busy/error. The masks alone do not provide the required polling or timeout sequence.

## Dependencies and Integration Points

This generated header depends on matching GC 12.1.0 register-address and default-value headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` supplies the register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_default.h` supplies reset/default values where generated.
- AMDGPU SOC15 register helpers consume these field masks and shifts through `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related macros.

Observed or implied source-tree integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c` reads `regRLC_RLCS_BOOTLOAD_STATUS` and checks `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE`, and reads `regRLC_RLCS_FED_STATUS` for FED error classification.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_0.c` has analogous RLC bootload polling through `regRLC_RLCS_BOOTLOAD_STATUS`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.c` and `imu_v12_1.c` configure IMU mailbox access and firmware/RLC RAM flows using the same IMU register families that begin here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/*` maps `GFX_IMU` as an SMU feature on relevant platforms, making the IMU status/mailbox and power-management request fields part of the larger power-management contract.
- Debug, reset, SR-IOV, and fatal-error-recovery paths use the RLC_RLCS, FED, VFI, GRBM security, and firewall fields to diagnose hangs, acknowledge errors, or coordinate FLR/recovery.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write adjacent hardware control bits, causing firmware boot failure, GPU hangs, missed interrupts, bad power-state transitions, or broken security isolation.
- This chunk crosses many address blocks. Reusing similar names across RLC, RLC_RLCS, PF/VF RLC, PSP, and IMU contexts without the matching `reg...` offset can target the wrong aperture.
- Several fields are command or handshake bits, not durable configuration. Misusing safe-mode commands, SRM/GPM commands, interrupt acknowledgements, FED acks, IMU/RLC toggles, or SOC request busy bits can race firmware or leave hardware waiting for an acknowledgement.
- RLC_RLCS bootload and bootload-ID fields are bring-up critical. Incorrect interpretation of `BOOTLOAD_COMPLETE`, IRAM load/done, or ID-loaded bits can create false successful initialization or spurious timeout failures.
- Power and clock-gating fields must remain coordinated with SMU, RLC firmware, and reset paths. Forcing CGTT/ICG/MGCG overrides, deep-sleep allowances, memory power controls, or GFXCLK DS disable bits outside established sequencing can cause intermittent hangs or excess power draw.
- FED and firewall/security fields are recovery and isolation sensitive. Incorrect masks can hide fatal errors, acknowledge the wrong source, misreport FLR-needed state, or weaken GRBM/SDP/firewall protection.
- IMU mailbox and scratch registers are firmware protocol surfaces. Access-control, mutex, status-toggle, and scratch-field misuse can desynchronize IMU firmware startup or power-management messages.
- The chunk starts and ends mid-family. Final file-level research must merge adjacent chunks before making complete claims about `RLC_GFX_IH_CLIENT_SE_STAT_H` and `GFX_IMU_SCRATCH_*`.

## Test and Validation Signals

Useful validation is mostly build, bring-up, reset, and hardware-integration coverage:

- Build AMDGPU, KFD, and SMU code paths that include `gc/gc_12_1_0_sh_mask.h`; this catches missing or renamed macros.
- GFX 12.1 boot tests should reach `RLC_RLCS_BOOTLOAD_STATUS.BOOTLOAD_COMPLETE` without timeout and should report sane `RLC_RLCS_BOOTLOAD_ID_STATUS1/2` values after firmware load.
- RLC/FED recovery tests should exercise `RLC_RLCS_FED_STATUS`, `RLC_RLCS_FED_RESP`, `RLC_RLCS_FED_INT_MASK`, `RLC_CONSOLIDATED_FED_STS`, and `RLC_HOST_FED_ACK`, including SDMA, CP, UTCL2, SE, CANE, and AID sources.
- Interrupt validation should cover CP/SPM interrupt pending/ack/info fields, SDMA interrupt status/info, IH status/control, and RLC GFX IH client buffer overflow/protocol-error reporting.
- Power-management and suspend/resume tests should cover CGTT/ICG clock overrides, RLC memory sleep controls, SOC/GFX deep-sleep allow masks, GFXOFF/FA-DCS allowance, and IMU power-management IRQ behavior.
- IMU firmware tests should validate mailbox access-control programming, `GFX_IMU_C2PMSG_*` exchanges, RLC/IMU command/data/status toggles, MP1/RLC mutex behavior, SOC request busy/error handling, and scratch register version reporting.
- SR-IOV and FLR tests should cover PF/VF safe-mode/VFI windows, VF control fields, GRBM IOV ranges, firewall violation reporting, and `NEED_TO_APPLY_FLR` propagation.
- Register dumps from hung or recovered systems should include the RLC_RLCS bootload, GPM, GRBM idle/busy, FED, memory-power, UTCL2 busy, IMU/RLC status, and security/firewall registers with values that match expected field boundaries.

## Chunk Notes

This document covers only `subset-b-002600`, lines 20297-22799 of `gc_12_1_0_sh_mask.h`. It deliberately does not create a final per-file report; the merge/reconciliation lane should combine this with adjacent chunk documents to complete the generated GC 12.1.0 register map analysis.

### subset-b-002601: lines 22800-25181

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 22800-25181

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for packing and decoding 32-bit register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin with the trailing `GFX_IMU_SCRATCH_5__DATA_MASK` from a register whose marker and shift are in the previous chunk, then cover GFX IMU scratch, timestamp, interrupt-controller, clock/reset/isolation, RAM, fence, timer, fuse, and bootloader fields. The range then crosses GRBMH, PA/GE, SQ/SQC/SQG, and the start of SX debug-busy fields. It ends inside `SX_DEBUG_BUSY_9`, after the first visible mask for `IDX_BANK7VAL2_BUSY`, so the complete SX busy diagnostic family continues in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph or distributed filesystem logic.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 graphics hardware. Driver code pairs these macros with the matching register addresses from `gc_12_1_0_offset.h` and uses them through helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` instead of hard-coding bit positions.

This chunk focuses on low-level graphics management, shader, cache/TLB, and diagnostics surfaces:

- GFX IMU state, including scratch registers, global timestamp offsets, PIC interrupt mask/level/edge/priority/status registers, interrupt-handler gasket state, clock and doorbell controls, RLC throttle/reset/override controls, DPM counters, RLC RAM access windows, fence logging, core control/status, reset and isolation controls, timers, fuse control, D-RAM/I-RAM access, and RLC bootloader address/size fields.
- GRBMH control and status, including read timeout, path disable controls, graphics block busy/clean indicators, fine-grain clock-gating target bits, soft reset bits, read-error capture, clock enables, invalid-pipe reporting, and sync state.
- PA/GE front-end controls for rate limiting, shader-array configuration, interface-safe registers, primitive assembler/setup/clip debug and FIFO controls, and scan-converter debug control.
- SQ/SQC/SQG shader control registers, including shader execution configuration, SQC cache behavior, random wave priority, FIFO sizing, deterministic stress/error injection controls, PIT weights, thread-trace selection, shader cycle counters, host trap status, GL1X status/control, performance snapshot control, watchpoint address/control registers, UTCL0 fault/retry/control registers, VMID fault/error status, indirect SQ register access, timeout status, and miscellaneous SQC controls.
- SX shader-export debug state, including busy bitmaps for exp FIFOs, export buffers, scoreboards, column request paths, blend queues, position/index banks, and related reserved fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the raw mask for that field inside the 32-bit register value.
- Matching register addresses and base indices are supplied by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h`.
- Consumers normally combine these symbols with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, SOC15 register-offset helpers, indexed-register helpers, debugfs/register-dump code, and firmware or command-stream programming paths.

Important register groups in this range include:

- `GFX_IMU_SCRATCH_6` through `GFX_IMU_SCRATCH_15`: full-width scratch data registers used as firmware/driver-visible IMU scratch state. The chunk starts with only the final mask for `GFX_IMU_SCRATCH_5`.
- `GFX_IMU_FW_GTS_*`, `GFX_IMU_GTS_OFFSET_*`, and `GFX_IMU_RLC_GTS_OFFSET_*`: low/high timestamp and timestamp-offset fields, with 32-bit low halves and 24-bit high halves.
- `GFX_IMU_CORE_INT_STATUS`, `GFX_IMU_PIC_INT_MASK`, `GFX_IMU_PIC_INT_LVL`, `GFX_IMU_PIC_INT_EDGE`, `GFX_IMU_PIC_INT_PRI_0` through `GFX_IMU_PIC_INT_PRI_7`, `GFX_IMU_PIC_INT_STATUS`, `GFX_IMU_PIC_INTR`, and `GFX_IMU_PIC_INTR_ID`: IMU interrupt state, masking, trigger mode, priority, active interrupt reporting, and interrupt ID decode.
- `GFX_IMU_IH_CTRL_*`, `GFX_IMU_IH_STATUS`, and `GFX_IMU_GFX_IH_GASKET_CTRL`: interrupt-handler gasket controls and buffer status/overflow visibility.
- `GFX_IMU_GFXCLK_BYPASS_CTRL`, `GFX_IMU_CLK_CTRL`, `GFX_IMU_RLC_CG_CTRL`, `GFX_IMU_RLC_THROTTLE_GFX`, `GFX_IMU_GFX_RESET_CTRL`, `GFX_IMU_VDCI_RESET_CTRL`, and `GFX_IMU_GFX_ISO_CTRL`: clock bypass/gating, throttling, reset, VDCI reset, and isolation controls.
- `GFX_IMU_RLC_RAM_INDEX`, `GFX_IMU_RLC_RAM_ADDR_HIGH`, `GFX_IMU_RLC_RAM_ADDR_LOW`, `GFX_IMU_RLC_RAM_DATA`, `GFX_IMU_D_RAM_ADDR`, `GFX_IMU_D_RAM_DATA`, `GFX_IMU_I_RAM_ADDR`, and `GFX_IMU_I_RAM_DATA`: indexed RAM access windows for RLC, data RAM, and instruction RAM.
- `GFX_IMU_RLC_BOOTLOADER_ADDR_HI`, `GFX_IMU_RLC_BOOTLOADER_ADDR_LO`, and `GFX_IMU_RLC_BOOTLOADER_SIZE`: bootloader location and size fields in the `gfx_imu_pspdec` address block.
- `GRBMH_STATUS`, `GRBMH_SOFT_RESET`, `GRBMH_READ_ERROR`, `GRBMH_GFX_CLKEN_CNTL`, `GRBMH_NOWHERE`, `GRBMH_INVALID_PIPE`, and `GRBMH_SYNC`: GRBMH status, reset, error, clock, invalid access, and synchronization field definitions.
- `GE_RATE_CNTL_*`, `CC_GC_SHADER_ARRAY_CONFIG`, `GE_SE_CNTL_STATUS`, `GE_SPI_IF_SAFE_REG`, `GE_PA_IF_SAFE_REG`, `PA_SU_DEBUG_CNTL`, `PA_CL_CNTL_STATUS`, `PA_CL_ENHANCE`, `PA_CL_RESET_DEBUG`, `PA_SU_CNTL_STATUS`, `PA_SC_FIFO_DEPTH_CNTL`, `PA_PH_DEBUG_CNTL`, and `PA_SC_DEBUG_CNTL`: geometry, primitive assembly, clipping, setup, and scan-converter debug/configuration knobs.
- `SQ_CONFIG`, `SQC_CONFIG`, `SP_CONFIG`, `SQ_ARB_CONFIG`, `SQ_DYN_VGPR`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, and `SQ_PIT_WEIGHT`: shader execution, arbitration, cache, FIFO, dynamic VGPR, and stress/error-injection layout.
- `SQ_SHADER_CYCLES_LO/HI`, `SQ_PERF_SNAPSHOT_CTRL`, `SQ_INTERRUPT_AUTO_MASK`, `SQ_INTERRUPT_MSG_CTRL`, and `SQ_DEBUG_HOST_TRAP_STATUS`: shader cycle/performance snapshot, interrupt, and trap debug fields.
- `SQ_WATCH0_*` through `SQ_WATCH3_*`: four shader watchpoint address/control sets with address high/low fragments, VMID fields, masks, and valid bits.
- `SQG_UTCL0_*`, `SQC_UTCL0_*`, `SQG_VMID_FED_*`, `SQG_SE_PIT_CONTROL`, `SQC_PIT_CONTROL*`, `SQC_MISC_CONFIG`, `SQ_TIMEOUT_CONFIG`, and `SQ_TIMEOUT_STATUS_SIMD*`: shader TLB/cache fault, retry, PIT, timeout, and miscellaneous control/status fields.
- `SQ_IND_INDEX`, `SQ_IND_DATA`, and `SQ_CMD`: indirect SQ register access and command fields.
- `SX_DEBUG_BUSY`, `SX_DEBUG_BUSY_2` through `SX_DEBUG_BUSY_9`, and `SX_DEBUG_1`: shader-export diagnostic busy/status bitmaps.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 12.1.0 generated register headers for the active ASIC.
2. Select a register address from `gc_12_1_0_offset.h`.
3. Use this file's shift/mask macros, usually through field helpers, to compose or decode a register value.
4. Read or write the register through MMIO, indexed access, RLC-safe accessors, firmware-mediated paths, command packets, register dump tools, profiling tools, or debugfs paths.

For IMU and GRBMH controls, higher-level code sequences reset, boot, clock, isolation, interrupt, and RAM-window operations around GPU initialization, firmware loading, reset, suspend/resume, or diagnostics. For SQ/SQC/SQG controls, runtime code and tooling program shader/cache/TLB controls, watchpoints, timeout behavior, performance snapshots, and trap/interrupt behavior. For SX debug registers, diagnostic code reads transient busy bitmaps to understand whether export, blend, position, or index paths are still active. This file does not encode ordering constraints, waits, privilege checks, clear-on-read/write-one-to-clear behavior, or side effects.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- GFX IMU scratch registers, timestamp offsets, interrupt-controller configuration, clock/reset/isolation settings, timer compare values, RAM-window indices, and bootloader address/size fields persist in the relevant hardware register file until reset, power-gating loss, firmware reinitialization, or driver reprogramming.
- IMU status, interrupt status, IH gasket status, DPM counters, timer values, core status, power-good, and overflow fields can change asynchronously as firmware and hardware run.
- GRBMH status and busy/clean fields are live hardware state for graphics blocks such as SC, DB, CB, UTCL1, TCP, GL1, GE, RLC, WGS, EA, GL2, SQG, PA, TA, SX, and SPI. Reset and clock-enable fields are persistent controls until cleared or reset.
- PA/GE debug/configuration fields are graphics front-end state. Some are passive configuration, while reset/debug fields can have side effects when written.
- SQ/SQC/SQG configuration, watchpoint, timeout, PIT, performance snapshot, and UTCL0 controls persist until overwritten, context-switched, reset, or power-managed. Status and retry/fault fields can be sticky, transient, or clear-sensitive depending on hardware semantics outside this header.
- SX debug-busy registers are observation surfaces for live pipeline state. They should be treated as snapshots, not persistent configuration.

Reserved fields appear throughout the chunk. Callers should preserve reserved bits during read-modify-write unless emitting a documented full-register value from the hardware programming guide.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h`, which supplies matching register offsets and base-index metadata. The generated shift/mask header must remain synchronized with that offset header and AMD's GC 12.1.0 register database.

Likely integration points in AMDGPU include:

- GFX IMU firmware/bootstrap, RLC interaction, doorbell, fence, interrupt, DPM, timer, reset, isolation, and RAM-access code paths that need the `GFX_IMU_*` fields.
- PSP/RLC firmware loading or validation paths that program `GFX_IMU_RLC_BOOTLOADER_*` fields.
- Graphics reset, hang diagnosis, and idle-wait paths that read `GRBMH_STATUS`, use `GRBMH_SOFT_RESET`, or inspect GRBMH read-error/invalid-pipe state.
- Power-management and clock-gating code that programs IMU/GRBMH/SQ/SQC/SX clock and fine-grain clock-gating override fields.
- Shader debug, trap, watchpoint, and timeout handling paths using `SQ_WATCH*`, `SQ_DEBUG_HOST_TRAP_STATUS`, `SQ_INTERRUPT_*`, and `SQ_TIMEOUT_*`.
- GPUVM fault/retry diagnostics and cache/TLB setup using `SQG_UTCL0_*`, `SQC_UTCL0_*`, and VMID fault/error status fields.
- Profiling and register-dump tooling that decodes shader cycle counters, performance snapshots, PIT controls, SQ/SQC/SQG status, and SX busy maps.

Because this is generated hardware metadata, most concrete behavior is expressed in consumers through AMDGPU helper macros and register-access wrappers rather than in this file.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while programming or decoding the wrong hardware bit.
- The chunk starts and ends mid-register family. It starts with only the mask for `GFX_IMU_SCRATCH_5__DATA`, while the associated marker/shift are in the previous chunk, and it ends inside `SX_DEBUG_BUSY_9`. The final file-level research must reconcile these artificial boundaries.
- IMU reset, isolation, clock, bootloader, RAM-window, and fence controls are low-level management surfaces. Misprogramming them can break firmware boot, RLC interaction, interrupts, reset recovery, or power transitions.
- PIC interrupt masks, levels, edges, priorities, status, and ID fields are dense and repetitive. Off-by-one shifts can route, mask, or prioritize the wrong interrupt and may only appear under specific firmware or fault conditions.
- Timestamp high fields use 24-bit masks while low fields are 32-bit. Consumers must not assume every low/high pair is two full 32-bit halves.
- Indexed RAM and indirect SQ access registers require correct sequencing outside this header. A valid mask does not guarantee that arbitrary reads/writes are safe at runtime.
- Reset, soft-reset, timeout, trap, fault, and error-injection fields may be write-one-to-clear, pulse-style, sticky, or side-effecting. The generated macros do not describe access semantics.
- Watchpoint address fields are split and aligned, with low address fields beginning at bit 6 and high address fields using 25 bits. Ad hoc address packing can silently produce watchpoints on the wrong address range.
- UTCL0 fault/retry and VMID fault/error status fields can be transient or sticky. Poor clear/sampling order can hide faults or report stale VMID state.
- SX debug-busy bitmaps are broad and highly repetitive. A mask mismatch can make diagnostics claim the wrong sub-pipeline is stuck, which is especially risky during hang triage.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and hardware/runtime diagnostics:

- Build AMDGPU code paths that include `gc_12_1_0_sh_mask.h` and `gc_12_1_0_offset.h`; missing or renamed macros should surface at compile time.
- Mechanically compare this line range against AMD's authoritative GC 12.1.0 register database. Every complete field should have matching `__SHIFT` and `_MASK` entries, and masks should align with their shifts.
- Cross-check the registers named in this chunk against `gc_12_1_0_offset.h` for matching address definitions and base indices.
- Run static sanity checks for repeated structures: PIC mask/level/edge bitmaps, eight interrupt-priority registers, timer0/timer1 layouts, watchpoint0-3 layouts, SQG/SQC UTCL0 controls, and SX debug-busy register families should remain structurally consistent where hardware expects repetition.
- Exercise GPU init, firmware boot, suspend/resume, GPU reset, and RLC/IMU bring-up on GC 12.1.0 hardware. Signals include successful IMU/RLC boot, stable doorbell/interrupt delivery, no unexpected fence-log or IH overflow, and clean reset recovery.
- Validate GRBMH idle/hang diagnostics by comparing decoded `GRBMH_STATUS`, read-error, invalid-pipe, and sync fields against known-good register dumps or simulator traces.
- Run shader debug and trap/watchpoint tests that program `SQ_WATCH*`, generate controlled traps or memory accesses, and verify that decoded status/VMID/address fields match the workload.
- Run GPUVM fault/retry tests that exercise SQG/SQC UTCL0 status and retry controls, with expected signals in VMID fault/error fields and no stale or missing fault reporting.
- Run profiling or performance snapshot tests using shader cycle counters and `SQ_PERF_SNAPSHOT_CTRL`, checking that controlled workloads move expected counters.
- During hang or stress tests, sample SX debug-busy registers and compare decoded busy bits with hardware traces or known pipeline activity.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002601`. The previous chunk owns the beginning of the `GFX_IMU_SCRATCH_5` definition. This chunk then covers most of the visible IMU management block, GRBMH, PA/GE debug/configuration, SQ/SQC/SQG shader and TLB/cache controls, and the beginning of SX debug-busy state. The next chunk should complete `SX_DEBUG_BUSY_9` and continue the remaining generated GC 12.1.0 shift/mask definitions. The final per-file research should merge these boundaries before describing the complete `gc_12_1_0_sh_mask.h` register map.

### subset-b-002602: lines 25182-27636

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 25182-27636

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the tail of the `SX_DEBUG_BUSY_9` mask list, then cover `SX_DEBUG_BUSY_10` and a broad SPI diagnostics/configuration block. The main middle of the chunk crosses generated address blocks for TP (`TD_*`, `TA_*` texture front-end controls), RB (`DB_*`, `CB_*`, `GB_*`, backend/render-cache controls), `spipdec2` throttle controls, RMI memory-interface controls, UTCL1 cache/TLB controls, and the beginning of SH shader-program registers for PS, GS/ESGS, and the start of HS/LS state. Although the path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for the GC 12.1.0 graphics IP. Driver code pairs these masks with register addresses from the matching `gc_12_1_0_offset.h` header and uses AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to pack fields before MMIO writes, command-packet programming, or firmware setup, and to decode status/debug reads.

This chunk describes several hardware areas:

- SX/SPI busy/debug controls, scratch status, wave lifetime controls/status, compute-unit enable masks, work-pending/active counters, lightweight-bench data selectors, GDS/SX buffer sizing, trap-screen registers, and crawler controls.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_tpdec`: TD/TA texture data/address controls, power/debug enable bits, format/rounding/aniso/determinism settings, FIFO credits, and texture front-end busy/status bits.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_rbdec`: DB depth/stencil debug and FIFO/arbiter controls, backend memory/cache/free-cacheline/ring/watermark fields, CB hardware controls, backend mapping/GPU ID fields, cache eviction points, and fine-grain clock-gating override fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_spipdec2`: pixel-queue event and export throttle fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_rmi_gfx_se_rmidec`: RMI routing, request/return queue state, UTCL1-facing controls, formatter, scoreboard, crossbar arbiter, XNACK/debug, CID mapping, spare/mode bits, and redundancy controls.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_utcl1dec`: UTCL1 bypass/page-size/hash/allocation-log/status fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_shdec`: shader-program checksum, program-address, resource, user-data, request-control, output-config, meshlet, and user-accumulator fields for PS, GS/ESGS, and the beginning of HS/LS.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register-address symbols are provided by the companion GC 12.1.0 offset header and are consumed by AMDGPU MMIO helpers, packet builders, debug paths, golden-register programming, and hang-dump code.

Notable macro families in this slice are:

- `SX_DEBUG_BUSY_9` tail and `SX_DEBUG_BUSY_10`: SX busy bits for index/value banks and POS/IDX scoreboard, requester, PA/SX, and write-control queues.
- `SPI_DEBUG_CNTL`, `SPI_DEBUG_CNTL_2`, `SPI_DEBUG_CNTL_3`, `SPI_DEBUG_READ`, `SPIRA_DEBUG_READ`, `SPIS_DEBUG_READ`, and `BCI_DEBUG_READ`: selectors and read-data fields for SPI debug inspection, plus gating/debug overrides and FIFO debug write enablement.
- `SPI_DEBUG_BUSY`, `SPI_SLAVE_DEBUG_BUSY`, `SPI_WGP_WORK_PENDING`, `SPI_CSQ_WF_ACTIVE_STATUS`, `SPI_*_WF_ACTIVE_COUNT*`, `SPI_WF_LIFETIME_*`, `SPI_PS_MAX_WAVE_ID`, and `SPI_SCRATCH_ADDR_STATUS`: live status and instrumentation fields for shader-stage busy state, scratch overflow attribution, wave IDs, lifetime accounting, and per-WGP/CSQ wave activity.
- `SPI_CONFIG_PS_CU_EN` and `SPI_CONFIG_CU_MASK_{GFX,HP3D,CS}*`: CU and WGP masks for pixel, graphics/HP3D, and compute scheduling paths.
- `SPI_LB_*`, `SPI_GDS_CREDITS`, `SPI_SX_EXPORT_BUFFER_SIZES`, `SPI_SX_SCOREBOARD_BUFFER_SIZES`, `SPI_P0/P1_TRAP_SCREEN_*`, `SPI_GFX_CRAWLER_CONFIG`, and `SPI_CS_CRAWLER_CONFIG`: lightweight-benchmark counters, GDS/SX credit sizing, trap-screen address/range filters, and crawler activity/FSM controls.
- `TD_*` and `TA_*`: texture-data/address registers covering format behavior, rounding, power throttling, debug enable, FIFO credits, anisotropic filtering parameters, deterministic-mode disables, PRT behavior, texture status, and scratch/debug data.
- `DB_DEBUG*`, `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH*`, `DB_RING_CONTROL`, `DB_MEM_*`, `DB_ARB_CONFIG`, `DB_EXCEPTION_CONTROL`, `DB_DFD_INDIRECT_*`, `DB_SUMMARIZER_TIMEOUTS`, and `DB_FGCG_*`: depth/stencil backend debug, compression, HiZ/HiS, stencil/depth read forcing, arbitration, FIFO sizing, cacheline/watermark tuning, exception handling, indirect DFD access, summarizer timeout, and clock-gating controls.
- `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG_1`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `GB_ADDR_CONFIG_READ`, `CB_HW_CONTROL*`, `CB_HW_MEM_ARBITER_CTL`, `CB_FGCG_SRAM_OVERRIDE`, and `CB_CACHE_EVICT_POINTS`: render backend disable/configuration, GPU/backend mapping, color-buffer hardware control, cache arbiter, SRAM clock-gating override, and evict thresholds.
- `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL`: event/throttle knobs for SPI pixel/export paths.
- `RMI_*`: memory-interface general controls/status, subblock busy/status, crossbar setup, probe pop logic, XNACK and UTC/UTCL1 controls, TCIW formatter, scoreboard counters/status, arbiter config, clock control, UTCL1 status, RB/GLX CID mapping, spare behavior, and redundancy repair controls.
- `UTCL1_CTRL_1`, `UTCL1_HASH_CTRL`, `UTCL1_ALOG`, and `UTCL1_STATUS`: per-client bypass, invalidation forcing, page-size, hashing, allocation logging, idle/busy, XNACK, and range-invalidation status.
- `SPI_SHADER_PGM_*_{PS,GS,HS}` and `SPI_SHADER_USER_DATA_*`: shader program code addresses/checksums, resource fields for VGPR/SGPR counts, priority, float mode, privilege/debug/trap/exceptions, scratch/LDS/shared VGPR configuration, CU enables, wave limits, instruction prefetch, and 32 dword user-data windows for PS and GS.
- `SPI_SHADER_REQ_CTRL_{PS,ESGS}`, `SPI_SHADER_GS_OUT_CONFIG_PS*`, `SPI_SHADER_GS_MESHLET_*`, and `SPI_SHADER_USER_ACCUM_*`: scheduling request grouping/throttling, GS/PS export/interpolator counts, meshlet dimensions/export allocation/interleave, and user accumulator contribution fields.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 12.1.0 generated register headers for the detected ASIC.
2. Choose a register address from the matching offset header.
3. Read the current register value, prepare an indexed/debug/perf access, or construct a command/MMIO write value.
4. Use these `__SHIFT` and `__MASK` constants, typically through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract field values.
5. Apply the value in initialization, golden-register programming, shader/ring setup, queue scheduling, power management, reset/recovery, debugfs, hang analysis, or performance/telemetry code.

For the SPI and SX debug groups, runtime code selects a pipe/thread/group/SIMD/SH/debug bank, enables the debug register path when needed, then reads the relevant debug data or busy register. Wave lifetime and active-count fields are live counters/status registers; reset/count controls and selector registers must be sequenced by the driver or firmware, not by this header.

For TD/TA, DB/CB/GB, RMI, and UTCL1 fields, initialization and golden-setting paths program persistent hardware policy: texture formatting and determinism, backend compression/debug modes, cache and FIFO depths, arbitration, memory-interface routing, XNACK behavior, UTCL1 bypass/hash/page-size, and clock-gating overrides. Status registers are read by diagnostics and hang/recovery paths to determine which subblocks remain busy.

For SH shader-program fields, graphics pipeline setup programs code base addresses, resource descriptors, per-stage user SGPR/user-data registers, trap/exception behavior, CU masks, wave limits, GS meshlet parameters, and GS/PS export/interpolator counts before waves are launched. The macros do not document the higher-level packet ordering, cache flush, VMID, or firmware sequencing needed around those writes.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, command submission, and AMDGPU initialization/recovery code.

SPI/SX status fields are mostly live hardware state: busy bits, active wave counts, work-pending bits, scratch overflow attribution, wave lifetime counters, and debug-read data can change while the GPU is running. Some control fields, such as `SPI_GFX_CNTL__RESET_COUNTS`, debug enable/selectors, crawler controls, CU masks, and trap-screen ranges, persist until reprogrammed or reset and may have side effects when written.

TD/TA, DB/CB/GB, RMI, and UTCL1 control registers persist as pipeline, cache, routing, arbitration, compression, XNACK, clock-gating, and TLB/cache policy. Incorrect full-register writes can alter unrelated reserved or mode bits, disable compression or cache behavior, starve queues, force unnecessary bypasses, or leave the frontend/backend stuck in a debug or low-power override mode. Busy/status registers should be treated as volatile, and indirect DFD/debug accesses may need hardware-specific select/read sequencing outside this header.

Shader-program and user-data registers are persistent pipeline state for a draw or dispatch context. Program low/high address fields, user-data address fields, resource descriptors, CU masks, wave limits, trap/exception enables, LDS/shared VGPR sizing, meshlet controls, and export/interpolator counts must match the compiled shader and command stream. A bad mask or shift can point execution at the wrong code address, allocate the wrong VGPR/SGPR/LDS resources, corrupt user SGPR mapping, misconfigure trap handling, or produce invalid exports.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_default.h`, where present, provides reset/default values for related registers.
- Common AMDGPU macros and helpers, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, and golden-register programming helpers, consume these field definitions.
- GC 12.1.0 code that includes this header includes AMDGPU graphics initialization/recovery, MES, SDMA, IMU, gfxhub, KFD queue management, and AMDKFD interop paths.

Integration points include shader setup for PS/GS/HS/LS, command processor and graphics ring initialization, KFD/compute scheduling masks, trap/debug-screen programming, debugfs and hang dumps, performance and wave-lifetime telemetry, golden-register tables, power/clock-gating policy, cache/TLB invalidation diagnostics, XNACK handling, render-backend compression and eviction tuning, and RMI/UTCL1 routing between shader, texture, render-backend, and memory-system blocks.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- The chunk starts and ends mid-family. It begins in the tail of `SX_DEBUG_BUSY_9` and ends in the middle of `SPI_SHADER_PGM_RSRC1_HS`; adjacent chunks are required for complete SX and HS/LS shader-resource context.
- Similar register families are not interchangeable. PS, GS, ESGS, HS, CS, GFX, HP3D, TD/TA, DB/CB, and RMI fields often look structurally alike but have different widths, reserved bits, side effects, or stage-specific meanings.
- Debug and status registers can be volatile, latched, sticky, clear-on-read, or write-one-to-clear depending on hardware behavior not encoded here. Casual debug writes can disturb the state being investigated.
- Full-width `DATA`, `MEM_BASE`, and `CHECKSUM` masks do not imply unconstrained values. Address fields can have alignment, address-unit, VM, high/low split, or packet-ordering constraints outside this header.
- CU/WGP masks and shader resource fields affect scheduling and occupancy. Incorrect packing can disable compute units, over-allocate resources, break fairness, or produce launch failures only under specific shader stages.
- TD/TA determinism, texture-format, rounding, and PRT bits can cause subtle rendering differences rather than obvious crashes.
- DB/CB/RMI/UTCL1 control fields are high-risk for coherency and hangs: compression disables, cache bypasses, eviction points, FIFO depths, watermarks, XNACK behavior, and routing/hash fields can create data corruption, stalls, performance collapse, or reset loops if misprogrammed.
- Meshlet and GS/PS export fields must match shader compiler output. Mismatched threadgroup dimensions, export counts, primitive/interpolator counts, or LDS sizes can corrupt geometry/pixel data.
- Reserved masks are present in several registers. Callers should preserve reserved bits unless a hardware programming sequence explicitly requires a value.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_sh_mask.h`, especially GC 12.1.0 GFX, MES, KFD, gfxhub, SDMA, IMU, reset, debug, and power-management paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that registers in this chunk have matching address macros in `gc_12_1_0_offset.h` and expected reset/default entries where generated.
- Static mask/shift sanity checks: masks align with shifts, field masks do not overlap unexpectedly, repeated user-data families remain consistent, full-width fields use `0xFFFFFFFFL`, and reserved masks cover only unused bits.
- GFX bring-up and suspend/resume tests that validate golden-register writes for TA/TD, DB/CB, RMI, and UTCL1 controls without hangs or unexpected busy bits.
- Shader execution tests for PS, GS/ESGS, meshlet paths, and HS/LS startup that exercise program address packing, resource descriptors, user SGPR counts, scratch/trap/exception bits, CU masks, wave limits, LDS/shared VGPR sizing, exports, and user-data windows.
- Debug/hang tests that read `SPI_DEBUG_*`, `SX_DEBUG_BUSY_*`, `SPI_DEBUG_BUSY`, `SPI_SLAVE_DEBUG_BUSY`, TD/TA/DB/RMI/UTCL1 status fields, and scratch overflow attribution during known workloads.
- Wave telemetry tests that reset/read lifetime counters, active wave counts, max wave IDs, work-pending fields, CSQ active counts, and lightweight-benchmark data under controlled workloads.
- Render and texture stress tests covering anisotropic filtering, deterministic modes, gather/rounding behavior, PRT, depth/stencil compression, color-buffer cache eviction, DCC/compression behavior, backend mapping, and trap-screen ranges.
- Memory-system stress tests with XNACK, UTCL1 invalidation, RMI reorder/bypass/no-fill controls, crossbar arbitration, scoreboard status, and CID mapping while checking for faults, stale data, or reset loops.
- Runtime warning signals include stuck SPI/SX/TA/TD/DB/RMI/UTCL1 busy bits, shader launch failures, trap storms, bad scratch overflow attribution, incorrect wave counts, rendering corruption, cache coherency failures, XNACK anomalies, and repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002602`. It covers lines 25182-27636 of `gc_12_1_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the `SX_DEBUG_BUSY_9` context before line 25182 and the remaining HS/LS shader-resource definitions after line 27636.

### subset-b-002603: lines 27637-30183

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 27637-30183

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `__SHIFT` value and a matching `_MASK` value used by AMDGPU register helpers to compose or decode 32-bit MMIO/indexed-register values. There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the middle of the hull-shader resource programming family, immediately after earlier `SPI_SHADER_PGM_RSRC1_HS` shifts, and continue through hull-shader resource/user-data fields, SPI request/arbitration/debug/DIDT controls, TCP watchpoint fields, and a large graphics-decoder block for depth buffer, stencil, scissor, viewport, clip, VRS, color blend, and pixel-shader interpolation/input state. The chunk ends at the opening comment for `SPI_PS_INPUT_CNTL_23`, before that register's fields are emitted in the next chunk.

Although the repository path is nested under a `ceph-client` source mirror, this file is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for GC 12.1.0 registers. Driver code pairs these field macros with register address symbols from the matching GC 12.1.0 offset header and, where available, generated default/reset-value headers. Consumers normally use these constants through helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` so hardware register values can be packed or decoded without hard-coded bit positions.

This slice covers several graphics-programming surfaces:

- Hull/LS-HS shader state: `SPI_SHADER_PGM_RSRC1_HS`, `SPI_SHADER_PGM_RSRC2_HS`, 32 `SPI_SHADER_USER_DATA_HS_*` payload registers, `SPI_SHADER_REQ_CTRL_LSHS`, and four `SPI_SHADER_USER_ACCUM_LSHS_*` contribution registers.
- SPI scheduler and debug controls: time-slot arbitration, WCL pipe percentage controls for graphics, HP3D, and compute queues, per-VMID user-accum/debug controls, compute queue reset, wavefront context-save status, DIDT throttle controls, and DIDT type masks.
- TCP watchpoints: four watch address/control triplets with 48-bit-style high/low address fields, VMID matching, mask, mode, valid, and attach bits.
- DB/depth/stencil render state: render control/override, depth view and size, Z/stencil metadata/base addresses, GL1/cache temporal policy, depth bounds, count/viewport controls, VRS center location, shader/depth/stencil controls, EQAA, alpha-to-mask, stencil refs/op values/read masks/write masks, and TA border-color base address.
- PA/SC/CL viewport and clipping state: screen/window/generic/viewport scissors, clip rectangles and extensions, edge rules, hardware screen offsets, user clip planes, guard-band adjust registers, raster/tile steering controls, 16 viewport transform sets, and 16 Z min/max ranges.
- VRS and color state: VRS override, feedback/rate surface bases and sizes, VRS info, color-buffer GL2 cache policy, and constant blend color components.
- Pixel-shader input/interpolation state: `SPI_PS_IN_CONTROL`, interpolation control, shader index/position/Z/color export format, barycentric control, PS input enable/address masks, and `SPI_PS_INPUT_CNTL_0` through the start of `SPI_PS_INPUT_CNTL_23`.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.
- Register-address symbols are expected in the companion `gc_12_1_0_offset.h` header, commonly with `mm...` names matching these register names.
- AMDGPU callers normally access these fields through `REG_SET_FIELD`, `REG_GET_FIELD`, MMIO read/write helpers, command-packet register programming, debug/perf dump decoders, reset/recovery code, virtualization handling, and shader/pipeline state setup.

Important macro families in this slice include:

- `SPI_SHADER_PGM_RSRC1_HS` and `SPI_SHADER_PGM_RSRC2_HS`: hull-shader VGPR/SGPR counts, priority, float mode, privilege/debug/perf controls, forward progress, WGP mode, LS VGPR component count, FP16 overflow, scratch enable, user SGPR count, trap/OC LDS/threadgroup-size controls, exception enables, LDS size, and shared VGPR count.
- `SPI_SHADER_USER_DATA_HS_0..31`: full-width data payload registers used to pass shader user-data SGPR values to the hull-shader stage.
- `SPI_SHADER_REQ_CTRL_LSHS` and `SPI_SHADER_USER_ACCUM_LSHS_0..3`: LS-HS soft grouping, request count, allocation timeout, hard-lock thresholds, producer lockout, global scanning, allocation-rate throttling, and user-accum contribution fields.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0`, and `SPI_ARB_CYCLES_1`: SPI pipe time-slot ordering, duration multipliers, and per-time-slot cycle durations.
- `SPI_WCL_PIPE_PERCENT_GFX`, `SPI_WCL_PIPE_PERCENT_HP3D`, and `SPI_WCL_PIPE_PERCENT_CS0..7`: wavefront control/launch percentage fields for graphics, HP3D, and compute pipe groups.
- `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, `SPI_COMPUTE_WF_CTX_SAVE`, `SPI_SAVE_RESTORE_STATUS`, `SPI_CONFIG_DIDT_CNTL`, and `SPI_CONFIG_DIDT_TYPEMASK`: VMID-scoped accumulation/debug control, compute queue reset, wavefront context-save address/status, and dynamic instruction/data throttling configuration.
- `TCP_WATCH0..3_{ADDR_L,ADDR_H,CNTL}`: texture/cache watchpoint address and control fields with VMID, address mask, mode, valid, and attach behavior.
- `DB_RENDER_CONTROL`, `DB_DEPTH_VIEW`, `DB_DEPTH_VIEW1`, `DB_RENDER_OVERRIDE`, `DB_RENDER_OVERRIDE2`, `DB_DEPTH_SIZE_XY`, `DB_Z_INFO`, `DB_STENCIL_INFO`, and DB base-address pairs: depth/stencil surface layout, compression/decompression, HiZ/HiS, HTILE, Z-range precision, read/write base addresses, sample controls, and render override modes.
- `DB_SHADER_CONTROL`, `DB_DEPTH_CONTROL`, `DB_STENCIL_CONTROL`, `DB_EQAA`, and `DB_ALPHA_TO_MASK`: depth/stencil test state, shader export/depth ordering, sample/overrasterization behavior, alpha-to-mask offsets, and conservative/ordered pixel-shader controls.
- `SC_MEM_TEMPORAL`, `SC_MEM_SPEC_READ`, `PA_SC_*`, `PA_CL_*`, and `PA_SU_*`: cache temporal/speculative-read policy, viewport/scissor bounds, window offsets, clip rectangles, edge rules, raster config, tile steering, user clip planes, guard-band clip/discard adjust values, and viewport transforms.
- `PA_SC_VRS_*`: variable-rate shading override, rate/feedback surface addresses and dimensions, and VRS software mode fields.
- `CB_RMI_GL2_CACHE_CONTROL` and `CB_BLEND_*`: color-buffer GL2 read/write cache policy and full-width floating-point blend constant components.
- `SPI_PS_IN_CONTROL`, `SPI_INTERP_CONTROL_0`, `SPI_SHADER_*_FORMAT`, `SPI_BARYC_CNTL`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, and `SPI_PS_INPUT_CNTL_0..22`: pixel-shader interpolation mode, export format, barycentric enable/control, input enable/address bitmaps, and per-attribute interpolation controls. Attributes 0 through 19 include point-sprite texture fields; attributes 20 through 22 omit the point-sprite texture bits in this range.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 12.1.0 register metadata for the active ASIC generation.
2. Choose the matching register address from `gc_12_1_0_offset.h`.
3. Read an existing register value or construct a command-packet/MMIO register value.
4. Use the `__SHIFT`/`_MASK` pairs, usually through generated register helpers, to pack field values or extract status bits.
5. Apply the resulting value during shader setup, graphics draw state programming, VRS setup, depth/stencil/color state setup, TCP debug watchpoint programming, SPI scheduling/debug control, queue reset/recovery, or hang/perf diagnostics.

For shader setup, graphics pipeline code writes hull-shader resource registers, user-data registers, LS-HS request controls, and pixel-shader interpolation/input registers before dispatching draws. For render state, command submission programs DB/PA/SC/CL/CB state from API pipeline state: depth/stencil formats and bases, stencil refs/masks, viewport transforms, scissor rectangles, clip planes, blend constants, VRS rate images, and pixel-shader input mappings. For debug and recovery, code may program TCP watchpoints, decode SPI save/restore state, reset compute queues, inspect context-save wavefront status, or tune/disable SPI/DIDT behavior.

This generated header does not encode ordering requirements, polling loops, clear-on-read semantics, sticky bits, reserved-bit preservation rules, address alignment units, cache coherency sequences, or side-effect timing. Those rules live in AMDGPU engine code, firmware interfaces, command-stream validation, and hardware programming guides.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, and AMDGPU runtime programming.

Shader resource and user-data fields persist as context state until replaced by later command-stream writes, reset, preemption/context restore, or power-transition reinitialization. Incorrect VGPR/SGPR, LDS, scratch, trap, exception, user SGPR, or WGP-mode masks can make hull shaders launch with invalid resources, wrong trap behavior, or broken scratch/LDS accounting. Pixel-shader input and interpolation state similarly persists as draw state and must match compiled shader expectations; bad attribute offsets, defaults, flat-shade flags, validity bits, or barycentric controls can corrupt interpolation or make shaders read unintended attributes.

DB/PA/SC/CL/CB registers are active graphics pipeline state. Depth/stencil base addresses, metadata/compression modes, stencil refs/masks, depth bounds, viewport/scissor rectangles, clip planes, VRS surfaces, blend constants, and color/depth cache policy remain relevant across draws until reprogrammed. Split base address fields and `BASE_256B` VRS fields imply address-unit and alignment constraints outside this header. Full-register writes around dense render override and shader control registers must preserve reserved bits unless the hardware sequence explicitly defines them.

SPI scheduler, WCL, debug, DIDT, compute reset, and context-save status fields include privileged or side-effecting controls. Queue reset, wavefront save/restore, debug-per-VMID, and DIDT throttling can alter execution behavior or recovery state; they should not be treated as passive status. TCP watchpoint registers are persistent debug state and can affect memory/debug behavior for selected VMIDs and address windows until disabled.

Viewport, scissor, clip, and VRS arrays are heavily repeated state. Off-by-one index mistakes, partial programming of multi-register families, or mismatched top-left/bottom-right pairs can create rendering clipping errors that are hard to diagnose from register dumps alone.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register family staying internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` should provide matching register address macros.
- Any matching GC 12.1.0 default/reset header should remain consistent with these masks.
- AMDGPU register helpers provide the actual field packing/extraction and MMIO or command-packet access mechanisms.
- AMDGPU GFX, shader pipeline setup, graphics command submission, KFD/compute queue recovery, CP/SPI debug, VRS, DB/CB/PA/SC state emission, reset/suspend/resume, SR-IOV/virtualization, debugfs, perf, and hang-dump paths are likely consumers.

Integration points include hull-shader program resource emission, shader user-data upload, LS-HS scheduling controls, SPI pipe arbitration and WCL throttling, VMID-scoped debug/accumulation, compute queue reset and wavefront context-save handling, TCP watchpoint setup, depth/stencil surface programming, Z/stencil compression metadata, GL1/GL2 cache policy selection, stencil/depth tests, EQAA and alpha-to-mask behavior, screen/window/viewport scissors, clip rectangles and user clip planes, raster/tile steering, VRS rate/feedback images, blend constants, and pixel-shader attribute interpolation.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- This chunk starts and ends mid-family. `SPI_SHADER_PGM_RSRC1_HS` began before line 27637, and `SPI_PS_INPUT_CNTL_23` continues after line 30183; adjacent chunks are required for complete family-level conclusions.
- Many fields are repeated arrays with only index changes: 32 hull-shader user-data registers, 16 viewports, 16 viewport scissor pairs, 16 viewport transform/Z ranges, 6 user clip planes, 4 clip rectangles, 4 TCP watchpoints, and 23 visible pixel-shader input controls. Generator or copy mistakes can be isolated to one index and produce index-specific render/debug faults.
- Address fields use different units and widths. DB Z/stencil and TA base pairs, TCP high/low watch addresses, and VRS `BASE_256B` surfaces require correct split-address and alignment handling outside the mask definitions.
- Dense DB render override/control fields can carry side effects for compression, decompression, HiZ/HiS, sample counts, ReZ, VRS center selection, conservative/ordered pixel shader, and depth-before-shader behavior. Full-register writes are risky without reserved-bit preservation.
- Pixel-shader input controls are similar but not uniform. Attributes 0 through 19 expose point-sprite texture fields, while 20 through 22 in this range omit those fields; assuming a single template for all 32 inputs can encode nonexistent bits.
- Stencil and depth state contains front/back-face variants. Swapping `_BF` masks or default values can cause one-sided rendering failures that are not obvious in simple tests.
- Viewport/scissor fields mix 16-bit, 15-bit, 13-bit, 12-bit, and full-width data fields. Treating them as a uniform coordinate format can truncate or sign/extend incorrectly.
- VRS rate and feedback surfaces are stateful memory references. Wrong base, size, mode, or override fields can cause invalid shading rates, corrupt feedback, or memory faults.
- SPI compute reset, wavefront context-save, debug, TCP watchpoint, and DIDT controls are not harmless decode fields. Incorrect writes can reset queues, disturb debug sessions, change throttling, or mask execution problems.

## Test Signals

Useful validation is primarily generated-data consistency, build coverage, and graphics/runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_sh_mask.h`, especially GFX pipeline state, shader setup, DB/CB/PA/SC emission, VRS, debug/hang dump, reset, and queue recovery paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database to confirm every `__SHIFT` and `_MASK` value in this line range.
- Cross-checks that every register in this chunk has matching address macros in `gc_12_1_0_offset.h` and expected defaults in the matching generated default header where applicable.
- Static mask/shift sanity checks: masks should align with shifts, full-width data fields should use `0xFFFFFFFFL`, split base-address masks should match documented widths, repeated indexed families should remain structurally consistent where hardware intends, and fields should not overlap unless documented.
- Shader pipeline tests that validate HS resource programming, user-data SGPR layout, LS-HS request controls, pixel-shader input enable/address masks, interpolation defaults, flat shading, FP16 interpolation mode, barycentric controls, and export format selection.
- Render-state tests covering depth/stencil enable/write/compare modes, stencil front/back refs/op values/read/write masks, depth bounds, EQAA, alpha-to-mask, shader depth export/kill behavior, sample counts, and DB render override paths.
- Surface/address tests that program Z/stencil read/write bases, TA border-color base, and VRS rate/feedback bases with known aligned addresses and verify correct high/low or `BASE_256B` packing.
- Viewport/scissor/clip tests that exercise all 16 viewport rectangles, viewport scissors, viewport transforms, Z min/max ranges, screen/window/generic scissors, clip rectangles, clip rectangle extensions, edge rules, user clip planes, and guard-band adjustments.
- VRS tests that vary override rate, combiners, rate-surface enablement, feedback writeback, surface sizes, and software mode fields under controlled draws.
- TCP/debug tests that program watchpoints for each watch index and VMID, verify address match/mask behavior, and ensure disabling clears debug effects.
- SPI scheduling/recovery tests that cover WCL percentages, arbitration durations, user-accum VMID controls, compute queue reset, wavefront context-save status, and DIDT type masks without unexpected hangs or performance regressions.
- Runtime warning signals include HS launch failures, shader input/interpolation corruption, missing or wrong point-sprite attributes, depth/stencil one-sided failures, bad clipping/scissor behavior, invalid VRS rates or feedback writes, cache/compression anomalies, stuck compute queue reset, unexpected wavefront context-save state, TCP watchpoints firing on the wrong VMID/address, and GPU reset loops.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002603`. It covers lines 27637-30183 of `gc_12_1_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the partial `SPI_SHADER_PGM_RSRC1_HS` and `SPI_PS_INPUT_CNTL_23` families and to place these SPI, TCP, DB, PA/SC/CL, VRS, CB, and pixel-shader input definitions in the full GC 12.1.0 register map.

### subset-b-002604: lines 30184-32568

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 30184-32568

## Scope

This chunk covers a generated AMD GC 12.1.0 shader/register mask header range. It starts in the middle of `SPI_PS_INPUT_CNTL_23` and ends in the middle of `PA_SC_ENHANCE_2`, so merge-time reconciliation should join it with adjacent chunks for the complete file-level view. The range contains 2,179 `#define` macros: field shift constants named `...__SHIFT` and bit masks named `..._MASK` for graphics pipeline registers.

## Purpose

The header provides compile-time bitfield metadata for programming GC 12.1.0 registers in the AMDGPU driver. These macros let C code construct, mask, compare, or patch hardware register values without embedding raw bit positions. The covered registers describe late graphics-pipeline state: pixel shader input interpolation, shader export/blend optimization, color blend controls, primitive assembly and clipping/rasterization controls, depth/HiZ/HiS and binning controls, MSAA sample locations and masks, render target color buffer state, and several PA/SC enhancement controls.

The chunk does not implement functions or own runtime logic. Its behavioral importance comes from being included alongside companion address headers such as `gc_12_1_0_d.h`, where `mm...` register offsets are defined, and from being consumed by AMDGPU register programming paths, golden-register initialization, generated clear-state tables, command emission, and debug/register decode helpers.

## Important API Surface

- `SPI_PS_INPUT_CNTL_23` through `SPI_PS_INPUT_CNTL_31` expose per-pixel-shader input fields: `OFFSET`, `DEFAULT_VAL`, `FLAT_SHADE`, `ROTATE_PC_PTR`, `PRIM_ATTR`, `DUP`, `FP16_INTERP_MODE`, `USE_DEFAULT_ATTR1`, `DEFAULT_VAL_ATTR1`, `ATTR0_VALID`, and `ATTR1_VALID`. These shape how SPI routes interpolated or default primitive attributes into the pixel shader.
- `SPI_BARYC_SSAA_CNTL`, `SPI_TMPRING_SIZE`, and `SPI_GFX_SCRATCH_BASE_LO/HI` cover shader interpolation/sample behavior and shader scratch/tmp-ring memory programming. Scratch base fields split GPU addresses across low/high registers.
- `SX_PS_DOWNCONVERT_CONTROL`, `SX_PS_DOWNCONVERT`, `SX_BLEND_OPT_EPSILON`, `SX_BLEND_OPT_CONTROL`, and `SX_MRT0_BLEND_OPT` through `SX_MRT7_BLEND_OPT` describe shader-export color downconversion and per-MRT blend optimization controls.
- `CB_BLEND0_CONTROL` through `CB_BLEND7_CONTROL` define per-render-target blend equation fields: color/alpha source blend, destination blend, combine function, separate alpha blending, enable, and `DISABLE_ROP3`.
- `PA_CL_*`, `PA_SU_*`, `PA_SC_*`, `GE_*`, `VGT_*`, and `DB_*` macros cover primitive setup, clipping, viewport transform enablement, NGG/subgroup control, line/point state, stereo, variable-rate shading, conservative rasterization, AA sample layout, HiZ/HiS metadata surfaces, DB/HTILE behavior, GS output sizing, and draw payload handling.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_COLOR_CONTROL`, `CB_COLOR{0..7}_*`, and `CB_MEM{0..7}_INFO` define color buffer render target masks, shader write masks, color-control mode bits, render target base addresses, views, dimensions, swizzle/resource type attributes, FDCC compression controls, extended base-address bits, format/compression metadata, and memory info.
- The tail switches to address block `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_pfvf_padec` and defines `PA_SC_VRS_SURFACE_CNTL`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, and the first part of `PA_SC_ENHANCE_2`, covering VRS surface/cache controls and many rasterizer/scanner enhancement or workaround bits.

## Control Flow

There is no executable control flow in this range. Control flow is indirect: driver code combines these masks and shifts into register writes that are emitted through AMDGPU MMIO accessors, command processor packets, clear-state arrays, or golden-register setup. A typical use is:

1. Start from a desired 32-bit register value or a read-modify-write value.
2. Clear a field with `~REGISTER__FIELD_MASK`.
3. Insert a value with `(value << REGISTER__FIELD__SHIFT) & REGISTER__FIELD_MASK`.
4. Write the result to the matching `mmREGISTER` offset from the companion register-address header.

Because many registers in this range are replicated by slot, state emission code generally loops or expands over MRT/render-target indices 0 through 7, selecting matching `CB_COLORn_*`, `CB_BLENDn_CONTROL`, or `SX_MRTn_BLEND_OPT` macros.

## State and Persistence

The macros are stateless, but they describe persistent GPU context state. Values programmed into these registers persist in the graphics context until changed by later command streams, clear-state restore, context switch restore, or device reset. Important persistent domains include:

- Pixel shader ABI state in `SPI_PS_INPUT_CNTL_*`, where invalid offsets/default selectors can misroute attributes or feed undefined/default values into shaders.
- Render target and blend state in `CB_*` and `SX_*`, including blend equations, color write masks, base addresses, view ranges, format metadata, swizzle/resource type, FDCC compression, and extended base-address fields.
- Rasterization state in `PA_*`, `GE_*`, and `VGT_*`, including clip/viewport behavior, point and line parameters, primitive filtering, NGG limits, over-rasterization/conservative rasterization, VRS, binning, and MSAA sample positions.
- Depth/metadata state in `DB_HTILE_SURFACE` and `PA_SC_HIZ/HIS_*`, where address/size/control mismatches can corrupt metadata or cause incorrect depth/stencil visibility behavior.

The generated constants themselves are stable build artifacts; persistence risk is in consumers using the wrong field width, wrong generation, or wrong companion address header for the actual ASIC revision.

## Dependencies and Integration Points

- Depends on naming and bit layouts generated from AMD GC 12.1.0 register specifications. This header must remain synchronized with `gc_12_1_0_d.h` register offsets and other GC 12.1.0 generated headers.
- Integrated through AMDGPU graphics code under `drivers/gpu/drm/amd/amdgpu`, which uses SOC15 register helpers, golden-register tables, clear-state arrays, and command submission paths. Repository search shows related legacy/current usage patterns for `SPI_PS_INPUT_CNTL_23` clear-state entries and `PA_SC_ENHANCE_2` golden-register programming in other GFX generations.
- Connected to user-visible graphics APIs through Mesa/KFD/AMDGPU state emission: render target setup, blending, MSAA, VRS, conservative rasterization, shader scratch, and primitive/rasterizer state eventually map to these register fields.
- Uses C preprocessor constants only; no type checking is available. Consumers must pair the correct `REGISTER__FIELD__SHIFT` with the matching `REGISTER__FIELD_MASK`.

## Risks

- Bitfield drift is the primary risk. If generated masks do not match the hardware specification or the corresponding address header, register writes can silently program the wrong field.
- The chunk starts and ends inside register definitions. Documentation or automated processing must not treat this chunk as containing complete definitions for `SPI_PS_INPUT_CNTL_23` context or all of `PA_SC_ENHANCE_2`.
- Repeated indexed registers create copy/paste hazards. `CB_COLORn_*`, `CB_BLENDn_CONTROL`, and `SX_MRTn_BLEND_OPT` fields are mostly parallel; using the wrong target index can bind, blend, or compress the wrong MRT.
- Address-splitting and extended-base fields are sensitive. `SPI_GFX_SCRATCH_BASE_LO/HI`, `CB_COLORn_BASE`, and `CB_COLORn_BASE_EXT` must be composed consistently with GPU address alignment rules.
- Compression and metadata fields such as `CB_COLORn_FDCC_CONTROL`, `CB_COLORn_INFO`, `CB_MEMn_INFO`, `DB_HTILE_SURFACE`, and HiZ/HiS base/size registers have high corruption risk if mismatched with allocation layout or clear/decompress paths.
- Enhancement/workaround bits in `PA_SC_ENHANCE*` often encode hardware-specific behavior. Incorrect defaults can cause rendering hangs, missed synchronization, power regressions, or subtle rasterization differences.

## Test Signals

- Build coverage: compile AMDGPU with this generated header included; syntax errors, duplicate definitions, or missing masks surface immediately.
- Register-generation consistency: compare this header with the matching GC 12.1.0 register XML/spec generation output and with `gc_12_1_0_d.h` names for one-to-one address/mask pairing.
- Graphics conformance: Vulkan/OpenGL CTS coverage for blending, MRT color masks, MSAA sample positions, conservative rasterization, VRS, point/line rendering, clipping, and render-target formats exercises many fields in this chunk.
- Runtime smoke tests: boot a GC 12.1.0 ASIC, run display and 3D workloads, and watch for GPU hangs, VM faults, render corruption, or golden-register programming warnings.
- Debug validation: register dumps after known state emission should decode cleanly using the same masks, especially `CB_COLOR{0..7}_*`, `CB_BLEND{0..7}_CONTROL`, `PA_SC_AA_*`, `PA_SC_BINNER_*`, and `PA_SC_ENHANCE*` fields.

### subset-b-002605: lines 32569-34980

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 32569-34980

## Scope

This chunk is a large middle section of AMD's generated GC 12.1.0 shift/mask register-layout header. It contains C preprocessor constants only: no functions, structs, enums, variables, locks, allocation paths, or executable branches are introduced here. Each register field is represented by a `REGISTER__FIELD__SHIFT` macro and a matching `REGISTER__FIELD_MASK` macro.

The range starts inside `PA_SC_ENHANCE_2`: the first lines in this chunk contain the tail of that register's masks, while the corresponding register comment and early field shifts are in the previous chunk. It then covers complete or near-complete field layouts for these hardware areas:

- Pixel/scissor and primitive-binner controls: `PA_SC_ENHANCE_3`, `PA_SC_BINNER_CNTL_OVERRIDE`, `PA_SC_PBB_OVERRIDE_FLAG`, `PA_SC_DSM_CNTL`, `PA_SC_TILE_STEERING_CREST_OVERRIDE`, SC/PH FIFO sizing, packer wave-ID controls, attribute-management controls, binner event controls 0-3, binner timeout/performance controls, VRS/HiZ/HiS surface and debug controls, and SC memory scope.
- User-accessible shader queue and shader memory registers: `SQ_RUNTIME_CONFIG`, global SQ debug status, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SQ_DEBUG`, trap base/memory address registers, `SQ_IND_INDEX_USER`, `SQ_CMD_USER`, and `SQ_IND_DATA_USER`.
- PF-only SPI debug/configuration registers: CDBG enables, global wave stall/trap controls, reset debug, GDS maximum wave ID, arbiter/feature/resource-limit controls, PC config controls, and compute wavefront context-save busy status.
- PF-only UTCL1 controls: `UTCL1_CTRL_0`, invalidation-request disable, `UTCL1_CTRL_2`, FIFO sizing, GCRD target/credit controls, and `UTCL1_IDENTITY_MODE0` through `UTCL1_IDENTITY_MODE7`.
- PF-only TCP/TXA/LDS controls: TCP invalidate/status/control registers, compression and arbitration controls, TCP-UTCL0 controls/status, request-ID hash and set-hash programming, `TCP_CNTL3`, `LDS_CONFIG`, per-CU resource-reserve controls, resource-reserve enables, thrashing/retry counters, TXA controls/status/arbitration, TCP credit controls, congestion control, and TDM controls.
- Graphics-user registers: tessellation/off-chip parameters, GE position/primitive ring base and size, line stipple and screen extents, P3D/HP3D/SC trap-screen controls, thread-trace user data, SQC cache invalidation, TA CS base address, DB occlusion counters, SPI config/throttle/attribute-ring/SQG/WGS/group-launch/GOG/TCP controls.

The range ends in the middle of `SPI_TCP_CNTL`: it includes the shifts for `DEFAULT_LDS_PARTITIONS`, `MIN_LDS_PARTITIONS`, `MAX_LDS_PARTITIONS`, `IDLE_ALLOC_OPT_DIS`, `PARTIAL_DRAIN_DIS`, `LDS_PINGPONG_DIS`, and only the `DEFAULT_LDS_PARTITIONS_MASK`. The remaining `SPI_TCP_CNTL__*` masks are outside this chunk and must be merged from the next chunk for a complete per-file report.

Although this repository path is under `ceph-client`, this file is AMDGPU DRM hardware metadata for the GC 12.1.0 graphics IP block, not distributed-filesystem code.

## Purpose

`gc_12_1_0_sh_mask.h` supplies the bit-level contract used by GC 12.1.0 AMDGPU and KFD code when packing and decoding MMIO register values. The companion `gc_12_1_0_offset.h` header gives register addresses; this file gives the bit positions inside those registers. Callers normally combine these macros through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` before using SOC15 register accessors such as `RREG32_SOC15()` and `WREG32_SOC15()`.

The PA/SC/PH portion describes rasterization, primitive binning, packed-primitive behavior, VRS detail-rate handling, HiZ/HiS surface behavior, FIFO sizing, binner event inclusion, and performance-counter sampling controls. These fields influence draw batching, context-state grouping, event behavior inside binned rendering, depth/stencil hierarchical tests, clock gating, and debug overrides.

The SQ/SPI portions describe shader memory configuration, debug/trap controls, indirect user wave access, global SQ status, trap-handler base addresses, shader processor debug/stall controls, wave launch behavior, allocation/resource limits, and context-save busy state. In GC 12.1.0 consumers, nearby masks are used by `gfx_v12_1.c` and `amdgpu_amdkfd_gfx_v12_1.c` for trap enablement, KFD debug behavior, and device initialization.

The UTCL1/TCP/TXA portion describes translation-cache, texture/cache, memory-permission, XNACK, retry, hash, compression, credit, and arbitration controls. These fields are tied to shader memory access, VM translation/invalidation, atomic support, write-ack behavior, scratch/spill cache behavior, cache hashing, texture aligner behavior, and timeout/thrashing protection.

The graphics-user tail covers shader-stage ring buffers and debug-visible graphics state: tessellation factor and off-chip parameters, geometry-engine position and primitive rings, screen extents, trap-screen coordinates/counters, SQ thread-trace user-data registers, SQC cache invalidation status, TA base address, DB occlusion counters, and SPI scheduling/throttle/attribute-ring/group-launch controls.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace consumed by AMDGPU/KFD GC 12.1.0 source files that include `gc/gc_12_1_0_sh_mask.h`.

Important macro families include:

- `PA_SC_ENHANCE_2__*` tail masks for SC/BCI/SPI early wakeup, break-batch behavior, PBB timeout and reset handling, null-primitive batching, and reserved bits. This chunk does not contain the full register definition.
- `PA_SC_ENHANCE_3__*` fields for PBB workload mode, EOP packet filtering, null-primitive and z-prepass optimizations, pixel wait/sync counters, packer force-EOV behavior, VRS AA-mask handling, and SC GL1X clock-gating disables.
- `PA_SC_BINNER_CNTL_OVERRIDE__*`, `PA_SC_PBB_OVERRIDE_FLAG__*`, `PA_SC_DSM_CNTL__*`, and `PA_SC_TILE_STEERING_CREST_OVERRIDE__*` for binning mode overrides, persistent/context states per bin, FPOVs per batch, pipe/RB/SA/SE tile steering, and forced EOV resources.
- `PA_SC_FIFO_SIZE__*`, `PA_SC_IF_FIFO_SIZE__*`, `PA_PH_INTERFACE_FIFO_SIZE__*`, `PA_SC_PACKER_WAVE_ID_CNTL__*`, `PA_SC_ATM_CNTL__*`, and `PA_SC_PKR_WAVE_TABLE_CNTL__*` for internal primitive/tile/interface FIFO depths, packer wave limits, attribute limits, and fine/coarse clock-gating controls.
- `PA_SC_BINNER_EVENT_CNTL_0..3__*` for how events such as streamout stats sampling, cache flushes, partial flushes, context-done, wait-sync, perf counter start/stop/sample, pipeline stat start/stop/sample, streamout flush, break-batch, and debug/trap events interact with binning.
- `PA_SC_BINNER_TIMEOUT_COUNTER__*` and `PA_SC_BINNER_PERF_CNTL_0..3__*` for timeout and performance histogram thresholds.
- `PA_SC_P3D_TRAP_SCREEN_HV_LOCK`, `PA_SC_HP3D_TRAP_SCREEN_HV_LOCK`, `PA_SC_TRAP_SCREEN_HV_LOCK`, and later matching `*_HV_EN`, `*_H`, `*_V`, `*_OCCURRENCE`, and `*_COUNT` fields for trap-screen write protection, enablement, coordinates, occurrence limits, and counters.
- `PA_SC_VRS_SURFACE_CNTL_1__*`, `PA_SC_HIZ_SURFACE_CNTL__*`, `PA_SC_HIS_SURFACE_CNTL__*`, `PA_SC_HIZ_DEBUG__*`, `PA_SC_HIS_DEBUG__*`, and `SC_MEM_SCOPE__*` for VRS rate/debug behavior, hierarchical Z/stencil cache flush/filter/prefetch/debug behavior, and surface memory scopes.
- `SQ_RUNTIME_CONFIG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, and `SQ_DEBUG` for SQ runtime/debug state and shader memory address/alignment/prefetch/retry controls. `gfx_v12_1.c` defines `DEFAULT_SH_MEM_CONFIG` from `SH_MEM_CONFIG__ADDRESS_MODE__SHIFT`, `SH_MEM_CONFIG__ALIGNMENT_MODE__SHIFT`, and `SH_MEM_CONFIG__INITIAL_INST_PREFETCH__SHIFT`.
- `SQ_SHADER_TBA_LO/HI` and `SQ_SHADER_TMA_LO/HI` for trap-handler base and memory addresses, including the `SQ_SHADER_TBA_HI__TRAP_EN` bit.
- `SQ_IND_INDEX_USER`, `SQ_CMD_USER`, and `SQ_IND_DATA_USER` for user indirect SQ access: wave/workitem selection, auto-increment, command mode, VMID/queue targeting, and data transfer.
- `SPI_CDBG_SYS_GFX`, `SPI_CDBG_SYS_HP3D`, `SPI_CDBG_SYS_CS0`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, `SPI_GDBG_WAVE_CNTL3`, and `SPI_RESET_DEBUG` for shader-pipe debug enables, global wave stalls, trap routing, per-stage wave stalls, and reset-status snapshots.
- `GDS_COMPUTE_MAX_WAVE_ID`, `SPI_ARB_CNTL_0`, `SPI_FEATURE_CTRL`, `SPI_SHADER_RSRC_LIMIT_CTRL`, `PC_CONFIG_CNTL_0/1`, and `SPI_COMPUTE_WF_CTX_SAVE_STATUS` for compute wave limits, SPI arbitration/features/resource limits, primitive/PC configuration, and per-pipe/per-queue context-save busy bits.
- `UTCL1_CTRL_0`, `UTCL1_UTCL0_INVREQ_DISABLE`, `UTCL1_CTRL_2`, `UTCL1_FIFO_SIZING`, `GCRD_SA0_TARGETS_DISABLE`, `GCRD_SA1_TARGETS_DISABLE`, `GCRD_CREDIT_SAFE`, and `UTCL1_IDENTITY_MODE0..7` for UTCL1 invalidation, duplicate detection, translation fault locking, range invalidation, credits, target disablement, and identity-mode return attributes such as snoop, fragment size, permissions, XNACK, PTE TMZ/no-PTE, SPA, IOSTEER, memory type, dirty/prefetch/TEE/HDM flags.
- `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CNTL2`, `TCP_CREDIT`, `TCP_DEBUG_DATA`, `TCP_COMPRESSION_CNTL`, `TCP_ARB`, `TCP_UTCL0_CNTL1`, `TCP_UTCL0_CNTL2`, and `TCP_UTCL0_STATUS` for texture/cache invalidation, busy/status reporting, cache behavior, compression overrides, atomic/permission response behavior, invalidation toggles, XNACK/retry/protection status, and fine/coarse clock gating. `gfx_v12_1.c` uses `TCP_UTCL0_CNTL1__ATOMIC_REQUESTER_EN`, `TCP_CNTL3__DISABLE_EARLY_WRITE_ACK`, and `TCP_CNTL__TCP_SPILL_CACHE_DISABLE` through `REG_SET_FIELD()`.
- `TCP_RQID_HASH_CNTL`, `TCP_SET_HASH_CFG`, and `TCP_SET_HASH_MASK_*` for request-ID/set hash programming across 64, 128, 192, 256, 320, 384, and 448-entry mask families.
- `TCP_CNTL3`, `LDS_CONFIG`, `SPI_RESOURCE_RESERVE_CU_0..15`, and `SPI_RESOURCE_RESERVE_EN_CU_0..15` for TCP priority/coalescing/write-ack behavior, LDS configuration, and per-CU VGPR/SGPR/LDS/wave/barrier reserve settings plus enable/type/queue masks.
- `TCP_UTCL0_THRASHING_CTRL`, retry threshold counters, `TCP_UTCL0_XNACK_RETRY`, retry timer thresholds, `TXA_CNTL`, `TXA_CNTL_AUX`, `TXA_CNTL2`, `TXA_STATUS`, `TXA_TDM_ARB_CNTL`, `TCP_CREDIT2`, `VC_CONGESTION_CONTROL`, and `TXA_TDM_CNTL` for VM thrash/retry protection, XNACK retry accounting, texture aligner credits, determinism disables, busy status, TDM arbitration, and congestion limits.
- `VGT_TF_RING_SIZE`, `VGT_HS_OFFCHIP_PARAM`, `GE_POS_RING_BASE/SIZE`, and `GE_PRIM_RING_BASE/SIZE` for tessellation/off-chip and graphics-engine position/primitive ring configuration.
- `PA_SU_LINE_STIPPLE_VALUE`, `PA_SC_LINE_STIPPLE_STATE`, `PA_SC_SCREEN_EXTENT_MIN/MAX_0/1`, and the P3D/HP3D/SC trap-screen field families for draw-state, screen-region, and trap-screen programming.
- `SQ_THREAD_TRACE_USERDATA_0..7`, `SQC_CACHES`, `TA_CS_BC_BASE_ADDR`, `TA_CS_BC_BASE_ADDR_HI`, and `DB_OCCLUSION_COUNT0..3_LOW/HI` for thread-trace annotations, SQC cache invalidate/complete bits, texture-address base, and 63-bit occlusion query counters.
- `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, `SPI_GS_THROTTLE_CNTL1/2`, `SPI_ATTRIBUTE_RING_BASE/SIZE`, `SPI_SQG_EVENT_CTL`, `SPI_COMPUTE_WGS_CONTROL`, `SPI_GRP_LAUNCH_GUARANTEE_ENABLE/CTRL`, `SPI_GOG_ALLOCATION_CTRL`, and the partial `SPI_TCP_CNTL` definition for SPI scheduling, context-save timing, throttling, attribute-ring memory, SQG events, WGS, launch guarantees, allocation retry/timeout, and TCP/LDS partition behavior.

Representative direct consumers in this repository include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c`, which includes this header, builds `DEFAULT_SH_MEM_CONFIG` from `SH_MEM_CONFIG` fields, enables TCP atomics with `TCP_UTCL0_CNTL1`, disables early write ACK with `TCP_CNTL3`, disables TCP spill cache with `TCP_CNTL`, and enables per-VMID debug traps using SPI debug fields outside but adjacent to this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, which includes this header and maps KFD debug trap masks through GC 12.1 SPI debug-control fields, using the same generated-mask contract as the SQ/SPI debug families in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.c`, `imu_v12_1.c`, `gfxhub_v12_1.c`, `sdma_v7_1.c`, `soc_v1_0.c`, and KFD queue/MQD files, which include the GC 12.1.0 generated register headers and rely on offset/mask consistency for low-level register programming.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime pattern for fields in this chunk is:

1. GC 12.1.0 initialization or a debug/performance path selects the target GC instance/XCC, often through `GET_INST(GC, xcc_id)` and SOC15 register helpers.
2. The driver reads or initializes a 32-bit register value.
3. It uses `REG_SET_FIELD()` with one of these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pairs to pack a field value, or uses `REG_GET_FIELD()` to decode a readback value.
4. It writes the packed value to the register offset from `gc_12_1_0_offset.h` or interprets the readback as a status/debug snapshot.

For GC 12.1 golden-register setup, `gfx_v12_1_init_golden_registers()` iterates over active XCCs. It calls helper functions that read `regTCP_UTCL0_CNTL1`, set `ATOMIC_REQUESTER_EN`, read `regTCP_CNTL3`, set `DISABLE_EARLY_WRITE_ACK`, read `regTCP_CNTL`, set `TCP_SPILL_CACHE_DISABLE`, and write the values back. Those runtime branches live in `gfx_v12_1.c`; this chunk only defines the bit locations used by the field helpers.

For KFD and debug flows, consumers program SPI/SQ debug registers to enable traps, stall wave launch, map software exception masks to hardware exception fields, and issue SQ commands. The `SQ_IND_INDEX_USER`, `SQ_CMD_USER`, `SQ_IND_DATA_USER`, `SPI_GDBG_WAVE_CNTL`, `SPI_GDBG_TRAP_CONFIG`, and `SPI_GDBG_WAVE_CNTL3` field definitions describe the user/privileged debug transport and stall/trap surfaces; the actual command sequencing and synchronization live in AMDGPU/KFD code.

For rasterization and binning, state setup or generated clearstate packets can write PA/SC/PH controls before or during graphics pipeline initialization. Runtime draw submission then depends on those programmed binner, FIFO, VRS, HiZ/HiS, and screen/trap-state registers while hardware processes primitives, events, and depth/stencil tests.

For memory/cache behavior, TCP/UTCL1/TXA/SQC fields are used when the driver changes cache-invalidation, atomics, translation, retry, XNACK, compression, hashing, spill, and write-ack policies. Some fields are configuration state written during initialization; others are trigger/status fields such as `TCP_INVALIDATE__START`, `TCP_STATUS__*`, `TCP_UTCL0_STATUS__*`, `TXA_STATUS__*`, or `SQC_CACHES__COMPLETE`.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe hardware register state owned by the GPU and programmed by AMDGPU/KFD.

PA/SC/PH fields generally persist as graphics pipeline configuration until rewritten, reset, or restored from context state. Binning mode, FIFO sizing, VRS surface behavior, HiZ/HiS controls, event inclusion, and clock-gating overrides can affect many draws after a single write. Incorrect masks here can cause overbroad or underbroad binning, missed synchronization events, depth/stencil culling errors, invalid VRS rate handling, or performance regressions that appear workload-dependent.

SQ/SPI debug and trap fields are live hardware debug state. Trap-handler base addresses, trap enable bits, wave-stall controls, SQ command fields, and indirect user data affect trap/debug behavior for selected waves, queues, VMIDs, or shader stages. Readback status such as `SQ_DEBUG_STS_GLOBAL` or `SPI_COMPUTE_WF_CTX_SAVE_STATUS` is volatile and should be treated as a snapshot unless the caller has quiesced the relevant engine.

Shader memory configuration fields such as `SH_MEM_BASES` and `SH_MEM_CONFIG` persist as shader-visible memory mode state. Wrong address mode, alignment mode, prefetch, retry, or base packing can break shader memory semantics across graphics and compute workloads.

UTCL1/TCP/TXA fields include both persistent policy and transient status. Translation-cache duplicate detection, invalidation filtering, identity-mode return attributes, TCP compression, hash masks, credits, atomic enablement, early-write-ack behavior, XNACK/retry, thrashing thresholds, and TXA determinism controls remain in force until changed. Status and counter fields such as TCP busy bits, UTCL0 fault/retry/PRT/timeout detection, retry counters, TXA busy bits, and SQC cache complete bits are hardware-updated observations.

Resource reservation fields for `SPI_RESOURCE_RESERVE_CU_0..15` and `SPI_RESOURCE_RESERVE_EN_CU_0..15` persist per CU/resource slot and can change how VGPR, SGPR, LDS, wave, barrier, type, and queue resources are reserved. Bad packing can reduce occupancy, starve queues, or create fairness/performance bugs.

Graphics-user ring, screen, trace, cache, TA, DB, and SPI fields persist as graphics pipeline or debug/performance configuration. GE ring base/size fields describe memory-backed hardware buffers; thread-trace user-data fields become diagnostic annotations; DB occlusion counters are hardware-updated query results split into low and high halves; SPI attribute-ring fields describe memory size and cache policy for shader interpolation/attribute storage.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register family being used consistently:

- `gc_12_1_0_offset.h` supplies the matching `reg...`, `mm...`, and `ix...` register offsets. This chunk supplies only field shifts and masks.
- `soc24_enum.h` supplies enum values used by GC 12.1.0 code for register fields and packet definitions.
- AMDGPU SOC15 helpers and common register helpers provide `RREG32_SOC15()`, `WREG32_SOC15()`, `SOC15_REG_OFFSET()`, `REG_SET_FIELD()`, and `REG_GET_FIELD()`.
- `gfx_v12_1.c` integrates `SH_MEM_CONFIG`, TCP, and SPI/SQ generated masks with initialization, ring setup, debug trap enablement, golden-register programming, and XCC selection.
- `amdgpu_amdkfd_gfx_v12_1.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c` integrate the same generated mask header with KFD queue setup and debugger/trap behavior.
- `mes_v12_1.c` and `imu_v12_1.c` include the generated GC 12.1.0 headers for micro-engine and initialization behavior; they rely on the header set being synchronized even when they do not use every field in this specific chunk.
- Clearstate and packet-generation paths can program PA/SC/SPI/GE/DB state via packet streams rather than direct MMIO. The field definitions still describe the hardware layout used when code needs to pack or decode those registers.

The chunk is intentionally low level. It does not decide which binner settings are selected for a workload, when to enable KFD traps, which cache policy is correct for a buffer, when to invalidate TCP/SQC caches, or how performance/debug data is surfaced to user space. Those policies live in AMDGPU, KFD, Mesa/userspace command streams, firmware, and hardware initialization data.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong numeric shift or mask compiles cleanly but programs or decodes the wrong hardware bits.
- The range is not register-aligned at either end. `PA_SC_ENHANCE_2` is incomplete at the start, and `SPI_TCP_CNTL` is incomplete at the end. Whole-file research must merge adjacent chunks before making complete claims about those registers.
- Many fields are single-bit disables or overrides. Inverting the meaning in documentation or code review is easy: names such as `DISABLE_*`, `FORCE_*`, `*_OVERRIDE`, and `*_NOFILL` require careful reading at each call site.
- PA/SC binner event controls use many 2-bit fields for event treatment. Mixing event fields or treating them as booleans can make binned rendering miss flushes, break batches unnecessarily, or include the wrong synchronization events.
- FIFO, wave-limit, credit, timeout, and threshold fields directly affect hardware flow control. Incorrect masks can create hangs, underutilization, starvation, or workload-specific performance cliffs.
- VRS, HiZ, and HiS fields affect visible rendering correctness. Wrong mask usage can change shading rate, depth/stencil culling, flush behavior, or prefetch behavior without an obvious kernel error.
- SQ/SPI debug fields are security- and stability-sensitive because they affect trap routing, wave stalls, user indirect access, and per-VMID/queue debug behavior. Incorrect field layout can stall unrelated workloads or leak misleading debug state.
- Shader memory fields affect address mode, alignment, prefetch, retry, private/shared bases, and trap addresses. A bad mask can break shader memory semantics across many queues.
- UTCL1 identity-mode fields encode permission, XNACK, TMZ, no-PTE, SPA, IOSTEER, MTYPE, dirty, prefetch, TEE, and HDM return attributes. Cross-generation reuse or partial packing errors can compromise fault behavior or memory isolation.
- TCP/TXA controls include atomic enablement, compression bypass/disable, write-combining, early write ACK, illegal PCIe atomic handling, XNACK retry, and deterministic behavior. These are not cosmetic performance bits; wrong values can change correctness and coherency.
- `TCP_SET_HASH_MASK_*` families are repetitive. A generation or copy/paste error in a single set size can affect only certain cache hash geometries, making failures hard to reproduce.
- Per-CU resource reservation fields repeat for 16 CUs and include matching enable registers. Array-like programming must keep data and enable registers aligned by CU index.
- DB occlusion counters are split into low and high registers with a 31-bit high mask. Readback consumers must handle split-counter consistency and rollover.
- Thread-trace user-data registers are full-width data fields; they are easy to treat as harmless, but they affect diagnostic correlation and trace interpretation.
- Cross-generation names are reused heavily. GC 12.1.0 masks must be paired with GC 12.1.0 offsets and not borrowed from GC 12.0.0, GC 11, GC 10, or GCA headers even when macro names match.

## Test Signals

Useful validation combines generated-data checks, build coverage, and hardware/runtime behavior:

- Build AMDGPU and KFD with GC 12.1.0 support enabled. This catches missing or renamed macros in `gfx_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `mes_v12_1.c`, `imu_v12_1.c`, `gfxhub_v12_1.c`, `sdma_v7_1.c`, `soc_v1_0.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c`.
- Mechanically compare this chunk against AMD's authoritative GC 12.1.0 register database, focusing on repeated families such as `PA_SC_BINNER_EVENT_CNTL_*`, `UTCL1_IDENTITY_MODE*`, `TCP_SET_HASH_MASK_*`, `SPI_RESOURCE_RESERVE_CU_*`, and `SPI_RESOURCE_RESERVE_EN_CU_*`.
- Verify that `gc_12_1_0_offset.h` and `gc_12_1_0_sh_mask.h` come from the same generated source revision. Offset/mask mismatches are especially dangerous for TCP/UTCL1, SQ/SPI debug, GE ring, SQC cache, and PA/SC binner controls.
- Exercise GC 12.1 initialization on hardware and confirm that golden-register writes for `TCP_UTCL0_CNTL1`, `TCP_CNTL3`, and `TCP_CNTL` apply the expected fields: atomics enabled, early write ACK disabled when intended, and TCP spill cache disabled when intended.
- Run graphics workloads that stress primitive binning, streamout, partial flushes, pipeline stats, perf counter start/stop/sample events, VRS, HiZ, HiS, line stipple, screen extents, and occlusion queries. Regressions may show as rendering corruption, missed occlusion counts, hangs, or large performance shifts.
- Run KFD debugger/trap tests on GC 12.1 hardware. Healthy signals include correct trap-on-start/trap-on-end behavior, correct exception-mask mapping, no unrelated VMID stalls, and sane wave launch mode behavior.
- Exercise shader memory configuration and trap-handler paths, including private/shared memory bases, retry behavior, trap address programming, and indirect SQ user access where supported.
- Exercise VM invalidation, atomics, XNACK/retry, and translation-fault workloads that stress UTCL1/TCP fields. Expected signals include correct fault attribution, no illegal stale translations, no retry storms, and correct atomic behavior.
- Test TCP cache behavior with workloads sensitive to compression, write-combining, spill cache, hash-set selection, and early write acknowledgement. Incorrect masks often appear as data corruption, intermittent shader faults, or performance cliffs rather than compile errors.
- Validate SQ thread trace and SQC cache invalidate flows. Thread traces should carry expected user-data values, and SQC invalidate sequences should observe the `COMPLETE` status as expected.
- Read DB occlusion counter low/high pairs under controlled query workloads and verify monotonic, plausible counter values with correct high-half masking.
- Run suspend/resume, GPU reset, and queue preemption tests with active graphics and compute workloads. SPI context-save status, TCP/UTCL1 state, and PA/SC state should recover without persistent stalls or corrupted rendering.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002605`. It covers lines 32569-34980 of `gc_12_1_0_sh_mask.h`. The previous chunk contains the beginning of `PA_SC_ENHANCE_2`; this chunk starts at that register's tail masks. The next chunk must provide the remaining `SPI_TCP_CNTL__*` masks after `DEFAULT_LDS_PARTITIONS_MASK`. The final per-file research document should merge these adjacent chunks to present complete register definitions and avoid treating the boundary partials as whole-register coverage.

### subset-b-002606: lines 34981-37627

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 34981-37627

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It defines preprocessor constants only: each hardware register field is represented by a `__SHIFT` macro and a matching `_MASK` macro for composing or decoding 32-bit MMIO register values. There are no C functions, structs, enums, global variables, branches, allocations, locks, callbacks, or direct persistence logic in this range.

The selected lines start in the middle of `SPI_TCP_CNTL`, so this document sees only the final masks for `MIN_LDS_PARTITIONS`, `MAX_LDS_PARTITIONS`, `IDLE_ALLOC_OPT_DIS`, `PARTIAL_DRAIN_DIS`, and `LDS_PINGPONG_DIS`; their shifts and the `DEFAULT_LDS_PARTITIONS` mask are immediately before the chunk boundary. The main covered address blocks are:

- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_comp_wgsdec`: WGS compute-dispatch register fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_wgsdec`: WGS controller, microcontroller, interrupt, status, scratch, metadata, and timer fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_gl1dec`: GL1/GL1X arbitration, credit, compression, UTCL0, control, and status fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_pfonly_secacdec`: shader-engine CAC and DIDT/EDC power-throttling fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_perfddec`: performance-counter data registers for GE2, GRBMH, PA, SPI, PC, SQ/SQG, SX, TA/TD/TCP, GL1, CB/DB, RMI, UTCL1, WGS, and related blocks.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_perfsdec`: performance-counter selector registers through `PA_SU_PERFCOUNTER1_SELECT`; the final line is only the `PA_SU_PERFCOUNTER1_SELECT1` register comment, with that register's fields in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.1 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_1_0_sh_mask.h` supplies the bit-level ABI between GC 12.1.0 hardware registers and AMDGPU/KFD driver code. Runtime code combines these masks with register addresses from `gc_12_1_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_FIELD15`, and `SOC15_REG_OFFSET`. This chunk describes WGS compute launch state, WGS microcontroller/debug state, GL1 cache/client arbitration, shader-engine power telemetry/throttling, and performance-monitor data and selector layouts.

The WGS compute-dispatch block defines fields for a hardware-driven compute dispatch path. It covers dispatch initiation flags such as compute-shader enable, partial thread-group enable, ordered append, ordering mode, scalar/vector L1 invalidation, ping-pong, tunnel, restore, wave32, AMP shader, display preemption disable, 2D interleave, WGS dispatch, and TTRACE queue id. It then defines grid dimensions, start and restart coordinates, per-axis full and partial thread counts, pipeline-stat and perfcount enables, program and dispatch-packet addresses, scratch base addresses, VMID, resource limits, per-SE CU destinations and static thread-management masks, temporary ring sizing, thread trace, dispatch and threadgroup ids, request controls, user accumulators, resource words, DDID index, shader checksum, dispatch interleave, relaunch controls, wave-restore address, prescaled dimensions, 16 user-data registers, dispatch tunnel/end sentinels, and a `NOWHERE` sink register.

The WGS controller block supplies fields for the WGS engine around interrupt reporting, endianness, generated base addresses, clock control, ME1 microcode address/data/checksum, suspend/resume context-save addresses and sizes, OS pipe exposure, DDID base/control, RS64 program counter and interrupt state, machine trap vector and interrupt-enable/pending registers, data/instruction cache base/bound/control windows, general-purpose registers, local data/instruction/scratch apertures, RS64 perfcount/exception state, ME1 pipe priority, IQ wait timers, microcode version, busy/stall/status surfaces, scratch index/data, latency-stat windows, TC perf-counter window selection, data registers, metadata base/control, IQ timer messages, and RS64 thread controls.

The GL1 block describes the shader-engine local cache and associated arbitration path. It covers GL1 and GL1X memory-pipe count, fine-grain clock-gating override, performance-counter enable override, arbitration status, DRAM burst masks and burst control, repeater clock-gating overrides, GL1A-to-GL1C and GL1XA-to-GL1XC credits, client-free delays, client-type compression overrides, compressor format overrides, GL1C/GL1XC control and status registers, UTCL0 controls/status/retry state, and secondary control fields.

The SE CAC/DIDT block describes shader-engine current/power estimation and throttling controls. It includes CAC controls, soft controls, override values, window aggregate values and cycle counters, DIDT EDC control/throttle/threshold/stretch/counter/stall/status/overflow/power-delta fields, per-block CAC weights for LDS, TCP, SQ, SP, SQC, CU, UTCL1, GL1C, and SPI, plus the indexed `SE_CAC_IND_INDEX` and `SE_CAC_IND_DATA` access registers.

The performance data/select blocks define the low/high counter storage and selector programming for many graphics sub-blocks. Most counter-data registers expose either a full 32-bit low value or a 16-bit high value. Selector registers commonly expose 10-bit event selector fields, a 4-bit counter mode, and high-nibble performance mode fields. Specialized selector forms include GRBMH user-defined busy/clean masks for many sub-blocks and TCP filter/filter-enable fields for cache operation, opcode, swizzle, data/number format, sample count, address mode, GLC/SLC, and compression attributes.

## Important APIs, Types, and Macros

This chunk defines no callable APIs or C types. Its API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register comments such as `//WGS_COMPUTE_PGM_RSRC1` and address-block comments preserve generated hardware grouping.
- Companion address symbols are in `gc_12_1_0_offset.h`, for example `regWGS_COMPUTE_DISPATCH_INITIATOR`, `regWGS_STATUS`, `regGL1_DRAM_BURST_CTRL`, `regSE_CAC_IND_INDEX`, `regTCP_PERFCOUNTER_FILTER`, and `regPA_SU_PERFCOUNTER0_SELECT`.

Observed GC 12.1 consumers include `gfx_v12_1.c`, `mes_v12_1.c`, `sdma_v7_1.c`, `gfxhub_v12_1.c`, `imu_v12_1.c`, `soc_v1_0.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c`, all of which include the GC 12.1 offset and/or mask headers. The specific names in this chunk are mostly consumed by MMIO helpers, register-dump/profiling paths, power/clock/debug plumbing, and packet or firmware initialization flows rather than by a single local algorithm.

Two integration points are visible outside the generated headers. `soc15.c` provides locked indexed accessors for `SE_CAC_IND_INDEX` and `SE_CAC_IND_DATA`, so the final SE CAC registers in this chunk are part of the generic shader-engine CAC indirect access path. `gfx_v12_1.c` writes `regGL1_DRAM_BURST_CTRL` during GC 12.1 setup, so GL1 control fields in this chunk are runtime-relevant even when written as whole-register values rather than through `REG_SET_FIELD`.

## Control Flow

There is no executable control flow in this header. Control flow exists in consumers that compose register values, write MMIO registers, poll status bits, or decode register dumps using these constants.

The WGS compute path is a programmed-state flow: software or firmware writes program address, packet address, scratch address, program resource words, VMID, grid dimensions, thread counts, CU routing, user data, and related controls before asserting dispatch/initiation fields. Restart, relaunch, wave-restore, tunnel, dispatch-end, and status fields are then used by the hardware/firmware path to manage progress, recover waves, or report diagnostics.

The WGS controller path is a firmware/microcontroller flow. Microcode address/data/checksum registers support loading or inspecting WGS/ME1 firmware state; RS64 program counter, interrupt, cache base/bound/control, local aperture, timer, and scratch/data windows support initialization and debug. Busy, stalled, status, error, interrupt, and pending-interrupt fields are read or polled by diagnostics and recovery paths.

The GL1 path is a configuration/status flow. Driver setup or firmware can tune arbitration, burst policy, credits, client-free delay, compression overrides, UTCL0 behavior, and clock-gating overrides, then status registers expose stalls, FIFO pressure, request/data credits, retry state, translation activity, and other cache-front-end health signals.

The SE CAC/DIDT path uses both direct registers and indexed registers. Generic `soc15_se_cac_rreg()` and `soc15_se_cac_wreg()` serialize indexed accesses with `adev->reg.se_cac.lock`, write `SE_CAC_IND_INDEX`, then read or write `SE_CAC_IND_DATA`. DIDT/EDC fields are configuration/status surfaces for power throttling and error-detection controls; CAC weight registers feed shader-engine power/current estimation.

The performance-monitor path is a select, sample, read flow. Selector registers choose event ids, packing/modes, filters, and user-defined busy masks; counter data registers then expose low/high portions of sampled counts. GC clock-gating code in `gfx_v12_1.c` also toggles performance-monitor clock state through RLC controls outside this chunk, which is an enabling condition for reliable performance-counter sampling.

## State and Persistence

The macros themselves are compile-time constants and have no state. The hardware registers they describe are volatile MMIO state owned by the GC 12.1 graphics engine, shader engines, WGS firmware, cache blocks, power-management logic, and performance monitor hardware.

Some described register state is persistent across a running queue or dispatch. WGS program address, dispatch-packet address, scratch base, resource words, VMID, dimensions, user-data registers, static thread-management masks, destination CU masks, metadata base/control, cache apertures, and GL1 arbitration/credit/compression settings remain meaningful until reprogrammed, reset, or overwritten by firmware.

Other state is transient, sticky, or command-like. Dispatch initiator bits, relaunch controls, cache invalidate/prime controls, IQ timer active/rearm bits, interrupt status/pending bits, error latches, busy/stalled/status bits, latency-stat clear/enable bits, EDC overflow/status, and performance-counter values can change as hardware runs. Consumers must use the sequencing, polling, and timeout rules in the owning driver/firmware code because this header only describes bit positions.

SE CAC indirect accesses have software serialization in `soc15.c`. The index/data pair is shared hardware state, so callers must use the locked helper path or equivalent serialization to avoid racing an index write against another reader/writer.

## Dependencies and Integration Points

The immediate dependency is the generated GC 12.1 offset header, `gc_12_1_0_offset.h`, which supplies the register addresses corresponding to this chunk's field layouts. Unlike several older generated GC header sets in this tree, no `gc_12_1_0_default.h` file is present; GC 12.1 code uses explicit defaults in local source where needed and, in `mes_v12_1.c`, includes `gc_11_0_0_default.h` for shared default values.

Runtime integration points include:

- GC 12.1 graphics bring-up in `gfx_v12_1.c`, which includes this mask header, programs GL1/TCP/RLC/CP registers, initializes MEC/RLC firmware, controls clock gating, sets up queues, and reads status.
- MES bring-up in `mes_v12_1.c`, which includes the same generated headers and programs firmware, queues, doorbells, HQD/MQD state, and cache controls.
- KFD queue and debug paths in `amdgpu_amdkfd_gfx_v12_1.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c`, which rely on the same register macro contract for queue/debug register state.
- Generic SOC15 CAC access in `soc15.c`, whose `SE_CAC_IND_INDEX`/`SE_CAC_IND_DATA` accessors are the software integration point for the final SE CAC indexed registers.
- Performance tooling and debug/register-dump paths, which depend on counter-data, selector, TCP filter, WGS status, GL1 status, and GRBMH busy-mask fields to produce meaningful diagnostics.
- Power-management and throttling flows, where SE CAC weights, DIDT/EDC thresholds, throttle controls, rolling/average power deltas, and CAC aggregate windows connect shader-engine activity to power/current management policy.

The generated names also align with `soc24_enum.h`, which provides event selector enumerations for GC 12-era performance counters such as GL1C and GL1XC. Event enums identify what to count; this chunk identifies where those event ids and modes are encoded in hardware registers.

## Risks

The primary risk is silent hardware misprogramming. A wrong shift or mask usually still compiles, but it can write the wrong bit, truncate an address, enable a reserved mode, decode a stale status bit as current, or select the wrong performance event.

WGS compute fields are high risk because they describe dispatch launch state. Incorrect program address high/low masks, scratch base masks, VMID, resource words, user-data fields, thread counts, CU masks, dispatch initiator bits, or relaunch/restore controls can cause bad shader execution, lost dispatches, privilege issues, invalid memory accesses, or hangs during recovery.

WGS controller fields are high risk for firmware and diagnostics. Bad microcode address/data/checksum fields, RS64 cache controls, program-counter fields, interrupt/pending/error masks, local aperture fields, metadata controls, timer fields, or thread-control bits can break firmware bring-up, interrupt attribution, debug capture, or reset handling.

GL1 and GL1X fields are sensitive for memory correctness and performance. Arbitration, credit, burst, compression override, UTCL0, retry, and status fields affect cache traffic, translation behavior, and stall diagnosis. Wrong masks can produce subtle data-path corruption, severe performance cliffs, or misleading fault/stall reports.

SE CAC/DIDT fields are power-policy sensitive. Incorrect weight, threshold, throttle, stretch, rolling/average delta, override, or overflow fields can make power/current estimation inaccurate, trigger unnecessary throttling, or fail to throttle under high-current conditions. Indexed SE CAC access is also race-prone if the index/data pair is touched without proper locking.

Performance-counter fields are mechanically repetitive and easy to corrupt during generation or manual edits. Similar register families differ in high/low width, selector field names (`PERF_SEL`, `PERF_SEL0`, `PERF_SEL1`), mode packing, filter availability, and user-defined busy masks. Counter code may appear to work while silently sampling the wrong event or applying the wrong filter.

The chunk boundaries are themselves a reconciliation risk. It starts after the first `SPI_TCP_CNTL` field definitions and ends before `PA_SU_PERFCOUNTER1_SELECT1` fields. A merged per-file report must connect those partial registers with adjacent chunks.

## Test Signals

Useful compile-time signals are successful builds of GC 12.1 AMDGPU, MES, SDMA, GFXHUB, IMU, SOC, and KFD paths that include `gc_12_1_0_sh_mask.h`. Missing or renamed macros are normally caught by compilation, while wrong numeric values require hardware or register-level validation.

Graphics and compute bring-up signals include successful probe of GC 12.1 ASICs, MEC/RLC/MES firmware load, queue initialization, KIQ/MES ring tests, KFD queue creation, dispatch completion, suspend/resume, and GPU reset recovery. WGS-specific confidence would come from workloads that exercise work-graph or WGS dispatch paths, relaunch/restore behavior, thread trace, VMID isolation, scratch use, and user-data/resource programming.

GL1 signals include stable shader memory workloads, no unexpected VM/XNACK or cache retry storms, correct GL1/GL1X status under stress, no regressions from `regGL1_DRAM_BURST_CTRL` setup, and sane cache/performance behavior when compression, burst, credit, and arbitration settings are active.

SE CAC/DIDT validation should cover indexed `SE_CAC_IND_INDEX`/`SE_CAC_IND_DATA` reads and writes through the locked SOC15 helpers, power/thermal stress workloads, EDC threshold and overflow reporting, throttle activation/deactivation, CAC aggregate windows, and sane rolling/average power delta values.

Performance-monitor validation should program GE2, GRBMH, PA, SPI, PC, SQ/SQG, SX, TA/TD/TCP, GL1, CB/DB, RMI, UTCL1, and WGS counters with known event selectors; verify low/high counter reads; exercise TCP filters; verify GRBMH user-defined busy masks; and ensure performance-monitor clock gating does not leave counters frozen or returning implausible values.

Diagnostic signals include coherent register dumps for `WGS_STATUS`, `WGS_BUSY_STAT`, `WGS_STALLED_STAT1`, `WGS_BUSY_STAT2`, `GL1C_STATUS`, `GL1XC_STATUS`, `GL1XC_UTCL0_STATUS`, `DIDT_EDC_STATUS`, `DIDT_EDC_OVERFLOW`, `WGS_PERFMON_CNTL`, counter low/high registers, and selector registers after representative compute, graphics, memory, and power workloads.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002606`. It covers lines 34981-37627 of `gc_12_1_0_sh_mask.h`. The final per-file report should merge this with the preceding chunk for the full `SPI_TCP_CNTL` context and with the following chunk for `PA_SU_PERFCOUNTER1_SELECT1` and later performance selector definitions.

### subset-b-002607: lines 37628-40016

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 37628-40016

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask header slice. It contains 2,168 `#define` constants for register bit positions and bit masks, plus register-name comments that group those constants. There are no functions, structs, enums, variables, locks, allocation paths, or executable statements in these lines.

The slice starts in the middle of the performance-counter selection area, at `PA_SU_PERFCOUNTER2_SELECT`, and ends in the middle of `CGTT_PH_CLK_CTRL3`. The next chunk must provide the remaining `CGTT_PH_CLK_CTRL3` masks and any following registers before a full per-file report can make complete claims about the tail of the clock-control block.

Major register groups covered here are:

- Performance counter selectors for PA/SU, PA/SC, SPI, PC, SQ, SQG, SX, TA, TD, TCP, GL1C, GL1XC, CB, DB, RMI, PA/PH, UTCL1, WGS, GL1A, and GL1XA blocks.
- SQ and SQG performance-counter control fields, including shader-stage enables, pipe disables, force enable, VMID filtering, poll-before-read, and sample-finish status fields.
- SQ thread trace buffer, control, mask, token-mask, write-pointer, halt, poweroff-restore, status, draw/marker/dropped counters, and finish-done debug fields.
- The beginning of the `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_pwrdec` address block, covering fine-grained clock-gating and clock-trunk controls for SPI, PC, BCI, VGT, GS/NGG, PA, SQ, SQG, SX, TA, TD, DB, CB, RMI, SE CAC, and PH.

## Purpose

The purpose of this chunk is to publish ASIC-specific bit layouts for GC 12.1.0 graphics registers. Companion offset headers define the register addresses; this `*_sh_mask.h` file defines how software packs field values into those 32-bit registers and how it extracts fields from readbacks.

The performance-counter selectors let the driver or profiling stack choose hardware events and counter modes. The common selector pattern is:

- `PERF_SEL`, often plus `PERF_SEL1`, `PERF_SEL2`, or `PERF_SEL3`, for one or more event selector slots.
- `CNTR_MODE`, `COUNTER_MODE`, `SPM_MODE`, or `PERF_MODE` fields for counter behavior and streaming-performance-monitoring mode.
- `*_SELECT1` companion registers that carry extra selector lanes or mode fields.

The SQ thread-trace fields configure shader execution tracing. They describe trace buffer size/base registers, double-buffering, high-water and low-water control, interrupt generation, stall behavior, SIMD/WGP/SA selection, token inclusion/exclusion, write-pointer format, halt/poweroff handshakes, trace status, and dropped/finish counters. These fields are critical for profiling, debug capture, and KFD thread-trace interrupt interpretation.

The final pwrdec section describes clock-gating override registers. Those constants name on/off delay and hysteresis fields, performance-monitor clock overrides, register-clock overrides, debug-bus enables, and many `SOFT_OVERRIDE*` and `SOFT_STALL_OVERRIDE*` bits that can force clocks or stalls in individual graphics sub-blocks.

## Important APIs, Types, And Macros

This chunk's interface is C preprocessor metadata. The important API shape is the pair of generated names:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift for a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for that field.

Representative selector groups include:

- `PA_SU_PERFCOUNTER2_SELECT` and `PA_SU_PERFCOUNTER3_SELECT`, each with `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE` fields.
- `PA_SC_PERFCOUNTER0_SELECT` and `PA_SC_PERFCOUNTER0_SELECT1`, plus simpler `PA_SC_PERFCOUNTER1_SELECT` through `PA_SC_PERFCOUNTER7_SELECT` with only `PERF_SEL`.
- `SPI_PERFCOUNTER0_SELECT` through `SPI_PERFCOUNTER5_SELECT` and matching `*_SELECT1` registers.
- `PC_PERFCOUNTER0_SELECT` through `PC_PERFCOUNTER3_SELECT` and matching `*_SELECT1` registers.
- `SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT` and `SQG_PERFCOUNTER0_SELECT` through `SQG_PERFCOUNTER7_SELECT`; these use `PERF_SEL`, `SPM_MODE`, and `PERF_MODE` fields with 9-bit selector masks.
- `SX`, `TA`, `TD`, `TCP`, `GL1C`, `GL1XC`, `CB`, `DB`, `RMI`, `PA_PH`, `UTCL1`, `WGS`, `GL1A`, and `GL1XA` performance-counter selectors.

Important control and status groups include:

- `SQG_PERFCOUNTER_CTRL`: `PS_EN`, `GS_EN`, `HS_EN`, `CS_EN`, per-ME/pipe disable bits, and `POLL_BEFORE_PERF_READ`.
- `SQG_PERFCOUNTER_CTRL2` and `SQ_PERFCOUNTER_CTRL2`: `FORCE_EN` and `VMID_EN` masks.
- `SQ_PERFCOUNTER_CTRL`: stage enables and per-ME/pipe performance disables.
- `SQG_PERF_SAMPLE_FINISH`: `STATUS`.
- `CB_PERFCOUNTER_FILTER`: color-buffer perf filtering by operation, format, clear, MRT, sample count, and fragment count.
- `RMI_PERF_COUNTER_CNTL`: transaction/event/TC enable selectors, event-window masks, CID/VMID filters, burst-length threshold, soft reset, and SPM selection.

Important SQ thread-trace groups include:

- `SQ_THREAD_TRACE_BUF0_SIZE`, `SQ_THREAD_TRACE_BUF0_BASE_LO`, `SQ_THREAD_TRACE_BUF0_BASE_HI`, and the corresponding buffer 1 registers.
- `SQ_THREAD_TRACE_CTRL`: `MODE`, `GL1_PERF_EN`, `INTERRUPT_EN`, `DOUBLE_BUFFER`, `HIWATER`, `REG_AT_HWM`, `SPI_STALL_EN`, `SQ_STALL_EN`, `STALL_ALL_SIMDS`, `UTIL_TIMER`, `WAVESTART_MODE`, sync-count controls, `LOWATER_OFFSET`, `GL1X_PREFETCH_PAGE`, auto-flush fields, `NCP_REG_TOKEN_EN`, and `DRAW_EVENT_EN`.
- `SQ_THREAD_TRACE_MASK`: SIMD, WGP, SA, wave-type include, non-detail exclusion, and SIMD-power fields.
- `SQ_THREAD_TRACE_TOKEN_MASK`: token exclude, execution-token, BOP-event include, barrier/ALU-exec exclusions, register include/exclude/detail, and instruction exclude fields.
- `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_HALT`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_STATUS2`, draw/marker counters, dropped counter, and finish-done debug fields.

The pwrdec clock-control groups include:

- SPI-related `GFX_ICG_SPI_RA0_CLK_CTRL`, `GFX_ICG_SPI_RA1_CLK_CTRL`, `GFX_ICG_SPI_CS_CTRL`, `GFX_ICG_SPI_PS_CTRL`, `GFX_ICG_SPIS_CTRL`, `CGTX_SPI_DEBUG_CLK_CTRL`, and `GFX_ICG_SPI_CTRL`.
- Pipeline clock controls such as `GFX_ICG_PC_CLK_CTRL`, `GFX_ICG_BCI_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_GS_NGG_CLK_CTRL`, `CGTT_PA_CLK_CTRL`, `CGTT_SQ_CLK_CTRL`, `CGTT_SQG_CLK_CTRL`, `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL`, `SQ_CLK_CTRL`, `ICG_SQ_CLK_CTRL`, and `ICG_SP_CLK_CTRL`.
- Backend and cache-related controls such as `GFX_ICG_SX_CLK_CTRL0` through `GFX_ICG_SX_CLK_CTRL4`, `GFX_ICG_TA_CTRL`, `GFX_ICG_TD_CTRL`, `DB_CGTT_CLK_CTRL_0`, `GFX_ICG_CB_CTRL`, `GFX_ICG_RMI_CTRL`, `GFX_ICG_SE_CAC_CLK_CTRL`, and `CGTT_PH_CLK_CTRL0` through the first fields of `CGTT_PH_CLK_CTRL3`.

## Control Flow

There is no direct control flow in this header. Runtime control flow is provided by consumers that include this file and use the macros with AMDGPU register helpers. The typical flow is:

1. A GC 12.1.0 driver path chooses a register from `gc_12_1_0_offset.h`.
2. The driver constructs a 32-bit register value using field values shifted by `__SHIFT` and constrained by the matching `_MASK`, often through local helpers such as `REG_SET_FIELD()` or equivalent bit operations.
3. The driver writes the register through SOC15 MMIO helpers such as `WREG32_SOC15()` or reads through `RREG32_SOC15()`.
4. For status registers, the driver extracts fields from the read value with the generated mask/shift pair, often through `REG_GET_FIELD()`.

For performance counters, the runtime flow is selection/programming, workload execution, sample/finish polling, then counter readback. For SQ thread trace, the flow is buffer programming, mask/token/control setup, trace enable, status or interrupt observation, write-pointer and buffer readback, and optional halt/poweroff coordination. For clock-control fields, the flow is usually read-modify-write around feature toggles, power management transitions, debug modes, or performance-monitor clock override changes.

## State And Persistence Behavior

The macros themselves hold no state. They describe state fields in hardware registers.

Performance-counter selector state persists in the programmed GC hardware registers until reset, reprogramming, power-gating loss, or another driver/profiling client changes the selector registers. The selected events determine what the corresponding hardware counters accumulate or stream.

SQ thread-trace state is split between programmed configuration and live status. Buffer base and size fields point hardware at trace memory. Control, mask, and token-mask fields define what gets captured. Write pointer, busy/full/error/status, dropped counter, and finish-done fields are live hardware observations. These fields can change while shaders run, while trace buffers fill, when interrupts fire, or during halt/poweroff transitions.

Clock-control state is persistent hardware configuration while the graphics block remains powered and programmed. The `ON_DELAY`, `OFF_HYSTERESIS`, `REG_CLK_OVERRIDE`, `PERFMON_CLK_OVERRIDE`, `SOFT_OVERRIDE*`, and `SOFT_STALL_OVERRIDE*` fields alter how clocks gate or remain forced on. Wrong values can persist across workloads until reset or explicit restoration, affecting power, performance, trace collection, and debug visibility.

## Dependencies And Integration Points

This chunk depends on the generated AMD register database for GC 12.1.0. It must remain synchronized with:

- `gc_12_1_0_offset.h`, which supplies the register addresses for the fields named here.
- Other generated GC 12.1.0 headers, especially field names consumed by `REG_SET_FIELD()` and `REG_GET_FIELD()` call sites.
- AMDGPU SOC15 accessors such as `RREG32_SOC15()`, `WREG32_SOC15()`, and instance/XCC selection through helpers like `GET_INST(GC, xcc_id)`.
- GC 12.1.0 driver files that include this header: `gfx_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `sdma_v7_1.c`, `soc_v1_0.c`, `imu_v12_1.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c`.
- Profiling, perfmon, SPM, SQ thread-trace, GPU debug, KFD trace-interrupt handling, and clock/power-management paths that program or decode the named hardware registers.

The path lives under a `ceph-client` source tree mirror, but this file is AMD GPU driver hardware metadata and has no distributed-filesystem data path, no Ceph protocol behavior, and no storage persistence semantics.

## Risks And Edge Cases

- These macros are untyped constants. A wrong mask or shift can compile cleanly and silently program the wrong bits.
- Many register names repeat a similar pattern across blocks, but field widths differ. For example, SQ/SQG selectors use 9-bit `PERF_SEL` masks in this chunk, while many other blocks use 10-bit selector masks. Copying a selector pattern across blocks can corrupt neighboring mode fields.
- The chunk begins and ends mid-logical area. `PA_SU_PERFCOUNTER0/1` are in the previous chunk, and `CGTT_PH_CLK_CTRL3` is incomplete here. Whole-file analysis must merge adjacent chunks.
- Thread-trace fields are sensitive to buffer sizing, base-address programming, high-water/low-water thresholds, double-buffer selection, and token filters. A mask mismatch can cause lost packets, missing register/detail tokens, wrong buffer selection, or trace interrupts that never arrive.
- Performance-counter selector errors may produce plausible but wrong numbers. These failures are hard to catch with compile tests because the register writes remain syntactically valid.
- VMID and pipe-disable fields in `SQ_PERFCOUNTER_CTRL2`, `SQG_PERFCOUNTER_CTRL2`, and the per-ME/pipe controls can accidentally hide events from some workloads or queues.
- Clock-gating override fields can affect power and liveness. Leaving a soft override asserted may increase power or prevent clock gating; clearing a required debug/perfmon override may make counters or trace logic unreliable.
- Some `SOFT_OVERRIDE*` bits are sparse and hardware-specific. The absence of certain bit numbers is intentional generated metadata, not an invitation to fill gaps manually.
- Cross-generation AMD GC headers contain similarly named fields with different masks. Reusing GC 12.1.0 masks for GC 12.0, GC 11, or GC 9 hardware can break profiling or power-management behavior.

## Test Signals

Useful validation signals include:

- Build AMDGPU and AMDKFD with GC 12.1.0 support enabled. Missing macro names or renamed fields should surface in include users that rely on this register namespace.
- Run static or generated-header consistency checks that compare `gc_12_1_0_sh_mask.h` against AMD's authoritative GC 12.1.0 register database and the paired `gc_12_1_0_offset.h`.
- Exercise GPU performance-counter programming on GC 12.1.0 hardware across PA, SPI, SQ/SQG, TCP, GL1, CB, DB, RMI, and UTCL1 blocks. Look for implausible zero counters, saturated counters, or events attributed to the wrong block.
- Run SQ thread-trace capture with single and double buffering, VMID/WGP/SIMD masks, token filters, finish handling, and buffer-full interrupts. Validate `SQ_THREAD_TRACE_STATUS`, `STATUS2`, `WPTR`, dropped counter, and finish-done fields against expected trace buffer contents.
- Test KFD thread-trace interrupt paths on GC 12.1.0 workloads and confirm buffer-full and UTC/error reporting match hardware status.
- Toggle graphics clock-gating and perfmon-clock override paths, then check power-management telemetry, performance-counter reliability, and absence of hangs during suspend/resume, reset, and GPU fault recovery.
- Compare against nearby generated GC headers only with generation-aware expectations. Similar names should not be treated as proof that bit positions are interchangeable.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of the PA/SU performance-counter selection block and other preceding GC shift/mask definitions. The next chunk is needed for the rest of `CGTT_PH_CLK_CTRL3` and any following pwrdec or closing definitions. The final per-file research document should combine this chunk with adjacent chunks before summarizing complete performance-counter, thread-trace, and clock-control coverage for `gc_12_1_0_sh_mask.h`.

### subset-b-002608: lines 40017-42372

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 40017-42372

## Chunk Scope

This chunk is a generated AMD GC 12.1 register field header segment. It contains C preprocessor `#define` constants for bit shifts and masks, not executable functions. The definitions cover late graphics clock-gating controls, shader-array/user configuration, GRBMH remap controls, and a large GCVM/GCMC/GCUTCL2 virtual-memory register block. It is paired with `gc_12_1_0_offset.h`: offset macros identify MMIO registers, while this header identifies fields inside those 32-bit registers for `REG_SET_FIELD`, `REG_GET_FIELD`, direct shifts, and direct mask operations.

The range begins in the middle of `CGTT_PH_CLK_CTRL3`, so the first `CGTT_PH_CLK_CTRL3__SOFT_OVERRIDE*` definitions depend on earlier lines for the complete register field set. The chunk also ends in the middle of `GCVM_INVALIDATE_ENG11_REQ`; engines 12-17 request fields and later acknowledgement/range registers are outside this chunk.

## Purpose

The constants let GC 12.1 driver code program ASIC-specific hardware registers without embedding raw bit numbers at every call site. The visible register families support:

- Clock gating and power management overrides for TCP, LDS, UTCL1, GRBMH, scan converter, GL1 cache blocks, GCUTCL2, and GCVM L2.
- Shader engine/user-visible topology controls such as inactive WGPs, RB backend disablement, RMI redundancy repair, shader rate, GL1 pipe steering, and GL1 hash configuration.
- Remapping of WGP and RB resources through GRBMH hypervisor decode registers, including per-side SA0/SA1 remap enables and remap targets.
- GC memory-controller and VM apertures for framebuffer, AGP, system aperture, default page, dummy page, and identity mappings.
- GCVM L2 TLB/cache setup, cache invalidation, context control, protection-fault behavior, parity/debug/throttle controls, translation-assist request/response registers, and invalidation engine semaphore/request fields.

## Important Macro Groups

Clock-gating groups include `GFX_ICG_TCP_CTRL`, `GFX_ICG_TCP_CTRL2`, `ICG_LDS_CLK_CTRL`, `GFX_ICG_UTCL1_CTRL`, `GFX_ICG_GRBMH_CTRL`, `CGTT_SC_CLK_CTRL0..4`, `ICG_GL1C_CLK_CTRL`, `ICG_GL1XC_CLK_CTRL`, `ICG_GL1A_CTRL`, `ICG_GL1XA_CTRL`, and `GCUTCL2_ICG_CTRL` / `GCVM_L2_ICG_CTRL`. Most fields are `*_OVERRIDE`, `SOFT_OVERRIDE_*`, `OFF_HYSTERESIS`, `ON_DELAY`, `DYNAMIC_CLOCK_OVERRIDE`, `STATIC_CLOCK_OVERRIDE`, `AON_CLOCK_OVERRIDE`, or `PERFMON_CLOCK_OVERRIDE`. Driver code can force clock domains on/off, tune gating hysteresis, or keep debug/performance domains active.

Shader/topology groups include `GL1_PIPE_STEER_LSB`, `GL1_PIPE_STEER_MSB`, `GL1_HASH_CFG`, `GC_USER_SHADER_ARRAY_CONFIG`, `GC_USER_RB_BACKEND_DISABLE`, `GC_USER_RMI_REDUNDANCY`, and `GC_USER_SHADER_RATE_CONFIG_1`. These encode inactive WGP masks, RB backend masks, RMI repair controls, shader-rate fields, and GL1 steering/hash fields. `gfx_v12_1.c` uses the user shader array and RB backend masks when deriving active WGP/RB topology and programming harvested units.

GRBMH remap groups include `GRBMH_WGP_SA0_REMAP_CNTL`, `GRBMH_WGP_SA1_REMAP_CNTL`, `GRBMH_RB_SA0_REMAP_CNTL`, and `GRBMH_RB_SA1_REMAP_CNTL`. The WGP controls expose per-side `SIDE{0,1}_WGP{0..10}_SA{0,1}_REMAP_EN`, `REMAP_TO_SIDE`, and `REMAP_TO_WGP` fields; RB controls expose per-RB enable and remap target fields. These are low-level topology repair/remap knobs.

VM aperture and shared-function groups include `GCMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_{LSB,MSB}`, `GCMC_VM_FB_LOCATION_*`, `GCMC_VM_AGP_*`, `GCMC_VM_SYSTEM_APERTURE_*`, `GCMC_VM_MX_L1_TLB_CNTL`, and `GCMC_SHARED_ACTIVE_FCN_ID`. `gfxhub_v12_1.c` uses these register families to configure framebuffer/AGP/system apertures, default page addresses, L1 TLB behavior, and SR-IOV-visible framebuffer copy registers.

GCVM L2 groups include `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_L2_CNTL4`, `GCVM_L2_CNTL5`, `GCVM_L2_STATUS`, `GCVM_L2_MM_GROUP_RT_CLASSES`, bank-select, parity, GCR, PTE-cache dump, throttle, debug, and credit-safety registers. These fields configure L2 cache enablement, fragment processing, endian modes, PDE/PTE cache sizing and associativity, invalidate behavior, bank selection, parity checking/injection, page-walker throttling, credit updates, and fault-interrupt routing.

Protection-fault groups include `GCVM_L2_PROTECTION_FAULT_CNTL_LO32`, `GCVM_L2_PROTECTION_FAULT_CNTL_HI32`, `GCVM_L2_PROTECTION_FAULT_CNTL2`, `GCVM_L2_PROTECTION_FAULT_MM_CNTL3/4`, status/address/default-address registers, and `GCVML2_IH_FAULT_INTERRUPT_CNTL`. They cover fault status clearing, subsequent update allowance, default fault behavior for range/PDE/valid/read/write/execute/dummy faults, client-id interrupt masks, crash-on-fault controls, retry-fault interrupt controls, active page migration retry behavior, poison interrupt routing, and logged fault fields such as walker error, permission faults, CID, RW, VMID, VF, and VFID.

Context groups include repeated `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` definitions plus `GCVM_CONTEXTS_DISABLE`. Each context control register has the same field layout in this chunk: `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry flags for permission/invalid and other faults, and interrupt/default bits for range, dummy-page, PDE0, valid, read, write, and execute protection faults. `GCVM_CONTEXTS_DISABLE` provides one disable bit per context 0-15.

Invalidation groups include `GCVM_INVALIDATE_ENG0_SEM` through `GCVM_INVALIDATE_ENG17_SEM` and request layouts for `GCVM_INVALIDATE_ENG0_REQ` through the visible portion of `GCVM_INVALIDATE_ENG11_REQ`. Request fields include `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0..3`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY`.

Translation-assist groups include `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_ADDR_*`, request attributes, response address, and response attributes. They encode VMID/VFID/VF, GPA mode, requested permissions, client ID, request bit, response permissions, fragment size, snoop/SPA/IO/TMZ/no-PTE/MTYPE/compression/NACK/HDM/TMPM retry, and ACK.

## Control Flow and State Behavior

There is no local control flow because the file is declarative. Runtime control flow appears in consumers:

- `gfxhub_v12_1.c` reads and writes GCVM/GCMC registers through `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and `WREG32_SOC15_OFFSET`, using these masks with `REG_SET_FIELD` / `REG_GET_FIELD`.
- GFX hub initialization programs VM page-table base/start/end registers, system/AGP/framebuffer apertures, default fault pages, L1 TLB controls, GCVM L2 cache controls, context control registers, and identity apertures.
- VM invalidation code builds `GCVM_INVALIDATE_ENG0_REQ` values with the request masks in this chunk, then writes invalidate request registers and polls related semaphore/acknowledgement state from adjacent register definitions.
- Fault handling reads `GCVM_L2_PROTECTION_FAULT_STATUS_LO32` and decodes status bits from this chunk to report more faults, walker errors, permission failures, mapping errors, VMID/client fields, and access direction.
- KFD queue management copies `hub->vm_cntx_cntl` and toggles `GCVM_CONTEXT0_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT__SHIFT` for per-process XNACK behavior.

The state represented here is persistent hardware state, not software-owned memory. Values survive as MMIO register contents until rewritten by initialization, reset, suspend/resume restore, virtualization policy, or hardware events. Some fields are configuration state, such as context enable bits and cache sizing. Others are status or command-like state, such as fault status bits, invalidation request bits, semaphore bits, PTE dump readiness, credit update strobes, and translation-assist request/ack bits.

## Dependencies and Integration Points

This header depends on the AMDGPU register access macro stack understanding the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention. In practice, `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)` concatenate these names to find the generated shift/mask macros.

Known direct includers in the GC 12.1 code path include `amdgpu/gfxhub_v12_1.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/mes_v12_1.c`, `amdgpu/sdma_v7_1.c`, `amdgpu/imu_v12_1.c`, `amdgpu/soc_v1_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, and KFD queue/MQD managers. The VM and fault fields are most tightly integrated with `gfxhub_v12_1.c`; shader-array and RB fields are used by `gfx_v12_1.c`; XNACK retry control is used by `kfd_device_queue_manager_v12_1.c`.

The source is ASIC-version-specific. Similar names exist in older `gc_10_*` and `gc_12_0_0` headers, but field positions can differ. For example, GC 12.1 `GCVM_CONTEXT0_CNTL__PAGE_TABLE_BLOCK_SIZE__SHIFT` is visible at bit 4 in this chunk, while older GC headers place comparable fields differently. Reusing constants across ASIC generations would silently program wrong bits.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can break GPU VM setup, page fault retry behavior, invalidation, cache coherency, clock-gating, or resource harvesting without compiler errors.
- Repeated context and invalidate-engine definitions invite copy/paste or generator mistakes. Context 0-15 should remain layout-identical in this chunk; invalidate engine request definitions should remain layout-identical across engines, with the caveat that this chunk truncates after part of engine 11.
- Clock-gating override fields can affect power, hangs, and performance. Misprogramming `*_OVERRIDE`, `ALWAYS_BUSY`, or hysteresis fields may hide hardware idle/busy transitions or keep domains active.
- Fault-control fields are security and reliability sensitive. Defaults for read/write/execute/valid/PDE faults, retry-fault interrupts, no-retry crash behavior, and status clearing affect whether GPU VM faults are recoverable, visible, or fatal.
- SR-IOV/VF fields and framebuffer copy registers interact with virtualization policy. `gfxhub_v12_1.c` already avoids some aperture programming for VFs; any future consumer of `GCMC_SHARED_ACTIVE_FCN_ID` or `GCMC_VM_FB_LOCATION_*` must preserve PF/VF access rules.
- The line range starts and ends mid-register-family. A merged per-file report must reconcile neighboring chunks for complete `CGTT_PH_CLK_CTRL3` and `GCVM_INVALIDATE_ENG11+` coverage.

## Test and Validation Signals

- Build coverage: compile AMDGPU/KFD with GC 12.1 support so all `REG_SET_FIELD` / `REG_GET_FIELD` references resolve against this header and its offset companion.
- Boot/init signal: on GC 12.1 hardware or simulator, `gfxhub_v12_1` should initialize GART/system apertures, GCVM L2 controls, context controls, and identity aperture registers without VM hub timeouts.
- VM invalidation signal: GPUVM map/unmap and TLB invalidation paths should complete, with invalidation engine semaphore/ack polling not timing out.
- Fault signal: intentional GPUVM fault tests should decode `GCVM_L2_PROTECTION_FAULT_STATUS_LO32` fields coherently and should respect retry/no-retry and XNACK settings.
- KFD signal: per-process XNACK enable/disable should toggle the GCVM context retry bit consistently with `SH_MEM_CONFIG__RETRY_DISABLE`, and compute queues should continue to launch.
- Topology signal: harvested WGP/RB configurations should produce expected inactive WGP and RB backend masks in `gfx_v12_1.c`.
- Power/performance signal: clock-gating register programming should not regress idle power, hang detection, perf counter access, or workload stability.

### subset-b-002609: lines 42373-44638

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 42373-44638

## Scope

This chunk is the tail of AMD's generated GC 12.1.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, variables, allocations, locks, or executable branches. The covered register families are:

- The end of `GCVM_INVALIDATE_ENG11_REQ` plus complete request bitfields for invalidate engines 12-17.
- Acknowledgement and address-range fields for invalidate engines 0-17.
- Page-table base, start, and end address fields for GCVM contexts 0-15.
- Per-context and global GCVM L2 PTE-cache fragment-size controls.
- GCMC VM L2, GCUTCL2, GC ATC L2, and GC L2TLB performance counter configuration/result controls.
- Virtualization, host translation, IOMMU, framebuffer aperture, local/system memory aperture, and compression/translation bypass controls under the GC UTCL2 and GCMC VM blocks.
- GC ATC L2 cache/control/status/fault fields and GC L2TLB retry/reserved-space status fields.
- The `gfx_se_sqind` SQ wave debug-state bitfields from `SQ_DEBUG_STS_LOCAL` through `SQ_WAVE_EXEC_HI`, followed by the file's closing `#endif`.

The sibling offset constants for these registers live in `gc_12_1_0_offset.h`; this file defines how callers pack or decode each register value.

## Purpose

The purpose of this chunk is to expose hardware bit layouts for GC 12.1.0 GPU VM, translation cache, performance-monitor, virtualization, and shader-wave debug registers. AMDGPU code uses these macros through helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()` so driver code can set VM invalidation requests, program per-VMID page-table registers, configure fault/translation behavior, and decode diagnostic hardware state without hard-coding bit positions in C files.

The VM-side definitions support the graphics hub's address-translation path. `GCVM_INVALIDATE_ENG*_REQ` fields select VMIDs, flush type, L2 PTE/PDE invalidation levels, L1 PTE invalidation, fault-status clearing, request logging, 4K-only invalidation, and PDE3 invalidation. The matching `GCVM_INVALIDATE_ENG*_ACK` fields expose per-VMID completion acknowledgements and semaphore state. The `GCVM_CONTEXT*_PAGE_TABLE_*` fields define 64-bit page-directory entries and logical page ranges for each VM context.

The UTCL2/ATC/L2TLB definitions support translation-cache configuration and observability. They describe event selector ranges, counter enable/clear bits, trigger controls, ATC L2 request/cache behavior, fault logging, retry timeout attribution, reserved-space encoding detection, IOMMU enablement, VMID translation bypass, GPU host translation, and framebuffer/system-memory apertures.

The SQ definitions support low-level wavefront inspection. They provide masks for wave status, mode, exception flags, trap controls, program counter, execution mask, hardware IDs, scheduler state, instruction-buffer state, scratch base, TTMP registers, and XNACK state. In `gfx_v12_1.c`, these layouts pair with `ixSQ_WAVE_*` indices from the offset header for GPU hang/debug capture.

## Important APIs, Types, And Macros

The exported interface is entirely preprocessor macros using the generated naming scheme `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

Key VM invalidate fields in this chunk include:

- `GCVM_INVALIDATE_ENG12_REQ` through `GCVM_INVALIDATE_ENG17_REQ`: `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0` through `INVALIDATE_L2_PDE3`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY`.
- `GCVM_INVALIDATE_ENG0_ACK` through `GCVM_INVALIDATE_ENG17_ACK`: `PER_VMID_INVALIDATE_ACK` and `SEMAPHORE`.
- `GCVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through engine 17: low fields include `S_BIT` and `LOGI_PAGE_ADDR_RANGE_LO31`; high fields expose `LOGI_PAGE_ADDR_RANGE_HI14`.

Key per-context VM fields include:

- `GCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` through context 15: 64-bit page-directory entry halves.
- `GCVM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32/HI32` and `END_ADDR_LO32/HI32` through context 15: logical page-number range halves, with 13-bit high logical-page fields.
- `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `GCVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`: small/big fragment size fields and `BANK_SELECT`.

Key performance monitor fields include:

- `GCMC_VM_L2_PERFCOUNTER*_CFG` for counters 0-15, `GC_ATC_L2_PERFCOUNTER*_CFG` for counters 0-15, `GCUTCL2_PERFCOUNTER*_CFG` for counters 0-3, and `GC_L2TLB_PERFCOUNTER*_CFG` for counters 0-3. Each configuration register has `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR`.
- `*_PERFCOUNTER_RSLT_CNTL` registers expose `PERF_COUNTER_SELECT`, `START_TRIGGER`, `STOP_TRIGGER`, `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`.
- `GCUTCL2_PERFCOUNTER_EVENTS_GROUP_SELECT` selects event groups for UTCL2 performance counter sets.

Key translation, aperture, and fault fields include:

- `GCVM_PCIE_ATS_CNTL`, `GCVM_IOMMU_GPU_HOST_TRANSLATION_ENABLE`, `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, `GCVM_IOMMU_CONTROL_REGISTER`, and `GCVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVML2_SEC_MASTER`, `GCUTC_TRANSLATION_FAULT_CNTL0/1`, `GCUTCL2_COMP_EN_OVERRIDES`, and `GCUTCL2_ROUTER_CNTL`.
- `GCMC_VM_FB_SIZE_OFFSET_VF0` through `VF7`, `GCMC_VM_FB_OFFSET`, `GCMC_VM_LOCAL_FB_ADDRESS_START/END`, `GCMC_VM_LOCAL_FB_ADDRESS_LOCK_CNTL`, and cacheable/local/LPDDR system-memory aperture registers.
- `GC_ATC_L2_FAULT_CNTL`, `GC_ATC_L2_FAULT_STATUS`, and `GC_ATC_L2_FAULT_ADDR_LO/HI`, which clear/log ATC L2 faults and identify fault type, client ID, access type, VMID, VF, VFID, and logical address.
- `GC_L2TLB_RETRY_TIMEOUT_STATUS_0/1/2` and `GC_L2TLB_TLB0_RESERVED_SPACE_ENCODING_STATUS`, which attribute timeout or reserved-space events to logical address, VMID/VFID/VF, permissions, TMZ/TEE, client, TLB ID, and clear bits.

Key SQ wave fields include:

- `SQ_WAVE_STATUS`, `SQ_WAVE_STATE_PRIV`, `SQ_WAVE_MODE`, `SQ_WAVE_EXCP_FLAG_PRIV`, `SQ_WAVE_EXCP_FLAG_USER`, and `SQ_WAVE_TRAP_CTRL` for wave state, privilege flags, exception flags, and trap enablement.
- `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_EXEC_LO/HI`, `SQ_WAVE_M0`, `SQ_WAVE_TTMP0` through `SQ_WAVE_TTMP15`, `SQ_WAVE_SCRATCH_BASE_LO/HI`, and `SQ_WAVE_XNACK_MASK`.
- `SQ_WAVE_HW_ID1/2`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_DVGPR_ALLOC_LO/HI`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_IB_STS2`, `SQ_WAVE_IB_DBG1`, `SQ_WAVE_SCHED_MODE`, `SQ_WAVE_ACTIVE`, and `SQ_WAVE_VALID_AND_IDLE`.

## Control Flow

There is no direct control flow in the header. Runtime behavior is in consumers that combine these masks with register offsets and MMIO helpers.

For VM invalidation, `gfxhub_v12_1_get_invalidate_req()` in `amdgpu/gfxhub_v12_1.c` builds a request word using `REG_SET_FIELD()` against `GCVM_INVALIDATE_ENG0_REQ`. It sets the target VMID bit, flush type, L2 PTE/PDE invalidation bits including `INVALIDATE_L2_PDE3`, and L1 PTE invalidation before the VM hub code writes the request to the selected invalidate engine. `gfxhub_v12_1_xcc_init()` records the per-XCC base offsets for engine 0 request/ack/semaphore registers and computes `eng_distance` and `eng_addr_distance` from adjacent generated offsets, so the same field layout applies across engines.

For page-table programming, `gfxhub_v12_1_xcc_setup_vm_pt_regs()` writes the low and high page-table base halves with `WREG32_SOC15_OFFSET()` at `hub->ctx_addr_distance * vmid`. The shift/mask macros in this chunk define the full 32-bit payload fields for those base registers and the start/end range registers that surround them in hardware.

For SQ wave debug, `gfx_v12_1.c` writes `regSQ_IND_INDEX` using `SQ_IND_INDEX` fields from earlier in the header, then reads `regSQ_IND_DATA`. `gfx_v12_1_read_wave_data()` collects fields such as status, PC, `EXEC_LO/HI`, hardware IDs, GPR/LDS allocation, IB status, `M0`, mode, privileged state, exception flags, trap control, active/valid state, DVGPR allocation, and scheduling mode. The macros in this chunk are the decode contract for interpreting the returned 32-bit values.

For performance counters and ATC/L2TLB diagnostics, this chunk supplies configuration and result-control bitfields. Actual control flow is in performance/debug tooling or driver code that writes event selectors, enables counters, reads low/high result registers, and clears or stops counters through the generated result-control fields.

## State And Persistence Behavior

The macros themselves hold no software state. They describe hardware registers whose contents are persistent or transient depending on the underlying block.

VM context base/start/end registers persist in the GC VM hub until rewritten, reset, or power-gated according to hardware rules. AMDGPU stores enough register-offset metadata in `adev->vmhub[]` to program these per XCC, and some hub versions save/restore page-table base registers across suspend/resume or reset paths.

Invalidate request registers are command-style hardware state. The driver writes request bits for one or more VMIDs, then observes acknowledgement bits and semaphores in the corresponding `ACK` registers. Address-range fields narrow the invalidation scope when range-based invalidation is used. Incorrect request or range fields can leave stale translations in L1/L2 TLB/PTE caches.

Fault status registers are sticky diagnostic state until cleared through the corresponding control fields. ATC L2 fault status and address registers capture fault metadata such as client, VMID, VF/VFID, access type, and logical address. Retry-timeout and reserved-space status registers similarly preserve the detected condition until a clear bit is written.

Performance counter configuration registers persist while programmed. Counter result registers accumulate events until cleared, stopped, saturated, disabled, or reset. The `CLEAR`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE` fields are therefore state-changing controls, not passive decode fields.

SQ wave registers expose live shader-queue state for a selected resident wave. Fields such as PC, EXEC, trap flags, TTMPs, XNACK state, scheduler mode, allocation, and IB status can change as the wave executes, traps, stalls, or exits. Debug consumers must correlate with `SQ_WAVE_STATUS`, `SQ_WAVE_ACTIVE`, and `SQ_WAVE_VALID_AND_IDLE` before treating a captured value as meaningful.

## Dependencies And Integration Points

This chunk depends on AMD's generated GC 12.1.0 register database and must stay synchronized with:

- `gc_12_1_0_offset.h`, which supplies the `reg*` and `ix*` addresses/indices for the field layouts defined here.
- `amdgpu/gfxhub_v12_1.c`, which uses `GCVM_INVALIDATE_ENG0_REQ`, context page-table base fields, fault-control/status fields, and generated offsets to initialize and drive the GC VM hub.
- `amdgpu/gfx_v12_1.c`, which uses SQ indirect offsets plus the SQ field definitions to collect type-4 wave debug data.
- `amdgpu/mes_v12_1.c`, `amdgpu/sdma_v7_1.c`, `amdgpu/soc_v1_0.c`, `amdgpu/imu_v12_1.c`, `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, and KFD v12.1 queue-management files, which include the GC 12.1.0 offset/mask headers for register programming.
- `include/soc24_enum.h`, which provides event enum namespaces such as `GCUTCL2_PERF_SEL` that pair with the performance-counter selector fields.
- AMDGPU SOC15 MMIO helpers (`RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `SOC15_REG_OFFSET`) and field helpers (`REG_SET_FIELD`, `REG_GET_FIELD`).

The path is under a `ceph-client` source mirror, but this file is AMD GPU driver metadata. It has no Ceph or distributed filesystem control path.

## Risks And Edge Cases

- The file is generated, untyped hardware metadata. Wrong shifts or masks can compile cleanly while silently writing the wrong hardware bits or decoding incorrect fault/debug data.
- GC 12.1.0 values are ASIC-specific. Similar macro names in GC 12.0, GC 11, or GCA headers do not prove identical bit layouts or register availability.
- VM invalidation errors are high impact. Missing `INVALIDATE_L2_PDE3`, wrong `PER_VMID_INVALIDATE_REQ`, wrong address-range high/low fields, or bad acknowledgement masks can cause stale translations, timeouts, or hard-to-debug GPU VM faults.
- Context start/end high masks expose only defined high logical-page bits. Treating the fields as unconstrained 64-bit addresses rather than hardware logical page-number pieces can program invalid ranges.
- Fault status is sticky and may represent the first fault unless subsequent updates are enabled. Consumers that do not clear or log in the documented order can misattribute later faults.
- Performance counter fields combine event selectors and control bits in one word. Accidental writes to `CLEAR`, `ENABLE`, or `CLEAR_ALL` while changing `PERF_SEL` can lose samples or start counters at the wrong time.
- Translation bypass, IOMMU enablement, GPU host translation, VF framebuffer aperture, and local FB lock fields are security/virtualization sensitive. Wrong values can expose incorrect memory apertures, bypass translation unexpectedly, or break SR-IOV/guest isolation.
- SQ wave state is volatile. Reading `PC`, `EXEC`, exception flags, or TTMPs without checking validity/idle state can report stale or unrelated wave-slot contents.
- The chunk boundary starts in the middle of `GCVM_INVALIDATE_ENG11_REQ` and ends at the file terminator. Whole-file conclusions should merge with preceding chunks for the complete engine 0-11 request definitions and earlier GCVM/SQ field groups.

## Test Signals

Useful validation signals include:

- Build AMDGPU with GC 12.1.0 support enabled. Missing or renamed macros should fail in GC 12.1 paths such as `gfxhub_v12_1.c`, `gfx_v12_1.c`, MES, SDMA, SOC, IMU, and KFD queue-management units.
- Exercise VM context setup on GC 12.1 hardware and verify page-table base registers are programmed per VMID/XCC through `gfxhub_v12_1_xcc_setup_vm_pt_regs()`.
- Run VM invalidation and GART/page-table update workloads under IOMMU/GPUVM pressure. Stale mappings, VM fault storms, invalidate timeout logs, or mismatched ACK bits point to request/ack/range field problems.
- Trigger or inspect GCVM/ATC/L2TLB faults and confirm decoded client ID, VMID, VF/VFID, access type, and fault address match the failing access.
- Use performance monitoring or register-level diagnostics for GCMC VM L2, GCUTCL2, GC ATC L2, and GC L2TLB counters. Counter enable/clear behavior and event counts should match selected event groups and `soc24_enum.h` event IDs.
- Capture wave data through GC 12.1 debug/hang paths and verify PC, EXEC, HW IDs, allocation, IB state, trap/exception flags, and scheduler fields are plausible and ordered consistently with `gfx_v12_1_read_wave_data()`.
- Mechanically compare this generated block against AMD's authoritative GC 12.1.0 register database and the matching offset header; manual review should treat any divergence from generation as suspicious.

## Cross-Chunk Notes

The final per-file report should merge this chunk with earlier chunks for the complete `gc_12_1_0_sh_mask.h` register namespace. Important adjacent dependencies include earlier `GCVM_INVALIDATE_ENG0_REQ` through `ENG11_REQ` definitions, `GCVM_CONTEXT*_CNTL` fault-enable fields used by `gfxhub_v12_1_xcc_init()`, `SQ_IND_INDEX`/`SQ_IND_DATA` fields used by the SQ indirect read path, and the earlier GCVM protection-fault status/control fields printed by `gfxhub_v12_1_print_l2_protection_fault_status()`.
