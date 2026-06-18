# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 12608-15146

## Purpose

This chunk is a generated AMD DCN 4.1.0 register field shift/mask slice. It contains no executable C logic and defines no structs, enums, or functions. Its interface is a large set of preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; display driver code combines them with the matching `dcn_4_1_0_offset.h` register offsets and DC register helper macros to read, update, or write individual MMIO fields.

The requested range contains 2,110 `#define` entries, split into 1,057 shift macros and 1,053 mask macros, plus 402 register comments and 9 address-block comments. It starts at the tail of DPP1 converter configuration (`CNVC_CFG1_PRE_DEGAM`/`PRE_REALPHA`), covers DPP1 cursor, scaler, color-management, and DPP-top fields, then continues into DPP2 converter, cursor, scaler, and the beginning of DPP2 color-management gamma RAM A region fields. The boundaries are artificial line-chunk boundaries: the first `CNVC_CFG1_PRE_DEGAM` group began before this chunk, and `CM2_CM_GAMCOR_RAMA_REGION_16_17` continues after line 15146.

Although this file is under a local `ceph-client` source mirror, this range is AMDGPU Display Core hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside a 32-bit display register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, or update that field.

The main register families covered here are:

- `CNVC_CFG1_PRE_DEGAM` and `CNVC_CFG1_PRE_REALPHA`: tail of DPP1 converter pre-degamma selection and pre-realpha enable/alpha-blend controls.
- `CM_CUR1_*`: DPP1 cursor color-management fields for cursor enable/mode, pixel inversion, ROM cursor mode, update-pending status, 24-bit cursor colors, floating-point scale/bias, and two banks of cursor color-conversion matrix coefficients.
- `DSCL1_*`: full DPP1 scaler and image-processing layout, including coefficient RAM selection/data, scaler mode, tap counts, 2-tap hardcoded/sharp controls, manual replication, horizontal/vertical luma and chroma scale ratios and phase initialization, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer format/memory/counter state, scaler/output-buffer memory power, EASF sharpening/ring-estimation/bilateral-filter controls, super-resolution matrix fields, and ISHARP delta/noise/LBA/LUT-memory controls.
- `CM1_*`: DPP1 color-management fields for CM enable, post-CSC control, post-CSC matrix banks A/B, output bias, gamma-correction control, LUT index/data/control, gamma RAM A/B start/end/slope/base/offset/region descriptors, HDR multiplier coefficient, CM memory power/status, dealpha, and coefficient-format selection.
- `DPP_TOP1_*`: DPP1 top-level control, clock/gate selectors, soft reset, CRC readbacks and CRC control, and host-read control.
- Empty/comment-only `dcn_dcec_dpp1_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` boundary: this chunk marks the DPP1 perfmon address block but does not include perfmon field definitions inside the requested lines.
- `CNVC_CFG2_*`: DPP2 converter fields for surface pixel format, expansion/conversion/alpha/bypass/clamp/crossbar format control, floating-point bias/scale, color keying, alpha 2-bit LUT, pre-dealpha, pre-CSC mode and matrices for both A and B banks, coefficient format, pre-degamma, and pre-realpha.
- `CM_CUR2_*`: DPP2 cursor controls mirroring the DPP1 cursor CM layout: enable/mode/color, floating-point scale/bias, matrix mode/current status/coefficient format, and A/B matrix coefficient banks.
- `DSCL2_*`: DPP2 scaler and image-processing fields mirroring `DSCL1_*`, including scaler coefficient RAM, ratio/init/tap configuration, recout and line-buffer state, memory power controls, EASF/SC/ISHARP processing controls, and related PWL segment fields.
- `CM2_*`: beginning of DPP2 color-management fields, including CM control, post-CSC control and matrix banks, bias, gamma-correction control/LUT access, gamma RAM A start/end/slope/base/offset, and RAM A region descriptors through the partial `CM2_CM_GAMCOR_RAMA_REGION_16_17` group.

## Control Flow

This header slice has no local control flow. Runtime behavior comes from AMDGPU Display Core code that includes this generated header and its companion offset header:

1. DCN 4.1.0-specific code includes `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register-list macros token-paste register and field names into ASIC-specific register, shift, and mask tables.
3. DPP, DSCL, color-management, cursor, IRQ/resource, DMUB, and hardware-sequencer code use register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. Those helpers use the masks and shifts to preserve unrelated fields while programming plane conversion, scaling, cursor, color, power, CRC, and top-level DPP state.

The macros do not encode sequencing rules. Consumers still need to load cursor/color/scaler/gamma state in hardware-defined order, avoid writing status or pending bits as ordinary controls, coordinate double-buffered updates with vblank/update locks, and keep memory/clock power state consistent with active pipes.

## State And Persistence Behavior

This chunk stores no software state. It describes state that lives in DCN 4.1.0 display hardware registers:

- Converter state for DPP1/DPP2 pixel format, alpha handling, color keying, floating-point scale/bias, pre-dealpha, pre-CSC, pre-degamma, and pre-realpha.
- Cursor state for enablement, cursor mode, palette colors, pixel inversion, update-pending status, scale/bias, and cursor color-conversion matrices.
- Scaler state for filter coefficient RAM, active coefficient RAM bank, tap counts, luma/chroma scale ratios, phase initialization, recout/MPC dimensions, overscan, black color, line-buffer format, and autocal/update-pending status.
- EASF/SC/ISHARP state for adaptive sharpening, ring estimation, bilateral filtering, PWL segments, noise thresholds/gains, non-linear delta clipping, LBA curves, and delta LUT memory power.
- Color-management state for post-CSC, gamma-correction mode/current status, LUT index/data/configuration, gamma RAM A/B region metadata, HDR multipliers, output bias, dealpha, coefficient format, and CM memory power/status.
- DPP top-level state for clock enables/gates, fine-grain clock-gating repeat disable, soft reset, CRC capture/readback, and host-read behavior.

Persistence is hardware-defined. Configuration fields usually remain until a modeset, plane update, pipe teardown, power-gating transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, current-bank, update-pending, CRC, memory-power-status, and LUT-read/debug fields can be read-only, sticky, self-clearing, or valid only while the relevant DPP/DSCL/CM block is powered. This generated header does not distinguish read-only, write-one-to-clear, or side-effect fields; that knowledge lives in the hardware spec and block-specific driver code.

## Dependencies And Integration Points

- The shift/mask definitions must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which supplies the matching MMIO register addresses.
- `dcn_4_1_0_sh_mask.h` is included by DCN 4.0.1/4.1-family display code such as DMUB setup, IRQ service, clock manager, resource construction, and GPIO hardware translation/factory code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/`.
- The fields integrate with AMD Display Core register-access helpers and generated register-table macros. Most callers do not reference every macro directly; they build per-block tables for DPP, DSCL, CM, cursor, CRC, power, and top-level DPP blocks.
- Plane composition depends on this range for DPP1/DPP2 pixel conversion, cursor blending/color conversion, scaling/filtering, sharpening, color correction, gamma programming, HDR multiplier, and output formatting.
- Diagnostics and validation paths depend on DPP CRC fields, CM/DSCL memory power status, scaler update-pending/current-bank fields, gamma LUT read controls, and DPP host-read controls.
- Repeated layouts across DPP instances and DCN generations make the exact instance prefix important. `DSCL1_*` and `DSCL2_*` have matching shapes but represent different hardware pipes; `CM1_*` and `CM2_*` similarly target different DPP color-management instances.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while writing the wrong MMIO bits, corrupting adjacent fields, or silently leaving a feature unprogrammed.
- Generated-header and offset-header drift is the primary integrity risk. Correct masks paired with stale offsets, or correct offsets paired with stale masks, can misprogram display hardware without obvious compile failures.
- Chunk boundaries are not semantic. The first `CNVC_CFG1_PRE_DEGAM` group is incomplete in this slice, and the `CM2_CM_GAMCOR_RAMA_REGION_16_17` group continues in the next chunk.
- Full-register writes are risky because many registers pack controls, status, current-bank readbacks, pending bits, and high-bit masks such as `0x80000000L` into the same 32-bit word. Read-modify-write helpers are expected for most updates.
- Scaler fields are precision-sensitive. Width or shift mistakes in ratios, phases, tap counts, filter coefficients, recout sizes, or chroma/bottom-field initialization can cause blur, ringing, chroma offset, crop errors, underflow, or blank output.
- EASF/ISHARP fields are image-quality-sensitive and may only fail under specific content, scale ratios, or noise conditions. Incorrect PWL segment, gain, clip, or delta LUT fields can introduce subtle sharpening artifacts.
- Color-management fields are color-accuracy-sensitive. Wrong CSC, gamma RAM region, LUT, bias, coefficient-format, or HDR multiplier fields can produce visible color shifts, HDR regressions, or failures only under color-managed desktop/video workloads.
- Cursor fields are user-visible and latency-sensitive. Incorrect enable, update-pending, color, scale/bias, matrix, or mode masks can produce missing, miscolored, or incorrectly blended cursors.
- Memory-power and clock/reset fields can interact with runtime power management. Forcing memory/clocks off while active, or leaving debug/force fields enabled, can create intermittent modeset, resume, or pipe-underflow failures.
- DPP1/DPP2 repetition makes copy/generator drift easy to miss. A test that only exercises pipe 1 does not validate the equivalent pipe 2 fields.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1.0 display behavior:

- Build AMDGPU display support with DCN 4.1.0 headers enabled. Missing, renamed, or malformed macros should fail in generated register tables or DCN401/related resource, IRQ, DMUB, clock, GPIO, DPP, DSCL, and CM code.
- Mechanically compare this slice against the authoritative DCN 4.1.0 register database and the adjacent `dcn_4_1_0_offset.h` names, allowing for the known artificial start/end boundaries.
- Run static consistency checks that complete register groups have matching `__SHIFT` and `_MASK` pairs across adjacent chunks, especially for the partial `CNVC_CFG1_PRE_DEGAM` and `CM2_CM_GAMCOR_RAMA_REGION_16_17` groups.
- Exercise DPP1 and DPP2 independently with identity scale, up/downscale, fractional ratios, chroma formats, recout changes, overscan, scaler coefficient reloads, and line-buffer pressure.
- Validate cursor paths on DPP1/DPP2: enable/disable, motion, color changes, alpha/pixel inversion modes, FP scale/bias, matrix conversion, rapid updates, and suspend/resume.
- Validate color paths with CRC or visual/color tests for pre-CSC, post-CSC, gamma RAM A/B, LUT index/data/control, HDR multiplier, bias, dealpha/realpha, coefficient formats, and color keying.
- Exercise EASF/SC/ISHARP paths across content patterns and scale factors that stress ring estimation, bilateral filtering, PWL segment boundaries, noise detection, and delta LUT programming.
- Check DPP CRC and host-read diagnostics for stable readback, correct channel packing, and no stale values across pipe disable/enable cycles.
- Run runtime PM, suspend/resume, and GPU reset tests while checking CM/DSCL/OBUF/ISHARP memory power status, DPP clock/reset state, and absence of underflow or stuck update-pending bits.

## Cross-Chunk Notes

The previous chunk contains the earlier `CNVC_CFG1_PRE_DEGAM` definitions and the rest of preceding DPP1 converter state. The next chunk continues `CM2_CM_GAMCOR_RAMA_REGION_16_17` and later DPP2 color-management fields. The final per-file research document should reconcile adjacent chunks before making whole-file claims about all DCN 4.1.0 DPP instances or complete color-management gamma RAM coverage.
