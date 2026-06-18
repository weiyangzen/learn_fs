# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003496`: lines 1-8611, `Docs/researches/chunks/subset-b-003496_research.md`
- `subset-b-003497`: lines 8612-15193, `Docs/researches/chunks/subset-b-003497_research.md`
- `subset-b-003498`: lines 15194-21030, `Docs/researches/chunks/subset-b-003498_research.md`
- `subset-b-003499`: lines 21031-22477, `Docs/researches/chunks/subset-b-003499_research.md`

## Chunk Research

### subset-b-003496: lines 1-8611

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h lines 1-8611

## Scope And Purpose

This chunk is the opening 8,611 lines of AMDGPU's generated `soc21_enum.h` header. It starts the `_soc21_ENUM_HEADER` guard, adds non-driver-build GL blend-name compatibility aliases, and then defines a large set of `typedef enum` constants for SOC21/GC/DCN hardware register fields.

The source is data-only C ABI material. It does not implement functions, structs, storage, or executable logic. Its purpose is to give driver code symbolic names for hardware-programmed numeric field encodings across generic chip blocks, SDMA, memory/cache policy, display color/scaler/hub/plane/timing blocks, clock generation, DisplayPort/HDMI/TMDS link encoders, AUX/DDC sideband controllers, display I/O memory power states, audio formatting, and the beginning of HPO/DP stream-mapper definitions.

The chunk ends at the `DP_STREAM_MAPPER Enums` section marker, before the first stream-mapper enum body appears. Later chunks continue the same generated enum catalog for the rest of the file.

## Important APIs, Types, And Constants

The public API in this range is a flat set of named C enum types whose values are fixed hardware encodings. The enums are consumed by code that writes or decodes SOC21 register fields; they should be treated as part of the GPU hardware ABI rather than as ordinary software preference values.

The header prologue defines GL-style aliases such as `GL__ZERO`, `GL__ONE`, `GL__SRC_COLOR`, and related blend terms when `_DRIVER_BUILD` is not set and `GL_ZERO` is not already defined. These map to `BLEND_*` symbols defined elsewhere and are the only preprocessor compatibility names in this chunk.

The generic chip and memory/cache section covers:

- DSM error-injection and data-selection controls: `DSM_DATA_SEL`, `DSM_ENABLE_ERROR_INJECT`, `DSM_SELECT_INJECT_DELAY`, and `DSM_SINGLE_WRITE`.
- Cache and memory policies: `GL0V_CACHE_POLICIES`, `GL1_CACHE_POLICIES`, `GL1_CACHE_STORE_POLICIES`, `GL2_CACHE_POLICIES`, `TCC_CACHE_POLICIES`, `ReadPolicy`, `WritePolicy`, `MTYPE`, and `TCC_MTYPE`.
- VM/TLB request and fault encodings: `GATCL1RequestType`, `UTCL0FaultType`, `UTCL0RequestType`, `UTCL1FaultType`, `UTCL1RequestType`, and `VMEMCMD_RETURN_ORDER`.
- Performance monitor modes: `PERFMON_COUNTER_MODE` and `PERFMON_SPM_MODE`.
- Large SDMA performance selector tables: `SDMA_PERFMON_SEL` and `SDMA_PERF_SEL`, naming idle, ring-buffer, indirect-buffer, semaphore, interrupt, copy-engine, context-change, doorbell, cache-invalidation, UTCL2, metadata, TLBI, GCR, and channel-return events.

The display-pipe color and scaler groups define register field values for the front of the DCN processing path:

- `CNVC_CFG` names bypass, enable, pending, coefficient-format, pre-CSC, pre-degamma, channel crossbar, color keyer, expansion, denorm, and the broad `SURFACE_PIXEL_FORMAT` table. The pixel-format enum spans ARGB/RGBA variants, packed and planar YCbCr, 10/12/16-bit formats, float/fixed formats, RGBE, and mono formats.
- `CNVC_CUR` and `CURSOR` cover cursor enable/mode/ROM/expansion/clamp/pending controls, line chunking, pitch, request mode, snooping, stereo, TMZ, system-vs-guest addressing, and rotation/mirroring bypass.
- `DSCL` covers scaler mode selection, coefficient RAM selection, line-buffer memory config, boundary behavior, alpha/chroma coefficient selection, auto-calibration, sharpness, and output-buffer bypass/width/full-buffer controls.
- `CM`, `MPCC_OGAM`, and `MPCC_MCM` define LUT and color-management choices: 3D LUT width and size, RAM selection, gamma/PWL modes, gamut-remap and CSC coefficient formats, LUT segment counts, readback color selection, debug read, and memory-power states.

The display hub and request/return path groups describe plane fetch and memory behavior:

- `HUBP` covers VM page/chunk/group sizes, PTE row height, swath height, rotation, mirror, MALL use, blanking, VTG selection, soft reset, TTU disable, VREADY relation to VSYNC, and legacy pipe interleave.
- `HUBPREQ` covers DFQ sizing, metadata/data expansion, flip rate, interrupt masks, urgent flush behavior, row TTU mode, DCC mode/independent block encodings, surface flip behavior, flip stereo selection, TMZ, and update lock.
- `HUBPRET` covers return-path crossbars for alpha/Y/CB/CR data, detile buffer packer, memory power disable/force/status, pipe interrupt mask/type controls, and pixel CDC light-sleep.
- `HUBBUB_SDPIF` exposes `RESPONSE_STATUS` values such as OKAY, EXOKAY, SLVERR, DECERR, protocol violation, transaction error, timeout, and CRS. `HUBBUB_RET_PATH` provides DCHUBBUB memory light-sleep/deep-sleep/shutdown encodings.

The timing, composition, CRC, and output-pixel blocks cover:

- `DPP_TOP` and `DC_PERFMON` CRC source selectors, test-clock selectors, eight repeated perf-counter state selectors, counted-value selection, increment modes, run/count-off modes, interrupt modes, and global/local state routing.
- `MPC_CFG`, `MPC_OCSC`, and `MPCC` update locks, MPC debug-bus routing, CRC source/mode/stereo/interlace controls, output CSC and denorm controls, MPCC alpha blending, layer/pass-through modes, stereo/subsample modes, background color bit depth, and output rate-control disable.
- `DPG`, `FMT`, `OPPBUF`, `OPP_PIPE`, `OPP_PIPE_CRC`, `OPP_TOP`, and `DSCRM` test-pattern generation, bit-depth conversion, truncation, spatial/temporal dithering, pixel encoding/subsampling, clamp formats, formatter/OPP memory power states, OPP segmentation, OPP CRC behavior, debug-bus selectors, OPP clock-gating status, and display-stream scrambling enable.
- `OTG` and `OPTC_MISC` define master/global/update locks, interlace/stereo modes, CRC routing, double-buffer timing, dynamic refresh-rate event modes, force-count-now triggers, manual and external flow-control sources, trigger A/B source and polarity selectors, vertical interrupt controls, static-screen overrides, V-total min/max event handling, GSL timing source selection, and sync polarity/timing division.

The display microcontroller, interrupt, and clock-generation sections include:

- `DMCUB`, `RBBMIF`, `IHC`, and `DMU_MISC` interrupt type/destination/status, invalid register-access cause, DC/GPU timer read-window selectors, timer start-position selectors, SMU interrupt controls, and DMU clock status.
- `DCCG` audio DTO source selection, deep-color DTO ratios, clock-branch resets, debug routing, FIFO error detection, performance run/HSYNC/VSYNC starts, global memory-power request disable, display clock ramp status, DP reference clock source, despread, jitter removal, DVO clock phase/skew controls, HDMI stream/character clock selection, PHY/symbol clock force controls, pixel-rate clock sources, PLL soft reset, timebase clock selection, test-clock division, VSYNC counter controls, and XTAL reference selection.

The link, sideband, and display I/O sections include:

- `HPD` interrupt ack/polarity values.
- `DP` and `DIG` values for DP PHY 8b/10b reset/disparity, scrambler controls, lane CRC/PRBS/test patterns, FEC, fast training, HBR2 patterns, DSC mode, embedded-panel mode, link-training complete/switch controls, MST/MSE/SAT fields, MSO link count, pixel encoding, secondary-data packet controls, stream-disable deferral/ack/mask, VBID polarity, DIG front/back-end routing, HPD selection, digital bypass, FIFO modes/errors, output CRC, test patterns, Dolby Vision enable, HDMI packet/ACR/audio/generic/ISRC/metadata/null packet controls, keepout, deep color, scrambling, TMDS color/test/modulation/data selection, HPD masking, and TMDS PLL/pad clock controls.
- `DP_AUX` values for AUX arbitration priority/status, HPD binding, test mode, PHY wake priority, RX/TX threshold and timing windows, GTC sync controls, error/interrupt ack bits, reset/done status, software-go/LS-read triggers, and timeout/precharge multipliers.
- `DOUT_I2C` values for DDC/I2C arbitration, priority, controller reset, software status reset, DDC line selection, transaction count, transfer start/stop, NACK behavior, EDID detect/reset, pad drive controls, speed threshold, and read-request interrupt type.
- `DIO_MISC`, `DME`, `VPG`, `AFMT`, and `HPO_TOP` values for DIO clock gating, DAC/TMDS muxes, DIO debug block selection, DIO/DME/VPG/AFMT memory power modes, metadata stream/HUBP selection, AFMT audio CRC and packet-source controls, audio layout override, AZ stream selection, HDMI max-packet send, audio-info source, audio interrupt mask, ACP source/type, and HPO top-level clock gating/test-clock selection.

## Control Flow

There is no C control flow in this chunk. Runtime flow is created by the AMDGPU driver paths that include this generated header together with SOC21 register offset and shift/mask headers, then program MMIO fields in a hardware-defined order.

The most important control-flow pattern is register-programming sequencing:

1. Driver code chooses symbolic enum values from this header according to display mode, plane format, memory layout, link type, power state, or diagnostic operation.
2. SOC15/DCN register helpers combine those enum values with generated field masks and shifts from companion headers.
3. Hardware observes the resulting field values and changes state in block-specific state machines such as HUBP fetch, MPCC blending, OTG timing, DCCG clock generation, DP link training, AUX/DDC transactions, or AFMT packet generation.
4. Driver code may poll or acknowledge status fields represented by matching enum values, for example reset-done, stream-disable ack, AUX errors, HPD/DOUT interrupts, CRC pending, DMDATA underflow, or display clock ramp completion.

Several enum families encode synchronization and double-buffer semantics rather than immediate behavior. Examples include `SURFACE_UPDATE_LOCK`, `MPC_CFG_*_VUPDATE_LOCK_SET`, `OTG_UPDATE_LOCK_OTG_UPDATE_LOCK`, `MASTER_UPDATE_LOCK_*`, `OTG_DOUBLE_BUFFER_CONTROL_*`, `DP_VID_M_N_DOUBLE_BUFFER_MODE`, and flip/update/stereo field selectors. Code that writes these fields must respect the surrounding vertical-update, frame-start, or lock/unlock sequence defined by DCN hardware and by the driver block implementation.

## State And Persistence Behavior

The enums themselves are compile-time constants and persist only in compiled code. The state they describe lives in SOC21 hardware registers. Those registers control durable block state until overwritten, reset, or lost through power transitions.

Stateful hardware areas represented in this chunk include:

- Plane and memory-fetch state: surface formats, DCC, TMZ, cursor address mode, VM page/chunk sizing, row height, swath height, MALL use, flip mode, update lock, and DMDATA repeat/update/underflow status.
- Color and blending state: CNVC/CM/MPCC/OGAM/MCM LUT selection, gamut/CSC coefficient format, alpha mode, denorm, dithering, FMT clamp, pixel encoding, and OPP CRC configuration.
- Timing state: OTG master enable, interlace/stereo, trigger selection, DRR/V-total min/max controls, vertical interrupt configuration, global/update locks, and GSL synchronization.
- Clock and power state: DCCG source selectors, clock force/reset/gating fields, display clock ramp status, memory power force/dis/selection fields for FMT/HUBPRET/DCHUBBUB/MPCC_MCM/DIO/DME/VPG/AFMT, and HPO top clock gating.
- Link and sideband state: DP training/FEC/DSC/MST/MSE/secondary-data settings, HDMI/TMDS packet and PLL controls, HPD interrupt polarity/ack, AUX arbitration/reset/error state, DOUT I2C transaction state, and AFMT audio-source/packet state.

Register state is normally reinitialized during device bring-up, display mode set, link training, plane updates, suspend/resume, GPU reset, DCN block reset, and power-gating transitions. This header does not save or restore state; it only names the encodings that the active SOC21 driver generation uses to do so.

## Dependencies And Integration Points

This header is a generated dependency of the AMDGPU SOC21/DCN register interface under `drivers/gpu/drm/amd/include`. It is expected to be used alongside matching SOC21 offset and shift/mask headers; enum values alone do not identify register addresses or bit positions.

Likely integration points include:

- AMD Display Core DCN resource, hub, plane, scaler, color, MPC/MPCC, OPP, OTG/OPTC, DIO, DCCG, AUX, I2C, HPD, HDMI/DP, AFMT, and DMCUB code.
- SOC15-style register access helpers that write fields by mask/shift using generated register constants.
- Display mode-setting and atomic-update paths that translate DRM plane formats, cursor properties, color-management state, link capabilities, audio settings, and connector/HPD state into hardware field encodings.
- Debugfs, interrupt, CRC capture, performance-monitor, error reporting, and bring-up diagnostics that select or decode named status, debug-bus, or performance-counter values.
- Firmware-facing or microcontroller-facing flows involving DMCUB, DMU/SMU interrupts, timer snapshots, and display clock/power coordination.

The numeric values are generation-specific. Similar enum names can appear in other AMDGPU generation headers, but they must not be assumed interchangeable without checking the matching register definitions and ASIC family.

## Risks And Edge Cases

The primary risk is accidental ABI drift. A one-bit enum value change can program a different hardware mode while still compiling cleanly. Because many names are human-readable but hardware-specific, review must compare changes to generated register specs or vendor drops, not infer correctness from neighboring constants.

Many enums contain reserved values, sparse layouts, or non-obvious polarity. Examples include cache policies with bypass/stream/no-allocate variants, `SURFACE_PIXEL_FORMAT` gaps, DP/TMDS/HDMI reserved encodings, `DIO_DBG_BLOCK_SEL` sparse debug IDs, `DMU_DC_GPU_TIMER_READ_SELECT` reserved windows, `OTG_TRIGA/B_*` large source-selector tables, and `DP_DPHY_HBR2_PATTERN_CONTROL_MODE` with a non-contiguous `0x6` value. Manual compaction or renumbering would be wrong.

Some field names encode negative logic or inverted status. Examples include memory-power "disable" fields, clock-gating disable fields, force-disable-clock fields, reset/done pairs, ack/clear values, mask/unmask fields, and status fields where `0` is enabled or active depending on the hardware definition. Callers should use the symbolic names rather than assuming `0` always means disabled or false.

Several generated names contain misspellings or awkward wording, such as `SURFACE_INUSE_RAED_NO_LATCH`, `FMT_CONTROL_SUBSAMPLING_MOME_*`, `DPHY_8B10B_RESETET`, `HDMI_DEFAULT_PAHSE`, and `DP_AUX_GTC_SYNC_CONTROL_OFFSET_CALC_MAX_ATTEMPT__*_ATTAMPS`. These are still exported identifiers. Renaming them would break users unless all references and generation sources are updated together.

Duplicated-looking enum families are not always interchangeable. `CM_*`, `CMC_*`, `MPCC_OGAM_*`, and `MPCC_MCM_*` describe related LUT/color blocks with different prefixes and sometimes different modes. Likewise, DP, DIG, TMDS, AUX, DOUT I2C, and AFMT controls share enable/ack/reset idioms but target different registers and state machines.

Because this chunk stops at a section boundary before `DP_STREAM_MAPPER` contents, file-level reconciliation must merge this report with later chunks before drawing whole-file conclusions about the complete SOC21 enum surface.

## Test Signals

There are no direct unit tests for this enum-only header. Useful validation signals are compile-time and hardware-integration oriented:

- A kernel build with AMDGPU DCN/SOC21 support enabled catches removed, renamed, or syntactically invalid enum identifiers.
- Static reference checks can verify that generated enum names used by DCN display code still resolve and that no local code duplicates raw numeric encodings where a named enum should be used.
- Display bring-up and atomic mode-setting on SOC21 hardware should cover plane format selection, cursor modes, scaler/color/LUT programming, MPCC blending, OPP/FMT output conversion, OTG timing, and DCCG clock source programming.
- Link tests should cover DP SST/MST, eDP, DSC/FEC where supported, HDMI/TMDS deep color, audio packet generation, HPD connect/disconnect interrupts, AUX transfers, DDC/EDID reads, and error/ack paths.
- Power-management tests should cover suspend/resume, DCN block reset, GPU reset, clock gating, memory light/deep sleep, shutdown force modes, MALL/static-screen behavior, and display clock ramp completion.
- Diagnostic tests should exercise CRC capture, performance counters, debug-bus selection, DMDATA underflow/clear, AUX/I2C error ack, and invalid register-access status decoding.

### subset-b-003497: lines 8612-15193

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h lines 8612-15193

## Scope And Purpose

This chunk is a large generated enum slice from the AMDGPU SOC21 hardware-description header. It exports symbolic C enum values for SOC21 register fields across display output, HDMI/DP audio and video encoders, Azalia/HDA audio, DSC compression, DWB writeback, RDPCS/PHY pipe controls, color-buffer and scan-converter graphics pipeline state, transaction/cache opcodes, RLC control, and the beginning of SPI performance-counter selectors.

The file is data-only. It has no functions, structs with storage, global variables, or executable control flow. Its purpose is to keep register programming code, debug tooling, and generated register metadata aligned with hardware-defined numeric values instead of scattering raw constants through driver code. The range starts at the complete `DP_STREAM_MAPPER_DP_STREAM_LINK_TARGET` enum immediately after the preceding `HPO_TOP` section. The requested line range ends inside `SPI_PERFCNT_SEL`; the enum continues beyond line 15193 through `SPI_PERF_BUSY` at line 15271 and closes at line 15272, so this chunk documents only the selector values present through `SPI_PERF_RA_ACCUM3_SIMD_FULL_GS`.

## Important APIs, Types, And Functions

The exported API is a collection of `typedef enum` definitions. Consumers can include `soc21_enum.h` and use names such as `TB_ENABLE`, `DP_SYM32_ENC_COMPONENT_DEPTH_10BPC`, `DSCC_ENABLE_ENUM_ENABLED`, `PHY_DP_RATE_5P40`, `BLEND_SRC_ALPHA`, `TC_OP_ATOMIC_ADD_RTN_64`, or `RLC_DOORBELL_MODE_ENABLE_PF_VF` when composing or decoding register fields.

Display and link-output enums cover:

- `DP_STREAM_MAPPER_DP_STREAM_LINK_TARGET` for selecting DP stream mapper link 0, link 1, or reserved value.
- `HDMI_STREAM_ENC_*` for HDMI stream encoder enable/reset, double-buffer disable, DSC mode, ODM combine mode, overflow/underflow status, programmable overwrite level, pixel encoding, read-clock source, and stream-active status.
- `HDMI_TB_ENC_*` and `INPUT_FIFO_ERROR_TYPE` for HDMI transport-block enable/reset, pixel encoding, deep-color depth, DSC mode, audio clock regeneration packet policy, ACP/audio-info/general-control/generic/ISRC/metadata packet send or continuous modes, CRC tap/type, AVMUTE, packet line reference, sync phase, borrow-buffer modes, and borrow-buffer memory power state.
- `DP_STREAM_ENC_*`, `ENUM_DP_SYM32_ENC_*`, and `ENUM_DP_DPHY_SYM32_*` for DP stream encoder reset/active/error state, DP symbol encoder audio mute, secondary data packet priority and scheduling, generic stream packet pending/deadline flags, component depth, pixel encoding, compressed/uncompressed format, memory power, CRC validity, DPHY CRC windows/taps, 8b/10b versus 128b/132b mode, lane count, link training/test-pattern selection, PRBS choice, stream override, SAT update, rate update, reset, and enabled/idle status.

Audio, GPIO, panel, and codec enums cover:

- `APG_*` values for audio CRC channel and mode, debug ACP packet type, audio DTO base/divisor/multiple, debug mux selection, DP ASP channel override, APG packet-source overrides, ramp sign, and APG memory power control.
- `DCIO_*` and `DCIOCHIP_*` values for display clock/test-clock muxing, async debug muxes, DCRXPHY/DSYNC soft reset, generic GPIO source selection, UNIPHY clock selection and lane crossbar/inversion, hotplug masks, GPU timer read/start positions, external VSYNC muxing, genlock/swaplock GSL masks, DPCS interrupt mask/type, AUX/I2C analog tuning, pad mode, polarity inversion, GPIO masks, HPD selection, pull-down enable, and reference-clock source.
- `PWRSEQ_*` values for backlight PWM enable/fractional enable, frame-start update, lock/readback behavior, GPIO masks, panel backlight/digital/sync polarity, target panel power state, and panel vary-backlight override.
- `AZ*`, `AZALIA_*`, `OUTPUT_STREAM_DESCRIPTOR_*`, and stream synchronization enums for HDA/Azalia CORB/RIRB sizes and reset, global controller reset/flush/status, unsolicited response acceptance, immediate-command status, stream interrupt/error/run/reset/priority fields, stream 0 through 15 synchronization bits, converter format bits per sample/channel count/base divisor/base multiple/base rate/stream type, digital converter flags, pin audio descriptor formats, multichannel mute/enable modes, HBR capability, endpoint/widget capabilities, codec reset, and latency counter control.

Compression, writeback, and PHY pipe enums cover:

- `DSCC_*`, `DSCCIF_*`, `DSC_TOP` generic `ENABLE_ENUM`/`CLOCK_GATING_DISABLE_ENUM`/`TEST_CLOCK_MUX_SELECT_ENUM`, and `POWER_STATE_ENUM` for DSC bits per component, DSC version fields, enable/reset, line-buffer depth, input pixel format, and memory power.
- `DWB_TOP` and `DWBCP` enums for writeback CRC source/continuous mode, overflow type and interrupt type, debug source, memory power, test clock, frame-capture eye/rate/stereo polarity, gamut remap coefficient format and mode, output gamma LUT segment count, LUT host/read color/debug configuration, OGAM mode/select, and PWL disable.
- `RDPCSPIPE_*`, `RDPCS_PIPE_*`, and `RPDCSPIPE_*` values for RDPCS pipe and SRAM clocks, FIFO enable/lane enable/status, soft resets, APB/message-bus and DP-alt interrupt masks, encoder type (`HDMI_TMDS_OR_DP_8B10B`, `DP_128B132B`), pack mode, PHY CR mux/parameter selection, reference range, SRAM load/init done, DP/HDMI PLL dividers, DP termination, detect-RX result, DP TX rate/width/P-state, PHY interface width, PHY link rate, alternate reference clock, test clock selectors, lane pack ordering, bit order reversal, and RDPCS memory power state/force.

Graphics, cache, and command/control enums cover:

- `GDS_PERFCOUNT_SELECT` for GDS/GWS/OA performance events, including request, grant, return, bypass, conflict, and write-completion selectors.
- `CB` enums such as `BlendOp`, `BlendOpt`, `CBMode`, `CBPerfClearFilterSel`, `CBPerfOpFilterSel`, `CBPerfSel`, `CBRamList`, `CmaskCode`, `CombFunc`, `MemArbMode`, and `SourceFormat`. These describe color blend factors, blend optimizations, color-buffer mode, performance filter fields, hundreds of CB perf selectors, color-buffer RAM arrays, CMASK encodings, combiner math, arbitration mode, and color export source format.
- `SC` enums such as `BinEventCntl`, `BinMapMode`, `BinSizeExtend`, `BinningMode`, `CovToShaderSel`, raster config map/x/y selectors for packer/RB/SC/SE/SE-pair routing, `ScUncertaintyRegion*`, `VRSCombinerModeSC`, `VRSrate`, and `SC_PERFCNT_SEL`. `SC_PERFCNT_SEL` is a very large selector table for scan-converter, binning, quad, tile, VRS, primitive, and backend stall/valid/busy events.
- `TC_EA_CID`, `TC_NACKS`, `TC_OP`, and `TC_OP_MASKS` for transaction/cache client IDs, no-fault/page-fault/protection-fault/data-error NACK reasons, 32-bit and 64-bit read/write/atomic/cache-invalidate opcodes, and opcode class masks (`TC_OP_MASK_FLUSH_DENROM`, `TC_OP_MASK_64`, `TC_OP_MASK_NO_RTN`).
- `GL2_EA_CID`, `GL2_NACKS`, `GL2_OP`, and `GL2_OP_MASKS` for GL2 client IDs, fault reason values, GL2 operation encodings, and analogous opcode masks.
- `RLC_DOORBELL_MODE`, `RLC_PERFCOUNTER_SEL`, `RLC_PERFMON_STATE`, and `RSPM_CMD` for RLC doorbell exposure modes, RLC perf event selection, perf monitor reset/enable/disable/rollover state, and RSPM commands such as idle, calibrate, SPM start/stop, perf reset/sample, profile start/stop, and forced sample.
- `SPI` begins with `CLKGATE_BASE_MODE`, `CLKGATE_SM_MODE`, `SPI_FOG_MODE`, `SPI_LB_WAVES_SELECT`, and the first part of `SPI_PERFCNT_SEL`. The visible `SPI_PERFCNT_SEL` values cover GS/HS/CS/PS wave, busy, crawler stall, persistent-update, dealloc, wave-group, resource-allocation stall/full/lock, accumulator SIMD-full, and export-arbiter selectors up to the chunk boundary.

## Control Flow

There is no direct control flow in this chunk. Runtime behavior is created by code that includes this header alongside SOC21 offset and shift/mask headers, then writes enum values into register fields or decodes register values for diagnostics.

A typical runtime path is:

1. ASIC-specific driver code selects SOC21 register offsets and masks for a display, audio, graphics, cache, or RLC register.
2. The code chooses one of these enum constants as the semantic value for a field, or compares a field value against one of these constants after reading hardware state.
3. Register helper macros write the encoded value to MMIO, indirect, or indexed registers, or debug/perf tooling exposes the decoded value to logs and counters.
4. Hardware interprets the numeric value as a mode, status, opcode, selector, packet policy, or performance event.

Because the header is generated field vocabulary, the ordering and numeric assignments are the control contract. For example, `TC_OP` uses bit-pattern families where `0x20` selects 64-bit/alternate width behavior and `0x40` selects no-return variants, while `TC_OP_MASKS` names these class bits. `SC_PERFCNT_SEL`, `CBPerfSel`, `GDS_PERFCOUNT_SELECT`, and `SPI_PERFCNT_SEL` are selector spaces, not bitmasks; their sparse holes and reserved values must be preserved.

## State And Persistence Behavior

The enum definitions themselves hold no mutable state and persist only as compile-time constants. The state they describe lives in SOC21 hardware registers, FIFOs, SRAMs, packet generators, counters, status latches, debug muxes, and power/reset controls.

Some values represent transient status (`*_PENDING`, `*_OVERFLOW_OCCURRED`, FIFO empty/full, reset status, stream active, immediate command busy). Others represent sticky or software-selected configuration that remains in hardware until reset, power transition, or a later register write changes it (encoder enable, clock gating, memory power force, panel target state, PHY rate, lane map, blend mode, perf selector). Performance selector enums determine what hardware counters observe; counter contents and latched status are separate register state in companion offset/mask headers.

Power and reset enums are particularly stateful in the hardware sense. Display/audio memory power force values distinguish no-force, light sleep, deep sleep, and shutdown requests; reset enums assert/deassert block resets; panel power sequencing values select target LCD/backlight state. Driver suspend/resume, GPU reset, display mode set, audio stream setup, and power-gating flows must restore or reprogram the relevant registers rather than assuming enum defaults imply live hardware defaults.

## Dependencies And Integration Points

This header depends only on the surrounding C preprocessor guard and earlier compatibility macros in `soc21_enum.h`; this chunk introduces no include dependencies of its own. The direct in-tree include found for this header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c`, and many other generated SOC21 register files refer conceptually to these values through matching offsets and masks.

Important companion files are SOC21 register offset and shift/mask headers under `drivers/gpu/drm/amd/include/asic_reg/`, especially DCN/DPCS/RDPCS/Azalia/display headers for the display and audio enums, and GFX/GC register headers for CB/SC/TC/GL2/RLC/SPI selectors. Nearby generation enum headers (`navi10_enum.h`, `vega10_enum.h`, `soc24_enum.h`, and older `asic_reg/gca/gfx_*_enum.h`) provide useful parity references, but they are not drop-in replacements because reserved values and selector additions can differ by ASIC family.

The integration surface is broad:

- DC display mode set, link encoder, stream encoder, DSC, DWB, HPO/RDPCS/PHY, audio packet, and panel-power code can use the display-side values.
- HDA/Azalia controller and codec endpoint code can use the audio stream, converter, pin, widget capability, CORB/RIRB, and unsolicited-response values.
- Graphics debug, register dumps, performance counter setup, KFD/queue manager code, and low-level GFX bring-up can use CB/SC/GDS/SPI/RLC selectors.
- VM, cache, fault handling, debug, and diagnostics can use TC/GL2 client IDs, operation encodings, and NACK reason values when interpreting hardware logs or programming debug filters.

## Risks And Edge Cases

The main risk is treating this generated enum header as ordinary source that can be hand-edited safely. A one-value shift in a selector table can redirect performance counters, misconfigure display/audio hardware, choose the wrong PHY rate, or make fault/opcode decoding misleading.

Several enum families are selector spaces with sparse or reserved values rather than dense application enums. `CBPerfSel`, `SC_PERFCNT_SEL`, `GDS_PERFCOUNT_SELECT`, and the partial `SPI_PERFCNT_SEL` have intentional gaps and reserved names. Review should compare changes against the generated hardware source or register specification, not infer the next value by local pattern.

The chunk boundary is an edge case. `SPI_PERFCNT_SEL` is incomplete in the requested line range: it starts at line 15041 and continues after line 15193. Any final per-file report should merge this with the adjacent chunk before describing the complete SPI selector table. Conversely, all earlier enums in this chunk are complete and can be reasoned about directly.

Another risk is name reuse across ASIC generations and blocks. Common names such as `BlendOp`, `TC_OP_MASKS`, `RLC_DOORBELL_MODE`, and `SPI_PERFCNT_SEL` exist in other enum headers. Including multiple generation headers in the same translation unit can create typedef or enumerator collisions. Code should include the enum header matching the active register-generation namespace and avoid mixing SOC21 values with SOC24, Navi10, Vega10, or GCA-specific definitions unless the build structure already isolates them.

Some spelling quirks are part of the exported ABI vocabulary, for example `HDMI_TB_ENC_DEFAULT_PAHSE`, `RPDCSPIPE_CNTL_TX_LANE_BIT_ORDER_REVERSE_BEFORE_PACK`, and `TC_OP_MASK_FLUSH_DENROM`. These should not be corrected casually because users may reference the generated names exactly.

## Test Signals

There are no unit tests for this data-only header. Useful validation is build, static, and hardware oriented:

- A kernel build that includes SOC21 display, audio, GFX, KFD, and perf/debug paths should catch missing typedefs or renamed enumerators.
- Register programming tests should verify HDMI/DP stream enable/reset, DSC enable, DWB capture, RDPCS PHY rate changes, panel power sequencing, and Azalia stream setup still produce working display and audio.
- Performance-counter tests should program CB, SC, GDS, RLC, and SPI selectors and confirm counters increment for expected workloads; sparse selectors should not alias neighboring events.
- Fault and cache diagnostics should decode `TC_NACKS`, `GL2_NACKS`, `TC_OP`, and `GL2_OP` values consistently with hardware traces.
- Suspend/resume, runtime power management, GPU reset, display hotplug, DP link training, HDMI audio playback, and KFD queue-manager initialization are integration signals that catch stale or mismatched enum values in stateful hardware flows.
- Generated-header diffs should be checked against AMD register-generation output, especially around reserved holes, opcode masks, power/reset enums, and the partial `SPI_PERFCNT_SEL` boundary.

### subset-b-003498: lines 15194-21030

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h lines 15194-21030

## Scope

This chunk is a generated AMDGPU SOC21 enum/value slice. It starts inside the tail of `SPI_PERFCNT_SEL`, then covers complete enum and value sections for shader processor input/output, shader queue, geometry engine, vertex grouper/tessellator, graphics block/global register bus manager, command processor, shader export, depth buffer, setup/rasterization, and the opening part of primitive hub performance selectors. It ends in the middle of `PH_PERFCNT_SEL` at `PH_PERF_SEL_SC5_PA3_DATA_FIFO_RD`; that enum continues in the next chunk.

The file is metadata only. It declares `typedef enum` value sets and `#define` constants that give numeric encodings for SOC21 register fields, packet fields, performance counter selectors, debug windows, and shader/geometry state. There are no functions, structs with storage, allocation paths, locks, branches, loops, MMIO reads/writes, or persistence code in this range.

Although the repository path is under a `ceph-client` source mirror, this chunk is AMD GPU register metadata. It does not implement distributed filesystem behavior.

## Purpose

`soc21_enum.h` gives semantic names to integer values that are written into or decoded from SOC21 hardware registers. The matching offset and shift/mask headers identify register addresses and bit positions; this enum header identifies the legal values that may occupy those fields.

The covered range includes:

- SPI output, sample, LDS, sprite-coordinate, and shader export/format enums.
- SQ and SQG enums for memory address/alignment modes, instruction types, issue reasons, resource descriptors, texture sampling controls, thread-trace masks, wave types, exception and wait-count partition constants, and large SQ performance selectors.
- COMP and GE enums for context-state data/control types plus geometry engine performance selectors.
- VGT and WD input-assembler/draw enums for primitive topology, source/index type, tessellation modes, geometry-stage enables, output path/primitive selection, DMA swap/buffer mode, and event type encodings.
- GB, GL1, TA, TEX, TCP, TD, GL2, and GRBM performance selectors plus texture/sampler/cache-policy enums.
- CP/CPC/CPF/CPG perf counter and latency/window selectors, scratch atomic operations, ME/pipe/ring IDs, perfmon state values, VMID/config-space constants, source-ID constants, and SPM state values.
- SX blend/downconversion/optimization and performance selectors.
- DB depth/stencil, PRT fault, flush event, pixel-pipe, Z mode/order, and large DB performance selector enums.
- PA/SU performance selector values for primitive assembly, clipping, setup, small primitive culling, scan converter sends, and geometry front-end activity.
- The first 661 entries of `PH_PERFCNT_SEL`, covering SC0 through part of SC5 primitive-hub arbitration and PA FIFO activity selectors.

## Important APIs, Types, and Constants

The public surface is the enum and macro namespace. Important complete enum groups in this chunk include:

- `SPI_PNT_SPRITE_OVERRIDE`, `SPI_PS_LDS_GROUP_SIZE`, `SPI_SAMPLE_CNTL`, `SPI_SHADER_EX_FORMAT`, and `SPI_SHADER_FORMAT`.
- `SH_MEM_ADDRESS_MODE`, `SH_MEM_ALIGNMENT_MODE`, `SQG_PERF_SEL`, `SQ_CAC_POWER_SEL`, `SQ_EDC_INFO_SOURCE`, `SQ_IBUF_ST`, `SQ_IMG_FILTER_TYPE`, `SQ_IND_CMD_CMD`, `SQ_IND_CMD_MODE`, `SQ_INST_STR_ST`, `SQ_INST_TYPE`, `SQ_LLC_CTL`, `SQ_NO_INST_ISSUE`, `SQ_OOB_SELECT`, and the large `SQ_PERF_SEL`.
- SQ resource and texture enums such as `SQ_RSRC_BUF_TYPE`, `SQ_RSRC_FLAT_TYPE`, `SQ_RSRC_IMG_TYPE`, `SQ_SEL_XYZW01`, `SQ_TEX_ANISO_RATIO`, `SQ_TEX_BORDER_COLOR`, `SQ_TEX_CLAMP`, `SQ_TEX_DEPTH_COMPARE`, `SQ_TEX_MIP_FILTER`, `SQ_TEX_XY_FILTER`, `SQ_TEX_Z_FILTER`, plus thread-trace include/exclude masks and shifts.
- `SQ_WAVE_TYPE`, with the alias macro `SQ_WAVE_TYPE_PS0`, and related `SQIND_*`, `SQ_GFXDEC_*`, `SQDEC_*`, `SQPERF*DEC_*`, exception, inserted-instruction, wait-count, and dependency-counter constants.
- `CSCNTL_TYPE` and `CSDATA_TYPE` with their `*_WIDTH` constants.
- `GE1_PERFCOUNT_SELECT`, `GE2_DIST_PERFCOUNT_SELECT`, and `GE2_SE_PERFCOUNT_SELECT`.
- VGT/WD draw enums including `VGT_DI_PRIM_TYPE`, `VGT_EVENT_TYPE`, `VGT_GS_MODE_TYPE`, `VGT_OUT_PRIM_TYPE`, `VGT_TESS_PARTITION`, `VGT_TESS_TOPOLOGY`, `WD_IA_DRAW_SOURCE`, and `WD_IA_DRAW_TYPE`.
- Cache/texture/performance enums including `CHA_PERF_SEL`, `CHCG_PERF_SEL`, `CHC_PERF_SEL`, `GL1A_PERF_SEL`, `GL1C_PERF_SEL`, `GL1H_REQ_PERF_SEL`, `TA_PERFCOUNT_SEL`, `TEX_*`, `TA_TC_*`, `TCP_*`, `TD_PERFCOUNT_SEL`, `GL2A_PERF_SEL`, and `GL2C_PERF_SEL`.
- Global/command processor enums such as `GRBM_PERF_SEL`, `GRBM_SE0_PERF_SEL` through `GRBM_SE7_PERF_SEL`, `PIPE_COMPAT_LEVEL`, `CPC_*`, `CPF_*`, `CPG_*`, `CP_ALPHA_TAG_RAM_SEL`, `CP_ME_ID`, `CP_PERFMON_ENABLE_MODE`, `CP_PERFMON_STATE`, `CP_PIPE_ID`, `CP_RING_ID`, and `SPM_PERFMON_STATE`.
- Shader export and depth/stencil/raster enums such as `SX_BLEND_OPT`, `SX_DOWNCONVERT_FORMAT`, `SX_OPT_COMB_FCN`, `SX_PERFCOUNTER_VALS`, `CompareFrag`, `ConservativeZExport`, `DFSMFlushEvents`, `DbMemArbWatermarks`, `DbPRTFaultBehavior`, `DbPSLControl`, `ForceControl`, `OreoMode`, `PerfCounter_Vals`, `PixelPipeCounterId`, `PixelPipeStride`, `RingCounterControl`, `StencilOp`, `ZLimitSumm`, `ZModeForce`, `ZOrder`, `ZSamplePosition`, `ZpassControl`, and `SU_PERFCNT_SEL`.

The macros in this range define constants rather than typed enums. Examples include SQ indirect debug partition offsets/sizes, SQ decoder address ranges, maximum SGPR/VGPR counts, exception bit encodings, shader wait-counter partitions, `SEM_*` response values, IQ retry/interrupt types, VMID size, secure/non-secure source IDs, and config/context/persistent register-space boundaries.

`PH_PERFCNT_SEL` is intentionally incomplete in this chunk. Lines 20369-21030 cover its start through `SC5_PA3_DATA_FIFO_RD`, including repeated per-SC/per-PA selectors for arbitration cycles, starvation/stall signals, send credits, graphics-pipe transitions, PA FIFO read/write/empty/full/null/event/overflow/EOP/EOPG/deallocation activity, and scan-converter windows.

## Control Flow and Data Flow

This header has no executable control flow. Its data flow is compile-time substitution:

1. A register field is identified by a generated offset header and shift/mask header, for example SOC21 GFX, SPI, SQ, VGT, TA/TCP/TD, CP, SX, DB, PA, or PH register metadata.
2. Driver or tooling code selects one of these enum constants as the semantic field value, such as a primitive type, draw source, texture clamp mode, cache policy, shader export format, perfmon state, or performance counter selector.
3. The value is packed into the target field with AMDGPU helper macros such as `REG_SET_FIELD()` or decoded from a register dump with the matching mask/shift constants.
4. Hardware interprets the resulting integer according to the SOC21 register specification.

Search results in this tree show `soc21_enum.h` included by KFD queue management (`amdkfd/kfd_device_queue_manager_v11.c`) and SOC21-related interrupt handling code referencing SOC21 constants from the same enum/header family. Many constants in this chunk are also mirrored by later-generation enum headers such as `soc24_enum.h`, which is a strong signal that this file is part of the generated ASIC register ABI rather than standalone driver logic.

For performance counters, the runtime flow is usually: select an event ID from enums such as `SQ_PERF_SEL`, `TA_PERFCOUNT_SEL`, `TCP_PERFCOUNT_SELECT`, `GL2C_PERF_SEL`, `GRBM_PERF_SEL`, `CPC_PERFCOUNT_SEL`, `SX_PERFCOUNTER_VALS`, `PerfCounter_Vals`, `SU_PERFCNT_SEL`, or `PH_PERFCNT_SEL`; program that selector into a perf counter select register; start/stop or sample the counter through CP/SPM/perfmon controls; then decode the count with knowledge of the selected hardware block.

## State and Persistence Behavior

The chunk stores no software state and persists nothing to disk. The declared constants describe hardware-visible values whose state lives in GPU registers, command processor state, debug/trace engines, performance counters, and shader/geometry/raster/cache units.

Configuration enums represent state that can persist in registers until reset, power loss, context switch, or later driver programming. Examples include shader memory modes, texture sampler modes, VGT draw/topology/tessellation modes, DB Z/stencil control, SX export formats, CP perfmon mode/state, and cache policy fields.

Performance selector enums do not themselves hold counts. They select which live hardware signal is accumulated by a counter. The selected event and counter state can be volatile, context-dependent, shader-engine-specific, or reset by perfmon control writes.

Several macro groups describe address ranges or partition geometry, such as SQ indirect-register partition offsets, SQ decoder ranges, config/context/persistent spaces, and wait-counter bit partitions. These are static ABI facts for this ASIC generation, not mutable driver state.

The header does not document reset values, valid sequencing, read-only versus write-only behavior, sticky bits, write-one-to-clear semantics, privilege restrictions, or whether a field is context-saved. Consumers must rely on hardware specs and the register programming sequences in AMDGPU.

## Dependencies and Integration Points

Direct dependencies and integration points are:

- SOC21 generated register offset and shift/mask headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/`, which define where these enum values are packed.
- AMDGPU register helper conventions, especially token-pasting field helpers such as `REG_SET_FIELD()` and `REG_GET_FIELD()`.
- KFD and GFX queue-management code that includes `soc21_enum.h` for generation-specific enum values.
- SOC21 interrupt and queue code in the AMDGPU/KFD tree that relies on related SOC21 constants to classify client/source IDs and queue behavior.
- Performance monitoring paths for SQ/SQG, GE, VGT, GL1/GL2, TA/TCP/TD, GRBM, CPC/CPF/CPG, SX, DB, SU, and PH blocks.
- Register dump, trace, and diagnostic tooling that maps raw selector numbers back to names.
- Later-generation enum headers such as `soc24_enum.h`; these are not dependencies at compile time, but they provide cross-generation comparison points for selector drift and renamed events.

This header sits at an ABI boundary between driver code and hardware. The enum names may look like ordinary C types, but the numeric values are the important contract.

## Risks and Edge Cases

- The chunk begins in the middle of `SPI_PERFCNT_SEL`; the earlier SPI performance selector values are outside this work item. Reconciliation should combine with the previous chunk before describing the full SPI selector enum.
- The chunk ends in the middle of `PH_PERFCNT_SEL`; only SC0 through part of SC5 are present here. The next chunk must provide the remaining PH selectors and the closing typedef.
- Most constants are unscoped C enum values or preprocessor macros. Name collisions are possible across included generated headers, and several names are generic (`UNDEF`, `FORCE_ENABLE`, `RINGID0`, `PIPE_ID0`, etc.).
- Numeric encodings are ASIC-generation-specific. Reusing SOC21 values with SOC24, GFX8, or another generated enum header can silently program the wrong event or mode even when names are similar.
- Performance selector enums are dense, large, and repetitive. A single off-by-one value can select a different hardware signal while still compiling and producing plausible counter data.
- Repeated selector patterns across shader engines, scan converters, PA lanes, GRBM SE instances, and cache pipes are easy to misread. Consumers must choose the correct instance-specific selector, not just a similarly named signal.
- Some enum values encode sensitive control behavior, such as CP scratch atomic ops, perfmon state transitions, debug/trace include masks, SQ indirect partitions, DB flush events, and VGT events. Writing these values in the wrong sequence can affect running GPU work or diagnostics.
- The header does not validate ranges. Passing an enum value into the wrong register field is a normal C integer operation and may not be caught at build time.
- Several value groups describe live hardware states or debug windows. Reading or writing corresponding registers while engines are active can race with hardware unless the caller follows block-specific quiesce/polling rules.

## Test and Validation Signals

Useful validation is mainly compile-time, generator, and hardware-integration coverage:

- Build AMDGPU/KFD paths that include `soc21_enum.h`, especially SOC21 GFX/KFD queue-management and perf/trace code, to catch missing or colliding names.
- Generator checks should verify that enum values are monotonic where expected and match the authoritative SOC21 register database for `SQ_PERF_SEL`, `VGT_DI_PRIM_TYPE`, `VGT_EVENT_TYPE`, `TA_PERFCOUNT_SEL`, `TCP_PERFCOUNT_SELECT`, `GL2C_PERF_SEL`, `GRBM_*`, `CP_*`, `PerfCounter_Vals`, `SU_PERFCNT_SEL`, and `PH_PERFCNT_SEL`.
- Cross-check each enum group against matching shift/mask field widths. For example, primitive type, texture clamp/filter, cache-policy, perfmon state, pipe/ring IDs, and performance selector fields must be wide enough for the maximum value used by SOC21.
- Register-dump decoders should map known raw values back to these names and should reject or label out-of-range values instead of assuming all fields share a common enum.
- Perf counter smoke tests on SOC21 hardware should program representative selectors from SQ, GE, TA/TCP/TD, GL2, GRBM, CP, SX, DB, SU, and PH and verify counters increment under workloads that exercise the corresponding block.
- Graphics pipeline tests should cover VGT draw source/index/primitive/topology/tessellation values, DB compare/stencil/Z modes, SX export/downconversion formats, and SPI shader export/sample settings through normal rendering paths.
- KFD/compute tests should exercise SQ memory modes, wave/instruction type reporting, CP queue/pipe/ring IDs, and perfmon enable/state transitions where those fields are visible to queue setup or debug paths.
- Trace/debug validation should cover SQ thread-trace include/exclude masks, SQ indirect register partition offsets, inserted-instruction IDs, exception bit values, and wait-counter/dependency partition constants.

## Chunk Boundary Notes

Merge/reconciliation should treat this document as a middle slice of `soc21_enum.h`. The previous chunk is needed for the start of `SPI_PERFCNT_SEL`, and the next chunk is needed for the remainder of `PH_PERFCNT_SEL`. Complete per-file research should preserve the fact that this range contains both typed enums and macro value groups, and that it is generated hardware ABI metadata rather than executable driver logic.

### subset-b-003499: lines 21031-22477

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h lines 21031-22477

## Scope And Purpose

This chunk is the closing 1,447-line segment of AMD's generated `soc21_enum.h` hardware enum header. It exports numeric selector values for SOC21 GPU blocks: the tail of `PH_PERFCNT_SEL`, complete `PhSPIstatusMode`, `RMIPerfSel`, `GCRPerfSel`, `UTCL1PerfSel`, interrupt-handler enums, `SEM_PERF_SEL`, `LSDMA_PERF_SEL`, the ROM signature constant, and `EFC_SURFACE_PIXEL_FORMAT`. The path sits below the mirrored `ceph-client` tree, but the content is AMDGPU hardware metadata, not Ceph filesystem code.

The definitions are compile-time ABI between AMDGPU/KFD code and SOC21 hardware register fields. They identify perf-counter mux inputs, interrupt-ring/interface encoding, semaphore and LSDMA monitor events, ROM image signature value, and video/compositor surface pixel formats. This chunk defines no functions, structs, variables, locks, allocations, sysfs nodes, or direct MMIO accesses.

The chunk starts mid-enum at `PH_PERF_SEL_SC5_PA3_DATA_FIFO_WE`, so the beginning of `PH_PERFCNT_SEL` is in the previous chunk. It ends at the `#endif /*_soc21_ENUM_HEADER*/` guard close.

## Important APIs, Types, And Constants

The exported API is the set of enum type names and enumerators consumed by SOC21 AMDGPU code or by shared generated register-programming paths:

- `PH_PERFCNT_SEL`: performance-counter selector values for the primitive/parameter handling path. This chunk covers SC5 PA3-PA7 FIFO events, full SC6 and SC7 selector groups, aggregate SC arbiter starvation/stall selectors, and per-SC FIFO status selectors through `PH_PERF_SC7_FIFO_STATUS_3 = 0x3ff`. The visible events cover data FIFO reads/writes, empty/full flags, null/event/FPOV/LPOV/EOP/EOPG writes, dealloc reads, screen/arbiter busy states, credit states, graphics pipe transitions, and FIFO status lanes.
- `PhSPIstatusMode`: selects PH/SPI status reporting mode: largest PA/PH FIFO count, arbiter-selected PA/PH FIFO count, or disabled.
- `RMIPerfSel`: two RMI performance events for RB-to-RMI write requests and read requests across all client IDs.
- `GCRPerfSel`: graphics cache request performance selectors. It enumerates request classes for SDMA0, SDMA1, CPC, CPG, CPF, RLC, PM, and PIO; each group separates GL2/GL1 range requests, less-than-16K, 16K, greater-than-16K, all-request, metadata, SQC data, SQC instruction, TCP, and TCP TLB-shootdown traffic. It also includes virtual/physical request selectors, heavy/light TLB shootdown, all requests, outstanding request clocks, UTCL2 request/return/inflight/credit/filter signals.
- `UTCL1PerfSel`: UTCL1 TLB/cache performance selectors for request, hit, miss, miss-handler behavior, UTCL2 requests/returns, XNACK retry, fault and permanent/PRT fault returns, credit or miss-handler stalls, outstanding request accumulation, bypass requests, invalidation filter hits, CP invalidation requests, UTCL2-to-UTCL1 invalidations, range invalidations, and all-VMID invalidations.
- `IH_CLIENT_TYPE`, `IH_INTERFACE_TYPE`, `IH_RING_ID`, and `IH_VF_RB_SELECT`: compact interrupt-handler encoding enums. They distinguish GFX/MM/multi-VMID clients, legacy versus register-write interfaces, interrupt/request/translation rings, and VF ring-buffer selection by client function ID, IH function ID, or PF.
- `IH_PERF_SEL`: large interrupt-handler performance selector enum. It covers cycle/idle/input/buffer-idle state, RB0/RB1/RB2 full/overflow/writeback/wrap/load-RPTR events, MC write activity and stalls, BIF line edge events, client credit/cookie/storm/drop/self-IV/buffer FIFO signals, 32 client interrupt inputs, and virtualization-specific per-VF variants for VF0-VF15 on ring-buffer fullness, overflow, write-pointer writeback/wrap, read-pointer wrap, BIF line edges, full-drain drops, and load-RPTR operations.
- `SEM_PERF_SEL`: semaphore performance selectors for cycle/idle, request-signal and request-wait events from SDMA0-3, UVD/UVD1, VCE0/VCE1, ACP, ISP, VP8, CPG engines, CPC immediate engines, CPC offline engines 0-31 for CPC1/CPC2, poll waits for those offline engines, MC read/write request/return events, and ATC request/return/XNACK/invalidation/VM-invalidation events.
- `LSDMA_PERF_SEL`: local SDMA performance selectors for ring-buffer state, command queue state, indirect-buffer queue state, execution idleness, SRBM register sends, memory-controller request/return activity, semaphore and interrupt request/response states, packet count, copy-engine idleness/stalls/FIFO fullness, GFX/RLC/page selection, context changes, doorbell, bus-address routing, L1/ATCL2 invalidation/XNACK paths, MMHUB requests/returns for CE/F32/atomic/RB/IB/WPTR, UTCL1/UTCL2 traffic, command operation match/start/end, CE busy transitions, perf-counter trigger transitions, DRAM ECC, and NACK generation errors.
- `ROM_SIGNATURE`: `0x0000aa55`, the standard BIOS/option-ROM signature value expected in ROM image headers.
- `EFC_SURFACE_PIXEL_FORMAT`: UVD EFC surface-format IDs for RGB/BGR/ARGB/RGBA formats, YCrCb/YCbCr ordering variants, 10-bit and 12-bit MSB/LSB packed or planar formats, 16:16:16:16 float/unorm/snorm variants, 4:2:0 planar and 4:2:2 packed YUV formats, RGB111110/BGR101111 fixed and float formats, and mono 8/10/12/16-bit formats.

## Control Flow And Runtime Behavior

There is no control flow in this header. Runtime behavior appears only when other driver code writes these numeric values into SOC21 register fields or compares hardware-provided values against them.

The typical flow is:

1. A SOC21-specific driver path includes `soc21_enum.h` directly or indirectly alongside generated register address and bitfield headers.
2. A perf-counter, interrupt, semaphore, DMA, ROM, or media setup path chooses one of these enum constants.
3. The value is packed into the appropriate selector or control field using generated register masks/shifts and written with AMDGPU register access helpers.
4. Hardware interprets the selector and routes the matching internal event, ring selection, status mode, signature comparison, or pixel-format behavior.

Concrete local integration is visible through direct include/use patterns around SOC21 KFD interrupt and queue code. `amdkfd/kfd_device_queue_manager_v11.c` includes `soc21_enum.h`, and SOC21 interrupt processing uses related SOC21 client/source IDs in `amdkfd/kfd_int_process_v11.c`, `amdkfd/kfd_int_process_v12_1.c`, `amdkfd/soc15_int.h`, and `include/soc15_ih_clientid.h`. The exact enum names in this chunk are mostly hardware selector vocabulary and appear heavily in adjacent generated headers such as `navi10_enum.h` and `soc24_enum.h`, which makes cross-ASIC generated consistency an important integration signal even when direct C references are sparse.

## State And Persistence Behavior

The enum definitions hold no mutable software state and persist nothing. They describe values for stateful hardware blocks:

- Perf-counter mux configuration persists in hardware registers until reprogrammed, reset, power-gated, or restored after suspend/resume.
- IH ring/interface/VF selection values affect interrupt routing and virtualization ring-buffer attribution when placed into IH configuration registers.
- Semaphore, GCR, UTCL1, PH, RMI, and LSDMA selectors control which internal event a counter observes; the counters and hardware FIFOs they observe are mutable hardware state outside this header.
- `ROM_SIGNATURE` is a fixed expected value used to identify ROM image contents, not a stored driver state variable.
- `EFC_SURFACE_PIXEL_FORMAT` values describe command/register programming for video or EFC surface interpretation; actual surfaces, tiling, memory, and format conversion state live elsewhere.

The file does not encode access permissions. Some selected events are counter inputs, some are status signals, some are virtualization-specific state, and some are programming values that may be meaningful only for particular SOC21 SKUs or enabled IP blocks.

## Dependencies And Integration Points

This header depends on the generated SOC21 hardware contract. Its numeric values must stay synchronized with companion SOC21 register headers under `drivers/gpu/drm/amd/include/asic_reg/` and with the hardware register database used to generate `soc21_enum.h`.

Important integration domains:

- AMDGPU perf-counter programming: `PH_PERFCNT_SEL`, `GCRPerfSel`, `UTCL1PerfSel`, `IH_PERF_SEL`, `SEM_PERF_SEL`, `LSDMA_PERF_SEL`, and `RMIPerfSel` are selector namespaces for internal block counters. Consumers need matching selector-field widths and the correct perfmon block/register for each enum family.
- Interrupt handling and virtualization: `IH_CLIENT_TYPE`, `IH_INTERFACE_TYPE`, `IH_RING_ID`, `IH_VF_RB_SELECT`, and the per-VF `IH_PERF_SEL_*_VF*` values tie into IH ring-buffer routing, SR-IOV virtual-function accounting, and KFD/amdgpu interrupt processing.
- DMA/cache/TLB monitoring: `GCRPerfSel`, `UTCL1PerfSel`, `SEM_PERF_SEL`, and `LSDMA_PERF_SEL` connect cache request paths, TLB invalidation/fault behavior, semaphore waits, local SDMA rings, MMHUB, ATCL2, and memory-controller traffic.
- ROM and media paths: `ROM_SIGNATURE` aligns with option-ROM parsing expectations, while `EFC_SURFACE_PIXEL_FORMAT` is an input vocabulary for UVD/EFC surface programming and format negotiation.
- Cross-generation generated headers: similar enum names appear in `navi10_enum.h` and `soc24_enum.h`. Some values intentionally match across generations, while others differ or have added dummy/reserved entries; consumers must include the ASIC-specific header rather than assuming a universal numeric table.

## Risks And Edge Cases

- The chunk begins in the middle of `PH_PERFCNT_SEL`. A final per-file report must merge with the previous chunk before making complete claims about the PH selector range.
- Generated enum drift can compile cleanly while breaking runtime behavior. A wrong selector value can route a perf counter to the wrong event, making diagnostics and power/performance tuning misleading rather than obviously failing.
- Repetitive per-instance patterns are off-by-one sensitive. `PH_PERF_SEL_SC6/SC7_PA0-PA7`, per-SC FIFO status selectors, `IH_PERF_SEL_*_VF0-VF15`, `SEM_PERF_SEL_CPC*_OFFL_E0-E31`, and `LSDMA_PERF_SEL_*_REQ/RET` ranges can be damaged by inserting or deleting one value.
- Sparse values are intentional. `LSDMA_PERF_SEL` skips several IDs, and `EFC_SURFACE_PIXEL_FORMAT` leaves gaps between format families. Code must not assume that every value in the numeric range is valid.
- Virtualization-specific IH selectors are high risk in SR-IOV environments. Misnumbered VF fullness, overflow, wrap, or full-drain-drop events can obscure noisy or wedged virtual functions.
- Pixel-format IDs are hardware ABI, not DRM fourcc values. Treating `EFC_SURFACE_PIXEL_FORMAT` as directly interchangeable with userspace DRM format constants would be unsafe without explicit translation.
- `ROM_SIGNATURE` is endian-sensitive in practice. The constant is `0xaa55` as a numeric value, while byte order in memory or MMIO reads depends on the ROM access path.
- Access type is not represented. Some selected signals may be debug-only, unsupported on specific IP revisions, or require clocks/power domains to be active before reads are meaningful.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU and KFD with SOC21 support to catch missing enum names, duplicate definitions, or include-order issues.
- Mechanically compare `soc21_enum.h` against the authoritative generated hardware database and against the matching SOC21 register field headers for selector width compatibility.
- Diff enum families against nearby generated headers (`navi10_enum.h`, `soc24_enum.h`) while accounting for deliberate ASIC differences, especially `GCRPerfSel`, `UTCL1PerfSel`, `IH_PERF_SEL`, `LSDMA_PERF_SEL`, and `EFC_SURFACE_PIXEL_FORMAT`.
- Runtime perf-counter smoke tests should program representative selectors from PH, GCR, UTCL1, IH, SEM, and LSDMA blocks and confirm counters change under targeted workloads: graphics/primitive traffic, SDMA copies, TLB invalidations or faults, semaphore waits, interrupt storms, and MMHUB memory traffic.
- KFD/SR-IOV testing should exercise interrupt rings and VF ring-buffer pressure so RB full/overflow/wrap/load-RPTR and full-drain-drop signals can be correlated with expected VF behavior.
- Media validation should program representative EFC formats, including RGB, YUV 4:2:0 planar, YUV 4:2:2 packed, high-bit-depth, float, and mono formats, then verify surface interpretation and rejection of unsupported values.
- ROM validation should verify that option-ROM reads identify the `0xaa55` signature through the actual ROM access path used by SOC21 devices.

## Cross-Chunk Notes

The previous chunk contains the start of `PH_PERFCNT_SEL`, including earlier SC and PA selector values. This chunk closes `PH_PERFCNT_SEL`, adds the remaining enum groups through UVD EFC formats, and closes the header guard. The merge lane should combine all chunks for `soc21_enum.h` before summarizing the file-level generated enum namespace.
