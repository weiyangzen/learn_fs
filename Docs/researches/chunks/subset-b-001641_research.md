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
