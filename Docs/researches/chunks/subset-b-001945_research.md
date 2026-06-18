# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 39691-42212

## Purpose

This chunk is a generated AMD DCN 3.2.0 register shift/mask header segment. It contains no executable C code; it publishes preprocessor constants that describe hardware register bit positions (`__SHIFT`) and field masks (`_MASK`) for display I/O, GPIO, UNIPHY, panel power/backlight sequencing, and the beginning of DSC compressor registers.

The range starts in the middle of `DIO_CLK_CNTL3`, then covers the DCIO/DIO display decode register blocks, the DCIO chip GPIO block, UNIPHY macro-reserved control blocks for UNIPHY instances 0 through 4, the panel power sequencer and backlight PWM block, and the start of `DSCC0` display stream compression PPS fields. It ends mid-register at `DSCC0_DSCC_PPS_CONFIG21__RANGE_MIN_QP11__SHIFT`, so later chunk reconciliation must merge this with the following range before making complete claims about the DSC PPS range tables.

The chunk defines 2,085 preprocessor constants: 1,038 shift constants and 1,047 mask constants. Although this source tree path is under `ceph-client`, the file is AMDGPU display hardware metadata, not distributed-filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, locks, memory allocation paths, includes, or direct MMIO operations in this chunk. The exposed interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, compose, or update that field.
- `// addressBlock: ...`: generated grouping comments that align the constants with hardware register blocks.

Major register families in this range are:

- DIO link and HDMI status controls: tail constants for `DIO_CLK_CNTL3`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, and `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL`. These describe TMDS symbol-clock gate disables, HDMI RX-status timer enable/type/status/mask/interval fields, and per-link encoder selection fields (`ENC_TYPE_SEL`, `HPO_HDMI_ENC_SEL`, `HPO_DP_ENC_SEL`).
- DCIO display decode registers: `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA` through `UNIPHYE_CHANNEL_XBAR_CNTL`, `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `DCIO_SPARE`, `INTERCEPT_STATE`, pattern generator controls, backlight-frame-start display select, GSL/genlock and swaplock pad controls, and `DCIO_SOFT_RESET`.
- DCIO GPIO/DDC/AUX/HPD registers: `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC5_*`, `DC_GPIO_DDCVGA_*`, `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, drive-strength and pad-strength controls, `PHY_AUX_CNTL`, AUX control registers 0 through 5, RX enable, pull-up enable, TX impedance selection, TX12 enable, and `AUXI2C_PAD_ALL_PWR_OK`.
- UNIPHY macro reserved controls: `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`, repeated for UNIPHY1, UNIPHY2, UNIPHY3, and UNIPHY4. These are full-width or reserved macro-control bitfield definitions used by low-level PHY programming or diagnostics.
- Panel power and backlight registers: `DC_GPIO_PWRSEQ_EN`, `DC_GPIO_PWRSEQ_CTRL`, `DC_GPIO_PWRSEQ_MASK`, `DC_GPIO_PWRSEQ_A_Y`, `PANEL_PWRSEQ_CNTL`, `PANEL_PWRSEQ_STATE`, `PANEL_PWRSEQ_DELAY1`, `PANEL_PWRSEQ_DELAY2`, `PANEL_PWRSEQ_REF_DIV1`, `PANEL_PWRSEQ_REF_DIV2`, `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, `BL_PWM_GRP1_REG_LOCK`, and `PWRSEQ_SPARE`.
- DSC compressor registers: `DSCC0_DSCC_CONFIG0`, `DSCC0_DSCC_CONFIG1`, `DSCC0_DSCC_STATUS`, `DSCC0_DSCC_INTERRUPT_CONTROL_STATUS`, and `DSCC0_DSCC_PPS_CONFIG0` through the beginning of `DSCC0_DSCC_PPS_CONFIG21`.

Important field categories include:

- Clock and routing fields for DCIO test-clock selection, display-clock gating, reference-clock output, UNIPHY channel crossbar sources, UNIPHY test clock muxing, TMDS clock gating, and DIO link-to-HPO encoder selection.
- Connector-management fields for DDC data/clock GPIOs, HPD GPIOs, AUX control, AUX/I2C pad power status, GPIO direction/value/mask registers, pad strength, pull-up enable, RX enable, TX drive, and TX impedance.
- Synchronization/debug fields for generic A/B outputs, genlock/swaplock pad controls, pattern generator pattern/enable, intercept-state reporting, pin straps, spare fields, and DCIO soft resets.
- Embedded-panel fields for power-sequence enable/control/masks/output state, panel power delays, reference dividers, backlight PWM duty/period/fractional mode/enable, and PWM group lock/update state.
- DSC PPS fields for Display Stream Compression configuration, status, interrupts, dimensions, slice geometry, transmit/decoder delay, scaling intervals, BPG offsets, rate-control model size, quantization limits, target offsets, rate-control buffer thresholds, and range min/max QP plus BPG offsets.

## Control Flow

This chunk has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes both `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`, then feeds these constants into register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `FD_MASK`, and `FD_SHIFT`.

Expected runtime usage is:

1. A DCN 3.2 component selects a symbolic register name and field.
2. The matching offset header supplies the register address or indexed instance offset.
3. This shift/mask header supplies the bit geometry for the field.
4. The register helper composes MMIO reads, writes, read-modify-writes, polling, or generated register-table initialization.

Observed direct include sites for the DCN 3.2.0 offset and shift/mask headers include:

- `display/dmub/src/dmub_dcn32.c`, which initializes DMUB register offset, mask, and shift tables.
- `display/dc/resource/dcn32/dcn32_resource.c`, which builds DCN32 hardware resource register tables, including DSC register tables.
- `display/dc/gpio/dcn32/hw_translate_dcn32.c`, which maps GPIO offsets/masks to logical GPIO IDs and maps logical DDC, HPD, and generic GPIO IDs back to DCN32 register offsets/masks.
- `display/dc/gpio/dcn32/hw_factory_dcn32.c`, which builds HPD, DDC, and generic GPIO register/mask/shift tables for DCN32.
- `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, and `amdgpu/gmc_v11_0.c`, which also consume DCN32 generated register metadata.

The chunk itself does not encode sequencing constraints. Hardware-specific callers must still sequence HPD/DDC/AUX access, link encoder selection, UNIPHY routing, soft resets, panel power, PWM programming, and DSC PPS programming according to the DCN display pipeline rules.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk, memory, firmware, or device registers by itself. It describes MMIO-backed hardware state in DCN 3.2.0 display blocks.

The represented hardware state includes:

- Link and clock routing state for DIO links A through F, HPO HDMI/DP encoder selection, DCIO test/reference clocks, UNIPHY channel crossbars, TMDS clock gating, and DCIO write-command delay.
- Connector pad state for GPIO generic lines, DDC data/clock lines, VGA DDC, HPD lines, AUX control, RX enable, pull-up enable, drive strength, pad strength, and pad power readiness.
- Synchronization and debug state for generic outputs, genlock, swaplock, intercept state, pattern generation, pin straps, spare registers, and DCIO reset controls.
- Embedded-panel state for power sequencing, power-on/off delays, backlight PWM duty and period, PWM register locks, and power-sequencer reference dividers.
- DSC state for compressor configuration/status/interrupts and PPS parameters used to generate compressed display streams.

Persistence is hardware-defined. Programmed MMIO values usually last until modeset reprogramming, power gating, suspend/resume, reset, or driver teardown. Status and interrupt fields may be read-only, sticky, latched, write-one-to-clear, or self-clearing depending on the authoritative register spec; this generated header only provides bit positions and masks.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the generated DCN 3.2.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` supplies the matching register offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c` uses DCN32 register-list macros to build resource objects, including the `dcn20_dsc_registers`, `dcn20_dsc_shift`, and `dcn20_dsc_mask` tables used by DSC instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.c` and `dcn20_dsc.h` provide the shared DSC programming path that consumes `DSCC*_PPS_CONFIG*` fields through register helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c` and `hw_factory_dcn32.c` consume `DC_GPIO_*`, HPD, DDC, and AUX-related masks and shifts to map logical GPIO/DDC/HPD concepts to DCN32 registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.c` and related panel-control headers show the broader panel/backlight programming model that uses `PANEL_PWRSEQ*` and `BL_PWM*` style fields. DCN32-specific resource wiring may reuse or adapt those shared panel-control abstractions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` turns generated masks and shifts into DMUB service tables, so macro name drift can break firmware-facing register access.

The generated field names also align with enum metadata in files such as `include/soc24_enum.h`, which documents DCIO enum values for clock selection, generic output selection, genlock/swaplock routing, and related controls. The enum file does not replace this header; it supplies value meanings while this header supplies bit placement.

## Risks And Edge Cases

- Field drift is the main risk. These constants are untyped preprocessor values, so a wrong mask or shift can compile cleanly while silently programming the wrong hardware bits.
- The chunk starts mid-`DIO_CLK_CNTL3`. Adjacent earlier chunks are needed to reconstruct the full register definition for that clock-control register.
- The chunk ends mid-`DSCC0_DSCC_PPS_CONFIG21`. The next chunk is required to complete the DSC range-QP table and any following PPS registers before drawing full DSC conclusions.
- DIO link selection fields control which HPO HDMI/DP encoder services each DIO link. Bad masks can cause connector routing failures, no display, wrong link training target, or failures limited to one physical connector.
- DCIO clock-gating, test-clock, reference-clock, and UNIPHY crossbar fields are low-level routing controls. Incorrect masks can produce hard-to-diagnose link instability, missing AUX/HPD activity, or failures that only appear during link retraining, hotplug, or low-power transitions.
- GPIO, DDC, HPD, and AUX fields are connector-visible. Mask errors can break EDID reads, DPCD/AUX transactions, hotplug detection, HPD IRQ handling, panel detection, or recovery after disconnect/reconnect.
- Pad strength, pull-up, RX enable, TX drive, and impedance fields are electrical controls. Incorrect values can create marginal signal integrity rather than deterministic failures, especially across cables, docks, and board variants.
- Panel power and backlight PWM fields are timing-sensitive. Incorrect delay, enable, reference divider, period, duty, or lock/update bits can cause black panels, flicker, incorrect brightness, failed resume brightness restoration, or unsafe panel power sequencing.
- DSC PPS fields directly affect compressed video stream syntax. Wrong bit placement for picture size, slice geometry, bits per pixel, rate-control buffer thresholds, QP ranges, or BPG offsets can cause sink decode failures, visual corruption, bandwidth miscalculation, or mode validation problems only on DSC modes.
- Full-width spare/reserved/UNIPHY macro-control fields are dangerous because they may look mechanically simple but still map to hardware-specific test, firmware, or reserved behavior. Callers should not infer safe write values from the presence of masks alone.

## Test Signals

Useful validation should combine generated-header checks with DCN32 display behavior:

- Build AMDGPU with DCN32 support enabled. Name mismatches should surface in `dmub_dcn32.c`, `dcn32_resource.c`, `hw_translate_dcn32.c`, `hw_factory_dcn32.c`, IRQ, clock-manager, or DSC register-table compilation.
- Mechanically verify that every generated field in this range has the expected `__SHIFT` and `_MASK` pair where the register schema requires both, and flag intentional exceptions such as partial registers at chunk boundaries.
- Compare this DCN 3.2.0 chunk against the matching authoritative register database or neighboring generated DCN headers for repeated blocks such as DIO link A-F, DDC1-5/VGA, HPD, UNIPHY0-4 reserved controls, panel power/backlight, and `DSCC0_DSCC_PPS_CONFIG*`.
- Exercise hotplug, HPD IRQ, EDID/DDC reads, DP AUX/DPCD transactions, HDMI RX-status handling, link encoder selection, MST/dock paths, and suspend/resume on DCN32 hardware.
- Exercise embedded panel power and brightness paths: boot brightness, brightness changes, backlight off/on, lid/panel power transitions, suspend/resume, and cases with fractional PWM enabled.
- Exercise DSC-enabled display modes across different resolutions, refresh rates, slice counts, bits-per-component, bits-per-pixel, RGB/native 4:2:0/native 4:2:2 formats where supported, and rate-control configurations.
- Watch for no-display on one connector, missing HPD, intermittent AUX failures, EDID read failures, backlight flicker, black panel after resume, DSC visual corruption, DSC link-training fallback, and rate-control buffer overflow/underflow interrupt anomalies.

## Cross-Chunk Notes

This is a chunk-level research document for lines 39691-42212 only. The final per-file report should merge it with adjacent chunks for the full `DIO_CLK_CNTL3` context before this range and the remainder of `DSCC0_DSCC_PPS_CONFIG21` plus later DSC registers after this range. It should also consolidate DCN32 GPIO, DIO, panel, and DSC integration with earlier and later chunks of the same generated header.
