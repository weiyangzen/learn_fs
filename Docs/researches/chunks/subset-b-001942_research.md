# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 32543-34940

## Scope

This chunk is a generated DCN 3.2.0 register-field shift/mask slice. It contains preprocessor constants only: 2,172 `#define` entries in this range, split almost evenly between 1,088 `_SHIFT` macros and 1,084 `_MASK` macros. There are no C functions, structs, enums, executable branches, allocations, locks, or direct MMIO operations in this chunk.

The range starts in the middle of the `DP3` DisplayPort register family, at `DP3_DP_LINK_FRAMING_CNTL`, and continues through the rest of `DP3` secondary-data, DPHY, MST/MSO, DSC, GSP, double-buffer, and ALPM field definitions. It then covers the `dcn_dc_dio_dig3_dispdec` address block for `DIG3` frontend, HDMI, AFMT, backend, and TMDS fields. It covers the `dcn_dc_dio_dp4_dispdec` address block for `DP4`, including link, stream, DPHY, secondary packet, MST/MSO, GSP, and ALPM fields. The chunk ends in the start of the `dcn_dc_dio_dig4_dispdec` address block after the first `DIG4` frontend/FIFO/test-pattern/metadata definitions and at the beginning of `DIG4_HDMI_CONTROL`; the rest of `DIG4` is outside this chunk.

## Purpose And Hardware Surface

This header is part of the AMDGPU Display Core register ABI for DCN 3.2.0. The matching offset header names the MMIO registers; this file supplies bit positions and masks used to pack and unpack fields within those registers. Runtime display code normally consumes these constants indirectly through register helper macros and generated register table initializers rather than by spelling every raw macro at each call site.

Major hardware areas represented here:

- `DP3` link/stream controls: link framing, MSA/VBID timing, video interrupt status, DPHY training/test/CRC/scrambler/FEC controls, fast training status, secondary-data packet controls, audio M/N values, MST slot allocation tables, MSO controls, DSC enable, metadata transmission, double-buffer status, GSP8-GSP11 controls, and AUX-less ALPM timing.
- `DIG3` digital front/backend controls: source selection, stereo sync, bypass/pixel selection, Dolby Vision enable/status, output CRC, test/random patterns, FIFO calibration and error state, AFMT enable, backend enable, force-disable, and version fields.
- `DIG3` HDMI packet generation: metadata packet scheduling, HDMI mode control/status, audio delay, ACR packet generation and readback, VBI and infoframe controls, generic packet send/line/checksum windows, generic packet data buffer control, and general-control packet fields.
- `DIG3` TMDS controls: control characters, feedback, stereo sync selection, sync character patterns, control bits, DC balancer behavior, sync DC-balance character, and generated TMDS control symbols.
- `DP4` link/stream controls: a nearly parallel instance to the DP3 definitions, with link status/training, pixel format, MSA colorimetry/misc fields, stream enable/status, steer FIFO overflow/TU size, DPHY controls, secondary packets, MST/MSO allocation, DSC, metadata, GSP, double-buffer, and ALPM/AUX-less ALPM controls.
- `DIG4` opening controls: frontend source/bypass/pixel/Dolby Vision selection, output CRC, test/random pattern, FIFO enable/reset/calibration/error, HDMI metadata packet control, and the first `DIG4_HDMI_CONTROL` fields.

## Important Definitions

The generated naming convention is consistent across the chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for that field.
- `//<REGISTER>` comments group the fields for one register.
- `// addressBlock: ...` comments mark hardware block boundaries, including `dcn_dc_dio_dig3_dispdec`, `dcn_dc_dio_dp4_dispdec`, and `dcn_dc_dio_dig4_dispdec` in this range.

Important macro families visible in the chunk:

- `DP3_DP_DPHY_*` and `DP4_DP_DPHY_*` define DisplayPort physical-layer controls for FEC, scrambler selection, bypass/skew bypass, training pattern selection, programmable symbols, 8b10b reset/disparity, PRBS generation, scrambler control, CRC selection/results, MST CRC slot windows, and fast training start/status. These fields are sensitive because they control link training, compliance patterns, diagnostics, and FEC-related behavior.
- `DP3_DP_SEC_*` and `DP4_DP_SEC_*` define secondary-data packet controls: stream enable, audio sample/timestamp/ACM/AIP/ASP/ATP/GSP/MPG enables, GSP line references, priorities, send/pending/deadline bits, framing packet bytes, audio M/N readback and programming, packet insertion position, metadata transmission, and extended GSP8-GSP11 controls.
- `DP3_DP_MSE_*` and `DP4_DP_MSE_*` define MST/MSE rate and slot-allocation state. `SAT0`, `SAT1`, `SAT2`, and matching status registers encode stream source, slot count, start slot, and update-pending fields for multiple virtual channels.
- `DP3_DP_MSO_*` and `DP4_DP_MSO_*` define multi-stream or split-output controls such as MSO enable, segment count, source select, MST enable, link count, OD start, HBlank masking, and secondary-stream pipe/source assignment.
- `DP3_DP_ALPM_CNTL`, `DP4_DP_ALPM_CNTL`, and `DP*_DP_AUXLESS_ALPM_CNTL1-5` define low-power main-link sleep/standby and AUX-less wake/FEC scheduling: send/pending bits, immediate control, LFPS symbol/cycle counts, wakeup and FEC line numbers, lock period, hardware mode, frame count, interrupt mask/status/clear, and wakeup frame/line reporting.
- `DIG3_DIG_FE_CNTL` and `DIG4_DIG_FE_CNTL` define digital frontend source routing, stereo sync, digital bypass, pixel grouping/input selection, Dolby Vision enable/metadata missed status, frontend symbol clock status, and TMDS pixel/color formatting. These are the bridge between the display pipe and DP/HDMI encoder instance.
- `DIG3_HDMI_*` macros define the HDMI packet generator and status surface. Notable groups include `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL0/1`, `HDMI_GENERIC_PACKET_CONTROL0/1/2/3/4/5/6/7/8/9/10`, `HDMI_DB_CONTROL`, ACR N/CTS registers for 32/44.1/48 kHz families, and ACR status readback.
- `DIG3_TMDS_*` macros define TMDS serializer state and control-symbol generation: character values, feedback, stereo sync control selection, sync pattern words, control bits, DC balancer enable/reset/test controls, DC-balance sync character, and generated control symbols for control lanes 0-3.
- `DIG3_DIG_FIFO_CTRL*` and `DIG4_DIG_FIFO_CTRL*` define frontend FIFO enable/reset, read start level, clock source, output pixel mode, reset done, error flags, overwrite/calibrated levels, min/max tracking, and recalculation/recompare controls.

The repeated-instance pattern is important: `DP3` and `DP4` carry substantially parallel field sets for two display/link instances, while `DIG3` and `DIG4` carry digital encoder frontend/backend fields for corresponding DIO instances. Compile-time symbol names encode the instance, so using a valid field from the wrong instance can still compile if the register table maps it incorrectly.

## Control Flow And State Behavior

This chunk has no executable control flow. Runtime behavior arises when Display Core code includes `dcn_3_2_0_sh_mask.h`, combines these field constants with register offsets from `dcn_3_2_0_offset.h`, and uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `SF(...)`, `SRI(...)`, `SE_SF(...)`, and register-list macros to access MMIO.

Typical runtime flow using these definitions:

1. DCN 3.2 resource construction includes the DCN 3.2.0 offset and mask headers and initializes stream/link encoder register tables. In `display/dc/resource/dcn32/dcn32_resource.c`, `SE_COMMON_MASK_SH_LIST_DCN32(__SHIFT/_MASK)` and link-encoder mask lists populate typed shift/mask structures consumed by encoder objects.
2. Modeset and stream enable paths select DIG frontend sources, configure FIFO and pixel formatting, enable HDMI or DP packet generation, program audio/metadata/GSP secondary packets, and toggle stream/link status fields.
3. DP link training, compliance, and diagnostics paths use DPHY fields for training patterns, scrambler behavior, PRBS/test symbols, CRC selection/results, FEC enable/status, fast training start/status, and MST CRC status.
4. MST/MSO paths program MSE rate, SAT slot allocation, MSO segmentation and source routing, then use update-pending/status fields to synchronize hardware state.
5. HDMI paths program ACR, audio, VBI, infoframe, metadata, generic packet, general-control, and TMDS fields, then monitor HDMI status/error and ACR status readback.
6. Low-power display paths use ALPM and AUX-less ALPM fields to schedule main-link sleep, standby, wakeup, FEC timing, interrupt handling, and hardware-mode transitions.

The state described by this chunk is hardware register state:

- Persistent programmed state includes DP stream framing, MSA/VBID timing, lane count, DPHY training/test/scrambler/CRC/FEC controls, secondary packet enables and line references, GSP send policy, MST slot allocation, MSO routing, DSC enable, ALPM timing, DIG source selection, HDMI packet scheduling, TMDS symbols, FIFO thresholds, and output CRC/test-pattern controls.
- Volatile readback includes link training/status, DPHY FEC active/ready status, CRC valid/results, MST phase/error status, fast-training complete/status, GSP send pending/deadline-missed flags, MSE update pending and SAT status, double-buffer pending status, ALPM pending/interrupt/frame/line status, FIFO reset/error/calibration status, HDMI packet/error status, ACR status, Dolby Vision metadata missed, and output CRC results.
- Side-effecting fields include interrupt ack/clear bits, overflow acknowledgements, stream disable ack, fast-training complete ack, CRC enable/reset-like controls, send triggers for secondary/GSP/HDMI packets, double-buffer update controls, ALPM wake/sleep sends and interrupt clear, FIFO reset/recalibration/recompare controls, HDMI error ack, and TMDS/random-pattern resets.

There is no persistence to disk or driver-owned durable storage. Any persistence is in the hardware register programming across display operations until reset, power-gating, suspend/resume, hotplug reconfiguration, or another modeset overwrites the values.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across AMD's DCN 3.2.0 register header set. The field names here must match the register names in `dcn_3_2_0_offset.h` and the typed Display Core register tables. Missing macros generally fail at compile time; incorrect numeric values can compile and produce runtime-only display, audio, link, or power-management faults.

Known consumers and integration paths include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, which includes `dcn/dcn_3_2_0_offset.h` and `dcn/dcn_3_2_0_sh_mask.h`, then constructs DCN32 stream/link encoder shift and mask tables from generated mask-list macros.
- `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.c` and related DIO stream encoder headers, which implement DP/HDMI stream encoder behavior using the per-instance register, shift, and mask tables initialized from these generated fields.
- `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.c` and `dcn31` link encoder infrastructure, where link encoder register helpers use generated masks for physical link, training, and transmitter state.
- `drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`, which includes this header for DCN32 interrupt source wiring and status/ack fields.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`, which includes the header for firmware/display microcontroller register interactions on DCN32 hardware.
- GPIO, clock manager, resource, and amdgpu memory-controller files that include the same DCN32 generated headers to share the register ABI for the ASIC.

This chunk is also tightly coupled to sibling generated headers for nearby ASIC generations, such as `dcn_3_2_1_sh_mask.h` and `dcn_3_5_1_sh_mask.h`, which carry many similarly named DP/DIG fields with generation-specific differences. Cross-generation copy/paste or table reuse needs explicit verification because fields such as Dolby Vision bits, embedded panel mode, back-to-back BS avoidance, ALPM controls, and generic packet windows can differ subtly between generations.

## Risks And Maintenance Notes

- Numeric mask/shift drift is the main risk. A wrong bit position for link training, FEC, scrambler, MST slot allocation, ALPM timing, HDMI packet scheduling, or TMDS control can compile cleanly while breaking only on real DCN 3.2.0 hardware.
- Repeated instance families create copy-generation hazards. `DP3` and `DP4` are very similar but not identical at the chunk boundaries, and `DIG3`/`DIG4` share frontend/FIFO definitions while this range contains all of `DIG3` and only the start of `DIG4`.
- Side-effecting ack/clear/send/reset fields are especially sensitive. Incorrect masks can drop interrupts, repeatedly send stale packets, miss GSP deadline failures, fail to clear HDMI or ALPM events, leave FIFO reset asserted, or acknowledge the wrong status bit.
- DisplayPort link-training and DPHY fields are hardware-timing sensitive. Errors may only appear with specific lane counts, link rates, FEC states, MST, fast training, compliance/test patterns, or after suspend/resume.
- MST/MSO and SAT fields are bandwidth and topology sensitive. Slot-allocation or update-pending field mistakes can cause flicker, blank streams, wrong stream-to-slot mapping, or failures only with MST hubs and multi-stream displays.
- HDMI infoframe/generic-packet controls are user-visible but mode-specific. Bad line-reference, send/continuous, checksum, DB-enable, or data-register masks can break HDR metadata, audio infoframes, vendor packets, or Dolby Vision metadata without affecting basic modes.
- ALPM and AUX-less ALPM fields affect low-power link behavior. Incorrect wake/sleep timing or interrupt fields can cause black screens, delayed wake, unnecessary power use, or intermittent failures around panel self refresh, replay-like flows, idle transitions, and hotplug.
- The chunk begins after the start of the `DP3` register block and ends before the full `DIG4` register block. Final per-file synthesis must merge neighboring chunks before claiming complete coverage of either the full header or full DIG/DP instance families.

## Test Signals

Useful validation should combine build-time generated-header checks with DCN32 hardware behavior:

- Build AMDGPU Display Core with DCN 3.2 support and ensure all stream/link encoder, IRQ, DMUB, GPIO, resource, and clock-manager consumers resolve the generated `DP3`, `DP4`, `DIG3`, and `DIG4` field names.
- Run generated-register consistency checks for this range: every field should normally have paired `_SHIFT` and `_MASK` macros; masks should fit 32-bit register width; fields within each register should not overlap unexpectedly; repeated `DP3`/`DP4` and `DIG3`/`DIG4` families should match the authoritative register database where intended.
- Exercise DP link training across link rates, lane counts, FEC on/off, fast training, compliance test patterns, PRBS/scrambler settings, and CRC diagnostics on connectors backed by the DP3/DP4 instances.
- Test MST and MSO paths with multi-stream topologies, slot-allocation updates, stream enable/disable, DSC on/off, and hotplug while monitoring MSE SAT status, update-pending fields, stream status, and underflow/flicker symptoms.
- Validate DP secondary data and GSP handling with audio, HDR metadata, adaptive sync metadata, DSC PPS/GSP paths, and metadata transmission timing; watch pending/deadline-missed bits and double-buffer status.
- Exercise HDMI modes on the DIG3 path, including deep color, scrambling, audio ACR at 32/44.1/48 kHz families, general-control packets, AVI/audio/MPEG infoframes, generic packets, HDR/Dolby Vision metadata, and VBI packets.
- Check TMDS-specific behavior on HDMI/DVI-style modes: control symbols, DC balancer, sync patterns, pixel encoding/color format, and stereo sync selection.
- Stress ALPM/AUX-less ALPM transitions with idle, display blank/unblank, panel power events, suspend/resume, link retraining, and hotplug; monitor wake/sleep pending bits, interrupt status/clear, wake frame/line reporting, and black-screen or delayed-wake failures.
- Use output CRC, DPHY CRC, MST CRC phase/status, FIFO error/reset-done/calibrated state, HDMI error status, ACR status, GSP deadline-missed fields, and ALPM interrupt state as diagnostics before and after modeset, packet, and power transitions.

## Chunk-Specific Summary

Lines 32543-34940 define DCN 3.2.0 bit shifts and masks for the tail of `DP3`, the full `DIG3` DIO/HDMI/TMDS block, the `DP4` DisplayPort block, and the beginning of `DIG4`. The content is generated register ABI rather than executable driver logic. Correctness depends on exact field values, instance-prefix consistency, safe handling of side-effecting status/ack/send/reset bits, and validation across DisplayPort link training, MST/MSO, DSC, secondary packets, HDMI packet generation, TMDS output, FIFO/CRC diagnostics, and ALPM low-power behavior.
