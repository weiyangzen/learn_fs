# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h lines 5242-7775

## Scope And Purpose

This chunk is a generated AMD DCN 2.0.0 register-offset header fragment. It contains preprocessor constants only: no C functions, structs, enums, variables, executable control flow, or direct I/O. The exported values map symbolic DCN display-engine register names to MMIO register offsets, with a matching `<REGISTER>_BASE_IDX` macro for the register-base segment used by AMDGPU/DC register helpers.

The source path is under a local `ceph-client` source mirror, but this file is part of the Linux AMDGPU display driver. It does not implement Ceph filesystem behavior. Its job is hardware ABI metadata for DCN 2.0-class display hardware, especially DPP pipes 1-3 and MPC/MPCC color-compositing/output-gamma blocks.

This line range spans 2,534 physical lines and 2,418 `mm*` macro definitions. It starts in the middle of the DPP1 color-management block, at `mmCM1_CM_SHAPER_LUT_WRITE_EN_MASK`, after the previous chunk's CM1 blend-gamma and shaper setup registers. It then covers:

- The tail of `CM1` shaper LUT, shaper RAM A/B region, memory-power, 3D LUT, and CM debug offsets.
- DPP1 perfmon instance `DC_PERFMON14`.
- Full DPP2 and DPP3 top, converter/cursor, scaler, color-management, and perfmon offset groups.
- MPC MPCC instance offsets for `MPCC0` through `MPCC7`.
- MPC output mux offsets for `MPC_OUT0` through `MPC_OUT5`.
- MPC global config, CRC, clock/reset, update/ack/status, stall, and perfmon event-control offsets.
- MPCC output-gamma RAM offsets for `MPCC_OGAM0` through `MPCC_OGAM5`.
- The beginning of `MPCC_OGAM6`, ending at `mmMPCC_OGAM6_MPCC_OGAM_RAMA_REGION_20_21`.

The chunk ends mid-address-block. The rest of `MPCC_OGAM6` and later `MPCC_OGAM7` offsets are in the next file chunk.

## Important APIs, Types, And Macros

There are no callable APIs or C type definitions here. The interface is the generated macro namespace:

- `mm<REGISTER>` gives the DCN 2.0 register offset.
- `mm<REGISTER>_BASE_IDX` gives the base segment index to combine with the offset.
- All macros in this chunk use `BASE_IDX` value `2`, which corresponds to the DCN base segment used by consumers through `BASE(mm..._BASE_IDX)`.

Important macro families:

- `mmCM1_CM_SHAPER_*`, `mmCM1_CM_3DLUT_*`, `mmCM1_CM_MEM_PWR_*`, and `mmCM1_CM_TEST_DEBUG_*` finish the color-management register set for DPP pipe 1. These cover shaper LUT access, split RAM A/B piecewise-linear regions, 3D LUT mode/index/data/control, output normalization/offsets, CM memory-power controls/status, and debug index/data.
- `mmDPP_TOP2_*` and `mmDPP_TOP3_*` define DPP top-level control, soft reset, CRC result/control, and host-read offsets for DPP instances 2 and 3.
- `mmCNVC_CFG2_*` and `mmCNVC_CFG3_*` define surface pixel format, format conversion, floating-point conversion bias/scale, color keyer, and alpha 2-bit LUT offsets. `mmCNVC_CUR2_*` and `mmCNVC_CUR3_*` define cursor control and two cursor color registers.
- `mmDSCL2_*` and `mmDSCL3_*` define scaler offsets: OTG blanking windows, mode, memory power, line-buffer format/control, autocalibration, black offsets, tap controls, coefficient RAM access, 2-tap control, MPC size, scale ratios, phase init, recout start/size, OBUF power/status, and DSCL debug index/data.
- `mmCM2_*` and `mmCM3_*` define the full DPP color-management sets for pipes 2 and 3: gamut remap A/B matrices, input CSC A/B matrices, degamma RAM A/B regions, degamma LUT access/control, CM control, blend-gamma RAM A/B regions, HDR multiplier, dealpha/coefficient format, shaper LUT/RAM, 3D LUT, memory power/status, and CM debug.
- `mmDC_PERFMON14_*`, `mmDC_PERFMON15_*`, and `mmDC_PERFMON16_*` define DPP-local perf counter control, state, current value, high/low counter, and perfmon control offsets.
- `mmMPCC0_*` through `mmMPCC7_*` define MPCC blend/composition offsets: control, top/bottom gain, output size, status, background color components, memory power control/status, mux control, opacity, and SM control.
- `mmMPC_OUT0_MUX` through `mmMPC_OUT5_MUX` define the output mux registers that connect MPCC trees to output processors.
- `mmMPC_*` defines MPC-wide host read, CRC control/results/selection, clock control, soft reset, update acknowledge/status, stall grace window, underflow, idle status, and perfmon event control offsets.
- `mmMPCC_OGAM0_*` through `mmMPCC_OGAM5_*`, plus the first part of `mmMPCC_OGAM6_*`, define MPC output-gamma LUT mode/index/data/control and RAM A/B piecewise-linear start, slope, end, and region offsets.

## Control Flow And Data Flow

This header chunk has no internal runtime control flow. Data flow is compile-time substitution into AMDGPU/DC register tables and MMIO helper calls.

The main inclusion pattern appears in DCN20 code such as `display/dc/resource/dcn20/dcn20_resource.c`, `display/dc/irq/dcn20/irq_service_dcn20.c`, `display/dmub/src/dmub_dcn20.c`, `display/dc/gpio/dcn20/hw_factory_dcn20.c`, `display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`, and `amdgpu/gmc_v10_0.c`. `dcn20_resource.c` includes both `dcn_2_0_0_offset.h` and `dcn_2_0_0_sh_mask.h`, then defines helpers such as `SR(reg_name)` and `SRI(reg_name, block, id)` that compute absolute register addresses as `BASE(mm..._BASE_IDX) + mm...`.

For DPP registers, `display/dc/dpp/dcn20/dcn20_dpp.h` builds `TF_REG_LIST_DCN20` out of names from this chunk. That list is expanded in resource construction to initialize per-pipe transform/DPP register structs. Runtime functions in `dcn20_dpp.c` then use register-helper macros such as `REG_GET`, `REG_UPDATE`, `REG_SET_2`, and `REG_GET_2` against those tables. Concrete examples include reading `CM_SHAPER_CONTROL`, `CM_3DLUT_READ_WRITE_CONTROL`, `CM_3DLUT_MODE`, and `CM_BLNDGAM_LUT_WRITE_EN_MASK` in `dpp20_read_state()`, powering DPP memory through `CM_MEM_PWR_CTRL`, `OBUF_MEM_PWR_CTRL`, and `DSCL_MEM_PWR_CTRL` in `dpp2_power_on_obuf()`, and programming converter/scaler state through `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `SCL_MODE`, `DSCL_CONTROL`, scale ratios, tap controls, and recout registers.

For MPC/MPCC registers, DC MPC headers and implementations use the same generated-address pattern. `dcn10_mpc.h` and `dcn20_mpc.h` define register lists for `MPCC_CONTROL`, `MPC_OUT_MUX`, and `MPCC_OGAM` instances, while MPC runtime code uses the resulting register arrays to program MPCC blend mode, alpha mode, global alpha/gain, output mux selection, MPCC status, and output-gamma LUT behavior.

No sequencing is encoded by these macros. The ordering lives in the display core and hardware sequencing code that consumes the register tables: modeset programming, plane enable/disable, scaler setup, color pipeline programming, MPCC tree assembly, output mux selection, CRC/debug access, and power-management transitions.

## State And Persistence Behavior

This chunk stores no software state and performs no I/O. It names mutable DCN hardware registers. Runtime state represented by these offsets includes:

- DPP color state: shaper LUT contents, 3D LUT contents/configuration, blend-gamma and degamma RAM regions, gamut remap matrices, input CSC matrices, HDR multiplier, dealpha/coefficient format, and debug selector/data state.
- DPP conversion and scaling state: pixel format, fixed/float conversion bias and scale, color keyer values, alpha LUT, cursor control/color, scaler mode, line-buffer format, coefficient RAM, tap counts, scale ratios, phase initialization, recout window, black offsets, and OTG blanking data.
- DPP and CM power state: shared CM memory power controls/status, DSCL LUT memory power, and OBUF memory power controls/status.
- DPP diagnostics: DPP CRC values/control, DC perfmon counters, scaler/color-management debug index/data registers, and host-read controls.
- MPC/MPCC composition state: MPCC blend mode, alpha blend/multiplied mode, overlap-only behavior, global alpha/gain, top/bottom gain, background color/depth, output size, mux control, opacity, MPCC memory power/status, and SM control.
- MPC-wide state: output mux routing, CRC control/results/selection, update acknowledge/status, clock/reset state, underflow, stall grace window, idle status, and perfmon event control.
- MPCC OGAM state: output-gamma mode, LUT bank/index/data/control, RAM A/B piecewise-linear start/slope/end/region definitions, and the partially covered OGAM6 RAM A range.

Persistence is hardware-defined and not declared in this offset header. Some registers hold programmed mode state until a subsequent modeset, color update, power transition, suspend/resume, GPU reset, or another driver write. Others are live status, sticky status, debug selector/data windows, counters, self-clearing update/acknowledge paths, or read-only hardware state. Names such as `*_STATUS`, `*_PWR_STATUS`, `*_UPDATE_ACK*`, `*_PENDING_TAKEN_STATUS*`, `*_CRC_RESULT*`, `*_PERFCOUNTER_STATE`, `*_SOFT_RESET`, and `*_HOST_READ_CONTROL` indicate likely access semantics, but side effects and clear behavior come from hardware documentation and the matching field masks, not from this file.

## Dependencies And Integration Points

This chunk depends on the rest of `dcn_2_0_0_offset.h` for the full include-guarded generated header and on `dcn_2_0_0_sh_mask.h` for field masks and shifts. It is also coupled to DCN 2.0 hardware documentation, SoC base-address headers such as `navi10_ip_offset.h`, and the AMD display `reg_helper` macros.

Direct include consumers found in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Important indirect consumers include DCN20 DPP code (`dcn20_dpp.h` and `dcn20_dpp.c`), common DPP/scaler code inherited from DCN10, and MPC/MPCC code (`dcn10_mpc.*`, `dcn20_mpc.*`) that assembles MPCC trees and output-gamma state.

Practical integration surfaces are DRM/KMS atomic modesets, plane composition, scaling, color management, cursor setup, per-plane and output CRC/debug readback, DC perfmon sampling, underflow detection, output mux routing, power gating/light sleep, suspend/resume reinitialization, DMUB register access, IRQ service mapping, and GPU memory/display interactions on DCN 2.0 ASICs.

## Risks And Edge Cases

- These constants are hardware ABI. An incorrect offset or base index can compile cleanly while reading or writing the wrong hardware register.
- The chunk starts and ends inside larger register families. CM1 shaper state depends on previous-chunk offsets, and OGAM6 is incomplete until the next chunk. Final synthesis should join these boundaries before treating either family as complete.
- Repeated per-instance names are easy to confuse. `CM2` versus `CM3`, `DSCL2` versus `DSCL3`, `MPCC5` versus `MPC_OUT5`, and `MPCC_OGAM5` versus `MPCC_OGAM6` differ only by instance number but target different hardware blocks.
- Base-index pairing matters. Consumers combine `mm..._BASE_IDX` with `mm...`; using a register offset without its generated base segment can address the wrong MMIO aperture.
- DPP color LUT programming is order-sensitive. Shaper, 3D LUT, degamma, blend-gamma, RAM A/B region, LUT index/data, and write-enable/control registers must be sequenced with the field masks from `dcn_2_0_0_sh_mask.h`.
- Scaler and format registers are packed and format-sensitive. Incorrect CNVC/DSCL offsets can produce bad pixel formats, broken cursor colors, incorrect scaling ratios or phase, line-buffer issues, or visual corruption without an obvious crash.
- Power-control offsets affect live display hardware. Misprogramming CM, DSCL, OBUF, or MPCC memory power controls can create black screens, hangs waiting for power-status fields, or resume failures.
- MPC/MPCC routing mistakes are high impact. Wrong MPCC control, mux, update-ack/status, or output mux offsets can attach planes to the wrong output, lose planes, leave stale composition state, or break atomic update synchronization.
- Diagnostics can mask functional issues. CRC, perfmon, debug, host-read, underflow, and idle-status offsets may only be exercised by debugfs or validation tooling, so regressions can escape normal display smoke tests.
- Generated repetition makes manual review brittle. The safest validation is comparison against an authoritative generated DCN 2.0.0 header rather than hand-inspecting every copied offset.

## Test Signals

Validation is mainly compile-time plus hardware behavior:

- Build AMDGPU/DC configurations with DCN 2.0 support enabled. Missing or renamed offsets should fail consumers in `dcn20_resource.c`, `dcn20_dpp.h`, DPP runtime code, MPC/MPCC code, DMUB DCN20 code, IRQ service code, GPIO factory code, clock manager code, and GMC code.
- Compare this range against a known-good upstream `dcn_2_0_0_offset.h` or the authoritative ASIC register database. Focus on instance numbering and offsets for `CM1` tail, DPP2/DPP3, `MPCC0-7`, `MPC_OUT0-5`, MPC global registers, and `MPCC_OGAM0-6`.
- Exercise DCN20 hardware with multiple planes and multiple pipes: plane enable/disable, blending, global alpha, premultiplied alpha, cursor updates, scaling, color keying, and output mux changes.
- Exercise color-management paths: degamma, shaper LUT, 3D LUT, blend/output gamma, gamut remap, HDR multiplier, input CSC, output gamma through MPCC OGAM, LUT bank selection, RAM A/B switching, and suspend/resume after color state is programmed.
- Exercise scaler and converter paths with RGB/YUV formats, 4:2:0 surfaces, scaling up/down, odd source sizes, different tap counts, cursor formats, and recout windows.
- Check power-management transitions around active streams: CM memory power, DSCL LUT memory power, OBUF memory power, MPCC memory power, clock/soft reset, idle status, and resume reprogramming.
- Use CRC/perfmon/debug signals where available: DPP CRC values, MPC CRC results, DC perfmon counters, underflow status, MPCC status, and debug index/data reads can catch wrong offsets that simple modesets miss.
- Watch user-visible regressions: black screen, missing plane, wrong output routing, corrupted scaling, incorrect gamma/color, cursor artifacts, underflow logs, failed page flips, hangs in register waits, or display loss after suspend/resume.
