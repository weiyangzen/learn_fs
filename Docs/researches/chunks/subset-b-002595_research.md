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
