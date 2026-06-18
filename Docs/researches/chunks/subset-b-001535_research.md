# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 15216-17814

## Scope And Purpose

This chunk is a generated-style AMD DCE 12.0 register offset header section. It contains C preprocessor constants only: symbolic register offsets and their paired `_BASE_IDX` values for MMIO register spaces, plus `ix...` constants for Azalia indexed registers. There are no C functions, structs, enums, or runtime branches in this range.

The mapped range starts in the middle of the `dce_dc_dcio_uniphy6_dispdec` register block, at `mmDCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED40`, and ends in the middle of `azf0inputendpoint3_inputendpointind`, at `ixAZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB`. Full conclusions for those two boundary blocks require adjacent chunk research.

The purpose of this chunk is to expose DCE 12.0 display-engine hardware addresses for late UNIPHY6 registers, full UNIPHY8 PHY/PLL register groups, DSI0/DSI1 controller blocks, DisplayPort receiver secondary-data blocks, one display performance monitor, ZCAL/calibration registers, and the Azalia HD-audio root, stream, endpoint, and input-endpoint indirect register maps. AMDGPU display code includes this header with `dce_12_0_sh_mask.h` and uses these constants as the compile-time address layer for `dm_read_reg_soc15()`, `dm_write_reg_soc15()`, indirect Azalia helpers, and generated register tables.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself. The `mm...` names are direct MMIO register offsets, almost always followed by a matching `_BASE_IDX` macro selecting the SOC15 base segment. In this chunk, most display block offsets use base index `2`; Azalia root and stream descriptor offsets use base index `1`; the `ix...` endpoint constants are indexed-register offsets and do not have `_BASE_IDX` companions.

Important macro families in this chunk include:

- Partial UNIPHY6 reserved macro-control table: `mmDCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED40` through `RESERVED159` provide contiguous reserved or undocumented PHY macro-control offsets from `0x2616` through `0x268d`, all with base index `2`.
- UNIPHY6 common, TX, and PLL controls: `mmDC_COMBOPHYCMREGS6_COMMON_*` defines common fuse, deemphasis, lane power-management, TX control, lane reset, ZCAL-code, and RFU offsets; `mmDC_COMBOPHYTXREGS6_*_LANE0` through `LANE3` define per-lane command-bus, margin/deemphasis, global TX, and RFU offsets; `mmDC_COMBOPHYPLLREGS6_*` defines PLL frequency, bandwidth, calibration, loop, regulator, observe, and DFT offsets.
- Full UNIPHY8 reserved macro-control table and split PHY views: `mmDCIO_UNIPHY8_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159` map a contiguous reserved region from `0x26b6` through `0x2755`. The same physical address range is also named through `mmDC_COMBOPHYCMREGS8_COMMON_*`, `mmDC_COMBOPHYTXREGS8_*_LANE*`, and `mmDC_COMBOPHYPLLREGS8_*`, giving consumers semantic names for common, lane TX, and PLL subblocks.
- DSI controllers: `mmDSI0_*` and `mmDSI1_*` define parallel MIPI DSI controller blocks. Each block includes display DSI control/status, clock, trigger, command, timing, PHY, lane, escape-mode, packet, virtual-channel, power, memory, and debug-style registers. The two blocks are separated by a regular offset stride: DSI0 starts at `0x27be`, while DSI1 starts at `0x28be`.
- DPRX secondary-data blocks: `mmDPRX_SD0_*` and `mmDPRX_SD1_*` provide DisplayPort receiver secondary-data control, video stream ID, SDP receive/acknowledge, MSA/VBID, timestamp, audio/MST/MSE activity, CRC, packet status, debug, and multi-stream allocation handled-state offsets. These support receiver-side DP status and packet tracking.
- Performance monitor and calibration: `mmDC_PERFMON10_*` defines the perf-counter control, state, count, high/low, and interrupt-misc offsets for display performance monitor instance 10. `mmCOMP_EN_CTL`, `mmZCAL_CTRL`, and `mmZCAL_FUSES` expose common impedance/calibration control and fuse state.
- Sparse or empty address block markers: the chunk contains `addressBlock` comments for VGA page-address and `dce_dc_dispdec[948..986]` ranges, but no `#define` lines inside this mapped interval. Those comments preserve generated register-database structure across chunk boundaries.
- Azalia root/controller MMIO registers: `mmCORB_*`, `mmRIRB_*`, `mmIMMEDIATE_COMMAND_*`, `mmAZROOT_*`, `mmAZENDPOINT_*`, `mmDMA_*`, `mmWALL_CLOCK_COUNTER`, and aliases expose the HD-audio command output ring buffer, response input ring buffer, immediate command interface, codec write control, endpoint index/data ports, DMA position buffer, and wall-clock counter.
- Azalia output stream descriptor MMIO registers: `mmAZSTREAM0_*` through `mmAZSTREAM7_*` define eight output stream descriptor blocks. Each block repeats control/status, link-position, cyclic-buffer length, last-valid index, FIFO size, format, BDL pointer, and link-position alias offsets.
- Azalia stream indirect registers: `ixAZF0STREAM0_*` through `ixAZF0STREAM15_*` define 16 stream-indexed FIFO/response/request counters: FIFO size control, FIFO information, FIFO index, FIFO data, and cumulative request count.
- Azalia output endpoint indirect registers: `ixAZF0ENDPOINT0_*` through `ixAZF0ENDPOINT7_*` define eight endpoint maps, each with 71 converter and pin-control offsets. They cover audio widget capabilities, converter format and stream ID, digital converter state, supported formats/rates, stripe/ramp/GTC controls, pin capabilities, unsolicited response, pin sense, widget control, speaker/channel metadata, audio descriptors 0-13, multichannel and HBR controls, lipsync, sink info, hotplug, configuration defaults, channel-status overrides, LPIB snapshots, coding/format-change state, wireless display identification, remote keepalive, and audio enabled/disabled/format-change interrupt status.
- Azalia input endpoint indirect registers: `ixAZF0INPUTENDPOINT0_*` through the partial `ixAZF0INPUTENDPOINT3_*` block define input converter and input pin-control offsets. Complete input endpoints 0-2 include format, stream ID, digital converter, supported formats/rates, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel/HBR, channel allocation, hotplug, configuration default, LPIB snapshots, input status control, and infoframe offsets.

## Control Flow And Data Flow

This header chunk has no executable control flow. Its data flow is compile-time substitution into register access sequences. A caller selects a macro such as `mmDSI0_DISP_DSI_CTRL` or `mmAZSTREAM0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`, combines it with the appropriate SOC15 base index or per-instance offset machinery, and then reads or writes the resulting hardware register.

The implied hardware flows are:

- PHY programming flows use the UNIPHY and COMBOPHY names to configure or inspect common PHY fuses, lane power, TX command/margin state, lane resets, PLL frequency/bandwidth/calibration, and debug/DFT observation state. The generated header intentionally exposes both reserved raw macro-control names and semantic common/TX/PLL aliases over overlapping address ranges.
- DSI bring-up uses DSI control, clock, lane, command, timing, packet, and PHY offsets to enable a panel link, send commands, configure escape/low-power behavior, program display timings, and monitor status/error/debug registers.
- DPRX flows read or program secondary-data and MSA/VBID state, track received SDP/audio/MST/MSE activity, handle ACT and allocation notifications, and inspect CRC or packet-status fields for validation and diagnostics.
- Performance-monitor flows configure monitor 10, start or stop counter collection, read high/low counter values, and handle interrupt/misc state.
- Azalia controller flows use CORB/RIRB and immediate-command registers to exchange HD-audio codec verbs and responses. Endpoint index/data registers provide another path to the codec endpoint indirect register space.
- Azalia stream flows program stream descriptor control/status, buffer length, last-valid index, FIFO size, audio format, BDL pointers, and link positions. The indirect `ixAZF0STREAM*` registers provide FIFO status and request-count views for more stream instances than the direct descriptor block list in this chunk.
- Azalia endpoint flows configure converter formats, bind channels/streams, expose sink and pin capabilities, handle hotplug or unsolicited responses, report audio enable/disable/format-change status, and snapshot LPIB timing state.

Because all behavior is driven by consumers, call ordering is external. The header only fixes the numeric contract that those consumers rely on.

## State And Persistence Behavior

The header stores no runtime state. Mutable and persistent state lives in the ASIC's MMIO and indexed register blocks. Values written through these offsets can remain active until explicitly reprogrammed, reset, power-gated, or overwritten by firmware/driver flows.

State classes represented by this chunk include:

- PHY configuration and calibration state: UNIPHY/COMBOPHY lane resets, lane power, TX control, margin/deemphasis, ZCAL, PLL frequency, PLL loop/bandwidth, regulator config, observe, and DFT registers affect physical display-link behavior.
- DSI controller state: command queues, lane/PHY control, clocks, timing, escape mode, virtual channel, packet generation, memory power, and debug/status values define panel-link operation and command-mode/video-mode behavior.
- DPRX receiver state: SDP, MSA, VBID, audio, MST, ACT, MSE allocation, CRC, timestamp, and handled-state registers capture receiver-side stream metadata and events.
- Performance-counter state: perfmon control, state, current values, high/low snapshots, and interrupt-misc state are mutable and can be latched or cleared according to hardware semantics outside this file.
- Azalia command/response state: CORB/RIRB pointers, base addresses, immediate-command output/response, codec write control, endpoint index/data, DMA position buffer address, and wall-clock counters are host-controller state used by audio command transport.
- Azalia audio-stream state: stream descriptor control/status, link-position counters, cyclic-buffer size, last-valid index, FIFO size, stream format, BDL pointer, FIFO data, and request counts track active audio DMA streams.
- Azalia codec endpoint state: converter format, stream/channel ID, pin widget controls, audio descriptors, sink information, multichannel/HBR/lipsync settings, hotplug and unsolicited response settings, LPIB snapshots, coding type, format-change status, wireless display identification, and audio enable/disable interrupt status reflect codec and display-audio endpoint behavior.

Incorrect constants are persistent in effect even though the header itself is static. A wrong offset for a PLL or TX register can misprogram physical links; a wrong DSI register can break panel command or timing setup; a wrong Azalia stream or endpoint index can route audio to the wrong converter or corrupt stream descriptor state until the block is reset or reinitialized.

## Dependencies And Integration Points

This file is an ASIC-specific generated register-address dependency. It is included by DCE 12.0 display code such as `dce120_timing_generator.c`, `dce120_hwseq.c`, `irq_service_dce120.c`, GPIO factory/translate code, and `dce120_resource.c`, normally alongside `dce_12_0_sh_mask.h`, `soc15_hw_ip.h`, `vega10_ip_offset.h`, and register helper headers. Those consumers use patterns such as register structs, `REG(reg)` macros, `dm_read_reg_soc15()`, `dm_write_reg_soc15()`, and per-instance offset calculations.

The most direct consumer pattern for the Azalia portion is the generic DCE audio layer. `dce_audio.c` defines `REG(reg)` for direct audio MMIO offsets and `IX_REG(reg)` for endpoint/stream indirect offsets, then routes reads and writes through helpers like `read_indirect_azalia_reg()` and `write_indirect_azalia_reg()`. The `mmAZ*` and `ixAZF0*` constants in this chunk are therefore part of the display-audio programming contract even when the higher-level audio code is shared across DCE/DCN generations.

Major integration surfaces are:

- DRM/KMS display bring-up and link-resource construction, where DCE 12.0 resource code selects clock sources, link encoders, stream encoders, AUX engines, I2C engines, timing generators, and hardware sequencer registers.
- Display physical-link programming for UNIPHY/COMBOPHY PHY and PLL state, including board/ASIC-sensitive sequences provided by link encoder, BIOS, firmware, or low-level display code.
- MIPI DSI panel support and diagnostics for control, command, lane, PHY, packet, timing, and memory-power registers.
- DisplayPort receiver/secondary-data handling for stream metadata, MST allocation, ACT handling, MSA/VBID tracking, CRC, and audio packet status.
- Display performance monitoring and calibration/debug paths that consume perfmon, ZCAL, observe, and DFT registers.
- Display-audio support, including HD-audio CORB/RIRB transport, immediate commands, stream descriptor programming, endpoint/pin capability handling, hotplug/unsolicited response state, audio format changes, HBR/multichannel controls, and LPIB timing snapshots.
- Generated-header consumers outside active runtime code, including register dumps, ASIC validation tooling, bring-up scripts, and comparisons against AMD's register database.

## Risks And Edge Cases

The primary risk is drift between this generated header and the DCE 12.0 register specification. The compiler can catch missing macro names, but it cannot tell whether an offset or base index points to the wrong hardware register.

Specific risks in this chunk include:

- Chunk boundaries are partial. The first definitions continue an earlier `UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED` run, and the final input endpoint 3 block stops before the rest of that endpoint's input pin controls. Adjacent chunks are needed for complete block-level audits.
- Several semantic register groups alias the same physical offsets. For example, UNIPHY8 raw reserved macros and COMBOPHYCM/TX/PLL names cover overlapping ranges. That is intentional in generated ASIC headers, but a consumer must use the semantic name matching the intended hardware subblock.
- Repeated per-lane and per-instance definitions are copy-sensitive. COMBOPHYTXREGS6/8 lanes 0-3, DSI0/DSI1, DPRX_SD0/SD1, AZSTREAM0-7, AZF0STREAM0-15, AZF0ENDPOINT0-7, and AZF0INPUTENDPOINT0-3 differ mainly by instance number and base offset; off-by-one mistakes are hard to detect in review.
- Base index mismatches are high impact. Most display PHY/DSI/DPRX/perfmon/ZCAL definitions use base index `2`, while Azalia direct registers use base index `1` and Azalia indexed registers omit base indices. Mixing these access paths can read or write an unrelated hardware block.
- Reserved/RFU definitions expose undocumented or hardware-reserved state. Even when names are present, generic code should not assume those registers are safe to write without ASIC-specific sequencing guidance.
- DSI and PHY sequencing is timing-sensitive. Misprogramming lane resets, PLL controls, escape-mode controls, or command/timing registers can produce panel bring-up failures, unstable links, or hangs waiting for status bits.
- DPRX/MST/ACT state is event-sensitive. Wrong offsets for ACT handled, MSE allocation, VBID/MSA, SDP, or audio packet status can cause missed stream changes, false diagnostics, or broken MST receiver behavior.
- Azalia audio endpoint maps are dense and repeated. Confusing stream descriptor MMIO offsets with `ix` endpoint indices, or output endpoints with input endpoints, can misroute audio, report wrong pin capabilities, break HBR/multichannel audio, or hide format-change/hotplug events.
- CORB/RIRB and DMA-position registers are host-controller state. Wrong offsets can corrupt audio command transport, DMA buffer accounting, or wall-clock/link-position synchronization.

## Test Signals

There are no unit tests for this header alone. Useful validation is mostly build coverage, generated-header comparison, register readback, and hardware integration testing:

- Build AMDGPU/DC configurations that include DCE 12.0 support. This catches missing or renamed macros and obvious include-order errors.
- Compare lines 15216-17814 against the authoritative AMD DCE 12.0 register database or a known-good upstream generated copy, paying special attention to the partial UNIPHY6 and input endpoint 3 boundaries.
- Verify SOC15 base-index handling with register readback: display PHY/DSI/DPRX/perfmon/ZCAL offsets should resolve through the display base segment, while Azalia direct registers should resolve through the Azalia/audio base segment and `ixAZF0*` names should be accessed only through indexed-register helpers.
- Exercise display link bring-up on hardware using the affected UNIPHY/COMBOPHY instances, including modes that require lane power changes, PLL programming, TX margin/deemphasis setup, reset sequencing, and suspend/resume restoration.
- Exercise DSI0 and DSI1 panel paths where available, covering command transmission, timing programming, low-power/escape behavior, lane/PHY setup, memory power, and status/error readback.
- Exercise DPRX secondary-data and MST/ACT handling with stream metadata changes, VBID/MSA changes, audio packets, MSE allocation changes, and CRC/status readback.
- Validate `DC_PERFMON10` with perf counter start/stop/read and interrupt/status behavior if monitor instance 10 is exposed by the platform.
- Exercise display audio over HDMI/DP: CORB/RIRB codec commands, immediate commands, output streams 0-7, indirect streams 0-15, endpoints 0-7, input endpoints where supported, hotplug/unsolicited response, HBR/multichannel formats, LPIB snapshots, and audio enable/disable/format-change interrupts.
- Run suspend/resume and display hotplug/audio hotplug tests, since these paths reveal stale register programming, wrong base indices, and state that is not restored correctly.
