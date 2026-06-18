# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 32537-34973

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.1.2 register shift/mask header. It exports preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for memory-mapped display controller registers. The companion offset header supplies register addresses; this file supplies the field layout consumed by the AMD display register helper macros.

The requested range starts in the tail of the OTG3 timing-generator block, immediately after the `OTG3_OTG_DRR_TIMING_INT_STATUS` definitions, and continues through dynamic refresh-rate, constant DTO, DSC start-position, pipe-update, and spare-register fields. It then covers OPTC misc selection and memory-power fields, `DC_PERFMON17`, HPD instances 0 through 4, the full DP0 and DIG0 DIO register groups, and the beginning of DP1 through `DP1_DP_SEC_CNTL2`. The range ends mid-DP1; later DP1 secondary-packet, metadata, ALPM, GSP, and following DIO blocks continue in the next chunk.

There are no functions, structs, branches, loops, or direct runtime side effects in this chunk. The public surface is generated macro metadata. Runtime behavior is created when DCN resource constructors bind these masks and shifts into timing-generator, HPD/GPIO, link-encoder, stream-encoder, interrupt-service, and hardware-sequencer objects, after which display code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related helpers to program hardware.

## Register Blocks Covered

The OTG3 tail covers dynamic refresh-rate programming and status: vertical-total reach ranges, vertical-total change limits, trigger-window X ranges, average-frame and last-used vertical-total readback, M-constant DTO phase/modulo, horizontal-duplicate request mode, DSC start X/line position, pipe update pending/status bits, and a spare register.

The OPTC misc block covers DWB source selection for three writeback paths, global swap-lock ready/timing-sync source selection, OPTC clock-gating/test-clock controls, ODM memory power force/disable bits for memories 0 through 7, unassigned and vblank ODM memory power modes, ODM memory power status readback, and an OPTC misc spare register. `DC_PERFMON17` follows with the standard display performance-counter and perfmon field set: counter event/value selection, increment and hardware-control modes, run/interrupt/restart controls, counter state lanes 0 through 7, perfmon state/report count/interrupt controls, clock and run-enable start/stop selection, counter-value interrupt status/ack bits, and high/low counter readback selectors.

HPD0 through HPD4 are repeated hotplug-detect blocks. Each instance defines interrupt status and sense fields, interrupt and RX interrupt ack/enable/polarity fields, HPD enable and timer fields, fast-training connection delay/enables, and connect/disconnect debounce filter delays.

DP0 is a complete DisplayPort transmitter register field group. It includes link control, pixel format, MSA colorimetry/misc/timing, DP configuration and lane count, video stream enable/status/deferred-disable, FIFO steering, video M/N timing generation, link framing and enhanced frame mode, HBR2 eye pattern, VBID and video interrupt controls, DPHY controls for training patterns, symbols, 8b/10b, PRBS, scrambling, CRC, MST CRC, fast training, BS/SR swap, and HBR2 pattern control. It also includes secondary-data packet controls for stream, audio, ACP/ISRC/MPG/GSP packets, secondary-packet framing, DP audio N/M and readbacks, timestamp mode, MSE rate and stream-allocation-table programming/status, MSA timing parameter registers, MSO controls, DSC control and bytes-per-pixel, metadata transmission, ALPM, GSP8 through GSP11 controls, and GSP enable double-buffer status.

DIG0 is the corresponding digital encoder and HDMI/TMDS block. It covers frontend and backend control, output CRC control/result, clock/test/random pattern fields, FIFO status and recalibration fields, HDMI metadata, general HDMI control/status, HDMI audio and ACR packet controls and readbacks, VBI/infoframe/generic packet controls 0 through 10, general-control packet fields, AFMT audio clock control, TMDS mode/control characters, stereo-sync selection, sync-character patterns, TMDS control bits, DC balancer controls, DIG version, and forced disable.

DP1 begins a second DisplayPort transmitter instance with the same generated shape as DP0, but this chunk only reaches `DP1_DP_SEC_CNTL2`. The covered DP1 fields include link/video/pixel/MSA setup, DPHY training/CRC/fast-training controls, secondary packet enables and framing, DP audio N/M and readbacks, timestamp mode, MSE rate/SAT programming and status, MSA timing parameters, MSO controls, DSC control, and GSP1 through GSP7 send/pending/deadline/any-line controls plus the GSP11 PPS bit in `DP1_DP_SEC_CNTL2`.

## Important APIs, Types, And Macros

The important interface is the generated naming contract:

- `<register>__<field>__SHIFT` gives the field bit offset inside a 32-bit register.
- `<register>__<field>_MASK` gives the mask for that field.
- `// addressBlock: ...` and `//REGISTER_NAME` comments delimit generated register groups but are not compiled APIs.
- Instance prefixes in this chunk include `OTG3`, `HPD0` through `HPD4`, `DP0`, `DIG0`, and `DP1`; shared or unindexed OPTC names include `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`.

The OPTC fields integrate with timing-generator register tables such as `dcn10_optc.h`, `dcn30_optc.h`, and `dcn314_optc.h`. These headers map `GSL_SOURCE_SELECT` and `DWB_SOURCE_SELECT` fields into `dcn_optc_shift`/`dcn_optc_mask` structures, and runtime functions update GSL ready-source selection and DWB source muxing through the register helper layer. The ODM memory-power fields are also pulled into DCN31-family hardware-sequencer register lists in `display/dc/resource/dcn31/dcn31_resource.c`.

The HPD fields integrate with `display/dc/gpio/hpd_regs.h`, DCN GPIO hardware factories, and IRQ services such as `irq_service_dcn314.c`, `irq_service_dcn315.c`, and related DCN-family files. IRQ tables bind `HPD*_DC_HPD_INT_STATUS` as HPD and HPD RX interrupt status registers; link and GPIO paths use HPD control, sense, debounce, and enable fields to detect and filter hotplug events.

The DP and DIG fields are consumed by link-encoder and stream-encoder register lists. `display/dc/dio/dcn10/dcn10_link_encoder.h` maps DP link, DPHY, MSE SAT, secondary-packet, stream-enable, and HPD fields into `dcn10_link_enc_registers` and mask/shift structures. `display/dc/dce/dce_stream_encoder.h` and `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` map DP pixel format, MSA timing/colorimetry, MSE rate, secondary-packet, audio, DSC, metadata, HDMI, AFMT, TMDS, and DIG FIFO fields into stream-encoder objects.

`display/dmub/src/dmub_dcn31.c` includes `dcn_3_1_2_sh_mask.h` directly for DMUB-side DCN31-family register definitions. DCN 3.1/3.1.2 resource code includes the generated offset and shift/mask headers, builds static register, shift, and mask tables, and passes those tables to constructors for timing generators, link encoders, stream encoders, HPD objects, DIO, and hardware sequencing.

## Functional Field Groups

The OTG and OPTC fields describe timing-generator and output-pipe coordination state. DRR fields bound vertical-total changes and trigger timing for variable refresh behavior. `OTG_DSC_START_POSITION` coordinates compressed-stream start timing. Pipe-update status exposes pending flip, DC register update, cursor update, and vupdate keepout status. GSL source fields select which pipe readiness signals participate in global-swap-lock synchronization. DWB source selection routes OPTC output to writeback instances.

The ODM memory-power fields provide explicit power controls and readback for multiple ODM memories. `ODM_MEM*_PWR_FORCE` and `ODM_MEM*_PWR_DIS` are per-memory controls; `ODM_MEM_UNASSIGNED_PWR_MODE` and `ODM_MEM_VBLANK_PWR_MODE` set policy for unassigned or vblank periods; `ODM_MEM*_PWR_STATE` exposes current state. These fields are used by DCN hardware sequencing around init, mode changes, blanking, and power management.

HPD fields provide the low-level connector presence and interrupt surface. Status exposes raw and delayed sense, HPD interrupt status, RX interrupt status, and filter timer values. Control fields acknowledge interrupts, set polarity, enable HPD and RX interrupts, configure connection/RX timers, and enable fast-training handoff behavior after connect. Toggle filter controls debounce connect and disconnect transitions.

The DP link and DPHY fields program physical/link-layer behavior: lane count, link-training-complete, training pattern, bypass/test selection, PRBS, scrambler behavior, symbol pattern registers, 8b/10b controls, CRC source/result, MST CRC slot windows, HBR2 eye/pattern controls, fast-training timing/state, and BS/SR swap sequencing. These fields sit under link training, compliance testing, CRC diagnostics, and MST setup.

The DP stream and MSA fields program stream presentation: pixel encoding, component depth, dynamic and YCbCr range, MSA misc/colorimetry, VBID, timing totals/start/sync/active dimensions, video M/N generation, stream enable/status/deferred-disable, FIFO reset, and video interrupt controls. Incorrect values here affect sink timing interpretation, color format, stream enable sequencing, and audio/video packet alignment.

The DP secondary-data, audio, MST, MSO, DSC, metadata, ALPM, and GSP fields provide packetized sideband behavior. Secondary controls enable audio/sample, timestamp, ACP, ISRC, MPG, generic stream packets, and GSP slots; `DP_SEC_CNTL2` through later registers control per-GSP send, pending, deadline-missed, any-line, and line-number behavior. MSE rate and SAT fields configure MST payload bandwidth and slot allocation. MSO controls split SST links. DSC fields select DSC mode, slice width, and bytes-per-pixel. Metadata and ALPM fields support modern link features such as HDR/metadata packets and panel low-power modes.

The DIG0 HDMI/TMDS fields provide the HDMI and legacy digital-encoder surface. They control HDMI packet-generation version, deep color, scrambling, keepout, null/general/control/infoframe/VBI packet scheduling, audio packet and ACR timing, AFMT audio clock, TMDS control characters and DC balancing, output CRC/test patterns, FIFO calibration/status, and frontend/backend enable/source selection.

## Control Flow And State Behavior

This header has no direct control flow. Its macros become runtime behavior only after expansion into register tables and register helper calls. Resource initialization pairs addresses from the matching DCN 3.1.2 offset header with shifts/masks from this file. Later, hardware blocks use those tables to read and update memory-mapped registers.

The described hardware state persists in display-controller registers until driver writes, firmware activity, reset, power transitions, or hardware events change it. Configuration state includes DRR windows, DWB/GSL muxes, memory-power modes, HPD timers/enables, DP lane/pixel/MSA/link settings, secondary packet enables, MSE/MST allocation, DSC/MSO setup, HDMI packet controls, TMDS controls, and DIG source/enable fields. Status and telemetry include pipe-update pending bits, ODM memory power state, perfmon counters and interrupts, HPD sense/interrupt state, DP stream status, DPHY CRC results, fast-training status, MSE update pending/SAT status, DIG FIFO status, and HDMI/CRC readbacks.

Several covered groups are explicitly ordered or timing-sensitive. DRR and pipe update fields interact with vertical timing and keepout windows. GSL source selection must match the pipes participating in synchronized updates. ODM memory power should not be forced off while the corresponding output path is active. HPD interrupt ack, polarity, filter, and enable programming must preserve latched status and avoid spurious connect/disconnect detection. DP training, stream enable, MSA timing, secondary packet transmission, MST SAT updates, and DSC enable must follow the link and stream sequencing expected by the sink.

MST and packet state is double-buffered or pending in several places. MSE rate and SAT updates expose pending/keepout state and require waits or polling before subsequent payload changes. `DP_SEC_*_SEND_PENDING` and deadline-missed fields indicate packet scheduling state; tests and runtime code must distinguish a scheduled packet from a completed packet. HDMI generic/infoframe controls similarly have update and line-selection semantics that can affect when a changed packet becomes visible on the wire.

## Dependencies And Integration Points

This file must stay synchronized with `dcn_3_1_2_offset.h`. The offset header supplies `reg...` address symbols for the same register names, while this header supplies field layout. A mismatch can break compilation in generated register-list initializers or silently program the wrong bits if names still compile but the hardware specification has drifted.

The OPTC and HWSEQ consumers include `display/dc/optc/dcn10/dcn10_optc.h`, `display/dc/optc/dcn30/dcn30_optc.h`, `display/dc/optc/dcn314/dcn314_optc.h`, and DCN31-family resource/hardware-sequencer setup. Runtime functions in OPTC and HWSEQ code use the GSL, DWB source, and ODM memory-power masks during synchronized update setup, writeback routing, and display memory power policy programming.

The HPD consumers include GPIO hardware factories, `display/dc/gpio/hpd_regs.h`, IRQ services, and link-encoder HPD helper paths. HPD status and control masks are central to connector detection, HPD RX interrupt processing, debounce timing, and AUX/HPD association.

The DP link-layer consumers include `display/dc/dio/dcn10/dcn10_link_encoder.h` and `display/dc/dce/dce_link_encoder.c`. Those paths program DP DPHY training, scrambler, PRBS, link framing, stream enable, MST SAT allocation, fast training, and HPD-related link state using the DP0 base field names from this generated header and per-instance register addresses.

The stream-encoder consumers include `display/dc/dce/dce_stream_encoder.h`, `display/dc/dce/dce_stream_encoder.c`, `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h`, and `display/dc/dio/dcn30/dcn30_dio_stream_encoder.c`. These paths program DP pixel format, MSA, M/N generation, secondary packet controls, HDMI infoframes, audio and ACR, AFMT, DIG FIFO, DSC packet state, metadata, and TMDS behavior.

The perfmon fields are generated diagnostic metadata. They may be used by register dumps, debug tooling, firmware-assisted diagnostics, or future instrumentation through the standard display register helper layer; correctness still matters because a wrong counter control or readback mask can mislead performance and interrupt analysis.

## Risks And Edge Cases

Generated-header drift is the main risk. An incorrect shift or mask can corrupt unrelated fields in the same 32-bit register, causing display timing instability, bad color format, failed link training, lost HPD events, broken audio/infoframes, MST payload allocation failures, DSC/MSO misprogramming, writeback source routing errors, or misleading diagnostic counters.

The chunk boundaries split logical hardware blocks. The OTG3 interrupt status register is partially in the previous chunk, and DP1 continues in the next chunk. Merge/reconciliation must not treat this chunk alone as complete coverage for OTG3 or DP1.

HPD status/control registers mix latched event bits, sense readback, ack bits, polarity, enables, and timers. Full-register writes or stale masks can accidentally acknowledge events, invert polarity handling, disable RX interrupts, or shorten debounce windows enough to create hotplug flapping.

DP link training and compliance fields are sensitive to ordering and sink capabilities. Training pattern selection, scrambler state, lane count, PRBS/test patterns, fast-training timers, and link-training-complete state must align with AUX/DPCD negotiation. Bad masks can pass normal modes but fail CTS, MST, fast-training, or HBR2 diagnostic cases.

MST/MSE programming has pending and keepout semantics. Updating SAT slots or MSE rate without respecting `DP_MSE_RATE_UPDATE_PENDING`, `DP_MSE_SAT_UPDATE`, and `DP_MSE_16_MTP_KEEPOUT` can create transient payload mismatches, bandwidth drops, or stream corruption.

Secondary packet and HDMI packet controls are stateful and line-timed. Wrong send, continuous, line-reference, any-line, or deadline fields can drop HDR/AVI/audio/GSP/ISRC packets, send them on the wrong line, or report missed deadlines. Some failures appear only as sink-side feature loss rather than a driver error.

DIG FIFO, CRC, and perfmon fields are diagnostic but still stateful. Tests must clear or acknowledge status before measuring, choose the intended read selector/source, and avoid interpreting stale CRC/perfmon/FIFO extrema as current behavior.

ODM and DIO memory-power controls can cause mode-change or suspend/resume-only failures. Forcing memories off while scanout, writeback, or output-merger paths are active can produce intermittent blanking, underflow-like symptoms, or bad wake behavior.

## Test Signals

Build-time coverage should catch missing or renamed macros in DCN31/312 include paths, OPTC/HWSEQ tables, HPD register lists, link-encoder masks, and stream-encoder masks. High-signal failures include missing `OTG3_*`, `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `ODM_MEM_PWR_CTRL3`, `HPD0_*`, `DP0_*`, `DIG0_*`, or `DP1_*` field names referenced by register-list macros.

Runtime HPD validation should exercise connect/disconnect and HPD RX interrupts across HPD0 through HPD4, including debounce timing, interrupt ack, polarity, delayed sense, and fast-training delay controls. Expected signals are stable connector detection, no interrupt storms, correct HPD RX handling, and accurate delayed sense readback.

DP link validation should cover SST and MST modes on DP0 and DP1 where routed, link training at multiple rates/lane counts, DPHY CRC, PRBS/compliance patterns, HBR2 pattern control, fast training, scrambler behavior, and stream enable/deferred-disable sequencing. Useful signals include successful modesets, no unexpected stream-status drops, correct CRC/test-pattern behavior, and passing CTS-style link tests.

MST and sideband packet validation should cover MSE rate programming, SAT slot allocation/status, SAT update pending/keepout waits, secondary packet enables, GSP send/pending/deadline status, HDR/metadata packets, ISRC/MPG, and DSC PPS/GSP11 behavior. Register dumps should show coherent MSA timing, MSE allocation, and packet scheduling state.

HDMI/DIG validation should cover HDMI deep color and scrambling, AVI/audio infoframes, generic packets, ACR N/CTS programming and readback, audio packet generation, TMDS controls, output CRC/test patterns, and DIG FIFO status. Expected signals are stable HDMI output, correct sink-reported packet/audio state, no FIFO error flags after clear, and matching CRC results for known frames.

Power-management validation should exercise blanking, mode changes, suspend/resume, writeback source changes, and ODM memory-power modes. Signals include correct ODM memory-power status, no blanking or corruption during vblank power policy changes, and no regressions in synchronized update/GSL paths.
