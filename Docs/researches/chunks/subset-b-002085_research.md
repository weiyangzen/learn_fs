# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 10403-12994

## Scope

This chunk is a generated AMD DCN 3.5.1 register-offset header slice. It contains C preprocessor constants only: `reg...` symbols for hardware register offsets and paired `reg..._BASE_IDX` symbols for selecting the register base segment used by the AMDGPU display register-access helpers. There are no functions, structs, enums, branches, loops, allocations, locks, syscalls, or software persistence paths in this range.

The requested range covers 2,592 source lines and 2,376 `#define reg...` lines. It starts inside the `dce_dc_pwrseq0_dispdec_pwrseq_dispdec` block at `regPWRSEQ0_PANEL_PWRSEQ_CNTL_BASE_IDX`, after the actual `regPWRSEQ0_PANEL_PWRSEQ_CNTL` offset was defined on the previous line. It then covers PWRSEQ1, four DSC/DSCC instances, DSC perfmon blocks 19 through 22, display writeback, DCHVM, HPO DisplayPort stream/link/PHY encoder blocks, four MPCC compositor blocks, four MPCC output-gamma blocks, and the first registers of MPC global config. It ends at `regMPC_PERFMON_EVENT_CTRL_BASE_IDX`, before the remaining MPC config registers in the next chunk.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata for DCN 3.5.1 display hardware, not Ceph filesystem code.

## Purpose

The purpose of this range is to map DCN 3.5.1 display-engine register names to numeric register offsets and register-base indices. Runtime AMDGPU display code uses these generated constants, together with matching shift/mask definitions from `dcn_3_5_1_sh_mask.h`, to build ASIC-specific register tables for low-level MMIO programming.

The hardware surfaces represented here include:

- Panel power sequencing and backlight PWM registers for PWRSEQ0/PWRSEQ1.
- Display Stream Compression control, PPS, status, memory power, error-statistic, rate-buffer, and perfmon registers for DSC instances 0 through 3.
- Display writeback top-level, flow-composition, CRC, overflow, reset, perfmon, gamut-remap, and output-gamma registers.
- Display Core host virtual memory and RIOMMU control/status registers.
- HPO DisplayPort stream encoders 0 through 3, APG audio-packet generators, DME blocks, VPG generic-packet/ISRC/MPEG packet blocks, 32-symbol stream encoders, link encoders for links 0 and 1, and 32-symbol DP PHY blocks 0 and 1.
- MPC MPCC compositor registers for MPCC0 through MPCC3.
- Per-MPCC output gamma and gamut-remap register windows for MPCC_OGAM0 through MPCC_OGAM3.
- The beginning of MPC global clock/reset/CRC/perfmon event control.

The constants are generated data, but they are a hardware ABI for the driver. A wrong offset or base index can compile cleanly and still make the driver program the wrong display engine, read stale status, reset the wrong block, misconfigure DSC, corrupt gamma/color state, or lose DisplayPort packet/audio behavior.

## Important APIs, Types, And Macros

This chunk exports the standard AMD generated offset naming convention:

- `reg<block>_<register>` gives the register offset value.
- `reg<block>_<register>_BASE_IDX` gives the base-index selector used by generated register-access macros.
- `// addressBlock: ...` comments identify the generated hardware address block.
- `// base address: ...` comments document the register database's block base before translation to the exported offset namespace.

There are no callable APIs or C data types in this chunk. Runtime code consumes these symbols through Display Core register lists, register-sequence tables, and `REG_*` helper macros that pair offsets from this file with field shifts/masks from the corresponding generated mask header.

Important macro families in this range include:

- `regPWRSEQ0_*` tail entries and complete `regPWRSEQ1_*` panel sequencing/backlight register pairs.
- `regDSC_TOP[0-3]_*`, `regDSCCIF[0-3]_*`, and `regDSCC[0-3]_*` for DSC top control, CIF config, PPS, status, error metrics, rate-buffer telemetry, memory power, and debug bus rotation.
- `regDC_PERFMON19_*` through `regDC_PERFMON22_*` for DSC perfmon, plus `regDC_PERFMON3_*` for writeback perfmon.
- `regDWB_*` and `regFC_*` for display writeback, flow-composition, CRC, overflow, host-read, soft-reset, gamut-remap, and output-gamma registers.
- `regDCHVM_*` for host-virtual-memory and RIOMMU control/status.
- `regDP_STREAM_ENC[0-3]_*`, `regAPG[0-3]_*`, `regDME[6-9]_*`, `regVPG[6-9]_*`, `regDP_SYM32_ENC[0-3]_*`, `regDP_LINK_ENC[0-1]_*`, and `regDP_DPHY_SYM32[0-1]_*` for HPO DisplayPort output.
- `regMPCC[0-3]_*` for per-compositor selection, blending, background, memory-power, and status registers.
- `regMPCC_OGAM[0-3]_*` for per-compositor output gamma LUTs, region tables, RAM A/B curve coefficients, offsets, and gamut-remap matrices.
- `regMPC_*` for the first global MPC clock/reset/CRC/perfmon event registers visible at the end of the chunk.

Most registers in this chunk have `BASE_IDX` value `2`, corresponding to display decoder/MMIO blocks in this generated header. MPC/MPCC/MPCC_OGAM registers use `BASE_IDX` value `3`, which is a distinct generated register-base domain. Mixing the two is an offset translation bug, not just a naming issue.

## Address Block Inventory

The chunk includes full or partial coverage of these generated address blocks:

- Partial `dce_dc_pwrseq0_dispdec_pwrseq_dispdec`, from `PANEL_PWRSEQ_CNTL_BASE_IDX` through `PWRSEQ_SPARE`.
- Complete `dce_dc_pwrseq1_dispdec_pwrseq_dispdec`.
- DSC instance blocks `dce_dc_dsc[0-3]_dispdec_dsc_top_dispdec`, `dsccif`, `dscc`, and `dsc_dcperfmon_dc_perfmon`.
- DWB blocks `dce_dc_wb0_dispdec_dwb_top_dispdec`, `wb_dcperfmon_dc_perfmon`, and `dwbcp`.
- `dce_dc_dchvm_hvm_dispdec`.
- HPO DP stream encoder blocks for stream encoders 0 through 3, with APG, DME, and VPG sub-blocks.
- HPO DP symbol encoder blocks `dce_dc_hpo_dp_sym32_enc[0-3]_dispdec`.
- HPO DP link encoder blocks for link encoders 0 and 1 only in this range.
- HPO DP PHY symbol blocks `dce_dc_hpo_dp_dphy_sym320_dispdec` and `dce_dc_hpo_dp_dphy_sym321_dispdec` only in this range.
- MPCC blocks `dce_dc_mpc_mpcc[0-3]_dispdec`.
- MPCC output gamma blocks `dce_dc_mpc_mpcc_ogam[0-3]_dispdec`.
- Partial `dce_dc_mpc_mpc_cfg_dispdec`, from `MPC_CLOCK_CONTROL` through `MPC_PERFMON_EVENT_CTRL_BASE_IDX`.

The largest repeated families are MPCC/OGAM and HPO DP. The chunk has 704 `regMPCC_OGAM...` macros, 120 `regMPCC[0-3]...` macros, 588 `regDP...` macros, 208 `regDWB...` macros, and 360 DSCC instance macros, plus smaller APG, VPG, DME, PWRSEQ, DCHVM, FC, and MPC groups.

## Power Sequencing And Backlight

The first visible line is a boundary artifact: `regPWRSEQ0_PANEL_PWRSEQ_CNTL_BASE_IDX` is included, but its matching offset macro appears one line earlier outside the requested range. The rest of the PWRSEQ0 tail includes panel state, delay registers, reference dividers, backlight PWM control and period, PWM group lock, and spare register entries.

PWRSEQ1 is complete in this chunk. It includes GPIO enable/control/mask/output registers, panel power-sequence control/state/delay/reference-divide registers, backlight PWM controls, PWM period, group-lock, and spare. These offsets feed panel bring-up, panel power-down, and embedded-panel backlight control code. Because the header only supplies addresses, ordering and timing semantics must come from the panel/power-sequencer driver logic and hardware spec.

## DSC And DSCC Blocks

DSC instances 0 through 3 are represented by top-control, DSCCIF, DSCC, and perfmon sub-blocks. Each instance has:

- `DSC_TOP*_DSC_TOP_CONTROL` and `DSC_DEBUG_CONTROL`.
- `DSCCIF*_DSCCIF_CONFIG0/1`.
- `DSCC*_DSCC_CONFIG0/1`, `DSCC_STATUS`, and `DSCC_INTERRUPT_CONTROL_STATUS`.
- `DSCC*_DSCC_PPS_CONFIG0` through `DSCC_PPS_CONFIG22`, which hold the packetized parameter set programmed for compressed streams.
- `DSCC*_DSCC_MEM_POWER_CONTROL`.
- Squared-error and max-absolute-error readbacks for R/Y, G/Cb, and B/Cr paths.
- Rate-buffer and rate-control-buffer maximum fullness telemetry.
- `DSCC*_DSCC_TEST_DEBUG_BUS_ROTATE`.
- One DC perfmon block per DSC instance: `DC_PERFMON19` for DSC0, `DC_PERFMON20` for DSC1, `DC_PERFMON21` for DSC2, and `DC_PERFMON22` for DSC3.

These registers integrate with mode validation and stream programming for DSC-enabled HDMI/DP paths. The PPS offsets are especially sensitive: a mismatched register list can produce a valid-looking compressed stream with bad slice, rate-control, or buffer behavior.

## Display Writeback And DCHVM

The writeback top-level block covers clock enable, memory power, flow-composition mode/flow/window/source size, update control, CRC controls/masks/results, output control, MMHUBBUB backpressure counter enable/value, host-read control, overflow status/counter, and soft reset. The associated `DC_PERFMON3` block supplies the standard perf counter control/state/current/low/high registers for writeback.

The `dwbcp` color-processing section includes HDR multiplier, gamut-remap mode/format, two gamut-remap coefficient banks, output gamma control/index/data/control, and a full RAM A/RAM B piecewise curve set for blue, green, and red channels. It includes start controls, start slopes, start bases, end controls, offsets, and region selectors 0 through 33 for each RAM bank.

`DCHVM` contributes host virtual memory and RIOMMU control/status registers: `DCHVM_CTRL0`, `DCHVM_CTRL1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0`. These are display memory-management surfaces and are sequencing-sensitive around power, memory access, and host-visible readback paths.

## HPO DisplayPort Blocks

The HPO DisplayPort section covers four stream encoders. Each stream encoder has clock control, input mux, audio control, clock-ramp-adjuster FIFO status/control registers, and spare register entries. Each stream also has:

- APG registers for audio-packet generation control/debug, packet control, audio CRC control/result, status/status2, memory power, and spare state. `APG1_APG_PACKET_CONTROL` appears twice with the same offset value `0x3707`, which looks like generated-header duplication and should be treated carefully by any tooling that assumes unique macro names.
- DME control and memory-control registers for DME6 through DME9.
- VPG registers for generic packet access/data, GSP frame/immediate update control, generic status, memory power, ISRC access/data, and MPEG info packets.
- DP symbol encoder registers covering stream/video control, video FIFO, double-buffering, pixel format, MSA0 through MSA8, HBlank control, SDP GSP controls 0 through 14, SDP audio controls, metadata packet control, VBID, panel replay, video CRC control/results/status, symbol count status/control, memory power, and spare.

The chunk also includes DP link encoder clock/spare registers for link encoders 0 and 1. Link encoders 2 and 3 are not present in this requested range, even though stream/symbol encoder blocks 0 through 3 are present.

The DP PHY symbol blocks are present for PHY instances 0 and 1. They include control/status, SAT update, VC rate controls 0 through 3, SAT VC state/status for virtual channels 0 through 3, training-pattern config, PRBS seeds, square-pulse and custom training-pattern registers, error status, symbol override, symbol count status/control, CRC config/status/count, and related debug/test surfaces. These offsets are used during link training, UHBR/HPO DP symbol handling, error diagnostics, and CRC/symbol-count validation.

## MPC, MPCC, Output Gamma, And Gamut Remap

The MPCC blocks `MPCC0` through `MPCC3` each include top and bottom pipe selectors, OPP ID, control, state-machine control, update-lock selection, top/bottom gain, movable color-management location control, background color components, memory-power control, and status. These registers describe how Display Core composes planes before the output pixel processor.

The four MPCC_OGAM blocks are highly repetitive and complete in this range. Each block has output-gamma control, LUT index/data/control, RAM A and RAM B curve descriptors, region selectors 0 through 33, per-channel offsets, gamut-remap coefficient format/mode, and two banks of 3x4 gamut-remap matrix coefficients. These are color-management state surfaces: wrong offsets can misprogram transfer functions or color-conversion matrices while leaving the rest of the display path apparently operational.

The final `dce_dc_mpc_mpc_cfg_dispdec` block is partial. This chunk includes global MPC clock control, soft reset, CRC control/selection/result registers, and perfmon event control. It stops before bypass background, host read, pending status, vupdate lock, mux, status, and other MPC configuration registers that follow in the source file.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by AMDGPU Display Core code that includes this generated offset file and expands register-access helpers against ASIC-specific register tables.

Typical usage is:

1. DCN 3.5.1 resource construction selects register-list structures for a block such as DSC, DWB, HPO DP, MPCC, or MPC.
2. The selected table binds offset macros from this file with field shifts/masks from `dcn_3_5_1_sh_mask.h`.
3. Runtime display code executes modeset, link training, DSC programming, writeback setup, plane composition, color-management updates, interrupt/status handling, power management, diagnostics, or CRC/perfmon reads.
4. `BASE_IDX` tells the lower register helper which base-address segment to use for the register offset.
5. The hardware latches configuration, updates status/counters/CRC values, generates events, or changes power/clock/reset state.

This file does not encode reset values, field widths, valid values, write-one-to-clear behavior, ordering requirements, delays, locking rules, or power-domain prerequisites. Those semantics must come from the matching shift/mask header, surrounding driver code, and hardware documentation.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed hardware state whose lifetime is governed by GPU reset, display modesets, link training, panel power transitions, suspend/resume, runtime power management, display hotplug, interrupt handling, and diagnostic reads.

Configuration/latching state represented in this chunk includes panel/backlight sequencing controls, DSC PPS/config/memory-power state, DWB flow/composition/output/color state, DCHVM and RIOMMU controls, HPO DP stream/audio/packet/link/PHY controls, APG/VPG/DME memory power, MPCC composition and blending configuration, output gamma LUT/curve/register banks, gamut-remap matrices, and MPC clock/reset/CRC/perfmon selection.

Volatile or readback-oriented state includes panel power state, DSC status and compression error statistics, rate-buffer fullness telemetry, perfmon counters, DWB CRC results, DWB overflow/backpressure counters, RIOMMU status, HPO DP packet/status/error/symbol/CRC counters, MPCC status, MPC CRC results, and other status/control registers whose side effects are not specified by the offset header.

Sequencing-sensitive registers include soft reset, memory-power controls, clock controls, update locks, panel power sequence delays, PWM locks, DSC interrupt/status and PPS programming, DWB update controls, HPO DP link/PHY training and CRC/symbol count controls, APG/VPG packet update controls, MPCC composition selectors, OGAM LUT index/data windows, and MPC global reset/clock controls.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCN 3.5.1 register headers, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h` for the adjacent offset definitions outside this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h` for field positions and masks that make these offsets usable for read/modify/write operations.

The generated offset and mask headers must come from the same hardware register database. A version skew between offset and mask headers can make a helper write the right bitfield shape into the wrong register or use the right register with stale bit definitions.

Expected Display Core integration points include DCN 3.5.1 resource construction, link encoder and HPO DP programming, DSC programming, writeback, MPC/MPCC plane composition, color management, CRC/perfmon diagnostics, memory/power sequencing, panel/backlight control, and DMUB/display firmware interactions that depend on ASIC-specific register addresses.

The most important runtime consumers are hardware-specific register table initializers under AMDGPU Display Core, plus helper paths for DP link training, DSC enable/disable, display writeback, color pipeline programming, audio/generic packet generation, panel power sequencing, and register diagnostics.

## Risks And Edge Cases

- The chunk starts with `PWRSEQ0_PANEL_PWRSEQ_CNTL_BASE_IDX` but not the corresponding offset macro. Any per-chunk parser must merge with the previous chunk to reconstruct complete PWRSEQ0 register pairs.
- The chunk ends halfway through MPC config. A file-level report must merge with the next chunk for the remaining global MPC registers.
- `APG1_APG_PACKET_CONTROL` is duplicated with the same value in this chunk. C preprocessing tolerates identical duplicate definitions, but generated-doc or register-database tooling that assumes one definition per name may miscount or flag this.
- Offset/base-index mismatch is the key risk. Many visually similar blocks use `BASE_IDX 2`, while MPCC/MPC/MPCC_OGAM use `BASE_IDX 3`.
- HPO DP blocks are highly repetitive across stream encoders 0 through 3, but link encoder and PHY coverage is asymmetric in this range. Copying a stream index into a link/PHY path can target absent or wrong hardware.
- DSC blocks are repetitive across four instances. A wrong `DSCCN` prefix can program a different compressor than the stream uses.
- MPCC and MPCC_OGAM blocks are repetitive and color-sensitive. Wrong instance selection can apply blending, gamma, or gamut-remap state to the wrong composed pipe.
- LUT access registers such as `*_LUT_INDEX` and `*_LUT_DATA` require driver-side ordering. The header cannot prevent stale index/data sequencing or concurrent access problems.
- Status, CRC, perfmon, interrupt, and counter registers may be clear-on-read, write-one-to-clear, latched, or sampled by update controls. The offset header does not describe those semantics.
- Power, clock, memory-power, and reset registers can affect block availability. Incorrect writes can make later status reads time out or produce misleading diagnostics.
- Panel power and backlight PWM programming is timing-sensitive. Offsets alone do not encode panel delay requirements or power-rail sequencing.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for any DCN 3.5.1 display code that includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
- Static generation checks that every non-boundary `reg...` offset in this chunk has a matching `_BASE_IDX` line and that offset/mask headers are generated from the same register database version.
- Register-table initialization checks that PWRSEQ, DSC, DWB, HPO DP, MPCC, MPCC_OGAM, and MPC register lists point to DCN 3.5.1 symbols, not nearby DCN revisions.
- Hardware smoke tests for embedded-panel power on/off, backlight PWM changes, DP modesets, DSC enable/disable at compressed modes, DWB capture, and plane composition.
- DP link-training and packet tests using HPO paths, including symbol-count/CRC/error-status readbacks and audio/generic packet validation.
- Color-management tests that load OGAM LUTs and gamut-remap matrices on each MPCC instance and verify CRC or visual output changes on the intended pipe.
- DSC stress tests that compare PPS programming, status, error counters, rate-buffer fullness, and perfmon counters across all four DSC instances.
- Suspend/resume and runtime power-management tests that exercise clock, memory-power, soft-reset, DCHVM, APG/VPG/DME, DWB, and MPCC state restoration.
- Register-dump sanity checks for duplicate macro handling, especially `regAPG1_APG_PACKET_CONTROL`, and for boundary completeness across adjacent chunks.
