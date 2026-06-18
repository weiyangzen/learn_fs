# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 8100-10752

## Scope

This chunk is a middle slice of the generated AMD DCN 4.2.0 register offset header. It contains only preprocessor metadata: 2,369 `#define` lines, including 1,184 register-offset macros and 1,185 `_BASE_IDX` macros. The one extra base-index macro is the opening boundary line for `regCM3_CM_GAMCOR_RAMA_OFFSET_B_BASE_IDX`; its matching offset macro is immediately before this chunk. All visible `_BASE_IDX` values in this range select DCN base segment `2`.

The range starts inside the `CM3` color-management gamma-correction RAM definitions and ends on the `dce_dc_dio_dig1_dme_dme_dispdec` address-block comment/base-address pair. The actual `DME1` register definitions begin in the following chunk.

## Purpose

The file gives DCN 4.2 display code symbolic names for memory-mapped display ASIC register offsets and the SOC/DCN base segment used to form absolute register addresses. Runtime code combines `regFOO_BASE_IDX` with `ctx->dcn_reg_offsets[]` or compile-time `DCN_BASE__INST0_SEG*` constants and the `regFOO` offset through helper macros such as `SR`, `SRI`, `REG_OFFSET_EXP`, `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

This chunk covers several display-output-facing hardware areas:

- Tail of DPP3 color management: `CM3_CM_GAMCOR_RAMA/RAMB_*`, HDR multiplier, coefficient format, histogram lock/index/data/status, debug registers, and CM memory power/status.
- DPP3 display-performance monitoring through `DC_PERFMON13_*`.
- Display Core Output Hub sideband plumbing: DisplayPort AUX instances `DP_AUX0`-`DP_AUX4`, HPD instances `HPD0`-`HPD4`, DPIA mux instances `DPIA_MUX0`-`DPIA_MUX5`, PHY mux instances `PHY_MUX0`-`PHY_MUX4`, and DCOH top-level control/status registers.
- OPP/output formatting for pipes 0-3: `FMT<n>`, `DPG<n>`, `OPPBUF<n>`, `OPP_PIPE<n>`, `OPP_PIPE_CRC<n>`, OPP top registers, DSCRM instances, and `DC_PERFMON14_*`.
- Output timing/combine control: `ODM0`-`ODM3`, full `OTG0`-`OTG3` timing-generator register sets, OPTC miscellaneous registers, and `DC_PERFMON15_*`.
- DIO common, I2C/DDC, stream-mapper, and performance-monitor registers.
- DIG0 stream encoder and DP0 link encoder registers for HDMI, TMDS, DisplayPort main-link, secondary-data/audio packets, MSA, MST/MSE, MSO, ALPM, GSP, symbol counters, panel replay, and fast training.
- Start of DIG1 sideband/audio packet blocks: `VPG1` generic/ISRC packet registers and `APG1` audio-packet generator registers.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, includes, locks, allocations, callbacks, or executable statements in this range. The exported interface is the generated macro convention:

- `reg<REGISTER>`: the register offset used by DCN 4.2 register helpers.
- `reg<REGISTER>_BASE_IDX`: the index into the DCN base-address table. In this chunk, the value is consistently `2`.

Important macro families include:

- `regCM3_CM_GAMCOR_RAMA/RAMB_*`, `regCM3_CM_HDR_MULT_COEF`, `regCM3_CM_HIST_*`, and `regCM3_CM_MEM_PWR_*` for DPP pipe 3 color/gamma RAM programming, histogram access, and memory power state.
- `regDP_AUX<n>_*` for AUX software transactions, arbitration, interrupt control, low-speed status/data, AUX PHY transmit/receive control, wake control, and wake status.
- `regHPD<n>_DC_HPD_*` for hotplug interrupt/status/filter/toggle and RX interrupt/status registers.
- `regDPIA_MUX<n>_DPIA_MUX_CNTL` and `regPHY_MUX<n>_*` for USB4/DPIA and PHY routing selection/status.
- `regFMT<n>_*`, `regDPG<n>_*`, `regOPPBUF<n>_*`, `regOPP_PIPE<n>_*`, and `regOPP_PIPE_CRC<n>_*` for output formatter clamping, bit depth, dithering seeds, 4:2:0/4:2:2 handling, display-pattern generation, OPP buffering, and CRC capture/readback.
- `regODM<n>_ODM_*` and `regOTG<n>_*` for output data merger state and timing generator totals, sync/blanking, triggers, stereo/interlace, status counters, snapshots, update locks, vertical interrupts, CRC windows/results, static-screen, global sync, vstartup/vupdate/vready, dynamic refresh rate, request control, p-state, and encryption state.
- `regDC_I2C_*` and `regDIO_*` for DDC/I2C transactions, arbitration, DIO power/status/debug, and stream mapping.
- `regDIG0_*` and `regDP0_*` for DIG0 HDMI/TMDS and DP0 DisplayPort link programming, including HDMI info/audio/generic packets, ACR, DP DPHY training/scrambling/CRC, transfer-unit control, secondary-data/audio packet timing, MST/MSE, MSO, ALPM, GSP, symbol counters, and panel replay hooks.
- `regVPG1_*` and `regAPG1_*` for DIG1 generic video packets, ISRC access, audio packet control/debug, IEC 60958 debug registers, audio CRC, ramp generation, and APG memory power/status.

## Control Flow

This header has no local control flow. Runtime sequencing is imposed by AMDGPU display code that token-pastes these macro names into per-block register tables:

1. DCN42 resource, IRQ, GPIO, clock-manager, and DMUB files include `dcn_4_2_0_offset.h` together with `dcn_4_2_0_sh_mask.h`.
2. Register-list macros in block-specific headers are expanded by `SR`, `SRI`, `SRI_ARR`, `REG_OFFSET_EXP`, and related helpers to compute absolute MMIO addresses from `BASE(reg*_BASE_IDX) + reg*`.
3. Higher-level display paths use the generated register tables to program link discovery, AUX/DDC transactions, hotplug handling, timing generators, OPP formatting, stream encoders, DP/HDMI packets, audio packets, CRC diagnostics, and performance counters.

The macros themselves do not express ordering. Consumers must still sequence display clocks, resets, mux selection, AUX/HPD enablement, OPP/OTG update locks, stream-encoder programming, DP link training, HDMI/DP infoframe/audio setup, and interrupt acknowledgement according to DCN 4.2 hardware rules.

## State And Persistence Behavior

The header stores no software state and persists nothing to disk. It names hardware-backed state in the display engine:

- `CM3` gamma/histogram registers hold color pipeline programming and histogram/debug state for DPP pipe 3 while that block is powered.
- AUX, HPD, DDC/I2C, mux, and DIO registers expose live connector-side control/status, interrupt, arbitration, wake, routing, and transaction state.
- FMT/DPG/OPPBUF/OPP/CRC registers hold output formatter, pattern generation, buffering, CRC capture, and memory-power state for OPP pipes 0-3.
- ODM/OTG/OPTC registers hold live timing state: totals, sync windows, blanking, trigger windows, counters, frame counts, vblank/vline interrupts, update locks, CRC windows/results, DRR parameters, global sync, p-state, and static-screen controls.
- DIG0/DP0/VPG1/APG1 registers hold stream-encoder state for HDMI/TMDS/DisplayPort link formatting, training, secondary-data packets, audio packets, MST/MSO allocation, ALPM/panel replay, symbol counters, and audio-packet diagnostics.
- `DC_PERFMON13`, `DC_PERFMON14`, `DC_PERFMON15`, and DIO perfmon registers expose performance-counter control and readback state.

Persistence is hardware-defined. Configuration fields generally remain until modeset, link retraining, stream disable/enable, suspend/resume, power gating, GPU reset, or driver reinitialization. Status, interrupt, CRC, counter, wake, and transaction fields may be read-only, sticky, self-clearing, write-one-to-clear, double-buffered, or valid only while relevant display clocks and power domains are active. This offset header does not encode those access semantics; the matching shift/mask header and consuming block drivers supply them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.2.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h`, which provides field shifts and masks for these offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which includes this header and expands register lists for DCN42 hardware blocks using `BASE(reg*_BASE_IDX) + reg*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, which uses these offsets and masks for HPD, vblank, vline, vupdate, page-flip, and DMUB outbox interrupt descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c` and `hw_translate_dcn42.c`, which use DCN42 register metadata for GPIO, HPD, DDC, and AUX translation/factory wiring.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, which includes the generated DCN42 metadata for clock-manager register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, which initializes DMUB register offsets through `REG_OFFSET_EXP`; most DMUB-critical registers are in other chunks, but this file verifies the whole generated header participates in DCN42 DMUB support.

Functional integration points include connector discovery and hotplug, AUX/DDC EDID and DP sideband transactions, USB4/DPIA routing, pipe output formatting, timing generator programming, vblank/vline/DRR behavior, CRC diagnostics, HDMI/DP stream-encoder setup, DP link training, MST/MSO bandwidth allocation, audio/infoframe packet delivery, ALPM/panel replay behavior, and display performance monitoring.

## Risks And Edge Cases

- Offset/base-index macros are untyped preprocessor constants. A wrong value can compile cleanly while directing the driver to a valid but incorrect MMIO address.
- Because every visible `_BASE_IDX` is `2`, an accidental segment change in this range would be suspicious and high impact; it would route register helpers through a different DCN base segment.
- This is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching shift/mask file, firmware expectations, and silicon documentation.
- The chunk begins with a boundary-only `regCM3_CM_GAMCOR_RAMA_OFFSET_B_BASE_IDX` line. Whole-register pair validation must include the previous chunk for that register.
- The chunk ends on the `DME1` address-block comment/base-address pair without the actual `regDME1_*` macros. The following chunk owns those offsets.
- Repeated per-instance families are copy-sensitive. AUX0-4, HPD0-4, FMT/DPG/OPP/OTG0-3, and the DIG/DP instance layout can look structurally identical while carrying instance-specific offset deltas.
- OTG timing, update-lock, vblank/vline interrupt, CRC, and DRR registers are sequencing-sensitive. A misplaced offset can produce blanking errors, missed interrupts, visible timing jitter, bad CRC diagnostics, or failures that appear only during modeset, variable refresh, or suspend/resume.
- AUX/DDC/HPD offsets are connector-discovery critical. Mistakes can appear as failed EDID reads, broken DP link training, missed HPD/HPDRX events, or broken USB4/DPIA routing.
- Stream-encoder packet and audio offsets can cause HDMI/DP sinks to receive bad infoframes, ACR/N/M values, secondary-data packets, MST allocation state, or audio packets without necessarily causing a build failure.
- Perfmon and status registers mix control, sticky status, and readback semantics. Wrong offsets can clear unrelated events or produce misleading diagnostics.

## Test Signals

Useful validation for this chunk combines generated-header consistency checks with DCN42 display behavior:

- Build AMDGPU display with DCN42 enabled. Missing or renamed macros should fail in resource construction, IRQ service, GPIO translation/factory, clock-manager, DMUB, OPP, OPTC, DIO, AUX/I2C, stream-encoder, and audio register-table setup.
- Mechanically verify every `reg*` offset in this range has exactly one matching `reg*_BASE_IDX`, allowing the expected boundary exception for `regCM3_CM_GAMCOR_RAMA_OFFSET_B`.
- Cross-check offset values and base indexes against AMD's DCN 4.2.0 generated register source and compare repeated families against adjacent DCN 4.x headers where the layout should match.
- Exercise connector workflows: HPD/HPDRX interrupts, AUX native transactions, EDID reads over DDC/I2C, USB4/DPIA mux routing, link retraining, wake/status paths, and unplug/replug across suspend/resume.
- Exercise OPP/OTG paths on four pipes: modesets, vblank/vline interrupts, page flips, update locks, static-screen entry/exit, interlace/stereo where supported, CRC capture/readback, DRR/VRR changes, and multi-display synchronization.
- Exercise HDMI and DisplayPort stream-encoder behavior on DIG0/DP0: TMDS and DP link training, MSA programming, secondary-data/infoframe delivery, audio ACR/N/M programming, MST/MSE/MSO allocation, ALPM/panel replay, symbol counters, and fast-training status.
- Monitor kernel logs, IRQ counters, EDID/AUX traces, display CRCs, link-training traces, sink audio enumeration, perfmon readback, and suspend/resume logs for missed interrupts, failed transactions, invalid packets, wrong timing, or resume-only register-restore failures.

## Cross-Chunk Notes

The previous chunk owns the matching offset macro for the first line's `regCM3_CM_GAMCOR_RAMA_OFFSET_B_BASE_IDX` and the earlier `CM3` gamma-control setup. This chunk owns the remaining visible `CM3` gamma/histogram tail, DCOH/AUX/HPD/mux, OPP/OTG, DIO, DIG0/DP0, and DIG1 VPG/APG macro groups. The next chunk begins with the actual `DME1` register macros and continues DIG1/DIO families. The final merged file report should reconcile these boundaries before making complete claims about all DCN 4.2.0 offset families in this header.
