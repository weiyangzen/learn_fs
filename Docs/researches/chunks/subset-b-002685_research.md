# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_3_sh_mask.h lines 1-2410

## Purpose

This chunk is the opening generated register field mask/shift header for AMD GC 9.4.3 graphics-core registers. It starts the include guard for `gc_9_4_3_sh_mask.h` and defines 2,172 preprocessor constants for 204 register blocks through line 2410.

The chunk covers these address blocks:

- `xcd0_gc_grbmdec`: graphics register bus manager status, error reporting, soft reset, trap, scratch, RSMU, IOV, fence, UTCL2 invalidation, and power-control field definitions.
- `xcd0_gc_cpdec`: command processor, CPF, CPC, MEC, queue, ring-buffer, read/write pointer, stalled/busy status, interrupt-debug, debug-bus, and privilege-violation field definitions.
- `xcd0_gc_padec`: primitive assembler, VGT, IA, WD, PA/SC/CL/SU, binning/event, UTCL1, shader-array, primitive config, and front-end pipeline tuning fields.
- The beginning of `xcd0_gc_sqdec`: SQ, SQC, LDS, SH memory, shader-rate, debug, interrupt, UTCL1, cache, clock-gating, timeout, and MFMA configuration fields.

The final line of the chunk is intentionally mid-register: line 2410 ends at `SQ_UTCL1_CNTL2__SHOOTDOWN_OPT_MASK`; the remaining `SQ_UTCL1_CNTL2` masks and later SQ fields are outside this work item.

## Important APIs, Types, And Data

This header defines no functions, structs, enums, global variables, or storage. Its public API is a generated preprocessor namespace with two constants per hardware field:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift amount for extracting or inserting the field.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.

Important groups in this chunk include:

- GRBM status and control macros such as `GRBM_STATUS__GUI_ACTIVE_MASK`, `GRBM_STATUS2__CPAXI_BUSY_MASK`, `GRBM_SOFT_RESET__SOFT_RESET_*_MASK`, `GRBM_READ_ERROR*`, `GRBM_WRITE_ERROR`, `GRBM_IOV_ERROR`, `GRBM_RSMU_READ_ERROR`, and `GRBM_GFX_CNTL` queue-selection fields.
- CP/CPC/CPF/MEC macros for scheduler and queue observability: `CP_CPC_STATUS`, `CP_CPC_BUSY_STAT`, `CP_CPC_STALLED_STAT1`, `CP_CPF_STATUS`, `CP_CPF_BUSY_STAT`, `CP_STALLED_STAT1/2/3`, `CP_BUSY_STAT`, `CP_STAT`, `CP_GRBM_FREE_COUNT`, ring/queue availability and pointer fields, command-index/data fields, interrupt debug bits, and ME/MEC halt, step, reset, and icache invalidation bits.
- PA/VGT/WD/IA front-end macros for primitive flow and raster/binning behavior: `VGT_CACHE_INVALIDATION`, `VGT_DMA_CONTROL`, `VGT_CNTL_STATUS`, `IA_CNTL_STATUS`, `WD_CNTL_STATUS`, `PA_CL_ENHANCE`, `PA_SC_BINNER_EVENT_CNTL_0` through `_3`, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_ENHANCE_2`, FIFO sizing, and UTCL1 invalidation/control fields.
- SQ/SQC/LDS/SH macros for shader core behavior: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_DSM_CNTL*`, `SQ_DEBUG_STS_GLOBAL*`, `SH_MEM_BASES`, `SH_MEM_CONFIG`, `SH_CAC_CONFIG`, `SQ_TIMEOUT_CONFIG/STATUS`, shader-rate configuration, interrupt controls, and `SQ_UTCL1_CNTL1` plus the first part of `SQ_UTCL1_CNTL2`.

These constants are normally used with AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, masked register writes, and debug register dumps. The companion `gc_9_4_3_offset.h` supplies register addresses; this file supplies field placement inside each 32-bit register.

## Control Flow

There is no executable control flow. Compile-time inclusion makes symbolic field layouts available to C code that reads or writes GC 9.4.3 registers.

Runtime flow is created by consumers. Typical patterns are:

- Read a register via MMIO or indexed register access, then extract a field with the matching mask and shift.
- Build a new register value by clearing a mask and inserting a shifted field value.
- Poll busy/status bits from `GRBM_STATUS*`, `CP_*_STATUS`, `IA_CNTL_STATUS`, `VGT_CNTL_STATUS`, `WD_CNTL_STATUS`, or `SQ_DEBUG_STS_GLOBAL*` before reset, suspend, mode changes, or fault handling.
- Write reset, halt, invalidate, queue-threshold, timeout, binning, or UTCL1 control bits during initialization, bring-up, debug, or recovery paths.

Since this is register metadata, branch behavior and sequencing requirements live in callers and hardware documentation, not in the header itself.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe volatile GPU hardware state:

- Status and busy fields reflect live hardware state and can change between reads.
- Reset, halt, invalidate, bypass, force-miss, clock-gating, timeout, and debug fields are control state held in hardware registers until overwritten, reset, or lost through power/reset transitions.
- Error registers such as GRBM read/write/IOV/RSMU error fields and UTCL1 fault/retry/PRT status fields expose latched or sampled hardware fault state depending on the register semantics enforced by the hardware block.
- Scratch and dump fields (`GRBM_SCRATCH_REG*`, `CP_*_HEADER_DUMP`, command data, and related debug fields) are register-backed diagnostic state, not file-system or software persistence.
- Queue, ROQ, STQ, MEQ, CEQ, ring pointer, FIFO, and credit fields expose transient command processor occupancy and flow-control state.

No persistent on-disk state, firmware blob management, or software cache is implemented here.

## Dependencies

The chunk depends on generated AMD ASIC register metadata being synchronized with GC 9.4.3 hardware:

- `gc_9_4_3_offset.h` provides the register offsets for these field definitions.
- AMDGPU's register manipulation helpers consume the `*_SHIFT` and `*_MASK` naming convention.
- Driver code under `drivers/gpu/drm/amd/` must include the GC 9.4.3 headers only for compatible ASICs; similar register names in other GC generations can have different field layouts.
- Hardware/firmware initialization code, reset paths, power-management code, queue scheduling, GPUVM invalidation, and diagnostics rely on these masks matching the silicon.

The header has no direct include dependencies in this chunk beyond its own include guard, but incorrect generation or stale synchronization with the offset/default headers would break consumers at compile time or, worse, misprogram hardware at runtime.

## Integration Points

Primary integration points are AMDGPU's GC 9.4.3 support paths:

- GPU reset and idle-detection paths using GRBM busy, clean, active, read/write-error, and soft-reset masks.
- Command processor bring-up, halt/step/debug, queue setup, and recovery code using CP, CPF, CPC, MEC, ring-buffer, ROQ/STQ/MEQ/CEQ, stalled-stat, and interrupt-debug masks.
- Graphics front-end initialization and diagnostics using VGT, IA, WD, PA/CL/SC/SU, primitive config, shader-array config, binning-event, FIFO, and UTCL1 masks.
- Shader-core initialization, debug, ECC/error-injection, timeout, cache, memory-base/config, interrupt, performance-trap, and UTCL1 invalidation paths using SQ/SQC/LDS/SH masks.
- Debugfs, register dump, fault decoding, and bring-up scripts that decode raw register values into named fields.

The source path places this file in the distributed Ceph client's vendored Linux AMDGPU tree. It is not Ceph filesystem logic itself; it is low-level GPU driver register metadata carried by that source tree.

## Risks

- A wrong mask or shift can silently corrupt unrelated bits in a hardware register, which is especially dangerous for reset, halt, invalidate, clock-gating, memory-translation, and privilege/error registers.
- Cross-generation reuse is unsafe. GC 9.4.3 names overlap with other `gc_*_sh_mask.h` files, but field widths and positions may differ.
- The chunk boundary splits `SQ_UTCL1_CNTL2`; analysis or generated consumers must not assume line 2410 contains the complete register definition.
- Many status bits are transient. Poll loops that read GRBM, CP, PA/VGT, or SQ status must handle races, timeouts, and hardware blocks entering or leaving busy state between reads.
- Debug, DSM, error-injection, force-miss, force-snoop, bypass, and clock-gating fields can significantly alter execution behavior or performance if written outside controlled bring-up/debug flows.
- Reserved and spare fields appear in several registers. Callers should preserve unknown bits unless hardware documentation explicitly requires a value.
- Error and fault fields include VF/VMID/VFID/TMZ/privilege information; incorrect decoding can misattribute virtualization or memory-protection failures.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage of AMDGPU GC 9.4.3 code that includes `gc_9_4_3_sh_mask.h` alongside `gc_9_4_3_offset.h`.
- Static checks that every field in lines 1-2410 has a paired `SHIFT` and `MASK`, except where the chunk boundary intentionally cuts off the rest of `SQ_UTCL1_CNTL2`.
- Cross-header consistency checks against generated offset/default headers and neighboring GC 9.4.x headers for expected register families.
- Runtime smoke tests on matching GC 9.4.3 hardware that exercise GPU reset, command submission, queue setup, suspend/resume, GPUVM invalidation, and fault reporting without invalid-register or timeout errors.
- Register dump or debugfs checks that decode GRBM/CP/PA/SQ busy and fault bits into plausible names under idle and load.
- Fault-injection or recovery tests that verify GRBM read/write errors, CP privilege violations, UTCL1 fault/retry/PRT status, timeout status, and CP interrupt-debug bits decode correctly.
