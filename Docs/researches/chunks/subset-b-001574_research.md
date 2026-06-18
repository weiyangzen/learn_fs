# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_sh_mask.h lines 11924-13127

## Scope And Purpose

This chunk is the final generated shift/mask section of the AMD DCE 8.0 register field header. It contains preprocessor constants only: no functions, structs, enums, variables, or executable C logic. The macros encode bit positions and bit masks for DCE 8.0 display-engine MMIO registers and indexed audio codec registers.

The source path sits under a local `ceph-client` mirror, but this file belongs to the Linux AMDGPU display driver. It does not implement Ceph filesystem behavior. Its role is hardware metadata for Southern Islands/Sea Islands era display hardware paths that include DCE 8.0 support.

This range starts in the middle of the `AZALIA_F2_CODEC_PIN_CONTROL_MULTICHANNEL01_ENABLE` register family. The earlier mask definitions for that register are in the previous chunk. From there it covers the rest of the file through the include guard close:

- `AZALIA_F2_*` audio pin-control and channel-status fields for a second codec/function endpoint.
- `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17` byte fields.
- `AZALIA_F0_*` endpoint, converter, pin parameter, pin control, audio descriptor, multichannel, hotplug, unsolicited response, and IEC 60958 channel-status override fields.
- Global `AZALIA_*`, `AZ_TEST_*`, and audio stream/debug/latency/CRC registers.
- `BLND_*`, `SM_CONTROL2`, and `PTI_CONTROL` blender, stereo mode, pixel timing interface, update, underflow, and debug fields.
- `SI_*` scan-in enable, clock/memory power configuration, debug, and hard-debug fields.
- `CNV_*` converter/writeback-like frame/window/source-size, CSC, clamp, CRC, and debug fields.
- `SISCL_*` secondary/input scaler coefficient RAM, scaling ratios, taps, clamps, overflow/conflict interrupts, outside-pixel strategy, CRC, backpressure, and debug fields.
- `XDMA_*` PCIe client, tiling, interrupt, clock gating, memory power, BIF/status, RBBMIF timeout, power-gating, SERDES, and debug fields.

The last nonblank source line is `#endif /* DCE_8_0_SH_MASK_H */`, closing the header opened at the top of the file.

## Important APIs, Types, And Macros

There are no callable APIs or C type definitions in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.
- Indexed audio endpoint register names are paired with address/index macros from `dce_8_0_d.h`; normal MMIO register names are paired with `mm*` address macros from the same address header.

Important macro families in this chunk:

- `AZALIA_F2_CODEC_PIN_CONTROL_*` defines F2 HDMI/DP audio pin behavior: multichannel pair enables, mute bits, channel IDs, lipsync fields, HBR capability/enable, sink info index/data, manufacturer/product IDs, sink description length, port IDs, association info, and output-active status.
- `SINK_DESCRIPTION*` gives one-byte description masks/shifts used with audio sink description data.
- `AZALIA_F0_CODEC_CONVERTER_*` defines codec converter widget capabilities, supported stream formats and sample sizes/rates, converter format packing, channel/stream IDs, digital converter flags, stripe control, ramp rate, GTC embedding controls, and GTC delta debug/counter fields.
- `AZALIA_F0_CODEC_PIN_PARAMETER_*` and `AZALIA_F0_CODEC_PIN_CONTROL_*` define pin widget capability bits, unsolicited-response controls, pin sense, widget output enable, speaker/channel allocation, audio descriptors 0-13, multichannel mapping, lipsync response fields, HBR response fields, sink info words, hotplug/audio-enabled state, forced unsolicited-response payloads, configuration defaults, association info, and output-active state.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_*` and matching F2 override groups define IEC 60958 channel-status override fields for source number, clock accuracy, word length, sampling frequency, original sampling frequency, sampling coefficient, MPEG surround, CGMS-A, validity, and per-channel numbers.
- Global `AZALIA_*` fields cover controller clock gating, audio DTO phase/module and force control, audio SCLK selection, underflow filler sample, data/BDL/CORB/RIRB/DP DMA snoop/isochronous controls, cyclic-buffer position/sync, global payload capabilities, output stream arbiter latency hiding, debug, CRC0/CRC1 controls/results/channels, stream indexed access, FIFO size, latency counters, cumulative request counts, and stream debug data.
- `BLND_*`, `SM_CONTROL2`, and `PTI_CONTROL` describe blend mode, alpha mode, multiplied/global alpha, stereo frame/field alternation, force/current polarity, pixel timing enable/gap/mode, update pending/taken/lock, underflow interrupt status/ack/mask/pipe index, v-update locks for DCP/SCL/cursor paths, register-update pending flags, and test/debug access.
- `SI_*` covers scan-in enable, display-clock scan-in/SISCL gate and ramp disables, line-buffer/LUT light-sleep or shutdown disables, scan-in test clock selection, RAM power-save mode, memory power-state readbacks, and scan-in debug mode/source-width/error fields.
- `CNV_*` defines converter input source/pipe selection, frame count, window enable, stereo eye selection/order, new-content and frame-enable bits, window start/size, update state, source size, CSC bypass and matrix coefficients, round offsets, per-channel clamps, test CRC controls/results, and test debug access.
- `SISCL_*` defines secondary scaler coefficient RAM addressing and tap data, mode and tap counts for Y/RGB and CbCr, destination size, horizontal/vertical fixed-point scale ratios, initial phases, round/clamp values, overflow and coefficient-RAM conflict interrupt fields, outside-pixel black-color strategy, CRC controls/results, MCIF backpressure counter controls, and debug index/data registers.
- `XDMA_*` defines PCIe client swap/VMID/privilege fields, local surface tiling parameters, master/slave urgent and underflow interrupt status/mask/ack bits, clock-gating delays and per-pipe dynamic gate disables, memory light-sleep/shutdown controls and state, BIF error status/clear, performance status, busy status, RBBMIF read/write delay and timeout fields, power-gating control/write/status fields, always-on debug selector, and test debug data.

## Control Flow And Data Flow

This header chunk has no internal runtime control flow. Data flow is compile-time substitution: a driver C file includes `dce_8_0_sh_mask.h`, combines a mask/shift macro with a register address or indexed register ID from `dce_8_0_d.h`, and then performs MMIO or indexed audio endpoint reads/writes through AMDGPU/DC helper macros.

The legacy DCE 8.0 display path in `amdgpu/dce_v8_0.c` is a concrete consumer of the audio fields in this chunk. Its audio helpers read `ixAZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` and decode `PORT_CONNECTIVITY` to detect connected pins, write lipsync fields into `ixAZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, program speaker allocation through `ixAZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, fill ELD/SAD audio descriptor registers, and toggle `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL__AUDIO_ENABLED_MASK`.

The DC resource path also consumes DCE 8.0 masks through generated field-list macros. `display/dc/resource/dce80/dce80_resource.c` includes this header and uses structures such as `dce_transform_shift`, `dce_transform_mask`, `dce_stream_encoder_shift`, and `dce_stream_encoder_mask` built from macros in common DCE headers. Those lists draw from the generated `__SHIFT` and `_MASK` constants in this header to initialize register-helper metadata for timing generators, transforms, stream encoders, link encoders, OPPs, IPPs, GPIO, IRQ service, and hardware sequencing.

No sequencing is encoded by the macros themselves. Runtime callers must order writes around endpoint index/data accesses, audio hotplug state, ELD/SAD programming, DTO and stream setup, update-lock/pending/taken bits, interrupt acknowledgements, scaler coefficient RAM programming, power-gated blocks, clock-gated blocks, and XDMA/MCIF memory activity.

## State And Persistence Behavior

The header stores no software state and performs no I/O. The mutable state represented by this chunk lives in DCE 8.0 hardware registers and audio codec endpoint register space.

State categories represented here include:

- HDMI/DP audio state: codec converter format, channel/stream IDs, digital converter bits, pin capabilities, connection and speaker allocation data, EDID-derived audio descriptors, lipsync latency, sink identity/description, HBR controls, IEC 60958 channel status overrides, hotplug audio enablement, stream FIFO and DMA controls, audio DTO, SCLK, and CRC/debug counters.
- Display blend/update state: blend/alpha mode, global alpha, stereo alternation, pixel timing controls, update lock/pending/taken state, v-update locks across DCP/SCL/cursor sources, and underflow interrupt state.
- Converter and scaler state: CNV input selection, window/source size, CSC coefficients, clamps, CRC state, SISCL coefficient RAM, tap counts, scale ratios, phase initialization, output clamps, overflow/conflict interrupt state, outside-pixel fill colors, and MCIF backpressure counters.
- Power and diagnostic state: Azalia controller clock gating, scan-in/LUT/LB memory power configuration, XDMA clock gates, XDMA memory power state, BIF error state, RBBMIF timeout behavior, power-gating SERDES status, and debug index/data registers.

Persistence is register-specific and not declared in this generated header. Some fields are durable control bits that remain programmed until a later modeset, audio reconfiguration, power-management transition, suspend/resume, GPU reset, or another driver write. Others are transient hardware status bits, sticky interrupt flags, write-one-to-clear acknowledgements, self-clearing update requests, indexed register windows, counters, or read-only hardware status. Names such as `*_ACK`, `*_MASK`, `*_INT_STATUS`, `*_PENDING`, `*_TAKEN`, `*_LOCK`, `*_CLEAR`, `*_BUSY`, and `*_POWER_STATE` hint at behavior but do not define access type or side effects.

## Dependencies And Integration Points

This chunk depends on the rest of `dce_8_0_sh_mask.h` for the complete include-guarded generated header and on `dce_8_0_d.h` for matching MMIO addresses and indexed register IDs. It is also coupled to DCE 8.0 hardware documentation and to common AMD display register helper conventions.

Direct include consumers found in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.c`, which notes that some register shifts and masks are shared for DCE 10.0 and DCE 8.0 clock-manager code.

Practical integration surfaces are DRM/KMS modeset and audio setup, HDMI/DP audio ELD/SAD programming, audio pin and hotplug handling, display-clock and audio DTO programming, vblank/vupdate/page-flip adjacent display sequencing, transform/scaler/blender setup, diagnostic CRC/debug flows, power gating/light sleep, XDMA and memory-interface status handling, and reset/resume reinitialization for DCE 8.0-class ASICs.

## Risks And Edge Cases

- The constants are hardware ABI. A wrong mask or shift can compile cleanly while programming the wrong hardware bit, corrupting adjacent fields, leaving interrupts uncleared, or silently disabling audio/display functionality.
- This chunk starts mid-register. The `AZALIA_F2_CODEC_PIN_CONTROL_MULTICHANNEL01_ENABLE` family is split across the previous chunk and this one; final per-file synthesis needs adjacent chunk context.
- Audio endpoint access is indexed. Mixing `AZALIA_F0_CODEC_ENDPOINT_INDEX/DATA`, F0 pin-control registers, F2 pin-control registers, or normal MMIO registers can read/write the wrong register window.
- Audio data is EDID-derived and format-sensitive. Incorrect descriptor, speaker allocation, HBR, lipsync, channel ID, IEC 60958, or HDMI/DP connection bits can produce no audio, wrong channel mapping, unsupported formats, bad latency reporting, or receiver compatibility failures.
- Update and interrupt fields use similar names with different semantics. `BLND_UPDATE`, `CNV_UPDATE`, `BLND_UNDERFLOW_INTERRUPT`, `SISCL_OVERFLOW_STATUS`, `SISCL_COEF_RAM_CONFLICT_STATUS`, and `XDMA_INTERRUPT` include pending/taken/lock/status/ack/mask fields whose clear and mask polarities must match the hardware spec.
- Color and scaler fields are packed. CNV CSC coefficients, clamps, SISCL tap coefficients, fixed-point scale ratios, phase inits, and outside-pixel colors can produce subtle image-quality failures even when modesets succeed.
- Power/clock fields can affect live hardware. Azalia clock gating, scan-in/SISCL gates, LB/LUT power states, XDMA clock-gating delays, and XDMA memory light-sleep/shutdown controls need correct sequencing around active streams and resume paths.
- XDMA fields include tiling, VMID, privilege, interrupt, BIF error, timeout, and power-gating controls. Misprogramming can cause underflows, PCIe/BIF errors, memory-access faults, busy waits, or display corruption in paths using XDMA/display memory clients.
- Generated repetition increases review risk. Similar F0/F2 audio fields, descriptor indices, channel-number fields, CRC0/CRC1 fields, CNV/SISCL CRC fields, and mask fields named `*_MASK_MASK` are easy to confuse in hand edits.

## Test Signals

Validation is mainly compile-time plus hardware behavior:

- Build AMDGPU/DC configurations that include DCE 8.0 support. Missing or renamed macros should be caught by `dce_v8_0.c`, DCE80 resource construction, timing generator, IRQ service, GPIO, hwseq, GMC/GFX/PM, and shared DCE helper code.
- Compare the generated masks and shifts against a known-good upstream DCE 8.0 generated header or the authoritative ASIC register database, focusing on this chunk's audio endpoint fields, BLND/CNV/SISCL update and interrupt fields, packed coefficient/clamp fields, and XDMA tiling/power/interrupt fields.
- Exercise HDMI and DisplayPort audio on DCE 8.0 hardware: hotplug, pin detection, ELD/SAD programming, stereo and multichannel PCM, compressed formats, HBR if supported, channel allocation, lipsync values, suspend/resume, and audio enable/disable during modesets.
- Check negative audio signals: no connected audio pin logs, missing ALSA HDMI/DP sink, wrong speaker layout, muted channels, unsupported receiver format, audio dropouts after hotplug, or audio loss after resume.
- Exercise display modes that touch blender and update-lock paths: page flips, cursor updates, overlay/plane blending, global alpha, vupdate/vblank synchronization, and underflow interrupt handling.
- Exercise CNV/SISCL paths where available: scaled source sizes, odd/even tap programming, coefficient RAM updates, CSC/clamp changes, windowed capture/convert modes, CRC readback, overflow and coefficient conflict status, and MCIF backpressure counters.
- Monitor XDMA and memory-interface behavior under scanout or copy/display stress: urgent/underflow interrupts, BIF error status, busy status, RBBMIF timeout behavior, power-gating status, and regressions in black-screen, flicker, or GPU reset reports.
- Use debug and CRC fields as direct evidence when available: Azalia CRC0/CRC1, CNV test CRC, SISCL test CRC, stream latency counters, underflow/overflow status, and XDMA performance/status registers can catch bitfield mapping mistakes that plain compile tests cannot.
