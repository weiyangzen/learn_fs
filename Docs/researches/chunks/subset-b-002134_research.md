# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 39779-42166

## Scope

This chunk is a middle slice of AMDGPU's generated DCN 3.6.0 register shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. Its interface is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace, where each macro describes one bitfield position and already-shifted mask for DCN 3.6.0 display hardware registers.

The range starts in the tail of the `AFMT1_AFMT_AUDIO_CRC_CONTROL` block, covers the remainder of AFMT1, then full AFMT2, AFMT3, and AFMT4 audio formatter field groups. It then covers DME and VPG metadata/generic-packet field groups for DIG0 through DIG4. The final portion covers full DP AUX0 and DP AUX1 field groups and ends after the first few DP AUX2 arbitration fields. Adjacent chunks own the beginning of AFMT1 and the remainder of DP AUX2 and later blocks.

Although this file lives under `sources/distributed-fs/ceph-client`, this source is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network-protocol, or persistent-disk behavior.

## Purpose

The purpose of this header range is to give DCN 3.6 display code exact bit geometry for audio packet generation, metadata packet generation, generic secondary-data packets, and DisplayPort AUX engines. Runtime code pairs these masks and shifts with `dcn_3_6_0_offset.h` offsets to build register tables and perform MMIO read/modify/write operations through AMD display helper macros.

The covered hardware areas are:

- `AFMT1` tail plus `AFMT2` through `AFMT4`: HDMI/DP audio formatter fields for ACP packet type bytes, VBI audio packet controls, audio layout/channel enable/DP stream ID, HDMI audio infoframe payload, IEC 60958 channel-status words, audio CRC generation/result, audio test ramp generation, audio status bits, packet-send/update/ack controls, audio source selection, and AFMT memory power.
- `DME0` through `DME4`: display metadata engine controls for metadata HUBP requester selection, metadata engine enable, stream type, double-buffer pending/taken state, DB clear/disable controls, missed-transmission status/clear, and DME memory power.
- `VPG0` through `VPG4`: video packet generator fields for indexed generic packet data, frame-synchronized and immediate generic packet update triggers/pending bits, generic-packet lock/conflict status, VPG GSP memory power, ISRC indexed packet data, and MPEG infoframe fields.
- `DP_AUX0` and `DP_AUX1`: DisplayPort AUX channel control, software transaction launch, arbitration, interrupt/status/ack/mask bits, software and link-service data windows, DPHY TX/RX timing and status, GTC sync control/error/status, and PHY wake handshakes.
- `DP_AUX2` beginning: AUX control, software transaction control, and the first arbitration fields before the chunk ends.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important API is the generated macro pattern:

- `*_SHIFT` gives the least-significant bit position for a field.
- `*_MASK` gives the field mask in final register position.
- The register prefix encodes the block and instance, for example `AFMT2_AFMT_AUDIO_PACKET_CONTROL2`, `DME3_DME_CONTROL`, `VPG4_VPG_GSP_FRAME_UPDATE_CTRL`, or `DP_AUX1_AUX_GTC_SYNC_STATUS`.

The AFMT groups are the audio packet programming surface for stream encoders. Key fields include `AFMT_AUDIO_CHANNEL_ENABLE`, `AFMT_AUDIO_LAYOUT_SELECT`, `AFMT_DP_AUDIO_STREAM_ID`, `AFMT_HBR_ENABLE_OVRD`, `AFMT_60958_OSF_OVRD`, `AFMT_AUDIO_INFO_*`, IEC 60958 channel-status masks across `AFMT_60958_0/1/2`, and send/update bits such as `AFMT_AUDIO_SAMPLE_SEND`, `AFMT_60958_CS_UPDATE`, and `AFMT_AUDIO_INFO_UPDATE`. AFMT status and ack fields expose audio enable, HBR enable, FIFO overflow, and audio-enable-change handling. `AFMT_MEM_PWR_*` fields describe formatter memory power force/disable/state controls.

The DME groups are compact but stateful. `DME*_DME_CONTROL` selects the `METADATA_HUBP_REQUESTOR_ID`, enables metadata transmission, selects metadata stream type, reports and clears double-buffer/taken state, can disable DB behavior, and reports/clears missed metadata transmission. `DME*_DME_MEMORY_CONTROL` provides memory power force, disable, state, and default low-power-state fields.

The VPG groups define generic and standardized packet payload access. `VPG*_VPG_GENERIC_PACKET_ACCESS_CTRL` selects an indexed data word and `VPG*_VPG_GENERIC_PACKET_DATA` packs four payload bytes. `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL` provide update and pending bits for generic packet slots 0 through 14. `VPG*_VPG_GENERIC_STATUS` provides lock and conflict detection/clear fields. `VPG*_VPG_ISRC1_2_*` and `VPG*_VPG_MPEG_INFO*` define ISRC and MPEG infoframe byte packing and update fields.

The DP AUX groups describe the low-level AUX engine. `DP_AUX*_AUX_CONTROL` carries enable/reset/reset-done, link-service read/update controls, HPD disconnect handling, mode detection, HPD selection, impedance calibration request enable, test mode, deglitch, and spare bits. `AUX_SW_CONTROL` launches software transactions and programs start delay and write-byte count. `AUX_ARB_CONTROL` coordinates ownership between software and DMCU/firmware users. `AUX_INTERRUPT_CONTROL` exposes software done, link-service done, GTC sync lock, and GTC sync error interrupt/status/ack/mask fields.

The AUX status and data fields are transaction-critical. `AUX_SW_STATUS`, `AUX_LS_STATUS`, `AUX_SW_DATA`, and `AUX_LS_DATA` describe done/request status, timeout state, HPD disconnect, partial-byte and invalid-start/stop/sync conditions, reply byte count, NACK state, and 8-bit data bytes. DPHY controls define TX half-symbol timing, precharge, timeout, input hysteresis, RX threshold/filter/phase-detect behavior, and TX/RX state readback. GTC sync fields define enable, impedance calibration, lock acquisition/maintenance periods, retry/error thresholds, controller state, error acks, detailed RX error status, reply byte count, and master-request state. `AUX_PHY_WAKE_CNTL` exposes wake go/pending/priority/ack handshaking.

## Control Flow

The header itself has no local control flow. Runtime behavior comes from consumers that include both `dcn_3_6_0_offset.h` and this shift/mask header, expand register-list macros, then use register helper operations such as `REG_READ`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and related wrappers to access MMIO fields.

A typical DCN 3.6 path is:

1. DCN36 resource, IRQ, DMUB, AFMT, VPG, AUX, and stream-encoder code includes or indirectly consumes the DCN 3.6 generated offset and mask headers.
2. Resource construction macros such as `SRI`, `SRI_ARR`, and `SRI_ARR_INIT` paste logical register names onto generated instance names like `regAFMT2_AFMT_AUDIO_PACKET_CONTROL2`, `regVPG3_VPG_MEM_PWR`, or `regDP_AUX1_AUX_CONTROL`.
3. Field-list macros paste logical fields onto generated `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` constants.
4. Higher-level display code sequences the actual programming: audio infoframe/channel-status updates in AFMT, metadata/generic packet writes in DME/VPG, AUX transactions for DPCD/I2C-over-AUX, hotplug/HPD handling, link training, and low-power transitions.

Visible integration in this tree includes `dcn36_resource.c`, which includes this header and uses DCN36 resource macros to build VPG, AFMT, and AUX register tables; `dmub_dcn36.c`, which initializes DMUB-visible register masks/shifts via `FD_MASK` and `FD_SHIFT`; and `irq_service_dcn36.c`, which includes the generated headers while building DCN36 interrupt metadata.

## State And Persistence Behavior

This file stores no runtime state and persists nothing by itself. It describes fields in hardware registers whose state is owned by live display hardware and driver programming.

State represented by this chunk includes:

- AFMT audio state: audio channel enable/layout, DP stream ID, HBR override, audio infoframe bytes, IEC 60958 channel-status fields, sample-send/update controls, CRC/test-ramp configuration, status/ack bits, and AFMT memory power.
- DME metadata state: metadata engine enable, selected HUBP requester, stream type, DB pending/taken/clear/disable state, missed-transmission status, and memory power.
- VPG packet state: indexed generic packet payload bytes, frame/immediate update pending state for generic packet slots, lock/conflict status, memory power, ISRC payload bytes, and MPEG infoframe payload/update bits.
- AUX state: AUX enable/reset, transaction launch and arbitration ownership, interrupt masks and acks, SW/LS status and data windows, DPHY timing/filtering/status, GTC sync lock/error state, and PHY wake state.

Some fields are status-only or status-like readbacks, including reset done, pending bits, memory-power state, audio FIFO overflow, audio enable changes, generic conflict status, AUX done/request/error/status fields, reply byte counts, TX/RX state, GTC controller state, and PHY wake pending/ack. Other fields are write controls that can change active hardware immediately or at a synchronized update point. Indexed data registers are especially stateful because a selected index controls which payload word a later write reads or updates.

Bad programmed values can persist until a pipe is reprogrammed, an encoder/AUX block is reset, display power is cycled, suspend/resume restores state, or the GPU is reset. The generated header has no restore, locking, or validation logic; those responsibilities live in display resource, stream encoder, AFMT/VPG, AUX, DMUB, and IRQ code.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, which provides matching register offsets and base indices. These masks and shifts are only correct when paired with the DCN 3.6.0 offset header and the DCN36 register-instance layout.

Important integration points include:

- `display/dc/resource/dcn36/dcn36_resource.c`: includes this header, defines base/offset/field expansion macros, builds VPG and AFMT register tables through `VPG_DCN31_REG_LIST_RI(id)` and `AFMT_DCN31_REG_LIST_RI(id)`, builds AUX register tables through `DCN2_AUX_REG_LIST_RI(id)`, initializes `AUX_RESET_MASK` from `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK`, and documents mapping of VPG/AFMT/DME register blocks to DIO instances.
- `display/dc/dcn31/dcn31_afmt.h` and AFMT implementation files: define the AFMT register and field lists consumed by DCN36 resource construction, including audio source, channel enable, 60958 channel status, sample send, and memory-power fields present in this chunk.
- `display/dc/dcn31/dcn31_vpg.h` and VPG implementation files: define VPG register/field lists for generic packet access, update controls, conflict handling, and VPG memory power that are backed by the VPG0-VPG4 masks in this chunk.
- `display/dc/dce/dce_aux.h` and AUX helpers: use the AUX register table and field masks for DP AUX and I2C-over-AUX transactions, timeouts, interrupt/status handling, and engine reset/wake behavior.
- `display/dmub/src/dmub_dcn36.c`: initializes DMUB register offsets, masks, and shifts using `FD_MASK` and `FD_SHIFT`, relying on this header for fields shared with firmware-facing services.
- `display/dc/irq/dcn36/irq_service_dcn36.c`: includes the same generated headers for DCN36 interrupt metadata and source mapping.

The namespace is generated and cross-generation-looking but not interchangeable. Nearby DCN 3.5.x and DCN 4.x headers may share many field names while differing in offset layout, block count, or exact bit geometry. Consumers must bind the right offset and shift/mask pair for the target ASIC.

## Risks And Edge Cases

The largest risk is silent hardware misprogramming. A wrong `*_SHIFT` or `*_MASK` still compiles, but it can update the wrong bits, leave stale bits behind, corrupt adjacent fields, or decode status incorrectly.

Chunk boundaries matter. The first lines are only the tail of `AFMT1_AFMT_AUDIO_CRC_CONTROL`, so this chunk alone cannot fully describe AFMT1. The final lines stop in `DP_AUX2_AUX_ARB_CONTROL`, so the remainder of DP AUX2 belongs to the following chunk. The merge lane must combine adjacent chunks before making whole-file or whole-block conclusions.

Instance mapping is critical. The same logical AFMT, DME, VPG, and AUX register layout repeats across instances. A mask from AFMT4 or DP_AUX1 is often bit-identical to AFMT2 or DP_AUX0, but it must still be paired with the correct generated offset and DIO/HPO mapping. Wrong instance selection can route audio, metadata, packet, or AUX operations to the wrong display link.

AFMT fields are visible to end users through audio behavior. Incorrect channel enable/layout, DP stream ID, HBR override, 60958 fields, infoframe update bits, or sample-send controls can cause missing audio, wrong channel mapping, bad sample-rate/word-length reporting, HDMI/DP sink compatibility problems, or stale audio infoframes.

DME/VPG fields affect secondary-data packet delivery. Incorrect indexed writes, update timing, conflict clear, pending-bit interpretation, ISRC/MPEG payload packing, or memory-power controls can cause missing or stale infoframes, HDR/metadata regressions in adjacent packet paths, packet conflicts, or display behavior that only fails on specific stream encoders.

AUX fields are high impact. Wrong control, arbitration, timeout, HPD-disconnect, interrupt, data, DPHY timing, or GTC sync masks can break EDID reads, DPCD access, link training, MST sideband messaging, LTTPR handling, PSR/replay interactions, firmware-mediated AUX access, or hotplug recovery. AUX errors may surface as timeouts or invalid replies rather than obvious bitfield bugs.

Power and reset fields are sensitive. AFMT/VPG/DME memory power, AUX reset, AUX PHY wake, and low-level DPHY controls interact with active display links. Bad sequencing can leave blocks inaccessible, force memories off while active, make reset-done polling fail, or create intermittent failures across suspend/resume and runtime power transitions.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for DCN36 resource construction, AFMT/VPG stream encoder objects, AUX/I2C helpers, DMUB register initialization, and IRQ service code that includes the DCN 3.6 offset and shift/mask headers.
- Generated-register consistency checks that every `*_MASK` has a matching `*_SHIFT`, field masks match the hardware register database, and every register referenced by DCN36 resource lists exists in `dcn_3_6_0_offset.h`.
- Cross-generation diffs against AMD's authoritative DCN 3.6.0 register database and nearby DCN 3.5.x / DCN 4.x headers, with expected differences explicitly reviewed.
- AFMT tests for HDMI/DP audio bring-up, channel layouts, HBR audio, IEC 60958 channel status, sample-rate/word-length reporting, audio infoframe updates, FIFO-overflow status/ack behavior, CRC/test paths, and suspend/resume restore.
- VPG/DME packet tests for generic packet payload writes, frame-synchronized and immediate updates, pending-bit clearing, conflict reporting/clear, ISRC and MPEG infoframe payloads, metadata DB pending/taken transitions, missed-transmission reporting, and memory-power transitions.
- AUX tests for EDID and DPCD reads/writes, I2C-over-AUX, link training, HPD disconnect during transactions, timeout paths, invalid reply/status decoding, interrupt/ack/mask behavior, firmware/DMUB-mediated AUX operations, MST sideband traffic, LTTPR accesses, and AUX wake behavior.
- Power-management tests for AFMT/VPG/DME memory power, AUX reset/reset-done polling, AUX PHY wake, runtime display idle, hotplug, suspend/resume, and GPU reset recovery.

Regression symptoms from bad constants include missing or misreported display audio, stale or absent infoframes/metadata packets, generic-packet conflicts, broken EDID/DPCD access, DP link-training failures, MST failures, HPD/AUX timeout storms, stuck reset or wake bits, incorrect interrupt acks, and failures isolated to DCN 3.6 ASICs or specific DIO instances.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dcn_3_6_0_sh_mask.h`. The preceding chunk owns earlier AFMT1 fields before line 39779. The following chunk owns the rest of DP AUX2 after line 42166. The merge/reconciliation lane should treat this document as the AFMT1-tail/AFMT2-4, DME0-4, VPG0-4, DP_AUX0-1, and DP_AUX2-beginning portion of the full DCN 3.6.0 shift/mask contract.
