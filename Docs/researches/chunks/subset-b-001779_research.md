# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h lines 5261-7902

## Scope

This chunk is a generated DCN 3.0.3 register offset slice from `dcn_3_0_3_offset.h`. It contains only preprocessor constants: register-address macros and matching `*_BASE_IDX` macros, plus comment markers for register address blocks. There are no C functions, structs, enums, or executable statements in this range.

The range starts in the tail of the `DIG1` HDMI/TMDS encoder block, covers `DP1`, DCIO, GPIO, DSC0/DSC1, writeback, MPC/MPCC/OGAM, HPO HDMI stream encoder, ABM0/ABM1, HDA/Azalia controller and codec-indexed blocks, VGA indexed registers, Azalia stream-indexed windows 0-15, and Azalia endpoint indexed windows 0-3. The final `azf0endpoint3_endpointind` block is truncated by the chunk boundary at `AUDIO_DESCRIPTOR1`, so the next chunk or file-level merge must account for the rest of that endpoint block.

## Purpose And Hardware Surface

The file is part of the low-level ABI between AMDGPU Display Core and DCN 3.0.3 display hardware. Each `mm*` macro gives an MMIO register offset, each `ix*` macro gives an indirect-index register offset, and each `*_BASE_IDX` macro selects the register base aperture used by AMDGPU register access helpers. The constants are paired with the companion `dcn_3_0_3_sh_mask.h` field definitions so driver code can combine address, mask, shift, and base index for register read/modify/write operations.

Major hardware areas in this chunk:

- `DIG1` tail: HDMI audio clock regeneration/status, AFMT control, digital backend enable/control, TMDS control characters, feedback, sync/DC balance, DIG version, lane enable, and force-disable offsets.
- `dce_dc_dio_dp1_dispdec`: DisplayPort link, pixel format, MSA, stream, steer FIFO, DPHY, CRC, fast training, secondary-data packet, audio `M/N`, MSE/MST scheduling, MSO, DSC, metadata, ALPM, and GSP offsets for the DP1 encoder.
- `dce_dc_dcio_dcio_dispdec` and `dce_dc_dcio_dcio_chip_dispdec`: DCIO generic registers, reference clocks, UNIPHY link/xbar, panel power sequencing, backlight PWM, GSL/swaplock pads, DCIO reset, generic/DDC/AUX/HPD GPIO masks/data/enables/readbacks, receive enables, and mutexes.
- `dce_dc_dsc0*` and `dce_dc_dsc1*`: DSC top/control, DSCCIF config, DSCC configuration/status/interrupts, PPS configuration registers 0-22, memory power control, squared-error/max-error/rate-buffer diagnostics, debug index/data buses, and DSC-local perfmon blocks.
- `dce_dc_wb0*`: DWB top controls, flow control, CRC, backpressure, host-read, overflow, soft reset, writeback perfmon, and DWB color-processing registers for HDR multiplier, gamut remap matrices, output gamma LUTs, RAM A/B piecewise regions, and debug access.
- `dce_dc_mpc*`: MPCC0/1 mux/alpha/top/bottom controls, MPCC status, MPCC output gamma and gamut remap banks, MPC global clock/reset/CRC/background/denorm/configuration registers, output CSC, RMU 3D LUT and shaper controls, and MPC perfmon.
- `dce_dc_hpo*`: HPO HDMI AFMT packet/audio/infoframe control, VPG generic packet access/status, DME control/memory control, HPO top clock control, and HPO perfmon.
- `dce_dc_opp_abm0_dispdec` and `dce_dc_opp_abm1_dispdec`: Adaptive backlight management and PWM state for two ABM instances, including ambient/user/target/current levels, final/min duty cycle, ACE slopes/thresholds, luma statistics, histogram controls/results, sample rates, and master lock.
- `dce_dc_hda_*`, `az*`, `azf0stream*`, and `azf0endpoint*`: HDA command/response ring registers, stream/endpoint control windows, codec parameter and converter/pin-control offsets, audio descriptors, sink info, CRC result indices, and per-stream/endpoint indirect register maps.
- `vga_*ind`: legacy VGA sequencer, CRT, graphics, and attribute-controller indirect register offsets.

## Important APIs, Types, And Definitions

There are no callable APIs or types here. The usable surface is the macro naming contract:

- `mmNAME` defines a direct MMIO register offset, for example `mmDP1_DP_LINK_CNTL`, `mmDSCC0_DSCC_CONFIG0`, `mmDWB_ENABLE_CLK_CTRL`, `mmMPC_CLOCK_CONTROL`, or `mmABM0_BL1_PWM_AMBIENT_LIGHT_LEVEL`.
- `mmNAME_BASE_IDX` defines the base-aperture index for that direct register. This chunk uses base index `2` for much of DIO/DCIO/DSC/writeback, base index `3` for MPC/HPO/ABM blocks, and base index `0` for HDA controller-style registers.
- `ixNAME` defines an indirect register index rather than a direct MMIO address. This is used for VGA indexed registers and Azalia codec/stream/endpoint index spaces.
- `// addressBlock:` and `// base address:` comments identify generated register blocks and instance offsets. They are not compiled, but they are important for humans and for comparing the generated header with ASIC register specifications.

Important repeated macro families:

- DP1 offsets include link/stream configuration (`DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`), training/PHY controls (`DP_DPHY_*`, `DP_HBR2_EYE_PATTERN`, fast training status), packet/audio controls (`DP_SEC_*`, `DP_SEC_AUD_N/M`, timestamp), MST/MSE controls (`DP_MSE_*`), DSC/MSO controls (`DP_DSC_CNTL`, `DP_MSO_CNTL*`), and metadata/ALPM/GSP controls.
- DSC0 and DSC1 are parallel instances. Both expose top, DSCCIF, DSCC, `PPS_CONFIG0` through `PPS_CONFIG22`, rate-buffer diagnostics, error counters, debug index/data, and perfmon offsets. Instance 1 has the same logical layout shifted by its block base.
- DWB top and DWBCP offsets split capture plumbing from color processing. The top block handles enable, flow, window/source sizing, CRC, overflow, reset, and backpressure. The DWBCP block contains HDR multiplier, gamut remap matrices, OGAM LUT index/data/control, per-channel RAM A/B slope/base/end/offset/region registers, debug controls, and gamut remap A/B matrix coefficients.
- MPCC0 and MPCC1 contain per-compositor-combiner controls, while MPCC_OGAM0 and MPCC_OGAM1 mirror large output gamma/gamut-remap banks for two MPCC OGAM instances. MPC CFG/OCSC/RMU then provide global composition, output color space conversion, and 3D LUT/shaper state.
- Perfmon blocks use the same register pattern across DSC, writeback, MPC, and HPO: `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`.
- HDA/Azalia direct registers include CORB/RIRB pointers and base addresses, wall clock, codec read/write command/data, stream control/status, CRC controls, and endpoint index/data windows. The `ixAZF0STREAM*` and `ixAZF0ENDPOINT*` families then define the per-stream and per-endpoint codec register indices addressed through those windows.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior appears only when included C code uses these offsets through AMDGPU's register helper layer. A typical path is:

1. DCN 3.0.3-specific code includes `dcn_3_0_3_offset.h` and `dcn_3_0_3_sh_mask.h`.
2. Resource, IRQ, DMUB, or block-specific register tables bind symbolic names to offsets, base indices, shifts, and masks.
3. Runtime code calls helpers such as `REG_GET`, `REG_SET`, or `REG_UPDATE` through per-block register structures.
4. The hardware register state persists in MMIO or indirect-indexed register files until overwritten, acknowledged, power-gated, reset, or changed by firmware/hardware.

The state represented by this chunk is hardware-backed:

- DP1 state controls active link formatting, training, stream timing, MSA/MST/MSO/DSC metadata, audio secondary packets, and diagnostic CRC/training status.
- DCIO/GPIO state controls physical display IO resources: reference clocks, lane routing, panel sequencing, backlight PWM, AUX/DDC/HPD GPIO ownership, and reset/pad behavior.
- DSC state controls display stream compression programming, PPS payloads, memory power, interrupt/status behavior, and compression diagnostics.
- DWB and DWBCP state controls capture/writeback enablement, flow/window sizing, CRC and overflow reporting, output color transforms, and output gamma LUT contents.
- MPC/MPCC/OGAM/OCSC/RMU state controls compositor routing, alpha/blending, output color conversion, output gamma, gamut remap, 3D LUT, CRC, and performance counters.
- HPO/AFMT/VPG/DME state controls high-performance HDMI packet generation, audio/infoframe routing, generic packets, DME memory/control, clocks, and perfmon counters.
- ABM state tracks brightness policy inputs, PWM output levels, luma/histogram samples, ACE configuration, sample rates, and register-lock state.
- HDA/Azalia state includes host command/response rings, stream formatting and routing, endpoint pin/converter controls, audio descriptors, sink information, hotplug/unsolicited response controls, CRC readbacks, and format/audio-enable interrupt statuses.
- VGA and Azalia `ix*` definitions are indirect-indexed state rather than independent direct MMIO registers; callers must select the correct index/data window before reading or writing.

The macros themselves do not encode ordering, locking, range checks, or ownership. Callers must still sequence programming according to the hardware block rules, such as disabling a stream before reprogramming DP link state, respecting panel/backlight power sequencing, loading DSC PPS registers coherently, updating writeback or gamma LUTs at safe update points, and using HDA command/response rings in the expected producer/consumer order.

## Dependencies And Integration Points

This header is consumed by DCN 3.0.3 display code under `drivers/gpu/drm/amd/display`. In this tree it is included by:

- `display/dmub/src/dmub_dcn303.c`, together with `dcn_3_0_3_sh_mask.h`, for DCN303 DMUB register access.
- `display/dc/irq/dcn303/irq_service_dcn303.c`, together with the shift/mask header, for DCN303 IRQ-source register definitions.
- `display/dc/resource/dcn303/dcn303_resource.c`, together with the shift/mask header, for DCN303 resource/block register tables.

The important dependencies are:

- The companion `dcn_3_0_3_sh_mask.h` field macros. Offset macros identify registers; field masks/shifts define how to manipulate bits inside those registers.
- AMDGPU Display Core register helper macros and generated register structures. These helpers combine register offset, base index, field mask, and field shift.
- DC block implementations for DP/DIO, DCIO/GPIO, DSC, writeback, MPC/MPCC, HPO HDMI, ABM, and audio. The blocks rely on stable macro names to initialize per-instance register lists.
- Linux DRM/AMDGPU interrupt, hotplug, modeset, audio, writeback, color-management, and diagnostics paths that indirectly program the registers represented here.
- ASIC register generation inputs. Because this is generated data, the authoritative source is the hardware register specification, not local hand-written logic.

## Risks And Maintenance Notes

- Numeric drift is the main risk. A single wrong offset or base index can make a valid register helper access a different hardware register, which may silently corrupt unrelated display state.
- Instance symmetry is dense. DP, DSC, ABM, MPCC OGAM, stream, and endpoint blocks repeat similar names with instance numbers. Copying an offset or base index across instances without validating the generated value can break only one pipe/stream/endpoint and be hard to isolate.
- Direct `mm*` and indirect `ix*` macros are not interchangeable. Using an `ixAZF0ENDPOINT*` or VGA indexed value as a direct MMIO address would target the wrong aperture.
- The chunk starts and ends mid-logical-block. `DIG1` context begins before line 5261, and endpoint3 continues after line 7902. File-level research must merge neighboring chunks before drawing complete per-block conclusions.
- Address and field definitions are split across headers. Updating an offset without the matching `*_sh_mask.h` field definitions, or vice versa, can compile but produce broken read/modify/write behavior.
- Hardware sequencing is external to this header. The constants allow access to reset, power, clock, panel, PWM, LUT, and audio command registers, but they do not prevent unsafe writes during active scanout, link training, capture, or codec command processing.
- HDA/Azalia and VGA blocks include overlapping index/data windows and legacy-style aliases. Read/write side effects depend on the selected index and on whether the access is through controller, endpoint, stream, or codec-indirect space.
- Many offsets touch visible-output behavior: backlight PWM, ABM, color matrices, gamma LUTs, DSC PPS, stream metadata, and audio routing. Misprogramming can cause black screens, visible color errors, link failures, audio loss, or interrupt storms.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware smoke coverage:

- Build AMDGPU with DCN 3.0.3 support and ensure all DCN303 resource, IRQ, and DMUB register tables compile against these macro names.
- Compare this header and `dcn_3_0_3_sh_mask.h` against the ASIC register source to verify each register has the expected offset, base index, and field layout.
- Exercise DP1 modesets, link training, MST/MSO/DSC paths, audio secondary-data packets, and metadata packet programming while checking for link-training, CRC, or packet-status errors.
- Test DCIO hotplug, AUX/DDC transactions, panel power sequencing, backlight PWM updates, and GPIO ownership/readback paths.
- Run DSC-enabled display modes on both DSC instances and check PPS programming, compression status, underflow/interrupt status, and DSC perfmon readback.
- Exercise writeback capture through DWB, including window/source sizing, overflow reporting, CRC, and DWB color-processing/LUT paths.
- Validate MPC/MPCC color-management paths with blend, OCSC, OGAM, gamut remap, shaper, and 3D LUT programming, including CRC or visual test patterns where available.
- Exercise HPO HDMI AFMT/VPG/DME packet generation and HPO perfmon counters.
- Test ABM0/ABM1 brightness transitions, ambient/user/target level updates, histogram/luma statistics, and register-lock behavior.
- Validate HDA/Azalia audio playback, stream format changes, endpoint pin sense/hotplug, unsolicited responses, audio descriptor/sink-info access, and codec command/response ring behavior.

## Chunk-Specific Summary

Lines 5261-7902 define register offsets and base indices for a broad DCN 3.0.3 display hardware surface rather than executable behavior. The most important responsibilities in this slice are DP1 link/packet/audio state, DCIO/GPIO/panel/backlight control, DSC0/1 compression programming, writeback and DWB color processing, MPC/MPCC color and composition state, HPO HDMI packet generation, ABM brightness policy, and HDA/Azalia/VGA indirect register maps. Correctness depends on exact generated offsets, correct base-index selection, and consistent use with companion shift/mask definitions and block-specific register access sequencing.
