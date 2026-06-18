# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h lines 8446-14863

## Scope

This chunk is a generated-style register enumeration section for Navi10 AMDGPU hardware. It contains no executable functions, but it is an important ABI-like mapping layer: enum names and numeric constants encode register field values used by display, audio, shader, geometry, cache, color-buffer, and performance-counter programming paths elsewhere in the driver stack.

The chunk starts in the DCIO display I/O enum block and ends at the beginning of `GL1C_PERF_SEL`, with that final enum continuing past the assigned line range. The complete source file must be merged with adjacent chunks before making whole-file claims.

## Purpose

The primary purpose is to provide named constants for hardware register fields in Navi10:

- DCIO/DCIOCHIP values for display I/O routing, HPD, AUX/DDC/I2C pads, PHY lane selection, vsync muxing, GPIO masks, reset asserts, impedance calibration, and reference clock source selection.
- AZ/Azalia audio controller, endpoint, root, input endpoint, and stream descriptor values for HD Audio controller operation, codec parameters, stream synchronization, CORB/RIRB DMA rings, immediate commands, converter formats, digital converter control, pin widgets, multichannel mute, HBR capability, and audio memory power control.
- DSC, DSCCIF, DSC_TOP, CNV, and WBSCL display pipeline values for display stream compression, writeback, scaler coefficient RAM addressing, pixel formats, bpc selection, stereo/interlaced/frame capture state, warmup modes, CRC, backpressure, and memory power states.
- DPCSRX/DPCSTX/RDPCSTX link and PHY values for DisplayPort receive/transmit clocks, DVI link modes, RDPCS soft resets, FIFO and interrupt masks, SRAM/clock controls, DP alt-mode toggles, memory power, PHY reference/termination/rate/width, and test clock muxing.
- CB/color-buffer values for blend factors, combine functions, CB modes, CMASK addressing/codes, memory arbitration, source export formats, and a large `CBPerfSel` selector table.
- TC and GL2 memory/cache operation values for read/write/atomic/cache invalidate operations, fault/nack encodings, and EA client IDs.
- SPI and SQ shader front-end values for sample/fog/point-sprite controls, shader export formats, clock-gating modes, texture/sampler state, resource types, selectors, wave types, performance counters, indirect wave commands, ECC/error sources, rounding, address/retry/alignment modes, thread-trace token masks, watch modes, and scheduler modes.
- COMP, GE/VGT/WD, GB, and GLX values for command stream data/control field widths, primitive topology, draw initiator modes, pipeline events, tessellation/geometry stage modes, performance counters, EDC behavior, and GL1/CHA performance monitor selection.

## Important Types And Constants

### DCIO and DCIOCHIP

Key types include `DCIO_DIO_OTG_EXT_VSYNC_MUX`, `DCIO_DIO_EXT_VSYNC_MASK`, `DCIO_DSYNC_SOFT_RESET`, `DCIO_DACA_SOFT_RESET`, `DCIO_DCRXPHY_SOFT_RESET`, `DCIO_DPHY_LANE_SEL`, `DCIO_DPCS_INTERRUPT_TYPE`, `DCIO_DPCS_INTERRUPT_MASK`, `DCIO_DC_GPU_TIMER_READ_SELECT`, `DCIO_IMPCAL_STEP_DELAY`, and `DCIO_UNIPHY_IMPCAL_SEL`.

`DCIOCHIP_*` enums then describe pad modes and electrical behavior: `DCIOCHIP_HPD_SEL`, `DCIOCHIP_PAD_MODE`, `DCIOCHIP_AUXSLAVE_PAD_MODE`, polarity inversion, powerdown permission, GPIO/I2C mask and drive controls, 2/4/5-bit enable masks, 27 MHz reference source selection, DVO VREF controls, SPDIF mode, AUX/I2C slew and spike controls, voltage/current/resistance tuning, receiver selection, and AUX/I2C power/readiness flags.

Several definitions intentionally encode bit masks rather than dense indexes, for example `DCIOCHIP_MASK_4BIT_ENABLE = 0xf`, `DCIOCHIP_5BIT_ENABLE = 0x1f`, and `DCIOCHIP_2BIT_ENABLE = 0x3`. These must be treated as field values, not enum ordinals.

### Azalia Audio

The AZ controller section includes generic enable/status aliases, `AZ_GLOBAL_CAPABILITIES`, global control reset/flush/unsolicited response fields, state-change status, stream synchronization enums for streams 0 through 15, CORB/RIRB ring reset and size fields, immediate-command status, and DMA position buffer enable.

The AZ endpoint sections define codec converter format fields for stream type, base rate, multiple, divisor, bits per sample, and channel count for both output and input endpoints. Digital converter state includes channel status bits, non-audio/copy/pre/validity flags, digital enable, and keepalive/silent stream. Pin-control enums describe widget output/input enable, unsolicited response enable, downmix inhibition, multichannel mute groups, pair-vs-single multichannel mode, audio descriptor format codes, and HBR capability.

The F0 endpoint and input endpoint parameter sections mirror HD Audio capability registers. They enumerate audio widget type, LR swap, power control, digital/analog, connection lists, unsolicited response, processing, striping, format override, amplifier presence, audio channel capability, pin EAPD/DP/HDMI/balanced/input/output/headphone/jack/trigger/impedance capabilities. Many names end in `_RESERVED` because the hardware field value exists even when the value is not a supported runtime configuration.

`MEM_PWR_FORCE_CTRL`, `MEM_PWR_DIS_CTRL`, `MEM_PWR_SEL_CTRL`, and related variants describe audio memory light-sleep, deep-sleep, and shutdown controls. `CC_RCU_DC_AUDIO_*_PORT_CONNECTIVITY` values map display audio routing ports.

### DSC, CNV, WBSCL, DPCS/RDPCS

`DSCC_*` and `DSCCIF_*` values cover DSC slice reset bits, DSC major/minor version fields, line-buffer depths, bits per component, enable state, memory power force/state/disable, and compressed input pixel format. `ENABLE_ENUM`, `CLOCK_GATING_DISABLE_ENUM`, and `TEST_CLOCK_MUX_SELECT_ENUM` provide top-level DSC enable, clock-gate polarity, and test clock selection.

`CNV_*` and `WB_*` enums configure display writeback/conversion: writeback enable, clock/memory power gating, test clock selection, writeback scaler memory states, output bpc, capture rate/enable, crop, interlace, stereo eye/type/polarity/split, update pending/lock, CSC bypass, CRC controls, soft reset, and GMC warmup. `WBSCL_*` then names coefficient RAM tap pairs, phases, filter types, scaler mode, pixel depth, coefficient RAM bank select/read select, tap enable, tap counts, status clear/mask, interrupt source type, CRC masks, backpressure counter enable, and outside-pixel strategy.

`DPCSRX_RX_CLOCK_CNTL_DPCS_SYMCLK_RX_SEL`, `DPCSTX_DVI_LINK_MODE`, and the `RDPCSTX_*` / `RDPCS_*` enums map DP/PCS link controls: CBUS/SRAM/TX resets, FIFO enables, refclk and div2 clock controls, SRAM clock gates/bypass/status, DP alt-mode toggle interrupts and masks, memory power modes, PHY reference range, CR/JTAG muxing, SRAM load/init completion, DP TX termination, power state, rate, width, detect result, MPLL divisors, and RDPCS test-clock selectors.

### CB, TC, GL2

The CB section includes `CBMode`, `BlendOp`, `CombFunc`, `BlendOpt`, `CmaskCode`, `MemArbMode`, `CBPerfOpFilterSel`, `CBPerfClearFilterSel`, `CBPerfSel`, `CmaskAddr`, and `SourceFormat`. These are used by color-buffer and render-backend paths for render target mode, blend factors, blend equation selection, blend optimization overrides, CMASK state, arbitration policy, and performance counter selection.

`CBPerfSel` is especially large and encodes detailed probes for CB busy state, tile/quad valid-ready paths, cache hits/misses/stalls/flushes, DCC cache and key/compression-ratio states, memory controller request/in-flight counts, event signals, blend optimization opportunities, DCC compress/decompress TID flow, split causes, NACKs, early write returns, and EOP/context done signals. Consumers must preserve the exact numeric selector values.

`TC_OP_MASKS`/`TC_OP` and `GL2_OP_MASKS`/`GL2_OP` describe memory operation encodings: read/write, 32-bit and 64-bit atomics with and without return, floating-point atomics, flush-denorm variants, cache invalidation/writeback operations, metadata invalidation, probe/filter operations, no-op acks, and reserved holes. `TC_NACKS`/`GL2_NACKS` provide page/protection/data fault encodings. `TC_EA_CID` and `GL2_EA_CID` map error attribution to clients such as RT, FMASK, DCC, TCP/SQC, CPF/CPG, IA, WD, PA, SDMA, RLC, CP, UTCL2, Z/stencil, and HTILE.

### SPI and SQ

SPI enums cover sample selection (`SPI_SAMPLE_CNTL`), fog mode, point-sprite coordinate override, shader export formats, clock gate sequencing/multipliers, load-balancing wave selection, and a large `SPI_PERFCNT_SEL` table. `SPI_PERFCNT_SEL` spans vertex, geometry, hull, compute, pixel, export, resource allocation, LDS/RA pressure, clock-gating, pixel allocation, NGG, shader write cache, and ES/LS counters.

SQ enums cover sampler/texture behavior (`SQ_TEX_CLAMP`, XY/Z/MIP filtering, anisotropy, depth compare, border color), resource descriptor types (`SQ_RSRC_BUF_TYPE`, `SQ_RSRC_IMG_TYPE`, `SQ_RSRC_FLAT_TYPE`), image filter mode, component selection (`SQ_SEL_XYZW01`), out-of-bounds behavior, wave type, performance selection, power counters, indirect wave commands, command broadcast scope, EDC information source, floating-point rounding, interrupt word encoding, instruction-buffer state, instruction-stream state, wave instruction-buffer ECC state, memory address/retry/alignment mode, thread-trace masks, thread-trace mode, wave-type filters, utilization timer, wavestart mode, runtime frequency, watch modes, and wave scheduler modes.

The SQ block also defines non-enum register-layout constants:

- `SQIND_*` offsets and sizes for global/local registers, wave hardware registers, SGPRs, and VGPRs.
- Decoder address windows such as `SQ_GFXDEC_*`, `SQDEC_*`, `SQPERFSDEC_*`, `SQPERFDDEC_*`, `SQGFXUDEC_*`, and `SQPWRDEC_*`.
- Dispatcher and maximum program register counts (`SQ_MAX_PGM_SGPRS`, `SQ_MAX_PGM_VGPRS`).
- Exception bit positions for VALU exceptions, address watches, memory violation, and high address-watch bits.
- Hardware inserted instruction IDs for ECC interrupt messages, thread-trace new PC, traps, kill sequence, SPI WREXEC, and host register traps.
- `SIMM16_WAITCNT_*` field partitions and dependency-counter field sizes.
- `SQ_EDC_FUE_CNTL_*` selectors for SIMD, SQ, LDS, TD, TA, and TCP error handling.

`SQ_PERF_SEL` is a broad performance selector table for waves, items, quads, events, wait reasons, instruction categories, replay, XNACK, issue and stall cycles, VMEM/SMEM/LDS/TEX/FLAT behavior, user-defined selectors, UTCL0/UTCL1 translation and permission events, TTrace, SQC power/cache/TLB events, and dummy range sentinels. It intentionally mixes `SQ_`, `SQG_`, `SQC_`, and `SP_` selector ranges in one enum.

### COMP, GE/VGT/WD, GB, GLX

The COMP section defines `CSDATA_TYPE` and `CSCNTL_TYPE`, plus field-width constants for type/address/data partitions. These support encoded command stream data/control fields.

GE/VGT/WD enums describe draw and geometry front-end programming:

- Primitive output and input topology via `VGT_OUT_PRIM_TYPE`, `VGT_DI_PRIM_TYPE`, grouped primitive type/order, and tessellation output topology.
- Draw initiator source, major mode, index size, DMA swap/buffer type, output path, group conversion, GS mode/cut/output primitive type, cache invalidation policy, tessellation type/partition, distribution mode, factor zero/one detection, and shader-stage enable encodings.
- `VGT_EVENT_TYPE`, a command/event selector table for cache flushes, partial flushes, streamout, EOP/IB/context events, pipeline stats, thread trace, pixel pipe stats, suspend, NGG/legacy pipeline enable, and draw done.
- `GE_PERFCOUNT_SELECT`, a long geometry-engine performance selector table covering assembler, DMA, UTCL1/UTCL2, DS/ES/GS/HS/LS/VS pipeline state, table/ring high-water marks, thread groups, clipper paths, streamout, clock validity, NGG, TE, and stall/starvation signals.
- `WD_IA_DRAW_TYPE`, `WD_IA_DRAW_REG_XFER`, and `WD_IA_DRAW_SOURCE` for input assembler draw packet interpretation; `GSTHREADID_SIZE` defines a GS thread-id field width.

`GB_EDC_DED_MODE` configures data-error detection behavior as log, halt, or interrupt+halt. GLX-related performance selector enums include `CHA_PERF_SEL`, `CHC_PERF_SEL`, `CHCG_PERF_SEL`, and the beginning of `GL1A_PERF_SEL`/`GL1C_PERF_SEL`, covering cache hierarchy busy/stall/request/burst/in-flight/cycle counters. The assigned chunk ends after `GL1C_PERF_SEL_CORE_REG_SCLK_VLD`; remaining `GL1C_PERF_SEL` values continue in the following lines/chunk.

## Control Flow

There is no runtime control flow in this chunk. All declarations are compile-time constants. Runtime control flow exists in consumers that write or decode Navi10 registers using these values, typically through generated register headers, display/audio initialization code, command submission paths, power management sequences, performance counter setup, debug/tracing paths, and interrupt/error handlers.

The important "flow" implied by this chunk is hardware programming order in consuming code:

- Reset, clock, and power enums gate safe transitions for DCIO, Azalia, DSC, writeback, RDPCS, and shader blocks.
- Format/topology enums are selected before enabling stream, converter, shader, or draw paths.
- Event and performance selector enums are written to command/register fields before triggering samples or collecting counters.
- Status, fault, NACK, ECC, and completion enums are read back and interpreted by diagnostics or recovery paths.

## State And Persistence

This header persists hardware ABI knowledge in source form. The enum values are effectively persistent contracts with Navi10 silicon and firmware-visible register encodings. The values do not store runtime state themselves, but they define the legal and reserved state encodings for hardware registers.

Several state categories are visible:

- Binary enable/disable, assert/deassert, mask/unmask, reset/not-reset, run/not-run, set/not-set state.
- Multi-state power modes such as on, light sleep, deep sleep, shutdown, and forced memory power modes.
- Audio stream/ring state such as CORB/RIRB reset, stream stopped/not stopped, immediate command busy/result valid, and stream descriptor errors.
- Display/video state such as interlaced/progressive, stereo eye, update lock/pending, frame capture, CRC, and writeback scaler memory state.
- Shader and cache state such as wave type, wait counters, exception bit positions, EDC source, cache operation, NACK fault type, and trace/watch filters.
- Geometry command state such as draw source, index size, primitive topology, pipeline event type, and enabled shader stage roles.

Because the constants are used to encode/decode hardware state, renaming can break source users, and changing numeric values can break hardware programming even if compilation succeeds.

## Dependencies

This chunk depends only on C enum and preprocessor syntax. It has no includes or function calls in the visible range. Its real dependencies are external hardware documents or generated register metadata that define the numeric encodings.

Downstream dependencies are more important:

- Navi10 register headers and AMDGPU/DC code likely include this file to write register bitfields symbolically.
- Audio code paths depend on AZ/Azalia enums matching HD Audio controller and AMD display-audio endpoint encodings.
- Display Core paths depend on DCIO, DSC, CNV, WBSCL, DPCS/RDPCS constants for link training, AUX/DDC/I2C, writeback, compression, and PHY programming.
- Command processor, shader, cache, and performance-monitor paths depend on CB, TC, GL2, SPI, SQ, GE/VGT/WD, and GLX selectors.
- Debug, profiling, and trace tools depend on large performance selector tables and event IDs being stable.

## Integration Points

Integration is by inclusion and constant reference. Expected consumers include code that:

- Programs display I/O pads, hotplug detect, GPIO/I2C/AUX, vsync routing, and PHY resets.
- Configures HDMI/DP audio converters, stream descriptors, codec pins, pin capabilities, HBR behavior, and audio DMA ring state.
- Sets DSC/writeback/scaler pixel formats, memory power, CRC capture, and coefficient RAM indexing.
- Configures RDPCS/DP link clocks, PHY rates, widths, termination, reset, memory power, and DP alt-mode interrupt masks.
- Emits graphics command events (`VGT_EVENT_TYPE`) and draw initiator fields.
- Selects CB/SPI/SQ/GE/GL1 performance counters and interprets results.
- Handles cache operations, atomics, invalidations, NACK/fault attribution, EDC/ECC reporting, watchpoints, and thread trace.

## Risks And Edge Cases

- Numeric values are hardware register encodings. Any edit that renumbers, deduplicates, sorts, or "cleans up" enum values can silently corrupt device programming.
- Several enums are bit masks or field bit positions, not dense enum sequences. Examples include `DSCC_ICH_RESET_ENUM`, `TC_OP_MASKS`, `GL2_OP_MASKS`, `SQ_TT_TOKEN_MASK_*`, and 2/4/5-bit DCIOCHIP mask enums.
- Reserved values are intentionally present. Removing `_RESERVED` entries can make decode tables incomplete or shift assumptions in tools.
- Naming contains generated quirks and typos such as `MASIK`, `STEAM`, `PROCESING`, `CAPABLILITY`, `SLAVER`, mixed-case constants like `RDPCS_TEST_CLK_SEL_REF_DIG_FR_clk`, duplicate-ish sentinel names in `SQ_PERF_SEL`, and values whose labels are opposite to field polarity (`CLOCK_GATING_DISABLE_ENUM_ENABLED = 0`). These are compatibility risks, not cleanup opportunities.
- Some enum names are generic (`ENABLE_ENUM`, `POWER_STATE_ENUM`) and can collide if included in translation units with other generated headers. This is a known generated-header hazard.
- The chunk ends mid-definition for `GL1C_PERF_SEL`; merge logic must combine adjacent chunks before producing final per-file research.
- Large perf selector enums (`CBPerfSel`, `SPI_PERFCNT_SEL`, `SQ_PERF_SEL`, `GE_PERFCOUNT_SELECT`) are prone to off-by-one or truncated-table bugs if manually regenerated.

## Test Signals

Useful validation signals for code depending on this chunk:

- Compile coverage for all translation units including `navi10_enum.h`; this catches syntax breakage and duplicate-name conflicts.
- Static checks that selected known constants retain exact values, especially reset/power encodings, `VGT_EVENT_TYPE`, `TC_OP`, `GL2_OP`, and perf selector sentinels.
- Display bring-up tests covering HPD, AUX/DDC/I2C, DP/HDMI link training, vsync routing, DSC enablement, writeback, and audio over HDMI/DP.
- Audio tests covering stream start/stop, CORB/RIRB DMA, immediate commands, converter format programming, unsolicited response, HBR, and pin capability reporting.
- GPU command submission tests covering draw topology/index-size modes, VGT events, cache flush/invalidate events, shader wave scheduling/debug commands, and memory/cache atomics.
- Performance counter smoke tests for CB, SPI, SQ, GE, CHA/CHC/GL1 selectors, verifying that selector writes are accepted and counters change under known workloads.
- Error-injection or debug tests for NACK/fault decode, EDC/ECC source decode, thread trace, watchpoints, and SQ exception bit handling.

## Unresolved Cross-Chunk References

- `GL1C_PERF_SEL` begins at line 14860 and only the first three constants are inside this assigned chunk. The following chunk is required to document the rest of the enum.
- Earlier chunks define the beginning of `navi10_enum.h` and may establish include guards, generation metadata, broader enum naming conventions, and preceding DCIO groups. This chunk alone cannot determine whole-file generation provenance.
