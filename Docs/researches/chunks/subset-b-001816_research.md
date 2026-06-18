# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 34974-37370

## Scope

This chunk is a generated DCN 3.1.2 register-field mask slice from `dcn_3_1_2_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` macros for field bit positions, `_MASK` macros for raw 32-bit register masks, and comment markers that name hardware registers and address blocks. There are no C functions, structs, enums, executable branches, loops, or in-memory state objects in this range.

The slice starts in the tail of `DP1_DP_SEC_CNTL2`, covers the rest of the DP1 secondary-packet and late DisplayPort controls, then covers the full `dce_dc_dio_dig1_dispdec` DIG1 encoder/HDMI/TMDS field surface, the full `dce_dc_dio_dp2_dispdec` DP2 DisplayPort field surface, the full `dce_dc_dio_dig2_dispdec` DIG2 encoder/HDMI/TMDS field surface, and the beginning of `dce_dc_dio_dp3_dispdec` through the first `DP3_DP_DPHY_SYM0` symbol fields.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit layout ABI between AMDGPU Display Core code and DCN 3.1.2 display hardware. Companion offset headers identify MMIO register addresses; this mask header identifies each field's low bit and mask so display code can pack values, decode readbacks, and perform read/modify/write updates without embedding magic bit numbers in functional code.

Major hardware areas represented here:

- DP1 late secondary-packet controls: GSP1-GSP11 send/status fields, line-number fields, double-buffer disable/status fields, MSA/VBID override fields, secondary metadata transmission, DSC byte-per-pixel, ALPM PHY sleep/standby control, and GSP8-GSP11 per-packet controls.
- `DIG1` digital encoder fields: front-end mode and source selection, output CRC, clock/test/random patterns, FIFO status, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet controls, HDMI deep-color/general-control bits, audio formatter enable, backend enable/control, TMDS control, sync/control-character programming, DC balancer, and DIG version/force-disable.
- DP2 link and stream fields: link status, pixel format, MSA colorimetry, lane configuration, video stream enable/status, steer FIFO overflow, MSA misc, DPHY controls, video M/N timing, link framing, training patterns, 8b/10b and PRBS/scrambler controls, CRC controls/results, fast training, secondary packet control, audio M/N/timestamp, MST/MSE rate and slot allocation controls, MSA timing parameters, MSO, DSC, metadata, ALPM, and GSP8-GSP11 controls.
- `DIG2` duplicates the DIG1 encoder/HDMI/TMDS surface for the next digital encoder instance, with identical field families under the `DIG2_` prefix.
- DP3 begins at the end of this range with link, pixel format, MSA, stream, FIFO, DPHY internal/timing/M/N/framing/interrupt, FEC/scrambler/training, and the first DPHY symbol pattern fields.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's unshifted mask within the 32-bit register.
- `// addressBlock: ...` comments identify the display hardware aperture for following definitions.
- `//<REGISTER>` comments group field definitions by MMIO register.

Important field families in this chunk:

- Secondary data packet controls for DP1 and DP2 include GSP send requests, pending bits, active bits, deadline-missed bits, any-line mode, send-in-idle mode, line-reference selection, target line numbers, MSO lane enables, and double-buffer disable/status bits. These fields are used for DisplayPort secondary data packets such as infoframes, metadata, PPS/DSC-related packets, and generic stream packets.
- `DP*_DP_DB_CNTL` fields expose double-buffer pending/taken/clear/lock/disable state plus vupdate-specific pending/taken/clear bits. These are synchronization controls for programming packet/timing-related registers at safe update boundaries.
- MSA/VBID fields cover pixel encoding/component depth/combine, colorimetry misc bytes, MSA timing parameters, VBID override bits, stereo sync override, VBID field polarity, and MSA insertion location. These are part of the DisplayPort main stream attribute and video blanking ID programming path.
- DSC and MSO fields include DSC mode, slice width, bytes per pixel, MSO per-lane secondary packet enables, and metadata packet enable/line controls. These fields integrate compressed streams and multi-stream/multi-segment output paths with secondary data transmission.
- DP link/DPHY fields cover link-training-complete/status, lane count, stream enable/defer/status, steer/TU overflow interrupts and ACKs, FEC enable/ready/active state, scrambler selection/disable/advance/BS count/K-code, bypass/skew controls, training-pattern selection, symbol pattern registers, 8b/10b reset/disparity controls, PRBS enable/select/seed, CRC enable/selector/mask/result, MST CRC controls/status, and fast-training controls/status.
- DP MST/MSE fields include rate calculation controls, stream-rate updates, stream allocation table words, SAT update triggers/status, link timing, misc controls, and per-slot/status masks. These support DisplayPort multi-stream transport allocation and link scheduling.
- DIG front-end and backend fields select pixel source, enable the DIG front end/backend, select mode, report FIFO underflow/overflow, and expose DIG type/version/force-disable. The field names distinguish source/mode controls from status bits such as FIFO error state.
- HDMI packet fields cover metadata packet output, HDMI enable, keepout modes, null/audio/ACR/VBI/infoframe/generic packet send controls, line references, pending/status/readback bits, general control packet fields, audio sample rate/layout/channel count, and ACR CTS/N programming/readback for 32 kHz, 44.1 kHz, and 48 kHz families.
- TMDS fields cover clock pattern/test pattern data, random pattern seed, data and control character patterns, per-control-bit selection, feedback and stereo sync controls, DC balancer state, sync DC-balance characters, per-control-lane generator selection/delay/invert/modulation/feedback/pattern-enable fields, and a TMDS 2-bit counter enable.
- Interrupt-like fields in this range use a familiar status/ack/mask pattern: stream-disable interrupts, steer/TU overflow flags and ACKs, secondary packet pending/active/deadline bits, FIFO status, HDMI packet pending/sent state, and CRC result-valid state.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code combines these constants with register addresses and register helper macros. A typical usage pattern is:

1. Select the DCN 3.1.2 register address from a companion offset/header table.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack, update, or extract a field.
3. Perform an MMIO write, read, or read/modify/write through AMD display register helpers.
4. Let display hardware retain, consume, update, or clear the register-backed state according to the register semantics.

The state represented here is hardware state rather than driver-owned memory:

- Persistent configuration fields include DP link format, lane count, pixel encoding/depth, MSA/VBID values, DSC/MSO metadata settings, secondary packet enable/line scheduling, DIG source/mode/backend enables, HDMI packet/audio/ACR controls, TMDS patterns, DPHY scrambler/FEC/training configuration, and MST/MSE scheduling parameters.
- Volatile status/readback fields include link-training-complete, stream status, FIFO overflow/underflow, packet pending/sent/active/deadline state, DPHY FEC active status, CRC result valid/results, fast-training status, M/N readbacks, ACR CTS/N readbacks, SAT update status, and GSP enable double-buffer status.
- ACK, clear, reset, send, update, and trigger fields are side-effecting write paths. Examples include GSP send bits, `DP_DB_TAKEN_CLR`, vupdate taken clear, stream-disable ACK, steer/TU overflow ACKs, CRC enable/result capture controls, 8b/10b reset, MSE rate/SAT update requests, and HDMI packet send controls.
- Double-buffered fields are timing-sensitive. The `DP*_DP_DB_CNTL` and `DP*_DP_GSP_EN_DB_STATUS` definitions indicate that some GSP enable changes and packet controls can be staged and taken at update boundaries instead of immediately.
- Shared transport state must be sequenced with the active display pipe. DP link training, FEC, scrambler, MST/MSE slot allocation, secondary packet scheduling, DSC PPS/metadata, and ALPM PHY sleep/standby controls interact with live stream state and cannot be safely treated as independent booleans.

The masks do not encode ordering constraints. Correct callers still need to hold the appropriate display locks, use update locks or double-buffering where required, poll/observe pending and active status bits, avoid clearing latched interrupts before service, and respect link-training, stream-disable, power, and vblank/vupdate sequencing.

## Dependencies And Integration Points

This chunk integrates with:

- Companion DCN 3.1.2 register offset/address headers for the same ASIC register namespace, especially generated `dcn_3_1_2_offset.h` style tables.
- AMDGPU Display Core register helper macros and generated register tables that consume `<register>__<field>__SHIFT` and `<register>__<field>_MASK` constants for `REG_GET`, `REG_SET`, `REG_UPDATE`, and similar operations.
- DisplayPort stream setup code that programs link status expectations, lane count, pixel encoding/component depth, MSA/VBID, video M/N, link framing, stream enable/defer, DPHY training, FEC, scrambler, PRBS/test patterns, CRC, and fast training.
- DisplayPort secondary-packet code for GSP packet enables, line scheduling, metadata packets, DSC PPS/bytes-per-pixel fields, MSO per-lane packet enables, and packet send/pending/deadline status.
- MST/MSE scheduling code that updates rate controls, stream allocation table words, SAT update triggers, link timing, and MSE status fields for multi-stream transport.
- DIG encoder setup code that selects front-end source/mode, backend enables, FIFO handling, output CRC, HDMI/TMDS mode selection, test patterns, and force-disable/version checks.
- HDMI output code that manages metadata, audio, ACR, VBI, AVI/vendor/generic infoframes, general control packets, deep color, packet keepout behavior, and packet send/readback status.
- Audio formatter code that coordinates HDMI audio packet controls, AFMT enable, channel/sample metadata, and ACR N/CTS values/readbacks.
- Diagnostics and validation tooling that reads DP/DPHY CRC results, DIG output CRC, FIFO status, link/training status, packet status, TMDS patterns, and MST/MSE allocation status.
- Power-management and link idle paths using DP ALPM PHY sleep/standby send/pending/immediate/line-number fields and `DP_LINK_TRAINING_SWITCH_BETWEEN_VIDEO`.

Because these are generated preprocessor macros, name mismatches are usually compile-time failures only where a macro is referenced. Numeric mask or shift drift can compile cleanly and then misprogram MMIO fields at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.2 register specification is the main risk. An incorrect mask or shift can silently write the wrong bits in display hardware registers, affecting link training, stream enable, packet scheduling, HDMI audio/infoframes, MST allocation, or PHY state.
- This range is highly repetitive across DP1/DP2/DP3 and DIG1/DIG2 instances. Prefix mistakes can target the wrong link or encoder instance while still compiling if the mistaken macro exists.
- The chunk starts and ends in the middle of logical hardware coverage: it begins after the first `DP1_DP_SEC_CNTL2` shift fields and ends partway through DP3 DPHY symbol definitions. The merge/reconciliation lane must combine adjacent chunks for a complete per-file view.
- Side-effecting bits are easy to misuse in generic read/modify/write helpers. Clear/ACK/reset/send/update bits should be programmed with awareness of hardware semantics so pending interrupts, packet sends, MSE updates, CRC captures, and reset sequences are not lost or repeated unintentionally.
- Double-buffer and update-boundary fields require sequencing. Misusing GSP enable DB disable/status, `DP_DB_LOCK`, pending/taken/clear bits, or vupdate taken fields can cause partially applied secondary-packet changes or visible packet/timing glitches.
- DP secondary packet and metadata fields interact with DSC, MSO, MST, and HDMI/DIG packet paths. Incorrect line numbers, any-line mode, line-reference selection, or send-in-idle behavior can create missed deadlines or malformed metadata on the wire.
- Link PHY controls are stateful and hardware-sensitive. FEC, scrambler, bypass, training pattern, 8b/10b, PRBS, CRC, fast-training, and ALPM fields can disrupt active links if toggled outside the expected training or idle windows.
- MST/MSE rate and SAT update fields can affect bandwidth allocation for multiple streams. Bad values or missed update-status checks can cause link oversubscription, stream starvation, or incomplete slot updates.
- HDMI ACR/audio/infoframe fields must match the mode and audio format. Incorrect CTS/N, sample-rate, layout, deep-color, or packet-control fields can produce audio dropouts or invalid HDMI metadata despite a lit display.
- Wide fields such as M/N, ACR CTS/N, timestamp, symbol patterns, SAT words, CRC results, packet line numbers, and metadata payload-related controls have no type checking here. Callers must validate ranges and units before packing values.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display smoke tests:

- Build AMDGPU with DCN 3.1.2 support and ensure all referenced generated macro names resolve.
- Run generated-header consistency checks that each field has the expected `_SHIFT`/`_MASK` pair, masks fit in 32 bits, and fields do not overlap unexpectedly within each register.
- Exercise DisplayPort modeset paths using DP1, DP2, and DP3-adjacent hardware coverage, including lane count, pixel format, MSA/VBID, stream enable/defer, video M/N, link framing, and stream-disable interrupt handling.
- Run link-training and PHY diagnostics that cover DPHY training patterns, FEC enable/ready/active status, scrambler controls, PRBS, 8b/10b reset/disparity, CRC enable/result-valid/readback, and fast-training status.
- Validate DP secondary packet behavior for GSP1-GSP11, metadata packets, DSC PPS/bytes-per-pixel, MSO enables, any-line/line-number scheduling, send-in-idle, pending/active/deadline status, and double-buffer taken/clear behavior.
- Exercise DSC/MSO/MST cases, checking MSE rate update, SAT programming/update/status, link timing, MSA timing parameter fields, and stream allocation behavior under multiple stream configurations.
- Exercise HDMI output on DIG1 and DIG2, including HDMI enable, deep color/general control, metadata/infoframe/generic packet send controls, VBI/null/audio packets, ACR CTS/N programming, and packet status/readbacks.
- Run audio validation through DIG1/DIG2 HDMI paths, checking AFMT enable, audio sample rate/layout/channel count, ACR values, and absence of audio dropouts across mode changes.
- Use display diagnostics to verify DIG output CRC and DP DPHY CRC results, FIFO underflow/overflow status, TMDS test/control patterns, and random pattern seed behavior.
- Test suspend/resume, display blank/unblank, link idle, and ALPM paths to ensure PHY sleep/standby send/pending/immediate/line-number fields do not strand links or interfere with link training between video periods.

## Chunk-Specific Summary

Lines 34974-37370 define a dense DCN 3.1.2 register-field surface rather than executable code. The most important responsibilities in this slice are DP1 late secondary-packet scheduling, complete DIG1 and DIG2 encoder/HDMI/TMDS field maps, complete DP2 link/PHY/secondary-packet/MST/MSO/DSC field maps, and the opening DP3 link/PHY field map. Correctness depends on exact generated masks and shifts, instance-correct macro use, and hardware behavior under modeset, DP link training, secondary packet delivery, DSC/MSO/MST, HDMI audio/infoframes, CRC/test-pattern diagnostics, ALPM, and interrupt/status handling.
