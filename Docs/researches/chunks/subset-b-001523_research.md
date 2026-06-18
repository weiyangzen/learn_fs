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
