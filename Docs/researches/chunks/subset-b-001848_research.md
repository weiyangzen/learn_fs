# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 36981-39374

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes C preprocessor constants for field shifts and bit masks used by AMDGPU display code to address MMIO register fields on DCN 3.1.4 hardware.

The requested range covers 2,394 source lines and 2,171 `#define` entries: 1,096 `__SHIFT` constants and 1,075 `_MASK` constants. The apparent mismatch is caused by the artificial chunk boundary: the range ends inside `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` after 21 shift definitions, while that register's remaining masks continue after line 39374. Aside from that expected boundary effect, the complete registers in this slice have paired shift and mask definitions.

Although the path sits under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or exported runtime symbols in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same hardware field.

These constants are meaningful only with the matching offset header, especially `dcn_3_1_4_offset.h`, and with AMD display register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major register families in this chunk:

- `DP_AUX3_*` tail fields: AUX3 DPHY TX/RX timing, AUX GTC synchronization, GTC error/status reporting, and AUX PHY wake controls.
- Complete `DP_AUX4_*` block: AUX4 enable/reset, HPD selection, low-speed read, software AUX transaction control, arbitration between software and DMCU-style users, AUX done/error interrupts, software and low-speed transaction status/data windows, DPHY TX/RX tuning/status, GTC sync control/status, and AUX PHY wake handshaking.
- `VPG0_*`: video packet generator generic packet indexed data, generic secondary packet frame/immediate update controls, conflict/status bits, memory power controls, ISRC data, and MPEG packet info.
- `AFMT0_*`: audio formatter and HDMI/DP audio packet fields, including VBI audio packet placement, audio layout/channel enable, DP audio stream ID, HBR and 60958 overrides, audio infoframe payload fields, IEC 60958 channel-status bytes, audio CRC generation/results, test ramp controls, FIFO overflow/audio-enable status, audio packet send/update controls, audio source selection, and AFMT memory power controls.
- `DME0_*`: display metadata engine enablement, HUBP requestor ID, stream type, double-buffer pending/taken state, missed-transmission status/clear bits, and memory low-power controls.
- `DIG0_*`: digital front-end/back-end source selection, stereo and bypass routing, Dolby Vision enable/missed metadata status, output CRC, clock/test/random patterns, FIFO reset/calibration/error state, HDMI metadata packets, HDMI core control/status, ACR packets and CTS/N values, generic packet controls, HDMI double-buffering, TMDS control pattern generation, data balancing, sync characters, and DIG version/force-disable bits.
- `DP0_*`: DisplayPort link, pixel format, main-stream attributes, video stream enable/status, steering FIFO/TU overflow, DPHY training/symbol/scrambler/CRC/PRBS/FEC controls, fast training, secondary-data packet controls, audio timestamp/N/M fields, multi-stream transport MSE slot/rate controls, MSO controls, DSC control, secondary metadata transmission, ALPM controls, generic secondary packet 8-11 controls, generic packet enable double-buffer status, and AUX-less ALPM wake/sleep interrupt controls.
- Beginning of `VPG1_*`: generic packet access/data plus the start of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, ending before the register's mask definitions complete.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and DMUB code:

1. DCN 3.1.4-specific code includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`.
2. Register table or direct register-access macros paste register and field names into tokens such as `DP_AUX4_AUX_CONTROL__AUX_EN_MASK` or `DIG0_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN__SHIFT`.
3. Helper macros such as `FD_MASK` and `FD_SHIFT` populate field tables or construct read-modify-write operations.
4. Higher-level display code performs the actual ordering: AUX transactions for DPCD/I2C-over-AUX, HDMI/DP audio setup, generic packet scheduling, metadata double-buffer updates, DisplayPort link training and stream enablement, MST/MSO/DSC programming, ALPM transitions, interrupt acknowledgements, and suspend/resume restoration.

The generated masks do not encode ordering or access permissions. For example, the same chunk describes one-shot control bits, sticky status bits, clear/ack bits, read-only status, programmable timing fields, and double-buffer handshakes. Consumers must know the required sequence from hardware documentation and driver logic.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in memory or on disk. It describes fields in hardware registers whose values are owned by the display engine.

Hardware state represented by these fields includes:

- AUX channel state: enable/reset state, HPD association, software transaction queues, low-speed read windows, DPHY timing, GTC sync lock/error state, transaction reply/error status, CP IRQ/update flags, and PHY wake request/ack state.
- Packet-generation state: generic packet payload bytes, frame/immediate update requests and pending flags, ISRC/MPEG info payloads, packet lock/conflict status, and VPG memory power state.
- Audio formatter state: audio channel layout, enabled channels, DP stream ID, HBR and IEC 60958 controls, audio infoframe payloads, channel-status overrides, CRC/test generation, FIFO overflow, audio enable-change status, source selection, and AFMT memory power state.
- Metadata state: DME enablement, requestor routing, double-buffer pending/taken state, missed metadata transmission status, and DME memory power state.
- HDMI/TMDS state: scrambling, deep color, AVMUTE status, ACR generation, generic packet send/line/update controls, HDMI double-buffer locks, CTS/N values, audio/video metadata packet state, TMDS sync/control patterns, DC-balance controls, and DIG enable/clock status.
- DisplayPort state: link status, lane count, pixel encoding/depth, MSA fields, stream enable/status, steering FIFO and TU overflow, DPHY training/test/scrambler/CRC/FEC controls, secondary-data packet timing, MST allocation, MSO, DSC, secondary metadata, ALPM/AUX-less ALPM, generic secondary packet scheduling, and wake/sleep interrupt state.

Persistence is hardware-defined. Configuration fields generally retain values until modeset, link reprogramming, power gating, suspend/resume, or ASIC reset. Status, pending, interrupt, ack, clear, force, and done bits may be volatile, sticky, self-clearing, or write-one-to-clear depending on the register. This mask header does not say which fields have side effects.

## Dependencies And Integration Points

The masks in this chunk must match the generated DCN 3.1.4 offset database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h`

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which includes the offset and mask headers and expands DCN register/field tables through `DMUB_DCN31_REGS()`, `DMUB_DCN31_FIELDS()`, `FD_MASK`, and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`, which includes the same generated headers and uses token-pasted register/mask names for interrupt register descriptors.

Broader integration is with AMDGPU display code that programs the DIG, DP, HDMI, AFMT, VPG, DME, and AUX blocks. The generated constants are coupled to same-generation register lists and to repeated-instance naming conventions (`DIG0`, `DP0`, `VPG0`, `VPG1`, `DP_AUX4`, etc.). A field-name drift or wrong bit position can compile successfully if a token still exists, but it can cause hardware misprogramming at runtime.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These are untyped integer constants, so an incorrect mask can silently corrupt neighboring hardware fields.
- The chunk boundary is partial at both the file-context level and the ending register level. It starts in the tail of the `DP_AUX3` address block and ends inside `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`; final file-level analysis must merge adjacent chunks before making complete block-level claims.
- AUX register fields include arbitration, queued transaction, timeout, overflow, HPD disconnect, low-speed update, CP IRQ, GTC sync, and PHY wake bits. Blind read-modify-write or wrong ack handling can hang AUX transactions, lose HPD/CPIRQ signals, or break DPCD/I2C-over-AUX communication.
- HDMI/AFMT fields include audio packet send controls, ACR generation, HBR/layout overrides, FIFO overflow acknowledgements, channel-status updates, and infoframe payload fields. Mistakes can produce missing HDMI/DP audio, wrong channel maps, audio dropouts, bad CTS/N timing, or stuck audio interrupts.
- Generic packet and metadata fields rely on frame/immediate update and double-buffer pending/taken handshakes. Misprogramming can miss HDR/Dolby Vision/AVI/audio/vendor packets or update them on the wrong frame.
- DP0 fields cover link training, FEC, scrambler, MSA, stream enable, MST allocation, DSC, MSO, secondary packets, and ALPM. Errors can be mode-specific and appear only with MST, DSC, FEC, high bit rates, panel replay/low-power modes, or AUX-less ALPM.
- Several fields are replicated patterns, such as generic packet 0-14 updates and DP GSP 8-11 controls. Copy-generation errors may affect one packet slot while the rest work, making failures hard to localize.
- Memory power fields for VPG, AFMT, and DME must be coordinated with active use. Forcing low-power state at the wrong time can cause dropped packets or stale status.

## Test Signals

Useful validation combines generated-header consistency with hardware behavior:

- Build DCN 3.1.4 AMDGPU display and DMUB code. Missing or renamed macros should fail at `dmub_dcn314.c`, IRQ descriptor construction, register tables, or direct register-access compile sites.
- Mechanically verify that complete registers in lines 36981-39374 have matching `__SHIFT` and `_MASK` definitions. The known exception is `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, whose mask definitions continue after this chunk.
- Diff this slice against AMD's authoritative DCN 3.1.4 register database and neighboring DCN mask headers where repeated blocks are expected to remain layout-compatible.
- Exercise DisplayPort AUX reads/writes, I2C-over-AUX EDID reads, DPCD link-status reads, HPD/HPD-RX handling, CP IRQ handling, and suspend/resume on hardware using DCN 3.1.4 paths.
- Validate HDMI and DisplayPort audio across hotplug, modeset, sample-rate changes, HBR, stereo, multichannel, and receiver capability changes; watch for audio FIFO overflow, bad channel status, and missing audio devices.
- Validate generic packets and metadata: AVI/audio/vendor infoframes, HDR/Dolby Vision metadata, ISRC/MPEG packets, frame-update versus immediate-update behavior, and double-buffer pending/taken transitions.
- Exercise DP link modes that stress this slice: link training, FEC on/off, DSC, MST allocation, MSO/eDP panel modes, stream enable/disable interrupts, fast training, CRC/PRBS diagnostics, and ALPM/AUX-less ALPM wake/sleep paths.
- Monitor kernel logs, display artifacts, audio diagnostics, and connector-specific failures for stuck interrupts, AUX timeouts, packet deadline misses, metadata transmission missed flags, steering/TU overflows, link-training failures, or behavior limited to one DIG/DP/AUX instance.

## Cross-Chunk Notes

Earlier chunks own the beginning of the `DP_AUX3` block, including its control/software/arbitration/status/data registers before `DP_AUX3_AUX_DPHY_TX_REF_CONTROL`. Later chunks continue `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` with the remaining mask definitions and then the rest of the DIG1 VPG block. The final per-file document should reconcile those boundaries before summarizing complete address blocks for `dcn_3_1_4_sh_mask.h`.
