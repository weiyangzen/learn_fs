# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_enum.h lines 1-4832

## Purpose

This chunk is the first large section of the DCE 11.2 AMD display-engine register enumeration header. It contains no executable code; it is a compile-time vocabulary of `typedef enum` constants for register field values used by the AMDGPU display stack when programming DCE 11.2 hardware. The file begins with the MIT-style AMD register-documentation license and the `DCE_11_2_ENUM_H` include guard, then defines 930 enum types in the assigned line range.

The enums map human-readable field names to exact hardware encodings. They cover display controller timing, interrupts, clocks, DCIO pads, DCP graphics planes, HDMI/TMDS/DIG/DisplayPort link control, AUX channel timing, formatter and line-buffer data formats, scaler/color-management controls, underlay plane fields, watermark selection, and the first part of Azalia HD-audio controller/codec capabilities. The chunk ends mid-family at `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES_OUTPUT_AMPLIFIER_PRESENT`, so the following chunk owns the continuation of that Azalia input-pin capability block.

## Important APIs, Types, and Register Domains

The public API surface is entirely type names and enumerators. Callers include this header directly or indirectly through generated DCE register headers and use the constants when building bitfield writes or comparing decoded register fields.

Major enum groups in this chunk:

- `CRTC_*`: CRTC start/disable behavior, field polarity, total/min/max vertical timing, trigger A/B source and polarity, force-count-now controls, flow control, master enable, blanking, interlace, stereo, snapshots, interrupt masks/types, update locks, double buffering, VGA capture, test patterns, vertical interrupts, CRC selection, external timing sync, static-screen status, 3D structure, sync polarity, and horizontal repetition.
- `PERFCOUNTER_*` and `PERFMON_*`: performance counter value selection, increment mode, run/counter-off behavior, restart, interrupt enable/type, active state, counted value type, per-counter state selectors, and global performance monitor state.
- Generic DCCG/clock controls such as `ENABLE`, `ENABLE_CLOCK`, `FORCE_VBI`, `OVERRIDE_CGTT_SCLK`, `CLEAR_SMU_INTR`, `STATIC_SCREEN_SMU_INTR`, `JITTER_REMOVE_DISABLE`, `DISABLE_CLOCK_GATING`, `DCCG_DEEP_COLOR_CNTL`, reference clock selectors, pixel-rate PLL sources, DisplayPort DTO controls, symbol-clock forcing, DVO skew/phase controls, audio DTO sources, DCCG debug selections, FIFO error detection, clock branch resets, and DCCG performance sampling.
- `DCIO_*` and `DCIOCHIP_*`: generic signal muxing, UNIPHY test clocks and channel crossbars, external pad selections, GPIO/debug routing, UNIPHY link HPD masking, DVO/VIP mapping, LVTMA panel power sequencing, backlight PWM double-buffer/update controls, genlock/swaplock/GSL routing, GPU timer readback, DCIO clock gating, soft resets, DPCS interrupt masks/types, impedance calibration, HPD/pad/AUX electrical modes, DDC/I2C GPIO control, reference-source selection, DVO reference selection, SPDIF mode, and AUX slew/spike/current/resistor trims.
- `DCP_*`: graphics-plane enable/depth/format, tiling and swizzle metadata (`NUM_BANKS`, bank width/height, tile split, macro-tile aspect, array/micro-tile mode), address translation and privileged access, component crossbars, DFQ controls, plane mode/surface update pending/taken bits, update locks, page-flip interrupt control, prescale and CSC/denorm/rounding, keying, degamma/gamut/regamma, spatial dither/randomization, cursor and cursor2 formats/updates/stereo, LUT programming formats and autofill, CRC source/line selection, GSL/XDMA synchronization, rotation, and underflow/status counters.
- `HDMI_*`, `TMDS_*`, `DIG_*`, and `AFMT_*`: HDMI keepout, clock-channel rate, packet generation and infoframe send/continuous controls, audio clock regeneration, deep color, AVMUTE/default phase, TMDS color/encoding/control-symbol patterns, DIG front-end source and stereo selection, FIFO status/error handling, display-clock switch acknowledgement/masking, AFMT interrupt/audio packet/audio CRC/ramp/infoframe/audio-source selection, and DIG back-end mode/HPD selection.
- `DP_*`, `DPHY_*`, and `DP_AUX_*`: DisplayPort link training status, embedded panel mode, pixel encoding, dynamic and YCbCr range, component depth, MSA override bits, lane count, stream disable/overflow acknowledgement, M/N generation and double buffering, enhanced framing, VBID polarity, PHY analog/test/training/PRBS/CRC controls, secondary packet/audio/MST controls, fast training status/masks, AUX HPD selection, software transaction start, AUX arbitration priority, AUX interrupt acknowledgement, AUX TX/RX timing windows, threshold/detection settings, GTC sync controls, AUX error acknowledgements, and reset/done status.
- `FBC_IDLE_MASK_MASK_BITS`, `FMT_*`, `LB_*`, `LBV_*`, `SCL_*`, `SCLV_*`, and `COL_MAN_*`: frame-buffer-compression idle-mask bit positions, formatter pixel encoding/subsampling/bit-depth/dither/CRC/debug/clamp controls, line-buffer data format and interrupts, MVP flip/swaplock helpers, LBV underlay/video line-buffer formats, scaler coefficient RAM indexes/phases/filter types, scaler modes/taps/replication/auto-ratio/update-lock/sharpness/interrupt masks, scaler-video interlace/update status, and color-management CSC/gamma/prescale/denorm/global passthrough controls.
- `UNP_*` and `WATERMARK_MASK_CONTROL`: underlay-plane graphics/video formats, surface tiling, endian/crossbar mappings, update-lock and stereosync/stack-interlace controls, CRC source/line selection, rotation including mirrored variants, pixel-drop/buffer-mode controls, and active/set A-D watermark mask selection.
- `AZALIA_*`, `CC_RCU_*`, `GLOBAL_*`, `STREAM_*`, `CORB/RIRB`, and output stream descriptor enums: HD-audio codec reset, display audio port connectivity, Azalia controller generic register enable/status, global capabilities/control/status, stream synchronization bits, command/response ring sizes and resets, immediate command status, DMA position buffer enable, output stream status/interrupt/run/reset, stream format sample rates/multipliers/divisors/sample sizes/channel counts, F2 converter/pin controls, and F0 codec widget/pin capability descriptors.

## Control Flow and State Behavior

There is no runtime control flow in this header. The effective control flow is in consumers that write MMIO registers using these symbolic values. Several enum names encode hardware-state transitions:

- `*_CLEAR`, `*_ACK`, `*_RESET`, `*_RESET_DONE`, `*_UPDATE_TAKEN`, `*_UPDATE_PENDING`, and `*_INT_MASK` values represent write-one-to-clear, acknowledgement, reset sequencing, double-buffer update, and interrupt enable/mask semantics that callers must respect.
- `*_UPDATE_LOCK`, `MASTER_UPDATE_LOCK_*`, `SCL_UPDATE_LOCK`, `COL_MAN_UPDATE_LOCK`, DCP cursor/graphics update locks, and PWM group lock enums indicate staged programming paths where multiple register fields should be latched together.
- Clock and PHY selectors (`DCCG_*`, `PIPE_*`, `SYMCLK_*`, `DCIO_*`, `TMDS_TRANSMITTER_*`, `DP_AUX_DPHY_*`) affect hardware timing domains. Incorrect ordering in callers can produce display link instability even though this header itself is declarative.
- Link and packet controls for HDMI, TMDS, DIG, DP, AUX, and AFMT are stateful at the hardware level. Values such as stream-disable acknowledgement, link-training completion, M/N double-buffer modes, AUX arbitration ownership, and audio packet continuous-send modes are consumed by driver sequencing code.

Persistence is limited to hardware registers after writes by consumers. The enum constants themselves are compile-time definitions with no memory ownership, allocation, reference counting, file I/O, or persistent on-disk state.

## Dependencies and Integration Points

This header has no local includes and no external library dependency. Its integration dependency is naming and numeric compatibility with the paired DCE 11.2 generated register address, mask, and shift headers in the same ASIC register tree. The values are also coupled to DCE 11.2 hardware documentation and to display-driver code that composes field values into MMIO writes.

Practical integration points include:

- AMDGPU/DC CRTC timing and interrupt programming uses the `CRTC_*` and `MASTER_UPDATE_*` families.
- Clock and power-management paths use DCCG, reference clock, pixel-rate source, clock-gating, SMU interrupt, and static-screen enums.
- Connector/link setup paths use DCIO/UNIPHY/HPD/GPIO/AUX, TMDS/HDMI, DIG, DP, and DPHY values.
- Plane programming, atomic flips, cursor updates, color management, scaling, line-buffer setup, underlay/video plane setup, and CRC validation use DCP/FMT/LB/LBV/SCL/SCLV/COL_MAN/UNP enums.
- Audio-over-HDMI/DP and HDA controller support use AFMT and Azalia enums for stream formats, channel counts, converter capabilities, pin widgets, unsolicited response support, and ring-buffer control.

## Risks and Edge Cases

- Numeric encodings are hardware ABI. Renaming is mostly source-level churn, but changing values silently misprograms registers.
- Many enums contain `RESERVED`, `UNDEFINED`, duplicated, misspelled, or oddly named values (`OCCURED`, `PAHSE`, `PROGRASSIVE`, `MASIK`, `PROCESING`, `ENANBLE`, `RESETET`, `STEAM`). These appear to mirror generated hardware documentation and should not be "cleaned up" unless all consumers and generated sources are updated together.
- Some booleans use inverted semantics, such as masks where `0` can mean masked/disabled or enums named `DISABLE_*` where `1` disables a feature. Review call sites by hardware meaning, not by assuming `TRUE` or `ENABLE` polarity.
- Acknowledgement and clear enums often use `0` for no effect and `1` for clear/ack, but some names say `ACK_INT`/`NOT_ACK` or `MASK_INT`/`UNMASK`; misuse can leave interrupts stuck or unintentionally unmasked.
- Reserved DP/HDMI/audio format encodings must not be selected by generic format conversion code. Several enums expose reserved sample rates, divisors, lane counts, widget types, and color depths for completeness.
- The chunk boundary cuts through Azalia input-pin widget capabilities; any per-file synthesis should merge this with the next chunk before drawing conclusions about the full Azalia F0 capability set.

## Test Signals

Useful validation is mostly compile-time and hardware/driver behavior based:

- Kernel build or targeted header inclusion should catch duplicate type names, syntax errors, and changed enum identifiers.
- Register-programming unit tests or static assertions, where available, should verify important enum-to-bitfield encodings for display modes, DP link setup, HDMI audio, cursor/plane formats, and scaler/color paths.
- Runtime display tests should cover mode set, page flip, cursor update, interrupt ack/clear, vblank/vline, CRC capture, DP link training including AUX transactions, HDMI/TMDS packet emission, audio stream bring-up, panel power/backlight PWM, and underflow/FBC status paths.
- Hardware bring-up diagnostics should compare MMIO traces against expected DCE 11.2 register values, especially for inverted mask/disable fields and update-lock/double-buffer sequencing.
