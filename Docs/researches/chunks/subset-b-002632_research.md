# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 1-2407

## Scope

This chunk covers the opening 2,407 lines of the generated AMD GC 9.1 shader/register mask header. It includes the license guard and the beginning of the GC 9.1 register-field catalog: `gc_grbmdec`, `gc_cpdec`, `gc_padec`, and the first part of `gc_sqdec`. The range contains 2,173 `#define` macros for 203 register names, almost entirely paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

The chunk starts at the beginning of the file and ends in the middle of `SQC_EDC_CNT2`, so merge-time reconciliation should combine it with later chunks for the complete GC 9.1 header view.

## Purpose

`gc_9_1_sh_mask.h` provides compile-time bitfield metadata for programming Graphics Core 9.1 registers in the AMDGPU driver. It does not define register addresses; instead it complements generated offset headers such as `gc_9_1_offset.h` by naming each field's shift and mask. Driver code can then use raw C bit operations or helper macros such as `REG_SET_FIELD()` and `REG_GET_FIELD()` to construct, update, and decode 32-bit MMIO register values without embedding magic bit positions.

The covered range focuses on front-end graphics control and diagnostics:

- `gc_grbmdec` describes GRBM global graphics register bus management fields: global/SE busy status, read/write/IOV errors, soft reset bits, trap registers, scratch registers, power request controls, and UTCL2 invalidation ranges.
- `gc_cpdec` describes command processor status and control: CPC/CPF busy and stall signals, MEC/ME reset/halt/step controls, command/ring/queue FIFO thresholds and pointer status, PRT LOD statistics controls, and command-index/data access.
- `gc_padec` describes primitive assembly, vertex generation, input assembler, work distributor, primitive/rasterizer binner, PA/SC enhancement, UTCL1 control/status, and shader-array or primitive-configuration masks.
- `gc_sqdec` begins shader core metadata: SQ/SQC configuration, LDS behavior, wave priority, register credits, FIFO sizes, DSM/error-injection controls, shader memory base/config registers, SQ UTCL1 controls, shader TBA/TMA address fields, and SQC EDC/FUE counters.

## Important API Surface

The public surface is the macro namespace, not C functions or structs. The naming contract is `REGISTER__FIELD__SHIFT` for the bit position and `REGISTER__FIELD_MASK` for the already-shifted mask. Consumers must pair these names with matching `mmREGISTER` offsets from the same ASIC generation.

- GRBM status and reset macros include `GRBM_STATUS`, `GRBM_STATUS2`, `GRBM_STATUS_SE0` through `GRBM_STATUS_SE3`, and `GRBM_SOFT_RESET`. These are used to determine which graphics blocks are busy and which blocks need reset, including CP, RLC, GFX, CPF, CPC, CPG, CAC, CPAXI, and EA.
- GRBM error, trap, and virtualization macros include `GRBM_READ_ERROR`, `GRBM_READ_ERROR2`, `GRBM_WRITE_ERROR`, `GRBM_IOV_ERROR`, `GRBM_INT_CNTL`, `GRBM_TRAP_*`, `GRBM_RSMU_READ_ERROR`, and `GRBM_RSMU_CFG`. These decode faulty read/write requesters, ME/pipe/VM/VF identity, interrupt enables, and debug trap data.
- GRBM targeting and scratch macros include `GRBM_GFX_CNTL`, `GRBM_IH_CREDIT`, `GRBM_UTCL2_INVAL_RANGE_START/END`, `GRBM_NOWHERE`, and `GRBM_SCRATCH_REG0` through `GRBM_SCRATCH_REG7`. These support queue targeting, interrupt-handler credit programming, invalidation range selection, and scratch-based register-access tests.
- CP status and diagnostic macros include `CP_CPC_STATUS`, `CP_CPC_BUSY_STAT`, `CP_CPC_STALLED_STAT1`, `CP_CPF_STATUS`, `CP_CPF_BUSY_STAT`, `CP_CPF_STALLED_STAT1`, `CP_STALLED_STAT1/2/3`, `CP_BUSY_STAT`, and `CP_STAT`. They expose fine-grained command processor stalls across MEC, CPF, CPC, PFP, ME, CE, queues, semaphores, TC/UTCL, stream-out, append, and surface-sync paths.
- CP control and queue macros include `CP_MEC_CNTL`, `CP_ME_CNTL`, `CP_*_HEADER_DUMP`, `CP_*_INSTR_PNTR`, `CP_GRBM_FREE_COUNT`, `CP_CPC_GRBM_FREE_COUNT`, `CP_CPF_GRBM_FREE_COUNT`, `CP_CNTX_STAT`, `CP_ME_PREEMPTION`, `CP_ROQ_*`, `CP_STQ_*`, `CP_MEQ_*`, `CP_CEQ*`, `CP_RB*_RPTR`, `CP_RB_WPTR_*`, `CP_CMD_INDEX`, and `CP_CMD_DATA`. These define micro-engine reset/halt/step bits, instruction/header dump fields, ring/queue thresholds, read/write pointers, and indirect command-register access.
- PA/VGT/IA/WD macros include `VGT_*`, `IA_CNTL_STATUS`, `WD_CNTL_STATUS`, `WD_QOS`, `WD_UTCL1_*`, `IA_UTCL1_*`, `GFX_PIPE_CONTROL`, `VGT_DMA_*`, `WD_BUF_RESOURCE_*`, and shader-array/primitive configuration registers. These describe primitive grouping, DMA FIFO sizing, cache invalidation, wave IDs, inactive CUs, UTCL1 fault/retry/PRT state, and draw/input-assembler work distribution.
- PA/SC binner and raster controls include `PA_CL_*`, `PA_SU_CNTL_STATUS`, `PA_SC_FIFO_*`, `PA_SC_FORCE_EOV_MAX_CNTS`, `PA_SC_BINNER_EVENT_CNTL_0` through `_3`, `PA_SC_BINNER_TIMEOUT_COUNTER`, `PA_SC_BINNER_PERF_CNTL_*`, `PA_SC_PKR_WAVE_TABLE_CNTL`, `PA_UTCL1_CNTL1/2`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_DSM_CNTL`, and `PA_SC_TILE_STEERING_CREST_OVERRIDE`.
- SQ/SQC macros include `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQ_REG_CREDITS`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL`, `SQ_DSM_CNTL2`, `SQ_RUNTIME_CONFIG`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `CC_GC_SHADER_RATE_CONFIG`, `GC_USER_SHADER_RATE_CONFIG`, `SQ_INTERRUPT_*`, `SQ_UTCL1_CNTL1/2`, `SQ_UTCL1_STATUS`, `SQ_SHADER_TBA/TMA_LO/HI`, `SQC_DSM_CNTL*`, `SQC_EDC_FUE_CNTL`, and the start of `SQC_EDC_CNT2`.

## Control Flow

There is no executable control flow in this header. Runtime behavior appears when AMDGPU code reads or writes a matching register and applies these constants. A typical pattern is:

1. Read a register with an MMIO helper such as `RREG32_SOC15(GC, instance, mmREGISTER)`, or start from zero when constructing a value.
2. Extract a field with `REG_GET_FIELD(value, REGISTER, FIELD)`, or test a condition with `value & REGISTER__FIELD_MASK`.
3. Insert a field with `REG_SET_FIELD(value, REGISTER, FIELD, new_value)`, which relies on the matching `__SHIFT` and `_MASK` constants.
4. Write the result to the matching `mmREGISTER` offset with a SOC15/MMIO write helper.

The GFX 9 driver follows this pattern around GRBM soft reset: `gfx_v9_0_soft_reset()` reads `mmGRBM_STATUS` and `mmGRBM_STATUS2`, tests fields such as `GRBM_STATUS__PA_BUSY_MASK`, `GRBM_STATUS__CP_BUSY_MASK`, and `GRBM_STATUS2.RLC_BUSY`, then sets `GRBM_SOFT_RESET` fields before issuing reset sequencing. Although this particular source file includes the GC 9.0 mask header, it demonstrates the integration contract shared by the GC 9.x generated mask families. GC 9.1-specific consumers must use the GC 9.1 offset/mask pair.

## State and Persistence

The macros are stateless preprocessor constants. The state they describe lives in GPU hardware registers and can persist until changed by driver initialization, ring setup, command submission, context switch restore, power/reset handling, or full device reset.

- GRBM status and error registers are mostly read/diagnostic state. Their fields reveal live block activity, request queues, read/write faults, requester identity, VF/VM attribution, and interrupt causes.
- GRBM reset, clock, power, trap, UTCL2, and scratch registers are mutable control state. Wrong writes can halt traffic, invalidate the wrong address range, hide errors, or disrupt debug/trap behavior.
- CP queue/ring threshold, pointer, halt, step, reset, and preemption registers control command processor progress and diagnostics. They are tightly coupled to graphics and compute ring setup.
- PA/VGT/IA/WD and PA/SC registers represent persistent graphics-pipeline configuration: primitive assembly, DMA/invalidation behavior, inactive hardware masks, rasterizer/binning behavior, UTCL1 translation controls, and fault status.
- SQ/SQC registers represent shader-core configuration and diagnostics: cache sizing/behavior, LDS reporting, wave priority, register-credit state, shader memory aperture layout, trap handler address fields, UTCL1 invalidation/status, error injection, and EDC/FUE counters.

Because these constants define the bit layout, persistence risk comes from consumers using the wrong mask generation for the running ASIC, mixing `gc_9_1_*` offsets with another generation's masks, or treating reserved/workaround fields as stable public configuration knobs.

## Dependencies and Integration Points

- Depends on AMD's generated GC 9.1 register specification. The shift/mask pairs must stay synchronized with `gc_9_1_offset.h` and any GC 9.1 default/value headers used by initialization and golden-register paths.
- Integrates with AMDGPU SOC15 register access helpers in `drivers/gpu/drm/amd/amdgpu`, especially code that uses `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, indirect SQ register helpers, ring initialization, reset handling, and debug/register-dump paths.
- Integrates with PSP and ASIC-specific initialization code when GC 9.1 offsets are included for firmware or security processor register programming.
- Provides a decode contract for debugging tools and logs: raw register dumps can be mapped back to busy, stall, fault, queue, and control fields using these masks.
- Shares macro names with neighboring GC 9.x headers. That consistency helps common driver code but also makes include-order and ASIC-selection correctness important.

## Risks

- Bitfield drift is the main correctness risk. A wrong shift or mask can silently program an unrelated field, especially in reset, halt, trap, virtualization, UTCL invalidation, or shader memory configuration registers.
- The file is generated-style and untyped. C compilation catches missing macro names but cannot catch using `REGISTER_A__FIELD_MASK` with `REGISTER_B`, or pairing a GC 9.1 field layout with a GC 9.0/9.2/9.4 register address.
- Busy/reset fields have high blast radius. Misinterpreting `GRBM_STATUS*` can cause unnecessary resets or missed resets; misprogramming `GRBM_SOFT_RESET`, `CP_ME_CNTL`, or `CP_MEC_CNTL` can leave engines halted, stepped, or reset.
- Queue/ring pointer and threshold fields are sensitive to off-by-one and width mistakes. Incorrect `CP_ROQ_*`, `CP_STQ_*`, `CP_MEQ_*`, `CP_RB*`, or `CP_CEQ*` usage can wedge command submission.
- Fault and virtualization fields must be decoded accurately. `GRBM_IOV_ERROR`, `GRBM_WRITE_ERROR`, `GRBM_RSMU_READ_ERROR`, and UTCL1 status fields carry VF/VM/requester information used for diagnosis and isolation.
- Enhancement, DSM, and error-injection fields are hardware-specific. Accidentally enabling `*_DSM_*`, `*_ENABLE_ERROR_INJECT`, or reserved PA/SC/SQ controls outside intended test paths can create hangs or hard-to-reproduce corruption.
- This chunk ends mid-register at `SQC_EDC_CNT2`; downstream documentation must not treat the partial tail as the complete SQC EDC counter surface.

## Test Signals

- Build signal: compile the AMDGPU driver with the generated GC 9.1 headers; missing/duplicate definitions or syntax drift will fail immediately.
- Generation consistency: compare this header against the authoritative GC 9.1 register source and `gc_9_1_offset.h` to verify every field mask matches its documented bit range and every field belongs to the expected register.
- Reset/idle smoke tests: boot a GC 9.1 ASIC or emulator, exercise graphics and compute rings, and confirm GRBM/CP idle polling, soft reset, and RLC stop/start paths do not time out.
- Register decode validation: capture `GRBM_STATUS`, `GRBM_STATUS2`, CP busy/stall registers, PA/VGT/IA/WD status, and SQ/SQC status under known workloads; verify decoded fields match expected active blocks.
- Graphics conformance: Vulkan/OpenGL CTS and stress workloads covering draw dispatch, primitive assembly, streamout, binning, cache invalidation, preemption, shader scratch/trap setup, and VM fault handling exercise many of these fields indirectly.
- Fault-path tests: controlled VM faults, VF/VM isolation tests, and RAS/EDC diagnostics should produce decodable `GRBM_*ERROR`, UTCL1 status, SQC EDC/FUE, and CP stall information without misattribution.
