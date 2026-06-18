# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 2703-5277

## Scope

This chunk is a generated DCN 3.1.4 register-offset slice from `dcn_3_1_4_offset.h`. It contains preprocessor address constants only: `reg...` macros map symbolic AMD display-engine register names to MMIO register offsets, and adjacent `reg..._BASE_IDX` macros identify the register base aperture index. There are no C functions, structs, enums, branches, loops, or driver-owned storage objects in this range.

The requested range starts in the tail of `dce_dc_hda_azf0controller_dispdec`, beginning with the later AZALIA input/output CRC and memory-power registers. It then covers AZALIA function/root and stream endpoint offsets, DCHUBBUB memory/VM/arbitration offsets, HUBP/HUBPREQ/HUBPRET/cursor/perfmon register sets for pipe instances 0-3, DPP0 top/CNVC/DSCL/color-management/perfmon offsets, and the first two DPP1 top offsets.

## Purpose And Hardware Surface

The purpose of this header range is to provide the address ABI between AMDGPU Display Core code and DCN 3.1.4 hardware. Companion mask/shift headers describe bit fields inside these registers; this file gives the register numbers that display code uses with generated register helper tables and MMIO accessors.

Major hardware areas represented here:

- AZALIA display audio and codec registers. The slice includes the end of controller-level CRC and memory-power controls, root codec parameters, channel/resync/power/reset controls, audio port connectivity, GTC group offsets, stream index/data windows for streams 8-15, and input endpoint index/data windows for endpoints 0-7.
- DCHUBBUB SDPIF, return path, arbitration, debug, clock/power, and VM register surfaces. These offsets cover framebuffer/AGP/local-memory location, SDPIF and return-path memory power, detile buffers, compbuf/DET allocation, fabric and outstanding-request arbitration, watermark/change-urgency controls, urgent/readback/debug signals, and clock counter/readback registers.
- DCN VM request interface registers. The chunk defines VM context 0-15 controls and page table base/start/end address pairs, default fault address registers, and fault control/status/address registers.
- HUBP/HUBPREQ/HUBPRET/cursor surfaces for instances 0, 1, 2, and 3. Each instance has surface configuration, viewport and request-size registers, surface and metadata addresses, flip controls/status, in-use/readback addresses, TTU/QoS/prefetch/vblank/nominal/delivery timing registers, cursor image and DMDATA registers, memory-power controls/status, and read-line/interrupt/status registers.
- Per-HUBP DC perfmon blocks for instances 0-3, represented by `DC_PERFMON6` through `DC_PERFMON9`.
- DPP0 top, CNVC, cursor conversion, DSCL, and CM offsets. These include DPP control/reset/clock/readback, surface pixel format, alpha/expansion/denorm/dynamic-range/clamping controls, DSCL scaler filter/tap/ratio/init/blank/recout/LB/OBUF registers, and a large color-management surface with CSC matrices, gamut remap, gamma correction, blend gamma, shaper LUTs, 3D LUT, HDR multiplier, memory power, and debug windows.
- DPP0 DC perfmon, represented by `DC_PERFMON10`.
- The start of DPP1 top coverage, with `DPP_TOP1_DPP_CONTROL` and `DPP_TOP1_DPP_SOFT_RESET`.

## Important Definitions

The exported interface is the generated macro naming convention:

- `reg<NAME>` gives a DCN 3.1.4 register offset such as `regHUBPREQ0_DCSURF_PRIMARY_SURFACE_ADDRESS` or `regCM0_CM_3DLUT_DATA`.
- `reg<NAME>_BASE_IDX` gives the base-address table index for that register. In this chunk almost all display-decoder registers use base index `2`; the file-level AZALIA controller section before this range used other base indices, and the range starts after that block's first lines.
- `// addressBlock: ...` comments group following offsets by generated hardware block.
- `// base address: ...` comments record the logical instance base for repeated blocks such as HUBP1 at `0x370`, HUBP2 at `0x6e0`, HUBP3 at `0xa50`, HUBP perfmon blocks at `0x1a74`/`0x1de4`/`0x2154`/`0x24c4`, and DPP0 perfmon at `0x3890`.

Notable register families in this slice:

- AZALIA CRC and memory-power registers: `AZALIA_INPUT_CRC{0,1}_CONTROL*`, `AZALIA_INPUT_CRC*_RESULT`, `AZALIA_CRC{0,1}_CONTROL*`, `AZALIA_CRC*_RESULT`, `AZALIA_MEM_PWR_CTRL`, and `AZALIA_MEM_PWR_STATUS`.
- AZALIA function/root registers: codec vendor/device/revision parameters, channel count, resync FIFO, function group type, supported size/rate and stream format, power state, reset, subsystem ID response, converter synchronization, and audio port connectivity.
- AZALIA stream and endpoint windows: stream 8-15 expose paired `AZALIA_STREAM_INDEX`/`AZALIA_STREAM_DATA` offsets, and input endpoint 0-7 expose paired codec input endpoint index/data offsets.
- DCHUBBUB memory/VM/aperture registers: `DCN_VM_FB_LOCATION_BASE/TOP`, `DCN_VM_FB_OFFSET`, `DCN_VM_AGP_*`, local HBM address start/end/lock, SDPIF and return-path memory-power controls/status, `VM_CONTEXT*_PAGE_TABLE_*`, default address, fault control/status, and fault address registers.
- DCHUBBUB arbitration and timing registers: outstanding request, SAT level, compress/fragment/DET allocation, watermark programming, change-urgency controls, self-refresh and urgent controls, arbitration debug, DCFCLK counter/readback, and fabric/SDPIF/debug registers.
- HUBP surface registers: per-instance surface config/address/tiling, primary and secondary viewport registers, request-size registers, control/clock/VMPG/debug, and DCFCLK/DPPCLK measure-window controls.
- HUBPREQ request registers: surface pitch, VMID, primary/secondary surface addresses, meta-surface addresses, surface control and flip controls, flip interrupts, in-use/earliest-in-use readbacks, expansion mode, TTU/QoS/watermark controls, VM aperture and L1 TLB controls, destination/prefetch/vblank/flip/nominal/delivery timing registers, cursor settings, and memory-power controls/status.
- HUBPRET return registers: return-path control, memory power, read-line controls, read-line value/status, and interrupt offsets.
- Cursor and DMDATA registers: cursor control/address/size/position/hotspot/stereo/destination offset, cursor memory power, DMDATA address/control/QoS/status/software data controls.
- DPP/CNVC/DSCL registers: DPP control/soft reset/clock/readback, CNVC pixel format and alpha/expansion/denormal/clamp controls, CNVC cursor conversion controls, DSCL coefficient RAM, scaler mode/taps/ratios/init, output black/overscan/blanking/recout/MPC/LB/OBUF and DSCL memory-power controls.
- DPP0 CM registers: post-CSC and gamut-remap matrices, bias, gamcor/blend-gamma/shaper indexed LUT data and RAM A/B control/region tables, HDR multiplier, dealpha, coefficient format, CM memory power, 3D LUT mode/index/data/read-write/output normalization/offset, and CM debug index/data registers.
- Perfmon register sets: each `DC_PERFMON*` block exposes counter control, state, perfmon control, current-value interrupt/misc, current-value low, and high/low counter readback registers.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code selects one of these symbolic offsets and calls register helpers to read, write, update, poll, or dump the corresponding MMIO register. A typical use sequence is:

1. Functional display code selects a generated `reg...` offset for the active ASIC block and pipe instance.
2. Companion `_SHIFT`/`_MASK` definitions from the matching DCN 3.1.4 mask header pack or extract fields.
3. Register helper macros perform MMIO access against the base index identified by `reg..._BASE_IDX`.
4. Hardware stores, latches, consumes, or reports the register-backed state.

The state represented here is hardware state rather than normal C memory:

- Persistent configuration state includes audio codec power/reset/channel settings, stream/endpoint indirect indexes, VM aperture and page-table context programming, HUBP viewport/tile/format/request configuration, surface and metadata addresses, cursor images, prefetch/vblank/nominal/delivery timing, DPP scaler ratios/taps/modes, CNVC format/alpha/clamp controls, color matrices and LUT contents, and perfmon event controls.
- Volatile readback/status state includes CRC results, memory-power status, VM fault status and fault addresses, DCHUBBUB urgent/debug/readback counters, surface in-use and earliest-in-use addresses, read-line status, DMDATA status, perfmon counter state/current values, and DCFCLK/DPPCLK measurement windows.
- Side-effecting or sequencing-sensitive registers include reset controls, power-control registers, surface flip controls and interrupts, VM context/fault control, indirect index/data pairs, LUT index/data windows, perfmon control registers, and debug index/data windows.
- Repeated instance state is separated by macro prefixes and generated base comments. HUBP/HUBPREQ/HUBPRET/CURSOR instance 0 uses unoffset base `0x0`, instance 1 uses `0x370`, instance 2 uses `0x6e0`, and instance 3 uses `0xa50`; prefix mistakes can program a different pipe while still compiling.

The header does not encode ordering constraints. Correct callers still need to hold the appropriate display locks, sequence register programming around vblank/vupdate and flip completion, coordinate VM and surface-address updates with page-table validity, poll or acknowledge status bits where required, and respect power-gating and memory-power transition timing.

## Dependencies And Integration Points

This chunk integrates with:

- Companion generated DCN 3.1.4 mask/shift headers, especially `dcn_3_1_4_sh_mask.h`, which provide field positions and masks for the offsets named here.
- AMDGPU Display Core register helper tables and macros that consume `reg...` and `reg..._BASE_IDX` constants for `REG_GET`, `REG_SET`, `REG_UPDATE`, block-specific register lists, and debug dumps.
- Display audio code that programs AZALIA codec parameters, stream windows, endpoint windows, CRC diagnostics, audio DTO/clocking from adjacent ranges, and memory-power state.
- DC hub/hubbub code that manages framebuffer/AGP/local-memory aperture setup, SDPIF and return-path behavior, compbuf/DET allocation, arbitration, watermarks, urgent state, fabric interactions, self-refresh behavior, and debug/performance readbacks.
- DCN VM code that programs VM contexts, page table base/start/end addresses, VMID behavior, default addresses, L1 TLB controls, and VM fault collection for display fetches.
- Plane programming and flip code that uses HUBP/HUBPREQ surface format, pitch, addresses, metadata addresses, tiling, viewport, VMID, flip-control, in-use, earliest-in-use, prefetch, vblank, nominal, delivery, and cursor-setting offsets.
- Cursor and DMDATA paths that program cursor image memory, position, hotspot, stereo behavior, DMDATA addresses, QoS, software control, and status.
- Return-path/read-line handling that uses HUBPRET read-line controls, read-line value/status, interrupts, and memory-power state.
- DPP setup code for pipe control/reset, color conversion, alpha handling, denormalization, clamping, scaling, line-buffer/OBUF controls, and memory power.
- Color-management code that writes post-CSC/gamut matrices, gamma/blend/shaper LUTs through index/data windows, shaper/3D LUT controls and data, HDR multiplier, dealpha, and coefficient-format registers.
- Performance monitoring and diagnostics code using the `DC_PERFMON6` through `DC_PERFMON10` register sets.

Because the file is generated, integration usually depends on exact macro names and numbers matching AMD's register specification and the rest of the generated register-pack for this ASIC generation. A missing macro normally causes a compile error where referenced; an incorrect numeric offset or wrong base index can compile cleanly and misprogram hardware.

## Risks And Maintenance Notes

- Numeric drift is the main risk. A wrong offset can silently target the wrong MMIO register, corrupting display audio, VM setup, surface fetch, flip sequencing, cursor fetch, DPP color/scaler state, or perfmon diagnostics.
- Base index drift is also dangerous. Nearly every macro in this chunk uses base index `2`, so an accidental copied base index can be hard to spot during review and may redirect accesses to the wrong register aperture.
- The chunk starts mid-block. Lines 2703-2733 are the tail of `dce_dc_hda_azf0controller_dispdec`, so reconciliation with the previous chunk is needed for a complete AZALIA controller view.
- The chunk ends mid-DPP1 top coverage after `DPP_TOP1_DPP_CONTROL` and `DPP_TOP1_DPP_SOFT_RESET`; later chunks are needed for the rest of DPP1.
- Repeated HUBP/HUBPREQ/HUBPRET/CURSOR instances are highly regular. Prefix or instance-number mistakes can still compile if the wrong instance macro exists, causing one pipe to receive another pipe's surface, cursor, power, or timing programming.
- Indirect index/data windows need careful sequencing. AZALIA stream/endpoint windows, CM LUT index/data windows, CM 3D LUT index/data windows, and test/debug index/data windows can produce wrong writes if index updates and data writes are interleaved across callers without serialization.
- Address registers are often split low/high and sometimes have luma/chroma or primary/secondary/meta variants. Callers must update all required halves and planes consistently, with correct alignment, tiling, VMID, and page-table state.
- Flip and in-use registers are timing-sensitive. Bad ordering around `DCSURF_FLIP_CONTROL`, flip interrupts, in-use readbacks, earliest-in-use readbacks, prefetch, vblank, nominal, and delivery parameters can cause visible corruption, underflow, stale frame display, or missed page-flip completion.
- VM and fault registers are global enough to affect multiple pipes. Incorrect context ranges, page-table base addresses, aperture bounds, fault controls, or default addresses can break display fetches across planes, not just the caller's immediate pipe.
- Memory-power controls/status exist in AZALIA, DCHUBBUB, HUBPREQ, HUBPRET, cursor, DSCL, OBUF, and CM blocks. Writes while a block is powered down or before status settles can be lost or can expose transient readback behavior.
- DPP color-management tables are large and stateful. Wrong CM LUT indices, RAM A/B region programming, shaper/3D LUT data format, or matrix coefficient offsets can produce subtle color regressions that are not caught by simple modeset tests.
- Perfmon registers are diagnostic but stateful. Counter control/state/value registers must be programmed and read in the expected order, or performance measurements may be stale, reset unexpectedly, or assigned to the wrong pipe/block.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display tests:

- Build AMDGPU with DCN 3.1.4 support and ensure all referenced `reg...` and `reg..._BASE_IDX` names resolve.
- Run generated-header consistency checks that every `reg...` macro has a matching `_BASE_IDX` macro, that offsets are monotonic within generated address blocks where expected, and that repeated instance blocks preserve the intended instance deltas.
- Compare this offset header against the matching DCN 3.1.4 register specification and companion mask/shift header to catch numeric offset drift, missing registers, base-index drift, and instance-prefix mistakes.
- Exercise AZALIA display audio modes, stream programming, endpoint access, power state transitions, and audio CRC diagnostics.
- Run basic and multi-plane modesets across HUBP/HUBPREQ instances 0-3, covering surface format, pitch, tiling, viewport, luma/chroma addresses, meta-surface addresses, VMID, and page-table-backed display fetches.
- Exercise page flips, cursor movement, cursor image updates, DMDATA paths, and plane enable/disable while checking flip interrupts, surface in-use/earliest-in-use readbacks, read-line status, and absence of underflow or stale frame presentation.
- Run VM fault-injection or negative tests where available, confirming `DCN_VM_FAULT_STATUS` and fault address registers report useful data and that valid VM context programming avoids display fetch faults.
- Stress watermark, prefetch, vblank, nominal, delivery, urgent, arbitration, compbuf/DET allocation, and self-refresh paths under high-resolution, multi-plane, rotation/compression, and memory-pressure cases.
- Validate DPP0 scaler and format paths with scaling up/down, chroma formats, alpha/realpha, dynamic range, denorm/clamp behavior, line-buffer/OBUF behavior, and DPP reset/clock controls.
- Validate DPP0 color management through post-CSC, gamut remap, gamma correction, blend gamma, shaper LUT, 3D LUT, HDR multiplier, dealpha, and coefficient-format paths using color test patterns or CRC/colorimetry checks.
- Use perfmon and debug tooling to read `DC_PERFMON6` through `DC_PERFMON10`, DCHUBBUB debug/readback counters, DCFCLK/DPPCLK measure windows, and CM debug index/data windows.
- Run suspend/resume, display hotplug, blank/unblank, audio suspend, and display power-gating tests to ensure memory-power control/status registers are sequenced correctly across AZALIA, hubbub, HUBPREQ/HUBPRET, cursor, DSCL/OBUF, and CM blocks.

## Chunk-Specific Summary

Lines 2703-5277 define a dense DCN 3.1.4 MMIO offset surface rather than executable code. The most important responsibilities in this slice are display audio codec/stream/endpoints, DCHUBBUB VM/arbitration/memory-power/debug registers, HUBP/HUBPREQ/HUBPRET/cursor pipe instances 0-3, DPP0 scaler/conversion/color-management/perfmon registers, and the beginning of DPP1 top control. Correctness depends on exact generated offsets and base indices, instance-correct macro use, serialized indirect index/data access, and hardware validation across audio, VM, plane fetch, flip, cursor, DPP color/scaler, power-management, and perfmon paths.
