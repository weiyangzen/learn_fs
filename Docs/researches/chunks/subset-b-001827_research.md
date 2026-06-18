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
