# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 42009-44390

## Scope

This chunk is a generated AMDGPU DCN 2.1.0 register shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, storage, or local executable logic. The exported contract is the naming and value pairing of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used by AMD display register helpers to pack, update, and decode fields in MMIO registers.

The range covers 2,382 source lines with 2,179 `#define` entries, including 1,087 `__SHIFT` constants and 1,253 mask constants or mask-named fields. It starts in the DIG4 audio formatter S/PDIF channel-status area, then covers DIG4 audio packet/TMDS controls, DP4 DisplayPort link and secondary-data controls, DCIO/UNIPHY routing and panel power/backlight controls, DC GPIO/DDC/HPD/AUX pad controls, AUX/I2C pad power-good state, and the first DSC0 top/DSCCIF fields.

## Purpose

The chunk provides the bit layout for a DCN 2.1.0 display-output lane: encoder instance 4 (`DIG4`), DisplayPort instance 4 (`DP4`), shared DCIO and GPIO pad controls, and the start of DSC encoder instance 0. Higher-level AMDGPU display code can use logical register and field names while this generated header supplies ASIC-specific field offsets and masks.

Major hardware areas covered here are:

- `DIG4_AFMT_*`: HDMI/DP audio formatter state for IEC 60958 channel status, audio CRC, audio test ramps, audio FIFO/status/ack bits, audio packet send, audio source selection, infoframe update, generic packet update/pending bits, and immediate-send status.
- `DIG4_DIG_*` and `DIG4_TMDS_*`: digital backend enable/source/mode/HPD selection, symbol clock state, lane enable, TMDS sync/control characters, control-bit generation, DC balancer configuration, feedback selection, and test pattern generation.
- `DP4_DP_*`: DisplayPort link state, pixel format, stream enable/status, M/N timing, MSA/VBID fields, DPHY training/test/CRC/scrambler/FEC controls, secondary-data packet generation, MST/MSE scheduling, MSO controls, DSC-over-DP mode and bytes-per-pixel, double-buffer control, metadata transmission, and ALPM sleep/standby controls.
- `DC_*`, `UNIPHY*`, `LVTMA_*`, and `BL_PWM_*`: display clock/generic clock selection, UNIPHY channel inversion and crossbar routing, write-command delays, pinstrap readback, LVTM panel power sequencing, backlight PWM, genlock/swaplock pad selection, DCIO clock gating, and soft resets.
- `DC_GPIO_*`, `PHY_AUX_CNTL`, and `AUXI2C_PAD_ALL_PWR_OK`: generic GPIOs, DDC pads 1-5 plus VGA DDC, genlock/swaplock, HPD pins, power-sequence pins, pad strength, AUX electrical controls, TX/RX enable, pullups, DDC I2C mode, AUX termination/hysteresis/VOD tuning, DP/DN swap, and per-PHY power-good status.
- `DSC_TOP0_*` and `DSCCIF0_*`: DSC clock/debug control and the first DSCCIF input-interface fields for underflow recovery/status, pixel format, component depth, double-buffer pending state, picture width, and picture height.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the generated macro namespace:

- `*_SHIFT` constants give the low bit position for a field.
- `*_MASK` constants give the field mask already shifted into register position.
- Register-heading comments such as `//DP4_DP_SEC_CNTL2` group fields by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dio_dp4_dispdec` identify the generated register block that owns the following registers.

Representative DIG4 audio and HDMI/TMDS macros include `DIG4_AFMT_60958_0__AFMT_60958_CS_*`, `DIG4_AFMT_AUDIO_CRC_CONTROL__AFMT_AUDIO_CRC_*`, `DIG4_AFMT_STATUS__AFMT_AUDIO_FIFO_OVERFLOW_MASK`, `DIG4_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_FIFO_OVERFLOW_ACK_MASK`, `DIG4_AFMT_VBI_PACKET_CONTROL1__AFMT_GENERICn_*`, `DIG4_HDMI_GENERIC_PACKET_CONTROL5__HDMI_GENERICn_IMMEDIATE_SEND*`, `DIG4_DIG_BE_CNTL__DIG_FE_SOURCE_SELECT_MASK`, `DIG4_DIG_LANE_ENABLE__DIG_LANEnEN_MASK`, and the `DIG4_TMDS_CTL*_GEN_CNTL` field groups for per-control-symbol source, delay, invert, modulation, feedback, and pattern output.

The DP4 block is the densest protocol surface in this chunk. Important groups include:

- `DP4_DP_LINK_CNTL`, `DP4_DP_CONFIG`, `DP4_DP_PIXEL_FORMAT`, `DP4_DP_VID_STREAM_CNTL`, `DP4_DP_VID_TIMING`, `DP4_DP_VID_N`, and `DP4_DP_VID_M` for stream/link enablement, lane count, pixel encoding/depth, and video timing generation.
- `DP4_DP_DPHY_CNTL`, `DP4_DP_DPHY_TRAINING_PATTERN_SEL`, `DP4_DP_DPHY_SYM*`, `DP4_DP_DPHY_8B10B_CNTL`, `DP4_DP_DPHY_PRBS_CNTL`, `DP4_DP_DPHY_SCRAM_CNTL`, `DP4_DP_DPHY_CRC_*`, and `DP4_DP_DPHY_FAST_TRAINING*` for physical-layer training, FEC, test symbols, scrambler, PRBS, CRC, MST CRC slot selection, and fast-training status.
- `DP4_DP_SEC_CNTL`, `DP4_DP_SEC_CNTL1`, `DP4_DP_SEC_CNTL2` through `_7`, `DP4_DP_SEC_FRAMING*`, `DP4_DP_SEC_AUD_*`, `DP4_DP_SEC_PACKET_CNTL`, and `DP4_DP_SEC_METADATA_TRANSMISSION` for secondary-stream/audio/generic packet scheduling, timestamps, GSP line targeting, active/idle send status, metadata packets, and PPS-related send state.
- `DP4_DP_MSE_*`, `DP4_DP_MSO_*`, `DP4_DP_DSC_CNTL`, and `DP4_DP_DSC_BYTES_PER_PIXEL` for MST allocation timing, multi-stream/multi-segment operation, and Display Stream Compression transport programming.
- `DP4_DP_DB_CNTL`, `DP4_DP_MSA_VBID_MISC`, and `DP4_DP_ALPM_CNTL` for double-buffer commit status, VBID/MSA overrides, and main-link PHY sleep/standby transitions.

DCIO and connector-pad macros include repeated `UNIPHYA` through `UNIPHYE` `*_LINK_CNTL` and `*_CHANNEL_XBAR_CNTL` groups, `DCIO_SOFT_RESET__UNIPHY*_SOFT_RESET_MASK`, `LVTMA_PWRSEQ_*`, `BL_PWM_*`, `DC_GPIO_DDCn_*`, `DC_GPIO_HPD_*`, `DC_GPIO_PWRSEQ_*`, `PHY_AUX_CNTL__AUX_PAD_*`, `DC_GPIO_AUX_CTRL_0` through `_5`, and `AUXI2C_PAD_ALL_PWR_OK__AUXI2C_PHYn_ALL_PWR_OK_MASK`.

The DSC fields are a partial start of a later whole-file section: `DSC_TOP0_DSC_TOP_CONTROL__DSC_CLOCK_EN_MASK`, clock-gating debug fields, and `DSCCIF0_DSCCIF_CONFIG0`/`CONFIG1` input format, underflow, update-pending, width, and height masks.

## Control Flow

This header has no local control flow. Runtime control flow appears in consumers that include `dcn_2_1_0_offset.h` and this shift/mask header, then feed the macros into AMD display register helper tables and read/modify/write operations.

A typical runtime path is:

1. DCN 2.1 code includes the generated offset header and this shift/mask header.
2. Register-table macros such as `REG`, `SF`, `SF_DDC`, `SF_HPD`, and family-specific mask-list macros paste register and field names into these `__SHIFT` and `_MASK` symbols.
3. Driver code calls register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or generated table initializers.
4. The helper layer uses the shift and mask values to isolate fields, update only the intended bits, poll status, or acknowledge hardware events.

Control-sensitive hardware flows represented by this chunk include audio formatter programming, HDMI/DP infoframe and generic packet updates, TMDS control-character generation, digital backend enable/disable, DP stream enable/disable, link training, FEC and scrambler setup, DPHY test/CRC capture, MST/MSE allocation, secondary-data packet scheduling, DSC transport setup, ALPM sleep/standby requests, UNIPHY lane routing, panel power sequencing, backlight PWM commits, hotplug/DDC/AUX pad operation, and DSC input-interface programming.

The macros do not encode access type or ordering. Callers must still know whether a field is read-only status, sticky status, write-one-to-clear ack, self-clearing command, double-buffered configuration, safe only while disabled, or owned jointly by firmware and hardware state machines.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware state that persists in DCN registers until software writes it, hardware changes it, a block reset occurs, or power management loses/restores the register contents.

State represented in this range includes:

- Audio formatter state: IEC 60958 channel-status bytes, audio sample send enable, audio source selection, audio test/ramp controls, CRC enable/result, FIFO overflow status/ack, audio enable/HBR status, and generic/infoframe packet update-pending flags.
- Digital encoder state: backend source selection, mode, HPD association, lane enables, symbol-clock on state, TMDS control symbol patterns, modulation/delay/invert settings, and forced digital disable.
- DisplayPort link state: training completion/status, lane count, stream enable/status, pixel format/depth, timing M/N values, DPHY FEC/training/scrambler/CRC/test state, secondary/audio packet control, MSE/MSO allocation, DSC packetization, metadata transmission, double-buffer pending/taken status, and ALPM pending state.
- DCIO state: generic clock routing, UNIPHY channel inversion/crossbar/link-enable state, pinstrap readbacks, soft reset bits, genlock/swaplock pad control, panel power-sequence target and status, and PWM period/duty/update lock.
- GPIO/AUX/DDC/HPD state: pin masks, output values, enables, readbacks, pad pullup/pulldown and strength, DDC clock/data modes, AUX pad electrical tuning, HPD receive/mask selection, TX/RX enable, and AUX/I2C PHY power-good bits.
- DSC state: DSC top-level clock/debug enable and DSCCIF input-interface underflow, pixel format, bits-per-component, update-pending, picture width, and picture height fields.

Many fields are configuration latches, but several are live status or pending bits. Incorrect values can persist until a modeset, connector hotplug, audio reconfiguration, suspend/resume sequence, DCN block reset, or full GPU reset reprograms the affected hardware.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies matching register addresses and base indices. This chunk supplies the bit positions inside those registers. The generated identifiers also depend on AMD display macro conventions that paste register and field names into `_MASK` and `__SHIFT` symbols.

Direct include sites visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the DCN 2.1 offset and mask headers for DMUB-facing DCN21 register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes these headers while mapping DCN21 IRQ sources and programming interrupt/status register fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes the generated headers while constructing DCN21 resources for links, encoders, GPIO/DDC/AUX, audio/display output, DSC, and related blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`, which expands DDC and HPD register/mask lists from this header into GPIO hardware objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`, which translates generated GPIO register offsets and masks such as `DC_GPIO_GENERIC_A__...`, `DC_GPIO_HPD_A__...`, and genlock/swaplock masks into software `gpio_id` and enum values.

Cross-generation helpers also reveal how these macros are consumed. `display/dc/gpio/ddc_regs.h` references `DC_GPIO_AUX_CTRL_5` and DDC I2C-mode field macros, while `display/dc/dsc/dcn20/dcn20_dsc.h` uses `DSCCIF0_DSCCIF_CONFIG0` field macros for DSC input-interface programming. The same generated field names appear across closely related ASIC generations, so field layout drift can affect shared helper macros even when the include path is generation-specific.

Although the repository prefix is `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, networking, or durable persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong shift or mask compiles cleanly but can make register helpers alter the wrong bits, truncate a value, miss status, clear the wrong event, or leave a pending command stuck.

DIG4 and DP4 fields are output-path critical. Bad masks in audio formatter, TMDS, DP stream, DPHY, secondary packet, MSE/MSO, DSC, or ALPM fields can cause no display, failed link training, unstable MST, missing HDR/metadata/PPS packets, broken DSC transport, incorrect audio sample/channel status, stuck audio FIFO overflow, or incomplete stream disable/enable sequencing.

Status, ack, and pending bits are especially sensitive. Fields such as `AFMT_AUDIO_FIFO_OVERFLOW_ACK`, `AFMT_60958_CS_UPDATE`, generic packet pending bits, DP secondary-packet deadline/pending bits, DPHY CRC valid/status bits, double-buffer taken/clear bits, and ALPM pending bits often require precise write sequences. A generic read/modify/write using an inaccurate mask can acknowledge an unrelated event or fail to clear the intended one.

GPIO, DDC, HPD, and AUX pad fields are board- and connector-sensitive. Errors in DDC pad mode, pullups, power disable, HPD receive masks, AUX termination, DP/DN swap, hysteresis, VOD tuning, or AUX/I2C power-good handling may show up only on certain connectors, boards, cables, sink devices, or suspend/resume paths.

Repeated blocks increase copy-generation risk. `UNIPHYA` through `UNIPHYE`, `DC_GPIO_DDC1` through `DDC5`, HPD1 through HPD6, AUX1 through AUX6, and generic packet slots should be structurally consistent unless the ASIC register database intentionally differs. A one-off shift or width should be treated as suspicious during generated-header validation.

Chunk boundaries matter. This range starts after the beginning of the DIG4 audio-info section and ends in the middle of `DSCCIF0_DSCCIF_CONFIG1`; the final per-file document should merge adjacent chunks before making whole-file conclusions about DIG4 and DSC coverage.

## Test Signals

Useful validation signals are mostly generated-header checks plus DCN21 display, connector, audio, and DSC behavior:

- Build coverage for DCN21 DMUB, IRQ service, resource construction, GPIO factory/translation, DDC/AUX, display audio, DisplayPort, and DSC code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field in this chunk has a matching register/address definition in `dcn_2_1_0_offset.h`, that masks align with shifts and field widths, and that repeated instances remain structurally consistent.
- HDMI/DP audio tests for sample-rate and channel-status programming, infoframe updates, HBR/non-HBR audio, audio FIFO overflow handling, generic packet updates, hotplug audio recovery, and mode changes.
- DisplayPort tests for link training, stream enable/disable, lane-count changes, MST/MSE allocation, MSO paths, FEC/scrambler behavior, DPHY CRC/test modes, metadata/PPS packet transmission, DSC link operation, and ALPM sleep/standby transitions.
- Connector tests for HPD1-HPD6 detection and interrupts, HPDRX sideband events, EDID reads over DDC/AUX, AUX pad power transitions, suspend/resume, runtime power management, and plug/unplug stress.
- Panel tests for LVTMA power sequencing, backlight PWM period/duty/update locking, power-down minimum delays, and backlight recovery after modeset or power events.
- DSC tests that exercise `DSC_TOP0` clock enable/debug state and `DSCCIF0` input configuration, including underflow status/recovery and double-buffer update-pending behavior.

Regression symptoms from bad constants include failed EDID/AUX transactions, missing hotplug events, black screen on DP4/DIG4 connectors, unstable MST/MSO, incorrect or absent HDMI/DP audio, missing metadata or DSC PPS packets, stuck pending bits, panel power/backlight sequencing failures, DSC underflow interrupts, or failures that appear only on one generated link/pad instance.

## Cross-Chunk Notes

This is a constants-only chunk from a generated DCN 2.1.0 hardware header. Adjacent chunks own earlier DIG4 HDMI/audio-info fields and later DSCC/DSC fields. The merge lane should combine this artificial line range with neighboring chunks so the final per-file document presents the generated register contract as a whole rather than as independent source modules.
