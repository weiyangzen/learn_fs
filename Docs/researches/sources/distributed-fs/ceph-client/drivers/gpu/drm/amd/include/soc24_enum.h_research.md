# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003500`: lines 1-8494, `Docs/researches/chunks/subset-b-003500_research.md`
- `subset-b-003501`: lines 8495-14960, `Docs/researches/chunks/subset-b-003501_research.md`
- `subset-b-003502`: lines 14961-20490, `Docs/researches/chunks/subset-b-003502_research.md`
- `subset-b-003503`: lines 20491-21073, `Docs/researches/chunks/subset-b-003503_research.md`

## Chunk Research

### subset-b-003500: lines 1-8494

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h lines 1-8494

## Scope And Purpose

This chunk is the first 8,494 lines of AMD's generated `soc24_enum.h` hardware enum header for SOC24-class AMDGPU blocks. It is a compile-time register-value contract, not executable logic: it defines enum names and exact numeric encodings used when programming SOC24 graphics, memory, SDMA, display, timing, link, audio, AUX, I2C, and interrupt-control registers.

The path sits under a `ceph-client` source mirror, but this file is AMDGPU hardware metadata. It is unrelated to Ceph filesystem protocol behavior except that it is part of the mirrored kernel source tree.

The header begins with the `_soc24_ENUM_HEADER` include guard and a non-`_DRIVER_BUILD` compatibility block mapping `GL__*` OpenGL-style blend names onto `BLEND_*` symbols when `GL_ZERO` is not already defined. The rest of this chunk is generated `typedef enum` declarations. There are no functions, structs, global variables, allocations, locks, direct MMIO reads/writes, or persistence code.

## Important APIs, Types, And Enums

The exported API is the generated enum namespace. Each enum value is intended to match a hardware field encoding exactly; consumers generally pass these values to register-field helper macros, packet builders, or hardware abstraction code that already knows the target register and bitfield.

Major enum families in this chunk:

- Command processor, cache, memory, and MMU encodings: `CP_PERFMON_ENABLE_MODE`, `CP_PERFMON_STATE`, `GL0V_CACHE_POLICIES`, `GL1_CACHE_POLICIES`, `GL1_CACHE_STORE_POLICIES`, `GL2_CACHE_POLICIES`, `GL2_NACKS`, `GL2_OP`, `GL2_OP_MASKS`, `Hdp_SurfaceEndian`, `MTYPE`, `TCC_MTYPE`, `SCOPE`, `GATCL1RequestType`, `UTCL0FaultType`, `UTCL0RequestType`, `UTCL1FaultType`, and `UTCL1RequestType`. These cover performance counter state, cache policy, L2 operation opcodes, endian mode, memory type, request scope, and retry/XNACK fault semantics.
- SDMA and streaming performance monitor values: `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SDMA_PERFMON_SEL`, `SDMA_PERF_SEL`, and `SPM_PERFMON_STATE`. The SDMA selectors enumerate ring-buffer, IB, doorbell, context-change, cache/TLB invalidation, UTCL2, metadata, GCR, command operation, queue, and channel request/return events.
- Compression and cache policy controls: `READ_COMPRESSION_MODE`, `WRITE_COMPRESSION_MODE`, `ReadPolicy`, and `WritePolicy`, including bypass, raw-compressed, decompressed, stream, no-allocate, and cache-bypass selections.
- DPP/color/frontend display values: color/luma keying, denormalization, format crossbars, pixel expansion, pre-CSC/pre-degamma, `SURFACE_PIXEL_FORMAT`, cursor modes, scaler modes, line-buffer and output-buffer controls, sharpening, and the large CM/CMC LUT and color-matrix families. `SURFACE_PIXEL_FORMAT` maps hardware pixel-format codes for ARGB/RGBA, YCbCr, planar 4:2:0, packed 4:2:2, 10/12/16-bit, FP, RGBE, mono, and fixed/float 11:11:10 formats.
- Display CRC, perf counter, and hub/hubp setup: `CRC_*`, `TEST_CLK_SEL`, `PERFCOUNTER_*`, `PERFMON_*`, `BIGK_FRAGMENT_SIZE`, `CHUNK_SIZE`, `DPTE_GROUP_SIZE`, `META_CHUNK_SIZE`, `MIN_CHUNK_SIZE`, `VMPG_SIZE`, `VM_GROUP_SIZE`, `ROTATION_ANGLE`, `SWATH_HEIGHT`, and HUBP blanking, VTG, TTU, surface DCC, flip, stereo, TMZ, and update-lock enums.
- Cursor, metadata, hubbub, MPC, MPCC, DPG, FMT, OPP, and OTG display pipeline families. These define crossbar routing, memory power states, cursor pitch/snoop/stereo/TMZ/system-address modes, DMDATA update/underflow semantics, AXI-like response statuses, MPC/MPCC LUT/color/gamut/blending/stereo modes, display pattern generator bit depth/range/pattern, formatter dithering/clamping/subsampling, OPP CRC, and extensive OTG timing, update-lock, trigger, static-screen, vertical-interrupt, stereo, DRR, CRC, GSL, and flow-control values.
- DMCUB, RBBMIF, IHC, DMU, and DCCG values: DMCUB interrupt/timer-window encodings, invalid register access causes, GPU timer read selectors, interrupt destination/status, SMU interrupt controls, display clock gating, DTO source selection, deep-color DTO ratios, FIFO error detection, reference-clock selection, PHY/PLL pixel-rate sources, audio DTO choices, and clock/test mux controls.
- Link encoder and PHY values: DPHY 8b/10b, CRC, FEC, PRBS, training, fast training, component depth, compressed pixel format, DisplayPort pixel encoding, MST/MSE/MSO controls, DP secondary packet/audio/generic-stream packet controls, steering overflow, sync polarity, TU overflow, lane count, VBID, and stream disable/defer fields.
- DIG/HDMI/TMDS/DIO/I2C/DME/VPG/AFMT/AUX/HPD/HPO/stream-mapper values: DIG backend/front-end mode/source/stereo/fifo/test-pattern controls, HDMI ACR/audio/infoframe/null/generic/metadata packet controls, TMDS pattern and transmitter controls, DOUT I2C arbitration/DDC/EDID/transaction controls, DIO memory and clock gating, AFMT audio CRC/source/layout/infoframe/power controls, DP AUX arbitration/DPHY timing/GTC sync/interrupt/reset/timeout controls, HPD acknowledge/polarity, HPO test clock, and DP stream mapper targets.

The mapped range ends at line 8494 immediately after the first enumerator in `DP_STREAM_ENC_READ_CLOCK_CONTROL`; the enum closes on lines 8495-8496 outside this chunk. Final per-file reconciliation must merge the next chunk before treating that enum as complete.

## Control Flow And Runtime Behavior

There is no local control flow. Runtime behavior is created by code that includes this header and writes these enum values into SOC24 registers or command packets.

Typical usage pattern:

1. AMDGPU SOC24 code includes `soc24_enum.h` alongside register address, mask, and shift headers.
2. Higher-level driver logic chooses an enum value based on ASIC capability, display state, memory/cache policy, SDMA/perf event selection, link mode, or interrupt policy.
3. Register helpers pack the enum value into the appropriate field and perform the actual MMIO or indirect register operation.
4. Hardware persists or reports the resulting state until reset, power transition, reprogramming, or a hardware-owned status update changes it.

Direct include users in this tree include `amdgpu/gfx_v12_0.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/gmc_v12_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/mmhub_v4_1_0.c`, `amdgpu/mmhub_v4_2_0.c`, and `amdkfd/kfd_device_queue_manager_v12.c`. Display code also uses overlapping enum names and values such as surface formats through the DC hardware type layer; a search shows many `SURFACE_PIXEL_FORMAT_*` consumers in `display/dc`, `display/amdgpu_dm`, DPP, HUBP, DML, and resource calculation paths.

## State And Persistence Behavior

The header itself owns no state and persists nothing. The values describe stateful hardware fields whose side effects depend on the target register:

- configuration fields, such as cache policy, memory type, compression mode, pixel format, line buffer layout, update-lock mode, clock source, or AUX timing;
- action/handshake fields, such as reset, interrupt acknowledge, FIFO reset, AUX/I2C go, software trigger, or underflow clear;
- status selectors and readback encodings, such as invalid register access type, interrupt line status, DMCUB timer windows, DMU GPU timer sources, DPHY/FEC readiness, overflow/underflow status, and AUX arbitration state;
- power-management state, such as memory light/deep sleep/shutdown force/status controls across hub, MPCC MCM, formatter, DIO, DME, VPG, AFMT, DCOH, and HPO blocks.

Several enums intentionally use field-local names for identical `0`/`1` encodings. That is useful documentation and prevents mixing domains casually, but C does not enforce register-field compatibility once the value is used as an integer. Reserved values are present throughout and should remain preserved unless the hardware programming guide explicitly requires them.

## Dependencies And Integration Points

This generated enum header must stay synchronized with companion SOC24 register address and field headers under `drivers/gpu/drm/amd/include`, plus the display DC register programming layer that maps abstract DC state to hardware fields. It is part of the AMDGPU SOC24 contract for GFX12, GMC12, MMHUB/GFXHUB v12, KFD queue management, and DCN4-era display blocks.

Key integration surfaces:

- GFX/GMC/MMHUB/GFXHUB setup uses cache, MTYPE, GL2 operation, UTCL fault/request, scope, and perf monitor encodings.
- SDMA/KFD and performance tooling use the SDMA performance selector enums and perf counter state/mode enums.
- DC plane programming uses pixel-format, crossbar, DCC, swath/chunk/page, rotation, cursor, hubp, metadata, and surface flip/update-lock values.
- Color management uses CM/CMC/MPCC LUT, segment count, RAM selection, gamma, gamut remap, 3D LUT, coefficient format, and pending-state values.
- Timing and synchronization code uses OTG/OPTC/OPP CRC, trigger, DRR, GSL, vertical interrupt, stereo, update lock, static screen, and flow-control enums.
- Clock and power paths use DCCG, DCOH, HPO, PHY, PLL, DTO, deep-color, clock gating, soft reset, and memory-power enums.
- Display output paths use DP, HDMI, TMDS, DIG, DIO, DOUT I2C, AFMT audio/infoframe, DP AUX, HPD, stream mapper, and stream encoder values.

## Risks And Edge Cases

- Numeric values are ABI-like hardware contracts. A compile-clean value drift can silently program the wrong hardware behavior, especially for cache policy, GL2 opcodes, MTYPE, SDMA perf selectors, pixel formats, AUX timing, clock source selection, or interrupt acknowledge fields.
- The generated namespace is broad and not strongly typed at use sites. Many fields use generic names such as `ENABLE`, `BYPASS`, `SIGNED`, `INT_LEVEL`, `RESERVED_*`, or repeated `*_FALSE`/`*_TRUE` encodings; collisions or accidental cross-domain reuse are plausible in C.
- Some enum names preserve generated spelling, including apparent typos such as `SURFACE_INUSE_RAED_NO_LATCH`, `OPP_PIPE_DIGTIAL_BYPASS_CONTROL`, `FMT_CONTROL_SUBSAMPLING_MOME_*`, `OTG_3D_STRUCTURE_*_PROGRASSIVE`, and `DP_AUX_GTC_SYNC_CONTROL_OFFSET_CALC_MAX_ATTEMPT__*_ATTAMPS`. Renaming them for style would break consumers that depend on generated names.
- Reserved enumerators are explicit but not necessarily safe to write. Runtime code should use documented values and masked field writes rather than full-register writes that may alter adjacent reserved fields.
- Some values are active-low or counterintuitive: for example several `*_DIS_MODE` enums encode enable as `0`, many clock-gating disable controls encode enabled gating as `0`, and reset/ack/action fields may be pulse-like or self-clearing depending on the register.
- The chunk boundary splits `DP_STREAM_ENC_READ_CLOCK_CONTROL`; only `DP_STREAM_ENC_DCCG = 0` is inside this work item, while the second value and closing typedef are in the next lines.
- `SURFACE_PIXEL_FORMAT` here contains raw hardware encodings, while display DC code also defines abstract `SURFACE_PIXEL_FORMAT_*` values. Mapping between the two must be deliberate; raw enum values should not be assumed to match every software-facing DC enum.
- Power and link training fields often interact with timing-sensitive hardware state. Incorrect AUX timeout/precharge, DPHY training/FEC, HPD ack, I2C reset, or stream-disable values can cause display detection, link training, audio, or hotplug failures that are workload and monitor dependent.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU with SOC24, GFX12/GMC12/MMHUB/GFXHUB, KFD, and DC display support enabled so include users and enum references compile.
- Mechanically compare `soc24_enum.h` against the authoritative generated SOC24 register database and companion address/mask headers.
- Check generated enum completeness and boundaries: every `typedef enum` started before line 8494 should close within the chunk except the intentionally split `DP_STREAM_ENC_READ_CLOCK_CONTROL`.
- Exercise GFX/GMC/KFD paths that program cache, MTYPE, MMU fault, queue, and performance monitor fields.
- Exercise SDMA performance counter selection and ring/doorbell/context-change paths under copy, VM invalidation, and queue workloads.
- Exercise display plane programming across RGB, YCbCr, 4:2:0, 10/12/16-bit, FP, DCC, cursor, rotation, flip, TMZ, and stereo/update-lock cases.
- Run DC color-management and CRC tests covering LUT RAM selection, gamma/PWL, gamut remap, 3D LUT, MPCC blending, OPP/OTG CRC, and formatter dithering/clamping/subsampling.
- Validate link/output behavior on DP, HDMI, TMDS, AUX, HPD, I2C/DDC, audio/infoframe, MST/MSO, FEC, fast-training, and hotplug scenarios.
- Watch for kernel warnings, failed MMIO assertions, bad CRCs, page faults/XNACK anomalies, SDMA perf counter mismatches, display underflow/overflow, AUX/I2C timeouts, link training failures, audio packet loss, incorrect pixel formats, and suspend/resume regressions.

## Cross-Chunk Notes

This is a large-file chunk for lines 1-8494 only. Later chunks are required to complete `DP_STREAM_ENC_READ_CLOCK_CONTROL` and the rest of `soc24_enum.h`. The final per-file document should merge all chunks before making whole-file claims about the generated SOC24 enum namespace.

### subset-b-003501: lines 8495-14960

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h lines 8495-14960

## Scope

This chunk covers a large generated enum slice from AMD's SOC24 register enum header. The range starts in the tail of the `DP_STREAM_ENC` enum family and then defines 445 `typedef enum` blocks plus a small number of width/range `#define` constants. It ends inside the `PH_PERFCNT_SEL` enum; the PH performance-counter selector continues past line 14960 into the next chunk.

The covered register-block families are:

- DisplayPort stream/symbol/DPHY controls: `DP_STREAM_ENC`, `DP_SYM32_ENC`, and `DP_DPHY_SYM32`.
- Display audio, GPIO, clock, panel, and PHY blocks: `APG`, `DCIO`, `DCIO_CHIP`, `PWRSEQ`, and the Azalia/HDA `AZ*` families.
- Display compression and writeback: `DSCC`, `DSCCIF`, `DSC_TOP`, `DWB_TOP`, and `DWBCP`.
- Retimer/DP/HDMI PHY transmit control: `RDPCSTX` and `RDPCS`.
- Graphics command, geometry, cache, color, and perf blocks: `RLC`, `COMP`, `GE`, `CH`, `GRBM`, `CP`, `GCR`, `GC_EA_CPWD`, `GC_VML2PERFS`, `GC_VML2PL`, `CB`, and `PH`.

This header chunk contains no functions, structs, storage, allocation, locking, or executable control flow. Its semantics are the integer values that software writes into, or reads from, SOC24 hardware register fields.

## Purpose

`soc24_enum.h` is the symbolic value half of the SOC24 register ABI. The matching register address and shift/mask headers describe where a field lives; this file names the legal encodings for those fields. Consumers can use raw integer constants, but these enums document the intended hardware meanings: enable/disable bits, reset/assert states, power states, audio formats, topology modes, primitive types, ring identifiers, performance event selectors, and register aperture boundaries.

In this chunk the display-side enum families map DCN 4.x display hardware behavior, while the graphics-side families map GFX12 command processor, geometry, cache, color, and performance-monitoring behavior. Direct includes found in the tree are from SOC24 graphics and memory code such as `amdgpu/gfx_v12_0.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/gmc_v12_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/mmhub_v4_1_0.c`, `amdgpu/mmhub_v4_2_0.c`, and `amdkfd/kfd_device_queue_manager_v12.c`. The display enum names also align with generated DCN 4.1 register mask/address headers under `include/asic_reg/dcn/`.

## Important APIs, Types, and Constants

The public surface is the set of C enum type names and enumerator constants. Important families include:

- `DP_SYM32_ENC` and `DP_DPHY_SYM32`: DisplayPort stream/symbol encoder controls for enable/reset, CRC collection, component depth, pixel encoding, compressed/uncompressed format, secondary-data-packet priority, SOF reference, GSP trigger state, lane count, link-training modes, test patterns, PRBS selection, output path, scheduler status, SAT update state, stream override mode, and memory power states.
- `APG`: audio packet generator fields for audio CRC channel selection and continuous mode, debug ACP packet type, audio DTO base/divisor/multiple, APG debug muxing, DP audio-channel-count override, packet source overrides, ramp sign, and APG memory power control.
- `DCIO` and `DCIO_CHIP`: display IO and chip pad selectors for backlight PWM frame-start source, test clocks, generic A/B signal muxes, UNIPHY clock selectors, GPU timer read/start selection, genlock/swaplock masks, HPO encoder source, HPD/I2C/AUX pad electrical tuning, GPIO masking, pad mode, inversion, power-down, and 27 MHz reference source.
- `PWRSEQ`: panel and backlight power-sequencer fields for PWM enable/fractional enable, override routing, frame-start update, register lock, panel `DIGON`/`BLON`/`SYNCEN` polarity and state, target state, GPIO mask, and backlight delay override.
- `AZCONTROLLER`, `AZENDPOINT`, `AZINPUTENDPOINT`, `AZSTREAM`, `AZF0*`, and `AZROOT`: HDA/Azalia controller and codec encodings for CORB/RIRB size and reset, controller reset/flush, unsolicited responses, stream synchronization, output stream descriptor run/reset/error/interrupt bits, sample base rate/divisor/multiple, bits per sample, channel count, PCM/non-PCM stream type, digital-converter status bits, pin mute/output/input enables, widget capability flags, and HBR/DP/HDMI pin capabilities.
- `DSCC`, `DSCCIF`, and `DSC_TOP`: Display Stream Compression controls for bits per component, DSC version major/minor, enable/reset, line-buffer depth, input pixel format, memory power force/state, and top-level clock-gating/test-clock settings.
- `DWB_TOP` and `DWBCP`: display writeback controls for CRC mode/source, data-overflow status/interrupt type, debug selection, memory power, test clock, frame capture eye/rate/stereo polarity, gamut-remap coefficients/mode, output gamma LUT selection/readback, LUT segment count, and PWL/gamma mode.
- `RDPCSTX`/`RDPCS`: retimer/DP/HDMI transmit PHY control values for external reference clocks, SRAM/OCLA/TX clock enable and gate state, CBUS/SRAM/TX FIFO resets, FIFO status/error masks, DP Alt Mode lane/disable toggles, PHY CR mux/parameter source, reference ranges, SRAM init/load done status, PLL divisors, DP TX termination, TX rate/width/power state, RX detect result, lane packing/bit order, test clock mux, and PHY SRAM memory power state.
- `RLC`, `CP`, `GE`, `GRBM`, `CH`, `GCR`, `GC_EA_CPWD`, `GC_VML2PERFS`, `GC_VML2PL`, and `PH`: graphics control and performance selectors. These include RLC doorbell mode/perfmon commands, command processor latency/perf windows/selectors, CP ME/pipe/ring IDs, scratch atomic ops, register aperture constants (`CONFIG_SPACE_*`, `UCONFIG_SPACE_*`, `PERSISTENT_SPACE_*`, `CONTEXT_SPACE_*`), geometry primitive/index/source/DMA/event/tessellation/draw enums, GRBM busy selectors, global cache request counters, UTCL2/VML2 SPM event IDs, and PH per-shader-engine/per-pipe performance events.
- `CB`: color-buffer blend and mode encodings, including `BlendOp`, `BlendOpt`, `CBMode`, combiner functions, memory arbitration mode, and CB performance filters/selectors.
- `COMP`: small command-stream data/control type enums plus width constants for type/address/data fields.

Notable non-enum constants in this range include `CSDATA_*_WIDTH`, `CSCNTL_*_WIDTH`, command processor retry/interrupt type values (`IQ_QUEUE_SLEEP`, `IQ_OFFLOAD_RETRY`, `IQ_SCH_WAVE_MSG`, `IQ_DEQUEUE_RETRY`, `IQ_INTR_TYPE_*`), `VMID_SZ`, and register-space boundaries such as `CONFIG_SPACE_START/END`, `UCONFIG_SPACE_START/END`, `PERSISTENT_SPACE_START/END`, and `CONTEXT_SPACE_START/END`.

## Control Flow

There is no runtime control flow in this chunk. The only "flow" is implicit in hardware programming sequences that consume these constants:

1. Driver code selects a register field from the generated address and shift/mask headers.
2. It chooses one of these enum values as the field payload.
3. It composes a register value with field helper macros or direct bit operations.
4. Hardware later reports status or counter selector results using the same numeric encodings.

For example, a DP programming path can move from reset/assert values, through DPHY link-training/test mode selectors, into active stream/symbol encoder settings. A command processor queue path can use `CP_ME_ID`, `CP_PIPE_ID`, and `CP_RING_ID` to address a CP queue register set. A perf collection path can program `CPG_PERFCOUNT_SEL`, `GE*_PERFCOUNT_SELECT`, `GCRPerfSel`, or `PH_PERFCNT_SEL` into counter select fields and then sample counter registers elsewhere.

## State and Persistence Behavior

The enums themselves have no persistence, but many values describe persistent or observable hardware state:

- Reset and enable state appears throughout display, audio, PHY, DSC, DWB, CP, and stream descriptor blocks.
- Power state encodings recur for display/audio memories (`ON`, light sleep, deep sleep, shutdown) and RDPCS SRAM.
- Pending/status enums expose latched or polled hardware state, such as CRC validity, overflow, GSP trigger pending, DPHY rate/SAT update pending, scheduler status, FIFO empty/full, Azalia command busy/result valid, stream stop status, descriptor/fifo errors, and PHY SRAM init done.
- Register-space constants define CP register apertures that are persistent ABI boundaries for context/config/user-config/persistent register ranges.
- Performance selector enums do not store data by themselves, but they select persistent counter routing in hardware until the driver changes or resets the perf monitor state.

Because these are generated ABI constants, persistence correctness depends on the values staying bit-for-bit aligned with the SOC24 hardware specification and its generated shift/mask headers.

## Dependencies and Integration Points

This header depends only on normal C enum/preprocessor syntax and its include guard. It does not include other files in this range. It is integrated by inclusion in SOC24 AMDGPU/KFD implementation files and by name alignment with generated register headers:

- GFX/KFD consumers include `soc24_enum.h` directly for GFX12 command processor, graphics hub, memory controller, and queue-manager programming.
- Register writes normally pair these constants with `soc24_*_offset.h`, `*_sh_mask.h`, `SOC15_REG_OFFSET`, `RREG32/WREG32`, and `REG_SET_FIELD`/`REG_GET_FIELD` style helpers.
- Display register families in this chunk correspond to generated DCN 4.1 register definitions such as `include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`, especially for RDPCSTX/RDPCS, DCIO, APG, DSC, and DWB fields.
- Azalia/HDA enums bridge display audio register programming and the HD-audio style controller/codec protocol: CORB/RIRB rings, stream descriptors, pin widgets, converter formats, unsolicited responses, and digital converter status bits.
- CP ring/pipe/ME identifiers and register-space boundaries are ABI-sensitive integration points for AMDGPU and KFD queue setup, scheduling, and doorbell/register access code.

## Risks

- Numeric drift is the main risk. A wrong enum value can program a valid field with the wrong hardware meaning, which may manifest as display link failure, audio format mismatch, PHY instability, queue misrouting, bad perf data, or GPU hangs.
- Several enums use reserved encodings as named values. Driver code must not treat all enumerators as valid user-selectable modes; some represent reserved hardware encodings or status-only values.
- Similar names with inverted semantics can be error-prone, such as gate-disable fields where `0` means gate enabled and `1` means gate disabled, or reset/status bits where asserted/deasserted meanings differ by register.
- The chunk boundary cuts into `PH_PERFCNT_SEL`; consumers of this research should merge it with the following chunk before making claims about the complete PH performance selector list.
- Generated enum type names are global C identifiers. Cross-ASIC headers with similar enum names can conflict if included together incorrectly; SOC-specific code should include the matching SOC24 header only.
- Performance selector tables are hardware-version-specific. Reusing SOC21/Navi10 selector values for SOC24 or vice versa can silently collect the wrong event.
- This header has no compile-time coupling to the register field width. A value can overflow a field if the generated enum and shift/mask header disagree, so regeneration or manual edits require build and hardware validation.

## Test Signals

Useful validation signals are mostly build-time, register-programming, and hardware-observation checks:

- Compile SOC24 AMDGPU/KFD files that include `soc24_enum.h`, especially `gfx_v12_0.c`, `gfx_v12_1.c`, `gmc_v12_0.c`, `gfxhub_v12_0.c`, `mmhub_v4_1_0.c`, `mmhub_v4_2_0.c`, and `kfd_device_queue_manager_v12.c`, to catch enum-name drift.
- Exercise display bring-up over DP/HDMI/eDP, including link training, DSC, writeback/CRC paths, panel power sequencing, HPD/AUX/I2C, and audio playback. These cover the DP, APG, DCIO, PWRSEQ, AZ, DSC, DWB, and RDPCS families.
- Run KFD/AMDGPU queue tests that allocate rings and program ME/pipe/ring IDs, doorbells, and CP register apertures.
- Use perf counter tests or debugfs/perfmon tooling to program representative CP, GE, GRBM, GCR, GC_EA_CPWD, VML2, CB, and PH selector values and verify that counters increment under expected workloads.
- Check generated-header consistency by comparing enum maximum values against field masks in the matching SOC24/DCN shift-mask headers.
- Use suspend/resume and runtime power-management tests to verify reset, power-state, and memory power-force encodings across display, audio, RDPCS, DSC, DWB, and graphics blocks.

### subset-b-003502: lines 14961-20490

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h lines 14961-20490

## Scope And Purpose

This chunk is a large section of AMD's generated SOC24 enum header. It contains C `typedef enum` value tables only; it does not define executable functions, structs with storage, global variables, locks, allocations, or direct MMIO operations.

The values are a compile-time ABI between AMDGPU code and SOC24/GC 12-era hardware register fields, command packets, state descriptors, and performance-counter muxes. Companion register offset and shift/mask headers define where fields live; this file defines the legal symbolic values that may be written into those fields or decoded from them.

The range starts in the middle of `PH_PERFCNT_SEL`, covers many complete graphics/raster/shader/cache/texture/depth enum domains, and ends in the middle of `SU_PERFCNT_SEL`. Final per-file reconciliation should merge the adjacent chunks before making complete claims about those two boundary enums.

## Major Enum Groups

### Primitive Hub, Raster, And Scan Converter

The first part closes the tail of `PH_PERFCNT_SEL`. The covered values continue the per-scan-converter/per-primitive-assembler matrix for `SC3` through `SC7`, including PA FIFO reads/writes, empty/full status, null/event/FPOV/FPOP/EOP/EOPG/dealloc writes, arbiter stalls/starvation/busy, send credit states, graphics-pipe transitions, and `PH_PERF_SC*_FIFO_STATUS_*` selectors. This enum began before the chunk and has 1,024 total values, of which 592 are in this range.

Small primitive/raster configuration enums follow:

- `PhSPIstatusMode` selects PH-to-SPI status reporting by largest PA/PH FIFO count, arbiter-selected count, or disabled mode.
- `BinEventCntl`, `BinMapMode`, `BinSizeExtend`, and `BinningMode` describe binner event behavior, bin mapping mode, bin dimensions from 32 to 512 pixels, and force/disable/one-primitive-per-batch binning controls.
- `PkrMap`, `PkrXsel`, `PkrXsel2`, `PkrYsel`, `RbMap`, `RbXsel`, `RbXsel2`, `RbYsel`, `ScMap`, `ScXsel`, `ScYsel`, `SeMap`, `SePairMap`, `SePairXsel`, `SePairYsel`, `SeXsel`, and `SeYsel` provide raster-configuration mapping and tile-width selectors for packers, render backends, scan converters, shader engines, and shader-engine pairs.
- `ScUncertaintyRegionMode` and `ScUncertaintyRegionMult` select half-LSB/one-sided/two-sided uncertainty-region behavior and 1x/2x/4x/8x scale.
- `VRSCombinerModeSC` and `VRSrate` encode variable-rate shading combiner behavior and legal shading rates, including 1x1 through 4x4, conservative variants, and SSAA rates.

`SC_PERFCNT_SEL` is a complete 662-value scan-converter performance selector table. It covers SRPS/PSSW windows, tile and supertile flow, scissor/viewport/bounding-box rejection, quad and coarse-pixel activity, clip/cull and rasterization outcomes, HiZ/detail interactions, event/EOP/dealloc handshakes, SC-to-DB/SPI traffic, packer activity, PS wave flow, stalls, busy states, and repeated per-SC/per-PA FIFO status families. Consumers use these values as event IDs for SC performance counter select registers.

### Texture, TCP, TC, And Cache Operation Domains

`TC_EA_CID` names 16 export-address client IDs, including RT, FMASK, DB, UTL, TCP, command processor, SDMA, GCR, CPF, and PA-like clients. `TC_NACKS` describes no-fault, page-fault, protection-fault, and data-error NACK classes.

`TC_OP` is a 128-value operation-code table for texture/cache memory operations. It includes reads, atomics, writes, compare-swap and return/no-return variants, non-temporal and special memory forms, Z export variants, and reserved 64-bit/non-floating encodings. `TC_OP_MASKS` provides bit masks that classify flush-denorm, 64-bit, and no-return operation attributes.

Texture and sampler state enums include `TA_PERFCOUNT_SEL`, `TEX_BC_SWIZZLE`, `TEX_BORDER_COLOR_TYPE`, `TEX_CHROMA_KEY`, `TEX_CLAMP`, `TEX_COORD_TYPE`, `TEX_DEPTH_COMPARE_FUNCTION`, `TEX_FORMAT_COMP`, `TEX_MAX_ANISO_RATIO`, `TEX_MIP_FILTER`, `TEX_REQUEST_SIZE`, `TEX_SAMPLER_TYPE`, `TEX_XY_FILTER`, `TEX_Z_FILTER`, `TVX_TYPE`, `TA_TC_ADDR_MODES`, and `TA_TC_REQ_MODES`. Together they define texture-addressing performance events and legal sampler/resource encodings for border color, chroma keying, clamp behavior, normalized coordinates, depth compare function, signedness, anisotropy, mip/xy/z filtering, request size, resource validity, and TA-to-TC address/request modes.

TCP and GL cache enums include `TCP_CACHE_POLICIES`, `TCP_CACHE_STORE_POLICIES`, `TCP_COMPRESSION_BYPASS`, `TCP_COMPRESSION_OVERRIDE`, `TCP_OPCODE_TYPE`, `TCP_PERFCOUNT_SELECT`, `TCP_WATCH_MODES`, `TCP_WRITE_COMPRESSION_DISABLE`, `TD_PERFCOUNT_SEL`, `GL1A_PERF_SEL`, `GL1C_PERF_SEL`, `GL1XA_PERF_SEL`, `GL1XC_PERF_SEL`, `GL2A_PERF_SEL`, and `GL2C_PERF_SEL`. These encode L0/L1/L2 cache request classes, compression controls, watchpoint modes, texture data events, GL1/GL2 busy/stall/miss/hit/invalidating/request/return-credit activity, and per-client GL2 observations.

### SPI, SQ, PC, GRBMH, And Shader State

`PC_PERFCNT_SEL` is a 165-value primitive-assembler/parameter-cache selector table covering SC-to-PC pointer sends/valids, index and parameter-cache activity, vertex/primitive status, wave and work-launch counters, visibility and boundary-crossing events, and related busy or stall points.

SPI enums cover both state encoding and performance measurement:

- `SPI_FOG_MODE`, `SPI_LB_WAVES_SELECT`, `SPI_PNT_SPRITE_OVERRIDE`, `SPI_PS_LDS_GROUP_SIZE`, `SPI_SAMPLE_CNTL`, `SPI_SHADER_EX_FORMAT`, and `SPI_SHADER_FORMAT` define fog mode, late-branch wave selection, point-sprite coordinate override, PS LDS grouping, sample source, shader export format, and shader component count encodings.
- `SPI_PERFCNT_SEL` is a 284-value SPI selector table for shader-stage window validity, busy/idle states, wave launches, interpolator and parameter-cache activity, LDS/VGPR allocation, barrier and scoreboard behavior, stalls, wave limits, and RA request/allocation observations.

SQ and SQG enums include `SH_MEM_ADDRESS_MODE`, `SH_MEM_ALIGNMENT_MODE`, `SQG_PERF_SEL`, `SQ_CAC_POWER_SEL`, `SQ_EDC_INFO_SOURCE`, `SQ_IBUF_ST`, `SQ_IMG_FILTER_TYPE`, `SQ_IND_CMD_CMD`, `SQ_IND_CMD_MODE`, `SQ_INST_STR_ST`, `SQ_INST_TYPE`, `SQ_LLC_CTL`, `SQ_NO_INST_ISSUE`, `SQ_OOB_SELECT`, `SQ_PERF_SEL`, `SQ_ROUND_MODE`, `SQ_RSRC_BUF_TYPE`, `SQ_RSRC_FLAT_TYPE`, `SQ_RSRC_IMG_TYPE`, `SQ_SEL_XYZW01`, `SQ_TEX_ANISO_RATIO`, `SQ_TEX_BORDER_COLOR`, `SQ_TEX_CLAMP`, `SQ_TEX_DEPTH_COMPARE`, `SQ_TEX_MIP_FILTER`, `SQ_TEX_XY_FILTER`, `SQ_TEX_Z_FILTER`, `SQ_WATCH_MODES`, `SQ_WAVE_FWD_PROG_INTERVAL`, `SQ_WAVE_SCHED_MODES`, and `SQ_WAVE_TYPE`.

These values describe shader memory modes, alignment modes, global SQ performance events, CAC power attribution, EDC info sources, instruction-buffer state, image filter modes, indirect halt/resume/debug command modes, instruction classes, issue-block reasons, out-of-bounds behavior, rounding modes, resource descriptor types, component swizzles, texture filtering/clamping/depth compare fields as seen by SQ, watchpoint classes, wave progress intervals, scheduling modes, and wave types. `SQ_PERF_SEL` is the largest complete shader selector in this chunk, with 382 values spanning wave/instruction issue, stalls, LDS/VGPR/SGPR pressure, cache/memory behavior, branch and wait states, and scalar/vector/matrix activity.

`GRBMH_PERF_SEL` provides GRBMH-side selector values for count/user-defined and graphics/compute front-end, command, GE, and RLC busy states.

### SX, DB, Pixel Pipe, And Depth/Stencil State

SX enums include `SX_BLEND_OPT`, `SX_DOWNCONVERT_FORMAT`, `SX_OPT_COMB_FCN`, and `SX_PERFCOUNTER_VALS`. They define color blend optimization behavior, render-target export down-conversion formats, optimization-combine functions, and SX counter events for PA/SPI/SX/CB/DB interactions, exports, stalls, wave lifetimes, discard cases, and end-of-wave signals.

Depth/stencil and DB state enums include `CompareFrag`, `ConservativeZExport`, `DbMemArbWatermarks`, `DbPRTFaultBehavior`, `DbPSLControl`, `ForceControl`, `GLCompressionMode`, `OreoMode`, `StencilOp`, `ZLimitSumm`, `ZModeForce`, `ZOrder`, and `ZSamplePosition`. These values encode fragment compare functions, conservative Z-export promises, DB memory-arbiter watermark sizes, PRT fault result behavior, PSL control, force enable/disable/default behavior, GL compression/bypass modes, OREO ordering, stencil operations, Z-limit summary forcing, early/late/re-Z forcing, Z test ordering, and center/centroid sample position selection.

`PerfCounter_Vals` is the DB performance selector enum. Its 384 values cover SC-to-DB tile/quad/wave traffic, depth/stencil cache hits and misses, tile and quad stalls, Z/stencil read/write paths, pre-Z/post-Z sample and quad pass/fail counts, compression/decompression and fast-clear paths, HiZ/HiS behavior, SX/DB export formats, RMI request/return/ack traffic, VRS rates, PWS stalls, OREO table/cache events, and backend conflict or liveness stalls.

`PixelPipeCounterId`, `PixelPipeStride`, and `RingCounterControl` describe pixel-pipe counter selection and result layout: occlusion count slots, screen min/max extent counters, 32/64/128/256-bit strides, and split/ring-0/ring-1 counter routing.

### SU Boundary Enum

The chunk begins `SU_PERFCNT_SEL` at line 20281 and includes its first 209 selector values through `PERF_PH_SEND_4_SC` at line 20490. The enum continues after this chunk to line 20530. Covered values include PA/clip/SU primitive input and output counts, null/event/EOP flags, clipping and culling reasons, PASX/CLPR/CLIP/SU busy-starved-stalled state, per-shader-engine primitive-filter/output/null/stalled counters for SE0 through SE5, small-primitive culling histograms, SC qualified-send busy/not-busy events, PA FIFO-full signals, ENGG CSB/index/position request/return stalls, GE/SPI memory full/empty state, and PH send/output primitive counts for up to four scan converters.

## Important APIs And Integration Points

The API surface is the enum type and enumerator namespace:

- `typedef enum <Name> { ... } <Name>;` creates a C enum type for register field values or performance event IDs.
- Individual enumerators, such as `SC_SRPS_WINDOW_VALID`, `TC_OP_READ`, `SPI_PERF_GS_BUSY`, `SQ_PERF_SEL_NONE`, `DB_PERF_SEL_SC_DB_tile_sends`, `STENCIL_KEEP`, and `PERF_PAPC_SU_OUTPUT_PRIM`, are the constants consumers pass into register programming paths.

These definitions integrate with AMDGPU register programming for SOC24/GC 12 hardware. Typical consumers are graphics initialization, command/state packet construction, performance counter selection, debugfs/perf tooling, shader debugging, cache/watchpoint setup, raster/binning/VRS setup, texture/sampler descriptor programming, DB/SX state programming, and RAS/EDC diagnostics. In-tree users generally combine these enum values with companion files such as GC register offset headers, shift/mask headers, generated packet definitions, and AMDGPU helpers for `RREG32`, `WREG32`, `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15 register offsets, and command processor packet emission.

The path sits under a `ceph-client` source mirror, but the file is AMDGPU DRM hardware metadata, not Ceph distributed-filesystem logic.

## Control Flow

There is no runtime control flow in this chunk. Runtime behavior appears in code that selects one of these values and writes it into a hardware field, command stream packet, performance counter select register, or resource descriptor.

The implied control flow for a performance-counter user is:

1. Choose the hardware block and counter register, such as SC, SPI, SQ, TCP, GL1, GL2, SX, DB, PH, PC, TD, TA, or SU.
2. Write an enum value from the matching selector table into that block's event-select field.
3. Enable, sample, stop, and read the hardware counter through the block-specific performance-monitoring sequence.
4. Decode the result using the same enum domain so profiling tools can label the event correctly.

The implied control flow for state programming is to map a driver-visible state, API state, or command-stream packet field onto the corresponding enum value, pack it into the register or descriptor field using generated masks/shifts, and submit or write it through AMDGPU's normal register or ring path.

## State And Persistence Behavior

This header persists no software state. It describes values for stateful hardware registers, packets, descriptors, counters, and debug/status paths. Persistence is therefore owned by the hardware block and the driver code that programs or restores it.

State represented by this chunk includes raster/binning/VRS modes, shader export and sample modes, memory and cache policy bits, texture sampler and resource descriptor fields, shader debug/indirect command controls, watchpoint modes, DB/SX/Z/stencil policy, pixel-pipe counter selection, and many performance counter mux selections.

Performance counter select values remain in their hardware select fields until overwritten, reset, power-gated, or restored during GPU reset and suspend/resume handling. State descriptor values may live in command streams or GPU memory descriptors rather than MMIO registers. Some enum domains represent read-only status decodes or event classes rather than writable control state. This header does not encode access permissions, reset values, sticky behavior, or side effects.

## Dependencies

The chunk depends on the surrounding generated AMDGPU hardware-description set:

- Companion SOC24/GC register offset headers provide addresses for registers that consume these values.
- Shift/mask headers define bit positions for fields whose legal values are named here.
- Command processor packet and resource descriptor definitions define where state values are embedded in command streams or descriptors.
- AMDGPU KMS, Mesa/userspace-facing state translation, KFD, debug/perf tooling, and RAS/EDC code may rely on matching numeric values when programming hardware or decoding diagnostics.

Generated naming and numeric encodings are the contract. Renaming an enumerator breaks compile-time users; changing a numeric value can compile cleanly but program a different hardware behavior or count a different event.

## Risks And Edge Cases

- Boundary incompleteness: `PH_PERFCNT_SEL` starts before this range and `SU_PERFCNT_SEL` ends after it. A merged report must account for the missing starts/ends before treating them as complete enums.
- Event-selector drift: large tables such as `SC_PERFCNT_SEL`, `SPI_PERFCNT_SEL`, `SQ_PERF_SEL`, `PerfCounter_Vals`, `TA_PERFCOUNT_SEL`, `TD_PERFCOUNT_SEL`, `GL2C_PERF_SEL`, and `SU_PERFCNT_SEL` are dense. One inserted, deleted, or renumbered value can silently make profiling or debug data misleading.
- Cross-block namespace similarity: many blocks expose similarly named busy, stall, FIFO, read, write, hit, miss, and wave events. Using an enum value from the wrong block may still fit the field width while selecting an unrelated event.
- Hardware generation specificity: these SOC24 values should not be assumed valid for older SOC15/SOC21/Navi/Vega headers unless the generated database shows exact compatibility.
- Side-effectful debug controls: `SQ_IND_CMD_CMD` and `SQ_IND_CMD_MODE` include halt, resume, fatal-halt, and single-step controls. Incorrect use can disrupt running waves or leave shader hardware in a debug state.
- Memory/cache policy hazards: TC/TCP/GL/cache operation, compression, and address-mode enums affect memory ordering, compression, eviction, and fault behavior. Bad values can create data corruption, missed faults, or severe performance regressions.
- Rendering correctness hazards: VRS, binning, raster map, texture filtering, Z/stencil, conservative Z, blend optimization, down-conversion, and compression enums directly affect rendered output. Incorrect mappings may only show under specific formats, sample counts, VRS rates, or depth/stencil state combinations.
- Status-vs-control ambiguity: some domains name status or event IDs rather than writable controls. Consumers need the companion register spec to know whether a field is writable, read-only, sticky, self-clearing, or packet-only.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for SOC24/GC 12 AMDGPU code paths that include `soc24_enum.h`, catching missing or renamed enum symbols.
- Mechanical comparison against AMD's authoritative generated register database, especially numeric monotonicity and intentional gaps in large performance selector tables.
- Perf-counter smoke tests for SC, PH, SPI, SQ/SQG, PC, TA/TD/TCP, GL1/GL2, SX, DB, and SU blocks, verifying that selected events respond to workloads designed to exercise the named block.
- Rendering conformance tests covering VRS rates/combiners, binning modes, raster maps, texture clamp/filter/depth-compare modes, blend optimization/down-conversion, Z ordering, stencil operations, conservative Z export, and compression controls.
- Shader debug tests that exercise SQ indirect halt/resume/single-step commands only in controlled debug paths and verify waves recover.
- Cache and memory tests that cover TC/TCP operation classes, watch modes, compression bypass/override, cache policy, write compression disable, fault/NACK decoding, and address/request modes.
- GPU reset and suspend/resume tests that verify hardware state or descriptor programming using these values is restored or intentionally reinitialized.
- Cross-generation compile and runtime checks that ensure SOC24-specific enum values are not accidentally reused by incompatible ASIC families.

## Cross-Chunk Notes

Lines 14961-15553 are the tail of `PH_PERFCNT_SEL`; the first PH selector values are in the previous chunk. Lines 20281-20490 are the start and majority of `SU_PERFCNT_SEL`; the remaining SU selector values and the next `RMIPerfSel` enum begin after this chunk. The final merged file-level research should reconcile these boundaries before summarizing complete enum sizes.

### subset-b-003503: lines 20491-21073

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h lines 20491-21073

## Scope And Purpose

This chunk is the final section of AMD's generated `soc24_enum.h` hardware enum header. It starts at the tail of the `SU_PERFCNT_SEL` enum, defines complete selector enums for RMI, UTCL1, GC EA SE, and LSDMA performance counters, defines the `ROM_SIGNATURE` constant, defines `EFC_SURFACE_PIXEL_FORMAT`, and closes the `_soc24_ENUM_HEADER` include guard.

The file is under a `ceph-client` source mirror, but this chunk is AMDGPU register and packet metadata for SoC24-era AMD GPUs. It does not implement Ceph filesystem behavior, allocate memory, call functions, branch, lock, perform MMIO, or persist software state. Its purpose is to give driver and tooling code stable symbolic names for numeric hardware encodings that are written into register fields, command packets, firmware interfaces, or decoded from hardware-visible values.

## Important APIs, Types, And Constants

The exported API in this range is a C enum/define namespace:

- `SU_PERFCNT_SEL` tail entries `PERF_OUTPUT_PRIM_1_SC` through `PERF_PA_BUSY`, which complete shader/geometry front-end and primitive/output performance counter event IDs.
- `RMIPerfSel`, whose `RMI_PERF_SEL_*` entries select RMI performance events, including RB-to-RMI write/read requests, per-client-ID request/return valid events, NACKs, FIFO occupancy/empty/idle/starve/stall/busy events, RMI-to-TC requests and returns, TCIW formatter/reorder activity, early write acknowledgements, and consumer probe-generator handshakes.
- `UTCL1PerfSel`, whose `UTCL1_PERF_SEL_*` entries select UTCL1 TLB/cache events: requests, hits, misses, miss-handler activity, UTCL2 requests/returns, XNACK retry and fault returns, invalidation requests/acks, bypass requests, page-size bucket hits/returns, per-cache-core request/stall/collision/eviction counters, and ALOG interrupt/cache/PMM-credit events.
- `GC_EA_SE_PERFCOUNT_SEL`, whose `GC_EA_SE_PERF_SEL_*` entries select graphics client export-address/shared-engine memory traffic events. The enum covers DRAM, GMI, and IO read/write request groups, chained requests, request sizes, latency start/end markers, SARB virtual-channel traffic, return-valid/probe activity, MAM ARAM/DBIT hit/evict/query/flush/aflush events, coherent size requests, and RW turn-around metrics.
- `LSDMA_PERF_SEL`, whose `LSDMA_PERF_SEL_*` entries select low-speed SDMA/copy-engine performance events. The enum covers ring-buffer and indirect-buffer state, executor idle, MC read/write traffic, semaphore and interrupt response paths, command packet counting, copy-engine and F32 paths, context changes and doorbells, UTCL1/ATCL2 invalidation/XNACK/ACK events, MMHUB request/return events, operation start/end matching, CE busy windows, perfcnt triggers, DRAM ECC, and generated NACK errors.
- `ROM_SIGNATURE`, fixed to `0x0000aa55`, the conventional ROM image signature value used when probing or validating option ROM/VBIOS content.
- `EFC_SURFACE_PIXEL_FORMAT`, whose `EFC_*` entries encode surface pixel formats, including 16-bit and 32-bit RGB(A), YCrCb/YCbCr channel orderings, 10/12/16-bit component formats, float/unorm/snorm variants, 4:2:0 planar formats, 4:2:2 packed formats, packed 11/10-bit RGB/BGR formats, ACrYCb/CrYCbA 10-bit formats, and mono 8/10/12/16 formats.

All enum values are explicit hexadecimal constants. That makes the names an ABI-like mapping to hardware selector values rather than compiler-chosen C enum ordinals.

## Control Flow And Runtime Behavior

There is no runtime control flow in this chunk. Runtime behavior is indirect:

1. SoC24 AMDGPU/KFD source files include `soc24_enum.h` together with SoC24 register offset/mask headers.
2. Driver, debug, profiling, or firmware-interface code selects one of these enum values when programming a performance counter's event-select field, validating a ROM signature, or describing a surface/pixel format.
3. Hardware interprets the programmed numeric value and routes the corresponding event, status source, or data-format interpretation.

The direct include users visible in this tree include `amdgpu/gfx_v12_0.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/gmc_v12_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/mmhub_v4_1_0.c`, and `amdkfd/kfd_device_queue_manager_v12.c`. This chunk's specific enum names are not directly referenced elsewhere in the local tree, which is consistent with a generated all-in-one hardware namespace: consumers include the complete header while using only the symbols relevant to a given ASIC path or diagnostic build.

## State And Persistence Behavior

The header stores no software state. The state represented by these constants lives in hardware blocks or ROM/image data:

- Performance selector enums become transient or programmed hardware state when software writes event IDs into performance counter select registers. Counter state then persists in the GPU block until reprogrammed, reset, power-gated, or restored by driver suspend/resume handling.
- RMI, UTCL1, GC EA SE, and LSDMA events observe hardware queues, cache/TLB behavior, memory-fabric traffic, invalidation handshakes, request/return paths, stalls, busy/idle cycles, and error conditions. Some selected events are instantaneous pulses, some count cycles, and some accumulate occupancy or latency-style values depending on the owning counter block.
- `ROM_SIGNATURE` is not state by itself; it is the expected little-endian marker in ROM/VBIOS data used to distinguish a valid image header from unrelated memory.
- `EFC_SURFACE_PIXEL_FORMAT` values describe persistent format fields in surfaces, scanout/copy/display paths, firmware tables, or packet/register payloads that reference these encodings. The header does not define layout stride, tiling, endian, modifier, or colorimetry policy.

Access type and side effects are not encoded in the enum names. For performance counters, the register programming model defines whether a selector can be changed while counting, whether counters must be stopped/reset first, and how overflow/latch behavior works. For ROM and pixel-format use, validation and compatibility rules live in the consumer code and hardware specification.

## Dependencies And Integration Points

This chunk depends on the broader generated SoC24 register header set. `soc24_enum.h` supplies numeric encodings, while other headers under `drivers/gpu/drm/amd/include/asic_reg/` supply register offsets, masks, and reset values. AMDGPU helper layers then compose these constants into register writes or packet fields.

Important integration surfaces include:

- GFX performance monitoring and profiling paths that select `SU_PERFCNT_SEL` tail events for shader/primitive pipeline observation.
- Memory-fabric and render-backend diagnostics that can use `RMIPerfSel` to attribute RB/RMI/TC request, return, NACK, FIFO, stall, and probe-generator behavior.
- GPU virtual-memory and MMU/TLB diagnostics that can use `UTCL1PerfSel` to inspect UTCL1 hit/miss behavior, UTCL2 interaction, invalidation latency, cache-core behavior, and translation fault/XNACK activity.
- Graphics memory-export and shared-engine performance tooling that can use `GC_EA_SE_PERFCOUNT_SEL` to measure DRAM/GMI/IO request mix, latency windows, SARB traffic, MAM flush/query behavior, and coherent request sizes.
- SDMA/copy-engine profiling, reset triage, and memory-translation debugging that can use `LSDMA_PERF_SEL` to isolate ring/IB pressure, MC/MMHUB request flow, ATCL2/UTCL1 invalidation and XNACK returns, CE/F32 paths, doorbells, command windows, ECC, and NACK-generation errors.
- ROM/VBIOS parsing or validation code that compares image contents with `ROM_SIGNATURE`.
- Display, encode/copy, or firmware table paths that need a SoC24 enum value for `EFC_SURFACE_PIXEL_FORMAT`.

Because these are generated hardware encodings, they must remain synchronized with the SoC24 hardware database and any firmware or tools that consume the same numeric values. Mixing selector values from another ASIC generation can compile cleanly but route counters to the wrong internal signal.

## Risks And Edge Cases

- Numeric drift is high impact. A wrong enum value can program a valid but unintended event selector, producing misleading performance data without an obvious build failure.
- The chunk starts in the middle of `SU_PERFCNT_SEL`; the final report must merge with the previous chunk before treating the SU selector enum as complete.
- Several enum families are dense but have intentional gaps, such as `LSDMA_PERF_SEL` skipping values around `0x16`, `0x17`, `0x24`, `0x2c`, and `0x2d`, and `EFC_SURFACE_PIXEL_FORMAT` leaving ranges unused. Filling gaps or renumbering entries would break the hardware ABI.
- Many performance events have similar per-client or per-cache-core names. Copy/paste mistakes between CID0-CID7, cache core 0-3, read/write, request/return, or start/end events can silently invert diagnostic conclusions.
- Performance counter semantics are block-specific. Some selectors count cycles, some count pulses, some count sizes or latency windows, and some may require an accompanying counter mode. The enum alone is not enough to interpret raw counter values.
- RMI, UTCL1, and LSDMA events touch memory translation, invalidation, XNACK, NACK, MMHUB, and fault paths. Misinterpreting those counters can lead to incorrect conclusions about IOMMU, VM fault, or DMA-engine behavior.
- `ROM_SIGNATURE` should be checked with correct byte ordering and bounds-checked ROM access. A matching signature alone is not a full VBIOS validation.
- `EFC_SURFACE_PIXEL_FORMAT` names encode component order and bit-depth, but not all display/color metadata. Consumers still need to pair these values with plane layout, pitch, tiling/modifier, color space, and hardware block support.

## Test And Validation Signals

Useful validation is mostly compile-time, generated-header comparison, and hardware/runtime diagnostics:

- Build AMDGPU and KFD paths that include `soc24_enum.h`, especially GFX12, GMC12, GFXHUB12, MMHUB 4.1, and KFD queue-manager code, to catch syntax or missing-symbol regressions.
- Mechanically compare this enum range against the authoritative SoC24 hardware register database or generated upstream header to confirm each explicit numeric value and intentional gap.
- For performance selectors, run hardware perf-counter smoke tests that program representative events from each family and confirm counters change under matching workloads: geometry/primitive workloads for SU tail events, render-backend/memory traffic for RMI and GC EA SE, VM pressure and invalidation workloads for UTCL1, and SDMA copy/fill/doorbell/IB workloads for LSDMA.
- Validate read/write event pairs and per-client/per-core selectors by using asymmetric workloads where one CID, cache core, or engine path is expected to dominate.
- Exercise fault and retry paths, where practical, to check UTCL1 XNACK/fault, LSDMA ATCL2 return, DRAM ECC, and NACK-generation event visibility.
- Check ROM parsing paths with valid and invalid ROM images to ensure `ROM_SIGNATURE` is used as an initial marker rather than a complete integrity check.
- Validate EFC format mappings with display/copy/firmware tests that cover RGB(A), YUV planar, YUV packed, high-bit-depth, float, and mono formats, watching for swapped channels, wrong bit significance, or unsupported-format fallbacks.

## Cross-Chunk Notes

This is the final chunk of `soc24_enum.h`; it closes the include guard at line 21073. The previous chunk is required for the beginning and main body of `SU_PERFCNT_SEL`, while this chunk completes it and then covers the final enum/define families. A later merge/reconciliation pass should combine all chunks for this source file before making whole-file claims about the SoC24 enum namespace.
