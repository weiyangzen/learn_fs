<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a5xx.xml -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a5xx.xml

### Purpose
`a5xx.xml` is the rnndb register database for Qualcomm Adreno A5xx GPUs in the MSM DRM driver. It is not executable code; it is the source definition used by `drivers/gpu/drm/msm/registers/gen_header.py` to generate `generated/a5xx.xml.h`. Kernel A5xx code then includes that generated header and uses its `REG_A5XX_*`, packet-field, enum, and bit-mask macros for command processor setup, power management, preemption, debugfs, fault handling, performance counters, rendering state, and descriptor programming.

The file imports `freedreno_copyright.xml`, `adreno/adreno_common.xml`, and `adreno/adreno_pm4.xml`, then defines A5xx-specific formats, performance-counter selectors, the main `A5XX` register domain, and descriptor domains for texture samplers, texture constants, SSBO/image state, and UBO state.

### Important APIs, Types, And Functions
The public API surface is generated C preprocessor data rather than functions.

Key top-level enums include `a5xx_color_fmt`, `a5xx_tile_mode`, `a5xx_vtx_fmt`, `a5xx_tex_fmt`, `a5xx_depth_format`, and `a5xx_blit_buf`. These encode color/render-target formats, tiling modes, vertex attribute formats, texture formats including compressed ETC/DXT/RGTC/BPTC/ASTC cases, depth formats, and blit source selections.

Performance-counter selector enums cover the main GPU blocks: `a5xx_cp_perfcounter_select`, `a5xx_rbbm_perfcounter_select`, `a5xx_pc_perfcounter_select`, `a5xx_vfd_perfcounter_select`, `a5xx_hlsq_perfcounter_select`, `a5xx_vpc_perfcounter_select`, `a5xx_tse_perfcounter_select`, `a5xx_ras_perfcounter_select`, `a5xx_lrz_perfcounter_select`, `a5xx_uche_perfcounter_select`, `a5xx_tp_perfcounter_select`, `a5xx_sp_perfcounter_select`, `a5xx_rb_perfcounter_select`, `a5xx_rb_samples_perfcounter_select`, `a5xx_vsc_perfcounter_select`, `a5xx_ccu_perfcounter_select`, `a5xx_cmp_perfcounter_select`, and `a5xx_vbif_perfcounter_select`. These feed selector registers such as `CP_PERFCTR_CP_SEL_*`, `RBBM_PERFCTR_RBBM_SEL_*`, block-specific `*_PERFCTR_*_SEL_*`, and `VBIF_PERF_CNT_SEL*`.

The `A5XX` domain contains the main register map. Important register groups are:

- CP command processor registers: ring-buffer base/read/write pointer registers, scratch registers, protection registers, microcode debug address/data, indirect-buffer state, context-switch save/restore/SMMU registers, crash-dump registers, CP interrupt/fault status, and CP performance/power counter selectors.
- RBBM registers: debug bus controls, interrupt mask/status/clear, software reset controls, clock-control/hysteresis/delay registers for SP/TP/UCHE/RB/CCU/RAC/TSE/RAS/GPC/VFD/GPMU, always-on counters, global busy status, AHB error/split status, secure-video trust registers, and RBBM performance counters.
- VSC, GRAS, RB, PC, HLSQ, VFD, VPC, UCHE, SP, TPL1, VBIF, GPMU, GDPM, and sensor/power registers, including block address-mode controls, shader state controls, cache/invalidate/trap registers, texture state base registers, power/thermal/leakage/voltage controls, and low-level 2D/blit state.
- Inline bitsets such as `A5XX_INT0`, `A5XX_CP_INT`, `a5xx_gras_xs_cl_cntl`, `a5xx_xs_config`, `a5xx_xs_cntl`, `a5xx_sp_xs_ctrl_reg0`, `a5xx_sp_xs_pvt_mem_param`, `a5xx_sp_xs_pvt_mem_size`, and `a5xx_2d_surf_info`.
- Arrays such as `CP_SCRATCH[8]`, `CP_PROTECT[32]`, `VSC_PIPE_CONFIG[16]`, `VSC_PIPE_DATA_ADDRESS[16]`, `VSC_PIPE_DATA_LENGTH[16]`, `RB_MRT[8]`, `RB_MRT_FLAG_BUFFER[8]`, `VPC_VARYING_INTERP[8]`, `VPC_VARYING_PS_REPL[8]`, `VPC_VAR[4]`, `VPC_SO[4]`, `VFD_FETCH[32]`, `VFD_DECODE[32]`, `VFD_DEST_CNTL[32]`, `SP_VS_OUT[16]`, `SP_VS_VPC_DST[8]`, `SP_FS_OUTPUT[8]`, and `SP_FS_MRT[8]`.

Descriptor domains are separate generated layouts: `A5XX_TEX_SAMP` defines four sampler dwords and nested filter, clamp, and anisotropy enums; `A5XX_TEX_CONST` defines twelve texture descriptor dwords with swizzle/type enums, size, pitch, base address, depth, mip, tiling, and UBWC flag fields; `A5XX_SSBO_0`, `A5XX_SSBO_1`, and `A5XX_SSBO_2` define SSBO/image descriptor pieces; `A5XX_UBO` defines uniform-buffer base-address state.

### Control Flow
Build-time control flow starts in the MSM DRM `Makefile`: `generated/%.xml.h` is produced from `registers/adreno/%.xml` plus the shared Adreno imports, schema, copyright file, and `gen_header.py`; `generated/a5xx.xml.h` is listed in `ADRENO_HEADERS`. Runtime code does not parse this XML. Instead, `a5xx_gpu.h` includes `a5xx.xml.h`, and A5xx driver code compiles against the generated constants.

Runtime use follows the hardware pipeline:

- Initialization and resume code programs generated RBBM clock, reset, VBIF, UCHE, CP, and GPMU register macros from `a5xx_gpu.c` and `a5xx_power.c`.
- Ringbuffer and submission paths use CP ring pointer/base registers plus PM4 packet fields imported from `adreno_pm4.xml`.
- Preemption code writes context-switch save/restore/SMMU registers and ring write pointers using generated `REG_A5XX_CP_*` macros.
- Interrupt handling reads `RBBM_INT_0_STATUS`, masks/clears bits through `RBBM_INT_0_MASK` and `RBBM_INT_CLEAR_CMD`, and decodes CP hardware faults, hang detection, UCHE out-of-bounds/trap conditions, and voltage-droop signals.
- Rendering state programming uses the GRAS/RB/PC/VFD/VPC/SP/HLSQ/TPL1 register and descriptor definitions for binning, rasterization, render targets, depth/stencil, LRZ, stream-out, vertex fetch/decode, shader object addresses, shader private memory, texture/sampler state, and compute dispatch sizes.
- Debug and recovery paths read CP debug queues, RBBM status, always-on counters, crash-dump controls, HLSQ debug aperture registers, and trap/fault logs.

### State, Persistence, And Dependencies
The XML itself is persistent source data under the kernel tree. Its generated output is a build artifact consumed by C code; no runtime persistence is stored in the XML. The hardware state represented by the registers is volatile MMIO/device state, while addresses in many fields point at driver-managed GPU memory such as ringbuffers, firmware/microcode buffers, preemption records, crash-dump buffers, shader binaries, texture/sampler descriptors, render targets, depth/stencil buffers, LRZ buffers, UBWC flag buffers, SSBO/image resources, and UBOs.

Dependencies include the rnndb XML schema (`rules-fd.xsd`), `gen_header.py`, shared Adreno enums/types from `adreno_common.xml`, PM4 packet definitions from `adreno_pm4.xml`, and C consumers under `drivers/gpu/drm/msm/adreno/`. The definitions also depend on hardware contracts for A5xx register offsets, bit encodings, alignment constraints, and address-mode behavior. Several comments are reverse-engineering notes or guesses, so downstream code should treat undocumented fields carefully and verify behavior on real A5xx hardware.

### Integration Points
The primary integration point is `generated/a5xx.xml.h`, included by `adreno/a5xx_gpu.h`. Known consumers include:

- `a5xx_gpu.c` for ring operation, core initialization, clock-control tables, fault/interrupt handling, hang recovery, crash dumps, performance counters, busy-time reads, VBIF halt/reset paths, and status reporting.
- `a5xx_power.c` for GPMU firmware/data RAM, temperature, voltage, leakage, power-counter, GDPM, and throttling registers.
- `a5xx_preempt.c` for CP context-switch and ring-pointer registers.
- `a5xx_debugfs.c` for CP PFP/ME/MEQ/ROQ debug register reads.
- The shared MSM generated-header build flow, which also regenerates other Adreno generation headers and display headers.

The descriptor domains also integrate with userspace-facing GPU command streams indirectly: Mesa/freedreno and kernel driver code must agree on descriptor layouts, register names, and PM4 packet semantics. Any ABI-relevant mismatch can appear as rendering corruption, GPU faults, hangs, or broken performance/debug tooling.

### Risks
Register offset or bitfield mistakes are high impact because they compile into MMIO writes. A wrong `REG_A5XX_*` value can program the wrong block, break reset/power sequencing, corrupt GPU memory pointers, hang the command processor, or prevent fault cleanup.

The file mixes confirmed definitions with comments that explicitly say fields are guessed, unknown, duplicated, or inferred from blob traces. Areas with higher uncertainty include LRZ behavior, UBWC/flag-buffer metadata, separate 2D blit state, stream-out programming details, texture border-color offsets, shader private-memory sizing, and several `UNKNOWN_*` registers.

Format enums are cross-cutting. Incorrect `a5xx_color_fmt`, `a5xx_tex_fmt`, `a5xx_vtx_fmt`, tile-mode, swizzle, pitch-shift, or address-alignment encodings can cause silent rendering corruption rather than immediate probe failures.

Performance-counter selectors and counter registers must match hardware block expectations. Bad selectors may produce misleading profiling data, read stale counters, or disturb perf/power-counter setup.

Interrupt bit definitions are safety-critical for recovery. Incorrect `A5XX_INT0`, `A5XX_CP_INT`, or `RBBM_INT_0_MASK` bits can leave fatal interrupts unhandled, clear the wrong status, or classify recoverable events as hangs.

Generated header churn is a compatibility risk. Since C files include `a5xx.xml.h` directly, renaming registers, bitfields, enums, arrays, or descriptor domains can break builds or silently alter macro names expected by existing code.

### Test Signals
Build signals: regenerate and compile `drivers/gpu/drm/msm` so `generated/a5xx.xml.h` is produced without XML/schema/headergen errors and all A5xx consumers compile against the generated names. A simple source-level signal is that `a5xx_gpu.h` can include the generated header and existing references such as `REG_A5XX_CP_RB_WPTR`, `REG_A5XX_RBBM_INT_0_STATUS`, `A5XX_RBBM_INT_0_MASK_*`, `REG_A5XX_GPMU_*`, and `REG_A5XX_VBIF_*` resolve.

Runtime signals on A5xx hardware include successful GPU probe, firmware and GPMU initialization, clean ringbuffer startup, successful command submission, no unexpected `RBBM_INT_0_STATUS` errors, correct CP interrupt clearing, stable suspend/resume, preemption/context-switch success when enabled, and no SMMU stall or UCHE trap reports under normal workloads.

Graphics validation should exercise color/depth/stencil formats, MSAA, blits and resolves, GMEM-to-memory and memory-to-GMEM paths, LRZ-enabled and LRZ-disabled draws, UBWC/flag-buffer surfaces, vertex formats, texture formats including compressed formats, sampler wrap/filter/LOD modes, UBOs, SSBOs/images, stream-out, tessellation/geometry shader state where supported, and compute dispatch. Debug/perf validation should confirm readable CP debugfs output, plausible always-on/busy counters, selectable per-block performance counters, and useful crash-dump/fault status when forced error paths are tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/adreno/a5xx.xml -->
