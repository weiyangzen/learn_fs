# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 46600-49100

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes preprocessor constants for MMIO register field shifts and bit masks used by AMDGPU display code when programming DCN 3.1.4 display links, GPIO/AUX/DDC pads, panel power sequencing, backlight PWM, and the first Display Stream Compression block.

The requested range covers 2,501 physical lines with 2,101 `#define` entries: 1,051 `__SHIFT` macros and 1,050 `_MASK` macros. It starts at the final two masks for `DP4_DP_ALPM_CNTL`, then covers `DP4` secondary-data packet and AUX-less ALPM fields, several DCIO/DCIO-chip address blocks, `UNIPHY1` through `UNIPHY4` reserved macro-control fields, `PWRSEQ0` and `PWRSEQ1` panel/backlight fields, and the beginning of `DSC0` through `DSCC0_DSCC_PPS_CONFIG13`. The line range ends inside `DSCC0_DSCC_PPS_CONFIG13`, so later chunk research must cover the rest of the DSC PPS/range and diagnostic fields.

Although the repository path is under a `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

These constants are consumed with the matching DCN 3.1.4 offset header and register helper macros. `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes `dcn/dcn_3_1_4_offset.h` and `dcn/dcn_3_1_4_sh_mask.h`, then builds mask/shift tables used by DCN 3.1.4 resource construction. For DSC specifically, `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` uses `DSC_SF()` and `DSC_REG_LIST_SH_MASK_DCN20(mask_sh)` to paste names such as `DSCC0_DSCC_PPS_CONFIG1__BITS_PER_PIXEL_MASK` into typed field tables.

Major register families in this slice:

- `DP4_DP_GSP8_CNTL` through `DP4_DP_GSP11_CNTL`, `DP4_DP_GSP_EN_DB_STATUS`, and `DP4_DP_AUXLESS_ALPM_CNTL1` through `CNTL5`: DisplayPort instance 4 secondary generic-stream-packet controls, double-buffer pending status, main-link PHY sleep timing, AUX-less ALPM wake/FEC events, hardware-mode state, frame/line scheduling, and wakeup interrupt fields.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA/B/C_LINK_CNTL`, `UNIPHY[A-E]_CHANNEL_XBAR_CNTL`, `DC_PINSTRAPS`, `INTERCEPT_STATE`, `DCIO_PATTERN_GEN_*`, GSL/genlock/swaplock pad controls, and `DCIO_SOFT_RESET`: display IO clocks, generic outputs, link-channel inversion/crossbar mapping, pinstrap observations, pattern generation, global sync/lock pad routing, and soft reset fields for UNIPHY/DSYNC/PWRSEQ blocks.
- `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1` through `DDC5`, `DC_GPIO_DDCVGA`, `DC_GPIO_GENLK`, `DC_GPIO_HPD`, `DC_GPIO_PWRSEQ*`, `PHY_AUX_CNTL`, `DC_GPIO_TX12_EN`, `DC_GPIO_AUX_CTRL_0` through `5`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, and `AUXI2C_PAD_ALL_PWR_OK`: GPIO mask/output/input/enable fields, DDC/AUX pad mode and receive state, hotplug detect mask/enable/output fields, pad strength, AUX level/control fields, and power-good state.
- `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`, repeated for `UNIPHY2`, `UNIPHY3`, and `UNIPHY4`: full-width reserved macro-control register definitions. Each reserved register exposes a single `UNIPHY_MACRO_CNTL_RESERVED` field with shift 0 and mask `0xFFFFFFFFL`.
- `PWRSEQ0_*` and `PWRSEQ1_*`: panel GPIO enables/drive controls, panel power-sequence control/state, power-up/down delays, reference dividers, backlight PWM control/period, group-1 register locking/double-buffer update state, frame-start update behavior, and spare fields.
- `DSC_TOP0_*`, `DSCCIF0_*`, and the first part of `DSCC0_*`: DSC top clock/debug controls, DSC input-interface underflow recovery/status, input pixel format and component depth, picture size, compressor slice topology, double-buffer update status, rate-buffer interrupt/status bits, and PPS fields from config 0 through the first `RC_BUF_THRESH4` mask in config 13.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by the AMD display driver:

1. DCN 3.1.4 resource and hardware blocks include the generated offset and shift/mask headers.
2. Register-list macros paste instance, register, and field tokens into constants such as `DC_GPIO_AUX_CTRL_5__DDC_PAD3_I2CMODE_MASK`, `PWRSEQ0_BL_PWM_CNTL__BL_PWM_EN_MASK`, or `DSCC0_DSCC_PPS_CONFIG13__RC_BUF_THRESH4_MASK`.
3. `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `LE_SF`, `DSC_SF`, and related helper patterns use those constants to build MMIO writes or field tables.
4. Runtime display flows program these registers during link initialization, AUX/DDC transactions, hotplug handling, panel power-up/down, backlight updates, DP ALPM entry/exit, DSC PPS programming, and error/status polling.

The macros do not encode ordering. Consumers must still perform the hardware-specific sequence: hold or release soft resets at the right time, set pad modes before AUX/DDC activity, observe HPD and power-good state, lock or double-buffer backlight updates where required, program DSC PPS fields before enabling the compressor path, and clear or mask status/interrupt bits with correct access semantics.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on its own. It describes hardware register fields whose state is held by the display ASIC.

Hardware state represented by the fields includes DP4 secondary-packet scheduling, ALPM sleep/wakeup timing, link PHY sleep state, DCIO clock/test selections, UNIPHY channel polarity and source crossbar state, GPIO output/mask/input state, DDC/AUX pad modes and levels, HPD detect state, PWRSEQ and BLON/DIGON/VARY_BL panel GPIO state, panel power-sequencer state, PWM period/duty/update state, and DSC0 compressor/PPS/configuration/status state.

Persistence is hardware-defined. Configuration fields generally survive until modeset reprogramming, link/panel reset, display power-gating, suspend/resume, or ASIC reset. Status-like fields such as `*_PENDING`, `*_ACTIVE`, `*_OCCURRED`, `*_STATUS`, `*_STATE`, `*_RECV`, `FRAME_START_EVENT_RECOGNIZED`, and `AUXI2C_PAD_ALL_PWR_OK` may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register specification. This generated header only gives bit positions; it does not describe access type or side effects.

## Dependencies And Integration Points

The constants in this range must match the generated DCN 3.1.4 register-offset file at `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`. They are also tied to DCN base-address definitions and register helper code included by `dcn314_resource.c`.

Important in-tree integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes this header and constructs DCN 3.1.4 resource register tables. The file also locally supplies missing `DSCC0_DSCC_CONFIG0__ICH_RESET_AT_END_OF_LINE` shift/mask definitions, showing that generated DSC field coverage is supplemented in the resource layer.
- `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h`, whose `DSC_REG_LIST_DCN20(id)` and `DSC_REG_LIST_SH_MASK_DCN20(mask_sh)` consume the `DSC_TOP0`, `DSCCIF0`, and `DSCC0` fields in this chunk for DSC programming across DCN generations.
- Link-encoder helpers such as `dcn20_link_encoder.h` and `dcn21_link_encoder.h`, which expose `DCIO_SOFT_RESET` fields for UNIPHY reset control.
- GPIO/DDC/AUX helpers such as `display/dc/gpio/ddc_regs.h`, which reference `DC_GPIO_AUX_CTRL_*` and DDC pad fields through generated shift/mask names.
- Panel-control and hardware-sequencer layers, which use panel power-sequence and backlight PWM fields to coordinate embedded-panel power, brightness, and frame-start update behavior.

The chunk is boundary-sensitive. It starts after most of `DP4_DP_ALPM_CNTL` was defined in the previous chunk and ends before `DSCC0_DSCC_PPS_CONFIG13` is complete. Final file-level research should merge neighboring chunks before making complete claims about DP4 ALPM and DSC0 PPS coverage.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These are untyped macros, so a wrong bit position can compile successfully while corrupting adjacent hardware fields.
- Many fields are side-effect-sensitive. DP secondary-packet send bits, ALPM wakeup/FEC pending bits, HPD receive/status fields, AUX/DDC pad controls, panel power-sequencer target/override bits, PWM update locks, DSC interrupt/status bits, and DSC double-buffer pending bits may not tolerate generic read-modify-write patterns.
- Repeated generated families are copy-sensitive. `DP4_DP_GSP8` through `GSP11`, DDC1 through DDC5 plus DDCVGA, UNIPHY reserved blocks, and `PWRSEQ0`/`PWRSEQ1` are structurally similar; a single instance-prefix or mask-width error can break only one connector, panel, or PHY.
- GPIO and pad fields affect physical link behavior. Incorrect AUX/DDC pad mode, pull-up, receive-enable, TX12, or pad-strength programming can produce link-training failures, EDID/I2C failures, missing HPD, or intermittent hotplug.
- Panel power and backlight fields have user-visible and hardware-safety implications. Bad delay, polarity, override, or PWM lock/update fields can cause blank panels, flicker, incorrect brightness, or power sequencing outside panel requirements.
- DSC PPS fields are tightly coupled to `drm_dsc` parameters and link bandwidth calculations. Wrong picture/slice dimensions, bits-per-pixel/component, chunk size, rate-control model, offsets, or buffer thresholds can cause corrupted output only in modes that require DSC.
- Reserved UNIPHY macro-control registers expose full 32-bit masks. The header defines their layout but does not imply that arbitrary writes are safe; consumers should only touch reserved fields when backed by hardware programming guidance.

## Test Signals

Useful validation is a combination of generated-header consistency, build coverage, and hardware behavior:

- Build AMDGPU display paths for DCN 3.1.4 so includes of `dcn_3_1_4_sh_mask.h`, `dcn314_resource.c`, link encoder tables, GPIO/DDC helpers, panel-control code, and DSC register-table construction catch missing or renamed macros.
- Mechanically verify that every complete field in lines 46600-49100 has a matching `__SHIFT` and `_MASK` pair, accounting for the intentional boundary exceptions at the beginning `DP4_DP_ALPM_CNTL` masks and the ending partial `DSCC0_DSCC_PPS_CONFIG13`.
- Compare this generated chunk against AMD's authoritative DCN 3.1.4 register database and adjacent DCN generation headers where repeated layouts are expected to be identical.
- Exercise DP4 behavior on hardware: secondary-data packet send paths, MST/MSO-related packet controls, AUX-less ALPM sleep/wakeup, FEC wake scheduling, and deadline/pending status reporting.
- Test DDC/AUX and HPD across all represented pads/connectors: EDID reads, AUX transactions, hotplug/unplug, suspend/resume, MST topology changes, and failure recovery after transient HPD or AUX errors.
- Test embedded-panel sequencing and backlight: cold boot, modeset, blank/unblank, suspend/resume, brightness changes, frame-start synchronized PWM updates, and both PWRSEQ0/PWRSEQ1 paths where available.
- Validate DSC-required modes, especially high-resolution/high-refresh configurations, DSC enable/disable transitions, suspend/resume with DSC, and visual corruption or DSC underflow/overflow status.

## Cross-Chunk Notes

The previous chunk owns most of `DP4_DP_ALPM_CNTL`; this chunk only includes its final `DP_ML_PHY_SLEEP_PATTERN_NUM_MASK` and `DP_ML_PHY_SLEEP_STANDBY_LINE_NUM_MASK` lines before the `DP4_DP_GSP8_CNTL` block. The next chunk must continue `DSCC0_DSCC_PPS_CONFIG13` after `RC_BUF_THRESH4_MASK`, then cover the remaining DSC0 PPS threshold/range, memory-power, error, fullness, and debug fields. The final per-file document should reconcile those boundaries before summarizing full DP4 ALPM or DSC0 behavior.
