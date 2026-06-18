# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 39687-42210

## Scope

This chunk is a generated AMD DCN 3.2.1 register shift/mask slice. It contains preprocessor constants only: each `<REGISTER>__<FIELD>__SHIFT` macro gives a field bit position and each `<REGISTER>__<FIELD>_MASK` macro gives the corresponding in-register mask. `//<REGISTER>` comments group constants by hardware register and `// addressBlock:` comments identify the generated hardware address block.

There are no C functions, structs, enums, loops, branches, direct MMIO calls, locking paths, allocation paths, or software persistence paths in this range. Runtime behavior comes from AMDGPU Display Core code that includes this header with the matching `dcn_3_2_1_offset.h` register-address header and then feeds these constants to register helper macros such as `REG_UPDATE`, `REG_GET`, and related generated field helpers.

The range starts in the middle of `DIO_HDMI_RXSTATUS_TIMER_CONTROL`: the `DIO_HDMI_RXSTATUS_TIMER_ENABLE__SHIFT` line is immediately before this chunk, while the remaining shifts and all masks are here. It ends in the middle of `DSCC0_DSCC_PPS_CONFIG19`: this chunk includes shifts through `RANGE_MIN_QP8__SHIFT`, while the remaining shifts and all masks for config 19 continue in the next chunk. The later merge lane should treat both boundary registers as split.

## Purpose And Hardware Surface

The purpose of this header section is to provide the bit layout for DCN 3.2.1 display I/O, GPIO, UNIPHY, panel power sequencing, backlight PWM, and DSC encoder registers. These macros are a hardware ABI for the display driver: callers can assemble or decode packed MMIO register values without hardcoding raw bit positions.

The chunk covers these address blocks and register families:

- DIO and DCIO display decode registers: HDMI RX status timer fields, DIO link A-F encoder mux selection, generic clock/test outputs, DCIO clock/ref-clock control, UNIPHY lane inversion and channel crossbar fields, write-command delay, pinstraps, spare bits, intercept state, pattern generator state, genlock/swaplock pad controls, and DCIO soft reset bits.
- GPIO/DDC/HPD/AUX registers: generic GPIO masks, DDC1-DDC5 and DDCVGA mask/A/EN/Y fields, genlock GPIO fields, HPD mask/A/EN/Y fields, drive strength registers, power sequence enable bits, pad strength, AUX PHY control, TX impedance and TX12 enable fields, AUX control registers 0-5, RX enable and pull-up enable fields, and AUX/I2C pad power status.
- UNIPHY macro reserved register windows: repeated `DCIO_UNIPHY0` through `DCIO_UNIPHY4` `UNIPHY_MACRO_CNTL_RESERVED0..57` full-width masks. These expose generated placeholders or opaque macro-control words for five UNIPHY instances.
- Panel power sequence and backlight registers: `DC_GPIO_PWRSEQ_*`, `PANEL_PWRSEQ_*`, `BL_PWM_*`, lock/ref-divider/spare registers.
- DSC compressor control registers: `DSCC0_DSCC_CONFIG0/1`, `DSCC0_DSCC_STATUS`, `DSCC0_DSCC_INTERRUPT_CONTROL_STATUS`, and `DSCC0_DSCC_PPS_CONFIG0..19` through the start of config 19.

## Important Definitions

The DIO link selector group is a primary integration surface. `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` all define `ENC_TYPE_SEL`, `HPO_HDMI_ENC_SEL`, and `HPO_DP_ENC_SEL`. DCN link encoder code uses these fields to route a UNIPHY transmitter to legacy, HDMI FRL, or DP 128b/132b encoder paths and to choose the HPO encoder instance.

The DCIO/UNIPHY control group defines clock and physical lane steering fields:

- `DC_GENERICA` and `DC_GENERICB` select generic clock outputs and UNIPHY refdiv/fbdiv/fbdiv-SSC/div2 sources.
- `DCIO_CLOCK_CNTL` selects a test clock and disables the display-clock-to-DCIO gate.
- `DC_REF_CLK_CNTL` selects HSYNC and genlock clock outputs.
- `UNIPHYA` through `UNIPHYE` link and channel-crossbar controls define per-channel inversion bits and 2-bit source selectors for channels 0-3.
- `DCIO_WRCMD_DELAY` exposes the UNIPHY write-command delay field.
- `DCIO_SOFT_RESET` provides one-bit soft reset fields for AUX engines, I2C DDC engines, generic GPIO, HPD, DIO, DCIO outputs, backlight, genlock, and all UNIPHY links A-E.

The GPIO and connector-detect group is broad and repetitive:

- `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC5_*`, and `DC_GPIO_DDCVGA_*` provide mask, input/action, output-enable, and output-value bit fields for generic, DDC, AUX-pad, VGA, and DDC power-down controls.
- `DC_GPIO_GENLK_*` provides mask/A/EN/Y fields for genlock, swaplock, VSYNC, and related pad enable/value controls.
- `DC_GPIO_HPD_*` defines mask, A, enable, and Y bits for HPD1-HPD5 in this DCN 3.2.1 variant. Display GPIO translation code maps HPD ids to these masks.
- `DC_GPIO_DRIVE_STRENGTH_S0/S1`, `DC_GPIO_PAD_STRENGTH_1/2`, `DC_GPIO_DRIVE_TXIMPSEL`, `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN` tune or enable pad electrical behavior.
- `PHY_AUX_CNTL` and `DC_GPIO_AUX_CTRL_0..5` configure AUX pad RX selection, HPD RX mode, DDC pad I2C mode, pull-ups, and AUX/DDC pad behavior used by DDC/AUX helper code.
- `AUXI2C_PAD_ALL_PWR_OK` exposes per-pad power-good status for DDC/AUX pad groups.

The UNIPHY reserved blocks define `DCIO_UNIPHY{0..4}_UNIPHY_MACRO_CNTL_RESERVED{0..57}__RESERVED_*` fields, mostly as full-register `0xFFFFFFFFL` masks. Although named reserved, they are still generated addressable fields and should be treated as opaque hardware-owned words unless an ASIC specification gives a reason to access them.

The panel and backlight group includes:

- `DC_GPIO_PWRSEQ_EN`, `DC_GPIO_PWRSEQ_CTRL`, `DC_GPIO_PWRSEQ_MASK`, and `DC_GPIO_PWRSEQ_A_Y` for GPIO-controlled panel/backlight/Vary-Bright pin ownership and values.
- `PANEL_PWRSEQ_CNTL`, `PANEL_PWRSEQ_STATE`, `PANEL_PWRSEQ_DELAY1/2`, and `PANEL_PWRSEQ_REF_DIV1/2` for panel power-up/power-down sequencing, target state readback, delays, and reference dividers.
- `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK` for backlight PWM enable, polarity, period/count, group lock, and multi-panel group fields.

The DSCC0 group defines the DSC compressor control and picture-parameter-set packing:

- `DSCC0_DSCC_CONFIG0/1` exposes slice counts, ICH behavior, 4:2:0/4:2:2 mode, bits-per-component, BPG offset, native mode, and line-buffer depth controls.
- `DSCC0_DSCC_STATUS` reports idle state.
- `DSCC0_DSCC_INTERRUPT_CONTROL_STATUS` defines overflow, underflow, rate-control buffer model overflow, end-of-frame-not-reached status bits, and matching interrupt-enable bits.
- `DSCC0_DSCC_PPS_CONFIG0..18` maps DSC PPS fields including DSC version, PPS identifier, line-buffer depth, bits/component, bits/pixel, VBR/native/convert/block-pred flags, chunk size, picture and slice dimensions, initial delays, scale intervals, BPG offsets, initial/final offsets, flatness QP, rate-control model size, edge factor, quantization limits, target offsets, RC thresholds, and range QP/BPG-offset entries 0-6.
- `DSCC0_DSCC_PPS_CONFIG19` begins range entries 7-8 but is incomplete in this chunk.

## Control Flow And State Behavior

This chunk has no executable control flow. The effective control flow is in consumers:

1. DCN 3.2.1 resource initialization includes `dcn_3_2_1_offset.h` and this `dcn_3_2_1_sh_mask.h`, then expands generated register lists and field lists into per-block register/shift/mask tables.
2. Link encoder paths program `DIO_LINK*_CNTL` when selecting a transmitter's encoder type and HPO encoder instance.
3. GPIO/DDC/HPD translation code uses DDC, AUX, and HPD mask/shift fields to map logical connector services to physical pins, then register helpers read or update mask, A, EN, and Y registers.
4. Panel control and hardware sequencing code programs power-sequence controls, reads target state, stores/restores backlight-related registers, and updates BL PWM period/count/polarity fields.
5. DSC setup code writes `DSCC0_DSCC_CONFIG*` and `DSCC0_DSCC_PPS_CONFIG*` fields from computed display stream compression parameters, while interrupt/status paths can observe buffer underflow/overflow and end-of-frame errors.

The state represented here is MMIO hardware register state, not software-owned persistence. Programmed state includes DIO muxing, clock/test output selection, reset bits, GPIO ownership/enable/output values, AUX/DDC electrical modes, UNIPHY crossbar/inversion settings, panel sequencing delays and state targets, backlight PWM settings, DSC mode configuration, DSC PPS payload, and DSC interrupt enables. Volatile/readback state includes pin input values, HPD/DDC pad status, AUX/I2C power-good bits, panel power-sequence target state, DSC idle status, and DSC error occurrence bits.

Several fields are sequencing-sensitive even though they are only constants here. Soft reset bits, panel `DIGON/BLON` overrides, PWM register locks, interrupt occurrence/enable fields, HPD/DDC pin ownership bits, and DSC PPS fields should be updated through the established display helper paths so reserved and unrelated fields are preserved.

## Dependencies And Integration Points

This generated header depends on exact consistency with DCN 3.2.1 hardware register specifications and the matching offset header. `dcn321_resource.c` includes both `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`; the resource macros combine `reg<NAME>` addresses with `<REGISTER>__<FIELD>` masks and shifts to populate the DCN register structures.

Important integration points include:

- `display/dc/resource/dcn321/dcn321_resource.c`, which imports this ASIC register namespace for DCN 3.2.1 resource construction.
- `display/dc/dio/dcn31/dcn31_dio_link_encoder.*`, where `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` fields drive the DIO PHY mux for HDMI FRL and DP 128b/132b paths.
- `display/dc/gpio/ddc_regs.h` and related GPIO translation files, which use DDC/AUX/HPD masks and shifts to build connector GPIO tables.
- `display/dc/gpio/dcn32/hw_translate_dcn32.c` and adjacent generation-specific translation files, which map logical HPD pins onto `DC_GPIO_HPD_A` masks from this family of headers.
- `display/dc/dcn31/dcn31_panel_cntl.c` and panel-control headers, which consume `PANEL_PWRSEQ_*` and backlight PWM fields for embedded panel sequencing and brightness restoration.
- DSC support under `display/dc/dsc/`, especially shared DCN DSC field-list macros that expect `DSCC0_DSCC_*` and `DSCC0_DSCC_PPS_CONFIG*` fields to exist with the generated names.

## Risks And Maintenance Notes

- Numeric drift is the main risk. A wrong shift or mask can compile cleanly but direct writes to the wrong bits, breaking link muxing, HPD/DDC/AUX behavior, panel power sequencing, backlight PWM, or DSC PPS programming only on affected hardware.
- The chunk is highly repetitive. DIO link A-F, DDC1-DDC5, HPD groups, UNIPHY0-4 reserved windows, and DSC PPS threshold/range fields are susceptible to copy-generation mistakes that are hard to notice in review.
- Boundary completeness matters. The start omits one shift from `DIO_HDMI_RXSTATUS_TIMER_CONTROL`; the end omits the rest of `DSCC0_DSCC_PPS_CONFIG19`. The final merged per-file research should describe those registers using adjacent chunks.
- Fields named `RESERVED_*` should not be written opportunistically. Many reserved UNIPHY macro-control entries are full-width masks, but callers should still treat them as opaque unless the hardware spec or generated access layer explicitly requires access.
- GPIO and panel sequencing fields interact with external connectors and embedded panels. Incorrect ownership, enable, polarity, or delay bits can present as hotplug loss, failed EDID reads, panel blanking, stuck backlight, or suspend/resume regressions.
- DSC PPS fields are protocol-visible. Incorrect values may produce visual corruption, link training failures, or sink-side DSC rejection even when the driver compiles and the MMIO write path functions.

## Test Signals

Useful validation signals for changes touching this header region are:

- Build coverage for AMDGPU display code that includes DCN 3.2.1 generated register headers, especially `dcn321_resource.c` and shared DCN DIO/GPIO/panel/DSC users.
- Static comparison against the generated register source or ASIC register specification for every `_SHIFT`/`_MASK` pair in this chunk, including repeated DDC/HPD/UNIPHY/DSC families.
- Display bring-up tests on DCN 3.2.1 hardware across DP, HDMI FRL, hotplug, EDID/DDC, AUX transactions, and HPD interrupt paths.
- Embedded panel tests covering power on/off, backlight enable, PWM brightness changes, suspend/resume, and register restore behavior.
- DSC mode tests using compressed high-bandwidth modes, including visual validation, sink acceptance, and register dumps of `DSCC0_DSCC_CONFIG*` and `DSCC0_DSCC_PPS_CONFIG*`.
- Register dump checks before and after link/panel/DSC programming to confirm reserved bits remain stable and only intended fields change.
