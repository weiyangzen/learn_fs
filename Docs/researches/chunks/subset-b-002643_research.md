# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 27133-29689

## Purpose

This chunk is generated AMD GPU register metadata for GC 9.1. It defines bit shifts and masks for several late sections of the graphics-core register map: clock-gating controls, external-access and VM/SR-IOV controls, RLC hypervisor and GPU-IOV registers, clock/activity counter (CAC) programming and accumulators, and shader-queue indirect wave/debug status registers.

The file contains no executable logic. Its purpose is to provide the symbolic field names consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indirect `ix*` register access, and generated golden-register programming tables. The matching offset names live in the adjacent GC 9.1 offset header; this chunk supplies the field layout for those offsets.

The chunk starts in the tail of `CGTT_VGT_CLK_CTRL`, then covers these main groups:

- `CGTT_*_CLK_CTRL`, `*_CGTT_*CLK_CTRL`, `SQ_*_CLK_CTRL`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `CB_CGTT_SCLK_CTRL`, `DB_CGTT_CLK_CTRL_0`, `TCC_CGTT_SCLK_CTRL`, `TCA_CGTT_SCLK_CTRL`, `RMI_CGTT_SCLK_CTRL`, and `GCEA_CGTT_CLK_CTRL` clock-gating fields.
- `gc_utcl2_vmsharedhvdec` fields for per-VF framebuffer size/offset, MARC regions, IOMMU enable/performance, PCIe ATS, and UTCL2 clock gating.
- `gc_hypdec` fields for CP/RLC microcode windows, GRBM shadow/cam access, RLC GPU-IOV scheduling/config/status, virtual reset, interrupts, doorbell status, scratch, and SDMA save/restore status.
- `gccacind` and `secacind` CAC selection, override, weighting, and accumulator fields for many graphics sub-blocks.
- `sqind` shader-queue debug and wave-state fields, including `SQ_WAVE_MODE`, `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, and the beginning of `SQ_WAVE_HW_ID`.

## Important APIs, Types, And Data

The API surface is entirely preprocessor constants with the generated naming form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no C functions, structs, or enums in this chunk.

Important field families:

- Clock gating registers use a repeated layout: `ON_DELAY` at low bits, `OFF_HYSTERESIS` in bits 4-11, stall override fields around bits 16-23, and soft/core/register override fields in the high byte. These appear across IA, WD, PA, SC, SQ, SQG, SX, TD, TA, TCPI, TCI, GDS, DB, CB, TCC, TCA, CP/CPF/CPC, RLC, RMI, TCPF, EA, and UTCL2 domains. Variants add domain-specific override names such as `PRIMGEN_OVERRIDE`, `TESS_OVERRIDE`, `GS_OVERRIDE`, `PBB_*`, `PFF_ZFF_MEM_CLK_*`, `TCI_TCC*_CLK_OVERRIDE`, `RBIU_INPUT_OVERRIDE`, `MGLS_OVERRIDE`, or `SPARE`.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` expose small single-purpose disable fields; `SQ_POWER_THROTTLE` and `SQ_POWER_THROTTLE2` expose `MIN_POWER`, `DRAWER`, `FORCE_POWER`, `POWER_GOOD`, `HIGHER`, and `LOWER`.
- VM virtualization fields define `MC_VM_FB_SIZE_OFFSET_VF0` through `VF15` as paired 16-bit `VF_FB_SIZE` and `VF_FB_OFFSET` values, MARC base/relocation/length registers split into low and high halves, `VM_IOMMU_CONTROL_REGISTER__IOMMUEN`, `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER__PERFOPTEN`, and ATS fields `STU` plus `ATC_ENABLE`.
- RLC GPU-IOV fields define command execution and status (`RLC_GPU_IOV_CFG_REG1/2`), active function selection, scheduler block metadata, microcode/scratch address/data windows, timer control/status, virtual function masks, virtual reset requests, interrupt force/disable registers, SDMA preempt/save/restore status bits, and full-width busy/response/status fields.
- CAC fields define selection/control registers (`GC_CAC_CNTL`, `SE_CAC_CNTL`, `*_OVR_SEL`, `*_OVR_VAL`), two-16-bit weight slots per register for block signal weights, 32-bit accumulator fields, and override select/value bit ranges. The block coverage includes BCI, CB, CP, DB, GDS, IA, LDS, PA, PC, SC, SPI, SQ, SX, SXRB, TA, TCC, TCP, TD, VGT, WD, CU, PG, EA, RMI, UTCL2/ATCL2, router, VML2, and walker.
- SQ indirect debug fields describe queue occupancy and wave state. `SQ_DEBUG_STS_GLOBAL*` exposes busy and FIFO/wave levels; `SQ_DEBUG_STS_LOCAL` exposes local busy and wave level; `SQ_WAVE_MODE` covers FP rounding/denorm behavior, DX10 clamp, IEEE mode, exception enables, FP16 overflow, perf disable, GPR indexing, VSKIP, and CSP; `SQ_WAVE_STATUS` covers condition/status bits such as `SCC`, priorities, `PRIV`, trap/thread-trace enable, export readiness, `EXECZ`, `VCCZ`, barrier/halt/trap/valid/ECC/perf/replay/fatal-halt/export flags; `SQ_WAVE_TRAPSTS` covers exception, save-context, illegal instruction, XNACK, DP rate, and exception-cycle fields.

Representative consumers elsewhere in the tree show the intended macro contract. `gfx_v9_0_read_wave_data()` reads `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_HW_ID`, `ixSQ_WAVE_TRAPSTS`, and `ixSQ_WAVE_MODE` through SQ indirect access. PowerPlay tables in `smu7_powertune.c` program `ixGC_CAC_CNTL` entries through `GPU_CONFIGREG_GC_CAC_IND`; the masks in this chunk define how those packed values break down into enable, threshold, block, and signal fields.

## Control Flow

There is no runtime control flow inside this header. The control-flow model is:

1. GC 9.1-specific code includes generated offset and mask headers.
2. Callers read or write a register through SOC15, indexed, or indirect accessors.
3. `REG_SET_FIELD` and `REG_GET_FIELD` use the `__SHIFT` and `_MASK` constants to pack or unpack field values.
4. The hardware block interprets the final 32-bit register value.

For clock-gating fields, runtime code typically writes golden settings during ASIC initialization or power-management transitions. For CAC fields, PowerPlay/DPM tables select hardware signals, enable/disable counters, and program weights/overrides. For SQ wave fields, debug and hang-analysis paths use SQ indirect access to snapshot wave state into driver-visible buffers. For RLC GPU-IOV fields, hypervisor/SR-IOV control paths use command, scheduler, reset, doorbell, interrupt, and status fields as a hardware handshake surface.

## State And Persistence Behavior

The macros are compile-time-only and have no persistence. The hardware registers they describe are stateful and side-effect-bearing:

- Clock-gating controls persist in GPU registers until reset, power-gating, suspend/resume reinitialization, or explicit reprogramming. Incorrect override bits can force clocks on or stall gating.
- VM/IOMMU/ATS/MARC and per-VF framebuffer fields define hardware translation and virtualization state. These settings persist for the active device lifetime and must match the current PF/VF and memory-management configuration.
- RLC GPU-IOV registers carry scheduler state, active function IDs, virtual reset requests, doorbell status, interrupts, microcode/scratch windows, and save/restore status. Some registers are command or set/clear style and should be treated as transactional rather than passive storage.
- CAC accumulators are hardware counters. Weight and override registers affect how activity is counted or modeled; accumulator registers expose volatile telemetry that may reset on hardware reset or explicit CAC control actions.
- SQ debug and wave registers expose volatile execution state for currently selected shader waves. Reads reflect a point-in-time hardware snapshot and can change immediately as waves execute, halt, trap, or drain.

## Dependencies

This chunk depends on the generated GC 9.1 register database remaining synchronized across:

- `gc_9_1_sh_mask.h` for field masks and shifts.
- The matching `gc_9_1_offset.h` names for `mm*`, `reg*`, and `ix*` offsets.
- AMDGPU register helper macros that expand field names into masks/shifts.
- SOC15 block addressing for memory-mapped GC registers.
- Indirect register paths for `gccacind`, `secacind`, `sqind`, and hypervisor/indexed register spaces.
- PowerPlay/DPM tables that program CAC and power-related registers.
- GFX debug and hang-dump code that reads SQ wave registers.
- SR-IOV/hypervisor paths that manage RLC GPU-IOV, VF framebuffer windows, ATS, MARC, and virtual reset state.

The same field names also appear in sibling generated headers for other IP blocks or GC generations, but the exact offsets, field widths, and reserved bits can differ. Consumers must include the GC/IP-version-specific header selected for the ASIC.

## Integration Points

The primary integration point is AMDGPU's generated ASIC register include tree under `drivers/gpu/drm/amd/include/asic_reg/gc/`. Higher-level integration points include:

- GFX initialization and golden-setting tables for clock-gating register programming.
- Runtime power-management code that enables clock gating, CAC activity accounting, and power-throttle behavior.
- PowerPlay/SMU code that writes `GC_CAC_CNTL`, CAC weights, overrides, and accumulators through GC CAC indirect access.
- GPU virtualization/SR-IOV code using RLC GPU-IOV command/status, per-VF masks, active function IDs, doorbell status, virtual reset requests, ATS, IOMMU, and framebuffer partition fields.
- Microcode loading or inspection paths that use CP/RLC microcode address/data windows.
- Debugfs, hang detection, and GPU reset diagnostics that capture SQ wave mode/status/trap/hardware identity through `SQ_IND_INDEX` and `SQ_IND_DATA`.

## Risks

- A wrong shift or mask can silently corrupt unrelated bits in a hardware register; this is especially dangerous for high-bit override fields and reserved-bit regions.
- Cross-generation reuse is risky. GC 9.1 mask definitions should not be assumed valid for other GC versions, even when names look similar.
- Clock-gating override mistakes can cause hangs, excess power draw, broken performance counter behavior, or failure to enter low-power states.
- CAC weight/control mistakes can produce misleading power/activity telemetry or destabilize power tuning if thresholds, block IDs, signal IDs, or override values are packed incorrectly.
- SR-IOV and hypervisor fields are privilege-sensitive. Incorrect VF masks, active function IDs, reset requests, ATS enables, or framebuffer partition fields can affect isolation, device assignment, or recovery paths.
- Set/clear style status registers such as VF doorbell status set/clear and reset/interrupt force controls should not be handled like ordinary read/write fields.
- SQ wave-state reads are debug snapshots, not stable persistent state. Consumers must tolerate races with running waves and avoid interpreting stale or partially drained wave data as a deterministic program state.
- Reserved fields are explicitly named in several registers; writes should preserve documented reserved bits unless the programming sequence is known to require a full-register value.

## Test Signals

Useful validation is mostly compile-time, static, and hardware smoke coverage:

- Build coverage for GC 9.1 AMDGPU code that includes `gc_9_1_sh_mask.h` and uses `REG_SET_FIELD`/`REG_GET_FIELD` with these field names.
- Static consistency checks that each register in this chunk has matching offset definitions in the GC 9.1 offset header and, where applicable, matching default definitions in generated default headers.
- Golden-register table validation that clock-gating masks preserve reserved bits and only set documented override/delay/hysteresis fields.
- Runtime smoke tests on GC 9.1 hardware showing clock-gating initialization, suspend/resume, and GPU reset complete without register-access faults or hangs.
- Power-management tests that enable CAC programming and verify activity counters/weights behave plausibly under idle and graphics/compute load.
- SR-IOV validation that per-VF framebuffer, ATS, RLC GPU-IOV scheduler, doorbell, reset, interrupt, and SDMA save/restore status paths behave correctly for PF and VF contexts.
- GPU hang/debug tests that capture SQ wave dumps and decode `SQ_WAVE_STATUS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_MODE`, and `SQ_WAVE_HW_ID` fields without malformed output.
