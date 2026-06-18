# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003490`: lines 1-8445, `Docs/researches/chunks/subset-b-003490_research.md`
- `subset-b-003491`: lines 8446-14863, `Docs/researches/chunks/subset-b-003491_research.md`
- `subset-b-003492`: lines 14864-20395, `Docs/researches/chunks/subset-b-003492_research.md`
- `subset-b-003493`: lines 20396-22764, `Docs/researches/chunks/subset-b-003493_research.md`

## Chunk Research

### subset-b-003490: lines 1-8445

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h lines 1-8445

## Scope And Purpose

This chunk is the first 8,445 lines of AMD's generated Navi10 hardware enum header. It defines compile-time `typedef enum` constants that encode numeric values for GPU, display, memory-surface, timing-generator, link-encoder, AUX, I2C/DDC, and DCIO register fields. It does not define functions, structs with storage, variables, locks, allocations, sysfs/debugfs surfaces, or direct MMIO access.

The path is under a `ceph-client` source mirror, but the file is AMDGPU register metadata, not Ceph filesystem logic. Runtime behavior comes from AMDGPU display, memory-controller, hub, and graphics code that includes this header and writes these enum values through generated register accessor macros and ASIC-specific register-offset/mask headers.

This chunk contains 779 complete enum definitions. It also includes the file license, include guard, and a non-driver-build compatibility block that maps OpenGL-style blend names such as `GL__ZERO` to generated `BLEND_*` values. The chunk ends at the comment for `DCIO_DIO_OTG_EXT_VSYNC_MUX`; the actual `typedef enum DCIO_DIO_OTG_EXT_VSYNC_MUX` begins on line 8,446 and is outside this chunk.

## Important APIs, Types, And Constants

The exported API is the enum namespace itself. Consumers use these names as raw field values when packing hardware register fields with macros such as `REG_SET_FIELD`, `REG_UPDATE`, `REG_SET`, and generated DC register tables. Important families in this chunk include:

- GDS and general chip enums: `GDS_PERFCOUNT_SELECT` selects global data share performance events across shader engines/shader arrays plus GWS events. `GATCL1RequestType`, `UTCL1RequestType`, `UTCL1FaultType`, `UTCL0RequestType`, `UTCL0FaultType`, `VMEMCMD_RETURN_ORDER`, GL/TCC/GL2 cache policies, memory types, RMI client IDs, read/write cache policies, generic perfmon modes, surface array/tiling forms, DSM error-injection choices, and HDP endian modes define non-display hardware field values.
- Converter and cursor front-end enums: `CNVC_ENABLE`, `CNVC_BYPASS`, `DENORM_TRUNCATE`, `PIX_EXPAND_MODE`, `SURFACE_PIXEL_FORMAT`, `XNORM`, `COLOR_KEYER_MODE`, `CUR_ENABLE`, `CUR_MODE`, and related cursor ROM/expansion/pending enums describe pixel expansion, color keying, cursor formats, and conversion state.
- Display scaler and color management enums: DSCL entries such as `SCL_COEF_FILTER_TYPE_SEL`, `DSCL_MODE_SEL`, `SCL_AUTOCAL_MODE`, coefficient RAM selectors, boundary modes, line-buffer/OBUF controls, plus CM/CMC entries for bypass/enables, LUT config/mode/RAM selection, number of segments, internal CSC, gamut remap, coefficient format, and 3D LUT size/bit-depth.
- DPP and DC perfmon enums: DPP test-clock and CRC source/input selectors are followed by `PERFCOUNTER_*` and `PERFMON_*` values for counter value slice selection, increment mode, run/count-off controls, interrupt enable/type, counted value type, hardware stop selectors, counter state machines 0-7, and global/local state selection.
- HUBP/HUBPREQ/HUBPRET memory-display enums: rotation/mirror, pipe/bank/shader-engine geometry, swizzle modes, pipe interleave, render-backend counts, dimension type, metadata linear/alignment, array/tile/pipe config, micro-tile mode, tile split, bank width/height, macro tile aspect, swath height, PTE/DPTE/MPTE group sizes, blank/disable/no-outstanding status, VTG selection, TMZ/DCC flags, flip modes, surface update locks, interrupt controls, detile crossbar routing, DET/PIXCDC memory sleep, cursor memory/address modes, dynamic metadata status, and XFC pixel/frame/chunk choices.
- Composition, output, and pattern-generator enums: MPC config and OCSC enums cover CRC modes, vupdate lock bits, rate-control disable, denorm modes, output CSC coefficient formats, and CSC modes. MPCC enums cover blend/pass-through modes, per-pixel/global alpha modes, premultiplied-alpha flags, stereo/subsampling modes, stall interrupt ack/mask, background color bit depth, OGAM LUT RAM selection, and OGAM mode. DPG and FMT enums cover display pattern generation, dynamic range, bit depth, field polarity, pixel encoding/subsampling, bit reduction, truncation, spatial/temporal dithering/FRC, clamp formats, memory power, frame/random control, and PTI polarity.
- OPP and OTG timing enums: OPP pipe clock/bypass and CRC controls are followed by a large OTG block for start/disable points, field-number polarity, read-request disable, SOF pull, dynamic refresh rate min/max selection, trigger A/B source and pipe selections, flow-control sources and polarity, stereo, blanking, interlace, forced vsync, snapshots, update locks, double buffering, DRR average frames, vertical interrupts, CRC source/data modes, external timing sync, static-screen signaling, 3D structure, sync polarity, repetition counts, master/DRR update lock selection, GSL/master mode, PTI, and pipe abort.
- DMCUB/RBBMIF/IHC/DMU/DCCG/HPD enums: DMCUB timer/interrupt type, invalid-register-access type, DMU GPU timer read/start selection, interrupt line status, DMU clock gating and SMU interrupt controls, DCCG enable/clear/reference-source/clock-source selections, deep-color, refclock and DP refclock sources, pipe pixel-rate and PHY PLL sources, DTO/audio DTO selections, DISPCLK ramp and FIFO error detection, global memory power request disable, DCCG performance selects, soft resets, DVO skew/phase controls, vsync counter controls, and HPD interrupt acknowledge/polarity/RX acknowledge.
- DP/DIG/link and sideband enums: DisplayPort entries cover MSO link count, sync polarity, combine pixel count, link training completion, embedded-panel mode, pixel encoding, component depth, lane count, stream disable/defer/ack/mask, M/N generator settings, enhanced frame mode, DPHY lane pattern/test controls, 8b/10b reset/current disparity, PRBS/FEC/CRC, fast training, secondary packet/audio/MST scheduling, MSA override, DSC mode, and link training switch mode. DIG/HDMI/TMDS entries cover HDMI keepout, clock-channel rate, null/audio/ACR/GC/ISRC/MPEG/generic packet send/continuous controls, deep color, audio layout/CRC/ramp controls, TMDS color/pixel/control data selection, DIG FE/BE source and HPD selects, FIFO/test pattern controls, AFMT interrupt and audio source controls, Dolby Vision/metadata routing, and HDMI metadata packet timing.
- DP AUX, DOUT I2C, DIO_MISC, and DCIO enums: AUX entries define HPD selection, test mode, software go, link-service read trigger, arbitration priority/register ownership, ack fields, PHY TX/RX timing windows, thresholds, GTC sync controls, error acks, reset/done, and PHY wake priority. DOUT I2C entries define software transaction start/reset, DDC select, transaction count, arbitration, ack, DDC speed/drive/EDID detect controls, stop-on-NACK, data index writes, and read-request interrupt type. DIO/DCIO entries cover display I/O memory power, clock gating, soft resets, DAC/TMDS muxing, generic stereosync, HDMI RX status timer type, DX protection, generic clock output selection, UNIPHY clock/link/channel controls, LVTMA panel power sequencing, backlight PWM, group/frame update locking, GSL/genlock/swaplock masks, GPU timer start position, and DCIO clock test/gate selection.

## Control Flow And Runtime Behavior

There is no executable control flow in this header. Runtime use is indirect:

1. Navi10-era AMDGPU components include `navi10_enum.h` alongside register offset and mask headers.
2. Driver code chooses a symbolic enum value based on DRM plane, stream, link, tiling, cursor, timing, power, interrupt, or debug state.
3. Generated register helpers pack the enum's integer into the correct bitfield and write or read the actual hardware register.
4. Hardware blocks such as HUBP, MPC, MPCC, OPP, OTG, DCCG, HPD, DP, DIG, AUX, I2C, DCIO, GFX, GMC, GFXHUB, MMHUB, and ATHUB interpret the numeric value.

The header therefore forms a compile-time ABI between software policy code and Navi10 register specifications. It does not sequence hardware by itself; sequencing lives in display core, DCN register programming paths, amdgpu memory/hub setup, link training, modeset, page-flip, cursor, hotplug, AUX/DDC, and debug/performance-counter code.

## State And Persistence Behavior

The enums store no software state and persist nothing. The values describe stateful hardware fields whose contents can persist in registers until overwritten, reset, power-gated, or restored after suspend/resume.

State represented by this chunk includes cache policy and fault/request types, GDS performance event selection, surface format and tiling metadata, cursor and plane format/address mode, DCC/TMZ flags, flip/update lock and interrupt behavior, color conversion/LUT selection, scaler setup, CRC/perfmon state machines, display pipe timing and synchronization, MPCC blending and composition, dithering/truncation/FRC behavior, clock-source selection, hotplug and interrupt acknowledge bits, DP link and PHY training state, HDMI/audio packet generation, AUX/DDC/I2C ownership and transaction status, panel power/backlight controls, and genlock/swaplock grouping.

Several enum names encode write-one-to-clear or acknowledge semantics, for example `*_ACK`, `*_CLEAR`, and interrupt status controls. The header does not mark access type, side effects, reset values, or whether fields are read-only, write-only, latched, self-clearing, double-buffered, or timing-sensitive. Consumers must follow the relevant register programming model.

## Dependencies And Integration Points

Direct includes in this tree include Navi10/GFX10-era and later AMDGPU blocks such as `amdgpu/gfx_v10_0.c`, `amdgpu/gmc_v10_0.c`, `amdgpu/gfxhub_v2_0.c`, `amdgpu/mmhub_v2_0.c`, and newer hub/GFX variants that reuse the generated enum namespace. The header is also parallel to `soc21_enum.h` and `soc24_enum.h`, which carry many equivalent enum names for later ASIC generations.

Display integration is mostly through AMD DC/DCN register programming. Plane and cursor paths map DRM formats, tiling, cursor attributes, and update locks into DC-facing types, then lower layers program registers using generated enum values and masks. Link and connector paths use DP, DIG, HDMI, AUX, I2C/DDC, HPD, DCCG, and DCIO values during modeset, link training, MST/audio metadata programming, EDID/AUX transactions, hotplug handling, panel power sequencing, and backlight control.

The enum values must remain synchronized with Navi10 register field definitions and companion generated headers that provide register addresses, field masks, and field shifts. Renaming a value usually causes a build failure; changing the underlying integer can compile cleanly but program the wrong hardware mode.

## Risks And Edge Cases

- Numeric drift is the primary risk. A wrong enum value for `SURFACE_PIXEL_FORMAT`, swizzle/tile geometry, `DP_PIXEL_ENCODING`, `DP_COMPONENT_DEPTH`, `CURSOR_MODE`, `MPCC_CONTROL_MPCC_MODE`, `OTG_*`, `DCCG_*`, `DP_AUX_*`, or `DOUT_I2C_*` can compile but produce corruption, blank displays, failed link training, bad colors, broken EDID reads, incorrect cursor rendering, or hard-to-reproduce interrupt behavior.
- This chunk crosses many hardware domains. Some enum names are generic (`ENABLE`, `INT_MASK`, `CLOCK_GATING_EN`, `SOFT_RESET`) and can collide conceptually with other headers even when C enum constants live in the same global namespace. Consumers need the correct ASIC header and matching register field.
- Reserved values are explicitly present in many enums. Accidentally using reserved values in normal paths can rely on undefined hardware behavior.
- Some names reflect generated-source typos or legacy spellings, such as `ONE_SHADER_ENGIN`, `SURFACE_INUSE_RAED_NO_LATCH`, `HDMI_DEFAULT_PAHSE`, and `DPHY_8B10B_RESETET`. Cleanup-style renames would break consumers unless all users and generated headers are updated together.
- Interrupt ack/clear enums may have inverted-looking semantics relative to ordinary booleans. Treating `*_ACK`, `*_CLEAR`, and mask fields as plain enable bits can miss or spuriously clear interrupts.
- Display timing, update-lock, double-buffer, DRR, external sync, genlock, and swaplock values are sequencing-sensitive. Correct constants still need to be written at the right vblank/update point.
- The chunk boundary leaves only the comment for `DCIO_DIO_OTG_EXT_VSYNC_MUX`; the enum body starts in the next chunk. Final reconciliation should not claim this chunk contains that definition.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU with Navi10/GFX10/DCN display support enabled so all enum names referenced by GFX, GMC, GFXHUB, MMHUB, ATHUB, and display code compile.
- Mechanically compare enum names and integer values against the authoritative Navi10 register database and generated address/mask headers.
- Diff common enum families against `soc21_enum.h`, `soc24_enum.h`, and older DCE enum headers where hardware compatibility is expected, while allowing known ASIC-generation differences.
- Exercise modesets across RGB/YCbCr formats, 6/8/10/12 bpc, HDMI and DP, MST/SST, DSC/FEC-capable links, hotplug, EDID over DDC and AUX, backlight/panel power sequencing, page flips, cursor formats, rotation/mirroring, DCC/TMZ surfaces, variable refresh/DRR, suspend/resume, and display CRC/debug paths.
- Watch for kernel warnings, DC link-training failures, AUX/I2C timeouts, HPD storms, underflow or FIFO errors, incorrect CRCs, color/format mismatches, blank displays, broken audio infoframes, cursor artifacts, and regressions that appear only with multi-plane blending or multi-display timing synchronization.

## Cross-Chunk Notes

This is the opening chunk of `navi10_enum.h`, so it includes the license and file guard but not the final guard close. Later chunks continue the DCIO enum namespace beginning with `DCIO_DIO_OTG_EXT_VSYNC_MUX` and then cover the remaining ASIC enum families. The final per-file report should merge all chunks before making whole-file claims about the generated Navi10 enum set.

### subset-b-003491: lines 8446-14863

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

### subset-b-003492: lines 14864-20395

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h lines 14864-20395

## Scope And Purpose

This chunk covers the third generated-header slice of `navi10_enum.h` for AMD Navi10/GFX10-era register programming. The range starts in the tail of `GL1C_PERF_SEL`, includes the complete `GL1CG_PERF_SEL` enum, then spans generated enum groups for texture/cache/performance counters, command processor state, shader export and depth-buffer controls, texture/vertex resource fields, primitive/rasterization counters and raster configuration, RMI/GCR/UTCL1/SDMA performance selectors, and the first ADDRLIB surface tiling/address-configuration enums. It ends immediately after `NumLowerPipes`; `ColorTransform` begins in the next chunk.

The file section is not executable code. Its purpose is to provide symbolic, generation-specific integer values that driver code can place into register fields defined by companion offset and shift/mask headers. Most definitions are performance event selectors for hardware perfmon muxes; the smaller enums define legal field encodings for command processor IDs, perfmon state machines, texture and vertex descriptors, depth/stencil/raster controls, binning controls, SDMA selectors, and address-library tiling geometry.

## Important APIs, Types, And Constants

The exported API is the enum namespace. There are no functions, structs, globals, locks, allocation paths, or inline helpers. Consumers include this header and write enum constants into MMIO fields through AMDGPU helpers such as `REG_SET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, `SOC15_REG_OFFSET`, or generated register programming tables. The relevant source-tree include points found for this header are `amdgpu/gfx_v10_0.c`, `amdgpu/gfx_v11_0.c`, `amdgpu/gfxhub_v2_0.c`, `amdgpu/gmc_v11_0.c`, and `amdkfd/kfd_device_queue_manager_v10.c`.

Major enum families in this span are:

- Texture/cache and memory path selectors: `GL1CG_PERF_SEL`, `TA_TC_REQ_MODES`, `TA_TC_ADDR_MODES`, `TA_PERFCOUNT_SEL`, `TD_PERFCOUNT_SEL`, `TCP_PERFCOUNT_SELECT`, `TCP_CACHE_POLICIES`, `TCP_CACHE_STORE_POLICIES`, `TCP_WATCH_MODES`, `TCP_DSM_*`, `TCP_OPCODE_TYPE`, `GL2C_PERF_SEL`, and `GL2A_PERF_SEL`.
- Graphics register-bus and command processor selectors: `GRBM_PERF_SEL`, `GRBM_SE0_PERF_SEL` through `GRBM_SE3_PERF_SEL`, `CP_RING_ID`, `CP_PIPE_ID`, `CP_ME_ID`, `SPM_PERFMON_STATE`, `CP_PERFMON_STATE`, `CP_PERFMON_ENABLE_MODE`, `CPG_PERFCOUNT_SEL`, `CPF_PERFCOUNT_SEL`, `CPC_PERFCOUNT_SEL`, CP perf-window and latency-stat enums, and `CP_DDID_CNTL_*`.
- Shader export and depth-buffer controls: `SX_BLEND_OPT`, `SX_OPT_COMB_FCN`, `SX_DOWNCONVERT_FORMAT`, `SX_PERFCOUNTER_VALS`, `ForceControl`, `ZSamplePosition`, `ZOrder`, `ZpassControl`, `ZModeForce`, `ZLimitSumm`, `CompareFrag`, `StencilOp`, `ConservativeZExport`, `DbPSLControl`, `DbPRTFaultBehavior`, `PerfCounter_Vals`, `RingCounterControl`, `DbMemArbWatermarks`, `DFSMFlushEvents`, `PixelPipeCounterId`, `PixelPipeStride`, and `FullTileWaveBreak`.
- Texture, sampler, and vertex descriptor encodings: `TEX_BORDER_COLOR_TYPE`, `TEX_BC_SWIZZLE`, `TEX_CHROMA_KEY`, `TEX_CLAMP`, `TEX_COORD_TYPE`, `TEX_DEPTH_COMPARE_FUNCTION`, `TEX_DIM`, `TEX_FORMAT_COMP`, `TEX_MAX_ANISO_RATIO`, `TEX_MIP_FILTER`, `TEX_REQUEST_SIZE`, `TEX_SAMPLER_TYPE`, `TEX_XY_FILTER`, `TEX_Z_FILTER`, `VTX_CLAMP`, `VTX_FETCH_TYPE`, `VTX_FORMAT_COMP_ALL`, `VTX_MEM_REQUEST_SIZE`, `TVX_DATA_FORMAT`, `TVX_DST_SEL`, `TVX_ENDIAN_SWAP`, `TVX_INST`, `TVX_NUM_FORMAT_ALL`, `TVX_SRC_SEL`, `TVX_SRF_MODE_ALL`, and `TVX_TYPE`.
- Primitive/rasterization and backend counters/configuration: `PH_PERFCNT_SEL`, `SU_PERFCNT_SEL`, `SC_PERFCNT_SEL`, `SePairXsel`, `SePairYsel`, `SePairMap`, `SeXsel`, `SeYsel`, `SeMap`, `ScXsel`, `ScYsel`, `ScMap`, `PkrXsel2`, `PkrXsel`, `PkrYsel`, `PkrMap`, `RbXsel`, `RbYsel`, `RbXsel2`, `RbMap`, `BinningMode`, `BinSizeExtend`, `BinMapMode`, `BinEventCntl`, `CovToShaderSel`, and `ScUncertaintyRegionMode`.
- Memory-system, DMA, and address-library enums: `RMIPerfSel`, `GCRPerfSel`, `UTCL1PerfSel`, `SDMA_PERF_SEL`, `NUM_PIPES_BC_ENUM`, `NUM_BANKS_BC_ENUM`, `SWIZZLE_TYPE_ENUM`, `TC_MICRO_TILE_MODE`, `SWIZZLE_MODE_ENUM`, `SurfaceEndian`, `ArrayMode`, `NumPipes`, `NumBanksConfig`, `PipeInterleaveSize`, `BankInterleaveSize`, `NumShaderEngines`, `NumRbPerShaderEngine`, `NumGPUs`, `NumMaxCompressedFragments`, `ShaderEngineTileSize`, `MultiGPUTileSize`, `RowSize`, and `NumLowerPipes`.

The largest selector tables in this chunk are `PH_PERFCNT_SEL` with 960 values, `SC_PERFCNT_SEL` with 501 values, `SU_PERFCNT_SEL` with 427 values, `PerfCounter_Vals` with 346 values, `RMIPerfSel` with 257 values, `GL2C_PERF_SEL` with 228 values, and `SX_PERFCOUNTER_VALS` with 221 values. These wide enums are hardware perf event IDs rather than dense software state machines.

## Control Flow

This header has no runtime control flow. It affects compiled control flow indirectly by naming constants used when a driver chooses a register field value or selects a hardware performance event.

Typical usage flow is:

1. The driver selects an IP block and register field using the generation's offset and shift/mask headers.
2. It chooses one of these enum constants as the semantic value for that field, for example a CP perfmon state, a texture descriptor clamp mode, a DB compare or stencil operation, a raster config selector, or a perf counter event.
3. It packs the value into the register field and writes it through SOC15/MMIO helpers.
4. For diagnostic/performance paths, it later reads hardware counters or status registers and interprets the result according to the same generation-specific selector value.

The perf-selector enums are especially mux-oriented. Values such as `TA_PERF_SEL_*`, `TCP_PERF_SEL_*`, `GL2C_PERF_SEL_*`, `CPG_PERF_SEL_*`, `SX_PERF_SEL_*`, `DB_PERF_SEL_*`, `PH_*`, `PERF_*`, `SC_*`, `RMI_PERF_SEL_*`, `GCR_PERF_SEL_*`, `UTCL1_PERF_SEL_*`, and `SDMA_PERF_SEL_*` are intended to be written into perfmon select registers before counter collection. The smaller descriptor/config enums drive normal rendering and memory behavior rather than counter selection.

## State And Persistence Behavior

The enums themselves do not store state. They describe hardware-visible values that become persistent only after a consumer writes them into GPU registers or descriptors.

Longer-lived programmed state includes command processor ring/pipe/ME IDs, CP/SPM perfmon state and enable modes, texture/sampler resource encodings, vertex fetch descriptors, depth/stencil compare and update modes, DB pixel pipe counter controls, rasterization layout maps, binning controls, SDMA perf selector values, and ADDRLIB address-configuration fields. These persist in hardware or command streams until overwritten, context-switched, reset, or restored after suspend/resume.

Transient state is represented by the counters selected by the perf enums. The selector value is stable, but the counter result is live hardware state. Many selector names expose busy/idle cycles, stalls, FIFO full/empty conditions, cache hits/misses, TLB requests and misses, XNACK activity, latency bins, credit stalls, dealloc events, primitive/binning events, and clock-gating status. The header does not encode how counters latch, reset, overflow, multiplex, or synchronize with command submissions; those semantics live in the perfmon hardware and driver sequencing.

Some enum values are command-like or side-effect sensitive when written into their matching fields. CP perfmon states such as disable/reset/start/count/dump alter collection state; bin event controls can break, pipeline, or drop batches; DB force and flush-related values affect depth/stencil behavior; SDMA and GCR perf selectors expose invalidation, UTCL2, and TLB shootdown activity; texture and vertex descriptor encodings affect memory fetch interpretation.

## Dependencies And Integration Points

This chunk depends on the generated AMDGPU register-header convention. The enum values are meaningful only with matching Navi10/GFX10-era register offsets, masks, defaults, packet definitions, and hardware documentation. They complement headers such as GC/GFXHUB offset and sh/mask files, which provide register addresses and bitfield positions. On their own, these enums do not identify which register field consumes each value.

Integration points include:

- AMDGPU graphics initialization and context programming, where CP IDs, perfmon state, GRBM selectors, raster configuration maps, DB/SX state, and texture/vertex descriptor values are emitted into registers or command streams.
- KFD queue management for GFX10, which includes this header alongside queue and CP definitions.
- GMC/GFXHUB paths, which include the header for memory-type, cache, translation, invalidation, and hub-related enum values elsewhere in the file and may rely on matching generation constants.
- Performance monitoring and SPM collection, where the large TA/TD/TCP/GL2/GRBM/CP/SX/DB/PH/SU/SC/RMI/GCR/UTCL1/SDMA selector sets map software-visible perf event choices to hardware mux IDs.
- Texture and vertex fetch programming, where `TEX_*`, `VTX_*`, and `TVX_*` values define descriptor fields for sampler behavior, formats, request size, endian swap, destination/source swizzles, and instruction/resource type.
- Address library and surface layout code, where swizzle, array mode, pipe/bank/interleave, shader-engine, RB, GPU, compressed-fragment, tile-size, row-size, and lower-pipe enums express hardware memory-layout geometry.

There are overlapping enum names in older and newer generated headers under `include/asic_reg/` and top-level generation headers. Similar names do not guarantee identical numeric values. For example, `SDMA_PERF_SEL` and `ArrayMode` appear in other ASIC enum headers with generation-specific contents and gaps, so cross-generation code must include the correct header for the active IP version.

## Risks And Edge Cases

The primary risk is hardware ABI drift. These constants are numeric encodings for silicon register fields. A wrong value can still compile but select the wrong perf event, program an illegal descriptor mode, corrupt raster/backend routing, break binning, or misreport memory/cache/translation behavior.

The chunk boundary is important. The requested range begins after the `GL1C_PERF_SEL` typedef line and includes only its last five selector entries plus closing brace; a complete file-level description of `GL1C_PERF_SEL` needs the previous chunk. The range ends after `NumLowerPipes`; `ColorTransform`, `CompareRef`, and later ADDRLIB/display/format enums are in the next chunk.

Large perf selector tables are easy to treat as generic event lists, but they are block-specific. A `PH_PERFCNT_SEL` value cannot be substituted for an `SC_PERFCNT_SEL` value even when names mention similar events. Many tables include reserved holes or non-contiguous jumps, and those holes should remain exactly as generated.

Descriptor/config enums have visible rendering consequences. Incorrect `TEX_CLAMP`, depth compare, stencil op, `SX_DOWNCONVERT_FORMAT`, `TVX_DATA_FORMAT`, `SWIZZLE_MODE_ENUM`, or `ArrayMode` use can produce incorrect pixels, GPUVM faults, bad compression layout, or invalid memory interpretation.

Raster configuration and binning enums are topology-sensitive. `Se*`, `Sc*`, `Pkr*`, and `Rb*` mapping values describe how shader engines, scan converters, packers, and render backends are tiled or routed. Incorrect use can affect load balancing, primitive distribution, or backend addressing.

Performance and diagnostic fields can be privileged or timing-sensitive. Counter selection may need clocks enabled, stable perfmon state transitions, counter resets, and serialization around workloads. The header does not encode those ordering requirements.

## Test Signals

Useful validation signals are build and hardware-integration oriented:

- Build coverage for AMDGPU/KFD files that include `navi10_enum.h`, especially `gfx_v10_0.c`, `gfx_v11_0.c`, `gfxhub_v2_0.c`, `gmc_v11_0.c`, and `kfd_device_queue_manager_v10.c`.
- Perfmon/SPM tests that select representative TA, TD, TCP, GL2C/GL2A, GRBM, CP, SX, DB, PH, SU, SC, RMI, GCR, UTCL1, and SDMA events and verify nonzero or expected counter behavior under targeted workloads.
- Graphics conformance workloads that exercise texture clamp/filter/request-size behavior, vertex formats and fetch types, depth compare/stencil operations, SX downconversion/blend optimization, rasterization maps, and binning modes.
- GPU reset, suspend/resume, and power-gating tests that ensure perfmon state, texture/cache/raster/DB configuration, and address-configuration values are restored or regenerated correctly.
- Memory-layout and address-library tests that validate swizzle modes, array modes, pipe/bank/interleave geometry, row sizes, compressed-fragment modes, and shader-engine/RB topology on Navi10-class devices.
- Negative diagnostics for invalid or reserved selector values, ensuring driver interfaces either reject unsupported events or confine them to debug-only paths without affecting normal command submission.

### subset-b-003493: lines 20396-22764

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/navi10_enum.h lines 20396-22764

## Scope And Purpose

This chunk is the closing 2,369-line section of AMD's generated Navi10 enum header. It contains C enum typedefs and two scalar `#define` constants used as compile-time numeric names for Navi10 hardware register fields, packet fields, surface descriptors, interrupt-handler controls, semaphore performance counters, UVD/EFC formats, and a USB-PD revision constant. It defines no functions, structs with storage, global variables, branches, allocation paths, locks, MMIO accessors, or persistence logic.

The path is under a `ceph-client` source mirror, but the content is AMDGPU hardware metadata, not Ceph filesystem logic. Runtime behavior comes from DRM/AMDGPU code that includes this header or matching generated enum headers and writes the numeric values into packet/register fields described by other generated register-definition headers.

## Important APIs, Types, And Constants

The exported API is the enum namespace itself. Most enum values are direct hardware encodings and must remain synchronized with the ASIC register database:

- Render/depth/color encodings: `ColorTransform`, `CompareRef`, `ReadSize`, `DepthFormat`, `ZFormat`, `StencilFormat`, `CmaskMode`, `QuadExportFormat`, `QuadExportFormatOld`, `ColorFormat`, `SurfaceFormat`, `SurfaceNumber`, `SurfaceSwap`, and `RoundMode`. These cover DCC color transforms, depth/stencil compare modes and formats, color buffer formats, CMASK clear/fragment states, pixel export formats, numeric interpretation, channel swapping, and rounding.
- Surface/tile layout encodings: `IMG_NUM_FORMAT_FMASK`, `IMG_NUM_FORMAT_N_IN_16`, `TileType`, `NonDispTilingOrder`, `MicroTileMode`, `TileSplit`, `SampleSplit`, `PipeConfig`, `SeEnable`, `NumBanks`, `BankWidth`, `BankHeight`, `BankWidthHeight`, `MacroTileAspect`, `PipeTiling`, `BankTiling`, `GroupInterleave`, `RowTiling`, `BankSwapBytes`, and `SampleSplitBytes`. These describe color/depth tiling, micro/macro tile shape, tile split size, sample split, pipe/bank topology, shader-engine enablement, row size, and bank-swap/sample-split byte encodings.
- Buffer and image format tables: `BUF_FMT` has 128 entries, `IMG_FMT` has 430 declared entries in this chunk, `BUF_DATA_FORMAT` has 16, `IMG_DATA_FORMAT` has 117, `BUF_NUM_FORMAT` has 8, and `IMG_NUM_FORMAT` has 16. The tables cover UNORM/SNORM/scaled/integer/float variants, SRGB, packed 10/11/11 and 10/10/10/2 layouts, 32-bit through 128-bit vector formats, depth/stencil-packed forms, GB/GR and BG/RG formats, FMASK encodings, BC1-BC7 compressed formats, multimedia `MM_*` layouts, and reserved holes up to the encoded field width.
- Interrupt-handler enums: `IH_PERF_SEL` is the largest enum in this chunk with 718 performance selector values. It starts with cycle/idle and client/storm/cookie/buffer events, then includes memory-client events, 64 BIF selections, per-client selections for client 0-31, and ring-buffer event selectors for RB0/RB1/RB2 including write pointers, full flags, overflow flags, read pointers, and load-read-pointer selectors across PF/VF variants. `IH_CLIENT_TYPE`, `IH_RING_ID`, `IH_VF_RB_SELECT`, and `IH_INTERFACE_TYPE` define interrupt client grouping, interrupt/request/translation rings, virtual-function ring-buffer selection policy, and legacy versus register-write interrupt interface mode.
- Semaphore/performance-monitor enums: `SEM_PERF_SEL` has 175 selectors for SEM cycle/idle, request-signal and request-wait events from SDMA, UVD, VCE, ACP, ISP, VP8, CPG, CPC immediate engines, CPC offline engines 0-31 for CPC1/CPC2, poll-wait variants, MC read/write request/return events, ATC request/return/XNACK/invalidation events, and ATC VM invalidation.
- Firmware/video/display constants: `ROM_SIGNATURE` is `0x0000aa55`. `EFC_SURFACE_PIXEL_FORMAT` lists endian/channel-ordered RGB, RGBA, ARGB, YCrCb/CrYCb, planar 4:2:0, packed 4:2:2, fixed/float RGB111110/BGR101111, and monochrome pixel formats for the UVD EFC path. `UVDFirmwareCommand` defines UVD firmware command IDs for fence/trap, decoded and macroblock addresses, IT/display buffers, end-of-decode, display pitch/tiling, bitstream address, and bitstream size. `IP_USB_PD_REVISION_ID` is `0x00000000`.

## Control Flow And Runtime Behavior

There is no local control flow. The header is consumed as a generated numeric contract:

1. Navi10 register, packet, and descriptor programming code includes this header or a related ASIC enum header.
2. Driver logic maps DRM/KMS, GEM/TTM, command submission, display, UVD, interrupt, or power-management decisions onto these enum values.
3. Those values are packed into register fields, command processor packets, image/buffer descriptors, interrupt-handler controls, or performance-counter select fields using companion address and shift/mask headers.
4. The hardware interprets the packed numeric value, not the C enum name.

Because the enum values are simple constants, C type checking gives limited protection. In many call sites the effective API is an integer field in a descriptor or register, so wrong enum values can compile successfully and fail only as incorrect hardware behavior.

## State And Persistence Behavior

The file stores no software state and persists nothing. The enum values describe stateful hardware-visible encodings. Once a consumer writes one of these values into a register or descriptor, the resulting state may live in GPU registers, ring packets, memory-backed image/buffer descriptors, interrupt rings, firmware command buffers, or performance-monitor configuration until it is overwritten, reset, invalidated, or lost across power management transitions.

The state represented by this chunk includes render target/depth/stencil formats, compression metadata interpretation, tiling geometry, swizzle/channel order, numeric conversion behavior, buffer and image descriptor format fields, IH ring and virtualization selection, IH/SEM performance-counter selections, UVD/EFC surface formats, UVD firmware command slots, and ROM/USB-PD signature/revision constants.

## Dependencies And Integration Points

This chunk depends on the rest of `navi10_enum.h` for the complete generated namespace and on companion Navi10 headers that define register addresses and bitfields. Typical integration points are AMDGPU display, GFX, GMC, interrupt-handler, UVD/video, and power/performance-monitor code paths that need stable hardware encodings.

Nearby generated headers in this tree expose overlapping enum contracts for other ASIC generations, including `soc21_enum.h`, `soc24_enum.h`, `asic_reg/smu/smu_7_1_*_enum.h`, and `asic_reg/gca/gfx_*_enum.h`. Those files are useful parity references but are not substitutes for Navi10-specific values because reserved holes and later-generation additions can differ.

The format enums integrate with buffer/image descriptor setup and surface programming. The tiling enums integrate with address-library or mode-setting decisions that choose displayable versus non-displayable layouts, bank/pipe geometry, FMASK, CMASK, and depth layouts. The IH enums integrate with interrupt ring setup, SR-IOV/PF/VF ring selection, interrupt-client classification, and IH performance counters. The SEM enum integrates with semaphore/performance monitor programming across SDMA, media, command processor, memory controller, and ATC paths. The UVD/EFC enums integrate with firmware command buffers and video/display format handling.

## Risks And Edge Cases

- Generated-header drift is the main risk. A numeric change in these enums can compile cleanly while programming the wrong hardware value.
- The chunk starts at a comment boundary for `ColorTransform` and ends at the file guard close, so it is self-contained for the listed enums but not for the full `navi10_enum.h` namespace.
- `BUF_FMT`, `IMG_FMT`, `BUF_DATA_FORMAT`, and `IMG_DATA_FORMAT` contain many reserved holes. Treating reserved values as usable can produce descriptor faults, corrupted rendering, unsupported texture sampling, or undefined hardware behavior.
- Format families with similar names are not interchangeable. For example `SurfaceFormat`, `BUF_FMT`, `IMG_FMT`, data-format enums, and numeric-format enums encode related concepts at different abstraction levels and field widths.
- Tiling values affect memory addressing. Incorrect pipe, bank, row, split, or macro-tile settings can cause visible corruption, page faults, or failures that depend on resolution, sample count, compression, or displayability.
- Depth/stencil, CMASK, FMASK, and color-export encodings interact with compression and render backend behavior. Off-by-one values may appear only under MSAA, DCC, depth testing, fast clears, or specific export formats.
- IH selectors are highly repetitive across RB0/RB1/RB2, PF/VF, and client indices. Copy/paste or generated-order mistakes can misattribute interrupt performance events or break virtualization-specific interrupt routing diagnostics.
- SEM selectors are similarly repetitive across CPC immediate/offline engines and poll-wait variants. Incorrect selector values can make performance counters misleading without affecting normal functional execution.
- UVD firmware command enum values are protocol identifiers. Reordering or using the wrong command ID can make firmware parse a command buffer incorrectly even though the host-side structure compiles.
- `ROM_SIGNATURE` and `IP_USB_PD_REVISION_ID` are fixed constants; using them as mutable state or assuming they validate all ROM/USB-PD behavior would be misleading.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU/Navi10 code that includes `navi10_enum.h` so enum typedefs, duplicate names, and file-guard closure are compile-checked.
- Mechanically compare this line range with the authoritative generated Navi10 register database and with adjacent generated ASIC enum headers where parity is expected.
- Verify enum counts and boundary values for the large tables: `BUF_FMT` 128 entries, `IMG_FMT` 430 declared entries ending at `IMG_FMT_RESERVED_511`, `IMG_DATA_FORMAT` ending at `IMG_DATA_FORMAT_RESERVED_127`, `IH_PERF_SEL` ending at `IH_PERF_SEL_RB2_LOAD_RPTR_VF30`, and `SEM_PERF_SEL` ending at `SEM_PERF_SEL_ATC_VM_INVALIDATION`.
- Exercise runtime paths that create color/depth/stencil targets, compressed textures, BC formats, SRGB formats, FMASK/CMASK/MSAA resources, displayable and non-displayable tiling, and multimedia image formats.
- Validate interrupt handling and diagnostics under PF/VF or SR-IOV configurations, especially IH RB0/RB1/RB2 selector programming and ring selection policy.
- Validate SEM/IH performance counter programming by checking that selected events increment under the corresponding SDMA, UVD/VCE, command processor, memory controller, ATC, interrupt-ring, and virtualization workloads.
- Exercise UVD firmware command submission and EFC surface formats with planar 4:2:0, packed 4:2:2, RGB/RGBA, high-bit-depth, float/fixed, and monochrome surfaces.
- Watch for GPU page faults, descriptor validation errors, corrupted render targets, incorrect texture sampling, failed fast clears, interrupt storms or missed interrupts, bogus performance counter readings, and UVD firmware command failures.

## Cross-Chunk Notes

The merge lane should combine this with earlier `navi10_enum.h` chunks before making complete statements about the file. This chunk closes the header with `#endif /*_navi10_ENUM_HEADER*/`, so there is no following enum content in this source file after line 22764.
