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
