# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001827`: lines 1-2702, `Docs/researches/chunks/subset-b-001827_research.md`
- `subset-b-001828`: lines 2703-5277, `Docs/researches/chunks/subset-b-001828_research.md`
- `subset-b-001829`: lines 5278-7852, `Docs/researches/chunks/subset-b-001829_research.md`
- `subset-b-001830`: lines 7853-10395, `Docs/researches/chunks/subset-b-001830_research.md`
- `subset-b-001831`: lines 10396-12981, `Docs/researches/chunks/subset-b-001831_research.md`
- `subset-b-001832`: lines 12982-15245, `Docs/researches/chunks/subset-b-001832_research.md`

## Chunk Research

### subset-b-001827: lines 1-2702

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 1-2702

## Scope

This chunk covers lines 1-2702 of the DCN 3.1.4 generated register offset header. The source is a C preprocessor interface only: it contains the MIT license, an include guard, address-block comments, `#define` constants, and no functions, structs, enums, inline helpers, or executable statements.

The slice contains 2336 `#define` lines. It starts at the beginning of the file and ends inside the direct `dce_dc_hda_azf0controller_dispdec` block after `regAZALIA_INPUT_CRC1_CONTROL1`; later AZ controller registers continue in following chunks. The constants fall into two broad naming styles:

- `reg*` macros define direct MMIO register offsets plus matching `reg*_BASE_IDX` segment selectors.
- `ix*` macros define indexed-register offsets used through an index/data access window, generally without a `BASE_IDX` companion.

## Purpose

The header provides the offset half of the generated DCN 3.1.4 register ABI used by AMDGPU display code. Callers combine these offsets with segment-base constants, register access helpers, and the companion `dcn_3_1_4_sh_mask.h` field definitions to read or program display, DMU/DMCUB, MMHUBBUB, VGA, and Azalia/HDA audio hardware.

This chunk maps these hardware areas:

- HDA/Azalia controller ring and command registers at the top of the file: CORB/RIRB pointers, control/status/size registers, immediate command/response windows, and DMA position base address.
- Legacy VGA indexed blocks: sequencer, CRT controller, graphics controller, and attribute controller indices.
- Azalia sink information, input/output CRC result indices, 16 compact stream-latency/FIFO indexed blocks, eight output endpoint indexed blocks, eight input endpoint indexed blocks, and endpoint audio descriptor indices.
- VGA direct MMHUBBUB/VGA aliases with `BASE_IDX` 1, including CRTC/ATTR/GRPH/SEQ/DAC/GEN registers, VGA control, and source selection.
- Direct HDA endpoint/input-endpoint immediate command windows.
- Display clock generator (`DCCG`) offsets for pixel/DP/DSC/DPP/DTB/audio DTOs, clock gates, resync controls, GTC, time-base divisors, pixel-rate controls, vsync latch/count registers, and soft reset.
- F2 codec verb/index spaces for Azalia root, output endpoints, and input endpoints.
- DCCG, DMU, and MMHUBBUB performance monitor instances.
- DMU power-gating, miscellaneous, DMCU, interrupt-host-controller, foreground-security, RBBMIF, and DMCUB offsets.
- MCIF writeback and MMHUBBUB memory/warmup/VGA interface offsets.
- Direct HDA stream index/data windows for streams 0-7, direct endpoint index/data windows for endpoints 0-7, AZ clock/perfmon registers, and the beginning of AZ controller direct control/CRC registers.

## Important Macro Families

The `reg*` macros appear in pairs. For example, a register name such as `regDMCUB_INBOX0_BASE_ADDRESS` supplies the register offset, while `regDMCUB_INBOX0_BASE_ADDRESS_BASE_IDX` supplies the segment index used by local register helpers to compute the actual MMIO address. DCN 3.1.4 consumers define base arrays such as `DCN_BASE__INST0_SEG1` and use helper patterns like `BASE(regNAME_BASE_IDX) + regNAME`.

The top-level HDA controller block uses direct offsets without the later DCN segment bases, with base index 0. It exposes the classic HDA command/response ring interface (`CORB_*`, `RIRB_*`), immediate command and response windows, and DMA position buffer base registers.

The VGA indexed blocks use `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` constants for legacy VGA index spaces. The later direct VGA block maps the index/data ports and related control registers as `reg*` offsets with `BASE_IDX` 1.

The Azalia indexed output endpoint blocks are repeated for `AZF0ENDPOINT0` through `AZF0ENDPOINT7`. Each has the same offset layout: converter capability/control registers, format and stream/channel ID, digital converter control, stream formats and supported rates, stripe/ramp/GTC controls, pin capabilities, unsolicited response, pin sense, widget control, channel/speaker allocation, audio descriptors 0-13, multichannel controls, lipsync/HBR response, sink info 0-8, hot-plug control, forced unsolicited response, default configuration, channel-status override registers, association info, digital output status, LPIB snapshots, coding type, format-change, wireless-display ID, remote keepalive, audio-enable status, and audio enable/disable/format-change interrupt status.

The Azalia indexed input endpoint blocks are repeated for `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`. They are smaller than output endpoints and cover input converter format/channel/digital controls, supported formats/rates, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel enables, HBR response, channel allocation, hot-plug control, configuration default, LPIB snapshots, input status control, and infoframe.

The indexed stream blocks `AZF0STREAM0` through `AZF0STREAM15` each expose FIFO size control, latency counter control, worst-case latency count, cumulative latency count, and cumulative request count. The direct stream blocks later in the chunk expose the actual index/data windows for streams 0-7 with base index 2.

The `DCCG` block is dense and timing-sensitive. It includes PHY PLL pixel-clock resync controls, DP DTO enable, DSC/DPP clock DTO parameters, DPREFCLK/REFCLK/SYMCLK clock-gating controls, GTC DTO/current registers, microsecond/millisecond dividers, display clock frequency-change controls, memory power request controls, pixel-rate controls for OTG0-OTG3, HDMI/DP stream clock controls, audio DTO source and phase/module registers, vsync latch and count controls, and soft reset.

The DMU/DMCU/DMCUB blocks describe firmware-facing register state. The older DMCU block includes control/status, firmware address/checksum, ERAM/IRAM access, event trigger, interrupt masks/status/selectors, scratch, and master/slave communication registers. The DMCUB block includes address-translation regions and code-window top/offset registers, interrupt enable/ack/status/type, fault-address registers, security/memory controls, inbox/outbox base/size/read/write pointers, timer triggers/current/window, scratch registers, control registers, GPINT data, wake interrupt enable, and processor ID.

The MMHUBBUB and MCIF writeback blocks provide display memory-interface offsets: writeback buffer manager controls/status, buffer pitch/status/address/high-address/resolution, arbitration, SCLK/DRAM speed-change handling, VMID and QoS controls, warmup base/region/control/status, latency watermarks, memory power/clock/reset controls, outstanding counters, VGA interface controls, and DMU interface error status.

## APIs, Types, and Functions

There are no callable APIs, type definitions, or control functions in this chunk. The exported interface is the preprocessor macro namespace. These names behave like an ABI between generated register data and DCN 3.1.4 display code.

Observed integration points include:

- `display/dmub/src/dmub_dcn314.c`, which includes `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h`, defines DCN base segments, and builds the DMUB register table with `REG_OFFSET_EXP(reg_name)`.
- `display/dc/resource/dcn314/dcn314_resource.c`, which includes this header while constructing DCN 3.1.4 resource objects for hubbub, DCCG, audio, AUX/I2C, encoders, timing, and related display blocks.
- `display/dc/irq/dcn314/irq_service_dcn314.c`, which includes the same generated offset/mask pair for interrupt-service register programming and maps DCN interrupt source IDs to DAL interrupt sources.

The companion `dcn_3_1_4_sh_mask.h` supplies field shifts and masks. This offset header supplies addresses only; a caller needs both headers to perform field-level register programming safely.

## Control Flow

The header itself has no runtime control flow. Its constants imply the access flow used by display code:

1. Choose the correct register family and instance, such as `AZF0ENDPOINT3`, `AZF0STREAM7`, `DC_PERFMON2`, or a DMCUB inbox/outbox register.
2. For direct registers, compute the MMIO address from the selected base segment and `reg*` offset, using the matching `reg*_BASE_IDX`.
3. For indexed registers, write the `ix*` offset to the relevant index register, then read or write through the paired data register.
4. Combine the offset with field masks/shifts from `dcn_3_1_4_sh_mask.h` for read/modify/write, status polling, interrupt acknowledgement, clock control, firmware mailbox, or audio configuration flows.
5. Preserve ordering where hardware requires it: clock/DTO programming before dependent stream use, firmware memory/mailbox setup before DMCUB/DMCU handoff, ring pointers before enabling HDA DMA, and endpoint/stream format setup before audio enable.

The most sequencing-sensitive consumers are DCCG clock programming, DMU/DMCUB firmware and mailbox communication, interrupt status/destination routing, MCIF writeback buffer programming, and Azalia stream/endpoint/controller setup.

## State and Persistence

The file stores no mutable software state. The constants describe hardware state that persists in registers until reset, power transitions, firmware activity, or driver writes change it.

State domains visible in this chunk include:

- HDA CORB/RIRB and immediate-command state, DMA position base, audio DTO, stream index/data windows, endpoint index/data windows, controller clock gating, data/BDL/CORB DMA controls, underflow filler samples, output arbiter control, and input CRC controls/results.
- Output and input endpoint codec state: converter formats, stream IDs, digital converter flags, supported formats/rates, pin sense and hot-plug state, sink info, audio descriptors, multichannel controls, LPIB snapshots, coding/format-change state, remote keepalive, and audio enable/disable/format-change interrupt state.
- DCCG timing and clock state: DTO phase/modulo values, DP/HDMI/DSC/DPP/DTB/SYMCLK clock enables, time-base divisors, GTC current value, vsync latch/count registers, clock gates, and soft reset.
- DMU/DMCU/DMCUB state: power-gating configuration/status, firmware memory ranges and checksums, scratch/communication registers, interrupt masks/status/selectors, mailbox pointers, fault addresses, timers, security/memory controls, and wake/GPINT state.
- MMHUBBUB/MCIF state: writeback buffer addresses and status, watermark/QoS controls, VMID controls, warmup address and region controls, outstanding counters, VGA interface state, memory power and clock controls, and error status.
- VGA index/data and control state for legacy modes or compatibility paths.

Because these are hardware offsets rather than cached software values, persistence behavior is controlled by the ASIC and by driver sequencing. Firmware may also update some DMCUB/DMCU mailboxes, scratch registers, interrupt status, and timer/fault registers asynchronously.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is meaningful only in the AMDGPU DCN 3.1.4 register stack. The primary dependencies are:

- Companion generated field header `dcn_3_1_4_sh_mask.h`.
- DCN base segment definitions, such as the `DCN_BASE__INST0_SEG*` constants used by DCN 3.1.4 DMUB/resource/IRQ code.
- Register helper macros that turn `reg*` and `reg*_BASE_IDX` into final MMIO addresses and apply field masks/shifts.
- Indexed-register helper paths for the `ix*` spaces, especially Azalia endpoint/stream and VGA blocks.
- Firmware-facing DMUB/DMCUB code that expects DMCUB inbox/outbox, GPINT, scratch, fault, timer, and control register offsets to match the firmware contract.
- Display resource, audio, clock, writeback, interrupt, and memory-interface code that uses the generated macro names in instance lists and register tables.

The nearby DCN ASIC families contain many matching names with the same offsets, which is useful for generation consistency but also means a local change must be validated against DCN 3.1.4 specifically rather than copied from another ASIC generation by assumption.

## Risks

The main risk is silent hardware misprogramming. These macros are compile-time constants, so an incorrect offset or base index usually still builds but may read or write the wrong hardware register. The visible failures would likely appear as display clock instability, missing interrupts, DMUB/DMCUB firmware communication failures, writeback corruption, VGA fallback issues, or HDMI/DP audio breakage.

The `BASE_IDX` values are as important as the offsets. In this chunk, direct registers use multiple base indices: early HDA controller offsets use base index 0, many VGA/DCCG registers use base index 1, and DMU/DMCUB/MMHUBBUB/AZ direct display registers use base index 2. A correct offset with the wrong segment can target an unrelated register window.

The indexed `ix*` constants are not directly interchangeable with `reg*` offsets. Treating an indexed codec, stream, sink-info, descriptor, or VGA offset as a direct MMIO address would bypass the required index/data access path.

Repeated endpoint and stream layouts are vulnerable to generation drift. A one-line mismatch among `AZF0ENDPOINT0`-`7`, `AZF0INPUTENDPOINT0`-`7`, `AZF0STREAM0`-`15`, direct stream index/data windows, or direct endpoint index/data windows could affect only one connector or stream and be hard to spot in broad testing.

DMCUB offsets are firmware-contract sensitive. Inbox/outbox pointer, scratch, interrupt, security, fault, and GPINT offsets must match both host driver assumptions and the firmware running on the display microcontroller.

The chunk boundary is in the middle of `dce_dc_hda_azf0controller_dispdec`. Any final per-file analysis should merge the following chunk before treating the AZ controller direct register map as complete.

## Test Signals

Useful validation for this chunk is mostly build, generated-data, and hardware smoke coverage:

- Build coverage for DCN 3.1.4 files that include this header, especially `dmub_dcn314.c`, `dcn314_resource.c`, and `irq_service_dcn314.c`.
- Static checks that every direct `reg*` macro has the expected `reg*_BASE_IDX`, no duplicate macro names collide, and repeated endpoint/stream/perfmon layouts match where the hardware design expects them to match.
- Regeneration or diff checks against AMD's authoritative DCN 3.1.4 register database, with special attention to base indices and indexed-vs-direct register spaces.
- DMUB/DMCUB bring-up tests that validate firmware load/control, inbox/outbox traffic, GPINT handling, scratch registers, interrupts, timer reads, and fault reporting.
- Display clock tests covering DCCG DTO programming, DP/HDMI/DSC/DPP/DTB clock paths, pixel-rate controls, clock gating, GTC/current time-base reads, vsync latch/count programming, and soft reset behavior.
- IRQ tests that exercise display interrupt status continuation registers and interrupt destination programming for OTG, HPD, AUX, DIO/DCIO, DCCG, DMU, MMHUBBUB, writeback, DCHUB, MPC/OPP/OPTC, DSC, HPO, and AZ routes.
- HDMI/DP audio tests covering HDA ring setup, immediate command paths, stream index/data windows, endpoint index/data windows, codec verb offsets, hot-plug/audio-enable state, sink info, audio descriptors, multichannel/HBR/lipsync, LPIB snapshots, and input/output CRC paths.
- MCIF writeback and MMHUBBUB tests covering buffer address/high-address programming, buffer status, watermarks, VMID/QoS, warmup controls, memory power/clock/reset, and outstanding-counter readback.
- Legacy VGA or compatibility smoke tests for VGA index/data ports, VGA control, and source-select/split-control paths.

## Cross-Chunk Notes

This is the opening chunk of a 15245-line generated offset header. It establishes the include guard and many common low-address DCN 3.1.4 register maps, but it is not the complete file. The next chunk is required to complete the `dce_dc_hda_azf0controller_dispdec` block that starts at line 2662.

### subset-b-001828: lines 2703-5277

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

### subset-b-001829: lines 5278-7852

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 5278-7852

## Purpose

This chunk is generated AMD DCN 3.1.4 display-controller register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display hardware register names to numeric MMIO offsets plus companion base-index selectors. Runtime code combines `reg...` offsets with matching `reg..._BASE_IDX` values through register-table helper macros before issuing actual `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, or polling operations.

The range covers the end of DPP pipe 1, complete DPP pipe 2 and DPP pipe 3 display processing blocks, the first four OPP output-pixel-processing blocks, OPP top/DSCRM/perfmon metadata, the first four ODM input blocks, and the beginning of OTG0 timing-generator metadata. Although the repository path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this slice. The public interface is the generated macro namespace:

- `reg<block>_<register>`: a DCN 3.1.4 MMIO register offset.
- `reg<block>_<register>_BASE_IDX`: the DCN base-address segment selector for that register.

The requested range contains 2,383 `#define reg...` lines: 1,192 register-offset macros and 1,191 `_BASE_IDX` macros. All `_BASE_IDX` values present in the range are `2`. The apparent one-macro mismatch is a chunk-boundary artifact: line 7852 contains `regOTG0_OTG_FLOW_CONTROL`, while `regOTG0_OTG_FLOW_CONTROL_BASE_IDX` is on the next source line outside this work item.

Major macro families in this chunk:

- DPP1 tail: `regDPP_TOP1_DPP_CRC_*`, `regDPP_TOP1_DPP_CRC_CTRL`, and `regDPP_TOP1_HOST_READ_CONTROL`.
- `CNVC_CFG1`/`2`/`3`: surface pixel format, format control, floating-point bias/scale, color keyer, alpha LUT, pre-dealpha/realpha, pre-CSC matrices, coefficient format, and pre-degamma offsets.
- `CNVC_CUR1`/`2`/`3`: cursor control, cursor colors, and cursor floating-point scale/bias offsets.
- `DSCL1`/`2`/`3`: scaler coefficient RAM, mode/tap controls, horizontal/vertical ratios and inits, black color, update/autocal, overscan, OTG blanking, recout/MPC sizes, line-buffer format and memory controls, OBUF controls, and DSCL memory power/status.
- `CM1`/`2`/`3`: color-management control, post-CSC, gamut remap, output CSC, output color-space conversion, degamma/regamma/LUT setup, 3D LUT controls, bias/scale, HDR multiplier, dynamic-expansion, debug, and test/debug-data registers.
- `DC_PERFMON11`/`12`/`13`: DPP-local perf counter control, state, current value, high/low counters, and perfmon control registers.
- `DPP_TOP2`/`3`: DPP control, CRC control/value, and host-read control for DPP pipes 2 and 3.
- `FMT0` through `FMT3`: clamp components, dynamic expansion, bit-depth and 420/422 formatting, dithering/randomization, memory control, and format control offsets.
- `DPG0` through `DPG3`: display pattern generator control, ramp, dimensions, RGB/YUV color components, offset segment, and status.
- `OPPBUF0` through `OPPBUF3`, `OPP_PIPE0` through `OPP_PIPE3`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: output buffer controls, 3D parameters, pipe control, CRC mask/control/results.
- `OPP_TOP`, `DSCRM0` through `DSCRM3`, and `DC_PERFMON14`: OPP clock/ABM control, DSC forward config per stream, and OPP-local perf counter metadata.
- `ODM0` through `ODM3`: OPTC input global control, data-source select, data format, bytes per pixel, width, input clock, memory config, and spare registers.
- OTG0 beginning: horizontal/vertical timing totals, blanking, sync, trigger, forced-count, interrupt-status, and flow-control offsets.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by DCN314 display code:

1. DCN314 resource, IRQ, and DMUB code include `dcn_3_1_4_offset.h` together with the matching `dcn_3_1_4_sh_mask.h`.
2. Register-list macros paste block names and instance IDs into symbols such as `regCNVC_CFG2_FORMAT_CONTROL`, `regDSCL3_DSCL_UPDATE`, `regFMT1_FMT_BIT_DEPTH_CONTROL`, `regOPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2`, or `regODM3_OPTC_DATA_SOURCE_SELECT`.
3. Helpers in `dcn314_resource.c`, such as `SR(...)`, `SRI(...)`, and `SRII(...)`, compute `BASE(reg..._BASE_IDX) + reg...` and populate per-block register tables.
4. Display manager code then uses those tables to program plane formatting, scaling, color transforms, output formatting, pattern generation, CRC capture, DSC forwarding, ODM routing, and timing-generator state.

The macros do not encode ordering constraints. Consumers must still sequence clocks, memory power, pipe lock/unlock, double-buffered updates, color/LUT programming, scaling coefficient loads, output formatting, CRC capture, ODM routing, timing changes, interrupt handling, and suspend/resume restoration correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It names MMIO-backed GPU state whose lifetime is hardware-defined. Represented state includes:

- DPP input and plane-processing state for pixel format conversion, color keying, cursor composition, scaler ratios/taps, line-buffer and OBUF memory, DPP CRCs, and host reads.
- DPP color state for post-CSC, gamut remap, output CSC, degamma/regamma, LUT setup, 3D LUT control, HDR multiplier, dynamic expansion, and debug/test capture.
- Perfmon counter state for DPP pipes 1 through 3 and the OPP block.
- OPP output state for format clamping/dithering, 4:2:0/4:2:2 conversion, pattern generation, output buffering, pipe control, pipe CRC, ABM, and DSC forwarding.
- ODM input state for OPTC source selection, width/data-format configuration, input clocks, bytes-per-pixel accounting, and memory configuration.
- The beginning of OTG0 timing state for totals, blanking, sync, triggers, status, forced count, and flow control.

Configuration registers generally retain values until modeset, pipe reallocation, power gating, suspend/resume, or ASIC reset. Status, interrupt, debug, CRC, perf-counter, memory-power, update, and trigger registers can be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This offset header does not describe those semantics; field masks in `dcn_3_1_4_sh_mask.h` and the consuming display code provide the operational meaning.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.4 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h` for field shifts and masks.
- DCN314 base definitions such as `DCN_BASE__INST0_SEG2`, used by `BASE(reg..._BASE_IDX)`.

Observed include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

The strongest integration point is `dcn314_resource.c`, which includes this header, defines `DCN_BASE__INST0_SEG2` as the segment base, and uses token-pasting helpers to expand inherited DCN register-list macros such as `DPP_REG_LIST_DCN30(id)`, `OPP_REG_LIST_DCN30(id)`, and `OPTC_COMMON_REG_LIST_DCN3_14(id)`. `dmub_dcn314.c` includes the same offset and mask headers and computes offsets for the DMUB service register table via `REG_OFFSET_EXP(reg_name)`.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These are untyped preprocessor constants, so a wrong offset or `_BASE_IDX` can compile cleanly while directing register accesses to the wrong MMIO location.
- Repeated pipe families are copy-sensitive. DPP1/DPP2/DPP3, FMT0-FMT3, DPG0-DPG3, OPPBUF0-OPPBUF3, OPP pipe CRC0-CRC3, DSCRM0-DSCRM3, and ODM0-ODM3 are similar but not interchangeable; a single instance typo may only appear with particular display counts or pipe allocations.
- The line range starts after the beginning of DPP1 and ends in the middle of OTG0. File-level conclusions about DPP1 and OTG0 require adjacent chunks.
- Color and scaler registers are format-sensitive. Wrong CNVC, DSCL, CM, LUT, or HDR multiplier offsets can produce incorrect colors, cursor composition bugs, scaling artifacts, invalid CSC/gamut remap, or failures limited to specific pixel formats.
- Memory-power, OBUF, line-buffer, and update registers are sequencing-sensitive. Access while a block is gated, reset, or not clocked may be ignored, hang polling paths, or leave stale double-buffered state.
- OPP/FMT/DPG/CRC registers affect visible output and diagnostics. Offset mistakes can cause blank output, invalid dithering/clamping, broken test patterns, CRC mismatches, or misleading debug/perfmon data.
- ODM and OTG registers interact with timing and multi-pipe composition. Wrong source, width, clock, memory, blanking, sync, trigger, or flow-control offsets can break high-resolution, split-pipe, or multi-display modes.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN314 enabled; missing or renamed macros should fail while constructing DPP, OPP, OPTC, IRQ, and DMUB register tables.
- Mechanically verify that each non-`_BASE_IDX` `reg...` macro in this range has one matching `_BASE_IDX` macro, allowing for the documented boundary case where `regOTG0_OTG_FLOW_CONTROL_BASE_IDX` is immediately after line 7852.
- Verify all in-range `_BASE_IDX` values remain `2`, matching the DCN314 `DCN_BASE__INST0_SEG2` address segment used by resource and DMUB code.
- Diff this generated range against AMD's authoritative DCN 3.1.4 register database and adjacent DCN 3.x headers where compatibility is expected.
- Exercise display modes that allocate DPP/OPP/ODM instances 1 through 3: multi-monitor modesets, pipe split/ODM paths, scaling, cursor composition, rotation/format changes, HDR and color-management paths, and suspend/resume.
- Validate visual and diagnostic output: DPP/OPP CRC capture, DPG patterns, color/gamma/LUT programming, scaler coefficient loading, dithering/clamping, 420/422 formatting, ABM paths, and perfmon counters.
- Watch kernel logs and display diagnostics for underflow, stuck update/power-status polling, CRC mismatches, color corruption, scaler artifacts, blank display after modeset, broken resume, or failures limited to high-bandwidth ODM/OTG configurations.

## Cross-Chunk Notes

The previous chunk owns the start of DPP1, including the beginning of `DPP_TOP1`. This chunk begins at the DPP1 CRC/host-read tail and then covers complete CNVC/DSCL/CM/perfmon blocks for DPP1. The next chunk continues OTG0 immediately after `regOTG0_OTG_FLOW_CONTROL`, including its matching `_BASE_IDX` and the rest of the OTG0 timing-generator register set. The final per-file research document should reconcile these boundaries before making complete claims about all DPP or OTG register coverage in `dcn_3_1_4_offset.h`.

### subset-b-001830: lines 7853-10395

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 7853-10395

## Scope

This chunk is a generated DCN 3.1.4 register-offset slice from `dcn_3_1_4_offset.h`. It contains preprocessor constants only: `reg...` macros for MMIO register offsets and matching `reg..._BASE_IDX` macros, almost all with base index `2`. There are no C functions, structs, enums, branches, loops, allocation paths, or driver-owned state objects in this range.

The range starts in the tail of the OTG0 timing-generator block at `regOTG0_OTG_FLOW_CONTROL_BASE_IDX`, covers complete OTG1, OTG2, and OTG3 offset blocks, then covers shared OPTC/GSL/ODM, display I/O scratch/control/perfmon, HPD0-HPD4, DP AUX0-AUX4, and four repeated DIG instances. For DIG0 through DIG3 it includes VPG packet offsets, AFMT audio/infoframe offsets, DME offsets, DIG/HDMI/TMDS encoder offsets, and DP link offsets. The chunk ends partway through the DP3 block at `regDP3_DP_DPHY_SYM1_BASE_IDX`; later DP3 offsets are outside this work item.

## Purpose And Hardware Surface

The purpose of this header range is to provide the address half of the AMDGPU Display Core register ABI for DCN 3.1.4 hardware. Driver code uses these constants with companion field-mask headers to access display MMIO registers through generated register tables and helper macros instead of embedding numeric addresses in functional code.

Major hardware areas represented here:

- OTG timing generators: the tail of OTG0 plus full OTG1-OTG3 register-offset maps. These cover horizontal/vertical timing, blanking and sync controls, triggers, counters, stereo/interlace state, snapshots, update locks, CRC windows and data, static-screen control, global sync, DRR, DTO, DSC start position, pipe update status, and spare registers.
- OPTC/GSL/ODM shared controls: global sync source selection, OPTC clock and spare controls, ODM memory power controls/status, and DC perfmon counter registers for display-timing instrumentation.
- DIO shared controls: I2C/DOUT control, DIO scratch registers, stream encoder selection, global DIO control/status, PHY clock selection, DIG soft reset, link enable/control registers, and DIO perfmon registers.
- HPD0-HPD4 hotplug-detect blocks: interrupt status/control and toggle filter control offsets for the five hotplug pins exposed in this slice.
- DP AUX0-AUX4 blocks: AUX transaction control, arbitration, reply/read/write data, interrupt/debug/status, low-time count, and PHY wake control offsets for five DisplayPort AUX channels.
- DIG0-DIG3 repeated display output blocks: VPG generic packet registers, AFMT audio/infoframe registers, DME control/memory-control registers, DIG frontend/backend/HDMI/TMDS registers, and DP link/stream/PHY/secondary-packet/MST/MSO/DSC/ALPM registers for DP0-DP2 plus the beginning of DP3.

## Important Definitions

The exported interface is the generated macro naming convention:

- `reg<INSTANCE>_<REGISTER>` gives the register offset used by AMD display register accessors.
- `reg<INSTANCE>_<REGISTER>_BASE_IDX` selects the register base aperture index used by the generated register table. In this chunk the value is consistently `2`.
- `// addressBlock: ...` comments identify the hardware block for the following offsets.
- `// base address: ...` comments show the block-local hardware base used by the generated offset namespace.

Important offset families in this chunk:

- `regOTG0_*`, `regOTG1_*`, `regOTG2_*`, and `regOTG3_*` identify timing-generator registers for scan timing, vblank/vsync, frame and HV counters, update locks, vertical interrupts, CRC capture, global sync, dynamic refresh rate, trigger/manual-flow controls, DTO, DSC start position, and status readbacks.
- `regGSL_*`, `regOPTC_*`, and `regODM_*` expose shared display timing controls: global sync source selection, OPTC clock control/spare state, and ODM memory power state.
- `regDC_PERFMON15_*` and `regDC_PERFMON16_*` cover counter control, config, high/low value, and counter status offsets for display perfmon blocks.
- `regDOUT_*`, `regDIO_*`, `regDIG_SOFT_RESET`, and `regDIO_LINK*` provide shared DIO register offsets for DOUT/I2C configuration, scratch state, DIO global control/status, PHY clock selection, DIG reset, and link routing/control.
- `regHPD0_*` through `regHPD4_*` map hotplug interrupt status/control and debounce/toggle filter registers.
- `regDP_AUX0_*` through `regDP_AUX4_*` map AUX channel control, request/reply payload, arbitration, interrupt, debug, status, timing, and PHY wake registers. These are separate from the DP main-link `regDP0_*` style offsets.
- `regVPG0_*` through `regVPG3_*` map video packet generator generic packet access/data/update/status and MPEG infoframe registers.
- `regAFMT0_*` through `regAFMT3_*` map audio formatter VBI/audio packet controls, infoframe payload registers, IEC 60958 channel-status words, audio CRC/ramp/result/status, interrupt status, audio source control, and AFMT memory power registers.
- `regDME0_*` through `regDME3_*` map DME control and memory-control registers for each DIG instance.
- `regDIG0_*` through `regDIG3_*` map DIG frontend/backend enable and mode controls, output CRC, clock/test/random patterns, FIFO controls, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, HDMI general control, AFMT connection, TMDS pattern/DC-balancer controls, DIG version, and force-disable.
- `regDP0_*`, `regDP1_*`, and `regDP2_*` map complete DP main-link blocks in this slice: link control, pixel format, MSA colorimetry/misc/timing, stream control, DPHY/training/symbol/scrambler/FEC/CRC/PRBS controls, secondary-packet controls, audio M/N/timestamp, MST/MSE allocation, DSC/MSO metadata, generic stream packets, ALPM, and AUX-less ALPM controls.
- `regDP3_*` begins the next DP main-link block, from `DP_LINK_CNTL` through `DP_DPHY_SYM1`; the rest of DP3 is intentionally outside this chunk.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core code combines these offset macros with generated shift/mask constants and register helper APIs. A typical call path is:

1. Select a DCN 3.1.4 register offset such as an OTG timing register, HPD interrupt register, AUX request register, DIG HDMI packet register, or DP link register.
2. Pair the offset with field shifts and masks from the companion `dcn_3_1_4_sh_mask.h` generated header.
3. Use display register helpers such as generated `REG_GET`, `REG_SET`, `REG_UPDATE`, or equivalent accessors to issue MMIO reads, writes, or read/modify/write operations.
4. Hardware stores, consumes, latches, clears, or reports the register-backed state according to the block semantics.

The state represented by this chunk is hardware state, not normal kernel memory:

- Persistent configuration state includes OTG timing totals, blanking/sync placement, interlace/stereo/static-screen controls, global-sync selection, DIO link routing, DIG mode/source/backend enable, HDMI packet/audio/ACR/TMDS settings, DP pixel format, MSA/VBID/timing, link framing, DPHY training/scrambler/FEC settings, MST/MSE allocation, DSC/MSO metadata, VPG packet contents, and AFMT audio/infoframe contents.
- Volatile status/readback state includes OTG positions and counters, frame/VF/HV counts, interlace/stereo/snapshot/global-sync status, pipe update status, CRC data, HPD interrupt/toggle status, AUX replies/status/debug, DIO status, DIG FIFO and output CRC status, HDMI packet/readback status, DP stream/link/FEC/CRC/MST/MSE status, and ALPM pending/status registers.
- Side-effecting write paths are implied by many offsets even though the side effects are not described in this offset header. Examples include OTG count resets, manual triggers, update locks, vertical interrupt controls, CRC controls, HPD interrupt controls, AUX transaction control/arbitration, DIG soft reset, stream/backend enables, HDMI packet send controls, DP training pattern controls, secondary-packet send controls, MSE/SAT update triggers, and ALPM controls.
- Several register families are timing-sensitive. OTG update locks and double-buffer controls, DP secondary-packet scheduling, DP stream enable/defer, MST slot updates, DSC/PPS-related packet controls, HDMI infoframe updates, and ALPM state transitions need sequencing against vblank, vupdate, link training, stream disable, or power-management flows.

The offsets do not encode safety rules. Correct callers still need the appropriate display locks, pipe/update-lock sequencing, hardware status polling, ACK/clear semantics, and instance selection before touching live display registers.

## Dependencies And Integration Points

This generated header integrates with:

- Companion DCN 3.1.4 generated mask/shift headers that define the bit layout for each offset named here.
- AMDGPU Display Core register tables that aggregate `reg...` offset macros into per-IP block structures for timing generators, link encoders, AUX, HPD, audio formatter, video packet generator, and diagnostics code.
- Display modeset and timing code that programs OTG totals, syncs, blanking, update windows, DRR parameters, CRC capture, vertical interrupts, global sync, and pipe update status.
- Link encoder and connector code that uses DIO shared controls, DIG soft reset, link routing, HPD status/interrupts, and AUX transactions for DisplayPort and HDMI connector bring-up.
- DisplayPort main-link code that programs DP0-DP2 link control, lane and pixel-format state, MSA/VBID, video M/N, DPHY training/scrambler/FEC/CRC/test patterns, secondary packets, DSC/MSO metadata, MST/MSE scheduling, and ALPM.
- HDMI and TMDS code that programs DIG frontend/backend selection, HDMI enable/status, audio and ACR packets, VBI/infoframes/generic packets, deep-color/general-control state, TMDS patterns, and DIG force-disable/version checks.
- Audio paths that use AFMT packet controls, infoframe words, IEC 60958 words, audio CRC/ramp/status, audio source selection, and AFMT memory power offsets.
- Diagnostics and validation paths using OTG CRC, DIG output CRC, DP DPHY CRC, perfmon counters, FIFO status, AUX debug/status, HPD status, and TMDS/test-pattern registers.
- Power-management paths using ODM memory power, AFMT memory power, DME memory control, DP AUX PHY wake, DP ALPM/AUX-less ALPM, and PHY clock/link controls.

Because these are preprocessor constants, a missing macro reference is caught at compile time, but a wrong numeric offset or wrong instance prefix can compile and misprogram hardware at runtime.

## Risks And Maintenance Notes

- Numeric offset drift is the primary risk. If an offset no longer matches the DCN 3.1.4 register specification, the driver can write the wrong MMIO register while the C code still compiles.
- The slice is heavily repetitive across OTG1-OTG3, HPD0-HPD4, AUX0-AUX4, and DIG/DP0-DP3 instances. Prefix mistakes can target the wrong timing generator, connector, AUX channel, encoder, or link.
- The work item starts and ends mid-block. OTG0 is missing its earlier timing offsets, and DP3 is only present through `DP_DPHY_SYM1`; adjacent chunk research is required for a complete per-file view.
- Base-index consistency matters. Most macros in this range pair an offset with `_BASE_IDX 2`; changing either side independently can redirect register-helper access into the wrong MMIO base.
- Side-effecting registers are vulnerable to generic read/modify/write misuse. Reset, trigger, ACK, clear, send, lock, and update bits should be handled with block-specific semantics rather than treated like persistent booleans.
- Timing-sensitive OTG and packet registers can cause visible glitches if programmed while active without update locks, double-buffering, or vblank/vupdate sequencing.
- AUX and HPD offsets sit on hotplug/link-management paths. Incorrect status, interrupt, or arbitration register access can break connector detection, DPCD/EDID reads, link training, or wake behavior.
- DP MST/MSE, DSC, MSO, secondary-packet, and ALPM offsets interact with live link bandwidth and packet scheduling. Bad instance selection or stale offsets can cause missed metadata, failed compressed streams, stream starvation, or link idle/resume failures.
- HDMI audio/infoframe/ACR/TMDS offsets are user-visible despite being low-level constants. Wrong values can produce a lit display with bad audio, invalid metadata, CRC failures, or TMDS test-pattern problems.

## Test Signals

Useful validation signals for this chunk are mostly generated-header consistency, compile coverage, and hardware/display smoke tests:

- Build AMDGPU with DCN 3.1.4 support and ensure all generated `reg...` names referenced by register tables and display code resolve.
- Run generated-header checks that each non-`_BASE_IDX` offset has the expected `_BASE_IDX` partner, address-block ordering matches the hardware specification, and repeated instances preserve expected offset spacing.
- Exercise modeset coverage on multiple pipes using OTG0-adjacent state and full OTG1-OTG3 state: timing totals, sync/blanking, update locks, vertical interrupts, DRR, global sync, DSC start position, and CRC readbacks.
- Validate HPD0-HPD4 interrupt/toggle handling and DP AUX0-AUX4 transactions with connector hotplug, EDID reads, DPCD reads/writes, AUX wake, and link-training setup.
- Exercise DIG0-DIG3 HDMI/TMDS paths, including frontend/backend enable, HDMI packet controls, generic/infoframe/VBI/audio packets, ACR 32/44.1/48 kHz programming, TMDS controls, output CRC, FIFO status, and force-disable behavior.
- Exercise AFMT and VPG paths for all four DIG instances with audio infoframes, IEC 60958 data, generic packets, MPEG infoframes, CRC/status readback, and memory power transitions.
- Exercise DP0-DP2 link bring-up, MST, DSC, MSO, secondary packets, GSP scheduling, DPHY training patterns, FEC, scrambler, PRBS, CRC, video M/N, MSA/VBID, ALPM, and AUX-less ALPM.
- Include at least a DP3 smoke path for the registers covered here: link control, pixel format, MSA misc/colorimetry/config, stream control, steer FIFO, video timing/M/N, link framing, HBR2 eye pattern, interrupt control, DPHY control, training pattern selection, and symbol 0/1 programming.
- Use suspend/resume and display blank/unblank tests to cover memory-power, PHY wake, ALPM, HPD, AUX, and stream reprogramming paths.

## Chunk-Specific Summary

Lines 7853-10395 define a dense DCN 3.1.4 display register-offset surface rather than executable code. The central responsibility of this slice is mapping timing generators, display I/O, hotplug/AUX channels, packet/audio helpers, digital encoders, HDMI/TMDS controls, and DP main-link registers to the numeric MMIO offsets consumed by AMDGPU Display Core. Correctness depends on exact generated offsets, matching `_BASE_IDX` values, instance-correct macro use, and validation through modeset, hotplug/AUX, HDMI/audio, DisplayPort link-training, MST/DSC/MSO, ALPM, CRC, and power-management tests.

### subset-b-001831: lines 10396-12981

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 10396-12981

## Scope

This chunk is a generated DCN 3.1.4 register-offset header segment for AMDGPU display hardware. It contains only preprocessor constants: `reg...` names map logical display block registers to MMIO register offsets, and companion `..._BASE_IDX` constants select the register base index used by AMD's register access macros. There are no C functions, structs, or executable control-flow statements in the chunk; the behavior comes from how display code includes these constants into register tables.

The slice starts in the middle of the `dce_dc_dio_dp3_dispdec` register block at `regDP3_DP_DPHY_SYM2` and ends in the `dce_dc_hpo_dp_sym32_enc2_dispdec` block at `regDP_SYM32_ENC2_DP_SYM32_ENC_VID_MSA5`. It therefore covers the end of legacy DP3, legacy DIG4/DP4 stream output, DCIO/UNIPHY lanes, power sequencing, DSC/writeback support, HVM, and the first two full HPO DP stream/link encoder instances plus the beginning of HPO stream encoder 2.

## Purpose

The header provides the DCN314 address map consumed by display core resource construction. `dcn314_resource.c` includes `dcn/dcn_3_1_4_offset.h` alongside mask/shift headers and uses macros such as `SRI`, `SR`, and `SRII` to populate per-instance register structures. For this chunk, the main consumers are:

- legacy DIO stream encoder setup through `SE_DCN314_REG_LIST(id)` in `display/dc/dio/dcn314/dcn314_dio_stream_encoder.h`;
- VPG and AFMT/APG packet/audio helpers through `VPG_DCN3_REG_LIST`, `AFMT_DCN31_REG_LIST`, and `APG_DCN31_REG_LIST`;
- HPO DP stream encoders through `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` in `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`;
- HPO DP link encoders through `DCN3_1_HPO_DP_LINK_ENC_REG_LIST(id)` in `display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h`;
- DCN314 resource arrays such as `stream_enc_regs[]`, `vpg_regs[]`, `afmt_regs[]`, `apg_regs[]`, `hpo_dp_stream_enc_regs[]`, and `hpo_dp_link_enc_regs[]`.

## Register Groups In This Chunk

The chunk has these address-block regions:

- continuation of `dce_dc_dio_dp3_dispdec`: DP3 DPHY symbols, 8b/10b, PRBS/scrambler/CRC, fast training, secondary-data packet controls, audio M/N readback, MSE/SST/MST allocation timing, MSA timing/colorimetry, DSC, GSP8-GSP11, metadata transmission, ALPM, and AUX-less ALPM registers.
- `dce_dc_dio_dig4_vpg_vpg_dispdec` at base `0x164a0`: `VPG4_*` generic packet access/data/update/status, memory power, ISRC, and MPEG info registers.
- `dce_dc_dio_dig4_afmt_afmt_dispdec` at base `0x164cc`: `AFMT4_*` audio, VBI/infoframe, 60958 channel status, CRC, ramp, generic packet, and memory power registers.
- `dce_dc_dio_dig4_dme_dme_dispdec` at base `0x16524`: `DME4_DME_CONTROL` and `DME4_DME_MEMORY_CONTROL` metadata-engine controls.
- `dce_dc_dio_dig4_dispdec` at base `0x1000`: `DIG4_*` stream-encoder registers for HDMI packet generation, audio ACR, front-end control, FIFO, TMDS, clocks, CRC, stereo sync, and format conversion.
- `dce_dc_dio_dp4_dispdec` at base `0x1000`: `DP4_*` legacy DisplayPort link/video/secondary-data registers mirroring the DP3-style set for DIO instance 4.
- DCIO/DCIO chip and `UNIPHY1` through `UNIPHY4`: clock, power, PLL, training, DPCS, RDPCS, PHY control, test/debug, and data-swap/order registers for physical output lanes.
- `PWRSEQ0` and `PWRSEQ1`: backlight/LVTMA control, panel timing, GPIO, reference divider, reset, and debug/status registers.
- DSC0 through DSC3: DSC top, DSC CIF, DSCC encoder controls, PPS words, rate control, flatness, native 4:2:0/4:2:2, clock-gate, debug, and per-DSC perfmon registers.
- `WB0`: display writeback controls, scaling/tap/filter registers, writeback line/frame state, pixel format, interrupt/status, and writeback perfmon.
- `DCHVM`: HVM power control/status and debug.
- HPO stream encoder instances 0 and 1: `DP_STREAM_ENC*`, `APG*`, `DME5/6`, `VPG5/6`, `DP_SYM32_ENC0/1`, `DP_LINK_ENC0/1`, and `DP_DPHY_SYM320/321` blocks.
- HPO stream encoder instance 2 prefix: `DP_STREAM_ENC2`, `APG2`, `DME7`, `VPG7`, and `DP_SYM32_ENC2` through `VID_MSA5`.

All defines in this range use `_BASE_IDX 2`, except this chunk begins after earlier header regions that can use other base indices. That matters because the same logical register name may exist across ASIC headers with different base index or offset values.

## Important APIs, Types, And Macro Contracts

There are no local API functions, but the constants are part of a macro ABI used by display code:

- `reg<block><instance>_<register>`: symbolic MMIO offset. Examples in this chunk include `regDP3_DP_SEC_CNTL`, `regDIG4_HDMI_CONTROL`, `regVPG4_VPG_GENERIC_PACKET_DATA`, `regDP_STREAM_ENC1_DP_STREAM_ENC_CLOCK_CONTROL`, and `regDP_DPHY_SYM321_DP_DPHY_SYM32_TP_CONFIG`.
- `reg<...>_BASE_IDX`: register base selector consumed with the offset by low-level AMDGPU register macros.
- `SRI(name, block, id)`: used by resource macros to expand to instance-specific `reg<block><id>_<name>` plus base-index symbols.
- `SR(name)` and `SRII(name, block, id)`: related macros used for non-instance and double-indexed register arrays.
- `struct dcn10_stream_enc_registers`, `struct dcn30_vpg_registers`, `struct dcn31_afmt_registers`, `struct dcn31_apg_registers`, `struct dcn31_hpo_dp_stream_encoder_registers`, and `struct dcn31_hpo_dp_link_encoder_registers`: resource-side containers populated from these constants.

The chunk's legacy DIO symbols map to fields used by `SE_DCN314_REG_LIST(id)`, including HDMI controls, DP MSA, DP secondary-data packet controls, metadata transmission, DME control, FIFO, and DIG front-end control. The HPO symbols map to fields used by `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` and `DCN3_1_HPO_DP_LINK_ENC_REG_LIST(id)`, including stream clock/input/audio controls, SYM32 video MSA/format/FIFO/SDP/audio/CRC controls, link clock controls, DPHY status, test-pattern, PRBS seed, SAT and VC rate registers.

## Control Flow And Runtime Use

This header has compile-time substitution only. Runtime flow is indirect:

1. DCN314 resource construction includes this offset header and the matching shift/mask headers.
2. Resource macros instantiate static register arrays. For example, `stream_enc_regs[]` uses `SE_DCN314_REG_LIST(id)` for legacy stream encoders 0-4; `hpo_dp_stream_enc_regs[]` uses `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` for HPO stream encoders 0-3; `hpo_dp_link_enc_regs[]` uses `DCN3_1_HPO_DP_LINK_ENC_REG_LIST(id)` for HPO link encoders 0-1.
3. Construct functions attach the selected per-instance register table to hardware objects such as stream encoders, VPG/APG/AFMT helpers, or HPO link encoders.
4. Operational code uses `REG_READ`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and related macros against logical field names. Those macros dereference the pre-populated register offset and apply the paired mask/shift definitions.

The practical control flow covered by this chunk includes HDMI setup, DP secondary-data packet enablement, DP audio timestamp/M/N programming, DSC stream setup, VPG generic packet updates, APG audio packet generator enable/disable, HPO stream enable/reset/status polling, HPO DPHY training/test-pattern programming, and HPO MST/SST slot allocation updates.

## State And Persistence Behavior

The constants themselves have no mutable state and persist only as compiled-in register addresses. They define access points for hardware state held in display registers:

- DP/DIG stream state: pixel format, MSA timing, video M/N, VBID, stream enable/status, FIFO reset/enable, HDMI deep-color/scrambling/packet generation, audio ACR, and secondary-data packet enable bits.
- Packet metadata state: VPG/AFMT/APG generic packet RAM/data windows, frame-update and immediate-update latches, conflict/status bits, ISRC/MPEG/audio info state, and metadata-engine controls.
- Link/PHY state: UNIPHY clock/power/training controls, RDPCS/DPCS state, HPO link clock enable, DPHY reset/enable/status, lane count, mode, PRBS/test-pattern seeds, symbol override, CRC counters, SAT allocation, and VC rate updates.
- Panel and compression state: PWRSEQ backlight/panel timing/reset and DSC PPS/rate/flatness/clock-gate/debug/perfmon registers.
- Writeback state: WB enable/path, scaling filter/taps, line/frame counters, status and perfmon state.

Because these offsets address hardware registers, incorrect values can persist until the display engine is reprogrammed, reset, power-cycled, or overwritten by later driver operations. The generated header is not responsible for saving/restoring state; state ownership is in the display resource and hardware-sequencing layers.

## Dependencies And Integration Points

Direct dependencies are generated companion headers for the same ASIC family, especially `dcn_3_1_4_sh_mask.h`, and the core register-access macros used throughout AMD display code. The offset names must match field-definition prefixes in mask/shift headers and the register list macros in DC source headers.

Important integration points:

- `display/dc/resource/dcn314/dcn314_resource.c`: builds the static register tables for stream encoders, link encoders, VPG, AFMT, APG, HPO stream encoders, and HPO link encoders.
- `display/dc/dio/dcn314/dcn314_dio_stream_encoder.h` and `.c`: consume `DIG4_*`, `DP4_*`, DME, HDMI, and DP SEC/MSA offsets via `SE_DCN314_REG_LIST` and perform HDMI/DP stream programming.
- `display/dc/dio/dcn31/dcn31_dio_link_encoder.c` and shared DCN link-encoder code: use `DP_LINK_CNTL`, UNIPHY, DPCS, and RDPCS registers for link training and PHY control.
- `display/dc/dcn30/dcn30_vpg.h`, `display/dc/dcn31/dcn31_vpg.h`, and VPG implementation: use `VPG4`, `VPG5`, `VPG6`, and `VPG7` offsets for generic info-packet programming.
- `display/dc/dcn31/dcn31_apg.h`: consumes `APG0-APG2` offsets for HPO audio packet generator reset, enable, stream ID, debug audio channels, and memory-power controls.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` and HPO stream encoder implementation: use `DP_STREAM_ENC*` and `DP_SYM32_ENC*` offsets for UHBR/HPO stream setup.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and implementation: use `DP_LINK_ENC*` and `DP_DPHY_SYM32*` offsets for HPO link setup, training patterns, SAT/VC rate programming, and status polling.
- `display/dmub/src/dmub_dcn314.c` and `display/dc/irq/dcn314/irq_service_dcn314.c`: include the same offset header for DMUB and interrupt register access, though this exact slice is mostly display-output block offsets.

## Risks And Edge Cases

- Offset/header mismatch: These generated constants must be paired with the DCN314 mask/shift header. Reusing a DCN315/DCN320/DCN36 offset header with DCN314 resource tables can silently point register writes at the wrong MMIO locations.
- Instance mapping mistakes: The chunk includes both legacy DIO instances (`DIG4`, `DP4`, `VPG4`, `AFMT4`, `DME4`) and HPO instances (`DP_STREAM_ENC0-2`, `VPG5-7`, `DME5-7`). Resource comments in `dcn314_resource.c` note that VPG/AFMT/DME blocks are mapped to DIO block instances; off-by-one mapping errors can send info packets or metadata to the wrong stream.
- Partial chunk boundary: The chunk starts after the beginning of `DP3` and ends before completing `DP_SYM32_ENC2`; merge/reconciliation must combine adjacent chunks to get the full per-file register map.
- Duplicate logical registers: Some register names appear twice in macro lists, such as metadata transmission and HDMI metadata packet control in DCN314 stream encoder lists. Generated offsets must remain stable so duplicate logical consumers resolve consistently.
- Hardware side effects: Registers in this chunk include reset, enable, training, memory-power, CRC, status-clear, and update-pending controls. Bad offsets can cause visible display loss, audio loss, link training failure, panel backlight issues, metadata packet corruption, DSC corruption, or writes into reserved hardware.
- Base-index sensitivity: This slice consistently uses base index `2`, but other ASIC generations can have identical logical names with different offsets or base indices. Tests should catch both offset and base-index regressions.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware smoke tests rather than unit tests:

- Build coverage: compile AMDGPU display code for DCN314 with this header included, ensuring all `SRI`/`SE_SF` references resolve and register structures initialize cleanly.
- Register-table sanity: inspect generated/compiled `dcn314_resource.c` register arrays for expected offsets, especially `DIG4`, `DP4`, `VPG4`, `AFMT4`, `DME4`, `DP_STREAM_ENC0-2`, `DP_LINK_ENC0-1`, and `DP_DPHY_SYM320/321`.
- Display bring-up: attach HDMI and DP sinks on DCN314 hardware and verify stream enable, link training completion, correct pixel format/deep color, no blanking artifacts, and stable hotplug/retrain behavior.
- Packet/audio behavior: verify HDMI audio, DP audio, infoframes, HDR/metadata packets, ISRC/MPEG packets, and VPG/APG generic packet update paths; failures often indicate bad AFMT/VPG/APG/DME/DIG offsets.
- MST/HPO behavior: test DisplayPort MST and HPO-capable links, checking SAT/VC allocation updates, stream-to-link mapping, UHBR/HBR training patterns, and HPO stream/link enable/reset status.
- DSC and writeback: enable DSC output paths and display writeback where supported, watching for corruption, underflow, CRC mismatch, or perfmon/status anomalies.
- Power sequencing: panel/backlight and power-gating tests should watch PWRSEQ, DSC clock-gate, APG/VPG memory-power, and UNIPHY power-state side effects.

## Research Notes

This is a generated hardware contract rather than hand-written logic. The substantive behavior is in consumers that turn these offset macros into typed register tables and then into MMIO operations. The most important maintenance invariant is name alignment across three layers: offset macro names in this file, mask/shift field names in the paired generated headers, and register-list entries in DC resource/helper headers.

### subset-b-001832: lines 12982-15245

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 12982-15245

## Purpose

This chunk is generated AMD DCN 3.1.4 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to numeric MMIO offsets plus companion base-index selectors. DCN314 display code combines each `reg...` offset with its matching `reg..._BASE_IDX` through helper macros such as `BASE(reg..._BASE_IDX) + reg...`.

The requested range is the final large slice of `dcn_3_1_4_offset.h`. It starts in the tail of HPO DP Sym32 stream encoder 2, then covers HPO DP stream encoder 3, MPC/MPCC composition and color-management blocks, HPO HDMI stream encoder 0 packet/audio blocks, HPO top/mapper/perfmon blocks, ABM instances 0 through 3, DPIA MU status/timeout registers, and the second HDA/Azalia controller/endpoint aliases. The chunk has 2,136 `#define` lines: 1,068 register-offset macros and 1,068 matching `_BASE_IDX` macros.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, or direct includes in this range. Its public surface is the generated register macro namespace:

- `reg<block>_<register>`: a DCN314 MMIO register offset.
- `reg<block>_<register>_BASE_IDX`: the DCN base segment selector used by resource and hardware helper macros.

Every non-`_BASE_IDX` register macro in this chunk has a matching `_BASE_IDX`. The first HPO DP stream-encoder families use base index `2`; the MPC, HPO top/HDMI, ABM, DPIA, and HDA/AZ families in this slice use base index `3`. The base index is part of the address contract, so the numeric offset alone is not sufficient for safe register access.

Major macro families in this slice:

- Tail of `DP_SYM32_ENC2`: video MSA tail registers, HBLANK control, generic SDP/GSP controls 0-14, SDP audio/metadata controls, stream/VBID/panel replay/CRC controls, memory power, and spare register.
- `DP_STREAM_ENC3`, `APG3`, `DME8`, `VPG8`, and `DP_SYM32_ENC3`: HPO DP stream encoder 3 clock/input/audio controls, APG audio packet generator controls and CRC/status, DME memory/control, VPG generic packet/ISRC/MPEG registers, and Sym32 video/SDP/MSA/CRC/memory-power controls.
- `MPCC0` through `MPCC3`: compositor pipe controls for top/bottom selection, OPP routing, blending/control fields, update-lock selection, gains, background color, memory power, and status.
- `MPCC_OGAM0` through `MPCC_OGAM3`: per-MPCC output gamma controls, indexed LUT access/data, RAM A/B piecewise-region programming, offsets, start/end/slope/base controls, and gamut-remap coefficient registers.
- `MPC` configuration: clock control, mutex/arbiter controls, output MUXes, output CDE controls, DWB muxing, CRC controls/results, 1 mux, MMHUBBUB read-urgent select, shared memory-power control, and debug-select/data registers.
- `MPC_OUT0` through `MPC_OUT3` OCSC: output muxes, output CSC control and 3x4 coefficient registers for output color-space conversion.
- `MPC_RMU`: RMU control, memory power, MPCC muxing, shared control, shaper LUT programming, RAM A/B regions, 3D LUT indexed access/data/read-write control, normalization factor, and output offsets for two RMU pipelines.
- `DC_PERFMON22` and `DC_PERFMON23`: MPC and HPO perf counter control/state/current-value/high/low registers.
- `AFMT5`, `VPG9`, and `DME9`: HPO HDMI stream encoder 0 audio formatter packet/channel/status/CRC/audio source/memory-power controls, VPG generic packet registers, and DME control/memory-control.
- `HPO_TOP` and `DP_STREAM_MAPPER`: HPO top clock/hardware controls and stream-mapper controls 0-3.
- `ABM0` through `ABM3`: ambient/user/target/current/final PWM levels, minimum duty cycle, ABM/PWM update/lock controls, ACE offset/slope and threshold controls, luma statistics, sample rates, histogram bin shift/index controls, histogram results 1-24, and backlight master lock.
- `DPIA_MU`: RBBM interface timeout controls and status.
- `AZCONTROLLER1`, `AZENDPOINT1`, and `AZINPUTENDPOINT1`: HDA/Azalia CORB/RIRB pointers/control/status/size, immediate command/response interfaces, DMA position base addresses, and endpoint immediate command aliases.

## Control Flow

This header has no runtime control flow. The runtime sequencing is supplied by AMDGPU display code:

1. DCN314 resource, IRQ, DIO, DMUB, clock, HPO, ABM, VPG, AFMT, MPC, and related code includes `dcn_3_1_4_offset.h` together with `dcn_3_1_4_sh_mask.h`.
2. Register-list macros paste instance IDs into generated names such as `regMPCC0_MPCC_STATUS`, `regMPCC_OGAM3_MPCC_OGAM_LUT_DATA`, `regMPC_RMU1_3DLUT_DATA`, `regVPG9_VPG_GENERIC_PACKET_DATA`, or `regABM2_DC_ABM1_HG_RESULT_24`.
3. Resource helpers in `dcn314_resource.c` define address builders such as `SR(reg_name)` and `SRI(reg_name, block, id)` that expand the offset plus its `BASE_IDX` segment.
4. Hardware blocks later use the populated register tables through `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, wait/poll helpers, and DMUB register access paths.

The macros do not encode ordering or side effects. Consumers still must sequence clocks, power gating, memory power, stream setup, audio/infoframe packet updates, double-buffer commits, color LUT programming, ABM/backlight updates, perf counter sampling, HDA command rings, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files. It describes MMIO-backed GPU display state. The represented hardware state includes:

- HPO DP/HDMI stream-encoder state for input routing, clocks, audio controls, video MSA/MSA double-buffering, SDP/GSP packet controls, metadata packets, panel replay, CRC capture, memory power, and spare/debug controls.
- APG, VPG, AFMT, and DME state for audio/infoframe/generic packet generation, ISRC/MPEG metadata, audio CRC/status, packet update timing, memory control, and memory-power state.
- MPC/MPCC blending and routing state for plane composition, OPP/output selection, background color, gains, update locks, memory power, status, mutex arbitration, debug buses, CRC capture, and DWB routing.
- Output color-management state for MPCC output gamma LUTs, shaper LUTs, output CSC matrices, gamut-remap coefficients, 3D LUT access/data, normalization factors, and RMU pipeline routing.
- ABM/backlight state for user and ambient light inputs, ABM target/current levels, PWM duty-cycle output, ACE parameters, luma statistics, histogram bins/results, sample rates, register locks, and master backlight lock.
- DPIA MU RBBM interface status and timeout configuration.
- HDA/Azalia command-ring and immediate command state for the second controller and endpoint aliases.

Persistence is hardware-defined. Configuration registers normally retain values until modeset, block reprogramming, power gating, suspend/resume, or ASIC reset. Status, interrupt, lock, indexed data, CRC, histogram, perf counter, clear/ack, and command-interface registers can be read-only, sticky, write-one-to-clear, self-clearing, or timing-sensitive. This offset header does not define those semantics; the matching mask header and block-specific driver code do.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN314 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h` for field shifts and masks.
- DCN base-address definitions in `dcn314_resource.c`, especially `DCN_BASE__INST0_SEG2` and `DCN_BASE__INST0_SEG3`, which are selected through `_BASE_IDX` values.
- Register helper macros from `reg_helper.h` and local resource macros such as `SR`, `SRI`, `SRI2`, and `SRIR`.

Direct include sites for `dcn_3_1_4_offset.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

Important consumers around these register families include DCN314 resource-pool construction, DIO stream encoder setup, HPO DP stream/link encoders, `dcn31_vpg`, `dcn31_afmt`, ABM/DMUB backlight control, MPC/MPCC color and composition code, IRQ service setup, perf counter/debug paths, and HDA/Azalia display-audio initialization.

## Risks And Edge Cases

- Offset or base-index drift is the main risk. These are untyped preprocessor constants, so a bad offset or `_BASE_IDX` can compile cleanly while reading or writing the wrong MMIO register.
- The chunk begins inside `DP_SYM32_ENC2`; earlier macros for that block are owned by the previous chunk. File-level conclusions about encoder 2 require reconciliation with adjacent chunks.
- Repeated instance families are copy-sensitive. `MPCC0`-`MPCC3`, `MPCC_OGAM0`-`MPCC_OGAM3`, `ABM0`-`ABM3`, and HPO DP/HDMI packet blocks are structurally similar but not interchangeable.
- Indexed LUT/data pairs are sequencing-sensitive. Wrong `LUT_INDEX`, `LUT_DATA`, shaper, 3D LUT, or gamut-remap offsets can silently corrupt color programming and may only show on HDR, gamma, color-management, or multi-plane paths.
- Packet and audio controls are timing-sensitive. Bad VPG/AFMT/APG/DME/HPO offsets can cause missing or stale infoframes, audio dropouts, CRC failures, metadata corruption, or issues limited to DP/HDMI HPO paths.
- ABM and PWM registers affect visible backlight behavior. Incorrect offsets or lock handling can cause wrong brightness, flicker, unexpected dimming, failed ambient-light compensation, or resume-time backlight regressions.
- Perfmon, CRC, histogram, status, and command-ring registers may be read/clear or counter-like. Treating them as ordinary persistent configuration can lose diagnostics or create misleading telemetry.
- HDA/AZ aliases intentionally share some offsets, for example CORB and RIRB subfields mapped at the same register address. Mechanical duplicate-address checks must account for packed register fields and endpoint aliases.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN314 support enabled; missing or renamed macros should fail in DCN314 resource, IRQ, DMUB, DIO, HPO, VPG, AFMT, ABM, MPC, and related register-table construction.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 12982-15245 has exactly one matching `_BASE_IDX` macro, and that base-index values remain `2` for HPO DP stream-encoder register blocks and `3` for the later MPC/HPO/ABM/DPIA/HDA register blocks.
- Diff this chunk against AMD's authoritative DCN314 register database and adjacent generated headers where compatible register maps are expected, such as DCN 3.1.x and DCN 4.x offset headers.
- Exercise HPO DP and HPO HDMI outputs: modesets, link enable/disable, audio playback, packet/infoframe updates, metadata packets, panel replay paths where available, CRC capture, suspend/resume, and hotplug.
- Exercise composition and color-management paths: multi-plane blending, OPP routing, MPC CRCs, output CSC, gamut remap, output gamma, shaper LUTs, 3D LUT programming, and DWB routing.
- Validate ABM/backlight behavior across all exposed ABM instances: brightness updates, ambient-light input, ABM level changes, histogram/luma statistics, PWM duty cycle, register locking, and suspend/resume restoration.
- Watch kernel logs and display diagnostics for MMIO access faults, underflow, link-training failures, packet conflicts, audio loss, color corruption, backlight anomalies, stuck interrupts, perf counter anomalies, HDA command timeouts, and DPIA MU RBBM timeout/status errors.

## Cross-Chunk Notes

Earlier chunks own the beginning of `dce_dc_hpo_dp_sym32_enc2_dispdec`, including the control, FIFO, pixel-format, and first MSA registers. This chunk owns the encoder-2 tail and the final DCN314 offset-header blocks through `#endif`. The merge lane should reconcile this document with neighboring chunks before making complete claims about the full `dcn_3_1_4_offset.h` register map.
