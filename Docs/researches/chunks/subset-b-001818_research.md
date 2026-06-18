# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 39762-42177

## Chunk Scope

This chunk is a generated AMD DCN 3.1.2 ASIC register shift/mask header segment. It contains preprocessor constants only: `#define` pairs ending in `__SHIFT` and `_MASK` for bitfield extraction and register writes. There are no C functions, structs, enums, or executable control paths in the range. The behavioral content is the hardware contract encoded by the bit positions, masks, repeated display-engine instances, and address-block comments.

The chunk covers 2,162 macro definitions across these register families:

- `DIG4_*`: HDMI, TMDS, digital backend, and AFMT clock/control fields for digital link instance 4.
- `AFMT0_*` through `AFMT4_*`: repeated audio formatter packet, infoframe, CRC, test-ramp, status, source-select, and memory-power bitfields for five DIG/AFMT display pipes.
- `DME0_*` through `DME4_*`: repeated display metadata engine control and memory-power bitfields.
- `VPG0_*` through `VPG4_*`: repeated video packet generator generic-packet RAM access, frame/immediate update, status, memory-power, ISRC, and MPEG infoframe bitfields.
- `DP_AUX0_*`: DisplayPort AUX channel control, software/light-sleep status, data FIFO access, DPHY timing/status, and GTC synchronization bitfields.

## Purpose

The header supplies the mask and shift constants consumed by AMDGPU Display Core register-access macros. Driver code can compose read-modify-write operations by naming fields such as `DIG4_HDMI_DB_CONTROL__HDMI_DB_PENDING_MASK` and `DIG4_HDMI_DB_CONTROL__HDMI_DB_PENDING__SHIFT` instead of hard-coding numeric bit positions. This matters because the surrounding display driver programs hardware blocks directly and needs the generated register schema to match the DCN 3.1.2 register specification exactly.

Within this chunk, the constants describe HDMI/AFMT/audio packet programming for one digital output (`DIG4`) plus replicated AFMT, DME, and VPG blocks for display pipes 0 through 4. The final section describes DP AUX instance 0, including arbitration, interrupt, transfer status, PHY timing, and GTC sync control/status.

## Important Macro Groups

### DIG4 HDMI, TMDS, and Backend Fields

The chunk begins mid-register with `DIG4_HDMI_GENERIC_PACKET_CONTROL5` immediate-send and pending masks for generic packets 9 through 14. It then defines:

- `DIG4_HDMI_GC`: AVMUTE, continuous AVMUTE, default phase, packing phase, and packing override fields.
- `DIG4_HDMI_GENERIC_PACKET_CONTROL1` through `CONTROL4`, `CONTROL7` through `CONTROL10`: generic packet line scheduling fields for packet slots 0 through 14, plus per-slot double-buffer pending flags in `CONTROL10`.
- `DIG4_HDMI_DB_CONTROL`: HDMI and vupdate double-buffer pending/taken/clear/lock/disable fields.
- `DIG4_HDMI_ACR_*` and `DIG4_HDMI_ACR_STATUS_*`: audio clock regeneration CTS/N fields for 32, 44.1, and 48 kHz base rates and current status.
- `DIG4_AFMT_CNTL`: audio formatter clock enable/on status.
- `DIG4_DIG_BE_CNTL` and `DIG4_DIG_BE_EN_CNTL`: digital backend dual-link, swap, red/blue switch, front-end source select, link mode, HPD select, enable, and symbol clock status.
- TMDS fields: sync phase, control-character enables, feedback selection/delay, stereo sync select, sync character patterns, control bits, DC-balancer behavior, control generator parameters for CTL0/1 and CTL2/3, digital version, and forced disable.

These definitions are integration points for HDMI bring-up, audio infoframe scheduling, link enable/disable sequencing, and TMDS compliance/test programming.

### AFMT0-AFMT4 Audio Formatter Fields

Each AFMT instance has the same visible field layout. The repeated per-instance blocks include:

- `AFMT*_AFMT_VBI_PACKET_CONTROL`: HDMI audio packets per line and max-send control.
- `AFMT*_AFMT_AUDIO_PACKET_CONTROL2`: layout override/select, channel enable bitmap, DP audio stream ID, HBR override, and IEC 60958 OSF override.
- `AFMT*_AFMT_AUDIO_INFO0` and `AUDIO_INFO1`: HDMI audio infoframe checksum, channel count, coding type, checksum offset, extension coding type, channel allocation, level shift, downmix inhibit, and LFE playback-level fields.
- `AFMT*_AFMT_60958_0`, `_1`, and `_2`: channel-status fields including category code, source number, left/right channel numbers, sampling frequency, clock accuracy, word length, original sampling frequency, validity bits, and channel numbers for channels 2 through 7.
- `AFMT*_AFMT_AUDIO_CRC_CONTROL` and `AUDIO_CRC_RESULT`: audio CRC enable/continuous/source/channel/count, done status, and result data.
- `AFMT*_AFMT_RAMP_CONTROL0` through `RAMP_CONTROL3`: audio test ramp max/min/inc/dec counts, sign, and test-channel disable bitmap.
- `AFMT*_AFMT_STATUS`: audio enable, HBR enable, FIFO overflow, and AZ audio-enable change indication.
- `AFMT*_AFMT_AUDIO_PACKET_CONTROL`: sample-send, double-buffer enable, FIFO reset on disable, audio test mode, overflow ack, channel swap, 60958 channel-status update, and AZ change ack.
- `AFMT*_AFMT_INFOFRAME_CONTROL0`, `AUDIO_SRC_CONTROL`, and `MEM_PWR`: audio info source/update, source selection, and formatter memory power gating fields.

The `AFMT*_AFMT_INTERRUPT_STATUS` comments have no field defines in this chunk, which likely means that either the register has no named fields in this generated revision or its fields are defined outside the selected line range.

### DME0-DME4 Metadata Engine Fields

Each DME block defines:

- `DME*_DME_CONTROL`: metadata HUBP requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable, transmission missed, and missed-clear fields.
- `DME*_DME_MEMORY_CONTROL`: DME memory power force, disable, state, and default low-power state.

These fields support per-pipe metadata transmission. The double-buffer and missed-transmission flags are stateful hardware handshake bits and are likely read or cleared by display metadata programming paths.

### VPG0-VPG4 Video Packet Generator Fields

Each VPG block defines:

- `VPG*_VPG_GENERIC_PACKET_ACCESS_CTRL` and `GENERIC_PACKET_DATA`: indexed access to generic packet bytes, four bytes per data register access.
- `VPG*_VPG_GSP_FRAME_UPDATE_CTRL`: frame-update request and pending fields for generic packet slots 0 through 14.
- `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL`: immediate-update request and pending fields for generic packet slots 0 through 14.
- `VPG*_VPG_GENERIC_STATUS`: lock status, conflict occurrence, and conflict clear.
- `VPG*_VPG_MEM_PWR`: generic-stream-packet memory light-sleep disable, light-sleep force, and power-state reporting.
- `VPG*_VPG_ISRC1_2_ACCESS_CTRL` and `ISRC1_2_DATA`: indexed ISRC packet byte access.
- `VPG*_VPG_MPEG_INFO0` and `MPEG_INFO1`: MPEG infoframe checksum, payload bytes, frame flags, and update trigger.

The VPG fields are the packet RAM and packet-update counterpart to the HDMI generic packet controls in the DIG block. Driver sequencing must coordinate packet data writes, frame/immediate update triggers, and pending/status polling.

### DP_AUX0 Fields

The DP AUX block contains:

- `DP_AUX0_AUX_CONTROL`: AUX enable/reset/reset-done, light-sleep read/update disable, HPD-disconnect ignore, mode-detect enable, HPD select, impedance calibration request enable, test mode, deglitch enable, and spare bits.
- `DP_AUX0_AUX_SW_CONTROL`: software transaction go, light-sleep read trigger, start delay, and write-byte count.
- `DP_AUX0_AUX_ARB_CONTROL`: AUX register arbitration priority, register read/write control status, no-queued SW/LS go controls, and ownership request/done bits for software and DMCU. Some request and pending request names intentionally alias the same bit/mask.
- `DP_AUX0_AUX_INTERRUPT_CONTROL`: interrupt, ack, and mask fields for software-done, light-sleep-done, GTC sync lock done, and GTC sync error.
- `DP_AUX0_AUX_SW_STATUS` and `AUX_LS_STATUS`: done/request flags, receive timeout state, timeout, overflow, HPD disconnect, partial byte, non-AUX mode, min-count violation, invalid stop/start/sync, receive detect errors, reply byte count, AUX arbitration status, CP IRQ, light-sleep update, and update ack.
- `DP_AUX0_AUX_SW_DATA` and `AUX_LS_DATA`: indexed byte access to AUX software and light-sleep data buffers, including software read/write and autoincrement-disable fields.
- `DP_AUX0_AUX_DPHY_*`: TX reference/rate/divider, TX precharge and output-enable timing, RX window/filter/threshold/timeout controls, and TX/RX status including state and half-symbol period measurements.
- `DP_AUX0_AUX_GTC_SYNC_*`: GTC sync enable, impedance calibration, lock acquisition/maintenance timing, block request, interval reset window, retry counts, potential/definite error thresholds, lock acquisition timeout, retry for lock maintenance, and controller status fields through lock acquisition timeout state at the end of the chunk.

This is a high-risk control surface because AUX is used for DisplayPort DPCD/I2C-over-AUX communication and link management. Bitfield drift here can break monitor detection, link training, HDCP/CP IRQ handling, or AUX timeout/error recovery.

## APIs, Types, and Functions

There are no declared APIs, types, or functions. The exported interface is the macro namespace itself. Each register field normally appears as:

- `<REGISTER>__<FIELD>__SHIFT`: the right shift to normalize the bitfield value.
- `<REGISTER>__<FIELD>_MASK`: the raw register mask used to preserve or update the field.

Consumers are expected to use the macros with DC register helpers such as generated register lists, `REG_SET`, `REG_UPDATE`, `REG_GET`, or equivalent AMDGPU/DC bitfield utilities defined elsewhere. This chunk does not include the register offsets; it only supplies masks/shifts for already named register symbols.

## Control Flow and State Behavior

The header itself has no runtime control flow. The implied control flow comes from hardware handshakes:

- Generic HDMI/VPG packet update paths write packet payload/index data, trigger frame or immediate update bits, then observe corresponding pending/status bits.
- HDMI/metadata double-buffer paths use pending/taken/clear/disable fields to synchronize register updates with frame/vupdate boundaries.
- AFMT audio programming writes infoframe/channel-status/sample-send fields, may trigger 60958 updates, and must acknowledge FIFO overflow or AZ audio-enable changes via ack bits.
- DME metadata transmission uses engine enable, stream type, double-buffer state, and missed-transmission clear fields.
- DP AUX software transactions acquire AUX register ownership as needed, write buffer/index/byte count fields, set go, poll or handle done/error status, then acknowledge interrupts and release ownership.
- AUX GTC sync programming configures acquisition and maintenance windows, then reads controller status for lock complete, lock lost, or timeout.

State is entirely hardware-resident. The macros identify persistent and transient register fields, including power-state fields (`*_MEM_PWR_STATE`, `AUX_RESET_DONE`), pending/taken handshakes, interrupt ack/mask fields, and error clear/ack bits. Incorrect masks can cause stale pending bits, missed clear writes, or unintended modification of adjacent hardware state.

## Dependencies and Integration Points

This generated header depends on the DCN 3.1.2 ASIC register database and on the surrounding AMDGPU display driver conventions for bitfield naming. Integration points include:

- DCN register definition headers that provide register offsets for the same symbols.
- Display Core link encoder and stream encoder code that configures DIG/HDMI/TMDS fields.
- Audio formatter code that writes AFMT infoframe, channel-status, HBR, sample-send, source-select, and CRC/test fields.
- VPG packet-generation code for generic packets, ISRC packets, and MPEG infoframes.
- Metadata engine code that enables DME and coordinates HUBP requestor IDs and double-buffered metadata updates.
- DP AUX/I2C-over-AUX code, link training, HPD handling, CP IRQ handling, and DMCU/software AUX arbitration paths.
- Power-management code that observes or programs AFMT, DME, VPG, and AUX memory/light-sleep controls.

Because the file is an include under `drivers/gpu/drm/amd/include/asic_reg/dcn`, it is generally not edited by hand. Manual changes risk divergence from other generated register headers such as offset, default, or SOC-specific variants.

## Risks and Edge Cases

- This chunk starts in the middle of `DIG4_HDMI_GENERIC_PACKET_CONTROL5`; earlier shift definitions and packet 0-8 fields are outside this range. Merge reconciliation should combine adjacent chunks before making whole-file conclusions.
- Repeated AFMT/DME/VPG blocks must remain instance-consistent. A copy-generation error in one instance can silently affect only one display pipe.
- Several control surfaces use write-one-to-clear or ack-style semantics (`*_TAKEN_CLR`, `*_MISSED_CLR`, `*_ACK`, conflict clear). Incorrect masks can clear the wrong status or fail to clear an interrupt.
- Double-buffer and pending bits are timing-sensitive. Misprogramming HDMI generic packet, VPG frame/immediate update, DME metadata, or AFMT sample-send update fields can produce stale packets, dropped metadata, or visible/audio glitches.
- DP AUX arbitration fields include aliases where request and pending request share a shift/mask. Consumers must understand whether they are writing a request or reading pending state even though the bit position is identical.
- DP AUX DPHY timing fields are protocol-sensitive. Wrong masks or shifts can manifest as intermittent AUX timeouts, invalid starts/stops, partial bytes, or failed monitor detection rather than compile failures.
- Power-state fields are often read-only or hardware-controlled; treating them as writable in consumers would be a driver bug even though this header only exposes masks.
- The `SPARE_0` and `SPARE_1` fields in `DP_AUX0_AUX_CONTROL` should not be repurposed without hardware documentation.

## Test and Validation Signals

Useful validation for this chunk is mostly integration and hardware-oriented:

- Build coverage: compile AMDGPU/DC code with DCN 3.1.2 enabled to ensure all macro names match consumer references.
- Header consistency: compare generated mask/shift pairs against the authoritative DCN 3.1.2 register database and related offset/default headers.
- HDMI validation: exercise DIG4 HDMI output with audio, generic infoframes, AVMUTE, TMDS control symbols, and mode changes while checking for packet/update pending completion.
- Audio validation: test AFMT instances 0-4 for LPCM channel layouts, HBR modes, 60958 channel-status updates, FIFO overflow handling, audio CRC/test ramp, and hotplug audio-enable changes.
- Metadata/VPG validation: verify metadata and generic packet delivery across display pipes 0-4, including frame-update and immediate-update paths and conflict status handling.
- DP AUX validation: run monitor detection, DPCD reads/writes, I2C-over-AUX EDID reads, HPD disconnect handling, CP IRQ handling, software/DMCU arbitration, timeout/error paths, and GTC sync lock/loss behavior on AUX0.
- Power validation: suspend/resume, display idle, and hotplug scenarios should not leave AFMT/DME/VPG/AUX memory-power state or light-sleep fields in bad states.

## Open Questions for Merge Lane

- The chunk ends inside `DP_AUX0_AUX_GTC_SYNC_CONTROLLER_STATUS`; subsequent status masks and any following AUX blocks must be checked in the next chunk.
- Whole-file synthesis should verify how many DIG/AFMT/DME/VPG/AUX instances DCN 3.1.2 exposes and whether instances beyond 4 or AUX channels beyond 0 are defined in adjacent chunks.
- The merge lane should cross-check whether `AFMT*_AFMT_INTERRUPT_STATUS` intentionally has no bitfield definitions or whether the fields reside outside this chunk.
