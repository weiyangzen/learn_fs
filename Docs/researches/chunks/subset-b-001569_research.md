# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_d.h

Chunk: `subset-b-001569`
Covered source range: lines 3029-5712 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_d.h`

## Purpose

This chunk is the final tail of a generated AMD DCE 8.0 register address header. It contains C preprocessor constants that map display-controller register names to MMIO register offsets (`mm*`) and indexed subregister offsets (`ix*`). It has no executable logic; its value is the stable naming and address contract consumed by DCE 8.0 display, hotplug, audio, DisplayPort, scaler, memory/display front-end, VGA, and XDMA code.

The range starts mid-family in the audio formatter (`AFMT`) block, beginning at `mmDIG5_AFMT_ISRC2_0` and continuing through replicated DIG0-DIG6 audio/infoframe addresses. It then covers the remaining major DCE 8.0 blocks through the end of the file and terminates the header guard with `#endif /* DCE_8_0_D_H */`.

Major hardware register groups in this range are:

- DIG/AFMT/HDMI/TMDS/LVDS/DOUT addresses for audio packets, AVI/MPEG/vendor/infoframe payloads, HDMI audio clock regeneration, audio CRC/ramp/status, digital back-end enable, TMDS control/debug, LVDS data, lane enable, and DOUT scratch/power/debug controls.
- HPD and DDC/I2C addresses for six hot-plug detect lines, fast-training/toggle filtering, DDC status/speed/setup, software I2C transactions/data, generic I2C, EDID detect, and display interrupt status continuation registers.
- DisplayPort AUX debug indices, DMCU microcontroller registers, DisplayPort link encoder/stream/MST/secondary-data/AUX/GTC registers, DVO, FBC, FMT, LB, MVP, SCL, VGA, DMIF/DPG, Azalia audio, BLND, stereo converter/SISCL, and XDMA control/status/debug addresses.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this chunk. The public interface is the generated macro set:

- `mm<REGISTER>`: primary MMIO register offset used with register helpers such as `RREG32`, `WREG32`, `REG_SET`, and generation-specific register tables.
- `mm<INSTANCE>_<REGISTER>`: instance-specific aliases for replicated blocks, for example `mmDIG0_AFMT_AVI_INFO0`, `mmDP3_DP_LINK_CNTL`, `mmSCL5_SCL_MODE`, `mmLB4_LB_BUFFER_STATUS`, and `mmBLND2_BLND_CONTROL`.
- `ix<INDEXED_REGISTER>`: indirect/indexed register selector values, used with index/data register pairs such as VGA, AUX debug, FMT debug, MVP debug, Azalia codec, and Azalia stream/endpoint registers.

Important macro families include:

- `AFMT_*`, `HDMI_*`, and `DIG0..6_*`: HDMI/DVI/DP audio formatter and packetizer registers for ISRC2, AVI infoframes, MPEG infoframes, generic packets 0-7, ACR 32/44.1/48 kHz values, audio info, IEC 60958 channel status, audio CRC, ramp generation, packet enable, VBI packet control, infoframe control, audio source selection, and audio DTO debug.
- `DIG_BE_*`, `TMDS_*`, `LVDS_DATA_CNTL`, and `DIG_LANE_ENABLE`: digital back-end, TMDS, LVDS, sync character, CRC/debug, lane-enablement, and DC balancing addresses replicated across DIG0-DIG6.
- `DC_HPD1..6_*`, `DC_I2C_*`, `GENERIC_I2C_*`, and `DISP_INTERRUPT_STATUS*`: connector hotplug, HPD IRQ, fast-training, debounce/toggle filtering, DDC/I2C arbitration and transaction, generic I2C, EDID detect, and broad display interrupt summary registers.
- `DMCU_*`, `MASTER_COMM_*`, and `SLAVE_COMM_*`: display microcontroller control/status, firmware address/checksum, RAM access, event/interrupt routing, scratch, performance-monitor interrupt, and host/uC communication mailboxes.
- `DP_*`, `DP0..6_*`, and `DP_AUX0..5_*`: DisplayPort link control, pixel format, MSA, stream control, video timing/M/N, link framing, HBR2 eye pattern, DPHY training/symbol/scramble/CRC/fast-training, vertical timing override, secondary-data/audio/MST payload, debug, AUX transaction/status/PHY, and GTC synchronization registers.
- `DVO_*`, `FBC_*`, `FMT0..5_*`, `LB0..5_*`, `MVP_*`, and `SCL0..5_*`: DVO output, frame buffer compression, formatter clamp/dither/CRC/debug, line-buffer format/memory/vline/status/keyer/urgency, multi-view/AFR controls, and scaler coefficient/filter/viewport/overscan/mode-change/debug registers.
- VGA legacy registers: `GENMO`, `GENENB`, `GENFC`, DAC, sequencer, CRTC, graphics, attribute, source/select, memory base, cache, interrupt/status, and debug page registers plus indexed `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` values.
- `DPG_*` and `DMIF_PG0..5_*`: pipe arbitration, watermark masking, urgency, DPM, stutter, NB p-state change, repeater, hardware debug, and test debug addresses for display memory interface pipes.
- `AZALIA_*`, `AZF0STREAM*`, `AZF0ENDPOINT*`, and `ixAZALIA_*`: HDMI/DP audio controller, HDA CORB/RIRB/immediate-command/output-stream descriptors, codec function/pin/converter parameters, ELD/sink descriptors, multichannel/HBR/lipsync controls, CRC, stream index/data, latency counters, and endpoint index/data accessors.
- `BLND0..5_*`, `CNV_*`, `SISCL_*`, and `XDMA_*`: blender control/update/underflow/vupdate/debug, stereo input/converter color-space conversion and CRC, stereo scaler coefficient/filter/clamp/backpressure/debug, and XDMA display-side client/status/power/debug/page-gating registers.

## Control Flow

This header has no internal control flow. The macros are compile-time constants.

Runtime control flow appears in consumers:

1. A DCE 8.0 translation unit includes `dce_8_0_d.h` for register addresses and usually `dce_8_0_sh_mask.h` for bit-field masks and shifts.
2. Driver code selects an instance by using an explicit instance macro (`mmDIG3_*`, `mmDP2_*`, `mmSCL4_*`) or by adding a block offset to a base macro such as `mmAFMT_AVI_INFO0`, `mmDC_HPD1_INT_CONTROL`, or `mmAZALIA_F0_CODEC_ENDPOINT_INDEX`.
3. Register helpers perform MMIO reads/writes, indirect indexed reads/writes, or read/modify/write sequences using the address macro and the companion mask/shift macros.
4. Hardware state then drives asynchronous flows such as HPD interrupts, AUX completion/timeout/error status, DMCU events, vblank/vline status, underrun/underflow interrupts, audio stream state, and XDMA status.

Concrete local examples:

- `amdgpu/dce_v8_0.c` includes this header and uses `mmAZALIA_F0_CODEC_ENDPOINT_INDEX`/`DATA` for codec endpoint reads and writes; `mmDC_HPD1_*` plus per-HPD offsets for hotplug IRQ/status/control; and `mmAFMT_*` plus per-DIG offsets to write AVI infoframes, audio source selection, 60958 channel status, audio packets, CRC, and test-ramp controls.
- `display/dc/irq/dce80/irq_service_dce80.c` builds DCE80 IRQ source entries from `mmDC_HPD<n>_INT_CONTROL` and `mmDC_HPD<n>_INT_STATUS`.
- `display/dc/gpio/dce80/hw_factory_dce80.c` exposes HPD register addresses, including `mmDC_HPD<n>_INT_STATUS` and `mmDC_HPD<n>_TOGGLE_FILT_CNTL`, to the DC GPIO layer.
- `display/dc/resource/dce80/dce80_resource.c` includes this header while constructing generation-specific resource tables and locally supplies a few DPHY addresses that are not present in this generated file.
- `display/dc/dce80/dce80_timing_generator.c`, `display/dc/hwss/dce80/dce80_hwseq.c`, and `display/dc/gpio/dce80/hw_translate_dce80.c` include this header for generation-specific register tables.
- Older ASIC setup and power-management files such as `amdgpu/cik.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/gfx_v7_0.c`, `pm/powerplay/hwmgr/ci_baco.c`, and `pm/powerplay/smumgr/ci_smumgr.c` include the same address/mask headers for DCE 8.0 register programming and clock/power integration.

## State And Persistence Behavior

The header itself is stateless. It does not allocate memory, mutate kernel objects, persist data, or perform I/O. Its contents persist only as compiled constants in driver objects.

The hardware registers named by these macros represent persistent display engine state until changed by driver writes, firmware, display microcontroller activity, hotplug events, codec commands, power transitions, block resets, GPU reset, or suspend/resume restore. Important state classes include:

- per-DIG audio/infoframe state, including HDMI/DP packet payload registers, ACR values, audio packet enablement, IEC 60958 values, DTO/ramp/debug state, and audio CRC readback;
- connector state, including HPD sense/interrupt latches, debounce/toggle filter timing, fast-training control, DDC/I2C transaction state, EDID detect, and display interrupt summary bits;
- DMCU firmware and communication state, including firmware address windows, RAM access control/data, event triggers, interrupt masks/status, scratch registers, and master/slave command mailboxes;
- DisplayPort link state, including link control, MSA timing/colorimetry, video M/N, secondary-data/audio timestamps, MST payload allocation/rate state, DPHY training/test/CRC/scramble state, AUX software transaction buffers, and GTC synchronization status;
- pipe image-processing state for formatter, line buffer, scaler, blender, stereo converter, and stereo scaler blocks;
- legacy VGA state, which can still affect boot console, handoff, and compatibility paths;
- Azalia HDA state, including CORB/RIRB rings, immediate commands, stream descriptors, codec function/pin/converter parameters, ELD/sink descriptors, stream index/data, CRC, latency counters, and endpoint indirect registers;
- display memory arbitration and power states in DMIF/DPG and XDMA registers.

Access semantics are not encoded by the macro names. Callers must know which registers are read-only status, write-one-to-clear interrupt status, indirect index selectors, command/data windows, double-buffered update controls, or timing-sensitive programming points.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor. The practical hardware dependency is the companion field header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_sh_mask.h`

This file provides addresses; the companion `_sh_mask` file provides bit shifts and masks. Most non-trivial consumers need both to form correct register helper calls.

Primary local consumers and integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c`

Generic display-core helpers are also relevant even when they do not include this file directly. The DCE resource layer maps these macros into register tables consumed by stream encoder, AUX, GPIO, IRQ, timing generator, scaler, and transform code. For example, `display/dc/dce/dce_stream_encoder.c` relies on the AFMT generic-packet convention that there are eight generic packet payload registers, and generation-specific resource tables bind that convention to DCE 8.0 addresses.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped integer macros, so C cannot verify that a field mask from `dce_8_0_sh_mask.h` is paired with the intended address, that an instance prefix matches the active hardware block, or that an indirect `ix*` selector is written through the correct index/data register pair.

Repeated instance blocks are especially error-prone. DIG0-DIG6, DP0-DP6, AUX0-AUX5, FMT0-FMT5, LB0-LB5, SCL0-SCL5, DMIF_PG0-PG5, BLND0-BLND5, AZF0STREAM0-5, and AZF0ENDPOINT0-6 mostly share layouts with different offsets. A copy/paste error can compile and still program the wrong connector, stream encoder, scaler, line buffer, audio stream, or memory pipe.

Boundary and generation risks also matter:

- This chunk starts mid-AFMT block; the complete AFMT address family begins in the previous chunk. File-level reconciliation should merge the split families.
- This chunk ends the header; there is no next chunk for this file, and the final `#endif` confirms the macro list is complete for DCE 8.0.
- Some DCE80 resource code locally defines DPHY addresses not present in this file, such as `mmDP0_DP_DPHY_INTERNAL_CTRL` and `mmDP0_DP_DPHY_FAST_TRAINING`; consumers must not assume every later-generation DPHY register exists in this generated header.
- The header coexists with DCE 6, DCE 10, DCE 11/12, and DCN headers that reuse many names at different addresses. Including the wrong generation header can produce plausible builds but target the wrong MMIO offsets.

Timing-sensitive and protocol-sensitive areas include HPD debounce/ack/polarity, DDC/I2C transactions, AUX arbitration and timeout/error handling, DP link training and MST payload allocation, HDMI/DP audio packet programming, DMCU firmware/interrupt handoff, scaler coefficient RAM programming, DMIF watermarks/urgency, VGA legacy state, and XDMA power/status controls.

Indirect-register families need disciplined access ordering. `ixDP_AUX*_DEBUG_*`, `ixFMT_DEBUG*`, `ixMVP_DEBUG_*`, VGA sequencer/CRTC/graphics/attribute indices, Azalia codec selectors, stream index/data, and endpoint index/data registers can return or modify unintended state if the index register is shared, stale, or raced.

## Test Signals

Useful validation signals for this chunk include:

- build coverage for DCE 8.0 and related ASIC paths that include `dce_8_0_d.h`, especially `amdgpu/dce_v8_0.c`, DCE80 resource/IRQ/GPIO/timing/HW sequencing files, `cik.c`, `gmc_v7_0.c`, `gfx_v7_0.c`, CI BACO, and CI SMU manager code;
- generated-header consistency checks ensuring every `mm*` address used by DCE80 register tables has a matching field definition in `dce_8_0_sh_mask.h` where a fielded read/modify/write is expected;
- duplicate/instance checks that repeated DIG, DP, AUX, FMT, LB, SCL, DMIF, BLND, Azalia stream, and Azalia endpoint blocks have expected stride patterns and unique instance prefixes;
- connector tests across HPD1-HPD6, including connect/disconnect, rapid toggle debounce, delayed sense, HPD RX IRQ, interrupt acknowledge/re-enable, suspend/resume, and hot-unplug during AUX/DDC activity;
- DDC/I2C and DP AUX tests covering EDID reads, DPCD reads/writes, link training, timeout/error paths, HPD loss during transaction, and MST sideband traffic;
- HDMI/DP audio tests that program AFMT infoframes, IEC 60958 channel status, audio packet controls, ACR values, HBR/lipsync/multichannel Azalia controls, and verify audio presence plus codec ELD/sink data;
- DP link tests for pixel format, MSA, video timing, stream enable/disable, scrambling/training patterns, CRC readback, secondary-data packets, audio M/N/timestamp, and MST payload allocation/rate updates;
- display pipe tests for scaler coefficient RAM conflict status, viewport/overscan programming, formatter dither/clamp/CRC, line-buffer underflow/urgency/status, blender underflow/update state, and stereo converter/SISCL CRC/backpressure;
- power and reset tests around DMCU, DMIF/DPG, FBC, XDMA clock/power gating, and suspend/resume register restore;
- legacy VGA handoff tests confirming VGA source/select, memory base, cache, interrupt/status, and indexed VGA registers do not corrupt modern display pipe setup.
