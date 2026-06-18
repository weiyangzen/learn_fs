# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 28769-30986

## Purpose

This chunk is a generated DCN 3.5.1 shift/mask header section for AMD display engine registers. It defines C preprocessor constants that describe bit positions and masks for the second display I/O slice and adjacent packet/audio/metadata blocks: the tail of `DIG1`, the full `DP1` secondary-data and link block, `VPG2`, `AFMT2`, `DME2`, `DIG2`, and the beginning of `DP2`. It is not executable code; its job is to give AMDGPU display code stable field descriptors for read/modify/write operations against ASIC-specific MMIO registers.

The range contains 2,218 `#define` lines and no non-define statements. It starts mid-register at `DIG1_HDMI_GENERIC_PACKET_CONTROL10__HDMI_GENERIC2_EN_DB_PENDING__SHIFT` and ends mid-register at `DP2_DP_MSA_TIMING_PARAM3__DP_MSA_HSYNCWIDTH_MASK`, so some companion shift or mask fields for those boundary registers live in neighboring chunks.

## Important macros and field groups

- `DIG1_HDMI_*`, `DIG1_AFMT_CNTL`, `DIG1_DIG_BE_CNTL`, and `DIG1_TMDS_*` complete the first digital backend's HDMI, audio formatter, backend routing, and TMDS fields. Important controls include HDMI generic packet double-buffer pending bits, HDMI DB lock/disable/taken bits, ACR CTS/N fields for 32/44/48 kHz families, AFMT audio clock enable/status, backend source/HPD selection, and TMDS control-character, feedback, DC-balancer, sync, and generated control pattern fields.
- `DP1_DP_*` describes the first DisplayPort encoder slice. The fields cover link control, pixel format, MSA colorimetry/misc/timing, video stream enable/timing, DPHY training/scrambling/CRC/fast training, secondary-data packet controls, DP audio `N`/`M` values and readbacks, MSE rate and slot allocation tables, MSO stream enables, DSC mode, generic secondary packets `GSP0` through `GSP11`, DP double-buffer control, VBID overrides, metadata packet transmission, ALPM low-power signaling, and AUX-less ALPM timing/status fields.
- `VPG2_VPG_*` provides generic packet RAM access and status fields for the second video packet generator instance. It includes packet access control, packet payload data, frame-update and immediate-update controls for generic secondary packets, ISRC packet data, MPEG infoframe payload fields, status bits, and VPG memory power controls.
- `AFMT2_AFMT_*` describes the second audio formatter instance. It includes VBI/audio packet controls, audio infoframe fields, IEC 60958 channel status words, audio CRC controls/results, ramp generator controls, audio status, source selection, infoframe update controls, audio sample send/FIFO/channel-swap bits, and AFMT memory power fields.
- `DME2_DME_CONTROL` and `DME2_DME_MEMORY_CONTROL` define metadata engine 2 programming fields: HUBP requestor ID, engine enable, stream type, metadata double-buffer pending/taken/disable/clear bits, transmission-missed status/clear bits, and DME memory power controls.
- `DIG2_DIG_*`, `DIG2_HDMI_*`, `DIG2_AFMT_CNTL`, and `DIG2_TMDS_*` repeat the digital frontend/backend, HDMI, AFMT clock, and TMDS controls for the second digital encoder slice. This includes output CRC/test pattern/FIFO controls, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet control fields, HDMI GC and DB control, and TMDS generator fields.
- The `DP2_DP_*` portion begins the second DisplayPort encoder slice and runs through MSA timing parameter 3. It mirrors the early `DP1` groups for link/video/DPHY/secondary-data/audio/MSE status and MSA timing, but this chunk stops before `DP2_DP_MSA_TIMING_PARAM3__DP_MSA_HSYNCPOLARITY_MASK` and later DP2 groups.

There are no C functions, structs, or exported APIs here. The public surface is the generated macro naming contract: `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, paired with `regREGISTER` and `regREGISTER_BASE_IDX` macros in `dcn_3_5_1_offset.h`.

## Control flow and usage model

The header has no runtime control flow. Runtime flow is in AMDGPU/DC code that includes this file with `dcn_3_5_1_offset.h`, selects the register address, applies the generated field mask/shift, and issues an MMIO read/modify/write through DC register helper macros.

A typical consumer path is:

1. DCN 3.5.1 resource, IRQ, or DMUB code includes the offset and shift/mask headers.
2. Resource-construction macros collect related field lists for blocks such as VPG and AFMT.
3. Encoder, packet, audio, metadata, or power-management code chooses a `reg...` address, for example `regDIG2_HDMI_CONTROL`, `regDP1_DP_SEC_CNTL2`, `regAFMT2_AFMT_AUDIO_PACKET_CONTROL`, `regDME2_DME_CONTROL`, or `regDP2_DP_MSA_TIMING_PARAM3`.
4. The caller encodes or extracts a field using the matching `_MASK` and `__SHIFT` value and writes the updated 32-bit register value.
5. Hardware double-buffer and status fields such as `*_DB_PENDING`, `*_DB_TAKEN`, `*_SEND_PENDING`, `*_SEND_ACTIVE`, and `*_DEADLINE_MISSED` report whether the hardware accepted or missed the programmed update.

The companion offset header maps the covered groups into base index 2 register addresses, including `regDIG1_HDMI_DB_CONTROL` at `0x21d5`, `regDP1_DP_SEC_CNTL2` at `0x228d`, `regAFMT2_AFMT_AUDIO_PACKET_CONTROL` at `0x22ca`, `regDME2_DME_CONTROL` at `0x22d9`, `regDIG2_HDMI_CONTROL` at `0x22e6`, and `regDP2_DP_MSA_TIMING_PARAM3` at `0x23ac`.

## State and persistence behavior

The macros are compile-time constants and hold no software state. The state they describe lives in GPU display hardware registers and can persist until changed by modeset programming, audio/packet reconfiguration, link retraining, display power transitions, suspend/resume restore paths, or GPU/display IP reset.

Several fields describe hardware-latched or double-buffered state. HDMI and DP DB controls track pending/taken/lock/disable states for synchronized updates. DP secondary-data and HDMI generic packet fields hold packet send/continuous/immediate-send state and expose pending, active, deadline-missed, and line-number status. AFMT and DP audio `N`/`M` fields affect audio clock recovery and packet generation, while MSE/SAT fields hold Multi-Stream Transport slot allocation state. Memory-power fields in VPG, AFMT, and DME affect block-local low-power state and must match the block's active use.

## Dependencies and integration points

- Depends on `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h` for register addresses and base-index information.
- Included directly by `display/dc/resource/dcn351/dcn351_resource.c`, `display/dc/irq/dcn351/irq_service_dcn351.c`, and `display/dmub/src/dmub_dcn351.c`.
- Integrates with DC register helper/list macros that consume generated `*_MASK` and `*__SHIFT` symbols for block-specific register tables.
- Binds display encoder programming to HDMI, DisplayPort, TMDS, VPG, AFMT, DME, MST/MSO, DSC, ALPM, and metadata packet behavior in the AMDGPU DRM display stack.
- Shares repeated field layouts across instances: `DIG1`/`DIG2`, `DP1`/`DP2`, and second-instance `VPG2`/`AFMT2`/`DME2` all depend on consistent generated instance numbering.

## Risks and edge cases

- Boundary incompleteness: this chunk begins and ends in the middle of register definitions, so users must include the whole generated header rather than treating this range as an independent register catalog.
- Mask/offset mismatch: a field macro is only useful when paired with the correct `reg...` address and base index. Mixing `DP1` masks with `DP2` offsets, or `DIG1` masks with `DIG2` offsets, would silently program the wrong hardware instance.
- Reserved-bit corruption: callers should update fields with mask-preserving read/modify/write helpers. Full-register writes can disturb reserved or status/clear bits adjacent to the named fields.
- Write-one-to-clear and status fields: bits such as `*_TAKEN_CLR`, `*_ACK`, `*_MISSED_CLR`, FIFO overflow acknowledge, and collision acknowledge must not be handled like ordinary sticky configuration bits.
- Timing-sensitive packet updates: generic secondary packets, HDMI infoframes, DP metadata, and MSE/SAT updates have line references, immediate-send controls, pending bits, and deadline-missed status. Incorrect sequencing can show up only on particular sinks, MST topologies, refresh rates, or HDR/metadata modes.
- Audio regressions: AFMT and HDMI/DP ACR fields control sample transport, channel layout, IEC 60958 status, audio clock recovery, and FIFO behavior; wrong widths or stale double-buffer state can cause dropouts, bad channel maps, or sink enumeration issues.
- Power-management regressions: VPG/AFMT/DME memory-power and ALPM/AUX-less ALPM fields can reduce power, but bad enable/disable ordering can block packet/audio/metadata transmission or leave hardware in a higher-power state.

## Test signals

- Build coverage for DCN 3.5.1 with AMDGPU/DC enabled; missing or renamed generated macros should fail compilation in resource, IRQ, DMUB, encoder, packet, or audio code.
- Header consistency checks comparing repeated instance layouts: `DIG1` versus `DIG2`, early `DP1` versus `DP2`, and DCN 3.5.1 versus nearby generated DCN versions for expected field stability.
- Offset/mask reconciliation tests that verify covered `REGISTER__FIELD` macro groups have matching `regREGISTER` and `regREGISTER_BASE_IDX` entries in `dcn_3_5_1_offset.h`.
- Runtime modeset and link-training tests on DCN 3.5.1 hardware covering HDMI, DP SST, DP MST/MSO, DSC, HDR/metadata packets, and ALPM transitions.
- Audio tests for HDMI and DP endpoints, including 32/44.1/48 kHz families, channel layout changes, IEC 60958 updates, FIFO overflow handling, suspend/resume, and hotplug.
- Packet-status diagnostics: confirm `*_SEND_PENDING`, `*_SEND_ACTIVE`, `*_DEADLINE_MISSED`, DB pending/taken, metadata missed, and collision status bits behave as expected under frame-update, immediate-update, and line-referenced packet sends.
