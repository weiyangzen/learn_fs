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
