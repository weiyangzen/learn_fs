# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 5264-7875

## Scope

This chunk is a generated AMD DCN 3.5.1 register-offset header slice. It contains preprocessor constants only: 2,377 `#define` entries, of which 1,189 are register offsets and 1,188 are matching `_BASE_IDX` constants inside the requested line range. There are no C functions, structs, enums, variables, branches, allocations, locks, direct MMIO reads/writes, or filesystem persistence paths in this chunk.

The chunk begins in the middle of `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec`: lines 5242-5263 define the first CNVC CFG2 offsets, while this chunk starts at `regCNVC_CFG2_COLOR_KEYER_GREEN`. It also ends in the middle of `dce_dc_dio_dp_aux4_dispdec`: the final line in scope is `regDP_AUX4_AUX_DPHY_TX_CONTROL`, and the matching `_BASE_IDX` plus the remaining AUX4 registers continue after line 7875. Final file-level research should merge neighboring chunks before making whole-block completeness claims for CNVC CFG2 or DP AUX4.

Although this repository path is under a local `ceph-client` source mirror, the file itself is AMDGPU Display Core hardware metadata for the DCN 3.5.1 display engine.

## Purpose And Hardware Surface

`dcn_3_5_1_offset.h` supplies symbolic MMIO register offsets for the DCN 3.5.1 ASIC register map. Runtime display code combines each `reg...` value with `ctx->dcn_reg_offsets[reg..._BASE_IDX]` to produce final MMIO addresses. The paired `dcn_3_5_1_sh_mask.h` file supplies the matching field shifts and masks.

This range covers the second half of the display pipe frontend and a large part of the backend/link timing surface:

- Tail of DPP2 converter configuration, then DPP2 cursor, DSCL, color-management, and DPP perfmon registers.
- Full DPP3 top, converter configuration, cursor, DSCL, color-management, and DPP perfmon registers.
- OPP instances 0-3, including FMT output formatting, DPG pattern generation, OPP buffer control, pipe control, pipe CRC, top-level OPP control, DSCRM forward configuration, and OPP perfmon.
- OPTC/ODM/OTG instances 0-3, including timing generator totals/blanking/sync, vertical interrupt controls, global swap/sync, CRC, DRR/VTOTAL min/max, stereo, memory power, test/debug, global swap lock source selection, and OPTC perfmon.
- DIO registers for I2C/DDC, DIO miscellaneous link controls/status, HPD0-4 hotplug blocks, DIO perfmon, and DP AUX0-4 control/status/PHY/sync registers.

The numeric offsets in this chunk are not generic register IDs; they are part of the ASIC ABI. Incorrect values compile cleanly if names still exist, but they drive the display driver to the wrong hardware address at runtime.

## Important Definitions

The exported interface is a mechanically generated macro namespace:

- `reg<NAME>`: register offset within a generated base segment.
- `reg<NAME>_BASE_IDX`: index into `ctx->dcn_reg_offsets[]`, used by DCN351 resource and IRQ code to add the correct base address.

The consuming macros in `dcn351_resource.c` and `irq_service_dcn351.c` build final offsets with token pasting. Examples include `SR(reg_name)`, `SRI(reg_name, block, id)`, `SRI_ARR(reg_name, block, id)`, and `SR_ARR(reg_name, id)`, all of which evaluate to:

```c
BASE(reg..._BASE_IDX) + reg...
```

Important register families in this chunk:

- `CNVC_CFG2`, `CNVC_CUR2`, `DSCL2`, `CM2`: DPP2 color conversion, cursor color, scaling/filtering/line-buffer controls, post-CSC/gamut/gamma/degamma/shaper/3D LUT/HDR multiplier/debug controls, and DPP2 perfmon 13.
- `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, `CM3`: the same DPP frontend surface for pipe 3, with DPP3 perfmon 14.
- `FMT0-3`: output formatter clamp/dynamic expansion/dither/bit-depth/random-seed/alpha/420/422 format-control registers.
- `DPG0-3`: display pattern generator color components, ramps, bit-depth, stereo, and status registers.
- `OPPBUF0-3`, `OPP_PIPE0-3`, `OPP_PIPE_CRC0-3`: OPP buffer controls, pipe control, and output CRC control/window/result registers.
- `OPP_TOP`, `DSCRM0-3`, `DC_PERFMON16`: top-level OPP clock/ABM controls, DSC forward configuration per OPP, and OPP perf counters.
- `ODM0-3`: OPTC input/global control, data source selection, memory control/status, and spare registers.
- `OTG0-3`: 115 registers per timing generator instance, covering timing totals, active/display regions, blanking, sync, controls, stereoscopy, vertical interrupts, global sync/swap lock, CRC, DRR timing, underrun, double-buffer status, memory power, and debug.
- `GSL_SOURCE_SELECT`, `GSL_GROUP_SELECT`, `GSL_CONTROL`, `OPTC_DATA_SOURCE_SELECT`, `OPTC_INPUT_CLOCK_CONTROL`, `OPTC_INPUT_GLOBAL_CONTROL`, `OPTC_MISC_SPARE_REGISTER`: OPTC-wide misc/global-swap-lock selection and input control.
- `DC_PERFMON17`, `DC_PERFMON18`: OPTC and DIO display perfmon blocks.
- `DC_I2C_*`: DIO DDC/I2C software control, arbitration, transaction setup, speed, setup/hold timing, data, DDC setup, EDID detection, reset, and interrupt registers.
- `DIO_*` and `DIO_LINK[A-F]_CNTL`: DIO status, stream encoder count, memory power, stream encoder clock controls, power control, symbol clock controls, and per-link controls.
- `HPD0-4`: hotplug interrupt status/control, HPD control, filter, and toggle-filter registers.
- `DP_AUX0-4`: DisplayPort AUX control, software control/status/data, arbitration, interrupt control, LS status/data, PHY TX/RX controls/status, GTC sync controls/status, and PHY wake controls. AUX4 is partial in this chunk.

## Address-Block Inventory

The generated block comments in this range identify the following address blocks and line spans. Register counts exclude `_BASE_IDX` lines.

| Lines | Address block | Base | Registers | Notes |
| --- | --- | --- | ---: | --- |
| 5264-5303 | `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec` | `0xb58` | 20 in-scope | Partial leading block; starts at green/blue color-keyer and pre-CSC tail. |
| 5308-5314 | `dce_dc_dpp2_dispdec_cnvc_cur_dispdec` | `0xb58` | 4 | Cursor control and colors for DPP2. |
| 5320-5386 | `dce_dc_dpp2_dispdec_dscl_dispdec` | `0xb58` | 34 | DPP2 scaler coefficients, ratios, recout/MPC sizing, line buffer, and memory power. |
| 5392-5610 | `dce_dc_dpp2_dispdec_cm_dispdec` | `0xb58` | 110 | DPP2 color management, LUTs, HDR multiplier, and debug. |
| 5616-5632 | `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` | `0x43e8` | 9 | DPP2 perfmon 13. |
| 5638-6022 | `dce_dc_dpp3_dispdec_*` | `0x1104` | 185 | Full DPP3 top, CNVC, DSCL, and CM coverage. |
| 6028-6044 | `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` | `0x4994` | 9 | DPP3 perfmon 14. |
| 6050-6371 | `dce_dc_opp_*0-3_dispdec` | `0x0`, `0x168`, `0x2d0`, `0x438` | 124 | Repeated FMT, DPG, OPPBUF, OPP pipe, and pipe CRC blocks for four OPP instances. |
| 6377-6403 | OPP top and `DSCRM0-3` | mixed | 6 | OPP top controls and DSC forward selection. |
| 6409-6425 | `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec` | `0x6af8` | 9 | OPP perfmon 16. |
| 6431-6505 | `dce_dc_optc_odm0-3_dispdec` | `0x0`..`0xc0` | 32 | ODM input/source/memory controls. |
| 6511-7441 | `dce_dc_optc_otg0-3_dispdec` | `0x0`, `0x200`, `0x400`, `0x600` | 460 | Four complete OTG timing-generator instances. |
| 7447-7459 | `dce_dc_optc_optc_misc_dispdec` | `0x0` | 7 | GSL and OPTC-wide input controls. |
| 7465-7481 | `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec` | `0x79a8` | 9 | OPTC perfmon 17. |
| 7487-7591 | `dce_dc_dio_dout_i2c_dispdec` and `dce_dc_dio_dio_misc_dispdec` | `0x0` | 51 | I2C/DDC and DIO link/control/status registers. |
| 7597-7661 | `dce_dc_dio_hpd0-4_dispdec` | `0x0`..`0x80` | 25 | Five HPD interrupt/control/filter blocks. |
| 7667-7683 | `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec` | `0x7d10` | 9 | DIO perfmon 18. |
| 7689-7875 | `dce_dc_dio_dp_aux0-4_dispdec` | `0x0`..`0x1c0` | 86 in-scope | AUX0-3 complete; AUX4 partial at the end. |

## Control Flow And Runtime Behavior

This header has no runtime control flow. Behavior appears only after the generated constants are included by DCN351 code and expanded into register tables:

1. `dcn351_resource.c` includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`, defines `BASE(seg)` as `ctx->dcn_reg_offsets[seg]`, and expands register-list macros into typed structures.
2. `dpp_regs_init(id)` uses `DPP_REG_LIST_DCN35_RI(id)` to populate `struct dcn3_dpp_registers dpp_regs[4]`. The DPP2 and DPP3 offsets in this chunk feed pipe instances 2 and 3 for color conversion, scaling, color management, and diagnostics.
3. `opp_regs_init(id)` uses `OPP_REG_LIST_DCN35_RI(id)` to populate `struct dcn35_opp_registers opp_regs[4]` from the FMT/DPG/OPPBUF/OPP pipe/CRC definitions in this chunk.
4. `optc_regs_init(id)` uses `OPTC_COMMON_REG_LIST_DCN3_5_RI(id)` to populate `struct dcn_optc_registers optc_regs[4]` from the ODM/OTG/OPTC misc definitions in this chunk.
5. `aux_regs_init(id)`, `hpd_regs_init(id)`, and `aux_engine_regs_init(id)` build link/AUX/HPD register structures for five physical link-side instances. The AUX and HPD constants in this chunk are the address side of DDC, DP AUX, HPD interrupt, and link training support.
6. `irq_service_dcn351.c` uses the same `BASE(reg..._BASE_IDX) + reg...` pattern for HPD, HPD RX, VUPDATE, VBLANK, and VLINE0 interrupt source table entries. The `HPD0-4` and `OTG0-3` registers in this range are therefore part of interrupt enable/ack/status mapping.
7. Runtime display code calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_UPDATE`, and `REG_WAIT` through those typed structures. The offsets here choose the target register; the paired shift/mask header chooses the field inside that register.

The sequencing rules are not encoded here. Higher-level DCN code must still order plane setup, scaler programming, color pipeline programming, timing generator enable, output formatter enable, link/AUX transactions, interrupt acknowledgement, and power transitions correctly.

## State And Persistence Behavior

This chunk stores no software state. It describes hardware register state that lives in DCN 3.5.1 display, timing, output, and link blocks.

Programmed hardware state represented by these offsets includes:

- DPP converter and color-management state: color keying, pre/post CSC matrices, degamma/gamma/shaper control, 3D LUT access, gamut remap, HDR multiplier, alpha/dealpha/realpha, and cursor colors.
- DPP scaler state: coefficient RAM access, taps, scale ratios, filter initial conditions, overscan, recout/MPC sizing, line-buffer format and memory control.
- OPP output state: clamp, bit-depth expansion, dithering seeds and control, output format controls, display pattern generator values, pipe controls, OPP buffer settings, ABM control, and pipe CRC windows/results.
- OPTC/OTG timing state: horizontal/vertical totals, blanking, sync widths, active/display areas, control/status, stereo, CRC windows/results, dynamic refresh timing, global swap/sync settings, vertical interrupt position/ack/enable, and memory power controls.
- DIO link-side state: I2C/DDC transaction parameters and data, link clock/control registers, HPD filters and interrupt state, DP AUX transaction state, AUX PHY controls/status, and AUX GTC synchronization.
- Perfmon counter state for DPP, OPP, OPTC, and DIO instrumentation blocks.

Persistence is hardware-defined. Configuration generally survives until the next modeset, plane update, link retraining, hotplug event, power-gating transition, suspend/resume, driver reset, or ASIC reset. Status, interrupt, CRC, perfmon, busy, done, and clear registers are volatile and may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant clock and power domain is active. The generated offset header does not encode any of those access semantics.

## Dependencies And Integration Points

This chunk depends on name and numeric consistency across the generated DCN 3.5.1 register header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h` must provide matching field names, shifts, and masks for the registers referenced here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c` consumes these offsets for DCN351 resource construction. Relevant local initializers include `dpp_regs_init`, `opp_regs_init`, `optc_regs_init`, `aux_regs_init`, `hpd_regs_init`, and `aux_engine_regs_init`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c` consumes HPD and OTG offsets for IRQ source enable/ack/status tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c` includes the same offset header for DMUB register initialization, although the specific lines in this chunk are primarily display pipe/link register families rather than the core DMCUB mailbox register set.
- Shared block headers such as `dcn35_dpp.h`, `dcn35_opp.h`, `dcn35_optc.h`, `dce_aux.h`, `dce_i2c.h`, and DIO/link encoder headers define the register-list and field-list macros that token-paste these generated names.

The base-index pattern is a key integration constraint. Most constants in this chunk have `_BASE_IDX` value `2`, but some address-block comments expose local base offsets such as `0xb58`, `0x1104`, `0x6af8`, or `0x79a8`. Runtime code must use both pieces: the generated offset and the base segment selected by `_BASE_IDX`.

## Risks And Maintenance Notes

- Generated-offset drift is the main risk. A wrong numeric offset can target a valid but unrelated MMIO register, producing display corruption, missed interrupts, stuck link transactions, or power-management failures without a compile-time error.
- The chunk has partial block boundaries. `CNVC_CFG2` starts before this range and `DP_AUX4` continues after it; any completeness audit needs adjacent chunks.
- Repeated instance families can hide one-instance errors. DPP2/DPP3, OPP0-3, ODM0-3, OTG0-3, HPD0-4, and DP_AUX0-4 should follow intentional instance strides. A single bad offset can affect only one pipe or connector.
- DPP color pipeline registers are user-visible and precision-sensitive. Bad CSC, LUT, degamma/gamma, HDR multiplier, or alpha offsets can cause incorrect color, banding, broken HDR/SDR conversion, cursor color issues, or failures only on specific pixel formats.
- DSCL and line-buffer offsets are timing-sensitive. Incorrect scale ratio, filter init, recout/MPC size, or line-buffer memory offsets can cause black screens, underflow, corrupted scaling, or resume-only failures.
- OPP/FMT dither and format offsets affect sink-visible output. Errors can produce wrong bit depth, broken YCbCr 4:2:0/4:2:2 output, CRC mismatch, or display artifacts that may not appear on simple RGB modes.
- OTG registers include interrupt, timing, global sync, DRR, and swap-lock controls. Bad offsets can cause vblank/vline interrupt loss, page-flip timing bugs, tearing, variable-refresh issues, stereo issues, or blanking/sync misprogramming.
- HPD and AUX registers are hotplug/link-training critical. Wrong HPD status/ack/control or AUX SW data/status/PHY offsets can cause missed hotplug, interrupt storms, DP link-training timeouts, failed DPCD/EDID reads, or unreliable wake from low power.
- Perfmon and CRC registers are diagnostics but still side-effect-sensitive. Incorrect counter-control or CRC-control offsets can make validation misleading or disturb active display diagnostics.
- The generated names are untyped macros. Renaming or deleting a macro often fails at build time, but changing the number behind a stable name may only fail on actual DCN351 hardware.

## Test Signals

Useful validation should combine generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU Display Core with DCN351 enabled and confirm `dcn351_resource.c`, `irq_service_dcn351.c`, and `dmub_dcn351.c` compile against `dcn_3_5_1_offset.h` and the paired shift/mask header.
- Mechanically check every in-scope register has a matching `_BASE_IDX` where the pair lies inside the chunk; allow the known trailing boundary exception for `regDP_AUX4_AUX_DPHY_TX_CONTROL`, whose `_BASE_IDX` is outside the requested range.
- Diff this range against AMD's authoritative generated register database and nearby generated headers such as `dcn_3_5_0_offset.h` and `dcn_3_6_0_offset.h` where register layouts are expected to be compatible.
- Verify repeated-instance strides and register counts for DPP2/DPP3, OPP0-3, ODM0-3, OTG0-3, HPD0-4, and DP_AUX0-4; investigate any non-uniformity that is not documented by the hardware spec.
- Exercise four-pipe display modes on DCN351 hardware, including plane scaling, cursor enable, color transformations, HDR metadata/color pipeline changes, degamma/gamma LUT updates, 3D LUT access, and mixed pixel formats.
- Exercise OPP/FMT output paths across RGB and YCbCr modes, 6/8/10/12 bpc, dithering, 4:2:0 and 4:2:2 output, CRC capture, pattern generator output, and ABM interaction.
- Exercise OTG timing paths with modeset, blank/unblank, page flip, vblank/vline interrupts, variable refresh/DRR, stereo where available, global swap lock, suspend/resume, and multi-display sync scenarios.
- Exercise DIO link-side paths: HPD plug/unplug and HPD RX, DP AUX DPCD reads/writes, EDID over DDC/I2C, link training, low-power wake, and connector combinations that use AUX/HPD instances 0 through 4.
- Monitor kernel logs, debugfs diagnostics, vblank counters, page-flip completion, AUX timeout counters, HPD storm handling, CRC/perfmon output, underflow reporting, and resume/hotplug recovery after display power transitions.

## Chunk-Specific Summary

Lines 5264-7875 define DCN 3.5.1 register offsets for DPP2 tail registers, full DPP3 frontend registers, four OPP backend instances, four OPTC/OTG timing instances, and a large DIO/HPD/AUX link-control range. The content is generated register ABI rather than executable logic. Correctness depends on exact offset/base-index values, consistent repeated-instance layout, synchronization with `dcn_3_5_1_sh_mask.h`, and validation on real DCN351 display/link hardware across color, scaling, timing, output-format, hotplug, AUX/DDC, interrupt, CRC, perfmon, and power-management scenarios.
