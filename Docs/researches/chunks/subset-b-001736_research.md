# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 34585-36968

## Scope

This chunk is a generated AMDGPU DCN 3.0.1 register shift/mask header slice. It contains only preprocessor constants of the form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`, plus generated register/address-block comments. There are no C functions, structs, enums, storage objects, or executable branches in this range.

The range starts mid-register in the `DIG3_HDMI_GENERIC_PACKET_CONTROL0` mask list and ends inside the `DC_GPIO_RXEN` shift list. Complete interpretation of both boundary registers requires adjacent chunks. Inside those boundaries, this slice covers:

- `DIG3` HDMI/audio/video packet and TMDS fields.
- The `dce_dc_dio_dp3_dispdec` address block for DisplayPort link `DP3`.
- The `dce_dc_dcio_dcio_dispdec` address block for DCIO, UNIPHY, panel power sequencing, and backlight PWM fields.
- The beginning of the `dce_dc_dcio_dcio_chip_dispdec` chip GPIO address block, including generic GPIO, DDC/AUX, genlock/swaplock, HPD, panel power GPIO, pad strength, AUX/HPD electrical controls, and the start of RX-enable fields.

Across lines 34585-36968, the chunk contains 2,384 source lines, 199 register/address-block comments, 1,090 `__SHIFT` defines, and 1,247 `_MASK` defines.

## Purpose

The purpose of this header region is to encode the DCN 3.0.1 hardware bit layout used by AMD display code when programming one display output path and shared DCIO/GPIO infrastructure. The companion `dcn_3_0_1_offset.h` header supplies register addresses and base indices; this file supplies the field positions and masks consumed by register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

At a subsystem level, the slice describes:

- HDMI generic packet scheduling, immediate-send state, ACR values for 32/44/48 kHz audio families, audio formatter clock control, digital backend selection, TMDS lane/control-character behavior, and HDMI double-buffer control for `DIG3`.
- DisplayPort stream programming for `DP3`, including link status, pixel format, MSA colorimetry/misc fields, stream enable/status, FIFO overflow flags, DPHY scrambler/training/CRC controls, secondary-data/audio packet controls, MST/MSE slot allocation, DSC, ALPM, and GSP packet transmission state.
- DCIO clock/reference selection, UNIPHY link and channel crossbar control for PHYs A-D, write-command delays, pin straps, panel power sequence and backlight PWM control for panel instances 0 and 1, genlock/swaplock pads, and soft-reset bits for UNIPHY/DSYNC/DCRXPHY/ZCAL paths.
- GPIO pad ownership and state for generic, DDC, DDCVGA, genlock, HPD, and panel power sequence pins, plus pad strength and AUX/HPD electrical tuning fields.

This is part of the generated hardware contract. Driver code should not hard-code these bit positions in implementation files; it should consume the generated names so register tables and ASIC-specific code remain aligned with the register database.

## Important APIs, Types, And Macros

There are no callable APIs or local types in this chunk. The exported interface is the macro namespace itself:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: 32-bit mask for the same field.
- Comments such as `//DP3_DP_SEC_CNTL` and `//DC_GPIO_DDC1_MASK` group fields by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dio_dp3_dispdec` identify generated register blocks.

Important register families in this chunk include:

- HDMI/DIG3 packet and TMDS fields: `DIG3_HDMI_GENERIC_PACKET_CONTROL5/6/1..10`, `DIG3_HDMI_GC`, `DIG3_HDMI_DB_CONTROL`, `DIG3_HDMI_ACR_*`, `DIG3_AFMT_CNTL`, `DIG3_DIG_BE_CNTL`, `DIG3_DIG_BE_EN_CNTL`, `DIG3_TMDS_*`, `DIG3_DIG_LANE_ENABLE`, and `DIG3_FORCE_DIG_DISABLE`.
- DP3 link and stream fields: `DP3_DP_LINK_CNTL`, `DP3_DP_PIXEL_FORMAT`, `DP3_DP_CONFIG`, `DP3_DP_VID_STREAM_CNTL`, `DP3_DP_STEER_FIFO`, `DP3_DP_VID_TIMING`, `DP3_DP_VID_N`, `DP3_DP_VID_M`, `DP3_DP_LINK_FRAMING_CNTL`, `DP3_DP_VID_MSA_VBID`, and `DP3_DP_VID_INTERRUPT_CNTL`.
- DP3 physical/link-test fields: `DP3_DP_DPHY_CNTL`, `DP3_DP_DPHY_TRAINING_PATTERN_SEL`, `DP3_DP_DPHY_SYM0/1/2`, `DP3_DP_DPHY_8B10B_CNTL`, `DP3_DP_DPHY_PRBS_CNTL`, `DP3_DP_DPHY_SCRAM_CNTL`, CRC control/result/status registers, fast training registers, and HBR2 pattern control.
- DP3 secondary-stream, audio, MST, and DSC fields: `DP3_DP_SEC_CNTL*`, `DP3_DP_SEC_FRAMING*`, `DP3_DP_SEC_AUD_*`, `DP3_DP_SEC_PACKET_CNTL`, `DP3_DP_MSE_*`, `DP3_DP_MSA_TIMING_PARAM*`, `DP3_DP_MSO_CNTL*`, `DP3_DP_DSC_CNTL`, `DP3_DP_DSC_BYTES_PER_PIXEL`, `DP3_DP_SEC_METADATA_TRANSMISSION`, `DP3_DP_ALPM_CNTL`, `DP3_DP_GSP8_CNTL` through `DP3_DP_GSP11_CNTL`, and `DP3_DP_GSP_EN_DB_STATUS`.
- DCIO and PHY fields: `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA/B/C/D_LINK_CNTL`, `UNIPHYA/B/C/D_CHANNEL_XBAR_CNTL`, `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `DCIO_GSL_GENLK_PAD_CNTL`, `DCIO_GSL_SWAPLOCK_PAD_CNTL`, and `DCIO_SOFT_RESET`.
- Panel and backlight fields: `PANEL_PWRSEQ0_*`, `BL_PWM0_*`, `PANEL_PWRSEQ1_*`, and `BL_PWM1_*`, including power target/state, timing delays, reference dividers, PWM period/duty/fractional enable, group lock, update-pending, frame-start update, and readback controls.
- GPIO fields: `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC4_*`, `DC_GPIO_DDCVGA_*`, `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_PWRSEQ0_*`, `DC_GPIO_PWRSEQ1_*`, `DC_GPIO_PAD_STRENGTH_1/2`, `PHY_AUX_CNTL`, `DC_GPIO_TX12_EN`, `DC_GPIO_AUX_CTRL_0/1/2`, and the start of `DC_GPIO_RXEN`.

The generated pattern is mostly all shifts first followed by all masks for each register. Fields with names ending in `_MASK` as part of the hardware field name, for example `DP_STEER_OVERFLOW_MASK`, produce generated symbols with `_MASK_MASK`; those are expected and should not be simplified manually.

## Control Flow

This chunk has no runtime control flow. Its practical flow is compile-time macro expansion:

1. DCN 3.0.1 implementation files include `dcn/dcn_3_0_1_offset.h` and `dcn/dcn_3_0_1_sh_mask.h`.
2. Register-table macros concatenate register and field names to resolve the shift/mask constants in this file.
3. Runtime code uses the resolved constants to compose MMIO writes, extract MMIO read fields, or populate ASIC-specific register tables.
4. Hardware sequencing, ordering, waits, acknowledgements, and side effects are implemented in display, GPIO, DIO, panel, audio, and DMUB code; this header only supplies bit placement.

Observed direct include points for the DCN 3.0.1 offset/mask pair are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

The `dcn301_resource.c` file then wires the generated constants into resource objects for link encoders, stream encoders, audio, panel control, GPIO/I2C/AUX, clocks, DCCG, hubbub, DSC, DWB, and DMUB-facing infrastructure.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware register state owned by the GPU display block:

- HDMI/DIG state includes generic packet send/continuous/immediate-send/pending controls, generic packet line numbers, AVMUTE/default phase/packing phase, ACR CTS/N fields and status, audio formatter clock enable/on state, DIG backend source/mode/HPD selection, TMDS control character and DC-balance settings, lane enable state, and double-buffer pending/taken/lock/disable flags.
- DP3 state includes link-training completion/status, embedded panel mode, pixel encoding/depth, stream enable/status/deferred disable, M/N timing values, link framing, video interrupt status/ack/mask, FIFO/TU overflow flags, DPHY FEC/scrambler/bypass/test state, training pattern selection, PRBS/CRC/test symbol fields, fast training controls, secondary-data/audio packet enables, MST allocation slots, DSC enable and bytes-per-pixel programming, ALPM requests, and GSP packet send/pending/deadline state.
- DCIO/UNIPHY state includes reference/output clock selection, UNIPHY power-frequency-change and pixel-valid reset state, lane invert/crossbar/link-enable programming, HPD-gated link enable behavior, lane stagger delay, write-command delay knobs, pin strap readback, and soft-reset bits for PHY/display-sync blocks.
- Panel/backlight state includes panel power sequence enable/target/state/done flags, DIGON/SYNCEN/BLON control and override bits, power-up/power-down delays, PWM reference divider, PWM period and active fractional count, PWM enable, and group lock/update-pending state.
- GPIO state includes software mask/enable/output/readback fields, pull-down or power-down controls, AUX pad mode/polarity, DDC line strength, HPD delayed/raw sense and receive fields, panel power GPIO fields, pad drive strength, AUX/HPD slew/spike filter/bias/receiver/comparator tuning, and TX12/RXEN routing.

Persistence is hardware-defined. Many control fields remain effective until a modeset, link reconfiguration, backlight update, GPIO ownership change, power-gating transition, suspend/resume path, or ASIC reset reprograms them. Status and pending fields can change asynchronously with link training, secondary packet sends, hotplug activity, panel power sequencing, or hardware double-buffer updates. The generated masks do not encode read-only, write-one-to-clear, or side-effect semantics, so callers must follow the hardware programming model.

## Dependencies And Integration Points

This chunk depends on generated register metadata staying synchronized across files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h` pairs with this header by providing register offsets and base-index constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c` includes the pair and uses resource macros such as `SR`, `SRI`, `SRII`, and field macros to populate DCN301 register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c` includes the pair and builds DMUB common register field masks/shifts with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.h` maps panel/backlight fields from this chunk into `struct dcn301_panel_cntl_shift` and `struct dcn301_panel_cntl_mask`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.c` consumes those fields for panel power/backlight initialization, status checks, backlight level reads, and stored level handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn301/dcn301_dio_link_encoder.c` constructs DCN301 link encoders for UNIPHY transmitters A-G; the UNIPHY and DIG/DP fields in this chunk are part of the register namespace used by related DIO/link encoder paths.
- GPIO service, hardware factory, and translate layers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/` consume the same generic register model for DDC, HPD, generic GPIO, and genlock/swaplock ownership and translation.
- Audio and stream encoder paths rely on the DIG/HDMI/DP secondary-packet and ACR field definitions when HDMI/DP audio and info packets are programmed through DCN resource tables.

The direct contract is preprocessor name stability. A missing or renamed define usually fails at build time when a register table expands. A numerically wrong shift or mask can compile cleanly and cause bad MMIO behavior at runtime.

## Risks And Edge Cases

- The chunk starts after the shifts and early masks for `DIG3_HDMI_GENERIC_PACKET_CONTROL0`. Whole-file reconciliation must not treat this chunk alone as the complete definition for that register.
- The chunk ends before the `DC_GPIO_RXEN` masks and before later GPIO chip fields. Adjacent chunks are required for a complete RX-enable and chip GPIO view.
- Several field names naturally include `MASK`, which produces symbols such as `DP_STEER_OVERFLOW_MASK_MASK` and `DCIO_GENLK_CLK_GSL_MASK_MASK`. These are generated names, not typographical duplicates.
- Wrong HDMI generic packet, ACR, or double-buffer masks can produce silent audio/infoframe failures, stale metadata transmission, missed immediate sends, or incorrect CTS/N programming.
- DP3 contains many status, pending, ack, interrupt, CRC, training, FEC, MST, DSC, ALPM, and GSP fields. Treating these as ordinary read/write control bits can cause interrupt storms, missed acknowledgements, link training instability, or secondary-packet timing failures.
- DP MSE/MST allocation and MSO fields pack slot, timing, and stream data into narrow bit ranges. Numeric drift can affect only MST, DSC, or multi-stream cases, making failures topology-dependent.
- UNIPHY link and channel crossbar fields are repeated for PHYs A-D. Copy/generator drift in one instance can make failures connector-specific while other ports still work.
- Soft-reset masks for UNIPHY, DSYNC, DCRXPHY, and ZCAL are side-effect-sensitive. Incorrect or stale bit positions can reset the wrong hardware block or leave a block held in reset.
- Panel power sequence and PWM fields directly affect embedded panel power, backlight timing, and brightness. Bad masks can cause black panels, flicker, incorrect brightness readback, or unsafe sequencing around DIGON/BLON/SYNCEN.
- GPIO DDC/AUX/HPD fields are shared with connector detection and I2C/AUX transactions. Incorrect ownership, pull-down, pad mode, polarity, or receive-enable masks can break EDID reads, HPD detection, DP AUX communication, or wake/hotplug routing.
- AUX/HPD electrical tuning fields (`FALLSLEWSEL`, spike filter, bias/current/resistance/comparator/slew settings) should be changed only according to hardware guidance; the header cannot express board-specific signal-integrity constraints.
- Cross-ASIC reuse is risky. Many names resemble DCN 3.0.0 or DCN 3.0.2 headers, but DCN301-specific field layout should be treated as authoritative for Vangogh/DCN301.

## Test Signals

Useful validation signals for this generated-header chunk are build-time macro expansion plus hardware behavior on DCN301-class systems:

- Build AMDGPU display code with DCN301 enabled so `dcn301_resource.c`, `dmub_dcn301.c`, panel control, DIO, GPIO, audio, and DMUB register tables expand this header successfully.
- Compare this range against the register generator output and `dcn_3_0_1_offset.h` to ensure every register used by the resource tables has matching offset, shift, and mask definitions.
- Exercise HDMI output on the `DIG3` path, including generic info packets, AVMUTE, audio formatter clocking, ACR status, and packet double-buffer updates.
- Exercise DisplayPort link bring-up on the `DP3` path across SST, MST if supported, DSC, secondary-data packet transmission, audio, link retraining, suspend/resume, and hotplug/unplug cycles.
- Run DP link-training diagnostics that cover DPHY training pattern, FEC readiness/active status, scrambler state, CRC readback, PRBS/test-symbol paths, and fast-training status.
- Validate MST/MSE allocation and MSO/DSC paths with multi-stream or compressed modes, watching for slot allocation errors, deadline-missed GSP status, and MSA/VBID anomalies.
- Test embedded panel power sequencing and backlight control through brightness changes, DPMS off/on, boot splash handoff, suspend/resume, and backlight readback. Watch `PANEL_PWRSEQ*_STATE`, `BL_PWM*_GRP1_REG_UPDATE_PENDING`, and PWM enable/period/duty behavior.
- Exercise HPD, DDC, AUX, and GPIO paths across all available connectors: EDID reads, HPD IRQs, HPD RX sense, DP AUX transactions, DDCVGA if present, genlock/swaplock pins if supported, and generic GPIO ownership transitions.
- Check reset and recovery paths that touch `DCIO_SOFT_RESET`, UNIPHY link state, panel power sequencing, and GPIO receive-enable state after GPU reset or display core reinitialization.

## Cross-Chunk Notes

This chunk is a middle slice of a large generated mask header. The final per-file report should merge it with adjacent chunks to describe the full `DIG3`, `DP3`, DCIO, and GPIO chip field maps. In particular, adjacent chunks are needed for the beginning of `DIG3_HDMI_GENERIC_PACKET_CONTROL0` and the rest of `DC_GPIO_RXEN`.
