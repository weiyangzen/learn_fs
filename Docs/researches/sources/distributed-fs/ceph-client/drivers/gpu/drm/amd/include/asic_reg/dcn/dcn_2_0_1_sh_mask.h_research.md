# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001641`: lines 1-2551, `Docs/researches/chunks/subset-b-001641_research.md`
- `subset-b-001642`: lines 2552-5077, `Docs/researches/chunks/subset-b-001642_research.md`
- `subset-b-001643`: lines 5078-7595, `Docs/researches/chunks/subset-b-001643_research.md`
- `subset-b-001644`: lines 7596-10129, `Docs/researches/chunks/subset-b-001644_research.md`
- `subset-b-001645`: lines 10130-12631, `Docs/researches/chunks/subset-b-001645_research.md`
- `subset-b-001646`: lines 12632-15144, `Docs/researches/chunks/subset-b-001646_research.md`
- `subset-b-001647`: lines 15145-17562, `Docs/researches/chunks/subset-b-001647_research.md`
- `subset-b-001648`: lines 17563-19999, `Docs/researches/chunks/subset-b-001648_research.md`
- `subset-b-001649`: lines 20000-22091, `Docs/researches/chunks/subset-b-001649_research.md`

## Chunk Research

### subset-b-001641: lines 1-2551

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 1-2551

## Purpose

This chunk is the opening portion of AMDGPU's generated DCN 2.0.1 shift/mask header. It contains no executable C logic; it publishes compile-time constants that describe bit positions and already-positioned masks for display-controller hardware registers. Driver code pairs these macros with the matching register addresses from `dcn_2_0_1_offset.h` and the AMD display register helper macros.

The chunk covers the file prologue, include guard, and the first 2,091 `#define` entries across 21 address blocks. The visible hardware areas are:

- DCCG display clock generation, reference-clock, DTO, clock-gating, perf-monitor, millisecond/microsecond timer, pixel-rate, audio DTO, and vsync-count controls.
- DFS `DENTIST_DISPCLK_CNTL` and display/Azalia clock interrupt bits.
- HDA/Azalia endpoint, controller, root-codec, and input-endpoint register fields for HDMI/DP audio.
- DCHUBBUB SDPIF, return-path DCC constants, arbitration/watermark, DRAM self-refresh and p-state allowance, timeout, soft-reset, surface-check, VTG, and debug fields.
- HUBP/HUBPREQ/HUBPRET/CURSOR register families for pipe instances 0 and 1.
- The beginning of HUBP2, ending mid-register in `HUBP2_DCHUBP_REQ_SIZE_CONFIG_C`.

Each register field is represented by paired macros: `REGISTER__FIELD__SHIFT` gives the low bit index, while `REGISTER__FIELD_MASK` gives the shifted bit mask. The header is a generated hardware-layout contract, not a policy layer.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this range. The public interface is the macro namespace.

The `DCCG*`, `PHYPLL*`, `DP_DTO*`, `OTG*`, `DPPCLK*`, and `SYMCLK*` groups describe display clock programming:

- `PHYPLLA_PIXCLK_RESYNC_CNTL` and `PHYPLLB_PIXCLK_RESYNC_CNTL` expose pixel-clock resync, deep-color, clock-enable, and double-rate bits.
- `DCCG_DS_*` and `DCCG_GTC_*` expose display-synchronization/GTC DTO increment, modulo, current count, enable, reference-source, hardware-calibration, jitter, and delay-selection fields.
- `DISPCLK_FREQ_CHANGE_CNTL`, `DENTIST_DISPCLK_CNTL`, and the CGTT block controls expose clock ramp, step, ramp-done, FIFO-error detection, DENTIST divider/change controls, and turn-on/turn-off delays.
- `DCCG_GATE_DISABLE_CNTL` and `DCCG_GATE_DISABLE_CNTL2` expose clock-gate disable bits for display, SOC, DP reference, DPP, DSC, DMCUB, AOM, audio DTO, refclk, DSI, byte, ESC, and SYMCLK paths.
- `OTG0_PIXEL_RATE_CNTL` and `OTG1_PIXEL_RATE_CNTL` expose pixel-rate source, DP DTO enable, add/drop-pixel controls, half-rate output, and DIO FIFO error bits.
- `DPPCLK*_DTO_PARAM`, `DPPCLK_DTO_CTRL`, `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO*_PHASE/MODULE`, and `DCCG_VSYNC_*` provide DPP and audio DTO setup plus vsync latch/counter fields.

The HDA/Azalia groups describe the GPU display-audio register surface:

- Endpoint index/data pairs exist for two codec endpoints and three input endpoints.
- `AZALIA_CONTROLLER_CLOCK_GATING`, `AZALIA_AUDIO_DTO`, `AZALIA_AUDIO_DTO_CONTROL`, and `AZALIA_SOCCLK_CONTROL` expose clock gating, audio DTO phase/module, DTO force, and deep-sleep-exit control.
- `AZALIA_DATA_DMA_CONTROL`, `AZALIA_BDL_DMA_CONTROL`, `AZALIA_RIRB_AND_DP_CONTROL`, and `AZALIA_CORB_DMA_CONTROL` expose non-snoop, isochronous, interrupt-generation, underflow, and DP update frequency fields.
- Root codec fields expose vendor/device ID, revision ID, channel-count, supported rates and bit depths, supported stream formats, power-state, codec reset, subsystem ID, converter synchronization, and audio port-connectivity overrides.

The DCHUBBUB groups describe central display memory arbitration and hub behavior:

- `DCHUBBUB_SDPIF_CFG0`, `DCHUBBUB_SDPIF_PIPE_SEC_LVL`, and `DCHUBBUB_SDPIF_PIPE_DMDATA_SEC_LVL` expose SDPIF request/response status, credit controls, security levels, and metadata security levels.
- `DCHUBBUB_RET_PATH_DCC_CFG*` registers expose full-width DCC return-path constants for up to eight surfaces, and return-path memory power control/status fields.
- `DCHUBBUB_ARB_*` registers expose outstanding request limits, saturation level, QoS force, DRAM self-refresh and p-state force controls, four watermark sets for data/PTE/meta urgency and DRAM clock changes, watermark-change request/done/ack bits, and timeout enable.
- `DCHUBBUB_GLOBAL_TIMER_CNTL`, `SURFACE_CHECK*_ADDRESS_*`, `VTG*_CONTROL`, `DCHUBBUB_SOFT_RESET`, `DCHUBBUB_CLOCK_CNTL`, `DCFCLK_CNTL`, `DCHUBBUB_TIMEOUT_*`, and debug index/data fields expose global timing, surface in-use checks, VTG init/enable, reset, clock gating, timeout diagnostics, and debug read/write access.

The HUBP/HUBPREQ/HUBPRET/CURSOR families are repeated per pipe. This chunk fully covers instances 0 and 1 and starts instance 2:

- `HUBP0_*`, `HUBP1_*`, and the visible `HUBP2_*` macros describe surface format, rotation, mirroring, address/tiling layout, primary/secondary viewport starts and dimensions, request sizing, pipe disable/blanking/status, VTG selection, TTU mode, timeout/underflow status, and HUBP clock control.
- `HUBPREQ0_*` and `HUBPREQ1_*` describe surface pitch, luma/chroma primary/secondary/meta addresses, surface control, flip control, flip interrupts, in-use and earliest-in-use addresses, expansion mode, TTU QoS, nominal/vblank/flip timing parameters, per-line delivery, cursor fetch settings, reference-frequency-to-pixel-frequency ratio, DRQ delta limits, and memory power states for DPTE, MPTE, metadata, and PDE memories.
- `HUBPRET0_*` and `HUBPRET1_*` describe DET buffer base, pack/crossbar routing, DET/DMROB/PIXCDC memory power, read-line intervals/windows, vblank/read-line interrupt masks/types/clears/status bits, read-line value snapshots, and read-line inside/outside status.
- `CURSOR0_0_*` and `CURSOR0_1_*` describe cursor enable/mode/TMZ/snoop/system/pitch, position, size, hot spot, stereo offsets, destination offset, cursor memory power, DMDATA GPU address and attributes, DMDATA update/repeat/mode/size, QoS, done/underflow/clear status, and software DMDATA staging.

## Control Flow

This header has no runtime control flow. It is consumed by preprocessor expansion and compile-time symbol resolution.

A normal runtime path in the DCN201 display code is:

1. Select a DCN 2.0.1 register address from `dcn_2_0_1_offset.h`, often through register tables in the clock manager, resource builder, or IRQ service.
2. Select fields from this mask header through generated field macros, commonly via display helpers that use `reg__field` names.
3. Read, update, or write the target register through AMD display register access helpers.
4. Let the hardware interpret the programmed bits according to DCN sequencing, power, timing, link, memory, and interrupt rules.

Runtime behaviors represented by these constants include display-clock ramping, DTO programming, pixel-rate selection, clock gating, audio DMA and codec configuration, hubbub watermark programming, self-refresh/p-state allowance, timeout detection, HUBP surface fetch setup, page-flip control, cursor fetch and DMDATA metadata delivery, memory power transitions, and vblank/read-line interrupt handling. The macros themselves do not enforce ordering, valid values, status polling, write-one-to-clear behavior, or clock/power prerequisites.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in MMIO registers inside the display hardware.

State represented in this chunk includes:

- Clock and timing state: DCCG clock-source selects, DTO phase/module/increment/modulo values, DENTIST divider settings, ramp status, pixel-rate routing, millisecond/microsecond bases, vsync counters, and VTG enable/init fields.
- Audio state: Azalia endpoint windows, audio DTOs, DMA snoop/isochronous modes, codec capabilities, channel-count controls, power state, reset, converter synchronization, and port connectivity overrides.
- Hub and memory-arbitration state: SDPIF status/credits, hubbub DCC constants, outstanding-request limits, QoS force, watermarks, DRAM self-refresh/p-state gating, timeout thresholds/status, soft reset, and surface in-use check addresses.
- Pipe fetch state: surface format, tiling, swizzle/address config, luma/chroma viewport geometry, surface addresses, meta addresses, flip state, TTU parameters, prefetch/vblank/flip timing, per-line delivery, and memory power state for request/return buffers.
- Cursor and metadata state: cursor surface address/format/position/hot spot, secure/TMZ/snoop/system attributes, cursor memory power state, DMDATA address, DMDATA update/repeat/mode/size, QoS, and underflow status.

Persistence is hardware-defined. Some fields are latched programming values, some are live status bits, some are sticky interrupt or underflow bits that need explicit clear/ack writes, some may be self-clearing controls, and some are read-only capability/status fields. Register contents may be changed by display modesets, atomic page flips, interrupt handlers, hotplug handling, runtime power management, suspend/resume, firmware/BIOS setup, hardware clock/power gating, or ASIC reset. This header does not mark those distinctions; consumers must rely on DCN documentation and local sequencing code.

## Dependencies And Integration Points

This chunk belongs to the generated DCN 2.0.1 register-header set. The direct companion address header is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h`

Direct in-tree consumers found for `dcn_2_0_1_sh_mask.h` are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`

The clock manager uses the clock/DCCG field layout for DCN201 display clock programming. The resource code uses generated register and field metadata to populate DCN201 hardware blocks such as hubps, timing generators, links, pipes, and display services. The IRQ service uses the generated masks and shifts to decode and program interrupt status, masks, and acknowledgements. Consumers generally include both the offset and mask headers so they can combine a physical MMIO address with the correct bit layout.

Although the repository path sits under `sources/distributed-fs/ceph-client`, this source is AMDGPU display-driver hardware metadata. It has no Ceph filesystem protocol, distributed filesystem consistency, network, or storage semantics.

## Risks And Edge Cases

The core risk is silent hardware misprogramming. A wrong shift or mask normally still compiles, but it can update the wrong bits, fail to update the intended bits, or corrupt adjacent fields during read-modify-write sequences.

High-risk clock fields include clock-source selects, DTO increments/modulos, DENTIST divider controls, pixel-rate source/DTO enable bits, DISPCLK ramp controls, and clock-gate disable bits. Bad constants here can produce blank screens, unstable modesets, incorrect pixel clocks, audio clock drift, hangs waiting for status bits, or excess power.

Hubbub and HUBP fields are also sensitive. Watermark, DRAM self-refresh/p-state, outstanding-request, surface-address, tiling, viewport, prefetch, TTU, per-line delivery, and memory-power fields directly affect display memory fetch. Incorrect values can cause underflow, flicker, corruption, missed flips, visible cursor artifacts, memory faulting, timeout interrupts, bad power-management decisions, or resume failures.

Interrupt and status fields need special care. `*_CLEAR`, `*_ACK`, `*_STATUS`, interrupt-mask, underflow-clear, and timeout-clear bits can have write-one-to-clear or hardware-latched behavior that is not expressed by the macro names alone. Treating a status bit like a normal writable value can drop interrupts or leave sticky errors uncleared.

Repeated instance layouts create generation and maintenance risk. Pipe 0 and pipe 1 are fully represented here with nearly identical `HUBP`, `HUBPREQ`, `HUBPRET`, and `CURSOR` families; pipe 2 starts at the end of the chunk. Any instance suffix mismatch can compile and only fail on a specific pipe, plane, cursor, or display topology.

Address-window style registers, such as Azalia endpoint index/data pairs and debug index/data pairs, require correct ordering in consumers. The macros describe the index and data fields but do not enforce the sequence of index selection before data access.

This research item ends at line 2551, before the complete `HUBP2_DCHUBP_REQ_SIZE_CONFIG_C` mask set and before the rest of the 22,091-line file. The missing masks after `HUBP2_DCHUBP_REQ_SIZE_CONFIG_C__MIN_CHUNK_SIZE_C_MASK` are a chunk boundary, not evidence that the source file is incomplete.

## Test Signals

Useful validation is mostly compile-time plus hardware behavior:

- AMDGPU/DCN201 builds should compile all generated field names referenced by `dcn201_clk_mgr.c`, `dcn201_resource.c`, and `irq_service_dcn201.c`.
- Generated-register validation should compare each `*_MASK` and `*__SHIFT` pair in this range against AMD's DCN 2.0.1 register database and the companion addresses in `dcn_2_0_1_offset.h`.
- Display modeset tests should exercise pipe 0 and pipe 1 with varied formats, tiling modes, rotations, viewport sizes, luma/chroma planes, and cursor configurations.
- Page-flip and vblank/read-line IRQ tests should verify flip interrupts, vblank/read-line masks, status, clear behavior, surface-in-use tracking, and earliest-in-use addresses.
- Memory-pressure and power-management tests should watch for HUBP underflow, DCHUBBUB timeout interrupts, bad p-state/self-refresh transitions, and incorrect request/return-buffer memory power states.
- Clock tests should verify DISPCLK/DPPCLK/DPREFCLK/audio DTO programming, pixel-rate selection, ramp-done status, FIFO error detection, and stable display/audio timing.
- HDMI/DP audio tests should validate Azalia codec capability exposure, endpoint access, DMA snoop/isochronous choices, audio DTO values, underflow filler behavior, and power-state transitions.
- Suspend/resume, hotplug, multi-display, cursor stress, and secure/TMZ surface scenarios should not leave stale cursor/DMDATA addresses, stuck memory-power state, missed interrupts, or corrupted display fetch settings.

Regression symptoms from bad constants include blank display, flicker, underflow logs, corrupted scanout, wrong cursor position or format, audio dropouts, incorrect display clock, repeated timeout interrupts, failed suspend/resume, missed vblank/read-line events, broken flips, or failures that appear only on one pipe instance.

## Cross-Chunk Notes

This is the first chunk of `dcn_2_0_1_sh_mask.h`. Later chunks continue pipe 2, additional pipe instances and display blocks, and the rest of the generated DCN 2.0.1 register layout. The final per-file document should treat all chunks as one generated hardware interface and avoid describing each register family as independent algorithmic code.

### subset-b-001642: lines 2552-5077

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 2552-5077

## Scope

This chunk is part of the generated AMD DCN 2.0.1 ASIC register mask/shift header. It covers lines 2552-5077 and exports preprocessor constants for display hub pipe, hub request/return, cursor, DPP top, converter, scaler, and color-management register fields. The slice contains 2,105 `#define` entries: 1,052 `__SHIFT` constants and 1,053 `_MASK` constants. It has no C functions, structs, enums, or executable control flow; its API is the generated macro namespace consumed by AMDGPU display register helper code.

The chunk starts in the tail of the `HUBP2_DCHUBP_REQ_SIZE_CONFIG_C` mask set and ends mid-register at `CM0_CM_BLNDGAM_RAMB_REGION_16_17`, so whole-file reconciliation must merge it with adjacent chunks for complete register-family coverage.

## Purpose

The purpose of this chunk is to map symbolic DCN 2.0.1 display register fields to exact bit positions and bit masks. Runtime AMDGPU display code can then use generated field names with register access macros instead of hand-coded shifts and constants.

Major hardware domains represented here are:

- `HUBP2` control, clock, debug, and measurement-window fields for hub pixel processor instance 2.
- `HUBPREQ2` and `HUBPREQ3` request-path fields for pitch, luma/chroma primary and secondary surface addresses, metadata surface addresses, DCC/TMZ control, flip control, flip interrupts, in-use/earliest-in-use tracking, expansion modes, TTU/QoS timing, blanking, prefetch, vblank, flip, nominal delivery timing, cursor request timing, ref-clock conversion, destination Y limits, and request memory power control/status.
- `HUBPRET2` and `HUBPRET3` return-path fields for detile-buffer control, memory power, read-line windows, vblank/read-line interrupt status/clear/mask bits, current read-line value, and read-line status.
- `CURSOR0_2` and `CURSOR0_3` fields for cursor enable/mode/pitch, surface address, size, position, hotspot, stereo, destination offset, cursor memory power, and DMDATA address/QoS/status/software-write handling.
- `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, and `DSCL0` fields for DPP control/reset/CRC/host-read, surface pixel format conversion, FP bias/scale, color keying, cursor color conversion, scaler coefficient RAM, scaler ratios/init/taps, RECOUT/MPC dimensions, line-buffer format, memory power, and output buffer control.
- `CM0` fields for input color-space conversion, gamut remap matrices, bias, degamma LUT programming, degamma RAM A/B region descriptors, blending gamma LUT programming, and blending gamma RAM A/B region descriptors.

## Important API Surface

The exported surface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important examples in this chunk include:

- `HUBP2_DCHUBP_CNTL__HUBP_DISABLE__SHIFT` / `_MASK`, `HUBP2_DCHUBP_CNTL__HUBP_UNDERFLOW_STATUS__SHIFT` / `_MASK`, and `HUBP2_HUBP_CLK_CNTL__HUBP_CLOCK_ENABLE__SHIFT` / `_MASK` for pipe enable, underflow, and clock state.
- `HUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS*`, `HUBPREQ2_DCSURF_SECONDARY_SURFACE_ADDRESS*`, and matching `_C` and metadata address macros for luma/chroma scanout and DCC metadata programming.
- `HUBPREQ2_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN`, `*_TMZ`, and secondary/meta TMZ fields for compression/security-related fetch configuration.
- `HUBPREQ2_DCSURF_FLIP_CONTROL`, `HUBPREQ2_DCSURF_FLIP_CONTROL2`, and `HUBPREQ2_DCSURF_SURFACE_FLIP_INTERRUPT` for update locking, pending flip state, GSL/triple-buffer behavior, and flip interrupt status/clear/mask fields.
- `HUBPREQ2_DCN_*`, `HUBPREQ2_PREFETCH_SETTINGS*`, `HUBPREQ2_VBLANK_PARAMETERS_*`, `HUBPREQ2_FLIP_PARAMETERS_*`, `HUBPREQ2_NOM_PARAMETERS_*`, and per-line delivery fields for request scheduling and watermark-style timing.
- The same `HUBPREQ3`, `HUBPRET3`, and `CURSOR0_3` families repeated for pipe instance 3.
- `DPP_TOP0_DPP_CONTROL`, `CNVC_CFG0_CNVC_SURFACE_PIXEL_FORMAT`, `CNVC_CFG0_FORMAT_CONTROL`, `DSCL0_SCL_*`, and `DSCL0_LB_*` for DPP format/scaler programming.
- `CM0_CM_ICSC_*`, `CM0_CM_GAMUT_REMAP_*`, `CM0_CM_DGAM_*`, and `CM0_CM_BLNDGAM_*` for matrix color transforms and piecewise LUT region programming.

These constants are normally consumed through AMD display helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, register field-list macros, and symbol-pasting helpers like `SF`, `TF_SF`, or block-specific field table builders. For this exact header family, `drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c` includes `dcn/dcn_2_0_1_sh_mask.h`; the DPP color-management fields visible here are also represented in DCN20 DPP field-list macros in `drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h`.

## Control Flow

There is no local control flow in this header chunk. Runtime behavior is external and follows the display driver's register programming sequences:

- Resource and block constructors bind generated offset, mask, and shift tables to specific DCN 2.0.1 hardware blocks.
- HUBP/HUBPREQ programming code writes format, tiling, pitch, address, metadata, DCC, TMZ, VM/timing, and flip-related fields when enabling planes or performing page flips.
- IRQ service code uses generated interrupt masks/shifts to enable, query, and clear vblank, read-line, and flip interrupts.
- DPP scaler and color code writes CNVC, DSCL, and CM fields while applying plane format conversion, scaling, gamut remap, degamma, and blending gamma state.
- Power-management paths write force/disable/low-power-mode fields and poll corresponding status fields for HUBPREQ, HUBPRET, cursor, DSCL, and OBUF memories.

Ordering is an implicit contract enforced by callers, not by this file. For example, callers must apply update locks, program related surface address and metadata fields, handle flip timing, and clear sticky interrupt bits in the sequence required by hardware.

## State and Persistence

The file has no software state. Its macros describe memory-mapped hardware state that persists in the GPU display blocks while powered:

- Surface pitch, address, metadata address, DCC, TMZ, and format fields define the active scanout memory interpretation.
- Flip control, pending, in-use, earliest-in-use, and interrupt fields track frame-boundary update state.
- TTU, prefetch, vblank, flip, nominal, per-line delivery, cursor timing, and ref-frequency conversion fields persist as scheduler parameters used by HUBPREQ.
- Clock, blank, disable, timeout, underflow, read-line, and memory power fields expose live block state and sticky health/status bits.
- DPP, CNVC, DSCL, and CM fields persist as active image processing state for a plane, including scaler coefficients/ratios, color matrices, LUT indices/data, and gamma region descriptors.

Incorrect constants can therefore corrupt persistent hardware programming until a modeset, block reprogramming, GPU reset, or power transition restores correct register contents.

## Dependencies and Integration Points

This chunk depends on the matching DCN 2.0.1 register offset header and on AMD display register helper macros that paste register and field identifiers into `__SHIFT` and `_MASK` symbols. It is tightly coupled to the DCN 2.0.1 hardware register specification.

Key integration points include:

- DCN 2.0.1 IRQ service setup through `drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`, which includes this mask header for interrupt source field metadata.
- HUBP and HUBPREQ/HUBPRET display pipe code that programs scanout surfaces, flip sequencing, request timing, cursor fetch state, and memory power state by pipe instance.
- DPP code, especially DCN20-generation field-list macros in `drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h`, which reference `CM0_CM_BLNDGAM_*`, `CM0_CM_DGAM_*`, scaler, converter, and color management fields.
- Register address constants in the corresponding `dcn_2_0_1_offset.h` family; mask/shift definitions are only meaningful when paired with the correct register offsets.
- Cross-generation generated headers such as `dcn_2_0_0_sh_mask.h`, `dcn_2_1_0_sh_mask.h`, and later `dcn_3_*`/`dcn_4_*` variants. The names are similar, but field presence and masks can diverge, so copying between generations is risky.

## Risks

- A wrong mask or shift silently writes the wrong hardware bits. Highest-risk fields in this chunk include surface addresses, metadata addresses, DCC/TMZ enables, flip locks/pending bits, interrupt clears, memory power controls, scaler ratios, and color LUT region descriptors.
- Pipe instance drift is likely because `HUBPREQ2`/`HUBPREQ3`, `HUBPRET2`/`HUBPRET3`, and `CURSOR0_2`/`CURSOR0_3` are near-duplicate families. A one-bit mismatch may only affect a specific pipe or multi-display layout.
- Address-high masks are narrower than address-low masks, typically 16-bit versus 32-bit. Treating the address pairs uniformly can truncate scanout, metadata, or DMDATA addresses.
- Status and clear bits share registers with mask/type/control bits in interrupt and underflow paths. Incorrect read-modify-write masks can lose interrupts, fail to acknowledge sticky status, or clear status unexpectedly.
- Timing fields are narrow and packed. Overflow or stale masks in prefetch, vblank, nominal, delivery, and scaler-ratio fields can produce underflow, tearing, or validation failures only under specific modes.
- Color-management region macros use repeated RAM A/RAM B and channel-specific start/slope/end/region patterns. A swapped region offset or channel mask can create hard-to-debug color/gamma errors rather than compile failures.
- Because this is a generated constants-only header, normal unit tests do not exercise the macros directly; many errors surface only through integration builds, static comparison, or hardware/display behavior.

## Test Signals

Useful validation signals for changes to this chunk are:

- AMDGPU display driver compilation for DCN 2.0.1 and nearby DCN20 paths, which catches missing or renamed macros in IRQ, HUBP, DPP, scaler, and color-management code.
- Static diff against the vendor register database or adjacent generated DCN 2.0.1 artifacts, especially verifying each `__SHIFT` has the intended `_MASK` and that repeated pipe 2/pipe 3 families remain consistent where hardware requires it.
- Multi-pipe runtime display tests with planes on pipe 2 and pipe 3, including primary/secondary plane flips, luma/chroma formats, DCC-enabled surfaces, TMZ-protected surfaces, cursor movement, stereo cursor fields, and metadata-address changes.
- Interrupt tests for flip, vblank, and read-line mask/status/clear behavior in `HUBPREQ*` and `HUBPRET*` registers.
- Suspend/resume, memory power-gating, and clock-gating tests that verify memory power status fields converge and no underflow/timeout bits remain stuck.
- Image-quality tests for DPP0 conversion, scaling, color keying, gamut remap, degamma, and blending gamma programming, including LUT load/readback or visual CRC-style checks where available.

## Chunk Notes

This chunk is generated register metadata, not functional logic. The main research value is identifying the hardware surfaces covered and the risk profile of the exported constants: display memory fetch, flip/interrupt sequencing, request timing, cursor fetch/DMDATA, DPP scaler/format conversion, and color-management LUT/matrix programming. The final merged file report should connect this slice with adjacent chunks to cover the complete `dcn_2_0_1_sh_mask.h` register map.

### subset-b-001643: lines 5078-7595

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 5078-7595

## Purpose

This chunk is part of the generated DCN 2.0.1 register shift/mask header for the AMDGPU display engine. It contains no executable C code; it defines `#define` constants that describe bit positions and masks for display pipe processor (DPP) registers. The driver uses these constants to build per-ASIC `shift` and `mask` tables, then accesses fields through the `REG_GET`, `REG_SET`, `REG_UPDATE`, and related register-helper macros.

The assigned range starts in the middle of the DPP0 color-management (`CM0`) blend-gamma RAM-B region definitions, then covers DPP0 shaper, 3D LUT, and color-management memory-power fields. It then defines the DPP1 top, converter, cursor, scaler, and full color-management field set, and ends at the beginning of the DPP2 scaler block after `DSCL2_SCL_HORZ_FILTER_INIT`.

The highest-value content is the DPP1 block because it is complete in this range: `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, `DSCL1`, and `CM1` masks collectively describe the programmable path from source pixel format conversion, cursor handling, scaling/filter coefficient RAM, color-space/gamma/LUT processing, and DPP diagnostics.

## Important APIs, Types, And Macros

- `*_SHIFT` macros: give the right-shift amount for a named register field. Examples include `CM1_CM_SHAPER_CONTROL__CM_SHAPER_LUT_MODE__SHIFT`, `CNVC_CFG1_FORMAT_CONTROL__ALPHA_EN__SHIFT`, and `DSCL1_SCL_MODE__SCL_COEF_RAM_SELECT__SHIFT`.
- `*_MASK` macros: give the bit mask for the same field. These are paired with the shift constants by the register-helper layer.
- `CM0_*`, `CM1_*`: color-management field definitions for blend gamma, degamma, shaper LUTs, 3D LUT, input CSC, gamut remap, bias, HDR multiplier, coefficient format, de-alpha, and color-management memory power.
- `DPP_TOP1_*` and `DPP_TOP2_*`: DPP control, clock enable, reset, CRC value/control, and host-read-rate field definitions.
- `CNVC_CFG1_*` and `CNVC_CFG2_*`: converter configuration fields for source pixel format, expansion, alpha, bypass/alignment, clamping, floating-point bias/scale, color keying, and 2-bit alpha LUT entries.
- `CNVC_CUR1_*` and `CNVC_CUR2_*`: cursor-control fields for enable, cursor mode, ROM degamma enable, pixel inversion, alpha modulation, colors, and FP scale/bias.
- `DSCL1_*` and `DSCL2_*`: display scaler fields for coefficient RAM addressing/data, scaler mode, tap counts, 2-tap controls, manual replication, scale ratios, initial filter phase, overscan, recout/MPC size, line-buffer format/memory, OBUF power, and scaler memory power.
- Integration macros outside this file, especially `TF_REG_LIST_DCN201(id)` and `TF_REG_LIST_SH_MASK_DCN201(mask_sh)` in `display/dc/dpp/dcn201/dcn201_dpp.h`, alias the DCN 2.0 DPP register and field lists and consume these generated symbols.

## Register Families Covered

- DPP0 color-management tail, lines 5078-5647: completes `CM0_CM_BLNDGAM_RAMB_REGION_18_19` through `_32_33`, then defines `CM0` HDR multiplier, shared/blend-gamma memory-power control and status, de-alpha, coefficient format, shaper LUT control/data/write-enable, shaper RAM A/B region maps, shaper memory-power controls/status, 3D LUT mode/index/data/read-write controls, output normalization/offsets, and test debug index/data.
- DPP1 top/control, lines 5648-5714: `DPP_TOP1_DPP_CONTROL` exposes clock enable, input/output enable, and read-only enable/status fields; `DPP_TOP1_DPP_SOFT_RESET` covers DPP and CM reset bits; CRC registers expose RGB/A captured values and CRC mode/source/stereo/interlace/pixel-format controls.
- DPP1 converter and cursor, lines 5715-5818: `CNVC_CFG1_*` configures source pixel interpretation and color keying; `CNVC_CUR1_*` configures cursor0 modes and colors.
- DPP1 scaler, lines 5819-6055: `DSCL1_*` defines coefficient RAM programming, scaler mode and coefficient RAM bank selection, tap counts, filter scale ratios/initial phases, overscan, recout/MPC geometry, line-buffer configuration/status, scaler LUT memory power/status, output buffer control, and OBUF memory power.
- DPP1 color management, lines 6056-7356: `CM1_*` mirrors the full color pipeline, including input CSC and gamut-remap matrices, bias, degamma LUT RAM A/B region tables, blend-gamma LUT RAM A/B region tables, shaper LUT RAM A/B region tables, HDR/3D LUT controls, memory-power controls/status, and output offsets.
- DPP2 beginning, lines 7357-7595: defines the same DPP top, converter, cursor, and early scaler coefficient/mode/tap/ratio fields for instance 2. The range ends before the rest of `DSCL2` is defined.

## Control Flow

There is no runtime control flow in this header. The effective flow is compile-time table construction followed by runtime register-helper calls:

1. `display/dc/resource/dcn201/dcn201_resource.c` includes `dcn_2_0_1_sh_mask.h`.
2. `dcn201_resource.c` builds `tf_shift` with `TF_REG_LIST_SH_MASK_DCN201(__SHIFT)` and `tf_mask` with `TF_REG_LIST_SH_MASK_DCN201(_MASK)`.
3. `dcn201_dpp.h` maps `TF_REG_LIST_SH_MASK_DCN201()` to `TF_REG_LIST_SH_MASK_DCN20()`, so the DCN 2.0 DPP field list is populated from symbols such as `CM0_CM_SHAPER_CONTROL__CM_SHAPER_LUT_MODE__SHIFT` and `CNVC_CFG0_FORMAT_CONTROL__ALPHA_EN_MASK`. Per-instance register addresses are separately built through `TF_REG_LIST_DCN201(id)`.
4. Runtime code in `dcn201_dpp.c`, `dcn20_dpp.c`, `dcn20_dpp_cm.c`, and inherited DCN10 scaler helpers uses `REG_UPDATE`, `REG_SET`, and `REG_GET` with field names. The helper layer looks up the shift/mask values in the DPP object and emits masked MMIO reads/writes.

The DPP1 and DPP2 symbols in this chunk are generated instance-specific equivalents of the instance-0 symbols used to populate shared field lists. They matter for direct instance-specific register maps and for consistency across generated DCN register headers, even when the common DPP field table is anchored on the `CM0`, `CNVC_CFG0`, and `DSCL0` naming pattern.

## State And Persistence Behavior

The header itself owns no software state and performs no reads or writes. Its state effect is indirect: every mask and shift controls how later driver code mutates hardware MMIO registers. Those register writes persist in display hardware until changed by another modeset/color update, power transition, or hardware reset.

The fields in this chunk describe several hardware state machines and RAM-backed blocks:

- Color LUT state persists in DPP-local degamma, blend-gamma, shaper, and 3D LUT RAMs. Region tables define LUT offsets, segment counts, start/end points, base values, slopes, and active RAM bank selection.
- Converter state persists pixel-format, alpha, clamping, color-key range, and 2-bit alpha LUT settings for each pipe.
- Scaler state persists coefficient RAM contents, selected coefficient bank, tap counts, scale ratios, initial phases, overscan, line-buffer format, and memory-power overrides/status.
- Cursor state persists cursor mode, enable, color registers, ROM enable, pixel inversion, and FP scale/bias.
- Diagnostic state includes DPP CRC controls and captured CRC values.

Because fields are packed into shared 32-bit registers, an incorrect mask or shift can corrupt adjacent hardware state during a read-modify-write operation.

## Dependencies

This generated header depends on the DCN 2.0.1 ASIC register specification and must stay aligned with the paired address header `dcn_2_0_1_offset.h` and higher-level DPP register lists. The driver-side dependencies are:

- `display/dc/resource/dcn201/dcn201_resource.c`, which includes this file and instantiates DPP register, shift, and mask tables for DCN 2.0.1 resources.
- `display/dc/dpp/dcn201/dcn201_dpp.h`, which reuses DCN 2.0 DPP register and field-list macros for DCN 2.0.1.
- `display/dc/dpp/dcn201/dcn201_dpp.c`, which wires the DPP function table and uses the populated tables for setup, scaler programming, color functions, cursor functions, and alpha keying.
- `display/dc/dpp/dcn20/dcn20_dpp.c` and `display/dc/dpp/dcn20/dcn20_dpp_cm.c`, which provide shared DCN20-era implementations for state readback, converter setup, color keying, cursor attributes, HDR multiplier, degamma, blend LUT, shaper LUT, and 3D LUT programming.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c`, inherited for scaler coefficient RAM programming and scaler setup paths that use `DSCL*_SCL_*` masks and shifts.
- `reg_helper.h` and the display MMIO service layer, which combine register offsets, masks, and shifts into actual MMIO transactions.

## Integration Points

The primary integration point is DCN201 resource creation. `dcn201_resource.c` allocates four DPP instances and passes the per-instance `tf_regs[]`, shared `tf_shift`, and shared `tf_mask` tables into `dpp201_construct()`. From there, each `struct dcn201_dpp` uses these tables through the DPP function table.

Important runtime paths connected to this chunk include:

- Plane setup: `dpp201_cnv_setup()` programs `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `ALPHA_2BIT_LUT`, cursor disable bits for unsupported YUV layouts, and powers on OBUF/scaler LUT memory.
- Alpha/color keying: `dpp2_cnv_set_alpha_keyer()` writes `COLOR_KEYER_CONTROL` and low/high channel ranges for alpha, red, green, and blue.
- Cursor configuration: `dpp2_set_cursor_attributes()` writes `CURSOR0_CONTROL`, `CURSOR0_COLOR0`, and `CURSOR0_COLOR1`; inherited cursor position code also relies on compatible cursor register tables.
- Scaler programming: inherited scaler helpers write `SCL_COEF_RAM_TAP_SELECT`, `SCL_COEF_RAM_TAP_DATA`, `SCL_MODE`, tap controls, scale ratios, initial phases, line-buffer controls, and scaler memory-power bits.
- Color pipeline: `dpp20_read_state()` reads shaper, 3D LUT, and blend-gamma status; `dpp2_set_degamma_pwl()`, `dpp20_program_blnd_lut()`, `dpp20_program_shaper()`, and `dpp20_program_3dlut()` rely on the CM LUT, region, RAM-select, write-enable, and status fields represented here.
- Diagnostics and bring-up: `DPP_TOP*_DPP_CRC_*`, `DPP_TOP*_DPP_SOFT_RESET`, and host-read controls are exposed for state readback, validation, and low-level debug.

## Risks And Edge Cases

- This file is generated hardware interface data. Manual edits are risky because a one-bit error in a mask or shift can make register-helper read-modify-write calls program the wrong field while still compiling cleanly.
- The requested range starts mid-family at `CM0_CM_BLNDGAM_RAMB_REGION_18_19`; the earlier `CM0` blend-gamma control, RAM-A, and RAM-B region definitions are outside this chunk. Any final per-file report must reconcile this chunk with adjacent chunks before describing the full DPP0 color path.
- The range ends inside the `DSCL2` scaler block after `DSCL2_SCL_HORZ_FILTER_INIT`; later DPP2 vertical filter, line-buffer, memory-power, and OBUF fields are outside this chunk.
- Instance naming is repetitive and easy to mismatch. `CM1_*`, `CNVC_CFG1_*`, and `DSCL1_*` must correspond to DPP instance 1 register addresses; substituting an instance 0 or 2 symbol in a register list would direct writes to the wrong pipe.
- LUT programming depends on bank selection/status fields. Wrong `*_WRITE_SEL`, `*_RAM_SEL`, `*_CONFIG_STATUS`, or `*_MODE_CURRENT` masks can cause the driver to update a currently active LUT bank or read stale status.
- Power-management fields such as `CM*_CM_MEM_PWR_CTRL*`, `DSCL*_DSCL_MEM_PWR_CTRL`, and `OBUF_MEM_PWR_CTRL` can gate SRAMs used by later programming. Incorrect values can cause timeouts, blank output, or lost LUT/coef RAM contents.
- Scaler coefficient fields pack two signed coefficients and enable bits into one word. Incorrect masks for `SCL_COEF_RAM_EVEN_TAP_COEF`, `SCL_COEF_RAM_ODD_TAP_COEF`, or their enable bits can produce image-quality regressions rather than obvious failures.
- CRC and host-read controls are diagnostic-facing but can affect validation. Incorrect CRC source, pixel-format, stereo, cursor, or mask fields would make hardware CRC tests misleading.

## Test Signals

- Build coverage: compile the AMDGPU display driver for a DCN201-enabled configuration. The generated symbols must satisfy `TF_REG_LIST_SH_MASK_DCN201(__SHIFT)` and `_MASK` table initialization without missing-field errors.
- Modeset smoke tests on DCN 2.0.1 hardware: attach displays, enable multiple planes, move/scale planes, and verify no blanking or DPP power/timeout errors.
- Pixel-format coverage: exercise ARGB/RGB formats, FP16 formats, 4:2:0 YCbCr/YCrCb formats, 10-bit formats, and 2-bit alpha LUT cases that drive `CNVC_CFG*` fields.
- Cursor tests: enable mono and color cursors, toggle cursor degamma/ROM behavior, and verify cursor disable behavior on formats where the DPP setup forces cursor off.
- Scaling tests: cover identity, upscaling, downscaling, chroma scaling, even/one-tap cases, and coefficient RAM bank switching. Visual inspection and CRC comparison should catch wrong `DSCL*` masks.
- Color tests: program degamma, blend gamma, shaper LUT, 3D LUT, HDR multiplier, gamut remap, and bypass modes, then compare hardware CRCs or captured output against reference images.
- Power-management tests: suspend/resume, display power-gating, and repeated modesets should preserve or correctly reprogram CM/scaler SRAM state after memory-power transitions.
- Diagnostics: DPP CRC readback should change predictably with source selection, pixel-format selection, cursor inclusion, and CRC mask fields.

### subset-b-001644: lines 7596-10129

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 7596-10129

## Scope

This chunk is part of AMDGPU's generated DCN 2.0.1 register field shift/mask header. It covers lines 7596-10129 of `dcn_2_0_1_sh_mask.h` and contains preprocessor constants only: 2,111 `#define` entries, including 1,056 `__SHIFT` constants and 1,079 `_MASK` constants. There are no C functions, structs, enums, variables, loops, or branches in this source range.

The chunk starts in the middle of the DPP2 display scaler (`DSCL2`) field definitions, covers the complete DPP2 color-management (`CM2`) field block, then covers DPP3 top/CNVC/cursor/scaler blocks and the beginning of the DPP3 color-management (`CM3`) block. The final per-file reconciliation should merge this artificial slice with adjacent chunks because both the opening `DSCL2` area and the closing `CM3_CM_BLNDGAM_RAMB_REGION_0_1` area are partial logical regions.

## Purpose

The purpose of this range is to publish exact bit positions and masks for DCN 2.0.1 display pipe registers. Functional display code uses these constants with the matching register address header, `dcn_2_0_1_offset.h`, and DC register helper macros to encode and decode packed memory-mapped hardware register fields.

The represented hardware domains are:

- Tail `DSCL2` fields for horizontal/vertical luma and chroma scale ratios, filter init phases, bottom-field phases, black offsets, scaler update pending state, scaler autocalibration, external overscan, OTG blanking, recout/MPC geometry, line-buffer data format, line-buffer memory partitions and counters, DSCL memory power, OBUF control, and OBUF memory power.
- Full `CM2` color-management fields for bypass/update state, input CSC matrices, gamut remap matrices, bias, degamma control and LUT access, degamma RAM A/B piecewise-linear region metadata, blend-gamma control and LUT access, blend-gamma RAM A/B region metadata, HDR multiplier coefficient, CM memory power/status, dealpha, coefficient format, shaper controls/LUTs/RAM A/B region metadata, additional memory power controls, and 3D LUT mode/index/data/read-write normalization/offset fields.
- `DPP_TOP3` fields for DPP3 control, soft reset, CRC readout/control, and host read control.
- `CNVC_CFG3` fields for surface pixel format, format conversion/expansion/clamping, floating-point bias/scale, color keyer control and color values, and alpha 2-bit LUT.
- `CNVC_CUR3` cursor fields for cursor0 enable/mode/format/address-related control, cursor colors, and cursor FP scale/bias.
- Full `DSCL3` fields mirroring the scaler, line-buffer, memory-power, OBUF, overscan, blanking, recout, and MPC geometry controls for DPP instance 3.
- Beginning `CM3` fields for color-management bypass/update state, input CSC and gamut remap matrices, bias, degamma control/LUT/RAM region metadata, and blend-gamma control/LUT/RAM A plus the start of RAM B region metadata.

Although this repository path is under `ceph-client`, this header range is AMD display hardware metadata. It has no Ceph filesystem protocol behavior and no distributed filesystem persistence semantics.

## Important API Surface

The exported API surface is the macro namespace. Each hardware field is represented by paired constants:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned bit mask for read-modify-write and extraction helpers.

Representative field families include:

- `DSCL2_SCL_VERT_FILTER_INIT__SCL_V_INIT_FRAC__SHIFT` / `_MASK` and the related chroma/bottom-field forms for scaler phase programming.
- `DSCL2_DSCL_MEM_PWR_CTRL__LB_G*_MEM_PWR_FORCE__SHIFT` / `_MASK` and `DSCL2_DSCL_MEM_PWR_STATUS__LB_G*_MEM_PWR_STATE__SHIFT` / `_MASK` for scaler LUT and line-buffer memory power control/status.
- `CM2_CM_ICSC_C11_C12__CM_ICSC_C11__SHIFT` / `_MASK` and the other matrix coefficient fields for input color-space conversion.
- `CM2_CM_GAMUT_REMAP_CONTROL__CM_GAMUT_REMAP_MODE__SHIFT` / `_MASK` plus RAM A/B matrix coefficients for gamut remapping.
- `CM2_CM_DGAM_LUT_INDEX`, `CM2_CM_DGAM_LUT_DATA`, and `CM2_CM_DGAM_LUT_WRITE_EN_MASK` fields for degamma LUT programming.
- `CM2_CM_BLNDGAM_*` and `CM3_CM_BLNDGAM_*` region fields for piecewise-linear blend-gamma RAM layout, with LUT offsets, segment counts, region starts, slopes, end bases, and end slopes.
- `CM2_CM_SHAPER_*` and `CM2_CM_3DLUT_*` fields for HDR shaper and 3D LUT programming, normalization, offsets, and read/write control.
- `DPP_TOP3_DPP_CRC_CTRL` and `DPP_TOP3_DPP_CRC_VAL_*` fields for DPP-level CRC diagnostics.
- `CNVC_CFG3_CNVC_SURFACE_PIXEL_FORMAT__CNVC_SURFACE_PIXEL_FORMAT__SHIFT` / `_MASK` and `CNVC_CFG3_FORMAT_CONTROL` fields for pixel format conversion, expansion mode, alpha enablement, clamping, and bypass behavior.
- `DSCL3_DSCL_AUTOCAL`, `DSCL3_LB_MEMORY_CTRL`, `DSCL3_OBUF_CONTROL`, and `DSCL3_OBUF_MEM_PWR_CTRL` fields for DPP3 scaler setup and buffering.

Consumers do not normally spell the long instance-specific identifiers directly. DCN code builds register, shift, and mask tables with macros such as `TF_REG_LIST_DCN201(id)`, `TF_REG_LIST_SH_MASK_DCN201(__SHIFT)`, `TF_REG_LIST_SH_MASK_DCN201(_MASK)`, `SF(...)`, and per-block `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `REG_READ` helpers.

## Control Flow

This header chunk has no local runtime control flow. Runtime behavior is created by the display core that includes this generated metadata:

1. DCN 2.0.1 resource construction includes `dcn_2_0_1_offset.h` and this mask header, then expands block-specific list macros into `dcn201_dpp_registers`, `dcn201_dpp_shift`, and `dcn201_dpp_mask` tables.
2. DPP setup code selects pixel formats, alpha handling, input color space, cursor behavior, scaler mode, scaler ratios, taps, color transforms, degamma/blend/shaper/3D LUT programming, and memory-power policy.
3. Register helper macros combine the register address with the corresponding `__SHIFT` and `_MASK` values from this header to write packed fields or decode hardware state.
4. Hardware applies those programmed fields during modeset, plane enable, scaling, color-management update, cursor update, page flip, power-gating, diagnostic CRC capture, or display readback.

Ordering constraints are external to this file. For example, callers must sequence LUT index/data/write-enable programming correctly, avoid reading status before hardware has latched updates, and respect DSCL/OBUF/CM memory-power transition timing. This header only supplies bit layouts; it does not encode access type, reset values, self-clearing behavior, or safe programming order.

## State And Persistence Behavior

The file stores no software state. Its constants map to hardware register state that persists according to DCN 2.0.1 hardware rules while the display block is powered.

The represented hardware state includes:

- Scaler geometry and filtering state: scale ratios, initial phases, taps/coefficient RAM access, black offsets, overscan, blanking, recout size/start, MPC output size, line-buffer format, line-buffer partitioning, and OBUF behavior.
- Color pipeline state: CM bypass and update-pending bits, input CSC and gamut remap coefficients, bias values, degamma and blend-gamma LUT modes, LUT indices/data/write masks, HDR multiplier, dealpha, coefficient format, shaper LUTs, shaper scale/offset, and 3D LUT controls/data/output normalization.
- Power state: DSCL LUT/line-buffer memory force/disable/status bits, OBUF memory power force/disable/mode/state bits, and CM memory power/status fields.
- Diagnostic state: DPP3 CRC values/control and host read control.
- Converter and cursor state: surface pixel format, format expansion/conversion/clamping, FP bias/scale, color-key alpha/R/G/B values, alpha 2-bit LUT entries, cursor enable/mode/color fields, and cursor FP scale/bias.

Some fields are programmed configuration, some are readback/status, some are write-enable or index/data ports, and some are update-pending or power-state indicators. The header does not distinguish those classes beyond field names. Incorrect constants can therefore create persistent hardware misconfiguration until the driver reprograms the block, resets the pipe, power-cycles the block, or the GPU resets.

## Dependencies And Integration Points

This chunk is tightly coupled to the generated DCN 2.0.1 register address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h`

Direct include points found in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`

For this specific chunk, the most direct integration is DPP resource setup in `dcn201_resource.c`, where `TF_REG_LIST_DCN201(id)` and `TF_REG_LIST_SH_MASK_DCN201(...)` bind DPP register addresses, shifts, and masks into `tf_regs`, `tf_shift`, and `tf_mask`. Those tables are passed to `dpp201_construct()` in `display/dc/dpp/dcn201/dcn201_dpp.c`.

Functional users include shared DPP and color-management code:

- `display/dc/dpp/dcn201/dcn201_dpp.c` programs `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `ALPHA_2BIT_LUT`, cursor disable paths, and DPP functions for degamma, blend LUT, shaper LUT, 3D LUT, scaler, HDR multiplier, and gamut remap.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c` uses DSCL fields for scaler modes, autocalibration, line-buffer configuration, recout/MPC dimensions, OBUF behavior, and DSCL memory power polling.
- `display/dc/dpp/dcn10/dcn10_dpp_cm.c` uses CM fields for gamut remap matrices, degamma/blend/shaper piecewise-linear LUT programming, CM memory power, LUT write masks, and color-management readback.
- `display/dc/core/dc_hw_sequencer.c` reaches these DPP operations through high-level plane/color update sequencing, so errors here can surface during normal modeset, atomic commit, and color-management flows.

The instance suffixes are part of the contract. `CM2`/`DSCL2` and `CM3`/`DSCL3` describe different DPP instances with nearly mirrored layouts. Generic code relies on instance-indexed register lists rather than treating the names as interchangeable.

## Risks And Edge Cases

- Silent hardware misprogramming is the main risk. A wrong shift or mask can compile cleanly while writing adjacent fields or failing to update the intended hardware bits.
- Repeated instance blocks are vulnerable to generated copy/paste drift. `DSCL2`/`DSCL3` and `CM2`/`CM3` are similar but must match the exact DCN 2.0.1 register database for each instance.
- LUT programming fields are high risk because index, data, write-enable mask, RAM select, and region metadata must agree. Bad masks in `CM*_DGAM_*`, `CM*_BLNDGAM_*`, `CM*_SHAPER_*`, or `CM*_3DLUT_*` can produce wrong gamma, banding, HDR errors, or incorrect color-space output.
- Matrix coefficient fields are packed 16-bit halves. Incorrect masks for CSC or gamut remap coefficient pairs can corrupt one coefficient while preserving the other, making color errors subtle and format-dependent.
- Scaler ratio and phase fields use fixed-width fractional formats. Overflow or wrong masks in scale ratio/init fields can cause visual distortion, edge sampling errors, scaler underflow, or bad 4:2:0 chroma alignment.
- Geometry fields such as blanking, overscan, recout, MPC size, and line-buffer partition counts are packed into shared registers. Bad values can affect only specific modes, pipe splits, or scaling ratios.
- Power-control fields combine force, disable, mode, and status semantics. Confusing `*_MEM_PWR_CTRL` with `*_MEM_PWR_STATUS`, or using a bad mask in `REG_WAIT`, can leave DSCL/CM/OBUF memories unavailable or unnecessarily powered.
- Converter and cursor fields are format-sensitive. Incorrect `CNVC_SURFACE_PIXEL_FORMAT`, alpha, clamp, FP bias/scale, color key, or cursor fields can break only certain pixel formats such as FP16, 10bpc, packed RGB, or 4:2:0 video.
- The chunk boundaries are not semantic boundaries. The line range starts after earlier `DSCL2` definitions and ends before completing `CM3_CM_BLNDGAM_RAMB_REGION_*`; whole-file analysis should not infer missing hardware support from this slice alone.

## Test Signals

Useful validation for changes to this generated range is mostly build-time plus display hardware behavior:

- Build AMDGPU display code paths that include `dcn_2_0_1_sh_mask.h`, especially DCN201 resource, IRQ, clock manager, DPP, DSCL, and CM translation units.
- Static generated-register comparison should verify every `__SHIFT` and `_MASK` value against AMD's DCN 2.0.1 register database and the matching addresses in `dcn_2_0_1_offset.h`.
- Modeset and plane tests should exercise DPP instances 2 and 3 with no scaling, upscaling, downscaling, 4:2:0 luma/chroma scaling, multi-plane composition, pipe split, overscan, cursor enable/disable, and recout/MPC geometry changes.
- Color-management tests should cover input CSC, gamut remap, degamma PWL, blend LUT, shaper LUT, 3D LUT, HDR multiplier, coefficient format changes, and readback where supported.
- Pixel-format tests should cover ARGB/RGBA variants, RGB565/ARGB1555, 10bpc formats, FP16, RGB111110/BGR101111, and 4:2:0 video formats that drive CNVC and input CSC fields.
- Power-management stress should cover suspend/resume, runtime power gating, memory power transitions, clock changes, and repeated color/scaler updates while checking that `*_UPDATE_PENDING`, `*_MEM_PWR_STATUS`, and OBUF/DSCL status fields settle.
- Diagnostic signals include DPP CRC sanity, lack of DSCL/OBUF underflow symptoms, stable cursor behavior, absence of color banding or matrix errors, and no unexpected hangs during LUT programming.

## Cross-Chunk Notes

This is a generated constants-only slice. Its substantive behavior lives in the DCN201 display driver code and DCN 2.0.1 hardware. Adjacent chunks are needed to describe the full `dcn_2_0_1_sh_mask.h` file, including the earlier DPP2 scaler fields before line 7596 and the remaining CM3 fields after line 10129.

### subset-b-001645: lines 10130-12631

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 10130-12631

## Scope

This chunk is a generated AMD DCN 2.0.1 register field header segment. It contains 2,107 preprocessor definitions: 1,053 `__SHIFT` constants and 1,054 `_MASK` constants. The definitions describe bit positions and masks for color-management (`CM3_CM_*`), multi-plane compositor (`MPCC*`), MPC global/output, and MPCC output-gamma (`MPCC_OGAM*`) hardware registers. There are no C functions, types, branches, or storage objects in this chunk; its runtime effect comes from inclusion by display driver register tables and `REG_*` access macros elsewhere in the AMD display stack.

## Purpose

The chunk provides the bitfield contract for programming display-pipeline hardware blocks on DCN 2.0.1 ASICs. These macros let higher-level display code pack and unpack MMIO register values without hard-coded numeric shifts in functional code. The covered register families configure:

- `CM3_CM_BLNDGAM_RAMB_*`, continuing blend-gamma RAM B endpoint and 34-region piecewise-linear metadata for the CM3 color-management block.
- `CM3_CM_HDR_MULT_COEF`, `CM3_CM_DEALPHA`, `CM3_CM_COEF_FORMAT`, shaper LUT, 3D LUT, and CM memory power control/status fields.
- `MPCC0` through `MPCC4` compositor instance selection, blending, gain, background color, memory power, stall, and status fields.
- MPC global controls such as clock/reset, background bypass, stall window, host read, vertical-update lock sets, output muxes, and denormalization clamp controls.
- `MPCC_OGAM0`, `MPCC_OGAM1`, and the first part of `MPCC_OGAM2` output-gamma RAM A/B mode, LUT index/data/control, PWL region layout, slope, start, and endpoint fields.

## Important APIs, Types, And Macros

This header segment is consumed indirectly by generated register-list macros and typed register structures rather than exposing functions itself. The important API surface is the naming convention:

- `REGISTER__FIELD__SHIFT` gives the low-bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask in the 32-bit register value.
- Comments such as `// addressBlock: dce_dc_mpc_mpcc0_dispdec` group definitions by hardware address block.

For MPC/MPCC integration, `drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h` maps these names through `SF(...)`, `SRII(...)`, and field-list macros into `struct dcn20_mpc_shift`, `struct dcn20_mpc_mask`, and `struct dcn20_mpc_registers`. `dcn20_mpc.c` then reads the generated shift/mask tables when programming output gamma:

- `mpc2_ogam_get_reg_field()` copies `MPCC_OGAM_RAMA_*` shifts and masks into an `xfer_func_reg`.
- `mpc2_program_luta()` and `mpc2_program_lutb()` bind the instance-specific RAM A/B register addresses and call `cm_helper_program_xfer_func()`.
- `mpc20_configure_ogam_lut()` updates `MPCC_OGAM_LUT_RAM_CONTROL` fields for write masks and RAM bank selection.
- `mpc20_get_ogam_current()` reads `MPCC_OGAM_CONFIG_STATUS`.
- `mpc20_power_on_ogam_lut()` writes `MPCC_OGAM_MEM_PWR_DIS`.

The MPCC0-4 and MPC output fields also align with the older DCN10 common MPC code for blending, output muxing, and status reads, while DCN20 adds output gamma and denormalization fields.

## Control Flow

The chunk itself has no executable control flow. At build time the preprocessor makes these shift/mask constants available to DCN-specific register table initializers. At runtime, control flow is driven by display-manager operations:

1. DC creates an MPC implementation for the ASIC generation with register addresses, shifts, and masks initialized from generated headers.
2. Plane composition paths use MPCC fields such as `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, `MPCC_MODE`, alpha blending mode, global alpha/gain, background bpc, and gain mode through `REG_UPDATE*` helpers.
3. Color pipeline paths choose an MPCC OGAM LUT bank, program PWL region metadata and LUT data, then switch or query active gamma state using the associated control/status fields.
4. Output paths configure MPC output muxes and denorm/clamp fields for OPP routing and color range handling.
5. Power-management paths toggle CM and MPCC/OGAM memory power controls and may poll status fields in newer generations.

Because `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT` depend on these masks and shifts, an incorrect definition silently changes the MMIO bitfield touched by otherwise type-correct code.

## State And Persistence

The macros do not persist state in system memory. They describe persistent hardware state held in display MMIO registers until overwritten, reset, power-gated, or reinitialized during modesets/resume. Relevant hardware state described by this chunk includes:

- Double-buffer-like gamma bank state for RAM A/RAM B in both CM shaper/blend gamma and MPCC OGAM blocks.
- LUT write index/data/control state for shaper, 3D LUT, and OGAM programming.
- Memory power force/disable/status state for shared CM memory, blend-gamma memory, 3D LUT memory, and MPCC OGAM memory.
- MPCC compositor state for plane links, blending parameters, gains, OPP assignment, status, and stall accounting.
- MPC update-lock and output mux/denormalization state that affects when routed output changes become visible.

The display driver must restore these registers after GPU reset, display resume, or full hardware reinitialization. The header does not encode defaults or sequencing constraints.

## Dependencies

This chunk depends on the generated ASIC register ecosystem around `dcn_2_0_1`. It is meaningful only when paired with register-address headers for the same ASIC and the AMD display register helper macros. Key dependencies and consumers include:

- `drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h` for register/field list construction.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.c` for MPCC, MPC output CSC/denorm, and output-gamma programming.
- Common color helpers such as `cm_helper_program_xfer_func()` and `cm_helper_program_color_matrices()`, which consume register/field metadata.
- `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and related MMIO helpers that combine masks and shifts to access fields.

There are no Linux VFS, Ceph, networking, or distributed-filesystem dependencies in this specific source chunk despite its repository path.

## Integration Points

The major integration point is AMDGPU Display Core on DCN 2.0-class hardware. The chunk is source-tree-aligned under `drivers/gpu/drm/amd/include/asic_reg/dcn`, while functional integration occurs under `drivers/gpu/drm/amd/display/dc`.

Important integration surfaces:

- MPCC blending and routing: `MPCC0_MPCC_*` through `MPCC4_MPCC_*` fields support five compositor instances. Per-instance register names share the same field layout, allowing array-indexed register programming.
- MPC global/output: `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_OUT0_MUX`, `MPC_OUT1_MUX`, and denorm clamp registers connect plane-composition output to OPP/output paths.
- Update locks: `ADR_CFG_CUR_VUPDATE_LOCK_SET*`, `ADR_CFG_VUPDATE_LOCK_SET*`, `ADR_VUPDATE_LOCK_SET*`, `CFG_VUPDATE_LOCK_SET*`, and `CUR_VUPDATE_LOCK_SET*` fields coordinate atomic-ish hardware updates around vertical update windows.
- Color pipeline: CM3 shaper, blend gamma, HDR multiplier, 3D LUT, and MPCC OGAM registers integrate with transfer-function and color-management programming.

## Risks

- Field drift risk: generated masks/shifts must match the DCN 2.0.1 register spec exactly. A wrong bit position can program an adjacent hardware field and cause display corruption, blanking, incorrect gamma, broken blending, or power-state issues.
- Cross-generation reuse risk: DCN20 code often uses instance-zero field definitions as canonical layouts for all instances. If a later ASIC or instance has a divergent layout, the shared `SF(MPCC_OGAM0_..., ...)` pattern can become unsafe.
- Bank-selection risk: OGAM and CM shaper/blend gamma use RAM A/B banks. Incorrect `*_LUT_RAM_SEL`, `*_CONFIG_STATUS`, region, start, end, or slope fields can select the wrong bank or produce transient color glitches during updates.
- Power-control polarity risk: fields named `*_PWR_DIS`, `*_PWR_FORCE`, and `*_PWR_STATE` are easy to misuse because enable/disable polarity differs by field. The header gives masks only, not semantics.
- Partial chunk boundary risk: this segment begins in the middle of `CM3_CM_BLNDGAM_RAMB_*` and ends in the middle of `MPCC_OGAM2_MPCC_OGAM_RAMB_*`; the complete per-file report must merge adjacent chunks for full register-family coverage.
- Testing gap risk: normal compilation verifies macro names exist, but cannot prove that bit masks match hardware. Hardware or emulator validation is needed for behavioral confidence.

## Test Signals

Useful validation signals for code depending on this chunk:

- Build coverage for DCN 2.0.1 AMDGPU display code with generated register lists enabled; missing or renamed macros should fail compilation in `dcn20_mpc.h`/related initialization units.
- Modeset and plane-composition tests that exercise multiple MPCC instances, global alpha/gain, background color, OPP routing, and MPC output mux fields.
- Color-management tests that program output gamma PWL LUTs, switch between RAM A and RAM B, and verify observed gamma output or CRCs.
- HDR/shaper/3D LUT tests that write LUT indices/data and validate rendered output against expected transfer functions.
- Suspend/resume, GPU reset, and display hotplug tests that confirm CM, MPCC, MPC, and OGAM state is restored and no stale power-disabled memory state remains.
- Register readback diagnostics for `MPCC_STALL_STATUS`, `MPCC_STATUS`, `CM*_MEM_PWR_STATUS`, and `MPCC_OGAM_CONFIG_STATUS` when debugging display bring-up.

### subset-b-001646: lines 12632-15144

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 12632-15144

## Purpose

This chunk is part of AMDGPU Display Core Next 2.0.1 generated register field metadata. It contains no executable C logic; it publishes compile-time bit positions and masks for DCN hardware registers. Each field is represented by paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Runtime display code combines these constants with companion address macros from `dcn_2_0_1_offset.h` and register helper macros such as `SF`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

The assigned range covers several display-pipeline blocks:

- The tail of the `MPCC_OGAM2` output-gamma RAM B region table for regions 20-33.
- Full `MPCC_OGAM3` and `MPCC_OGAM4` output-gamma blocks, including mode, LUT index/data/control, RAM A and RAM B start/slope/end controls, and paired region descriptors for regions 0-33.
- `MPC_OUT0` and `MPC_OUT1` output color-space-conversion fields for two coefficient banks, plus the MPC OCSC debug index register.
- Output pixel processor blocks for OPP/FMT/DPG/OPPBUF/OPP_PIPE instances 0 and 1, covering clamping, dithering, pixel format, 4:2:0/4:2:2 handling, display-pattern-generator controls, OPP buffer sizing/3D parameters, and OPP pipe clock gating.
- OPP top clock-control bits.
- ODM/OPTC input blocks for instances 0 and 1, including underflow/double-buffer status, data source selection, DSC data format, bytes-per-pixel, width, input clock control, and spare registers.
- The `OTG0` timing-generator block and the beginning of the `OTG1` block, covering horizontal/vertical timing, dynamic refresh-rate controls, trigger controls, enable/blank/interlace/status fields, CRC/signature capture, static-screen/3D/GSL/global-update controls, range timing interrupts, DRR/request/DSC positions, and early `OTG1` timing/control fields through `OTG1_OTG_INTERLACE_STATUS`.

Although this repository path is under a local `ceph-client` tree, this source is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem state, or storage persistence.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this chunk. The macro namespace is the API.

The `MPCC_OGAM*` macros describe per-MPCC output gamma LUT programming. Important field families include `MPCC_OGAM_MODE`, `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, `MPCC_OGAM_LUT_RAM_CONTROL`, per-channel RAM A/B start controls, linear slopes, end bases/slopes, and repeated region descriptors. The region descriptors pack two regions per register: a low-half LUT offset and segment count, then a high-half LUT offset and segment count. The repeated masks are consistent across instances and RAM banks: LUT offsets use 9-bit fields, segment counts use 3-bit fields, and start/end/slope/base fields use wider 16-18 bit ranges depending on the register.

The `MPC_OUT*_CSC_*` macros expose the output color-space-conversion matrix. `MPC_OUT_CSC_COEF_FORMAT` selects coefficient format per output path, `MPC_OUT0_CSC_MODE` and `MPC_OUT1_CSC_MODE` select the OCSC mode, and the `C11_C12` through `C33_C34` registers carry packed 16-bit coefficients for banks A and B. `MPC_OCSC_TEST_DEBUG_INDEX` exposes a debug selector field for MPC OCSC diagnostics.

The `FMT0` and `FMT1` macros describe the formatter side of OPP. They cover clamp lower/upper bounds for R/G/B, dynamic expansion enable/mode, pixel encoding and subsampling controls, bit-depth truncation, spatial/temporal dithering controls, random seeds, clamp data enable/color format, side-by-side stereo, 4:2:0 memory power and phase status, and 4:2:2 left-edge extra pixel control.

The `DPG0` and `DPG1` macros describe display pattern generator state: enable/mode, dynamic range, bit depth, vertical/horizontal resolution, ramp offsets/increments, active dimensions, color values, segment offset/width, and double-buffer pending status.

The `OPPBUF0`, `OPPBUF1`, `OPP_PIPE0`, and `OPP_PIPE1` macros describe OPP buffer and pipe controls: active width, pixel repetition, display segmentation, overlap pixels, 3D active-space sizes, and OPP pipe clock enable/status bits. `OPP_TOP_CLK_CONTROL` provides top-level OPP clock-gating override bits.

The `ODM0` and `ODM1` macros expose OPTC/ODM input state. `OPTC_INPUT_GLOBAL_CONTROL` contains enable, double-buffer, underflow status/clear, and current-status fields. `OPTC_DATA_SOURCE_SELECT` chooses source segments and segment count. `OPTC_DATA_FORMAT_CONTROL`, `OPTC_BYTES_PER_PIXEL`, and `OPTC_WIDTH_CONTROL` carry DSC/data-format related fields. `OPTC_INPUT_CLOCK_CONTROL` controls and reports input clocks.

The `OTG0` and `OTG1` macros expose timing-generator fields. Core fields include totals, blanking, sync start/end/polarity, `OTG_CONTROL` enable/reset/start/disable/current-state bits, `OTG_BLANK_CONTROL`, interlace controls/status, status position/frame counters, trigger A/B controls and manual triggers, force-count and force-vsync controls, vertical interrupt controls, CRC windows/data, static-screen controls, 3D structure controls, global sync lock controls, master update locks, global-control update-lock windows, DRR and request controls, and DSC start position. This chunk includes the complete `OTG0` set in the range and the first part of `OTG1` through interlace status.

## Control Flow

This header range has no runtime control flow. It is preprocessor data.

Runtime behavior appears through consumers that bind these field layouts into component-specific register tables. A typical flow is:

1. A DCN201 module includes `dcn_2_0_1_offset.h` for register addresses and this file for field masks/shifts.
2. A component header lists the fields it needs with `SF(register, field, mask_sh)` or related helper macros.
3. Initialization code stores the selected masks/shifts in component structures for MPC, OPP, OPTC/timing-generator, IRQ, or clock-management paths.
4. Runtime code uses `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `REG_READ`, `REG_WRITE`, or `REG_WAIT` to pack/unpack register values using the generated masks and shifts.
5. Hardware applies the resulting MMIO writes according to display engine sequencing rules, double-buffer update modes, vblank/update locks, or self-clearing status/ack behavior.

Control-sensitive behavior represented by this chunk includes programming output gamma LUTs, selecting MPC output CSC modes and coefficients, configuring formatter bit depth and dithering, enabling pattern generators, configuring OPP buffers and clocks, selecting ODM/OPTC inputs and DSC widths, enabling OTG timing, changing dynamic refresh-rate totals, handling vertical/range interrupts, using OTG triggers, synchronizing global updates, and reading CRC/status counters. The macros themselves do not enforce legal values, sequencing, read-only status semantics, or write-one-to-clear behavior.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in display hardware registers.

The represented state spans several display subsystems:

- MPCC output gamma state: LUT mode, selected RAM, LUT index/data payloads, RAM A/B region segmentation, per-channel starts, slopes, end bases, and end slopes.
- MPC output CSC state: output CSC mode, coefficient format, double-buffered A/B matrix coefficient banks, and OCSC debug selection.
- OPP/FMT state: clamp bounds, dynamic expansion, pixel encoding, subsampling, truncation, spatial and temporal dithering, random seed values, 4:2:0/4:2:2 handling, pattern generator programming, OPP buffer geometry, and pipe clock state.
- ODM/OPTC state: data source routing, DSC data format and slice width, bytes-per-pixel, input clock gating/status, double-buffer pending, and underflow sticky status/clear bits.
- OTG state: active timing, blank/sync windows, trigger configuration/status, frame/line counters, vertical interrupt windows, CRC capture windows/results, static-screen counters, stereo/3D settings, global sync lock, master update locks, DRR timing bounds, request controls, and DSC start position.

Persistence is hardware-specific. Some fields are persistent programming values until reset or power gating; some are double-buffered and take effect only at a selected update point; some are live status bits; some are sticky interrupt/status bits requiring explicit clear/ack fields; and some are self-clearing trigger fields. Values can be changed by modesets, atomic commits, vblank/update-lock sequences, hotplug handling, suspend/resume, firmware/BIOS handoff, power management, or ASIC reset. This generated header does not encode those access rules.

## Dependencies

This chunk depends on the generated DCN 2.0.1 register-header ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h` supplies matching register addresses and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c` includes both offset and mask headers and declares DCN201 display-resource capabilities, including `max_num_otg = 2`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn20/dcn20_mpc.h` consumes `MPC_OUT0_CSC_*` and `MPCC_OGAM0_*` style mask/shift fields through `MPC_COMMON_MASK_SH_LIST_DCN2_0`; this chunk provides the same generated field layout for later MPCC/OPP instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h` consume FMT, OPPBUF, OPP_PIPE, and DPG field names through `OPP_SF`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.h`, `dcn20_optc.h`, and `dcn201_optc.h` consume OTG and ODM fields through `SF` entries used by timing-generator code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c` also include this mask header for DCN201-specific register field access.

The generated constants assume the AMD DC register helper convention where `REGISTER__FIELD_MASK` is already positioned and `REGISTER__FIELD__SHIFT` is the low bit. Any consumer that computes `(value << SHIFT) & MASK` or extracts `(reg & MASK) >> SHIFT` depends on that invariant.

## Integration Points

The main integration point is the DCN201 display-resource construction path. `dcn201_resource.c` includes this header during resource setup, and the component factories use the selected register lists and mask/shift lists to instantiate MPC, OPP, OPTC/timing-generator, IRQ, and clock-manager objects.

MPC/MPCC integration covers plane composition and post-blend color processing. Output gamma macros are used by MPC code that programs output transfer functions and LUT RAMs. CSC macros are used by output color-space-conversion paths that program RGB/YCbCr conversion or gamut/range transformations.

OPP/FMT/DPG integration covers final pixel formatting before timing generation and link output. Formatter masks influence truncation, dithering, clamping, pixel encoding, stereo, and chroma-subsampling behavior. DPG fields support internal pattern generation for bring-up, diagnostics, and test modes. OPPBUF and OPP_PIPE fields control buffering, segmentation, and pipe clocking.

ODM/OPTC integration covers output data routing into timing generators and DSC-aware output paths. The DCN201 OPTC header directly references `ODM0_OPTC_DATA_SOURCE_SELECT`, `ODM0_OPTC_DATA_FORMAT_CONTROL`, `ODM0_OPTC_BYTES_PER_PIXEL`, and `ODM0_OPTC_WIDTH_CONTROL`, which are defined in this chunk for instances 0 and 1.

OTG integration covers modesets, vblank timing, dynamic refresh rate, global update synchronization, CRC capture, interrupts, stereo/3D state, and stream enable/disable. Runtime code in the DC timing-generator implementation updates fields such as `OTG_CONTROL.OTG_MASTER_EN`, `OTG_V_TOTAL_CONTROL`, `OTG_DOUBLE_BUFFER_CONTROL`, and `OTG_GSL_CONTROL` using masks with this naming pattern.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly while clearing the wrong bits, failing to update the intended field, corrupting adjacent fields during read-modify-write, or misreading status.

High-risk MPCC/MPC fields include output gamma LUT index/data/control, RAM A/B region descriptors, start/slope/end values, OCSC modes, coefficient formats, and packed CSC coefficients. Errors can cause wrong transfer functions, color shifts, clipping, banding, incorrect RGB/YCbCr conversion, or failed color-management programming.

High-risk OPP/FMT fields include bit-depth truncation, dither enable/depth/mode, pixel encoding, subsampling mode, 4:2:0 memory control, clamp bounds, and DPG controls. Bad constants can cause visible artifacts, wrong color range, chroma placement errors, disabled clocks, bad test patterns, or OPP underflow.

High-risk ODM/OPTC fields include segment source selection, DSC mode, DSC bytes-per-pixel, slice width, input clock enable/status, double-buffer pending, and underflow status/clear. Mistakes can route the wrong data stream into an OTG, break DSC output, leave underflow status stuck, or gate clocks unexpectedly.

OTG fields are especially sequencing-sensitive. `OTG_MASTER_EN`, sync/blank totals, DRR min/max/mid controls, trigger clear/status bits, vertical interrupt clear/status bits, CRC controls, global sync lock, master update locks, and double-buffer update modes affect live scanout. Incorrect values can cause blank display, unstable refresh timing, missed vblank interrupts, CRC test failures, deadlocks waiting for update pending bits, or hangs during enable/disable.

The repeated instance layout creates generator-copy risk. `MPCC_OGAM3` and `MPCC_OGAM4`, `FMT0` and `FMT1`, `DPG0` and `DPG1`, `ODM0` and `ODM1`, and `OTG0` and `OTG1` are mostly mirrored. A suffix mismatch can affect only one display pipe and may only surface on dual-display, ODM, or multi-pipe configurations.

This chunk starts and ends on artificial line boundaries. It begins after the earlier `MPCC_OGAM2` RAM B region table has already started, and it ends inside the `OTG1_OTG_INTERLACE_STATUS` register after the shift fields and before the remaining masks and following `OTG1` fields. The final per-file merge should treat these as chunk boundaries rather than source omissions.

## Test Signals

Useful validation is mostly compile-time, generated-register consistency, and display hardware behavior:

- Kernel/driver builds for DCN201 paths should compile all `SF`/`OPP_SF`/component register-list references that rely on this mask header.
- Generated-register validation should compare every `*_MASK` and `*__SHIFT` pair in this range against AMD's register database and the companion address definitions in `dcn_2_0_1_offset.h`.
- Color-management tests should exercise MPCC output gamma programming and MPC output CSC programming, including LUT uploads, coefficient-bank swaps, RGB/YCbCr conversion, HDR/SDR transfer behavior, and visible banding/clipping checks.
- Formatter tests should cover truncation, spatial and temporal dithering, clamping, pixel encoding, 4:2:0 and 4:2:2 modes, and side-by-side stereo where supported.
- Pattern-generator diagnostics should verify DPG enable/mode, active dimensions, color values, ramp increments, offsets, and double-buffer pending behavior.
- ODM/DSC tests should verify data source selection, DSC mode, bytes-per-pixel, slice width, segment width, input clock status, and underflow clear/status handling on both supported pipes.
- Timing tests should exercise OTG0 and OTG1 modesets across multiple timings, interlace, blanking/sync polarity, DRR, vblank interrupts, vertical interrupt windows, trigger A/B, force-count/force-vsync, CRC windows/results, master update locks, GSL, and DSC start position.
- Suspend/resume, hotplug, display blank/unblank, dual-display, and atomic modeset stress tests should not leave OTG update locks pending, clocks gated incorrectly, underflow bits stuck, or scanout enabled with stale timing.

Regression symptoms from bad constants include blank or flickering display, wrong colors or gamma, visible dithering artifacts, failed DSC modes, underflow storms, missed vblank/range interrupts, CRC mismatches, DRR instability, stuck update-pending waits, failed dual-pipe/ODM routing, or behavior that fails only on the second OTG/OPP/ODM instance.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_1_sh_mask.h` define preceding DCN201 display register mask families and the beginning of `MPCC_OGAM2`. Later chunks complete `OTG1_OTG_INTERLACE_STATUS` and continue through the rest of the `OTG1` and subsequent DCN register field families. The final per-file report should describe this source as one generated DCN201 hardware layout contract rather than as algorithmic driver code.

### subset-b-001647: lines 15145-17562

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 15145-17562

## Scope

This chunk is a generated-style AMD DCN 2.0.1 register field header segment. It contains only C preprocessor constants, not executable functions or structs. Each register field is exported as paired `__SHIFT` and `_MASK` macros so the AMD display driver can construct read/modify/write operations against memory-mapped display hardware registers.

The covered range starts in the `OTG1` timing generator block, continues through OPTC misc, DIO I2C, DIO power/clock/interrupt state, HPD0/HPD1, DP AUX0/AUX1, and ends inside the DIG0/TMDS encoder field set.

## Purpose

The chunk gives the DCN 2.0.1 display stack the bit layout for several display hardware units:

- `OTG1_*`: optical timing generator status, counters, snapshots, interrupts, CRC windows/results, static-screen detection, 3D/stereo state, global sync lock, GSL, DRR, DSC start position, and update-lock controls.
- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`: OPTC misc source routing and clock gating fields.
- `DC_I2C_*`: DDC/I2C controller command, arbitration, transaction, status, speed, setup, and data fields.
- `DIO_*`: DIO scratch registers, memory power state/control, clock gating, generic interrupt, and HDMI RX status timer fields.
- `HPD0_*` and `HPD1_*`: hot-plug-detect status, interrupt control, debounce/toggle filtering, fast train, and RX interrupt timing fields.
- `DP_AUX0_*` and `DP_AUX1_*`: DisplayPort AUX controller enable/reset, software and link-service transaction control, arbitration, interrupt, RX/TX data, PHY timing, and status fields.
- `DIG0_*`, `HDMI_*`, `AFMT_*`, `TMDS_*`: digital front/back end selection, HDMI packet/control/status, metadata/audio formatting, generic infoframe bytes, audio clock regeneration, IEC 60958 channel status, audio test/CRC, and TMDS pattern/control fields.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The public surface is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted register mask for that field.
- Field consumers combine these constants through AMD display register helper macros such as `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `I2C_SF`, `AUX_SF`, `LE_SF`, and `SE_SF`.

Important register families in this chunk:

- `OTG1_OTG_STATUS`, `OTG1_OTG_STATUS_POSITION`, `OTG1_OTG_STATUS_FRAME_COUNT`, `OTG1_OTG_STATUS_VF_COUNT`, and `OTG1_OTG_STATUS_HV_COUNT` expose live scanout state and counters.
- `OTG1_OTG_INTERRUPT_CONTROL`, `OTG1_OTG_GLOBAL_SYNC_STATUS`, and `OTG1_OTG_RANGE_TIMING_INT_STATUS` define interrupt mask/type/status/clear fields.
- `OTG1_OTG_UPDATE_LOCK`, `OTG1_OTG_DOUBLE_BUFFER_CONTROL`, `OTG1_OTG_MASTER_UPDATE_LOCK`, and `OTG1_OTG_GLOBAL_CONTROL0..3` define atomic timing-update and double-buffering behavior.
- `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC1_HW_STATUS`, `DC_I2C_DDC2_HW_STATUS`, `DC_I2C_TRANSACTION0..3`, and `DC_I2C_DATA` define DDC command setup and status reporting.
- `DP_AUX0_AUX_*` and `DP_AUX1_AUX_*` are nearly parallel channel instances for AUX control, arbitration, interrupts, SW/LS status, data FIFOs, DPHY timing, and DPHY status.
- `DIG0_HDMI_*`, `DIG0_AFMT_*`, and `DIG0_TMDS_*` define stream encoder fields for HDMI/DP audio/video packet generation and TMDS control.

## Control Flow

This header has no runtime control flow. Runtime flow is indirect:

1. DCN 2.0.1 resource and block constructors include this header along with the matching address header.
2. Register-table macros bind register addresses with the `__SHIFT` and `_MASK` constants into per-block register, shift, and mask tables.
3. Display code calls accessor helpers such as `REG_UPDATE`, `REG_GET`, `I2C_SF`, `AUX_SF`, `LE_SF`, or `SE_SF`.
4. Those helpers use the constants from this header to pack field values into MMIO writes or unpack field values from MMIO reads.

Examples of downstream use in the tree include:

- `display/dc/dce/dce_i2c_hw.c` updates `DC_I2C_CONTROL` fields such as `DC_I2C_GO`, `DC_I2C_SOFT_RESET`, `DC_I2C_DDC_SELECT`, and `DC_I2C_TRANSACTION_COUNT`.
- `display/dc/dce/dce_i2c_hw.h` maps `DC_I2C_*` field definitions through `I2C_SF`.
- `display/dc/dce/dce_aux.h` maps `DP_AUX0_AUX_CONTROL` fields through `AUX_SF`.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and later link encoder headers map AUX/HPD fields through `LE_SF`.
- `display/dc/dce/dce_stream_encoder.h` and DIO stream encoder headers map HDMI/AFMT/DIG fields through `SE_SF`.
- `display/dc/irq/dcn201/irq_service_dcn201.c` includes this DCN 2.0.1 shift/mask header for interrupt-related register definitions.

## State And Persistence Behavior

The macros are compile-time constants and store no software state. The state they describe lives in hardware registers:

- OTG state includes scanline/frame counters, vblank/hblank status, update-lock state, double-buffer pending bits, static screen state, CRC status/data, GSL sync gap status, and DRR last-used total.
- I2C and AUX state includes transaction in-progress/done bits, arbitration ownership, timeout/overflow/NACK/error status, reply byte counts, and hardware/firmware request state.
- HPD state includes current sense, delayed sense, RX interrupt status, connect/disconnect debounce counters, and interrupt acknowledgements.
- DIO power and clock fields describe persistent hardware gating or memory power choices until changed by driver power-management code or hardware.
- HDMI/AFMT/TMDS fields configure packet generation, metadata/audio payload bytes, double-buffer transfer, audio FIFO/CRC status, and TMDS encoding/test patterns.

Several fields are write-one-to-clear or acknowledgement style by naming convention, including interrupt `*_ACK`, `*_CLEAR`, `*_CLR`, and `*_TAKEN_CLR` fields. Incorrect writes can drop pending interrupts or clear evidence before higher layers observe it.

## Dependencies

This chunk depends on the wider AMD display register framework:

- Matching address definitions in the paired DCN 2.0.1 offset/header files provide register addresses. This file only provides field positions and masks.
- AMD DC register accessor macros expect the exact `REG__FIELD__SHIFT` and `REG__FIELD_MASK` names.
- Linux AMDGPU display code supplies MMIO access, IRQ service plumbing, DDC/AUX transaction state machines, link encoder setup, stream encoder setup, and power management policy.
- Hardware register semantics are defined by DCN 2.0.1 ASIC behavior; the header does not validate field values or sequence constraints.

## Integration Points

The chunk participates in these higher-level subsystems:

- Display timing and vblank handling through OTG status, frame counters, global sync, vertical interrupt, update-lock, and GSL fields.
- Atomic modeset/programming safety through OTG double-buffer, master update lock, VUPDATE keepout, global update lock, and HDMI/metadata double-buffer status fields.
- Connector discovery and EDID/DDC through DC I2C and HPD fields.
- DisplayPort sideband communication through DP AUX0/AUX1 fields, including DPCD/EDID access, link training support, HPD-disconnect detection, and low-speed AUX monitor status.
- HDMI and DP stream encoding through DIG0 HDMI packet controls, audio infoframes, generic packets, MPEG/ISRC payloads, ACR values, AFMT audio status, and TMDS encoder controls.
- Power management through DIO memory power, light-sleep, and clock-gating fields for I2C, DP, HDMI, AFMT, and DME blocks.

## Risks And Edge Cases

- Mask/shift drift from the real ASIC specification is high impact. A single incorrect bit can cause silent misprogramming of timing, interrupts, I2C/AUX transactions, HDMI packets, or power gating.
- The chunk is instance-specific in places. `OTG1`, `HPD0/1`, `DP_AUX0/1`, and `DIG0` names must match the address/header instance mapping used by the resource tables; cross-instance copy mistakes can compile but program the wrong block.
- Several status/control registers share fields for SW, DMCU/firmware, and hardware ownership. Bad arbitration masks around `DC_I2C_ARBITRATION` or `DP_AUX*_AUX_ARB_CONTROL` can race firmware or leave a bus permanently owned.
- Interrupt control fields include mask/type/status/ack/clear bits packed together. Read-modify-write helpers must avoid unintentionally setting clear/ack bits.
- Double-buffer and update-lock fields have ordering constraints that are not represented in the macros. Callers must still sequence locks, writes, pending waits, and unlocks correctly.
- Power gating and memory power force/dis fields can disable hardware needed by active links if used outside the proper power-management path.
- AUX/I2C status includes many error bits such as timeout, overflow, HPD disconnect, invalid stop/start/sync, partial byte, and NACK indicators. Tests that only check success paths may miss broken masks for recovery paths.
- Later ASIC headers have similar names with changed fields. Backporting or copying tables between DCN generations needs exact generation matching.

## Test Signals

Good validation signals for this chunk are mostly integration and hardware-oriented:

- Build coverage for DCN 2.0.1 display paths, ensuring all register table macro expansions compile with this header.
- Modeset and vblank tests that exercise OTG status, frame counters, vertical interrupts, update locks, global sync, and double-buffer pending bits.
- Display CRC tests that read `OTG1_OTG_CRC*` data and verify window/mask programming.
- EDID/DDC tests through I2C on both DDC channels, including timeout, NACK, overflow, and arbitration recovery cases.
- DisplayPort AUX/DPCD link-training tests across AUX0 and AUX1, including HPD disconnect and low-speed read status paths.
- Hotplug tests on HPD0 and HPD1 for connect/disconnect debounce, RX interrupt acknowledgement, polarity, and interrupt enable behavior.
- HDMI/DP stream encoder tests that verify infoframes, generic packets, audio packet enablement, ACR N/CTS values, AFMT channel status, and TMDS mode fields.
- Runtime power-management tests that toggle DIO clock/memory power fields and verify active links, audio, AUX, and HPD continue or resume correctly.

### subset-b-001648: lines 17563-19999

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 17563-19999

## Purpose

This chunk is part of AMDGPU Display Core's generated DCN 2.0.1 register shift/mask header. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and already-positioned masks for fields inside DCN display, link, PHY, DCIO, DDC, and HPD registers.

The covered range is the DIO/link-encoder tail of display instance 0, a full DP0 block, most of DIG1/DP1, and the beginning of DCIO GPIO/pinstrap metadata:

- The chunk starts in the middle of `DIG0_TMDS_CTL2_3_GEN_CNTL`, then completes `DIG0` version, lane-enable, AFMT audio-clock, AFMT VBI generic-packet update, and HDMI generic immediate-send fields.
- It defines the `DP0` DisplayPort link/stream block, including link status, pixel format, MSA metadata and timing, video stream enable/status, FIFO overflow reporting, DPHY training/test/CRC/scrambler controls, secondary-data and audio packet controls, MST/MSE allocation/status, DSC controls, metadata packet transmission, VBID misc fields, and data-bypass controls.
- It defines the `DIG1` digital encoder block, including front-end/back-end controls, output CRC, HDMI packet scheduling, HDMI audio/status/control, AFMT audio/infoframe/generic/ISRC/MPEG fields, TMDS control-symbol generation, lane enable, AFMT clock control, and generic-packet update/send controls.
- It defines the matching `DP1` DisplayPort block with the same broad register families as `DP0`, including DSC and metadata transmission fields.
- It begins DCIO-level register definitions for `DC_GENERICA`, `UNIPHYA`, `UNIPHYB`, `DC_PINSTRAPS`, `DCIO_CLOCK_CNTL`, DDC1/DDC2 GPIO registers, and the start of `DC_GPIO_HPD_MASK`.

Each hardware field appears through paired macros:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register position.

Driver code combines these constants with register-address macros from `dcn_2_0_1_offset.h` and with Display Core register helper macros such as `FN`, `FD`, `HWS_SF`, `SE_SF`, and `REG_UPDATE`-style helpers.

Although this source tree is under a `ceph-client` mirror path, this chunk is AMD GPU display hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, networking, or storage persistence.

## Important APIs, Types, And Constants

There are no functions, structs, enums, or storage objects in this chunk. The API surface is the macro namespace consumed by DCN201 resource tables and common display hardware blocks.

Important `DIG0` groups in this range are:

- `DIG0_TMDS_CTL2_3_GEN_CNTL`: control-symbol data selection, delay, inversion, modulation, feedback path, feedback sync, and pattern output for TMDS control lanes 2 and 3. The chunk begins after the first lines of this register, so adjacent chunk context is needed for the complete register.
- `DIG0_DIG_VERSION` and `DIG0_DIG_LANE_ENABLE`: digital encoder type and lane/clock enable bits.
- `DIG0_AFMT_CNTL`: AFMT audio clock enable/status.
- `DIG0_AFMT_VBI_PACKET_CONTROL1`: frame and immediate update controls plus pending bits for AFMT generic packets 0 through 7.
- `DIG0_HDMI_GENERIC_PACKET_CONTROL5`: immediate-send and pending bits for HDMI generic packets 0 through 7.

The `DP0_*` and `DP1_*` register families describe DisplayPort stream encoders for two hardware instances. Major groups include:

- Link and stream control: `DP_LINK_CNTL`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_LINK_FRAMING_CNTL`, and `DP_VID_INTERRUPT_CNTL`.
- Pixel and main-stream attributes: `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_MSA_MISC`, `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, `DP_VID_MSA_VBID`, `DP_MSA_TIMING_PARAM1` through `PARAM4`, and `DP_MSA_VBID_MISC`.
- DPHY training and diagnostics: `DP_DPHY_CNTL`, `DP_DPHY_TRAINING_PATTERN_SEL`, `DP_DPHY_SYM0` through `SYM2`, `DP_DPHY_8B10B_CNTL`, `DP_DPHY_PRBS_CNTL`, `DP_DPHY_SCRAM_CNTL`, CRC enable/control/result/MST status, fast-training controls/status, bit/serializer swap controls, HBR2 eye/pattern controls, and test-pattern fields.
- Secondary-data and audio packet controls: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `CNTL7`, `DP_SEC_FRAMING1` through `FRAMING4`, `DP_SEC_AUD_N/M` programming and readback, `DP_SEC_TIMESTAMP`, `DP_SEC_PACKET_CNTL`, and `DP_SEC_METADATA_TRANSMISSION`.
- MST/MSE programming: `DP_MSE_RATE_CNTL`, `DP_CP_MSE_STATUS`, `DP_MSE_RATE_UPDATE`, `DP_MSE_SAT0` through `SAT2`, `DP_MSE_SAT_UPDATE`, `DP_MSE_LINK_TIMING`, `DP_MSE_MISC_CNTL`, and `DP_MSE_SAT*_STATUS`.
- Compression and bypass: `DP_DSC_CNTL`, `DP_DSC_BYTES_PER_PIXEL`, and `DP_DB_CNTL`.

The `DIG1_*` groups describe the second digital/HDMI/TMDS stream encoder instance. They include front-end fields such as source select, pixel encoding, color format, stereosync, Dolby Vision, CRC/test patterns, FIFO status, HDMI metadata/generic/infoframe/audio/ACR controls, AFMT audio and IEC 60958 status fields, audio CRC/ramp/status fields, back-end enable/control fields, TMDS control character and DC-balancer fields, and AFMT/HDMI generic packet scheduling.

The DCIO groups at the end of the chunk include:

- `DC_GENERICA`: generic DCIO scratch/control payload fields.
- `UNIPHYA_LINK_CNTL` and `UNIPHYB_LINK_CNTL`: pixel-valid reset, minimum low duration, channel inversion, lane stagger, HPD mask, and pixel-frequency-change fields for the two UNIPHY links.
- `UNIPHYA_CHANNEL_XBAR_CNTL` and `UNIPHYB_CHANNEL_XBAR_CNTL`: lane crossbar source selections and link enable bits.
- `DC_PINSTRAPS`: hardware strap fields for SMS enable, audio availability, clock-controller bypass, and display connectivity.
- `DCIO_CLOCK_CNTL`: DCIO display-clock gate disable.
- `DC_GPIO_DDC1_*` and `DC_GPIO_DDC2_*`: DDC clock/data mask, pull-down, receive, AUX pad mode/polarity, hardware pull-down enable, drive-strength, output value, output enable, and input readback fields.
- `DC_GPIO_HPD_MASK`: HPD1-HPD6 mask, pull-disable, receive, and RX HPD selection fields. The chunk ends before `DC_GPIO_HPD_MASK` is complete.

Generated names that end in `MASK_MASK`, such as `DC_GPIO_DDC1_MASK__DC_GPIO_DDC1CLK_MASK_MASK`, are expected. The first `MASK` belongs to the hardware register/field name; the final `_MASK` is the generated mask-constant suffix.

## Control Flow

This header range has no runtime control flow. It is compile-time register metadata. Runtime behavior is created by code that chooses an instance, combines the offset and shift/mask tables, and performs MMIO reads or writes through Display Core helpers.

A typical DCN201 flow is:

1. `dcn201_resource.c`, `dcn201_clk_mgr.c`, or `irq_service_dcn201.c` includes `dcn/dcn_2_0_1_offset.h` and this shift/mask header.
2. Register-list macros instantiate per-block register tables for stream encoders, link encoders, audio engines, AUX/I2C/HPD, DIO, clock manager, and IRQ services.
3. Constructors such as `dcn20_stream_encoder_construct()`, `dcn201_link_encoder_construct()`, `dce_audio_create()`, `dcn10_dio_construct()`, and `dcn2_i2c_hw_construct()` receive address tables plus shift/mask tables.
4. Higher-level Display Core code performs modeset, link training, packet programming, audio setup, HPD/AUX/DDC handling, DSC setup, MST allocation, and clock/strap reads.
5. Hardware helpers encode or decode fields using these constants and issue register reads or writes.

Control-sensitive hardware actions represented by this chunk include enabling/disabling DIG lanes and clocks, scheduling AFMT/HDMI generic packets, enabling DP video streams, deferring DP stream disable, polling stream/link status, acknowledging DP FIFO overflows, programming MSA timing and VBID fields, selecting DP training and test patterns, enabling/disabling scrambling or CRC capture, programming secondary-data/audio packets, updating MST allocation tables, enabling DSC, selecting DDC/AUX pad behavior, reading HPD/DDC inputs, and changing UNIPHY lane routing/link state.

The macros do not encode legal values, access type, reset values, lock timing, or sequencing. Consumers must know when fields are writable, read-only, sticky, write-one-to-clear, self-clearing, double-buffered, or safe to change only during blanking/link-training windows.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes state held in DCN 2.0.1 display hardware registers.

Hardware state represented by this chunk includes:

- Digital encoder state: lane enables, DIG type, TMDS control-symbol generation, feedback and DC-balance behavior, FIFO status, output CRC/test-pattern state, front-end source/color/stereo state, and back-end enable state.
- HDMI/AFMT state: HDMI control/status, audio-packet and ACR controls, AVI/VBI/generic/infoframe scheduling, metadata packet control, AFMT audio clock, ISRC/MPEG/audio-infoframe payloads, IEC 60958 fields, audio CRC, ramp controls, packet update pending bits, and immediate-send pending bits.
- DisplayPort link and stream state: link-training complete/status, embedded-panel mode, lane count, pixel encoding/depth/combine, stream enable/status, MSA metadata/timing, video `M/N`, VBID, interrupt controls, framing, FIFO overflow flags, DPHY training/test/scrambler/PRBS/CRC status, secondary-data packet enable/update state, audio `N/M` values and readbacks, timestamp mode, metadata packet state, DSC mode/slice width/bytes-per-pixel, data-bypass disable, and MST/MSE allocation/status registers.
- DCIO/PHY state: UNIPHY channel inversion, lane stagger, crossbar lane mapping, link enable, pixel-valid reset, clock-gate override, generic DCIO scratch/control fields, and display strap readbacks.
- Connector GPIO state: DDC1/DDC2 clock/data output enables, output values, input readbacks, pad pull-downs, AUX pad mode/polarity, drive strength, hardware pull-down control, and HPD mask/pull-disable/receive status for HPD1-HPD6.

Persistence is hardware-specific. Programmed control fields generally persist until rewritten, display block reset, power gating, suspend/resume, or ASIC reset. Status fields reflect live hardware. Pending and immediate-send bits can be transient or self-clearing. FIFO overflow, CRC, interrupt, and status/ack fields may be sticky until explicitly cleared or acknowledged. Strap and fuse-like fields are usually read as board/ASIC configuration and should not be treated as mutable software state.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0.1 register-header contract:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h` supplies the matching `mm...` register addresses and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h` supplies the field layouts, including this chunk.
- Display Core `reg_helper.h` and common register macros fold offset/shift/mask constants into typed resource tables.

Observed local include points for this mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`

`dcn201_resource.c` is the main integration point for this range. It includes the offset and mask headers, defines stream encoder, link encoder, audio, AUX, HPD, I2C, DIO, and hardware-sequencer register tables, and creates DCN201 resources. The code also reads `DC_PINSTRAPS__DC_PINSTRAPS_AUDIO` through `generic_reg_get()` when populating resource straps.

The chunk's `DIG0`/`DIG1`, HDMI, AFMT, DP, DSC, and metadata fields integrate with stream encoder construction via `dcn20_stream_encoder_construct()`. The `UNIPHYA`/`UNIPHYB`, HPD, and AUX-related fields integrate with link encoder construction via `dcn201_link_encoder_construct()`. The `DC_GPIO_DDC*` fields integrate with hardware I2C/DDC creation through `dcn2_i2c_hw_construct()`. HPD fields also connect to IRQ source mapping and HPD acknowledgement logic in the DCN201 IRQ service.

The `DP0` and `DP1` register families are user-visible through display features: DP/eDP link training, MST, DSC, HDR/metadata secondary packets, audio, DP color format selection, stream enable/disable, and diagnostics. HDMI/TMDS and AFMT families are user-visible through HDMI video mode set, infoframes, generic packets, audio, ACR/N/CTS programming, and output CRC/test behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A bad shift or mask compiles successfully but can update the wrong bit, fail to update the intended field, corrupt adjacent fields during read-modify-write, or decode status incorrectly.

High-risk areas in this chunk include:

- Repeated instance layout. `DIG0`/`DP0` and `DIG1`/`DP1` use similar field families, and many consumers build tables by macro expansion. A prefix, instance, or lane mismatch can affect only one physical stream encoder or connector path and may be hard to reproduce.
- Chunk boundaries. The range starts in the middle of `DIG0_TMDS_CTL2_3_GEN_CNTL` and ends in the middle of `DC_GPIO_HPD_MASK`. Whole-file conclusions must merge adjacent chunks before treating either register as complete.
- Packet scheduling and pending bits. AFMT, HDMI generic, DP secondary-data, metadata, and VBI controls include frame-update, immediate-update, send, and pending fields. Incorrect handling can drop HDR metadata, AVI/audio/infoframe packets, ISRC/MPEG payloads, or generic packets.
- DP link and stream sequencing. `DP_VID_STREAM_ENABLE`, deferred disable, link-training status, MSA/VBID, `M/N`, DPHY training pattern, scrambler, PRBS, CRC, and FIFO overflow fields are timing-sensitive. Wrong constants can cause blank displays, failed link training, compliance-test failures, flicker, or incorrect diagnostics.
- MST/MSE state. SAT table fields, rate updates, link timing, and MSE status must align with stream allocation logic. Bad masks can misallocate MST bandwidth or report the wrong slot status.
- DSC fields. `DP_DSC_CNTL` and `DP_DSC_BYTES_PER_PIXEL` influence compressed stream transport. Incorrect field values can break high-bandwidth modes or produce sink-side decode failure.
- Audio fields. AFMT clocks, HDMI/DP audio packet controls, ACR programming, and audio `N/M` fields are sensitive to pixel clock and link configuration. Bad constants can produce missing audio, rate mismatch, or unstable audio after modeset/resume.
- GPIO/DDC/HPD side effects. DDC output enables, pull-downs, AUX pad modes, HPD masks, and receive fields are connector-facing. Incorrect writes can break EDID reads, AUX transactions, hotplug detection, or HPD RX handling.
- Status and clear semantics. Fields named `ACK`, `CLEAR`, `PENDING`, `STATUS`, `READBACK`, and `RESULT` should not be blindly read-modify-written without knowing whether they are sticky, self-clearing, or write-one-to-clear.
- Full-width and high-bit masks. Several fields use broad masks, including high bits such as HPD receive fields and packet-control bitmaps. Consumers should use unsigned 32-bit register helpers to avoid signedness or width surprises.

Reserved or generic fields such as `DC_GENERICA` should remain conservative unless backed by ASIC documentation or existing driver behavior. The generated header does not distinguish reserved, read-only, write-only, or firmware-owned fields.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Kernel/driver build coverage for DCN201 paths that include `dcn_2_0_1_sh_mask.h`, especially resource, clock-manager, IRQ, stream encoder, link encoder, audio, DIO, I2C, AUX, and HPD code.
- Generated-header checks that every field has matching `__SHIFT` and `_MASK` definitions, masks align to shifts, and repeated instance families are consistent across `DIG0`/`DIG1` and `DP0`/`DP1`.
- Diff validation against AMD's authoritative DCN 2.0.1 register database and the companion `dcn_2_0_1_offset.h`.
- HDMI/TMDS modeset tests that exercise lane enable, TMDS control-character generation, HDMI infoframes/generic packets, metadata packets, AFMT audio clocking, ACR/N/CTS, audio packet controls, and output CRC/test paths.
- DisplayPort/eDP tests for link training, video stream enable/disable, pixel encoding/depth/combine, MSA timing, VBID, `M/N`, scrambler, PRBS, training patterns, HBR2/TPS patterns, and link/status readback.
- MST tests that verify MSE rate programming, SAT0/SAT1/SAT2 allocation, update sequencing, link timing, and SAT status readback across multiple streams.
- DSC tests for compressed DP modes, including slice width, bytes-per-pixel programming, and interaction with metadata/secondary packets.
- HDR/metadata and infoframe tests that confirm DP secondary metadata and HDMI metadata/generic packets are sent on the expected lines and remain stable across modeset, fast update, and resume.
- Audio tests for HDMI and DP that verify AFMT clock state, packet generation, ACR status, and DP audio `N/M` programming/readback.
- AUX/DDC/HPD tests that cover EDID reads on DDC1/DDC2, AUX pad mode/polarity, hotplug mask/receive behavior, HPD IRQ acknowledgement, HPD RX interrupt paths, and suspend/resume reconnect behavior.
- Stress tests around hotplug, link retraining, runtime power management, suspend/resume, MST topology changes, DSC enable/disable, and repeated modesets, watching for blank displays, flicker, missing audio, bad EDID reads, incorrect HPD events, and stuck pending/status bits.

## Cross-Chunk Notes

This source slice is artificially bounded. Earlier chunks contain the beginning of `DIG0_TMDS_CTL2_3_GEN_CNTL` and preceding `DIG0` HDMI/TMDS fields. Later chunks complete `DC_GPIO_HPD_MASK` and continue with HPD output/enable/readback fields and the rest of the DCN 2.0.1 register-mask header. The final per-file report should merge this chunk with neighboring chunks before summarizing complete DIG0, HPD, GPIO, and DCIO behavior.

### subset-b-001649: lines 20000-22091

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 20000-22091

## Scope

This chunk is the final slice of AMDGPU's generated DCN 2.0.1 register shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used by register helper code to insert or extract fields from DCN 2.0.1 MMIO and indexed Azalia/HDA display-audio registers.

The range has 2,092 source lines, including 921 shift macros, 929 mask macros, and 232 register or address-block comments. It starts at the tail of `DC_GPIO_HPD_MASK`, covers DC GPIO HPD/AUX pad controls, then describes Azalia function-0 output endpoint blocks 0 and 1, a partial endpoint2 audio-descriptor mirror, input endpoint blocks 0 and 1, and ends with the file's closing `#endif`.

## Purpose

The chunk provides exact bit positions and already-positioned masks for DCN 2.0.1 display connector GPIO and display-audio hardware fields. Higher-level AMD display code can name logical fields while this generated header supplies ASIC-specific layout details.

Major hardware areas covered here are:

- `DC_GPIO_HPD_MASK`, `DC_GPIO_HPD_A`, `DC_GPIO_HPD_EN`, and `DC_GPIO_HPD_Y`: hot-plug detect mask, pad disable, receive mode, active value, enable, Schmitt/slew, selection, and output/readback fields for HPD pins.
- `DC_GPIO_PAD_STRENGTH_1`, `PHY_AUX_CNTL`, and `DC_GPIO_AUX_CTRL_1` through `_5`: connector pad drive strength, AUX/DDC pad wake/enable/pulldown, comparator/bias/resistor selection, spike rejection, slew, DP/DN swap, termination, hysteresis, AUX control, and voltage-output tuning fields.
- `AUXI2C_PAD_ALL_PWR_OK`: global AUX/I2C pad power-good and bypass controls.
- `AZF0ENDPOINT0_*` and `AZF0ENDPOINT1_*`: repeated HDMI/DisplayPort output audio codec endpoint metadata, converter controls, pin controls, sink/ELD-derived information, multichannel routing, HBR, channel-status overrides, LPIB snapshots, format-change tracking, keepalive, and audio enable/disable/format-change interrupt status.
- `AZF0ENDPOINT2_*`: only the channel-speaker and audio-descriptor portions appear in this chunk, apparently as an input-endpoint-adjacent generated alias or continuation.
- `AZF0INPUTENDPOINT0_*` and `AZF0INPUTENDPOINT1_*`: input converter and input pin controls, including input format/stream routing, digital converter state, input pin capabilities, unsolicited response, input pin sense, multichannel enable/mute/channel IDs, HBR, channel allocation, hot-plug audio enable, forced unsolicited response, configuration default, LPIB snapshots, input activity/status interrupts, and input infoframe fields.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The API contract is macro naming and the pairing of every field shift with its mask:

- `*_SHIFT` constants hold the low bit position of a field.
- `*_MASK` constants hold the field mask already shifted into register position.
- Register-heading comments such as `//AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` group the field macros by generated hardware register.
- Address-block comments such as `// addressBlock: azf0endpoint0_endpointind` and `// addressBlock: azf0inputendpoint1_inputendpointind` mark indexed codec endpoint register windows.

The GPIO/PHY macros are consumed by GPIO, HPD, DDC/AUX, and link-detection paths. Representative fields include `DC_GPIO_HPD_A__DC_GPIO_HPD1_A_MASK`, `DC_GPIO_HPD_EN__DC_GPIO_HPD1_EN_MASK`, `DC_GPIO_PAD_STRENGTH_1__RX_HPD_STRENGTH_SN_MASK`, `PHY_AUX_CNTL__AUX_PAD_WAKE_MASK`, `DC_GPIO_AUX_CTRL_1__DC_GPIO_AUX1_COMPSEL_MASK`, `DC_GPIO_AUX_CTRL_2__DC_GPIO_HPD12_SPIKERCEN_MASK`, `DC_GPIO_AUX_CTRL_3__AUX1_DP_DN_SWAP_MASK`, and `AUXI2C_PAD_ALL_PWR_OK__AUXI2C_PAD_ALL_PWR_OK_MASK`.

The output endpoint macros repeat a dense HDA codec endpoint model. Important groups include:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` for converter widget capability flags, delay, and type.
- `...CONVERTER_CONTROL_CONVERTER_FORMAT` for channel count, bits per sample, sample divisor/multiple/base rate, and stream type.
- `...CONVERTER_CONTROL_CHANNEL_STREAM_ID` for channel and stream IDs.
- `...CONVERTER_CONTROL_DIGITAL_CONVERTER` for digital enable, validity, pre-emphasis, copyright, non-audio, professional, category code, generation level, and keepalive fields.
- `...PARAMETER_STREAM_FORMATS`, `...PARAMETER_SUPPORTED_SIZE_RATES`, `...STRIPE_CONTROL`, `...RAMP_RATE`, `...GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*` for capability advertisement and stream synchronization.
- `...CODEC_PIN_PARAMETER_*` and `...CODEC_PIN_CONTROL_*` for pin capabilities, unsolicited response tags, pin sense, output enable, channel/speaker mapping, audio descriptors 0-13, multichannel routing, lipsync, HBR, sink info, hot-plug audio enable, forced unsolicited responses, configuration default, LPIB, coding type, format changed, wireless display identification, and remote keepalive.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` for IEC 60958 channel-status override fields.
- `...AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS` for output endpoint state and interrupt metadata.

The input endpoint macros mirror much of the converter/pin model but use `CODEC_INPUT_CONVERTER_*` and `CODEC_INPUT_PIN_*` names. Input-specific groups include `...INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` for input activity, channel layout, and unsolicited-response enables, plus `...INPUT_PIN_CONTROL_INFOFRAME` for channel count, channel allocation, infoframe byte 5, and valid state.

## Control Flow

This header has no local control flow. Runtime behavior occurs in consumers that include `dcn_2_0_1_offset.h` and this shift/mask header, then build register tables or issue MMIO/indexed-register accesses through helper macros.

A typical use pattern is:

1. DCN 2.0.1 resource, IRQ, clock, GPIO, DDC/AUX, or audio code includes the generated offset and shift/mask headers.
2. Register tables are assembled with macro expansion helpers such as `SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, and generation-specific mask-list macros.
3. Driver code calls helper operations such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or indexed Azalia endpoint accessors.
4. The helpers use these masks and shifts to read, update, acknowledge, or decode hardware fields.

Control-sensitive flows represented by this chunk include HPD interrupt/presence handling, AUX/DDC pad bring-up, connector detection, HDMI/DP audio endpoint setup, stream-to-endpoint binding, audio format/rate/channel programming, sink descriptor propagation, hot-plug audio enablement, HBR enablement, channel-status override programming, LPIB position snapshots, and audio enable/disable/format-change interrupt reporting.

The macros do not encode ordering, volatility, access permissions, or write-one-to-clear behavior. Callers must still know when a field is read-only status, sticky status, self-clearing, safe only during link/audio disable, or shared with firmware/hardware state machines.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register state that persists according to DCN/Azalia register semantics until changed by software, hardware, reset, or power management.

State represented in this range includes:

- HPD and GPIO state: pin masks, active values, enable bits, pull/power-disable controls, receiver selection, Schmitt/slew configuration, and pad output/readback values.
- AUX/DDC electrical state: pad wake, RX selection, pad mode, data/clock enable and power-disable bits, bias/resistor/comparator controls, spike rejection, termination, DP/DN swap, hysteresis, control nibbles, and voltage-output tuning.
- Audio converter state: stream format, channel count, sample size/rate encoding, channel/stream ID binding, digital converter status bits, keepalive controls, stripe/ramp/GTC embedding, and GTC delta/min/max readbacks.
- Output pin state: pin capabilities, pin sense, output enable, channel/speaker allocation, descriptor payloads, multichannel enable/mute/channel IDs, lipsync/HBR, sink info, hot-plug audio enable, forced unsolicited response payloads, default configuration, channel-status overrides, LPIB snapshots, coding type, format-change response, wireless display identity, remote keepalive, and audio interrupt state.
- Input endpoint state: input converter and pin capability/control values, input pin sense, multichannel routing, HBR, channel allocation, hot-plug audio enable, configuration default, LPIB snapshots, input activity/channel-layout status, unsolicited-response enables, and input infoframe state.

Some fields are configuration latches, some are live status readbacks, some are capability values exposed to the HDA codec model, and some are interrupt status/ack/mask/type fields. Incorrect software use can persist until a modeset, audio reconfiguration, connector hotplug, suspend/resume cycle, power reset, or full GPU reset reprograms the block.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h`, which provides matching register addresses and indexed-register offsets. This chunk provides the bit layout within those registers. The constants also depend on AMD display helper conventions that paste register and field names into `_MASK` and `__SHIFT` identifiers.

Direct include sites visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c`, which includes the DCN 2.0.1 offset and mask headers while building Cyan Skillfish/DCN201 resources, including display audio, link, GPIO, DDC/AUX, and IRQ objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`, which includes this header and expands generated masks into interrupt register entries for HPD, HPDRX, vblank, vline, vupdate, and page-flip sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`, which includes the header for DCN201 clock-manager register/field tables.

Shared GPIO translation code also relies on the HPD mask constants from this generated namespace. For example, `display/dc/gpio/dce80/hw_translate_dce80.c`, `display/dc/gpio/dce120/hw_translate_dce120.c`, and later DCN GPIO translators map `DC_GPIO_HPD_A__DC_GPIO_HPDn_A_MASK` values to software GPIO IDs.

Display audio integration flows through common DCE/DCN audio code and generation-specific resource tables that expose Azalia endpoint index/data windows to HDMI/DP audio setup. The endpoint and input-endpoint fields in this chunk are tightly coupled to matching `AZF0ENDPOINT*` and `AZF0INPUTENDPOINT*` offsets in the generated offset header.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or persistence-layer behavior.

## Risks And Edge Cases

The dominant risk is silent hardware misprogramming. A wrong shift or mask can compile cleanly but cause register helpers to alter the wrong bit, truncate a value, miss a sticky status bit, or acknowledge the wrong interrupt.

GPIO and AUX/HPD fields are connector-critical. Bad constants in `DC_GPIO_HPD_*`, `PHY_AUX_CNTL`, or `DC_GPIO_AUX_CTRL_*` can break hotplug detection, HPD IRQ delivery, DDC/AUX communication, DisplayPort link training, receiver selection, pad power state, or electrical tuning. Some failures may appear only on specific boards, connectors, cables, or suspend/resume paths.

Display audio fields are protocol-visible. Incorrect converter format, stream ID, digital converter, pin capability, audio descriptor, sink info, HBR, multichannel, channel allocation, or channel-status masks can produce missing HDMI/DP audio, wrong sample rate/channel advertisement, incorrect non-audio/professional/copyright metadata, broken HBR streams, or bad audio routing after hotplug.

Interrupt and status fields are especially sensitive. Audio enable/disable/format-change status groups and unsolicited-response controls mix status, mask, type, ack/clear, enable, and payload fields. A read/modify/write using the wrong mask can drop an interrupt, fail to clear a sticky bit, or report an event on the wrong endpoint.

The repeated endpoint layouts create copy/generation hazards. `AZF0ENDPOINT0` and `AZF0ENDPOINT1` should be structurally aligned, and `AZF0INPUTENDPOINT0` and `AZF0INPUTENDPOINT1` mostly mirror each other. Any one-off field-width or shift difference should be treated as suspicious unless the ASIC register database explicitly requires it.

Chunk boundaries matter. The range starts in the middle of `DC_GPIO_HPD_MASK`, so earlier shift definitions for that register live in the previous chunk. It also contains a duplicated `addressBlock: azf0inputendpoint0_inputendpointind` comment and a partial `AZF0ENDPOINT2_*` descriptor sequence amid input-endpoint material; the final merge lane should verify whether this is intentional generated aliasing or a source-generation irregularity before drawing whole-file conclusions.

## Test Signals

Useful validation signals are primarily generated-header checks plus DCN201 display, connector, and audio behavior:

- Build coverage for DCN201 resource, IRQ, clock manager, GPIO, DDC/AUX, and DCE/DCN audio code that includes `dcn_2_0_1_sh_mask.h`.
- Generated-register validation that every field has a matching address/register definition in `dcn_2_0_1_offset.h`, that masks match their shifts and widths, and that repeated endpoint/input-endpoint instances stay structurally consistent.
- Hotplug tests across HPD1/HPD2 and HPDRX paths, including plug/unplug storms, suspend/resume, runtime power transitions, and connector detection after display off/on.
- AUX/DDC validation through EDID reads, DisplayPort link training, HPD IRQ sideband handling, and failure-injection around pad power/wake paths.
- HDMI/DisplayPort audio tests for stream binding, PCM and non-PCM formats, sample-rate changes, multichannel layouts, HBR enablement, channel allocation, sink descriptor updates, and audio behavior across hotplug and modeset.
- Interrupt tests that confirm audio enabled, audio disabled, audio format changed, HPD, HPDRX, vblank, vline, vupdate, and page-flip interrupt masks/status/ack paths still report and clear expected events.
- LPIB and infoframe sanity checks that confirm snapshot locks, wrap counters, timer snapshots, input activity, channel layout, and infoframe-valid fields move plausibly during playback or capture-style input endpoint activity.

Regression symptoms from bad constants include missing hotplug events, failed EDID/AUX transactions, black screen after connector changes, no HDMI/DP audio, wrong audio channel layout or rate, stuck audio interrupts, format-change events not delivered, broken HBR audio, or endpoint-specific failures that only affect one generated instance.

## Cross-Chunk Notes

This is a generated constants-only chunk and the final chunk of `dcn_2_0_1_sh_mask.h`. The previous chunk owns the beginning of `DC_GPIO_HPD_MASK` and likely earlier DCIO/Azalia register families. The final per-file document should merge this slice with adjacent chunks to present the full DCN 2.0.1 register layout contract rather than treating this artificial line range as a standalone module.
