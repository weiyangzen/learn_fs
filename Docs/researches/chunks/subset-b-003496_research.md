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
