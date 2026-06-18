# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 39643-42087

## Scope And Purpose

This chunk is part of the generated AMD DCN 1.0 ASIC register field mask/shift header. It contains no executable C logic. Its purpose is to publish compile-time bitfield constants used by AMDGPU display code to compose and decode MMIO register values for DCN 1.0 display hardware.

The path lives under a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The range covers 2,134 preprocessor definitions: 1,059 `__SHIFT` constants and 1,075 mask constants. It begins at the tail of `DP6_DP_SEC_CNTL2` secondary-data packet fields, then covers these address blocks:

- `dce_dc_dcio_dcio_dispdec`: DP6 packet control tail, generic clock/reference controls, UNIPHY A-G link and crossbar controls, DCIO delays, pinstraps, DVO mapping, LVTMA panel power sequencing, backlight PWM, genlock/swaplock pads, DCIO clocks, OTG external-vsync routing, DCIO soft reset, DPHY lane selection, impedance calibration, DPCS interrupts, semaphores, and USB-C flip selection.
- `dce_dc_dcio_dcio_chip_dispdec`: generic GPIO, DVO data pins, DDC1-DDC6/VGA, sync, genlock/swaplock, HPD1-HPD6, panel-power GPIOs, pad strengths, AUX/I2C/DVO analog controls, I2S/SPDIF pins, AUX/HPD electrical controls, GPIO receive enables, and pull-up enables.
- `dce_dc_dcio_dcio_dac_dispdec`: four full-width reserved DAC macro control registers.
- Start of `dce_dc_dcio_dcio_uniphy0_dispdec`: `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED151`, each exposing one 32-bit reserved macro-control field.

This is a generated hardware ABI surface: the macro names and bit positions are the contract consumed by DCN register tables and field-access helper macros.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this chunk. The interface is the generated preprocessor naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the same field.
- Matching register address macros come from the DCN 1.0 address headers, especially `dcn_1_0_offset.h` / `dcn_1_0_d.h` style headers in the same ASIC register tree.
- Display-core helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, `REG_READ`, `FD`, `FN`, and `SF`-style register-table macros consume these generated names indirectly.

Important macro groups in this chunk:

- `DP6_DP_SEC_CNTL2` through `DP6_DP_SEC_CNTL7`, `DP6_DP_DB_CNTL`, and `DP6_DP_MSA_VBID_MISC`: DP6 secondary packet send, pending, missed-deadline, line-number, active, double-buffer, MSA, and VBID override fields.
- `DC_GENERICA`, `DC_GENERICB`, `DC_REF_CLK_CNTL`, and `DC_GPIO_DEBUG`: generic output and reference/debug mux fields, including UNIPHY clock-selector fields and GPIO/DPRX debug selection.
- `UNIPHYA_LINK_CNTL` through `UNIPHYG_CHANNEL_XBAR_CNTL`: seven repeated UNIPHY link-control and channel-crossbar register families for pixel-valid reset, channel inversion, lane-stagger delay, HPD-gated link enable, per-channel crossbar source, and link enable.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `DC_DVODATA_CONFIG`, `DCIO_CLOCK_CNTL`, `DIO_OTG_EXT_VSYNC_CNTL`, `DCIO_SOFT_RESET`, `DCIO_DPHY_SEL`, and `DCIO_USBC_FLIP_EN_SEL`: global DCIO timing, static strap, DVO, clock-gating/test clock, external-vsync routing, soft-reset, DPHY lane-map, and USB-C DisplayPort flip routing fields.
- `LVTMA_PWRSEQ_*` and `BL_PWM_*`: panel power sequencing, DIGON/SYNCEN/BLON override and state fields, power-up/down delays, PWM reference divider, PWM duty/period/fractional enable, and frame-start/register-lock controls.
- `DCIO_GSL_GENLK_PAD_CNTL` and `DCIO_GSL_SWAPLOCK_PAD_CNTL`: genlock/swaplock pad mask and flip-ready selection fields.
- `UNIPHY_IMPCAL_*`, `AUXP_IMPCAL`, `AUXN_IMPCAL`, and `DCIO_IMPCAL_CNTL*`: impedance-calibration enable/status/error/override/period/power-switch fields for UNIPHY links A-F and AUX P/N pads.
- `DCIO_DPCS_TX_INTERRUPT` and `DCIO_DPCS_RX_INTERRUPT`: DPCS TX A-G and RX A interrupt type, mask, and occurrence bits.
- `DCIO_SEMAPHORE0` through `DCIO_SEMAPHORE7`: request/grant bit ranges for DCIO hardware semaphores.
- `DC_GPIO_GENERIC_*`, `DC_GPIO_DVODATA_*`, `DC_GPIO_DDC*`, `DC_GPIO_SYNCA_*`, `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_PWRSEQ_*`, `DC_GPIO_I2CPAD_*`, and `DC_GPIO_I2S_SPDIF_*`: GPIO mask/value/enable/readback register families for generic pins, DVO data/control/clock, DDC/AUX pads, sync, genlock, swaplock, hotplug, panel power, general I2C, and audio pins.
- `DC_GPIO_PAD_STRENGTH_*`, `DC_GPIO_I2CPAD_STRENGTH`, `DVO_STRENGTH_CONTROL`, `DVO_VREF_CONTROL`, `DVO_SKEW_ADJUST`, `DC_GPIO_I2S_SPDIF_STRENGTH`, `DC_GPIO_AUX_CTRL_0`, `DC_GPIO_AUX_CTRL_1`, and `DC_GPIO_AUX_CTRL_2`: pad drive-strength, slew, spike rejection, comparator, bias, voltage-reference, and skew tuning fields.
- `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN`: grouped transmit, receive, and pull-up enables for GPIO, sync, HPD, genlock, swaplock, and panel-power pins.
- `DAC_MACRO_CNTL_RESERVED*` and `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED*`: full-register reserved fields that preserve generated register-map coverage even when field semantics are not public here.

## Control Flow

This chunk has no runtime control flow. Each line is a preprocessor definition, so all behavioral sequencing happens in consumer code that reads and writes MMIO registers.

DCN 1.0 display-core consumers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`

Representative runtime flows enabled by this macro vocabulary:

- GPIO translation maps logical HPD, DDC, generic, sync, and panel-power pins to `DC_GPIO_*_A`, `DC_GPIO_*_EN`, `DC_GPIO_*_Y`, and related mask fields. For example, `hw_translate_dcn10.c` switches over DCN GPIO register offsets and returns the appropriate `DC_GPIO_HPD_A__DC_GPIO_HPDn_A_MASK` or `DC_GPIO_DDCn_A__...CLK/DATA..._MASK` bits.
- Panel-control code shared across DCE/DCN generations uses `LVTMA_PWRSEQ_CNTL`, `LVTMA_PWRSEQ_STATE`, `LVTMA_PWRSEQ_REF_DIV`, `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK` fields to program backlight duty cycle, PWM period, PWM enable, update locks, and panel power state.
- Link-encoder and PHY bring-up code uses DCIO soft-reset and UNIPHY fields to reset individual UNIPHY/DSYNC blocks, configure lane inversion/crossbar routing, choose link-enable behavior, and manage signal-routing side effects.
- Interrupt service code consumes DPCS and display-related generated bit names through register tables so interrupt type, mask, occurrence, ACK, and routing code can refer to fields symbolically rather than using raw constants.
- Modeset/link paths can use DP6 packet and MSA/VBID fields when enabling secondary-data packet scheduling, PPS/GSP transmission, line-numbered packet sends, and double-buffered packet updates for the sixth DP stream.
- Connector sideband paths use DDC/AUX GPIO and pad-control fields when switching pads between AUX and DDC modes, configuring polarity, pull-ups, receive enables, pad strength, spike rejection, and comparator/bias behavior.

Because the header is declarative, it does not protect callers from bad sequencing. Consumers must order writes around reset, link enable, impedance calibration, panel-power delays, PWM update locks, HPD/DDC state transitions, interrupt clears, and semaphores.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. It describes hardware MMIO state.

The represented hardware state includes:

- DP6 packet-scheduler state: pending sends, active sends, line numbers, missed-deadline status, any-line sends, PPS, double-buffer pending/taken/lock/disable, and MSA/VBID overrides.
- DCIO and PHY state: generic clock outputs, reference clock output selection, debug muxes, UNIPHY link enable/reset/channel mapping/inversion, DPHY lane mapping, write-command delays, USB-C flip routing, soft-reset bits, and semaphore grants.
- Calibration state: UNIPHY and AUX impedance calibration enables, status bits, error/ack bits, measured values, step delays, override values, power-switch controls, and calibration intervals.
- Panel and backlight state: LVTMA power-sequence target/current state, DIGON/SYNCEN/BLON controls and polarities, delay counters, PWM duty/period/reference divider/fractional enable, and frame-start lock/update state.
- Connector GPIO state: mask, pull-up/pull-down, receive, output value, output enable, and readback bits for DDC, HPD, sync, generic, DVO, I2C, I2S/SPDIF, genlock, swaplock, and panel-power pins.
- Pad electrical state: drive strengths, slew settings, spike rejection, comparator selection, bias/reference enables, voltage reference, skew adjustment, AUX/DDC pad mode, and audio-pin strength.
- Reserved DAC and UNIPHY macro-control state: full-width register regions that are represented for address-map completeness but have no field semantics in this generated header chunk.

Field lifetime is hardware-specific and not encoded here. Some bits are persistent configuration until modeset, suspend/resume, power-gating, reset, or a later write. Others are read-only status, write-one-to-clear status, self-clearing request bits, sticky interrupt occurrence bits, hardware-latched strap/readback bits, or values sampled by firmware/PHY logic. Names such as `*_PENDING`, `*_TAKEN`, `*_LOCK`, `*_SOFT_RESET`, `*_CALOUT_ERROR_AK`, `*_INT_OCCUR`, `*_GNT`, `*_RECV`, `*_Y`, and `*_PWRSEQ_DONE` are semantic hints only; access type and side effects must come from the hardware specification and caller context.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 register-header set. It is useful only with the matching address and enum headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/`, plus display-core register accessor macros.

Direct include points for `dcn_1_0_sh_mask.h` found in this tree are:

- `display/dc/irq/dcn10/irq_service_dcn10.c`
- `display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `display/dc/gpio/dcn20/hw_translate_dcn20.c`
- `display/dc/resource/dcn10/dcn10_resource.c`

Primary integration areas:

- DCN10/DCN20 GPIO factory and translation layers for logical-to-MMIO mapping of HPD, DDC, sync, generic GPIO, and panel-power pins.
- DCN10 resource construction, where generated `mm` register addresses and field masks populate hardware block register tables.
- IRQ service tables for display and DCIO interrupt mask/status/ack fields.
- Shared panel-control code (`display/dc/dce/dce_panel_cntl.*` and later DCN panel-control implementations) that uses this same generated field vocabulary for backlight and panel power control.
- Link encoder and PHY code in later DCN generations use analogous `DCIO_SOFT_RESET`, `UNIPHY*_LINK_CNTL`, and crossbar fields, so this chunk is also a reference point for generation-to-generation compatibility of DCIO field names.
- Matching address headers such as `dcn_1_0_offset.h` / `dcn_1_0_d.h` provide register offsets; matching enum headers provide symbolic field values where fields are not simple booleans.

The file is generated, so the real upstream dependency is the ASIC register database and generator that produced the DCN 1.0 header family. Hand-edited divergence from sibling address/mask/enum headers is a build-time and hardware-behavior risk.

## Risks And Edge Cases

- Masks and shifts are hardware ABI. A one-bit error can compile successfully while programming the wrong GPIO pin, link lane, reset bit, interrupt mask, backlight value, or calibration control.
- This range contains many repeated instance families: UNIPHY A-G, DDC1-DDC6 plus VGA, HPD1-HPD6, semaphores 0-7, and reserved UNIPHY0 macro registers 0-151. Instance drift is easy to miss in review because names and masks differ only by small suffixes and bit positions.
- `*_MASK_MASK` names are intentional generated artifacts for fields whose logical field name ends in `MASK`. They are awkward but must not be simplified without changing all consumers.
- Several fields are sequencing-sensitive: `DCIO_SOFT_RESET`, `UNIPHY*_LINK_ENABLE`, impedance-calibration `ENABLE`/`OVERRIDE`, `BL_PWM_GRP1_REG_LOCK`, `DP6_DP_DB_LOCK`, DPCS interrupt occurrence bits, and semaphore request/grant fields can cause hangs, missed interrupts, or stale state if handled as ordinary read/write bits.
- GPIO families mix output value (`*_A`), output enable (`*_EN`), readback (`*_Y`), receive-enable, pull-up/pull-down, and mask semantics. Confusing these can break HPD detection, EDID/DDC transactions, AUX/DDC pad mode, panel power, or genlock/swaplock signaling.
- Backlight and panel-power fields affect visible hardware state. Wrong PWM period/duty, reference divider, BLON/DIGON/SYNCEN polarity, or delay programming can produce black panels, flicker, unsafe power sequencing, or resume failures.
- DDC/AUX pad electrical fields affect signal integrity. Incorrect slew, spike rejection, comparator, bias, polarity, pull-up, or drive-strength settings may work on one board and fail on long cables, marginal connectors, or Type-C/DP-alt-mode paths.
- Reserved DAC and UNIPHY macro-control registers are exposed as full-width masks without semantic protection. Consumers should treat them as generated coverage, not as permission to write arbitrary values.
- The chunk boundary is not semantic. It starts after earlier `DP6_DP_SEC_CNTL2` shift definitions and ends in the middle of the `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED*` sequence. The final per-file report must reconcile neighboring chunks for whole-file completeness.

## Test Signals

Useful validation is mainly compile-time plus hardware display behavior:

- Build AMDGPU display code with DCN 1.0 support enabled; missing or renamed macros should fail in DCN10 IRQ, GPIO, resource, panel-control, and register-table code.
- Compare this generated range against the matching DCN 1.0 address headers and adjacent DCN generations (`dcn_2_1_0_sh_mask.h`, `dcn_3_2_0_sh_mask.h`) to catch generation or instance-index drift in repeated DCIO/GPIO families.
- Exercise DCN10 hardware modesets across all available connectors and PHYs: DP/HDMI link bring-up, link disable/enable, suspend/resume, GPU reset recovery, multi-display, and Type-C/DP-alt-mode flip behavior where available.
- Validate connector sideband behavior: HPD connect/disconnect, HPD storm handling, DDC EDID reads on DDC1-DDC6/VGA, AUX/DDC pad mode switching, and GPIO readback/enable transitions.
- Validate panel/backlight behavior on eDP/LVDS-style panels: PWM duty and period programming, brightness changes, power on/off, suspend/resume, DIGON/BLON sequencing, and absence of flicker or black-screen regressions.
- Validate interrupt behavior for DPCS TX/RX and related display paths: masks, occurrence bits, ACK/clear handling, and lack of stuck interrupts after hotplug, link training, or modeset.
- Check negative signals in kernel logs and user-visible behavior: EDID read failures, HPD flapping, link-training loops, black screen, backlight stuck on/off, missed vblank/page events, display underflow, AUX errors, resume failures, and interrupt storms.
