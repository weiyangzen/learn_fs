# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_sh_mask.h lines 14837-17355

## Scope

This chunk covers lines 14837-17355 of the generated AMD GC 9.4.2 shader/register mask header. It contains 2,142 `#define` entries across 372 register names. The slice starts with the final `VGT_CNTL_STATUS__VGT_PRIMGEN_BUSY_MASK` bit from the preceding VGT status register, then covers WD/IA/VGT/PA front-end and primitive assembly controls, PA scanner/clipper/binning controls, UTCL1 policy/status fields, and a large performance-counter data/select register span.

The chunk crosses two visible address-block regions:

- Before line 15457, the register groups describe graphics front-end and PA/VGT/WD/IA controls, including UTCL1 policy, primitive/DMA controls, PA clip/scanner enhancement, binner event controls, FIFO sizing, and tile steering.
- From `// addressBlock: gc_perfddec` at line 15457 through line 16043, it defines performance-counter data register masks for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA/TD/TCP/TCC/TCA, CB/DB, RLC, and RMI blocks.
- From `// addressBlock: gc_perfsdec` at line 16045 to the end of this chunk, it defines performance-counter selector, global control, latency-stat selector, draw-window, GRBM busy-mask, SQ/SPI binning, texture/cache, color-buffer filter, and counter-mode fields.

This is a generated register metadata header, not executable driver logic. The public surface is the set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants consumed with matching GC 9.4.2 register offsets.

## Purpose

`gc_9_4_2_sh_mask.h` supplies bit positions and masks for AMDGCN/SOC15 GC 9.4.2 hardware registers, used by the Aldebaran graphics and KFD paths. This chunk's purpose is to let runtime code safely build and decode 32-bit register values for:

- Work distributor (`WD_*`) busy state, draw quality-of-service, UTCL1 policy/status, buffer resource sizing, and performance counters.
- Input assembler (`IA_*`) UTCL1 policy/status and performance-counter selects.
- Vertex geometry/tessellation (`VGT_*`) system configuration, max wave IDs, DMA primitive/control parameters, LS/HS config, and performance-counter selects.
- Primitive assembler/clipper/scanner (`PA_*`) clipper and scanner enhancement, binner events, FIFO sizing, UTCL1 controls, scanner out-of-order behavior, DSM/tile steering, and PA SU/SC performance counters.
- Command processor (`CP*`, `CPF`, `CPG`, `CPC`) performance counters, latency-stat selectors, draw object/window registers, and `CP_PERFMON_CNTL`.
- Global register bus manager (`GRBM*`) performance counters and user-defined busy/clean masks.
- Shader processor/input (`SPI`), shader queue (`SQ`), shader export (`SX`), global data share (`GDS`), texture address/data/cache (`TA`, `TD`, `TCP`, `TCC`, `TCA`), color buffer (`CB`), depth buffer (`DB`), runlist controller (`RLC`), and RMI performance-counter data/select registers.

The constants remove raw bit numbers from consumers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, golden-register programming, perf-event setup, debug register dumps, and low-level MMIO read/modify/write paths.

## Important API Surface

There are no structs, enums, functions, or inline helpers in this chunk. The API consists entirely of preprocessor macros. Important families are:

- `WD_CNTL_STATUS`, `WD_QOS`, `WD_UTCL1_CNTL`, and `WD_UTCL1_STATUS` expose WD busy bits, draw-stall control, UTCL1 retry/drop/bypass/invalidate/fragment/snoop policy, and fault/retry/PRT status plus UTCL1 IDs.
- `IA_UTCL1_CNTL` and `IA_UTCL1_STATUS` mirror the WD UTCL1 policy/status layout for input assembler traffic.
- `CC_GC_PRIM_CONFIG` and `GC_USER_PRIM_CONFIG` describe inactive IA and VGT/PA blocks, while `CC_GC_SHADER_ARRAY_CONFIG` and `GC_USER_SHADER_ARRAY_CONFIG` expose inactive CU masks. These are topology/configuration masks that must align with the companion offset header and ASIC harvesting rules.
- `VGT_SYS_CONFIG`, `VGT_VS_MAX_WAVE_ID`, `VGT_GS_MAX_WAVE_ID`, `VGT_DMA_PRIMITIVE_TYPE`, `VGT_DMA_CONTROL`, and `VGT_DMA_LS_HS_CONFIG` define primitive processing, DMA draw grouping, EOP/EOI switching, instance optimization, and tessellation input control fields.
- `WD_BUF_RESOURCE_1` and `WD_BUF_RESOURCE_2` split position, index, parameter, address-mode, and sideband buffer sizes across field ranges.
- `PA_CL_CNTL_STATUS`, `PA_CL_ENHANCE`, `PA_SU_CNTL_STATUS`, `PA_SC_FIFO_DEPTH_CNTL`, trap-screen locks, force-EOV counters, binner event controls, binner timeout/perf controls, `PA_SC_ENHANCE`, `PA_SC_ENHANCE_1`, `PA_SC_ENHANCE_2`, FIFO size registers, and `PA_SC_TILE_STEERING_CREST_OVERRIDE` cover front-end raster/clip/scanner behavior. Many fields are enable/disable or workaround-style bits, including out-of-order PA/SC guidance, PBB/binning, line-stipple reset, VPZ event routing, shader profiling, FDCE enhancements, clock-gating disables, and ECO spares.
- `PA_UTCL1_CNTL1` and `PA_UTCL1_CNTL2` include page-fragment, prefetch, invalidation, request-discard, stall, sparse, VMID/RDWR perf-event, and fragment-forcing controls for PA-side translation traffic.
- `CPG/CPC/CPF/GRBM/WD/IA/VGT/PA_SU/PA_SC/SPI/SQ/SX/GDS/TA/TD/TCP/TCC/TCA/CB/DB/RLC/RMI_PERFCOUNTER*_LO/HI` in `gc_perfddec` are performance counter data registers. Most low/high halves expose a single full-width `PERFCOUNTER_LO` or `PERFCOUNTER_HI` field, with notable 16-bit high-half masks for `PA_SU_PERFCOUNTER*_HI`.
- `*_PERFCOUNTER*_SELECT` in `gc_perfsdec` provide event-selection and counter-mode controls. Common fields include `PERF_SEL` or `CNTR_SEL*`, paired event selectors, `CNTR_MODE`, `PERF_MODE`, and `SPM_MODE`; block-specific selectors add masks such as SQ SQC bank/client/SIMD masks and GRBM user-defined busy masks.
- `CP_PERFMON_CNTL` defines global perfmon and SPM perfmon states, enable mode, and sample-enable fields.
- `CPF_TC_PERF_COUNTER_WINDOW_SELECT` and `CPG_TC_PERF_COUNTER_WINDOW_SELECT` select texture-cache counter windows, with `ALWAYS` and `ENABLE` bits.
- `CPF/CPG/CPC_LATENCY_STATS_SELECT` and the corresponding data registers define latency-stat index, clear, enable, and data fields.
- `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` describe draw-window/object filtering for CP-side measurement.
- `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, and `SQ_PERFCOUNTER_CTRL2` add SQ counter enable, trace, halt, SIMD/mode, thread-trace, SQG event, and reset controls beyond the repeated SQ select registers.
- `SPI_PERFCOUNTER_BINS` defines four min/max bin ranges packed into a 32-bit register.
- `VGT_PERFCOUNTER_SEID_MASK` scopes VGT performance counting by shader-engine ID.
- `CB_PERFCOUNTER_FILTER` gates CB performance events by operation, format, clear, MRT, sample count, and fragment count.
- The chunk ends inside `CB_PERFCOUNTER3_SELECT`: it includes `PERF_SEL__SHIFT`, `PERF_MODE__SHIFT`, and `PERF_SEL_MASK`, but the matching `PERF_MODE_MASK` is outside this chunk.

## Control Flow

The header itself has no runtime control flow. Driver control flow around these masks usually follows this pattern:

1. Include the GC 9.4.2 offset header and this mask header.
2. Choose the register address macro from `gc_9_4_2_offset.h`.
3. Compose, update, or decode the register value with `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, often through field helpers.
4. Apply the value through SOC15/MMIO helpers, packet programming, golden-register setup, KFD debug paths, performance-monitor configuration, or debug dump decoding.

Direct local include points are `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_2.c`, which owns Aldebaran GC 9.4.2 graphics setup, golden settings, reset, RAS, shader init, and performance-related flows, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_aldebaran.c`, which uses the same generated masks for KFD/debug register value construction.

The visible chunk implies several table-driven or indexed runtime flows even though no loops are present here:

- Performance monitor setup iterates over low/high counter registers and paired selector registers for each IP block.
- SQ exposes 16 repeated `SQ_PERFCOUNTER*_SELECT` families and separate counter control/mask registers; consumers must program the select and mode fields consistently with the counter data slot being read.
- GRBM select registers pack a `PERF_SEL` field plus many user-defined busy/clean masks; consumers can construct aggregate busy views by choosing which sub-block busy signals participate.
- PA scanner/binning controls are usually programmed during ASIC initialization or golden-setting application, not per draw, because they affect pipeline scheduling, binning, out-of-order behavior, and hardware workarounds.
- UTCL1 controls/status fields are consumed by memory-translation setup and diagnostic paths; status fields are read/decoded, while control fields are written with preserved reserved bits.

## State and Persistence

The macros are compile-time constants and hold no state. The registers they describe are persistent GPU hardware state until changed by the driver, firmware, reset, suspend/resume, power transition, or context restoration path.

PA/SC/VGT/WD/IA control registers affect long-lived pipeline behavior. Examples include inactive block masks, primitive/DMA switching policy, PA scanner enhancement/workaround bits, binning controls, FIFO sizes, tile steering, and draw-stall control. Incorrect values can persist beyond a single command submission and affect all graphics or compute work using the same GC instance.

UTCL1 fields in WD, IA, and PA affect memory-translation behavior for front-end/scanner traffic. Retry timers, bypass/drop modes, invalidation bits, force-snoop policy, VMID reset mode, sparse behavior, page-fragment forcing, and request-discard behavior can alter fault reporting and translation performance until reprogrammed.

Performance-counter data registers are read-only or counter-like hardware state in normal usage. Selector and control registers persist the active event mux, SPM mode, counter mode, mask/window/filter policy, trace enable, halt state, and sample enable. If perf setup fails to restore selectors, later profiling sessions or debug reads can observe stale event routing.

The PA binner and scanner fields contain many enable/disable and ECO spare bits. These are typically validated as ASIC-specific golden settings or workaround state; persistence matters across reset, power-gating, and multi-die initialization because GC 9.4.2/Aldebaran has die-specific setup paths.

## Dependencies and Integration Points

- The masks depend on the generated GC 9.4.2 register database and must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_4_2_offset.h`.
- The header guard and generated constants are used by AMDGPU code through ordinary C preprocessing. There is no runtime library dependency inside the header itself.
- `gfx_v9_4_2.c` includes this header with the companion offset header for Aldebaran graphics initialization and register programming. Its golden-setting arrays use generated register offsets; related field-level call sites in this driver family rely on `*_sh_mask.h` names remaining exact.
- `amdgpu_amdkfd_aldebaran.c` includes this header for KFD/debug register value construction using field helpers such as `REG_SET_FIELD`.
- SOC15 register helpers, MMIO accessors, RAS paths, KFD debug controls, perfmon/perf-event code, register dump tooling, and reset/suspend/resume flows are the likely integration surfaces for this chunk.
- Cross-ASIC generated headers under `include/asic_reg/gc/` and older `gca/` headers expose similar macro families. That makes this chunk part of a generated ABI-like source surface: names and bit layouts are expected by existing common AMDGPU code and by ASIC-specific programming tables.

## Risks

- Generated bitfield drift is the main risk. A wrong shift or mask silently programs the wrong hardware bit, and most consumers will still compile because these are untyped numeric macros.
- The range begins and ends mid-context. Line 14837 is only the final `VGT_CNTL_STATUS` mask from a previous register group, and line 17355 cuts off inside `CB_PERFCOUNTER3_SELECT`. Merge/reconciliation must combine adjacent chunks before claiming complete per-file coverage.
- Reserved and ECO spare fields are exposed as ordinary masks. Callers must know which bits are safe to write for GC 9.4.2 stepping and preserve reserved bits during read/modify/write.
- PA scanner/binning/enhancement fields have high hardware-behavior risk. Fields that disable resets, alter out-of-order threshold switching, bypass PBB/binning, flush on transitions, or change line-stipple/VPZ behavior can cause rendering corruption, hangs, or performance regressions if applied to the wrong ASIC revision.
- UTCL1 policy fields can affect fault visibility and recovery. Misprogrammed bypass, drop, invalidation, retry, page-fragment, sparse, prefetch, VMID, or force-snoop controls can produce hidden faults, false fault attribution, or unstable memory accesses.
- Performance counter select/data families are repetitive. Copy/paste or index mistakes can read one block's counter while selecting another block's event, especially around paired `*_SELECT`/`*_SELECT1` registers and low/high data halves.
- Some high-half counter masks are narrower than the common full-width pattern, notably the PA SU high halves. Generic decoding code must not assume every `*_HI` mask is `0xffffffff`.
- GRBM busy mask fields have names ending in `_MASK_MASK` because the field name itself includes `MASK`; this can be easy to misuse in scripts or generated field helper lookups.
- The chunk exposes filter/windowing registers for perfmon. Stale filters, window selectors, draw-window controls, or sample-enable state can make performance measurements misleading even when counters increment.

## Test Signals

- Build coverage: compiling AMDGPU with `gfx_v9_4_2.c` and `amdgpu_amdkfd_aldebaran.c` catches missing macros, duplicate definitions, syntax problems, and include-order issues.
- Header generation validation: compare lines 14837-17355 against the GC 9.4.2 source register database and `gc_9_4_2_offset.h`, verifying each `__SHIFT` has the expected mask, width, and register association.
- Adjacent-chunk merge validation: ensure `VGT_CNTL_STATUS` is completed from the prior chunk and `CB_PERFCOUNTER3_SELECT__PERF_MODE_MASK` is collected from the following chunk before writing the final per-file research report.
- Golden-register and init smoke tests: boot and reset Aldebaran/GC 9.4.2 hardware while checking dmesg for golden-setting failures, RAS initialization issues, GPU hangs, or graphics pipeline instability.
- UTCL1 diagnostics: exercise VM fault, retry/XNACK, PRT, sparse, and invalidation scenarios, then decode `WD_UTCL1_STATUS`, `IA_UTCL1_STATUS`, `PA_CL_CNTL_STATUS`, `PA_UTCL1_CNTL1`, and `PA_UTCL1_CNTL2` with these masks.
- Perfmon validation: program representative CP/GRBM/WD/IA/VGT/PA/SPI/SQ/SX/GDS/TA/TD/TCP/TCC/TCA/CB/DB/RLC/RMI counters, confirm selectors route the expected events, and verify low/high counter reads match known workloads.
- Counter filter/window tests: validate CP draw-window controls, CPF/CPG texture-cache windows, latency-stat selectors, SQ counter masks, SPI bins, VGT SEID masks, and CB filters against controlled workloads.
- Register-dump validation: decode known-good GC 9.4.2 register dumps and compare field names/values for PA scanner controls, UTCL1 controls/status, perf data registers, selector registers, and CB filter fields.
