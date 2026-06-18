# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 19737-22116

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C code; it publishes `#define` constants for field shifts and masks used by AMDGPU display code when packing and unpacking DCN 3.0.3 MMIO register values.

The selected range spans 2,372 macro/comment lines. It starts at the tail of the `DME1_DME_CONTROL` mask block, covers `DME1_DME_MEMORY_CONTROL`, then moves through the first digital-output instance's DIO encoder blocks: `DIG1`, `DP1`, DCIO, LVTMA/backlight power sequencing, and GPIO/DDC/AUX/HPD pad controls. The chunk ends inside `DC_GPIO_RXEN`; later receive-enable masks for the remaining HPD and panel-control pins are in the next chunk.

Although this file is under a local `ceph-client` source mirror, this content is AMD Display Core hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation sites, locks, or callbacks in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field within a 32-bit register value.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field, usually written with an `L` suffix.

Major macro families in this slice:

- `DME1_DME_CONTROL` tail and `DME1_DME_MEMORY_CONTROL`: metadata double-buffer status/clear/disable bits and DME memory power force, disable, state, and default low-power-state fields.
- `DIG1_DIG_FE_CNTL`: digital front-end source selection, stereosync selection/gating, start bit, digital-bypass selection, pixel input selection, Dolby Vision enable/missed-metadata status, symbol-clock status, and TMDS pixel/color format.
- `DIG1_DIG_OUTPUT_CRC_*`, `DIG1_DIG_CLOCK_PATTERN`, `DIG1_DIG_TEST_PATTERN`, and `DIG1_DIG_RANDOM_PATTERN_SEED`: output CRC enable/link/data selection, CRC results, static/random test-pattern controls, clock pattern, and random-pattern seed behavior.
- `DIG1_DIG_FIFO_STATUS`: FIFO level error/ack, overwrite level, calibrated average/min/max levels, read clock source, calibration status, and forced recalculation/recompute bits.
- `DIG1_HDMI_*`: HDMI metadata packet control, core HDMI control/status, audio packet delay, ACR packet control, VBI packet control, audio/MPEG infoframe control, generic packet send/continuous/line-reference/update-lock controls for packets 0 through 14, immediate-send/pending bits, global control packet fields, double-buffer controls, programmed and status CTS/N values for 32 kHz, 44.1 kHz, and 48 kHz families, and AFMT audio clock enable/status.
- `DIG1_DIG_BE_*` and `DIG1_TMDS_*`: digital back-end enable/mode/source/HPD selection, dual-link and lane controls, TMDS control-character generation, sync-character patterns, data-balance controls, CTL bit generation, DIG type/version, lane enable, clock enable, and force-disable.
- `DP1_DP_*`: DisplayPort link count/rate/spread, pixel format, MSA colorimetry and timing fields, video stream enable/status, steering FIFO, VBID/MSA miscellaneous data, video N/M values, link framing, HBR2 eye-pattern control, interrupts, DPHY control/training/symbol/test/scramble/CRC/fast-training fields, secondary-data packet controls, audio N/M and readback, MSE/MST rate and slot allocation controls/status, MSO controls, DSC bytes-per-pixel, ALPM controls, metadata transmission, and generic SDP controls for GSP8 through GSP11.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`: generic DCIO GPIO-style pins, clock gating/enable/status, reference clock mux/divider/root-gate control, and spread-spectrum state.
- `UNIPHYA_*` and `UNIPHYB_*`: link control and channel crossbar fields for the first two display PHY blocks, including enable, mode, connection, calibration, powerdown, output-enable, and lane crossbar mappings.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, and `DCIO_SOFT_RESET`: write-command delay tuning, strap reporting for audio/backlight/spread-spectrum and panel/connection capabilities, and soft resets for DIO, DP AUX, DC GPIO, and audio-related logic.
- `LVTMA_PWRSEQ_*`, `BL_PWM_*`, and `BL_PWM_GRP1_REG_LOCK`: embedded-panel power sequencing, state/readback, reference divider, delay programming, backlight PWM enable/debug/fractional and period controls, and grouped PWM register locking.
- `DCIO_GSL_GENLK_PAD_CNTL` and `DCIO_GSL_SWAPLOCK_PAD_CNTL`: genlock/swaplock pad mux, polarity, mask, and receive fields.
- `DC_GPIO_*`: generic GPIO, DDC1, DDC2, DDCVGA, genlock, HPD, power-sequence, pad-strength, PHY AUX, TX12 enable, AUX/I2C/HPD electrical tuning, and receive-enable fields. The chunk ends after `DC_GPIO_RXEN` masks for `GENERICA` through `HPD3`.

These macros are normally consumed through token-pasting helpers such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `SF(reg, field, post_fix)`, or block-specific register-table macros, rather than by direct handwritten references to every generated name.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMD Display Core and DMUB code:

1. DCN 3.0.3 users include the matching offset header and this shift/mask header.
2. Register helpers paste register and field tokens into names such as `DIG1_HDMI_CONTROL__HDMI_DEEP_COLOR_ENABLE_MASK` or `DP1_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE__SHIFT`.
3. Static register/field tables and helper macros convert those constants into packed MMIO reads, writes, field updates, interrupt masks, and firmware-service register descriptors.
4. Modeset, link-training, audio, HPD, AUX/I2C, backlight, panel-power, and interrupt paths perform the actual ordering around the raw bitfields.

The direct DCN 3.0.3 include sites visible in this tree are `display/dmub/src/dmub_dcn303.c` and `display/dc/irq/dcn303/irq_service_dcn303.c`. `dmub_dcn303.c` uses the generated masks and shifts to populate `dmub_srv_dcn303_regs` common register fields through `FD_MASK` and `FD_SHIFT`. `irq_service_dcn303.c` uses the same generated register database with `SRI` and `IRQ_REG_ENTRY` style macros for interrupt enable, acknowledge, and status register descriptors. The broader DIO, stream encoder, AUX, GPIO, and audio flows are implemented in shared AMD Display Core components that expect these ASIC-specific definitions to match the offset file.

The selected macros do not encode sequencing. Consumers still must order link disable/enable, clock enablement, DIO/PHY reset, DP link training, HDMI packet setup, double-buffer update/clear, MST/MSO slot programming, panel power sequencing, AUX/DDC ownership, HPD interrupt acknowledgement, and suspend/resume restore correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes bit layouts for hardware state maintained by the GPU display controller.

Important hardware state represented by the fields includes:

- DME metadata and memory-power state: metadata double-buffer status/clear/disable bits plus DME memory force/disable/default low-power controls.
- Digital encoder state: selected source, start/disable status, front-end/back-end clock status, DIG mode, HPD selection, dual-link settings, lane enables, TMDS control-character patterns, DCBALANCER state, and test-pattern programming.
- HDMI transport state: AVMUTE/error status, deep color and scrambling controls, audio delay, ACR send/continuous/auto-send/source/N-multiple controls, infoframe and generic packet scheduling, immediate-send pending bits, double-buffer state, and programmed/readback ACR N/CTS values.
- DisplayPort transport state: link rate/count/spread, stream enable, MSA timing and colorimetry, VBID overrides, DPHY training/scrambling/CRC/test state, fast-training state/acknowledge, secondary-data packet enable/scheduling, audio N/M, MST/MSE allocation, MSO control, DSC bytes-per-pixel, ALPM requests/pending state, and generic SDP enable/pending/deadline status.
- DCIO/PHY state: clock and reference-clock selection/gating, UNIPHY link modes and lane crossbars, soft-reset bits, strap-derived capabilities, and write-delay tuning.
- Panel and backlight state: LVTMA power-sequence control/state, delay counters, reference divider, PWM enable/period/fractional controls, PWM debug and register locks.
- GPIO/DDC/AUX/HPD state: output masks, output values, output enables, sensed values, pad pull-up/pull-down/drive-strength/receive controls, AUX pad mode and polarity, genlock/swaplock pins, HPD electrical tuning, and generic RX enables.

Persistence is hardware-defined. Configuration bits generally remain until overwritten, reset, power-gated, or restored after suspend/resume. Status, pending, acknowledge, clear, lock, readback, calibration, CRC, and error fields may be read-only, sticky, write-one-to-clear, self-clearing, or latch-on-read depending on the register. This generated header gives only shifts and masks; it does not describe access type, reset values, or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.3 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which provides matching MMIO offsets and base-index constants.
- `sienna_cichlid_ip_offset.h` and DCN base-segment macros used to turn generated offsets into absolute register addresses.
- AMD Display Core register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, `SF`, `SRI`, and block-specific register-list macros.
- DCN 3.0.3 DMUB register descriptors in `display/dmub/src/dmub_dcn303.c`.
- DCN 3.0.3 interrupt descriptors in `display/dc/irq/dcn303/irq_service_dcn303.c`.
- Shared DIO, DP/HDMI stream encoder, AUX/DDC, GPIO, HPD, backlight, and panel-power code paths that use the ASIC-specific offset and shift/mask headers to program hardware.

The chunk is source-tree aligned with DCN 3.0.3 hardware instance 1 naming. Similar macro families exist for other DIG/DP instances and other DCN ASIC generations, but the numeric masks in this file are only valid for the matching DCN 3.0.3 register layout.

## Risks And Edge Cases

- Mask/shift drift is the central risk. A wrong value still compiles but can silently write or read the wrong hardware bits.
- This chunk begins and ends inside larger generated blocks: it starts after the beginning of `DME1_DME_CONTROL` and stops inside `DC_GPIO_RXEN`. Adjacent chunks are required for complete file-level coverage.
- Repeated instance naming is copy-sensitive. `DIG1`/`DP1` fields look like other encoder instances, but a prefix mismatch can route programming to the wrong display output.
- HDMI and DP packet scheduling has pending, immediate-send, continuous-send, line-reference, deadline-missed, and double-buffer fields. Treating pending or clear bits as plain configuration can lose metadata packets, infoframes, or audio packets.
- DP link-training and DPHY fields are timing-sensitive. Incorrect training pattern, scramble, CRC, fast-training, or ALPM masks can cause link bring-up failures that only appear with specific panels, cables, rates, or power states.
- MST/MSE/MSO and DSC fields are bandwidth-sensitive. Bad slot allocation, rate X/Y, secondary-data enable, or bytes-per-pixel masks can produce black screens, corruption, audio loss, or multi-stream routing failures.
- GPIO/DDC/AUX/HPD fields mix output, enable, receive, pull, drive-strength, pad-mode, polarity, and electrical compensation controls. A bad mask can break EDID reads, AUX transactions, HPD detection, backlight control, or external genlock/swaplock.
- Power-sequence and PWM fields can affect embedded panels. Incorrect LVTMA sequencing, delay, PWM period, lock, or soft-reset handling can cause visible flicker, panel power timing violations, or backlight state loss across suspend/resume.
- Status/ack fields such as error, CRC, fast-training complete, secondary-packet pending, double-buffer taken, and interrupt acknowledgement may have clear-on-write semantics not visible in this header.

## Test Signals

Useful validation signals for changes touching this chunk or generated data around it include:

- Build coverage for DCN 3.0.3 AMDGPU display paths; token-pasting consumers catch missing or renamed macros at compile time.
- HDMI modeset tests covering deep color, scrambling, AVMUTE behavior, infoframes, generic metadata packets, Dolby Vision metadata, and audio ACR/N/CTS programming.
- DisplayPort link-training tests across link rates and lane counts, including DPHY training patterns, scrambling, CRC diagnostics, HBR2 eye pattern, fast training, ALPM, and link recovery.
- DP MST/MSO/DSC tests that verify stream allocation, MSE slot programming, secondary-data packets, VBID/MSA timing, and compressed stream bytes-per-pixel values.
- Audio playback over HDMI and DP, including sample-rate switching, infoframe generation, audio mute/unmute, N/M readback, and hotplug after modeset.
- AUX/DDC/HPD validation: EDID/DPCD reads, HPD and HPD RX interrupts, AUX polarity/pad mode behavior, GPIO receive states, and retry/error reporting.
- Embedded-panel tests: LVTMA panel power sequencing, backlight PWM enable/period/fractional behavior, register lock handling, suspend/resume, and runtime power-management recovery.
- Diagnostic register reads during failures: packet pending/deadline bits, double-buffer pending/taken bits, FIFO status, DP CRC results, DPHY training state, DC_PINSTRAPS, HPD status, AUX/DDC GPIO sense bits, and soft-reset status.
