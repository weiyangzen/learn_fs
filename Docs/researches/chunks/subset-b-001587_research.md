# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 15002-17515

## Scope

This chunk is chunk 7 of the generated AMD DCN 1.0 register shift/mask header. It covers lines 15002-17515 of `dcn_1_0_sh_mask.h`, starting in the middle of the DPP1 color-management gamma table definitions and ending at the first `DSCL3_SCL_VERT_FILTER_INIT_BOT_C` comment. The file is not executable code; it is a generated hardware register field contract made of `#define` constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`.

## Purpose

The chunk supplies bit positions and masks for display pipe processor register fields used by the AMD DC display driver. These constants let typed display code compose and decode memory-mapped hardware register values without hard-coding bit arithmetic at each call site.

The visible hardware areas are:

- Tail of `CM1` DPP1 color-management gamma fields, especially degamma RAM B and regamma RAM A/B piecewise-linear region programming.
- DPP1 output color controls including HDR multiplier, range clamp, denormalization, CM output mode, random seeds, and CM memory power state.
- DPP1 perf monitor block `DC_PERFMON13`.
- Full DPP2 top, CNVC format conversion, cursor, DSCL scaler, color-management, and perf monitor blocks.
- Beginning of DPP3 top, CNVC, cursor, and DSCL scaler blocks.

## Important API Surface

There are no C functions, structs, or enums in this chunk. The important API is the macro namespace consumed by register helper macros in the display driver.

Key macro families:

- `CM1_CM_DGAM_RAMB_*`: DPP1 degamma RAM B control. It defines per-channel start, start segment, linear slope, end, end slope/base, and region LUT offset/segment fields for regions 0-15.
- `CM1_CM_RGAM_*`: DPP1 regamma controls. It includes `CM_RGAM_CONTROL`, LUT index/data/write enable/status fields, and RAM A/B piecewise-linear programming. RAM A/B region tables cover regions 0-33 in packed pairs.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_RANGE_CLAMP_CONTROL_{R,G,B}`, `CM1_CM_DENORM_CONTROL`, `CM1_CM_CMOUT_CONTROL`, `CM1_CM_MEM_PWR_{CTRL,STATUS}`: DPP1 color output and memory power fields.
- `DC_PERFMON13_*` and `DC_PERFMON14_*`: DPP performance counter selector, state, counter control, and high/low count fields for DPP1 and DPP2 perfmon instances.
- `DPP_TOP2_*` and `DPP_TOP3_*`: pipe top-level controls, soft reset, CRC values/control, and host read rate control.
- `CNVC_CFG2_*` and `CNVC_CFG3_*`: pixel format, format conversion, denormalization, color keyer thresholds, and update-pending fields.
- `CNVC_CUR2_*` and `CNVC_CUR3_*`: cursor enable/mode/min/max/color/FP scale-bias fields.
- `DSCL2_*` and `DSCL3_*`: scaler coefficient RAM, filter mode, tap counts, ratios, init phases, overscan, recout/MPC size, line-buffer format, memory power, output buffer, and autocal fields.
- `CM2_CM_*`: DPP2 color-management matrix, input gamma, input/output CSC, gamut remap, bias/scale, degamma/regamma, HDR multiplier, clamps, denorm, output, random seed, and memory power fields.

The macros integrate with display register access helpers such as `FD(reg__field)`, `REG_SET`, `REG_UPDATE`, and the DPP mask/shift list macros in `drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h`. The paired `dcn_1_0_offset.h` supplies register addresses; this file supplies field layout.

## Control Flow

The chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. Hardware block-specific C code includes `dcn/dcn_1_0_sh_mask.h`.
2. DPP, scaler, color-management, GPIO, IRQ, and resource code names register fields through helper macros.
3. The preprocessor resolves field names to the `__SHIFT` and `_MASK` constants from this header.
4. Register helpers use the constants to preserve unrelated bits, insert field values at the correct shift, and read masked fields back from MMIO registers.

The ordering inside the chunk mirrors hardware block ordering, not program order. Repeated groups for DPP1, DPP2, and DPP3 are intentionally similar because each display pipe has its own register instance.

## State and Persistence

This header does not hold software state and does not persist data. It describes persistent hardware register state in the display engine:

- Gamma LUT and PWL region macros describe values that remain programmed in DPP CM RAM/registers until reprogrammed, reset, or power-gated.
- `*_UPDATE_PENDING`, `*_CONFIG_STATUS`, `*_AUTOFILL_DONE`, `*_MEM_PWR_STATUS`, and perf counter state masks describe hardware status bits that driver code polls or reads.
- `*_MEM_PWR_CTRL` fields for CM, DSCL line-buffer/LUT, and OBUF memory influence power-gated hardware RAM state.
- CRC and performance monitor counters expose diagnostic hardware state used for validation and telemetry.

Because the values are register layout constants, stale or incorrect masks can corrupt hardware state even though this file itself is static.

## Dependencies and Integration Points

Direct dependencies are generated companion headers and AMD display support macros:

- `dcn_1_0_offset.h` provides `mm...` register addresses and base indices for the same register names.
- `drivers/gpu/drm/amd/display/dc/dm_services.h` defines helper patterns such as `FD(reg_field)` that concatenate field names with `__SHIFT` and masks.
- DPP headers and source under `display/dc/dpp/dcn10/` define mask/shift lists and register-field structs that consume these symbols for color, gamma, scaler, cursor, and DPP top programming.
- Resource and initialization paths such as `display/dc/resource/dcn10/dcn10_resource.c` include the DCN 1.0 register definitions when constructing hardware objects for DCN 1.0 ASICs.
- GPIO, IRQ, and other display components include the same header for their own register namespaces elsewhere in the file; this chunk is focused on DPP/CNVC/DSCL/CM/perfmon fields.

The DPP2 and DPP3 macros in this chunk follow the same naming and field-width patterns as DPP1, allowing common or instance-indexed display pipe code to use register-list macros for multiple pipe instances.

## Risks

- Bit layout drift is the main risk. Any mismatch with the ASIC register specification can cause writes to affect the wrong field, especially packed fields such as gamma region offset/segment pairs, CSC matrix coefficients, DSCL ratios, line-buffer partition controls, and memory power controls.
- Boundary risk exists because this chunk begins mid-register group at `CM1_CM_DGAM_RAMB_START_CNTL_G` and ends just before the remaining `DSCL3_SCL_VERT_FILTER_INIT_BOT_C` definitions. Merge logic must combine neighboring chunks before drawing whole-file conclusions.
- Repeated instance naming creates copy/paste risk. `CM1` versus `CM2`, `CNVC_CFG2` versus `CNVC_CFG3`, and `DSCL2` versus `DSCL3` fields are structurally similar but must map to the correct instance and offset header entries.
- Some fields are write-sensitive or status-sensitive. Misusing masks for `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, `*_SOFT_RESET`, `*_UPDATE_PENDING`, perfmon state, or CRC controls can hang display programming sequences or invalidate diagnostics.
- Generated header changes are hard to unit-test directly; regressions often appear as display bring-up failures, color/gamma errors, scaler artifacts, cursor problems, CRC mismatches, or power-management instability.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for AMDGPU DCN 1.0 paths, proving every macro referenced by DPP, CM, CNVC, cursor, DSCL, perfmon, IRQ, GPIO, and resource code still resolves.
- Register programming tests or boot smoke tests on DCN 1.0 hardware that exercise plane enable, pipe reset, scaler setup, cursor enable, color conversion, gamma/degamma/regamma programming, and line-buffer allocation.
- CRC tests using `DPP_TOP{2,3}_DPP_CRC_*` and visual/color tests that detect wrong CSC, gamut remap, clamp, HDR multiplier, denorm, or gamma fields.
- Perf monitor tests that configure `DC_PERFMON13`/`DC_PERFMON14` counters and verify high/low counter reads change as expected.
- Power-management checks that toggle or inspect `CM*_CM_MEM_PWR_*`, `DSCL2_DSCL_MEM_PWR_*`, and `DSCL2_OBUF_MEM_PWR_*` without display underruns or hangs.
- Generated-header comparison against the authoritative ASIC register database, especially for packed masks, shift values above bit 16, and repeated DPP instance groups.
