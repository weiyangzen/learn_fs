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
