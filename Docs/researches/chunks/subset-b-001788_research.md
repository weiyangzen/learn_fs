# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 17342-19736

## Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; it defines `#define` constants for field shifts and masks used by AMDGPU Display Core register helpers when packing and unpacking memory-mapped display-controller registers.

The selected range starts inside the `DP_AUX1_AUX_INTERRUPT_CONTROL` mask list, completes the remaining `DP_AUX1` software AUX/status/DPHY/GTC-sync/PHY-wake fields, then covers the display I/O stream-encoder-related blocks for DIG instance 0: `VPG0`, `AFMT0`, `DME0`, `DIG0`, and `DP0`. It then begins the mirrored DIG instance 1 blocks for `VPG1`, `AFMT1`, and the start of `DME1_DME_CONTROL`; line 19736 stops before the rest of `DME1` and `DIG1`.

Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or callbacks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field, usually with an `L` suffix.

Major macro families in this slice:

- `DP_AUX1_*`: software AUX transaction status and FIFO data access, link-service status/data, DPHY TX/RX timing and status, AUX interrupt bits, AUX GTC sync control/error/status/counter fields, and AUX PHY wake control.
- `VPG0_*` and `VPG1_*`: video packet generator access/data registers, generic stream packet frame-update and immediate-update controls for packet slots 0 through 11, generic packet status, memory power control, ISRC indexed data, and MPEG infoframe fields.
- `AFMT0_*` and `AFMT1_*`: audio formatter fields for HDMI audio packet limits, audio layout/channel/stream selection, audio infoframe bytes, IEC 60958 channel-status words, audio CRC control/result, audio ramp test controls, audio status, audio sample send/test/overflow acknowledgements, infoframe update control, audio source selection, and AFMT memory power state.
- `DME0_*` plus the beginning of `DME1_DME_CONTROL`: metadata engine requestor, enable, stream type, double-buffer pending/taken/clear/disable fields, and DME memory power control for instance 0.
- `DIG0_*`: front-end source and pixel selection, Dolby Vision flags, symbol clock status, HDMI/TMDS pixel encoding/color format, output CRC, test/random/clock patterns, FIFO underflow/overflow/depth status, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet controls, HDMI guard-band/control-period/deep-color/status fields, TMDS control, TMDS data-balance and control-symbol generation, DIG version, lane enablement, and forced disable.
- `DP0_*`: DisplayPort link control, pixel format, MSA colorimetry/config/timing/misc/VBID fields, stream control, FIFO steering, VID M/N, link framing, DPHY control/training/symbol/8b10b/PRBS/scrambler/CRC/fast-training fields, secondary-data packet controls, DP audio M/N/timestamp fields, MST/MSE stream allocation table fields, MSO controls, DSC controls, double-buffer controls, ALPM, and generic stream packet slots 8 through 11.

The macros are normally consumed indirectly through token-pasting helpers such as `SF`, `SRI`, `SE_SF`, `HWS_SF`, and block lists like `DCN_AUX_MASK_SH_LIST`, `VPG_DCN3_REG_LIST`, `AFMT_DCN3_REG_LIST`, and `SE_DCN3_REG_LIST`.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMD Display Core:

1. `dcn303_resource.c` includes `dcn/dcn_3_0_3_offset.h` and this matching `dcn/dcn_3_0_3_sh_mask.h`.
2. Resource macros paste register and field tokens into generated constants, then initialize per-block register, shift, and mask tables.
3. DCN 3.0.3 constructors allocate display objects and pass those tables into component constructors such as `dcn30_dio_stream_encoder_construct()`, `vpg3_construct()`, `afmt3_construct()`, `dce110_aux_engine_construct()`, and `dcn10_dio_construct()`.
4. Modeset, hotplug, AUX/I2C, audio, HDMI, DP, MST, DSC, and infoframe paths use `REG_GET`, `REG_SET`, `REG_UPDATE`, and related helpers to access the hardware fields described here.

The macros do not encode sequencing. Callers must still order link training, stream setup, AUX transactions, infoframe updates, audio source selection, interrupt acknowledgement, double-buffer commits, memory power transitions, and suspend/resume restore correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes bit layouts for state held in GPU display hardware registers.

Important hardware state represented by the fields includes:

- AUX transaction state: software request completion, reply byte count, timeout/overflow/invalid-start/stop/sync errors, HPD disconnect indications, arbitration status, data byte/index access, and interrupt/ack/mask bits.
- AUX PHY/GTC state: TX/RX timing windows, symbol-period status, sync enable, lock acquisition/maintenance periods, error masks, offset/min/max counters, controller lock/error status, and PHY wake enable/delay parameters.
- VPG packet state: packet slot update modes, line numbers, send timing, generic packet readiness/collision status, and payload/index windows for generic, ISRC, and MPEG packets.
- AFMT/audio state: HDMI/DP audio stream ID, channel enable mask, layout override, audio infoframe bytes, IEC 60958 channel-status fields, CRC counters/results, test-ramp configuration, overflow and audio-enable status, and audio-source selection.
- DIG/HDMI/TMDS state: source selection, encoder start/bypass, test patterns, FIFO status, HDMI packet scheduling, ACR N/CTS programming and status, generic packet enable/update timing, guard-band and control-period settings, TMDS control-symbol generation, lane enablement, and forced disable.
- DP stream/link state: link rate/lane-count/enhanced framing, pixel encoding, MSA timing, training pattern and DPHY controls, scrambling/PRBS/CRC diagnostics, secondary packet and audio timing, MST allocation, MSO and DSC enablement, double-buffering, ALPM, and high-numbered generic stream packet controls.
- Metadata/DME state: metadata requestor selection, engine enable, stream type, double-buffer pending/taken state, disable flags, and memory power state.

Persistence is hardware-defined. Configuration bits generally remain until overwritten, reset, power-gated, or restored by driver resume paths. Status, interrupt, CRC, collision, timeout, double-buffer, and acknowledgement fields may be sticky, write-one-to-clear, read-only, self-clearing, or latch-on-read depending on the register. This generated mask file does not identify access type or side effects.

## Dependencies And Integration Points

The chunk depends on AMD's generated DCN 3.0.3 register database and must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which provides matching register addresses and base-index constants.

The direct consumer in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`. That file includes this header and uses token-pasted shift/mask constants to build:

- `vpg_regs`, `vpg_shift`, and `vpg_mask` for `VPG0` and `VPG1` stream packet generators.
- `afmt_regs`, `afmt_shift`, and `afmt_mask` for `AFMT0` and `AFMT1` audio formatter blocks.
- `stream_enc_regs`, `se_shift`, and `se_mask` for `DIG0` and `DIG1` stream encoder register programming; this chunk contains the complete `DIG0` side and starts the instance-1 adjacent blocks.
- `aux_engine_regs`, `aux_shift`, and `aux_mask` for `DP_AUX0/1` AUX engines; this chunk contributes the `DP_AUX1` field definitions.
- `dio_regs`, `dio_shift`, and `dio_mask` for the DIO wrapper power-control integration, though this specific chunk is mostly stream/AUX rather than the DIO global power register.

Higher-level integration is through Display Core link encoder, stream encoder, VPG, AFMT, DME, AUX, and audio objects. These objects expose behavioral operations such as AUX transfers, DP/HDMI stream enablement, infoframe programming, MST allocation, DSC setup, and audio packet control while relying on this header only for bit positions.

## Risks And Edge Cases

- Mask/shift drift is the main risk. A wrong generated value still compiles but can silently program the wrong hardware bit.
- The range is artificially chunked. It starts after the beginning of `DP_AUX1_AUX_INTERRUPT_CONTROL` and ends in the middle of `DME1_DME_CONTROL`, so adjacent chunks are required for complete file-level reasoning.
- Instance symmetry is copy-sensitive. `VPG0/AFMT0/DME0/DIG0/DP0` and `VPG1/AFMT1/DME1/DIG1` have similar names but distinct register instances; a prefix mismatch can route packets, audio, AUX, or metadata to the wrong engine.
- AUX status and interrupt fields are side-effect-sensitive. Mishandling done/ack/mask, timeout, HPD-disconnect, or arbitration fields can hang DPCD/EDID reads, break hotplug handling, or hide link-service updates.
- Packet update fields are timing-sensitive. Generic, AVI/audio, ISRC, MPEG, DP secondary-data, and GSP update controls interact with frame boundaries and double buffering; bad masks can produce stale, torn, or missing infoframes.
- Audio formatter fields affect externally visible HDMI/DP audio behavior. Incorrect channel enables, layout, stream ID, IEC 60958 fields, HBR override, or audio-source selection can cause silence, wrong channel mapping, or bad sink capability behavior.
- DP link-training and diagnostic fields are hardware-critical. Mistakes in DPHY, scrambler, PRBS, CRC, MSA, MST allocation, MSO, DSC, or ALPM fields can cause link training failures, display blanking, intermittent corruption, or power-state regressions.
- Status and memory-power fields may be read-only or asynchronous. Treating state bits as ordinary writable configuration can race power gating, FIFO state transitions, or metadata double-buffer ownership.

## Test Signals

Useful validation signals for changes touching this generated data include:

- Build coverage for the DCN 3.0.3 AMDGPU display target; token-pasted users catch missing or renamed macros at compile time.
- Boot and modeset tests on DCN 3.0.3 hardware using both DIG0 and DIG1 paths, including HDMI and DP outputs.
- AUX/DPCD/EDID tests on the second AUX engine, especially timeout, HPD disconnect, arbitration, and retry paths.
- DP link-training coverage across lane counts/rates, enhanced framing, MST allocation, DSC, MSO, ALPM, and suspend/resume.
- HDMI validation for ACR, deep color, generic packets, AVI/audio infoframes, guard-band/control-period behavior, and TMDS output.
- Audio playback tests for stereo, multichannel, HBR, channel-status, stream ID, audio source selection, FIFO overflow acknowledgement, and audio CRC diagnostics.
- Infoframe and metadata checks that verify VPG/AFMT/DME packet updates occur on the intended frame boundaries and no generic packet collision/status bits remain stuck.
- Runtime power-management and display resume tests that confirm AFMT, VPG, DME, AUX, and DIG state is restored after power gating.
