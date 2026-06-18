# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_enum.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001522`: lines 1-4832, `Docs/researches/chunks/subset-b-001522_research.md`
- `subset-b-001523`: lines 4833-6813, `Docs/researches/chunks/subset-b-001523_research.md`

## Chunk Research

### subset-b-001522: lines 1-4832

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

### subset-b-001523: lines 4833-6813

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_enum.h lines 4833-6813

## Purpose

This chunk is a generated AMD DCE 11.2 register enum section. It has no executable logic; it publishes numeric encodings used by the AMDGPU display stack, audio-over-display block, display-output debug paths, and related GPU register programming code.

The range starts in Azalia/HD-audio input-pin and converter enums, then covers display blender controls, scanout tiling and pixel-format enums, broad GPU debug/performance/memory-power encodings, hotplug and DisplayPort debug controls, display core soft reset selectors, DCO debug selectors, DOUT I2C/DDC transaction controls, blender-vertical variants, and DPCSTX debug/link-mode selectors. These enum values are hardware ABI constants: consumers shift them into register fields defined by the matching `*_sh_mask.h` headers and write them through AMDGPU/DAL register helpers.

## Important APIs, Types, And Constants

There are no functions, structs, global variables, or local algorithms in this chunk. The public surface is a sequence of `typedef enum` declarations whose member values must match DCE 11.2 hardware register specifications.

Major enum families in this range are:

- `AZALIA_F0_*` and `AZALIA_F2_*`: HDMI/DP audio-codec capability and input-converter values, including pin support for DP, HDMI, EAPD, input/output/headphone/jack/impedance capability, HBR capability, stream type, base sample rate, sample multiple/divisor, bits per sample, channel count, digital transmission enable, input-pin drive, unsolicited responses, and per-channel mute bits.
- `BLND_*` and `BLNDV_*`: display blender and vertical-blender control values for current/other pipe selection, alpha blending, stereo layouts, stereo polarity, feedthrough, global/current alpha policy, active-overlap-only blending, multiplied-alpha mode, stereo-matrix subsampling, frame/field alternation, super-AA degamma/regamma, underflow interrupt ack/mask, V-update locks across DCP graphics/surface/cursor/scaler/blender clients, and test/debug mux/write-enable controls.
- Display surface layout enums: `SurfaceEndian`, `ArrayMode`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, `SampleSplitBytes`, `NumPipes`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `ShaderEngineTileSize`, `NumGPUs`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`. These values describe endian swaps, linear/tiled/PRT/3D array modes, pipe/bank geometry, row sizes, GPU interleave, and multi-GPU tile geometry.
- GPU debug enums: `DebugBlockId`, `DebugBlockId_OLD`, and downsampled `DebugBlockId_BY2/BY4/BY8/BY16` maps. These identify debug clients such as VMC, SRBM, IH, SDMA, SMU, GRBM, RLC, display-controller blocks, UVD/VCE blocks, shader/texture/color/depth blocks, memory controllers, and reserved slots.
- Render/texture/data-format enums: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, and `IMG_NUM_FORMAT`. These encode depth/stencil/color formats, compressed-image formats, FMASK layouts, numeric interpretation, export formats, compare functions, and read widths.
- Address-library-style tiling/cache/power/perf enums: `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, `MacroTileAspect`, `GATCL1RequestType`, `TCC_CACHE_POLICIES`, `MTYPE`, `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SurfaceTiling`, `SurfaceArray`, `ColorArray`, `DepthArray`, `ENUM_NUM_SIMD_PER_CU`, `MEM_PWR_FORCE_CTRL`, `MEM_PWR_FORCE_CTRL2`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and `MEM_PWR_SEL_CTRL2`.
- Display-output control and debug enums: `HPD_INT_CONTROL_*`, `DPDBG_*`, `PM_ASSERT_RESET`, `DAC_MUX_SELECT`, `TMDS_DVO_MUX_SELECT`, many `*_SOFT_RESET` selectors for DAC/audio/FMT/MVP/ABM/DVO/DIG/DPDBG/DIGLP blocks, stereo-sync selectors, `DCO_DBG_BLOCK_SEL`, `DCO_DBG_CLOCK_SEL`, `DCO_HDMI_RXSTATUS_TIMER_CONTROL_DCO_HDMI_RXSTATUS_TIMER_TYPE`, and `FMT420_MEMORY_SOURCE_SEL`.
- DDC/I2C enums: `DOUT_I2C_CONTROL_*`, `DOUT_I2C_ARBITRATION_*`, `DOUT_I2C_ACK`, `DOUT_I2C_DDC_*`, `DOUT_I2C_TRANSACTION_STOP_ON_NACK`, `DOUT_I2C_DATA_INDEX_WRITE`, `DOUT_I2C_EDID_DETECT_CTRL_SEND_RESET`, and `DOUT_I2C_READ_REQUEST_INTERRUPT_TYPE`.
- DPCSTX enums: `DPCSTX_DBG_CFGCLK_SEL`, `DPCSTX_TX_SYMCLK_SEL`, `DPCSTX_TX_SYMCLK_DIV2_SEL`, `DPCSTX_DBG_CLOCK_SEL`, and `DPCSTX_DVI_LINK_MODE`.

## Control Flow

This header has no runtime control flow. Every declaration maps a symbolic name to a fixed integer value.

Runtime control flow is supplied by consumers in the AMDGPU display and DC paths. A typical path is:

1. Determine a software display/audio state, such as framebuffer DRM format, tiling flags, scaler/blender mode, connector hotplug interrupt policy, DDC transaction shape, or display encoder/link debug selection.
2. Translate that state into one or more enum values from this header.
3. Insert the enum value into a hardware register field using a matching shift/mask definition from a DCE 11.2 register header.
4. Read or write the register through `RREG32/WREG32`, DAL `dm_read_reg/dm_write_reg`, or `REG_UPDATE` style helpers.
5. Let hardware latch the new state immediately, on a vertical-update boundary, after an interrupt ack, or as part of a reset/link/I2C transaction sequence depending on the target register.

Examples visible elsewhere in the tree show this pattern: framebuffer setup chooses graphics depth/format, tiling mode, bank dimensions, tile split, macro-tile aspect, and pipe config before writing `GRPH_CONTROL`; LUT/color setup writes bypass and CSC-related enum values into display color registers; timing-generator code reads status-position fields through register helpers; scaler code programs scaler mode bits based on taps and pixel format.

## State And Persistence Behavior

The header itself stores no state and persists nothing. Its values describe state held in GPU display/audio/debug registers and in software-visible register programming conventions.

Hardware state represented by this chunk includes:

- Audio codec capability and format state for HDMI/DP Azalia widgets.
- Per-pipe blend mode, stereo mode, alpha policy, underflow interrupt state, V-update lock state, and debug/test mux state.
- Scanout and GPU surface layout parameters such as endian swap, tiling mode, tile split, bank width/height, pipe configuration, and pixel/texture/depth formats.
- Debug client selection, performance counter mode, streaming performance monitor mode, cache policy, memory type, and memory power force/select/disable requests.
- Hotplug ack/polarity bits, DP debug FIFO/error controls, block reset assertions, stereo sync source selection, DCO debug block/clock selectors, HDMI RX status timer type, and FMT420 source selection.
- DOUT I2C controller state, including selected DDC line, transaction count, start/stop, soft reset, status reset, arbitration priority, abort/request/done handshakes, ACK cleanup, drive mode, EDID detect mode, NACK policy, indexed data writes, and read-request interrupt type.
- DPCSTX debug clock/source and DVI dual-link role selection.

Persistence is register-specific. Some values are static capability encodings, some are transient write-one-to-clear or ack bits, some remain until a modeset/hotplug/DDC transaction updates them, and reset or power-management values can be cleared by display block reset, GPU reset, suspend/resume, runtime power transitions, or firmware/driver reinitialization. The enum header does not encode access permissions, reset defaults, timing requirements, or write-one-to-clear semantics.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register contract. It is paired with DCE 11.2 address and shift/mask headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/`, especially the `dce_11_2_*_d.h` and `dce_11_2_*_sh_mask.h` files that define register addresses and bit positions. The enum values are meaningful only when used with those register fields.

Important integration points include:

- Legacy AMDGPU DCE modeset code, which programs scanout, color, LUT, viewport, and tiling registers using enum-style values and field shifts.
- AMD Display Core DCE 11.x components, where timing generators, transforms/scalers, link encoders, HPD, I2C/DDC, audio, and debug paths access the same hardware register families through DAL helpers.
- DRM framebuffer and tiling integration, where DRM pixel formats and GEM tiling flags are converted into graphics control and surface-layout encodings.
- Connector detection and EDID reads, where HPD and DOUT I2C/DDC constants affect interrupt acknowledgement, polarity, line selection, transaction construction, NACK behavior, and EDID detect reset behavior.
- Audio-over-HDMI/DP paths, where Azalia format and capability values must line up with HDA verbs/register fields and sink capabilities.
- Debug, perf, and lab tooling, where debug block IDs, DCO/DPCSTX selectors, DP debug FIFO controls, and performance-monitor modes choose internal observation points.

Although this repository path is under a `ceph-client` source mirror, the chunk is AMDGPU kernel display hardware metadata. It does not implement Ceph filesystem behavior, network protocols, distributed state, or storage persistence.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These values are plain integers, so a wrong enum value can compile cleanly while selecting the wrong hardware mode or corrupting a neighboring field when combined with shift/mask macros.

High-risk areas include display scanout tiling and format constants. Mismatched `ArrayMode`, `PipeConfig`, `TileSplit`, bank geometry, endian, or color-format values can cause corrupted scanout, wrong channel order, bad stride interpretation, GPU memory fetch faults, or display underflow. Format enums overlap with graphics/render concepts that are not all valid for display scanout; consumers must only program modes supported by the target block.

Audio format enums are sensitive to protocol-level expectations. Bad sample-rate, divisor/multiple, channel-count, bits-per-sample, HBR, or digital-enable values can produce missing audio, invalid HDA/HDMI/DP audio packets, or sink compatibility failures.

Blender and V-update-lock values affect atomicity of visible updates. Incorrect lock or alpha/stereo mode programming can leave stale surfaces, tear updates across planes, break stereo composition, hide a pipe, or mask underflow interrupts.

Interrupt and ack fields are easy to misuse. HPD and DPDBG ack values may be write-one-to-clear or level/pulse sensitive depending on the register. Writing an enable where an ack is expected, or clearing an interrupt before software records it, can lose hotplug/RX events or flood the interrupt path.

Reset and power-control enums need strict sequencing. Asserting soft resets for DIG, FMT, audio, DVO, DAC, ABM, MVP, DPDBG, or DIGLP blocks while streams are active can blank displays or wedge link/audio state. Memory power force/select controls can also interact with display fetch liveness and power-management policy.

The debug block ID families are dense and repetitive. Copy-generation errors are difficult to spot manually, and the `OLD`/`BY2`/`BY4`/`BY8`/`BY16` variants are not interchangeable with the full `DebugBlockId` map. Selecting the wrong map can direct diagnostics to an unrelated client.

DOUT I2C/DDC values affect monitor discovery. Wrong DDC line selection, transaction count, NACK stop policy, arbitration handshakes, pad drive settings, or EDID reset behavior can make displays fail to detect, hang an I2C transaction, or interfere with another requester.

The chunk ends at the file terminator. The final per-file merge should treat this range as the closing part of one generated DCE 11.2 enum namespace, not as an isolated module with independent initialization.

## Test Signals

Useful validation signals are mostly build-time, generated-register-map, and hardware-behavior oriented:

- Kernel build coverage for ASIC paths that include DCE 11.2 enum headers; missing or renamed enum members should surface as compile errors.
- Generated-header comparison against AMD's authoritative DCE 11.2 register database, checking every enum member name and numeric value.
- Display modeset and page-flip tests across linear, 1D tiled, and 2D tiled framebuffers, including endian/channel-order sensitive formats and 10 bpc formats.
- Hotplug and EDID tests on every DDC line, including connect, disconnect, HPD RX interrupt, NACK, abort, soft-reset, and multi-transaction reads.
- HDMI/DP audio tests covering PCM/non-PCM, 44.1 kHz and 48 kHz bases, sample multiples/divisors, 16/20/24-bit depths, channel counts, and HBR-capable paths.
- Plane/blender tests for alpha blending, feedthrough/current-pipe/other-pipe modes, stereo modes, V-update locking, and underflow interrupt reporting.
- Suspend/resume, runtime power-management, and GPU reset tests verifying that soft-reset and memory-power-related values are restored in the right sequence.
- Debug/perf diagnostics that select DCO, DPCSTX, DPDBG, and GPU debug-block IDs and confirm observed signals come from the expected block/clock.

Regression symptoms from incorrect constants include corrupted or blank scanout, wrong colors, display underflows, lost hotplug events, failed EDID reads, missing HDMI/DP audio, stuck I2C transactions, failed link/debug diagnostics, or displays not recovering after suspend/resume.

## Cross-Chunk Notes

Earlier chunks of `dce_11_2_enum.h` define the beginning and middle of the same generated enum namespace, including CRTC, scaler, cursor, color, graphics, audio, link, and other display block constants that consumers combine with the families documented here. This chunk completes the file with late Azalia entries, BLND/BLNDV, tiling/format/debug/perf/memory-power, HPD/DPDBG/reset/DCO/DOUT-I2C, and DPCSTX constants. The final per-file research document should frame the complete header as a generated DCE 11.2 hardware value map rather than executable driver logic.
