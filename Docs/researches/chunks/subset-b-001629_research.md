# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 46977-49385

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains preprocessor constants only: each field is represented by a `__SHIFT` macro and usually a matching `_MASK` macro. The constants are consumed by AMDGPU display-core register helpers to pack, update, read, and decode fields in DCN 2.0 display hardware registers.

The source path lives under a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

This range starts inside the `dce_dc_dio_dig5_dispdec` address block and ends inside the HPD GPIO field list. The chunk boundary is not semantic:

- It begins at line 46977 after the first four `DIG5_DIG_FE_CNTL` shift fields already appeared in the previous chunk.
- It includes the rest of `DIG5_DIG_FE_CNTL`, the complete DIG5 HDMI/AFMT/TMDS/backend/display-output-control field groups, the complete DP5 DisplayPort stream/PHY/secondary-data field groups, DCIO global/link/power/backlight field groups, and most GPIO/DDC/GENLK/HPD field groups.
- It ends at line 49385 after the `DC_GPIO_HPD_EN` shift fields and before the matching `DC_GPIO_HPD_EN` mask fields, which continue in the next chunk.

The represented hardware surface is the sixth DIO/DIG instance (`DIG5` and `DP5`) plus shared DCIO and GPIO blocks. In display-core terms these fields cover one link encoder/stream encoder instance and the supporting physical link, DisplayPort packetization, HDMI packet/audio formatter, UNIPHY routing, panel/backlight sequencing, DDC/AUX pad behavior, and hotplug/general-purpose GPIO control.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, callbacks, or storage objects in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit position of a register field.
- `<REGISTER>__<FIELD>_MASK` gives the bitmask used by `REG_SET`, `REG_UPDATE`, `REG_GET`, `LE_SF`, `SF_DDC`, `SF_HPD`, and related generated-table helpers.
- Register address macros live in the matching `dcn_2_0_0_offset.h`; this file supplies the field-level metadata.

Important macro families in this chunk:

- `DIG5_DIG_FE_CNTL`, `DIG5_DIG_OUTPUT_CRC_*`, `DIG5_DIG_CLOCK_PATTERN`, `DIG5_DIG_TEST_PATTERN`, `DIG5_DIG_RANDOM_PATTERN_SEED`, and `DIG5_DIG_FIFO_STATUS`: DIG5 front-end source routing, stereo sync, start/bypass/pixel selection, Dolby Vision flags, TMDS encoding/color-format fields, output CRC control/result, test pattern generation, random pattern seed, and FIFO status/calibration/error fields.
- `DIG5_HDMI_*`: HDMI metadata packet control, generic packet line controls, core HDMI control/status, audio packet control, ACR packet control/status for 32/44/48 kHz families, VBI packets, infoframe controls, generic packet controls, gamut/control packet data, HDMI debug/DB control, and DME metadata control.
- `DIG5_AFMT_*`: audio formatter fields for IEC 60958 channel status words, audio infoframe and MPEG infoframe payload fields, ISRC packet payloads, generic HDR/generic packet payloads, audio CRC control/result, ramp/test audio controls, audio status, packet control, VBI generic-packet conflict/index controls, infoframe source/update controls, and audio source selection.
- `DIG5_DIG_BE_*` and `DIG5_TMDS_*`: DIG5 backend enable, dual-link/swap/interlace/control flags, TMDS control-character, feedback, stereo-sync, sync-character, control-bit, DC-balancer, and control-bit generator fields.
- `DIG5_DIG_VERSION`, `DIG5_DIG_LANE_ENABLE`, `DIG5_AFMT_CNTL`, `DIG5_AFMT_VBI_PACKET_CONTROL1`, `DIG5_HDMI_GENERIC_PACKET_CONTROL5`, and `DIG5_FORCE_DIG_DISABLE`: version/lane clock enable, AFMT enable/status, larger generic-packet line/control groups, and force-disable fields.
- `DP5_DP_*`: DisplayPort link control, pixel format, MSA colorimetry/misc/timing/VBID fields, stream control, steering FIFO setup, video timing/N/M values, link framing, HBR2 eye pattern, video interrupt controls, DPHY control/training/symbol/8b10b/PRBS/scrambler/CRC/fast-training fields, secondary-data packet/audio/timestamp/framing controls, MST/MSE rate and slot-allocation tables, MSO control, DSC control and bytes-per-pixel, DP debug/DB controls, metadata transmission, ALPM sleep/standby fields, and security/secondary stream control registers through `DP5_DP_SEC_CNTL7`.
- `DC_GENERICA`, `DC_GENERICB`, and `DC_REF_CLK_CNTL`: generic DC pin or scratch-style controls and reference-clock source controls.
- `UNIPHYA` through `UNIPHYF`: per-UNIPHY link enable, HPD mask, lane stagger, channel crossbar source, and lane inversion fields. These are the physical transmitter routing controls used by link encoder code.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `LVTMA_PWRSEQ_*`, `BL_PWM_*`, and `BL_PWM_GRP1_REG_LOCK`: write-command delay, strap readout, LVTM/eDP-style panel power sequence control/state/delays/reference divider, backlight PWM enable/debug/period/group lock fields.
- `DCIO_GSL_*`, `DCIO_CLOCK_CNTL`, and `DCIO_SOFT_RESET`: genlock/swaplock pad controls, clock enable fields, and soft reset bits for AUX, I2C, DIG, SYMCLK, and UNIPHY blocks.
- `DC_GPIO_GENERIC_*`: generic GPIO mask, output value (`A`), output enable (`EN`), and input/readback (`Y`) fields for generic pins A through G, plus receive, pull, mask, and mux selector fields.
- `DC_GPIO_DDC1_*` through `DC_GPIO_DDC6_*` and `DC_GPIO_DDCVGA_*`: DDC/AUX GPIO mask, output, enable, and input fields for six DDC pads and VGA DDC. Mask registers include CLK/DATA mask bits, pull-down enables, receiver state fields, AUX pad mode, polarity, hardware pull-down allowance, and drive strength fields.
- `DC_GPIO_GENLK_*`: genlock clock, genlock vsync, and swaplock A/B mask/output/enable/input fields.
- `DC_GPIO_HPD_MASK`, `DC_GPIO_HPD_A`, and the shift half of `DC_GPIO_HPD_EN`: HPD1 through HPD6 masking, pull disable, receive status, output values, and enable/schmitt/slew/spare/selector controls. The HPD enable masks begin immediately after this chunk.

## Control Flow

This chunk has no runtime control flow. It is declarative register-field metadata used by display driver code at compile time.

Runtime control flow appears in consumers that combine these field macros with register offsets and typed register tables:

- Link encoder setup uses `display/dc/dio/dcn20/dcn20_link_encoder.h` macros such as `LINK_ENCODER_MASK_SH_LIST_DCN20`, `UNIPHY_MASK_SH_LIST`, `DPCS_DCN2_MASK_SH_LIST`, and `UNIPHY_DCN2_REG_LIST`. Those lists reference fields from this chunk for DIG lane enable, TMDS control bits, UNIPHY channel crossbar/link enable, and `DCIO_SOFT_RESET` reset bits.
- DCN20 link encoder implementation programs DIG/DP/UNIPHY state while mapping BIOS transmitter objects such as `TRANSMITTER_UNIPHY_A` through `TRANSMITTER_UNIPHY_F/G` to hardware blocks. The masks here make those read-modify-write operations target the intended fields.
- DDC GPIO setup uses `display/dc/gpio/ddc_regs.h`. `DDC_GPIO_REG_LIST_ENTRY`, `DDC_REG_LIST_DCN2`, and `DDC_MASK_SH_LIST_DCN2` combine `DC_GPIO_DDCx_MASK/A/EN/Y` masks from this chunk with DDC setup and AUX pad control registers to build GPIO/DDC descriptors.
- HPD GPIO setup uses `display/dc/gpio/hpd_regs.h`. `HPD_GPIO_REG_LIST_ENTRY`, `HPD_REG_LIST`, and `HPD_MASK_SH_LIST` consume `DC_GPIO_HPD_MASK/A/EN/Y` fields to expose hotplug GPIO state and interrupt filtering to the HPD service path.
- Resource construction in DCN20 display code includes the generated offset and mask headers to populate per-block register structures. Later modeset, hotplug, audio, DP link-training, HDMI infoframe, and debug/CRC paths use those structures through `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and field-list macros.

Because this header only supplies constants, it does not enforce sequencing. Consumers must provide the ordering around link disable/enable, HPD masking, DDC pad switching between I2C and AUX, DP link training, DP secondary-data programming, HDMI/AFMT packet updates, FIFO/error acknowledgment, panel power sequencing, PWM updates, and soft-reset assertion/deassertion.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe hardware MMIO state.

Hardware state represented by these fields includes:

- DIG5 front-end/backend routing, enablement, lane-clock state, FIFO status, and CRC/test-pattern state.
- HDMI packet-generation state, including metadata, infoframes, generic packets, ACR, VBI, audio packet limits, deep color, scramble, keepout, error status, and debug/DB controls.
- AFMT audio packet state, IEC 60958 channel-status fields, audio test/ramp/CRC state, audio enable/status, high-bit-rate status, FIFO overflow indicators, and generic packet lock/conflict status.
- TMDS encoding and balancing state for HDMI/DVI-style signaling.
- DP5 stream configuration, MSA fields, MST/MSE slot allocation, secondary-data/audio packet framing, PHY training and CRC diagnostics, PRBS/scrambler controls, FEC/DSC-related state where present, metadata transmission, MSO, and ALPM low-power link state.
- UNIPHY channel routing and link enable state for physical transmitters A through F.
- DCIO clock and reset state for AUX, I2C, DIG, SYMCLK, and UNIPHY blocks.
- Panel/backlight state in LVTM power sequencing and PWM controls.
- GPIO state for generic pins, DDC/AUX pads, VGA DDC, genlock/swaplock, and HPD pins.

Persistence is hardware-defined rather than encoded in this file. Some fields are durable programming knobs that remain until a modeset, hotplug reconfiguration, suspend/resume, power-gating transition, reset, or explicit rewrite. Other fields are read-only status, sticky status, write-one-to-clear acknowledgments, self-clearing requests, latched counters, or debug/test controls. Names such as `*_STATUS`, `*_ACK`, `*_INT`, `*_ERROR`, `*_RESET`, `*_SEND`, `*_PENDING`, `*_UPDATE`, `*_MASK`, and `*_LOCK` identify likely side effects, but the exact access type and reset value require the hardware register specification and the consumers' access patterns.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract for DCN 2.0. It is meaningful together with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` for register addresses and base indices.
- Adjacent chunks of `dcn_2_0_0_sh_mask.h`, because this range starts and ends inside register-field groups.
- AMD display register helper macros and generated field-list helpers in `drivers/gpu/drm/amd/display/dc`.
- DCN20 resource, link encoder, stream encoder, GPIO, IRQ, DMUB, clock-manager, and hardware sequencer code that includes the generated headers.

Direct or practical integration points visible in this tree include:

- `display/dmub/src/dmub_dcn20.c`, which includes `dcn/dcn_2_0_0_sh_mask.h` for DMUB/DCN20 register operations.
- `display/dc/dio/dcn20/dcn20_link_encoder.h` and `display/dc/dio/dcn20/dcn20_link_encoder.c`, which use DIG lane, TMDS, UNIPHY, DPCS, AUX, and soft-reset fields for physical link control.
- `display/dc/gpio/ddc_regs.h` and `display/dc/gpio/hpd_regs.h`, which turn the DDC and HPD GPIO macros into typed register/mask tables.
- `display/dc/gpio/dcn20/hw_factory_dcn20.c`, which instantiates GPIO objects for DCN20 hardware.
- `display/dc/resource/dcn20/dcn20_resource.c`, which builds the DCN20 resource pool and register maps.
- `display/dc/hwss/dcn20/dcn20_hwseq.c`, `display/dc/link/link_dpms.c`, and common link code, which use transmitter/UNIPHY indices during power sequencing and link enablement.

The important cross-file contract is that field names in this mask header must match the symbolic field names expected by `LE_SF`, `SF_DDC`, `SF_HPD`, stream-encoder tables, and generic `REG_*` helper call sites. A field rename or value drift breaks either the build or the target hardware programming.

## Risks And Edge Cases

- This is hardware ABI data. A wrong shift or mask can compile cleanly while causing a read-modify-write to touch the wrong bit, leave stale bits set, or clear an unrelated status/control field.
- The chunk boundary is partial at both ends. `DIG5_DIG_FE_CNTL` is missing its first four shift definitions in this chunk, and `DC_GPIO_HPD_EN` is missing all mask definitions. Merge/reconciliation must combine adjacent chunks for complete per-register analysis.
- DIG5 and DP5 are instance-specific copies of repetitive DIO/DIG/DP blocks. Copy/paste drift from other instances can affect only the sixth display link, making failures connector- or board-dependent.
- HDMI/AFMT fields have many send/continuous/update/source bits. Incorrect masks can produce missing audio, incorrect ACR/N/M behavior, invalid infoframes, HDR metadata loss, generic-packet conflicts, or HDMI compliance failures.
- DP secondary-data and MSE/MSO fields are packetization-critical. Bad fields can break MST allocation, audio timestamps, metadata packets, DSC/MSO modes, or secondary-data framing without obvious compile-time failures.
- DPHY/training/CRC fields are link-critical. Wrong training pattern, scrambler, PRBS, fast-training, CRC, or ALPM masks can cause link-training failures, intermittent display loss, CRC mismatches, or low-power link exit failures.
- `DCIO_SOFT_RESET` fields control many shared blocks. An incorrect mask can reset the wrong AUX/I2C/DIG/SYMCLK/UNIPHY instance or fail to reset a stuck block, producing hard-to-debug hotplug or modeset failures.
- DDC/AUX pad mode and pull/drive-strength fields affect external electrical interfaces. Bad programming can cause EDID read failures, AUX/I2C contention, HPD flapping, signal-integrity problems, or failure to detect a display.
- HPD fields are split across this and the next chunk. Using only the visible shift half of `DC_GPIO_HPD_EN` without the corresponding masks would be incomplete for generated register tables.
- Status and acknowledgment fields such as FIFO errors, HDMI errors, AFMT overflow/change flags, DP CRC done/status, fast-training status, and metadata-missed flags may be sticky or write-one-to-clear; generic read/write code must avoid accidental clears.
- Backlight and panel-power fields are platform-visible. Incorrect LVTMA power-sequence or PWM masks can cause panel blanking, brightness failures, resume flicker, or delayed power-on/off behavior.

## Test Signals

Useful validation is a combination of compile-time checks and hardware behavior on DCN20-class systems:

- Build AMDGPU/DC with DCN20 enabled. Missing or renamed fields should fail in link encoder, GPIO/DDC/HPD, resource, DMUB, clock, and stream-encoder code paths.
- Diff generated shifts/masks against adjacent instances (`DIG0` through `DIG4`, `DP0` through `DP4`) and adjacent DCN headers when hardware is expected to match, paying special attention to instance suffix drift and chunk-boundary fields.
- Exercise the sixth display link where available: hotplug, modeset, suspend/resume, DPMS off/on, HDMI/DVI output, DP SST, DP MST, eDP/panel paths, and connector combinations that map to `DIG5`/`DP5`.
- Validate HDMI behavior: audio playback, ACR stability, infoframe contents, HDR/Dolby metadata delivery where applicable, deep color/scrambling, generic packets, and absence of HDMI audio/VBI error interrupts.
- Validate DP behavior: link training at supported rates/lane counts, MST slot allocation, DSC/MSO paths if supported, secondary-data/audio packets, ALPM entry/exit, FEC/CRC diagnostics where exposed, and stable video after retraining.
- Validate GPIO sideband behavior: EDID reads on DDC1-DDC6 and DDCVGA, AUX-vs-I2C pad mode switching, HPD connect/disconnect detection for HPD1-HPD6, and stable HPD debounce/filter behavior.
- Validate panel/backlight behavior on platforms using these fields: power sequencing delays, PWM period/duty programming, lock behavior, suspend/resume brightness restoration, and no panel flicker during enable/disable.
- Watch negative signals in kernel logs and display state: black screens, link-training failures, missed vblank/page flips, EDID/AUX/I2C timeouts, HPD flapping, audio dropouts, infoframe/HDR metadata failures, CRC mismatches, underflow or FIFO errors, and resume or DPMS regressions.
