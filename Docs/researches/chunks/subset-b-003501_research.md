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
