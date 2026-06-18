# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003507`: lines 1-7650, `Docs/researches/chunks/subset-b-003507_research.md`
- `subset-b-003508`: lines 7651-15208, `Docs/researches/chunks/subset-b-003508_research.md`
- `subset-b-003509`: lines 15209-21528, `Docs/researches/chunks/subset-b-003509_research.md`
- `subset-b-003510`: lines 21529-22532, `Docs/researches/chunks/subset-b-003510_research.md`

## Chunk Research

### subset-b-003507: lines 1-7650

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h lines 1-7650

## Scope

Work item `subset-b-003507` covers the first 7,650 lines of `vega10_enum.h`, a large AMDGPU Vega10 register enum header. The source file is 22,532 lines total, so this is a chunk report only; the complete per-file report must be synthesized later after all chunks for this header are available. This chunk begins at the license and include guard and ends immediately after the completed `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES_EAPD_CAPABLE` enum, with the next enum/comment boundary starting after line 7650.

## Purpose

This header provides named integer constants for Vega10 hardware register fields. The declarations are almost entirely `typedef enum` blocks whose enumerators map human-readable field values to exact hardware bit-pattern values. Code that programs Vega10 GPU, display, audio, performance, or memory/tile registers can include this file and use names instead of raw numbers when building register writes, interpreting register reads, or matching generated register documentation.

The chunk contains 707 `typedef enum` declarations. It does not define functions, structs, persistent data objects, inline helpers, or executable control flow. Its behavior is therefore compile-time and ABI-like: the semantic contract is the stability and correctness of enum names and numeric values.

## Important APIs And Types

The public surface in this chunk is the set of enum type names and enumerator constants. Important groups include:

- Header/compatibility declarations: `_vega10_ENUM_HEADER` guards the file; `_DRIVER_BUILD` and `GL_ZERO` conditionally expose `GL__*` aliases that map GL-style blend factors to `BLEND_*` enum values defined elsewhere in the larger header or a related include path.
- `GDS_PERFCOUNT_SELECT`: Global Data Share performance counter selector values, including bank/address conflicts, write/read buffer activity, per shader-engine/shader-array GDS operations, and GWS signals.
- Chip memory and address configuration enums: `MEM_PWR_FORCE_CTRL`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, `RowSize`, `SurfaceEndian`, `ArrayMode`, `NumPipes`, `NumBanksConfig`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `NumRbPerShaderEngine`, `NumGPUs`, `NumMaxCompressedFragments`, `ShaderEngineTileSize`, `MultiGPUTileSize`, and `NumLowerPipes`.
- Surface, texture, and buffer formats: `ColorFormat`, `SurfaceFormat`, `BUF_DATA_FORMAT`, `IMG_DATA_FORMAT`, `BUF_NUM_FORMAT`, `IMG_NUM_FORMAT`, `IMG_NUM_FORMAT_FMASK`, `IMG_NUM_FORMAT_N_IN_16`, `IMG_NUM_FORMAT_ASTC_2D`, and `IMG_NUM_FORMAT_ASTC_3D`.
- Tiling/swizzle fields: `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `SeEnable`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, `MacroTileAspect`, `SWIZZLE_TYPE_ENUM`, `TC_MICRO_TILE_MODE`, `SWIZZLE_MODE_ENUM`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, and `SampleSplitBytes`.
- Cache/MMU/fault/perf fields: `GATCL1RequestType`, `UTCL1RequestType`, `UTCL1FaultType`, `TCC_CACHE_POLICIES`, `MTYPE`, `RMI_CID`, `PERFMON_COUNTER_MODE`, and `PERFMON_SPM_MODE`.
- Display and audio pipeline blocks: `AZSTREAM`, `BLNDV`, `LBV`, `CRTC`, `FMT`, `HPD`, `LB`, `DIG`, `DCP`, `DC_PERFMON`, `SCL`, `SCLV`, `DPRX_SD`, `AZF0STREAM`, `BLND`, `AZF0ENDPOINT`, and `AZF0INPUTENDPOINT` register field enums.

Representative value contracts visible in this chunk:

- `ArrayMode` encodes linear, 1D/2D/3D tiled, thick, X-thick, and PRT tiled modes from `0x0` through `0xf`.
- `IMG_DATA_FORMAT` maps image resource format encodings from invalid, scalar/vector integer formats, packed depth formats, ETC2/BC/ASTC compression formats, FMASK, and `N_IN_16` forms through `0x3f`.
- `SWIZZLE_MODE_ENUM` maps linear, 256B, 4KB, 64KB, and variable swizzle modes with Z/S/D/R variants and X variants.
- `CRTC_*` enums model display controller timing, triggers, update locks, snapshots, interrupts, CRC selection, external timing sync, static-screen behavior, 3D structure, sync polarity, horizontal repetition, and dynamic refresh update modes.
- `HDMI_*`, `TMDS_*`, `DIG_*`, and `AFMT_*` enums model HDMI packet generation, audio clock regeneration, infoframe send/continuous modes, TMDS test/control patterns, digital encoder source routing, HPD selection, and audio FIFO/CRC controls.
- `DCP_*` enums model graphics plane enablement, tiling/swizzle fields, format/depth, endian/crossbar selection, gamma/degamma/regamma/color-space paths, cursor configuration, LUT access, CRC, GSL sync, XDMA underflow/flip handling, and surface counters.
- `PERFCOUNTER_*` and `PERFMON_*` enums model display perf counter value selection, increment modes, run/count-off control, interrupt modes, counter states, and global/local state selection.
- `SCL_*` and `SCLV_*` enums model scaler filter RAM indexing, phases, filter types, RGB/YCbCr scale/bypass modes, tap counts, replicate factors, update locks, coefficient completion, sharpening, and interrupt masks.
- `AZALIA_F0_CODEC_*` enums model HD-audio converter and pin widget capabilities, including widget type, LR swap, power control, digital capability, connection lists, unsolicited response, processing, striping, format override, amplifier capability, channel capability, pin capabilities, multichannel mode, HBR capability, DP enablement, and EAPD capability.

## Control Flow

There is no runtime control flow in this chunk. The only preprocessing flow is:

- `_vega10_ENUM_HEADER` prevents multiple inclusion.
- `_DRIVER_BUILD` and `GL_ZERO` determine whether the `GL__*` blend aliases are created.
- `ENUMS_GDS_PERFCOUNT_SELECT_H` guards the `GDS_PERFCOUNT_SELECT` typedef specifically, which matters because similar ASIC enum headers define the same type name.

Every other item in the chunk is a straight enum declaration. Runtime code elsewhere decides when to write these values to registers, poll status fields, or interpret hardware output.

## State And Persistence Behavior

This chunk stores no runtime state and performs no persistence. The enum constants are compiled into users of the header as integer constants. Persistent effects occur only indirectly when a consumer writes one of these values into hardware registers or firmware/shared-memory packets. Because register programming values become externally visible hardware state, enum numeric stability is the key state contract.

Several enums represent status/acknowledge/clear semantics, for example `*_ACK`, `*_CLEAR`, `*_INT_MASK`, `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `*_RESET`, and `*_RESET_ACK`. The header only names those values; it does not implement the read-modify-write ordering or polling loops needed to use them safely.

## Dependencies

This chunk has minimal direct C dependencies:

- It depends on enum support from the C compiler.
- The GL alias block depends on `BLEND_ZERO`, `BLEND_ONE`, `BLEND_SRC_COLOR`, and related `BLEND_*` identifiers being visible when `_DRIVER_BUILD` is not set and `GL_ZERO` is absent. Those identifiers are not defined in lines 1-7650, so they must come from later portions of the header or from another included generated enum/register header.
- The duplicated `GDS_PERFCOUNT_SELECT` guard suggests the same type name can appear in multiple ASIC headers; inclusion order and guard state can affect whether this typedef is emitted.

No Linux kernel headers are included directly in this chunk, and there are no macros for register offsets or bit masks here; those normally live in nearby generated register headers.

## Integration Points

Direct source search in the AMD GPU subtree shows `amdkfd/kfd_device_queue_manager_v9.c` includes `vega10_enum.h`. The enum names also appear in sibling generated ASIC headers such as `navi10_enum.h`, `soc21_enum.h`, and SMU enum headers, which indicates a shared generated-register-header pattern across GPU generations.

Likely consumers in the Vega10 stack include:

- KFD/queue-manager code configuring Vega10 queue, memory, and performance state.
- AMDGPU display code programming CRTC, FMT, HPD, LB, BLND/BLNDV, DIG/HDMI/TMDS/AFMT, DCP, SCL, and Azalia registers.
- Register pack/unpack code that combines these enum values with register field masks/shifts from companion `*_sh_mask.h` and `*_d.h` headers.
- Diagnostic/perf tooling that selects hardware counters using `GDS_PERFCOUNT_SELECT`, `PERFMON_*`, and `PERFCOUNTER_*` values.

Because this is a generated-style enum header, its primary integration role is as a chip-specific vocabulary layer aligned to the Vega10 hardware register specification.

## Risks

- Numeric drift is the main risk. Changing an enum value without matching the hardware spec can silently program the wrong register field value and cause display failure, incorrect surface layout, memory faults, broken audio, invalid performance counters, or GPU hangs.
- Name drift across ASIC headers is risky. The same enum type or enumerator names appear in nearby generation-specific headers; including multiple ASIC headers can collide unless guarded or isolated carefully.
- Some aliases intentionally share values, such as `MTYPE_WC` and `MTYPE_RW` both using `0x1`. Consumers must treat names as semantic aliases rather than unique values.
- Reserved values are explicitly represented. Code should avoid selecting `*_RESERVED*` entries unless hardware documentation requires them for a particular workaround.
- Some generated names contain spelling inconsistencies, for example `SCL_PSCL_ENANBLE`, `PAHSE`, `OCCURED`, `CAPABLILITY`, and `PROCESING`. Renaming these for spelling would break source compatibility with existing users.
- Boolean-looking fields are not uniformly active-high/active-low in meaning. For example `MASK`, `ACK`, `CLEAR`, `RESET`, `DISABLE`, and `ENABLE` enums must be interpreted against the specific register field.
- The chunk boundary occurs at an enum/comment transition in the Azalia input endpoint section; later chunks are needed to complete the whole source-file understanding and any remaining endpoint capability enums.

## Test Signals

Useful validation signals for this chunk are compile-time and hardware-facing:

- Build AMDGPU/KFD code paths that include `vega10_enum.h`, especially `amdkfd/kfd_device_queue_manager_v9.c`, with warnings enabled to catch duplicate typedefs or missing `BLEND_*` dependencies.
- Run static checks that compare enum numeric values against the generated register specification or the upstream kernel header version for Vega10.
- Run `rg`/include-order checks for duplicate enum type names across `vega10_enum.h`, `navi10_enum.h`, `soc21_enum.h`, and SMU enum headers.
- Exercise display modeset tests that cover CRTC timing/update locks, FMT depth/dither/CRC, HPD interrupts, LB underflow/line-buffer status, DIG/HDMI/TMDS programming, DCP plane/cursor/LUT paths, and scaler coefficient/update paths.
- Exercise audio-over-HDMI/DP tests that validate AZSTREAM, AFMT, and Azalia endpoint fields, including infoframes, audio clock regeneration, HBR capability, and FIFO reset behavior.
- Run GPU memory/surface layout tests that validate `ArrayMode`, `SWIZZLE_MODE_ENUM`, `IMG_DATA_FORMAT`, tiling, pipe/bank, and endian values against rendered images, compute buffers, and page-fault behavior.
- Exercise perf counter tests that program `GDS_PERFCOUNT_SELECT`, `PERFMON_*`, and `PERFCOUNTER_*` selectors and verify expected counter movement under known workloads.

## Cross-Chunk Notes

This chunk is only the first part of `vega10_enum.h`. Later chunks should verify:

- Whether `BLEND_*` values referenced by the early GL alias block are defined later in the file or through another include path.
- Whether remaining Azalia input endpoint enums continue immediately after line 7650.
- Whether the file eventually closes the `_vega10_ENUM_HEADER` include guard cleanly.
- Whether later portions introduce additional enum blocks, macros, or declarations that alter the whole-file dependency and integration picture.

### subset-b-003508: lines 7651-15208

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h lines 7651-15208

## Scope

This chunk is a middle slice of the Vega10 AMD GPU register-value header. It contains generated-style `typedef enum` declarations and a few `#define` constants for hardware register fields, not executable logic. The range starts inside the Azalia F0 codec input-pin capability declarations and then covers complete display, audio, clocking, color, cache, shader-input, and shader-queue enum sections through the beginning of the `SQDEC` value block.

## Purpose

The declarations in this slice provide symbolic names for raw numeric values that must be written to, or decoded from, Vega10 display/audio/GFX registers. They are used as ABI-like constants between the driver and GPU hardware blocks. Their purpose is readability and correctness for register programming paths: instead of using unexplained integers for DisplayPort training, AUX timing, DSI mode selection, Azalia audio stream setup, display clock routing, color-management mode selection, color buffer compression/perf events, texture-cache operations, SPI performance counters, and SQ debug/performance controls, driver code can use named constants tied to the hardware spec.

## Major Blocks And Types

- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES_*` and `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR_HBR_CAPABLE` continue the previous Azalia F0 codec section with HDMI, balanced I/O, input/output, headphone drive, jack detection, trigger, impedance-sense, and HBR capability values.
- `UNP_*` enums describe underlay graphics enablement, depth, tiling, bank geometry, address translation, color expansion, video format, endian swap, RGB crossbar selection, update-lock behavior, stereosync/interlace flip handling, CRC source/line selection, rotation, pixel drop, and buffer mode.
- `DP_*` and `DPHY_*` enums cover DisplayPort link/video programming: link-training completion, embedded panel mode, pixel encoding, dynamic range, YCbCr range, component depth, MSA overrides, lane count, stream disable/overflow interrupts, scrambler/8b10b/PRBS/CRC controls, fast training, secondary packets, MST encoder controls, HBR2 pattern modes, and GSP send/priority controls.
- `COL_MAN_*` enums model display color-management pipeline choices: update locks, input CSC mode/type/rounding, prescale, input gamma, output CSC, denorm clamp, regamma, global passthrough, degamma, and gamut-remap modes.
- `DP_AUX_*` enums define AUX-channel ownership, software transaction triggers, arbitration priority, interrupt acknowledgements, PHY TX/RX timing windows, detection thresholds, GTC sync windows/attempts, error acknowledgement, and reset state values.
- `DSI_*` enums configure MIPI DSI command/video modes: source and destination formats, flag clear, bit swapping, clock gating, ULPS entry/exit, lane enables, display/DSI/byte/escape clock resets, CRTC selection, packet byte order, video traffic/power/pulse modes, RGB swap, command packet type/order, data buffer selection, FIFO watermarks, command triggers, TE source/mux/mode/polarity, reset panel, CRC, EOT behavior, BIST, and debug clock selection.
- `DCIOCHIP_*`, `DCIO_*`, `DCO_*`, `DOUT_I2C_*`, `DPCSRX_*`, and `DPCSTX_*` enums describe display I/O pads, HPD selection, GPIO mask/drive/invert modes, AUX electrical trim values, generic signal routing, UNIPHY ref/fb divider debug selections, pad external signal muxing, DVO/LVTMA/backlight PWM controls, genlock/swaplock/global-sync routing, GPU timer position/read selection, soft resets, DPHY lane selection, DPCS interrupt behavior, debug async block selection, DisplayPort clock receiver/transmitter symbol-clock selection, and DDC/I2C controller arbitration/transaction controls.
- `GENERIC_AZ_*`, `AZ_*`, `STREAM_*`, `CORB_*`, `RIRB_*`, `IMMEDIATE_COMMAND_STATUS_*`, and `DMA_POSITION_*` enums cover the Azalia controller: generic register enable/status bits, 64-bit address capability, unsolicited response enable, flush/reset/status, codec-present state, per-stream stopped flags, CORB/RIRB reset and size selection, immediate command status, and DMA position-buffer enablement.
- `AZALIA_F2_CODEC_*`, `CC_RCU_DC_AUDIO_*`, `AOUT_*`, `I2S_*`, and `SPDIF_*` enums cover display audio endpoints and output: PCM/not-PCM stream type, sample rate/multiple/divisor, bits per sample, channel count, digital converter status/control bits, output/input pin enable and unsolicited response, downmix/multichannel mute/mode, codec reset, port connectivity, audio output FIFO/CRC, I2S word/alignment/bit-order/LRCLK settings, and SPDIF inversion.
- `DCCG_*`, `DCI_*`, `Lpt*`, `ENABLE`, `ENABLE_CLOCK`, `REFCLK_*`, `PIPE_*`, `CRTC_*`, and related clock enums define display clock gating, deep color, reference clock source selection, microsecond/millisecond timebase source, pixel-rate source and PLL routing, DP DTO controls, pixel add/drop, symbol clock forcing, DVO clock skew/in-phase controls, MVP source, audio DTO selection, DCCG debug/perf modes, clock-branch and PLL soft resets, low-power tiling pipe/bank values, and DCEF clock gating overrides.
- `CB*`, `SurfaceNumber`, `SurfaceSwap`, `BlendOp`, `CombFunc`, `BlendOpt`, `Cmask*`, and `MemArbMode` enums provide color-buffer render target state values: surface numeric format and swizzle, render mode including resolve/decompress/DCC decompress, rounding/source export format, blend factors and combine functions, blend optimization overrides, CMASK encodings, CMASK addressing, memory arbitration, and color-buffer performance-counter selectors/filters.
- `TC_OP_MASKS`, `TC_OP`, `TC_NACKS`, and `TC_EA_CID` enumerate texture-cache/global-memory operations and diagnostics: read/write, 32-bit and 64-bit atomics with and without return, denorm-flush variants, L1/L2 writeback/invalidate operations, metadata invalidation, NOP/ack operations, fault NACK categories, and EA client IDs for render targets, FMASK, DCC, depth/stencil, TCP/SQC, CPF/CPG/IA/WD/PA, and UTCL2/TPI.
- `SPI_*` enums describe shader processor input behavior and performance counters: sample interpolation selection, fog mode, point-sprite overrides, a long `SPI_PERFCNT_SEL` range for VS/GS/ES/HS/LS/CS/PS allocation, stalls, resource fullness, clock-gating, export counts, and shader export formats.
- `SQ_*`, `SH_MEM_*`, and `ENUM_SQ_EXPORT_RAT_INST` enums define shader queue/resource state: texture clamp/filter/aniso/depth-compare/border-color settings, buffer/image/flat resource types, image filter mode, XYZW/0/1 component selection, wave types, thread-trace token/misc/instruction/register/issue/capture fields, SQ performance selectors including SQC cache/TLB/replay counters, CAC power selectors, indirect command op/mode, EDC info source, floating-point round mode, interrupt word encoding, RAT export store/atomic instructions, instruction-buffer states, instruction-stream states, wave IB ECC states, and shader memory address/alignment modes.
- The final `#define` values in this chunk expose `SQ_WAVE_TYPE_PS0`, SQ indirect register partition offsets/sizes, and SQ GFX decoder address range/shift constants.

## APIs, Functions, And Control Flow

There are no functions, callbacks, structs, or runtime control-flow constructs in this chunk. The C API surface is a collection of globally visible enum typedef names and preprocessor constants. Control flow exists only in consumers that include this header and select these values while programming registers or decoding register values.

Because each enum maps exact integer encodings to symbolic names, consumers should treat these as hardware contract constants rather than ordinary software enums whose values can be reordered. Many enums are binary field values, while dense tables such as `CBPerfSel`, `TC_OP`, `SPI_PERFCNT_SEL`, and `SQ_PERF_SEL` define large numeric selector spaces with reserved gaps and hardware-specific ordering.

## State And Persistence

The header itself has no mutable state and performs no persistence. State changes occur when other driver paths write these values into MMIO registers, packetized command streams, saved context state, debug registers, perf-counter selectors, or audio/display control registers. Once programmed into hardware, the values can persist in GPU block registers until reset, mode-set reprogramming, context switch, power transition, or explicit driver update.

Several enum groups represent fields that are stateful in hardware:

- Update-lock and double-buffer-like controls for UNP and color management affect when display surface/color changes become visible.
- DP/DPHY/AUX/DSI reset, training, stream-disable, overflow, CRC, BIST, and interrupt acknowledgement values control hardware sequences with timing-sensitive side effects.
- Azalia CORB/RIRB, stream synchronization, flush, controller reset, immediate command, DMA-position, and pin/converter controls influence audio DMA and codec command state.
- DCCG/DCIO clock, soft-reset, PWM, genlock, swaplock, and timer selections affect display timing and power state.
- CB/TC/SPI/SQ perf-counter selector values control what hardware events are counted, sampled, or traced.
- SQ indirect partition and GFX decoder constants define memory/register layouts used by debug and wave-state inspection code.

## Dependencies And Integration Points

This file is a low-level include consumed by AMDGPU/DRM code that needs Vega10 register encodings. It depends only on the C compiler's enum and macro handling, but semantically it depends on the Vega10 hardware register specification and companion register headers that define field masks, shifts, and register addresses. Typical integration points are:

- Display Core or legacy display programming paths for DP, DSI, AUX, DCIO, DCCG, UNP, color-management, backlight PWM, HPD, I2C/DDC, and clock/reset fields.
- HDMI/DisplayPort audio setup paths for Azalia controller/endpoint, AOUT, I2S, SPDIF, and port connectivity fields.
- Graphics command setup and render backend programming for CB surface/blend/compression mode values.
- Cache/memory operation and fault-diagnostic paths for `TC_OP`, NACK, and EA client IDs.
- Performance monitoring, thread tracing, debug, and profiling infrastructure for CB/SPI/SQ selector enums, trace token types, indirect SQ command modes, SQ register partitions, and decoder address constants.
- Generated register access helpers or manually written register-update macros that combine enum constants with field shifts/masks from adjacent Vega10 headers.

## Risks And Edge Cases

- Numeric drift is the primary risk. Changing an enum value, removing a reserved entry, or reordering declarations can silently program the wrong hardware behavior while still compiling.
- Some names contain apparent typos inherited from the hardware/spec source, such as `STEAM_NOT_STOPPED`, `RESETET`, `ATTAMPS`, `DISBALE`, and `COL_MAN_MULTIPLE_UPDAT_EDISABLE`. These should not be "fixed" casually because downstream code may reference the exact symbols.
- Enum names are globally visible C identifiers. Short generic names in this slice, including `ENABLE`, `ENABLE_CLOCK`, `RoundMode`, `BlendOp`, and `SourceFormat`, can collide with other headers if include ordering or namespace assumptions change.
- Several enums contain reserved values that are still named. Drivers should avoid programming reserved encodings unless matching existing hardware sequences require them.
- Large selector enums such as `CBPerfSel`, `SPI_PERFCNT_SEL`, and `SQ_PERF_SEL` are especially vulnerable to incomplete updates when porting from another ASIC generation; counters may appear to work while measuring a different event.
- Write-one-to-clear or acknowledgement-like values, for example DP overflow/interrupt ACK and AUX error ACK fields, are side-effectful when written by consumers. Treating them as passive status values can clear interrupts unexpectedly.
- Clock, PHY, reset, and training fields are timing-sensitive. Incorrect combinations in DCCG, DCIO, DP AUX/DPHY, DSI, or DOUT I2C paths can cause link-training failures, blank display, DDC/EDID failures, audio loss, or hangs in polling loops.
- This chunk begins and ends mid-file. The preceding chunk owns earlier Azalia F0 context, and the following chunk begins after the `SQDEC value` marker with additional graphics front-end enum sections. Whole-file research needs both boundaries reconciled.

## Test Signals

Useful validation signals for consumers of this chunk are compile-time and hardware-behavior oriented:

- Build coverage for all AMDGPU/DRM objects that include `vega10_enum.h`; this catches missing or renamed symbols but not wrong numeric encodings.
- Static comparison against the generated source or hardware XML/register database, especially for dense selector enums and reserved-value positions.
- Display smoke tests across DP/eDP/DSI paths: link training, stream enable/disable, MST sideband operation, AUX/DDC EDID reads, HPD handling, deep color/YCbCr modes, color-management programming, backlight PWM, and suspend/resume.
- Audio-over-display tests for Azalia stream setup, codec reset, channel counts, sample rates, pin enable, silent keepalive, and unsolicited responses.
- Perf-counter and tracing tests that select representative CB, SPI, SQ, and SQC events and verify counters move under known workloads.
- GPU debug tests for SQ indirect register partition reads, wave-state decoding, thread-trace token parsing, EDC source reporting, and RAT export instruction decoding.
- Cache/memory operation tests for TC writeback/invalidate and atomic encodings where those values are used in command packets or diagnostics.

## Chunk Notes For Merge Lane

This chunk should be merged with neighboring chunks as one source-file report for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h`. It is intentionally chunk-scoped and does not create the final source-tree-aligned per-file document. The most important cross-chunk boundary is that this range starts inside Azalia F0 codec pin capability declarations and ends immediately after SQ indirect/GFX decoder constants at the `SQDEC value` marker.

### subset-b-003509: lines 15209-21528

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h lines 15209-21528

## Scope

This chunk covers the middle of the generated Vega10 AMDGPU enum header. It starts at shader-queue address-window and SQ constant definitions and ends inside the `RMIPerfSel` enum, after RMI/RB read-return counter selectors through `RMI_PERF_SEL_RMI_RB_32BRDRET_VALID_CID4`. The `RMIPerfSel` enum continues in the next chunk, so the RMI section is intentionally incomplete here.

The covered families are:

- SQ address windows, dispatcher limits, exception IDs, wait-count bit partitions, EDC controls, shader instruction encoding/opcode constants, special registers, send-message encodings, and target/format selectors.
- COMP `CSDATA_TYPE` constants for typed command-stream/debug data.
- VGT, IA, and WD primitive, draw-source, tessellation, pipeline-stage, event, and performance-counter selectors.
- GB, TA, TD, TCP, TCC, and TCA enums for tiling-table sizing, texture addressing, cache policy, watch/data selector modes, and texture/cache performance counters.
- GRBM and CP enums for global graphics block performance selectors, per-shader-engine GRBM selectors, command-processor ring/pipe/ME IDs, perfmon state, and command-processor microblock counters.
- SX and DB enums for blend optimization, color downconversion, depth/stencil behavior, DB/SX performance counters, ring counters, memory arbitration watermarks, DFSM flush events, and pixel-pipe counters.
- Texture and vertex fetch enums for sampler border/clamp/filter/dimension/format controls, texture/vertex data formats, swizzle source/destination selectors, endian swap, fetch instructions, numeric formats, and SRF/type modes.
- SU and SC performance-counter selector enums plus raster-routing/binning enums for shader engine, scan converter, packer, render backend, primitive binning, and coverage-to-shader selection.
- The beginning of RMI performance selectors for invalidation, UTCL1, and RB/RMI write/read request and return traffic.

This chunk is generated hardware-interface data. It contains `#define` constants and `typedef enum` declarations only. There are no C functions, no data structures with storage, no dynamic allocation, and no executable control flow.

## Purpose

`vega10_enum.h` provides symbolic names for numeric encodings used by Vega10 graphics, shader, cache, texture, command processor, raster, depth/color, and memory-interface blocks. The constants are an ABI between AMDGPU code and the hardware register fields, packet fields, shader/debug tools, and performance-monitor programming interfaces that expect exact numeric values.

The definitions let consumers use names such as `DI_PT_TRILIST`, `CACHE_FLUSH_AND_INV_TS_EVENT`, `SQ_OP_MUBUF`, `TEX_DIM_2D`, `CP_RING_ID_COMPUTE`, `SC_PBB_BUSY`, or `RMI_PERF_SEL_UTCL1_TRANSLATION_MISS` instead of embedding raw integers. That matters because most values are register-field encodings rather than independent software policy choices; changing a value changes what the hardware is asked to do or what event a counter measures.

## Important APIs, Types, and Constants

### SQ and Shader Instruction Constants

The chunk begins with SQ decode and performance decode address ranges such as `SQDEC_BEGIN/END`, `SQPERFSDEC_BEGIN/END`, `SQPERFDDEC_BEGIN/END`, `SQGFXUDEC_BEGIN/END`, and `SQPWRDEC_BEGIN/END`. It also defines SQ dispatcher and program-resource limits, including `SQ_DISPATCHER_GFX_MIN`, `SQ_DISPATCHER_GFX_CNT_PER_RING`, `SQ_MAX_PGM_SGPRS`, and `SQ_MAX_PGM_VGPRS`.

SQ exception and wait-count constants define hardware-visible bit positions and exception IDs:

- `SQ_EX_MODE_EXCP_*` maps VALU exception slots such as invalid operation, input denorm, divide-by-zero, overflow, underflow, inexact, integer divide-by-zero, watchpoint, and memory violation.
- `SQ_EX_MODE_EXCP_HI_*` maps additional address-watch exception slots.
- `INST_ID_*` reserves hardware-inserted instruction IDs for ECC interrupt, thread-trace PC, trap, kill sequence, SPI write-exec, and host register trap messages.
- `SIMM16_WAITCNT_*` defines the immediate partitions for VM, EXP, and LGKM wait counts.
- `SQ_EDC_FUE_CNTL_*` names fatal uncorrectable error control sources across SQ, LDS, SIMD lanes, texture address/data, and TCP.

The large `VALUE_SQ_*` block is a generated catalog of shader instruction encodings and operand spaces. It includes encoding class selectors for SOP, SMEM, VOP, VINTRP, DS, MUBUF, MTBUF, MIMG, EXP, and FLAT formats; offset/count constants for translating between VOP3 and VOP1/VOP2/VOPC/VOP3P/VINTRP encodings; register-count limits for VGPR, SGPR, TTMP, and attributes; bitfield sizes and shifts for `waitcnt`, `s_sendmsg`, and `s_setreg`/hardware register operands; opcode values for scalar, vector, LDS/DS, image, buffer, export, flat/global/scratch, interpolation, packed, SDWA, and DPP operations; and special source/destination values such as VCC, EXECZ, SCC, LDS, aperture, XNACK mask, M0, and inline constants.

These SQ values are likely consumed by shader compilation, debug, disassembly, tracing, and register-programming paths that need the Vega10 ISA encodings to match hardware exactly.

### COMP, VGT, IA, and WD

`CSDATA_TYPE` defines command-stream data record classes: thread group, state, event, and private data. The adjacent width constants (`CSDATA_TYPE_WIDTH`, `CSDATA_ADDR_WIDTH`, and `CSDATA_DATA_WIDTH`) define the packed representation size.

The VGT section defines frontend geometry and pipeline values:

- Primitive input/output enums: `VGT_OUT_PRIM_TYPE`, `VGT_DI_PRIM_TYPE`, `VGT_GRP_PRIM_TYPE`, and `VGT_GRP_PRIM_ORDER`.
- Draw/index setup enums: `VGT_DI_SOURCE_SELECT`, `VGT_DI_MAJOR_MODE_SELECT`, `VGT_DI_INDEX_SIZE`, `VGT_DMA_SWAP_MODE`, `VGT_INDEX_TYPE_MODE`, and `VGT_DMA_BUF_TYPE`.
- Pipeline routing and shader-stage enums: `VGT_OUTPATH_SELECT`, `VGT_GS_MODE_TYPE`, `VGT_GS_CUT_MODE`, `VGT_GS_OUTPRIM_TYPE`, `VGT_TESS_TYPE`, `VGT_TESS_PARTITION`, `VGT_TESS_TOPOLOGY`, and the `VGT_STAGES_*_EN` stage selectors.
- Synchronization and event enum `VGT_EVENT_TYPE`, covering cache flushes, partial flushes, streamout events, context done, pipeline statistics, perf counter start/stop/sample, thread trace start/stop/marker/flush/finish, DB/CB invalidation events, NGG/legacy pipeline enable events, and similar command processor event packet encodings.
- `VGT_PERFCOUNT_SELECT`, `IA_PERFCOUNT_SELECT`, and `WD_PERFCOUNT_SELECT`, which select geometry/frontend, input assembler, and work distributor performance events.

`WD_IA_DRAW_TYPE`, `WD_IA_DRAW_REG_XFER`, and `WD_IA_DRAW_SOURCE` identify draw transfer styles and draw sources for the IA/WD path. These definitions connect command-stream draw programming to the VGT/IA/WD hardware interpretation of primitive topology, index source, and pipeline stage routing.

### GB, Texture Cache, and Memory Cache Blocks

The GB section defines `GB_EDC_DED_MODE` plus tiling table and macrotable sizes. These constants describe graphics block error handling and table sizing rather than executable logic.

TA, TD, TCP, TCC, and TCA enums cover texture/cache behavior:

- `TA_TC_ADDR_MODES` names address calculation modes such as default and compatible modes.
- `TA_PERFCOUNT_SEL` and `TD_PERFCOUNT_SEL` select texture-address and texture-data unit events.
- `TCP_PERFCOUNT_SELECT` is a large selector space for texture cache requests, hits/misses, stalls, atomics, invalidations, tag/data behavior, FIFO pressure, and related cache-side metrics.
- `TCP_CACHE_POLICIES`, `TCP_CACHE_STORE_POLICIES`, and `TCP_WATCH_MODES` define cache read/store policy and watchpoint modes.
- `TCP_DSM_DATA_SEL`, `TCP_DSM_SINGLE_WRITE`, and `TCP_DSM_INJECT_SEL` select diagnostic/state-machine data and injection controls.
- `TCC_PERF_SEL` and `TCA_PERF_SEL` expose L2/cache-array performance selectors, covering requests, returns, probes, misses, stalls, invalidations, and backend traffic.

These enums are integration points for GPU performance monitoring, cache diagnostics, and low-level register programming. They do not implement cache behavior; they encode what hardware path or event is selected by a perf register or control field.

### GRBM and Command Processor

`GRBM_PERF_SEL` and the per-shader-engine `GRBM_SE0_PERF_SEL` through `GRBM_SE3_PERF_SEL` enumerate graphics register bus manager performance events and shader-engine-specific activity/idle/busy signals.

The command-processor section defines:

- `CP_RING_ID`, `CP_PIPE_ID`, and `CP_ME_ID` for naming graphics/compute/SDMA-style CP routing identities.
- `SPM_PERFMON_STATE`, `CP_PERFMON_STATE`, and `CP_PERFMON_ENABLE_MODE` for perf monitor state-machine and enable control encodings.
- `CPG_PERFCOUNT_SEL`, `CPF_PERFCOUNT_SEL`, and `CPC_PERFCOUNT_SEL` for graphics, frontend, and compute command processor performance selectors.
- `CP_ALPHA_TAG_RAM_SEL` for selecting CP alpha tag RAMs.
- CP-related response, retry, interrupt, VMID size, and configuration-space range constants (`CONFIG_SPACE*`, `UCONFIG_SPACE`, `PERSISTENT_SPACE`, and `CONTEXT_SPACE`).

These values tie packet execution, queue/ring selection, VMID-related addressing, and command processor perf monitoring into the rest of the AMDGPU command submission and diagnostics stack.

### SX, DB, Texture, Vertex, SU, and SC

The SX section provides render backend/color-output values such as `SX_BLEND_OPT`, `SX_OPT_COMB_FCN`, `SX_DOWNCONVERT_FORMAT`, and a large `SX_PERFCOUNTER_VALS` enum. These encode blend optimization modes, format downconversion choices, and SX performance events.

The DB section defines depth/stencil and depth-buffer operation values:

- `ForceControl`, `ZSamplePosition`, `ZOrder`, `ZpassControl`, `ZModeForce`, `ZLimitSumm`, `CompareFrag`, `StencilOp`, `ConservativeZExport`, `DbPSLControl`, and `DbPRTFaultBehavior`.
- `PerfCounter_Vals`, `RingCounterControl`, `DbMemArbWatermarks`, `DFSMFlushEvents`, `PixelPipeCounterId`, and `PixelPipeStride`.

Texture and vertex fetch enums define sampler and resource descriptor encodings:

- `TEX_BORDER_COLOR_TYPE`, `TEX_CHROMA_KEY`, `TEX_CLAMP`, `TEX_COORD_TYPE`, `TEX_DEPTH_COMPARE_FUNCTION`, `TEX_DIM`, `TEX_FORMAT_COMP`, `TEX_MAX_ANISO_RATIO`, `TEX_MIP_FILTER`, `TEX_REQUEST_SIZE`, `TEX_SAMPLER_TYPE`, `TEX_XY_FILTER`, and `TEX_Z_FILTER`.
- `VTX_CLAMP`, `VTX_FETCH_TYPE`, `VTX_FORMAT_COMP_ALL`, `VTX_MEM_REQUEST_SIZE`.
- `TVX_DATA_FORMAT`, `TVX_DST_SEL`, `TVX_ENDIAN_SWAP`, `TVX_INST`, `TVX_NUM_FORMAT_ALL`, `TVX_SRC_SEL`, `TVX_SRF_MODE_ALL`, and `TVX_TYPE`.

The SU and SC sections define `SU_PERFCNT_SEL` and `SC_PERFCNT_SEL`, both large performance selector spaces. The SC selector list covers scan converter input/output pressure, PA/SC and SC/SPI interfaces, PS arbitration, end-of-pipe/event synchronization, PBB/binning metrics, overlap/quad packer events, busy/starved states, and FIFO reads/writes.

The raster-routing enums (`SePairXsel`, `SePairYsel`, `SePairMap`, `SeXsel`, `SeYsel`, `SeMap`, `ScXsel`, `ScYsel`, `ScMap`, `PkrXsel2`, `PkrXsel`, `PkrYsel`, `PkrMap`, `RbXsel`, `RbYsel`, `RbXsel2`, and `RbMap`) encode tiling and mapping choices for shader engines, scan converters, packers, and render backends. `BinningMode`, `BinEventCntl`, and `CovToShaderSel` expose primitive binning policy and coverage-input selection.

### RMI Beginning

The final part of the chunk starts `RMIPerfSel`. The covered values include no-op/busy/clock/perf-window/event-send selectors, per-VMID and all-VMID invalidation request selectors, invalidation start/finish selectors, UTCL1 translation/permission/request/stall/FIFO events, RB-to-RMI write request selectors by client ID, write-return valid/NACK selectors, and the beginning of RB-to-RMI read request/read-return selectors. The enum does not finish in this chunk, so a complete RMI analysis must include the adjacent chunk.

## Control Flow

There is no runtime control flow in this chunk. The header contributes compile-time constants only.

The effective control flow is indirect: AMDGPU code, shader tooling, and diagnostics choose one of these values, write it into a register or command packet field, and the Vega10 hardware interprets that value. Examples include event packet dispatch using `VGT_EVENT_TYPE`, draw setup using VGT/IA/WD enums, perf counter setup using `*_PERFCOUNT_*` selectors, texture/sampler descriptor programming using `TEX_*` and `TVX_*`, or shader decode/disassembly using `VALUE_SQ_*`.

## State and Persistence Behavior

The header itself stores no state. The state represented by these constants lives in hardware registers, command packets, shader binaries, resource descriptors, and performance-monitor selector registers.

Important state categories include:

- Persistent or semi-persistent register programming, such as raster configuration maps, binning mode, texture cache policy, command processor perf monitor state, and depth/stencil control modes.
- Per-command or per-draw state, such as primitive type, draw source, index size, tessellation topology, event type, and VGT stage routing.
- Shader binary/descriptor encodings, such as SQ opcodes, operand selectors, target encodings, data formats, wait-count partitioning, send-message fields, and special register IDs.
- Diagnostic/performance state, such as which VGT/IA/WD/TA/TD/TCP/TCC/TCA/GRBM/CP/SX/DB/SU/SC/RMI event a hardware counter measures.
- Status or exceptional behavior selected by constants, such as SQ exception IDs, EDC fatal error sources, PRT fault behavior, DFSM flush events, and RMI invalidation events.

Persistence, reset values, and write semantics are not encoded in this enum header. Those semantics come from the corresponding register definitions, command packet formats, firmware conventions, shader ISA documentation, and hardware blocks that consume the numeric values.

## Dependencies and Integration Points

This header depends on the generated AMD register/header naming convention and on the Vega10 hardware ISA/register specification. It is typically included alongside Vega10 register offset and mask headers and consumed by AMDGPU ASIC-specific code.

Likely integration points include:

- Command submission and packet-building paths that emit VGT event types, primitive topology, draw source, index size, and pipeline-stage encodings.
- Shader compiler, disassembler, trap/debug, thread trace, and performance tooling that decode or generate SQ instruction formats and special operand values.
- GPU performance monitoring code that programs selectable counters for VGT, IA, WD, TA, TD, TCP, TCC, TCA, GRBM, CP, SX, DB, SU, SC, and RMI blocks.
- Texture, sampler, image, buffer, and vertex resource descriptor construction paths that use `TEX_*`, `VTX_*`, and `TVX_*` encodings.
- Depth/stencil, color backend, rasterization, binning, and scan-converter setup paths that rely on DB, SX, SU, SC, and raster routing enums.
- Cache, memory-interface, RMI, and VM/TLB diagnostic paths that interpret invalidation, request, stall, return, and error-source selector values.

The constants are ASIC-specific. Nearby AMD generations may share names but not always values or supported selectors. Mixing Vega10 enum values with non-Vega10 register layouts can silently program the wrong hardware behavior.

## Risks

- Numeric drift is high risk. A wrong enum value can select the wrong primitive topology, event packet, opcode, texture format, cache policy, perf counter source, or raster route while still compiling cleanly.
- Perf selector enums are long and repetitive. Copy/paste or generator errors can make counters report unrelated signals, which is hard to catch without hardware validation.
- SQ instruction constants are effectively ISA ABI. Incorrect opcodes, operand ranges, translation offsets, or special-register IDs can break shader disassembly, debug tooling, trap interpretation, or generated shader code.
- Event and flush enums affect synchronization. Misusing values such as cache flush, partial flush, context done, thread trace, or DB/CB invalidation events can cause hangs, stale memory visibility, bad timestamps, or missing trace data.
- Texture/vertex format and sampler constants affect memory interpretation. A bad data format, numeric format, swizzle selector, endian swap, clamp, filter, dimension, or request-size value can produce rendering corruption or memory faults.
- Raster/binning/routing constants encode hardware topology assumptions. Wrong SE/SC/PKR/RB mappings or binning controls can break load distribution, tile/bin behavior, or render backend routing.
- Security and isolation diagnostics can be affected indirectly. RMI, VMID, UTCL1, cache invalidation, and fault-related selector mistakes can hide invalidation failures or mislead debugging of GPU virtual memory faults.
- The chunk starts and ends mid-file. The full per-file report must reconcile prior SQ context before line 15209 and the continuation of `RMIPerfSel` after line 21528.

## Test and Validation Signals

Useful validation is mostly compile-time, shader/packet decode, and hardware integration coverage:

- Build AMDGPU and any Vega10 consumers that include `vega10_enum.h`; this catches missing, renamed, or syntactically invalid enum constants.
- Compare generated enum values against the authoritative Vega10 register/ISA database used to create the header, especially for SQ opcodes, VGT events, texture/vertex formats, and performance selectors.
- Run shader ISA/disassembly tests that cover SOP, SMEM, VOP, VOP3/VOP3P, VINTRP, DS, MUBUF, MTBUF, MIMG, EXP, FLAT/global/scratch, SDWA, DPP, send-message, wait-count, and trap encodings.
- Exercise command-stream tests for primitive topology, draw source, index size, tessellation, GS/HS/DS/VS stage routing, streamout, context done, cache flushes, partial flushes, thread trace events, and pipeline statistics events.
- Validate performance-counter programming for each covered block by selecting representative VGT/IA/WD/TA/TD/TCP/TCC/TCA/GRBM/CP/SX/DB/SU/SC/RMI events and checking that activity changes under targeted workloads.
- Run texture, sampler, image, buffer, and vertex-fetch tests that cover dimensions, formats, numeric formats, component selection, filtering, anisotropy, mip filtering, border color, clamp modes, endian swap, and request sizes.
- Exercise depth/stencil/color backend tests for compare/stencil ops, conservative Z export, Z order, Z mode force, PRT fault behavior, blend optimization, downconversion, and DB/SX counters.
- Validate raster routing and primitive binning on Vega10 hardware using workloads that stress multiple shader engines, scan converters, packers, render backends, PBB/binning modes, and coverage-to-shader selection.
- For the RMI beginning in this chunk, use VM/TLB invalidation and memory-traffic diagnostics to confirm UTCL1 misses/stalls, invalidation request selectors, and RB/RMI request/return selectors report plausible activity.

### subset-b-003510: lines 21529-22532

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h lines 21529-22532

## Scope And Purpose

This chunk is the closing 1,004-line section of AMD's generated Vega10 enum header. It starts in the tail of `RMIPerfSel`, then defines the complete `IH_PERF_SEL`, `SEM_PERF_SEL`, and `SDMA_PERF_SEL` performance selector enums, a fixed `ROM_SIGNATURE` constant, small XDMA swizzle/alpha/pipe-selection enums, and the final `_vega10_ENUM_HEADER` include guard close.

The path sits under a `ceph-client` source mirror, but this file is AMDGPU/DRM hardware metadata rather than Ceph filesystem logic. The values are compile-time names for Vega10 hardware encodings used by register programming, performance counter setup, interrupt diagnostics, SDMA diagnostics, ROM validation paths, and XDMA display/cross-display fields. This chunk defines no functions, global storage, locks, allocation paths, IO helpers, or runtime algorithms.

## Important APIs, Types, And Constants

The exported API is the generated C enum/define namespace. Consumers include this header and pass the numeric constants to register fields or descriptor fields defined by companion AMDGPU register headers.

- `RMIPerfSel` tail: the range continues the RMI performance-selector enum from earlier lines and ends it at `RMI_PERF_SEL_RMI_RB_EARLY_WRACK_NACK3 = 0x000000e7`. The covered tail includes RMI/RB 32-byte read returns by CID and NACK lane, RMI-to-TC write/read request selectors by CID, UTC/UTCL1 request and fault selectors, XNACK/latency/PRT/skid FIFO occupancy and busy selectors, TCIW request/busy/residency selectors, multiple ready-to-send/ready-to-receive handshake selectors across xbar/probegenerator/demux/formatter/consumer/pop/xnack paths, reorder FIFO selectors, and early write-ack selectors.
- `IH_PERF_SEL`: a 512-value interrupt-handler performance selector enum from `IH_PERF_SEL_CYCLE = 0x00000000` through `Reserved511 = 0x000001ff`. It covers IH cycle/idle/input/buffer state, RB0/RB1/RB2 full and overflow events, write-pointer writeback and pointer-wrap events, memory-controller write events, BIF line 0 rising/falling events, 16-VF selector ranges for RB0/RB1/RB2 full/overflow/wptr/rptr/BIF events, interrupt client selectors `CLIENT0_INT` through `CLIENT31_INT`, and large reserved ranges preserving hardware selector positions.
- `SEM_PERF_SEL`: a semaphore/performance-monitor selector enum ending at `SEM_PERF_SEL_ATC_INVALIDATION = 0x000000ad`. It covers cycle/idle, request-signal and request-wait events for SDMA0/SDMA1/UVD/VCE0/ACP/ISP/VCE1/VP8/CPG/CPC immediate engines, CPC1/CPC2 offline engine wait selectors for engines 0-31, CPC1/CPC2 offline poll-wait selectors for engines 0-31, memory-controller read/write request and return selectors, and ATC request/return/XNACK/invalidation selectors.
- `SDMA_PERF_SEL`: an SDMA performance selector enum ending at `SDMA_PERF_SEL_MMHUB_TAG_DELAY_COUNTER = 0x000000ff`. It covers SDMA cycle/idle/register idle, ring-buffer empty/full/pointer-wrap/poll/writeback state, RB/IB command FIFO idle/full state, execution idle and poll-timer expiry, MC read/write idle/count/stall selectors, SEM and interrupt request/response selectors, packet count, copy-engine idle/FIFO/stall selectors, queue source selectors for GFX/RLC0/RLC1/page, context-change and doorbell selectors, bus-arbitration read/write selectors, L1/ATCL2 invalidation and XNACK/ACK selectors, DMA L1/MC send selectors, L1 FIFO and L1-to-L2/MC idle selectors, invalidation wait/enable state, and tag-delay counters at `0xfe` and `0xff`.
- `ROM_SIGNATURE`: fixed SMUIO ROM signature constant `0x0000aa55`, matching the common PCI/option-ROM signature value used to identify a valid GPU ROM image header.
- `ENUM_XDMA_LOCAL_SW_MODE`: three XDMA common local swizzle-mode values: `SW_256B_D = 0x2`, `SW_64KB_D = 0xa`, and `SW_64KB_D_X = 0x1a`.
- `ENUM_XDMA_SLV_ALPHA_POSITION` and `ENUM_XDMA_MSTR_ALPHA_POSITION`: four alpha-byte lane selections each, mapping alpha to bits `7:0`, `15:8`, `23:16`, or `31:24`.
- `ENUM_XDMA_MSTR_VSYNC_GSL_CHECK_SEL`: six XDMA master pipe selectors, `PIPE0` through `PIPE5`, used to select which display pipe participates in the VSYNC/GSL check.

## Control Flow And Runtime Behavior

There is no local control flow in this chunk. It is declarative hardware metadata:

1. AMDGPU code includes `vega10_enum.h` along with Vega10 register offset and bitfield headers.
2. Driver logic chooses a selector or field value based on the block being programmed: RMI/IH/SEM/SDMA performance counter programming, interrupt diagnostics, SDMA queue diagnostics, ROM signature checks, or XDMA display setup.
3. The chosen enum value is written into a hardware register field, command/register packet field, or firmware-facing structure by code outside this header.
4. The GPU hardware interprets the numeric value. The C enum name is only a source-level alias.

The file itself performs no validation, range checking, fallback selection, or reserved-value filtering. Any such policy must be implemented by the consumer that picks these values.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. Its constants describe values that can select or affect stateful hardware behavior once written elsewhere.

The state represented by the selectors can persist in GPU register fields, performance counter mux configuration, interrupt-handler diagnostic configuration, SDMA performance monitor state, ROM parsing decisions, and XDMA display-control fields until overwritten, reset, or lost during a GPU reset or power-management transition. Reserved enum slots are also part of the persistent hardware contract because they preserve selector numbering even though they should not be selected as usable events.

## Dependencies And Integration Points

This range depends on the earlier parts of `vega10_enum.h` for the include guard, license block, GL aliases, and the beginning of `RMIPerfSel`. It integrates with companion generated Vega10 headers that define register addresses, register field masks, and shifts. The enum values are meaningful only when paired with the correct Vega10 hardware block and register field width.

Likely integration points include:

- AMDGPU performance counter setup for RMI, IH, SEM, and SDMA blocks.
- IH setup and diagnostics around ring-buffer fullness, overflow, write-pointer writeback, pointer wrapping, BIF line events, client interrupt lines, and SR-IOV/VF-specific event attribution.
- SEM diagnostics for synchronization request/wait behavior from SDMA, media engines, command processor paths, memory controller, and ATC.
- SDMA queue/ring/copy-engine diagnostics, context-change tracking, doorbell activity, MC/L1/ATCL2 traffic, and XNACK/invalidation behavior.
- ROM handling code that checks the `0xaa55` option-ROM signature before consuming ROM contents.
- XDMA master/slave display paths that need stable numeric values for swizzle mode, alpha lane position, and VSYNC/GSL pipe selection.

Nearby generated headers for other ASIC generations, such as `navi10_enum.h`, `soc21_enum.h`, `soc24_enum.h`, and `include/asic_reg/oss/*_enum.h`, provide useful parity references for naming and selector families. They are not drop-in substitutes because selector availability, reserved holes, and numeric assignments differ across GPU generations.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A single numeric change can compile cleanly while selecting the wrong hardware event or field value at runtime.
- The work item begins in the middle of `RMIPerfSel`; the merge lane must combine this with prior chunks before making complete claims about the full RMI selector enum.
- `IH_PERF_SEL` contains many `Reserved*` entries up to `0x1ff`. These reserve selector numbers and should not be treated as valid events unless hardware documentation explicitly says otherwise.
- `SDMA_PERF_SEL` has intentional gaps, including missing values around `0x16`, `0x17`, `0x24`, `0x2c`, `0x2d`, and `0x2f`/`0x30`, plus a jump from `0x5e` to `0xfe`. Code that assumes dense iteration over all values can select undefined hardware events.
- Repetitive VF-indexed IH values are easy to misread or generate incorrectly. RB0/RB1/RB2 groups have similar names but different selector ranges, and an off-by-one index can misattribute interrupt or virtualization behavior.
- SEM CPC offline engine selectors repeat across CPC1/CPC2, wait versus poll-wait, and engine indices 0-31. A wrong family still produces a legal integer but records the wrong diagnostic signal.
- SDMA selector names overlap conceptually with SEM and IH selectors. The enum type does not protect consumers that pass values as raw integers to register helpers.
- XDMA alpha-position enums use the same member suffixes for slave and master blocks but are distinct typedefs. Mixing them may compile in raw integer code while programming the wrong block's field.
- `ROM_SIGNATURE` only identifies the leading ROM signature value; it is not a complete ROM validation policy. Consumers still need bounds checks, table validation, checksum handling where applicable, and device-specific parsing.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU/Vega10 code that includes `vega10_enum.h` to catch duplicate enum names, malformed typedefs, missing include-guard closure, or syntax regressions.
- Mechanically compare lines 21529-22532 against the authoritative Vega10 register database or generated header source, especially `RMIPerfSel` ending at `0xe7`, `IH_PERF_SEL` ending at `0x1ff`, `SEM_PERF_SEL` ending at `0xad`, and `SDMA_PERF_SEL` tag-delay counters at `0xfe` and `0xff`.
- Exercise performance counter selection for RMI, IH, SEM, and SDMA blocks and confirm counters increment under matching workloads: SDMA copies, command processor semaphore waits, memory-controller traffic, ATC invalidation/XNACK behavior, interrupt storms, ring-buffer full/overflow conditions, and VF/PF interrupt activity.
- Validate SR-IOV/VF scenarios where IH per-VF selector ranges are expected to attribute events to the correct virtual function and ring buffer.
- Test SDMA ring-buffer and copy-engine stress paths that trigger RB empty/full, pointer wrap, doorbell, context-change, MC/L1 traffic, invalidation, XNACK, and tag-delay observations.
- Validate ROM parsing with known-good and malformed ROM images to ensure `ROM_SIGNATURE` is only the first acceptance gate.
- Exercise XDMA display paths that use alpha-position, local swizzle mode, and VSYNC/GSL pipe-selection fields, watching for swapped alpha channels, wrong tiling/swizzle behavior, or pipe-selection mismatches.
- Watch for silent failures: bogus performance counter readings, counters stuck at zero, misattributed VF events, missed or overflowing interrupts, SDMA queue stalls, XNACK/invalidation anomalies, ROM parse errors, and display corruption in XDMA paths.

## Cross-Chunk Notes

This chunk closes `vega10_enum.h` with `#endif /*_vega10_ENUM_HEADER*/`. There is no following enum content in this source file after line 22532. The merge/reconciliation lane should join this with earlier `vega10_enum.h` chunks before producing the final per-file research document.
