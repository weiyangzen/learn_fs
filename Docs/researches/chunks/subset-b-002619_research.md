# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 9638-12160

## Scope

This chunk is a generated AMD GC 9.0 shift/mask register-header segment. It contains C preprocessor constants only: hardware register fields are represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros for packing and decoding 32-bit register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start inside `SPI_SHADER_PGM_RSRC2_VS`, after the corresponding shift definitions and the first masks from the previous chunk, then cover shader user-data and shader-program-resource fields for VS/GS/ES/HS/LS/common shader stages, compute dispatch/program-resource fields, and a large command-processor (`gc_cppdec`) block. The range ends in the `gc_cppdec2` block after `CP_SD_CNTL`; the next register, `CP_SOFT_RESET_CNTL`, starts immediately after the selected range. This boundary matters because several register families are split across adjacent chunks.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM graphics-core hardware metadata and is unrelated to Ceph or distributed filesystem logic.

## Purpose

`gc_9_0_sh_mask.h` supplies bit layouts for GC 9.0 graphics hardware. Driver code pairs these masks with register addresses from the matching GC 9.0 offset header and uses helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` instead of open-coded shifts and masks.

This chunk covers three broad programming surfaces:

- Shader stage setup for graphics pipelines. The macros describe user SGPR payload registers, shader program base addresses, shader resource registers, LDS/scratch/trap controls, CU/SIMD enable masks, wave limits, exception masks, stream-out controls, and stage-to-stage VGPR component counts for vertex, geometry, export, hull, and local shader paths.
- Compute dispatch state. The macros describe dispatch initiator flags, grid dimensions, start/restart coordinates, thread-group dimensions, pipeline-stat/perfcount enables, compute program address and resources, VMID, resource limits, static thread-management masks per shader engine, temporary-ring sizing, thread tracing, dispatch identifiers, relaunch state, wave-restore addresses, and 16 compute user-data registers.
- Command processor state. The macros describe deferred-write/data-fabric registers, CP interrupt control and status, UTCL1 controls and errors, graphics and compute ring-buffer bases/control/read and write pointers, doorbell controls and ranges, priority and VMID mapping, active-ring state, per-ring and per-pipe interrupts, ECC first-occurrence reporting, program-counter and interrupt-routine start addresses, context/VMID/preemption controls, CPC instruction-cache controls, MEC interrupt-disabling fields, VMID preemption status, scheduler doorbells, MQD base/control fields, and CP-side UTCL1 status.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the raw mask for that field inside the 32-bit register value.
- Matching register addresses are supplied by the sibling GC 9.0 offset header. Consumers include this file from GFX9 AMDGPU and KFD code such as `gfx_v9_0.c`, `soc15.c`, `amdgpu_amdkfd_gfx_v9.c`, `kfd_mqd_manager_v9.c`, `gmc_v9_0.c`, `gfxhub_v1_0.c`, `mxgpu_ai.c`, and Vega10 power-management include paths.
- AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, `SOC15_REG_OFFSET`, and direct mask tests rely on these shift/mask names being exact.

Important register groups in this range include:

- `SPI_SHADER_USER_DATA_VS_0` through `SPI_SHADER_USER_DATA_VS_31`, `SPI_SHADER_USER_DATA_ES_0` through `SPI_SHADER_USER_DATA_ES_31`, `SPI_SHADER_USER_DATA_LS_0` through `SPI_SHADER_USER_DATA_LS_31`, `SPI_SHADER_USER_DATA_COMMON_0` through `SPI_SHADER_USER_DATA_COMMON_31`, and `COMPUTE_USER_DATA_0` through `COMPUTE_USER_DATA_15`: full-width user-data payload registers passed to shader stages or compute dispatches.
- `SPI_SHADER_PGM_LO_*` and `SPI_SHADER_PGM_HI_*` for ES, GS, LS, and HS: low and high fragments of shader program base addresses. The high fragments in this chunk expose 8-bit `MEM_BASE` fields.
- `SPI_SHADER_PGM_RSRC1_GS` and `SPI_SHADER_PGM_RSRC1_HS`: shader resource fields for VGPR/SGPR allocation, priority, floating-point mode, privilege, DX10 clamp, debug/IEEE modes, CU group enable, component count, CDBG user bit, and FP16 overflow behavior.
- `SPI_SHADER_PGM_RSRC2_GS_VS`, `SPI_SHADER_PGM_RSRC2_GS`, and `SPI_SHADER_PGM_RSRC2_HS`: scratch enable, user SGPR count, trap presence, exception enables, LDS sizing, on-chip LDS enable, user SGPR skipping, and high-bit SGPR count fields. GS variants also encode GS/ES or GS/VS VGPR component-count details.
- `SPI_SHADER_PGM_RSRC3_GS` and `SPI_SHADER_PGM_RSRC3_HS`: CU enable, wave limit, lock-low threshold, and SIMD disable fields. The GS layout places `CU_EN` in low bits, while HS places wave/lock/SIMD fields in low bits and `CU_EN` in the high half.
- `SPI_SHADER_PGM_RSRC4_GS` and `SPI_SHADER_PGM_RSRC4_HS`: late allocation and FIFO-depth style controls, including GS group FIFO depth and shader late allocation.
- `COMPUTE_DISPATCH_INITIATOR`, `COMPUTE_DIM_X/Y/Z`, `COMPUTE_START_X/Y/Z`, `COMPUTE_NUM_THREAD_X/Y/Z`, and `COMPUTE_RESTART_X/Y/Z`: compute dispatch dimensions, offsets, thread-group sizes, restart coordinates, and initiation flags such as order mode, thread tracing, force-start, compute-shader WAVES, and ordered append-enable bits.
- `COMPUTE_PGM_LO`, `COMPUTE_PGM_HI`, `COMPUTE_DISPATCH_PKT_ADDR_*`, `COMPUTE_DISPATCH_SCRATCH_BASE_*`, `COMPUTE_WAVE_RESTORE_ADDR_*`: compute program, packet, scratch, and wave-restore address fields.
- `COMPUTE_PGM_RSRC1` and `COMPUTE_PGM_RSRC2`: compute shader resource allocation and behavior fields, including VGPRs, SGPRs, priority, float mode, private/debug/IEEE bits, bulk VGPR fields, scratch, user SGPRs, trap, TGID enable bits, LDS size, TIDIG component count, exception enables, TG size enable, and temporary ring enable.
- `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE0` through `SE3`, and `COMPUTE_TMPRING_SIZE`: CU masking, wave limits, SIMD distribution, per-SE static thread management, and scratch wave/item sizing.
- `COMPUTE_THREAD_TRACE_ENABLE`, `COMPUTE_MISC_RESERVED`, `COMPUTE_DISPATCH_ID`, `COMPUTE_THREADGROUP_ID`, `COMPUTE_RELAUNCH`, and `COMPUTE_NOWHERE`: debug/trace, dispatch identification, threadgroup tracking, relaunch, and sink-register fields.
- `CP_DFY_*`: command-processor deferred-write/data-fabric address, data, control, status, and command fields.
- `CPC_INT_INFO`, `CPC_INT_ADDR`, `CPC_INT_PASID`, `CPC_INT_CNTL`, `CPC_INT_STATUS`, and `CPC_INT_CNTX_ID`: CPC interrupt context, ring ID, VMID, PASID, and interrupt enable/status fields.
- `CP_GFX_ERROR`, `CPG_UTCL1_CNTL`, `CPC_UTCL1_CNTL`, `CPF_UTCL1_CNTL`, `CPG_UTCL1_ERROR`, `CPC_UTCL1_ERROR`, and the `gc_cppdec2` `*_UTCL1_STATUS` registers: CP-side GPU virtual memory, retry, PRT, fault, no-execute, snoop, invalidate, and halt/error reporting.
- `CP_RB0_BASE`, `CP_RB_BASE`, `CP_RB1_BASE`, `CP_RB2_BASE`, their `_HI`, `_CNTL`, read-pointer-address, write-pointer, buffer-size, active, and VMID registers: graphics ring-buffer placement, sizing, cache policy, pointer update, and activity state.
- `CP_RB_DOORBELL_CONTROL`, `CP_RB_DOORBELL_RANGE_LOWER/UPPER`, `CP_MEC_DOORBELL_RANGE_LOWER/UPPER`, `CP_RB_DOORBELL_CONTROL_SCH_0` through `SCH_7`, and `CP_RB_DOORBELL_CLEAR`: doorbell offset, enable, hit, BIF drop, valid-range, scheduler queue, and clear fields.
- `CP_INT_CNTL`, `CP_INT_STATUS`, `CP_INT_CNTL_RING0/1/2`, `CP_INT_STATUS_RING0/1/2`, `CP_ME1_PIPE*_INT_CNTL/STATUS`, `CP_ME2_PIPE*_INT_CNTL/STATUS`, `CP_ME1_INT_STAT_DEBUG`, and `CP_ME2_INT_STAT_DEBUG`: command-processor interrupt enable/status bitmaps for timestamp, opcode, privilege, reserved-bit, GPF, ECC, queue/dequeue, query, context, generic, and idle/busy events.
- `CP_ME*_PIPE_PRIORITY_CNTS`, `CP_RING_PRIORITY_CNTS`, `CP_ME*_PIPE*_PRIORITY`, and `CP_RING*_PRIORITY`: ring and pipe priority counters and priority selectors.
- `CP_FATAL_ERROR`, `CP_PWR_CNTL`, `CP_MEM_SLP_CNTL`, `CP_ECC_FIRSTOCCURRENCE*`, `GB_EDC_MODE`, `CC_GC_EDC_CONFIG`, `CP_CPF_DEBUG`, `CP_PQ_WPTR_POLL_CNTL*`: fatal-error gating, power/sleep controls, ECC capture, EDC configuration, CPF debug, and write-pointer polling controls.
- `CP_CE_PRGRM_CNTR_START`, `CP_PFP_PRGRM_CNTR_START`, `CP_ME_PRGRM_CNTR_START`, `CP_MEC1_PRGRM_CNTR_START`, `CP_MEC2_PRGRM_CNTR_START`, and the matching interrupt-routine start registers: micro-engine program-counter and interrupt entry-point address fields.
- `CP_CONTEXT_CNTL`, `CP_MAX_CONTEXT`, `CP_IQ_WAIT_TIME1/2`, `CP_VMID_RESET`, `CP_VMID_PREEMPT`, `CP_VMID_STATUS`, `CP_PQ_STATUS`, and `CP_CPC_IC_*`: context-switching, queue/preemption, VMID reset/status, PQ status, and CPC instruction-cache base/control/operation fields.
- `CP_MEC1_F32_INT_DIS` and `CP_MEC2_F32_INT_DIS`: disable bits for MEC fatal/interrupt sources such as EDC ROQ/TC/GDS/scratch/DMA/SR memory errors, privilege/reserved-bit errors, wave restore, SUA violation, IQ timer, GPF CPF/DMA/CPC, queue message, and fatal EDC error.
- `CP_GFX_MQD_CONTROL`, `CP_GFX_MQD_BASE_ADDR`, `CP_GFX_MQD_BASE_ADDR_HI`, `CP_RB_STATUS`, and `CP_SD_CNTL`: scheduler/graphics MQD VMID and execution/cache policy, MQD base address, ring doorbell status, and CP sub-block enable bits for CPF, CPG, CPC, RLC, SPI, WD, IA, PA, RMI, and EA.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Include the GC 9.0 register offset and shift/mask headers for a GFX9 ASIC.
2. Select a hardware register address such as `mmCP_INT_CNTL_RING0`, `mmCP_RB_DOORBELL_CONTROL`, or a compute/shader register from the offset header.
3. Use this file's shift/mask macros, usually through `REG_SET_FIELD` or `REG_GET_FIELD`, to compose or decode a register value.
4. Read or write the register through MMIO, RLC-safe accessors, KFD queue-loading paths, command-stream programming, debugfs/register dump code, firmware setup, reset flows, or power-management sequences.

Representative GFX9 consumers show the pattern: `gfx_v9_0_enable_gui_idle_interrupt()` reads `mmCP_INT_CNTL_RING0`, sets `CNTX_BUSY_INT_ENABLE`, `CNTX_EMPTY_INT_ENABLE`, `CMP_BUSY_INT_ENABLE`, and sometimes `GFX_IDLE_INT_ENABLE`, then writes the register back. `gfx_v9_0` ring setup programs `mmCP_RB_DOORBELL_CONTROL` by writing `DOORBELL_OFFSET` and `DOORBELL_EN`, then programs the lower and upper doorbell ranges. KFD MQD setup uses compute and CP queue masks such as `COMPUTE_PGM_RSRC2__TRAP_PRESENT__SHIFT`, `COMPUTE_RESOURCE_LIMITS__FORCE_SIMD_DIST_MASK`, and HQD/doorbell fields from the same generated header family.

Ordering requirements are outside this file. For example, programming a ring buffer requires memory allocation, write-pointer backing storage, base address writes, buffer-size control, doorbell range setup, and enable sequencing in driver code. This header only names the bits used by those sequences.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state:

- Shader program, resource, and user-data registers are context/programming state for graphics shader stages. Values persist in the relevant hardware context until rewritten, context-switched, reset, or power-gated. User-data registers are full 32-bit payloads whose interpretation depends on shader ABI and command-stream setup.
- Compute dispatch and program-resource registers are per-dispatch or queue/context state. Dimensions, start/restart coordinates, dispatch IDs, scratch bases, wave-restore addresses, resource limits, static thread-management masks, and user data are live state consumed by compute scheduling and shader execution.
- CP ring-buffer base/control, read-pointer, write-pointer, buffer-size, polling, active, priority, and VMID fields are persistent queue-management state until the driver reprograms the ring, disables it, resets CP, or the GPU loses state.
- Doorbell enable, offset, hit, range, and scheduler-control bits are hardware interface state shared with CPU-visible doorbell writes. `HIT` and status-like fields may be set asynchronously by hardware when doorbells arrive.
- CP interrupt enable fields are persistent masks until changed or reset; status fields represent live or sticky hardware events depending on the specific register semantics. This header does not state whether a bit is write-one-to-clear, clear-on-read, sticky, or level-sensitive.
- UTCL1 error/status registers expose GPU virtual memory, retry, and PRT events from CP sub-blocks. Status can change asynchronously with memory traffic and fault handling.
- ECC, EDC, fatal-error, and first-occurrence fields expose error capture and error-routing state. Incorrect writes can suppress critical error reporting or leave stale captured state.
- Program-counter and interrupt-routine start registers configure CP micro-engine execution surfaces and persist until microcode reload, CP reset, or driver/firmware reprogramming.
- `CP_SD_CNTL` enables or disables major command-processor sub-blocks; these bits are high-impact persistent controls rather than passive status.

Reserved or undocumented fields appear throughout this generated range. Callers should preserve reserved bits during read-modify-write unless the hardware programming guide provides a full-register value.

## Dependencies And Integration Points

Primary dependencies:

- The matching GC 9.0 offset header supplies register addresses; this file supplies only bit layout.
- AMDGPU's common register-field helpers depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` spelling.
- The generated values must remain synchronized with AMD's GC 9.0 register database and the actual ASIC stepping targeted by the including driver path.

Integration points in this repository include:

- `amdgpu/gfx_v9_0.c`: core GFX9 graphics-ring setup, CP interrupt toggling, GUI idle interrupt handling, ring buffer and doorbell programming, reset/resume paths, and register access through `RREG32_SOC15`/`WREG32_SOC15`.
- `amdgpu/amdgpu_amdkfd_gfx_v9.c` and `amdkfd/kfd_mqd_manager_v9.c`: KFD queue/MQD setup, compute queue doorbells, HQD loading, compute trap/user-resource setup, resource limits, and force-SIMD-distribution policy.
- `amdgpu/soc15.c`, `gmc_v9_0.c`, and `gfxhub_v1_0.c`: SOC15/GFX9 initialization and memory-management paths that include the same generated masks for VM/fault/status handling.
- `amdgpu/mxgpu_ai.c` and `amdgpu/amdgpu_amdkfd_arcturus.c`: virtualization and ASIC-specific GFX9-family paths.
- `pm/powerplay/hwmgr/vega10_inc.h`: Vega10 power-management code that includes GC 9.0 register definitions for graphics-core power/clock interactions.
- Hardware firmware and command processor microcode expectations. CP micro-engine program-counter, interrupt-routine, instruction-cache, ring, and MQD fields must agree with firmware ABI and register database definitions.

## Risks

- Bitfield drift is the main risk. If a shift or mask differs from the hardware register database, `REG_SET_FIELD` can silently program the wrong bits, affecting shader execution, queue scheduling, interrupts, VM fault handling, or doorbell delivery.
- Split chunk boundaries can hide incomplete register definitions. This range begins after part of `SPI_SHADER_PGM_RSRC2_VS` and ends before `CP_SOFT_RESET_CNTL`; merge tooling must combine adjacent chunk research before treating the whole file as covered.
- Full-width user-data and address fields are easy to misuse because the header does not encode address alignment, high/low address composition, GPU virtual-vs-physical address rules, or shader ABI interpretation.
- Doorbell fields are sensitive. Wrong offsets, ranges, or enable bits can make rings fail to wake, receive another queue's doorbell, drop BIF doorbells, or leave stale hit state.
- CP ring-buffer sizing and pointer fields control command fetch. Incorrect buffer-size masks, read/write pointer addresses, cache policy, or no-update bits can cause hangs, lost command processing, or memory corruption.
- Interrupt masks and status fields are high impact. Enabling the wrong interrupt can flood IRQ handling; disabling privilege, opcode, GPF, ECC, EDC, or reserved-bit error reporting can hide hardware or userspace faults.
- VMID, PASID, preemption, and context-control fields cross process isolation boundaries. Misprogramming these fields can attribute faults incorrectly, preempt the wrong context, or break queue isolation.
- `CP_SD_CNTL`, fatal-error, reset, and EDC/ECC controls can alter global graphics-core behavior. They should be changed only inside validated initialization, reset, or recovery flows.
- The generated header lacks type checking. A macro from a similarly named but different ASIC generation or register family can compile while programming an incompatible bit layout.

## Test Signals

Useful validation signals for changes touching this area include:

- Build coverage for GFX9 AMDGPU/KFD paths with this header included, catching missing or renamed generated macros at compile time.
- Boot or module-load logs for GFX9 ASICs such as Vega, Raven, or Arcturus showing successful graphics and KFD initialization without CP, RLC, ring, VM, or firmware errors.
- Graphics ring tests that submit command buffers and verify fences, write pointers, read pointers, timestamp interrupts, and GUI idle interrupt behavior.
- KFD compute queue tests that create/destroy queues, ring doorbells, dispatch kernels, exercise trap-present and resource-limit paths, and validate MQD/HQD programming.
- Doorbell tests or diagnostics that confirm configured doorbell offsets/ranges match ring and queue indices and that doorbell-hit/status bits behave as expected.
- GPU VM fault tests that exercise CPG/CPC/CPF UTCL1 fault, retry, PRT, PASID, and VMID reporting without corrupting unrelated queue state.
- Suspend/resume, GPU reset, and hang-recovery tests, because ring buffer, CP context, interrupt masks, doorbells, and shader/compute state must be reprogrammed correctly after state loss.
- Error-injection or RAS tests for ECC/EDC/fatal-error paths, especially first-occurrence and MEC F32 interrupt-disable fields.
- Register-dump/debugfs checks comparing programmed CP ring, interrupt, VMID, and doorbell fields against expected decoded values from `REG_GET_FIELD`.
