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
