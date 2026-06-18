# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 15839-17880

## Purpose

This chunk is the final line range of AMD's generated DCN 4.2.0 register-offset header. It contains C preprocessor constants, not executable logic. Each `reg...` macro gives a register offset and each adjacent `reg..._BASE_IDX` macro gives the register-base selector used by AMD display register-access tables. In this range every visible base index is `3`, so consumers combine these offsets with the fourth MMIO base in the generated DCN 4.2.0 register-base table.

The chunk starts at an artificial boundary inside the `MPCC_MCM0` first gamut-remap definition: the offset for `regMPCC_MCM0_MPCC_MCM_FIRST_GAMUT_REMAP_MODE` is immediately before this range, while its `_BASE_IDX` line is the first line here. It then completes the tail of `MPCC_MCM0`, contains the complete `MPCC_MCM1`, `MPCC_MCM2`, and `MPCC_MCM3` blocks, and ends at the file terminator after Azalia stream 7 output-descriptor offsets.

The covered hardware surface is broad:

- MPC/MPCC MCM color-management offsets for shaper LUTs, 3D LUTs, 1D LUTs, first and second gamut-remap matrices, memory power control, and fast 3D-LUT load status for MPCC MCM instances 0-3.
- MPC configuration, CRC, pending status, vupdate lock-set, per-HUBP 3D-LUT fast-load configuration, and DWB mux offsets.
- HPO HDMI stream, TMDS/transport block, APG, VPG, DME, link encoder, FRL encoder, HPO top, DP stream mapper, and DC perfmon 23 offsets.
- OPP ABM0-ABM3 adaptive backlight and histogram/luma-statistic offsets.
- DPIA MU/glue/performance-counter offsets for DisplayPort-over-USB-C infrastructure.
- HDA/Azalia controller, endpoint/root immediate command aliases, and output stream descriptor offsets for audio streams 0-7.

Although the repository path sits under a `ceph-client` source mirror, this header is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, variables, or includes in this chunk. The public interface is generated macro naming:

- `reg<REGISTER>` expands to a numeric register offset, for example `regMPCC_MCM1_MPCC_MCM_SHAPER_CONTROL`, `regHDMI_TB_ENC_PACKET_CONTROL`, `regABM0_DC_ABM1_LS_SUM_OF_LUMA`, `regDPIA_MU_INTERRUPT_STATUS`, or `regAZSTREAM0_1_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`.
- `reg<REGISTER>_BASE_IDX` expands to the base-address table index paired with the offset.
- Address-block comments such as `dce_dc_mpc_mpcc_mcm1_dispdec`, `dce_dc_hpo_hdmi_tb_enc0_dispdec`, `dce_dc_opp_abm0_dispdec`, `dce_dpia_dpia_mu0_dpiadec`, and `dce_dc_hda_azcontroller_azdec` preserve the generated register database grouping.

Important macro families in this chunk:

- `regMPCC_MCM{1,2,3}_MPCC_MCM_*` and `regMPCC_MCM{1,2,3}_MPC_MCM_*` repeat a large color pipeline layout: shaper control/offset/scale/index/data/write-enable; shaper RAM A/B start, end, and 34 region registers; 3D LUT mode/index/data/read-write/out offset; 1D LUT control/index/data and RAM A/B curve registers; first and second gamut-remap coefficient-format, mode, and matrix coefficient registers; memory power control; and fast-load select/status.
- The tail of `regMPCC_MCM0_*` completes first and second gamut remap, memory power, and 3D-LUT fast-load status for instance 0.
- `regMPC_*`, `regADR_*`, `regCFG_*`, `regCUR_*`, and `regHUBP{0..3}_3DLUT_FL_*` cover global MPC clock/reset/CRC/status, vertical-update lock sets 0-3, and per-HUBP fast-load 3D-LUT bias/scale and config.
- `regHDMI_STREAM_ENC_*`, `regHDMI_TB_ENC_*`, `regAPG9_*`, `regVPG9_*`, `regDME9_*`, `regHDMI_LINK_ENC_*`, `regHDMI_FRL_ENC_*`, `regHPO_TOP_*`, and `regDP_STREAM_MAPPER_CONTROL*` cover the HPO HDMI/DP output path.
- `regDC_PERFMON23_*` covers performance-counter control, state, current value, and high/low counter latches for HPO perfmon 23.
- `regABM{0..3}_*` repeats the OPP adaptive backlight module layout: PWM levels, ABM control, ACE/PWL controls, histogram/luma-stat readouts, sample rates, histogram-bin shift flags/indices, result index/data, and backlight master lock.
- `regDPIA_*` and `regDPIA_MU_*` cover DPIA MU clock/reset per port, TPI status per port, interrupt status/control/ack, RBBM timeout/status, microsecond reference control, adapter status, glue control, and indexed performance counters.
- `regGLOBAL_*`, `regINTERRUPT_*`, `regCORB_*`, `regAZCONTROLLER1_*`, `regAZENDPOINT1_*`, `regAZINPUTENDPOINT1_*`, `regAZROOT1_*`, and `regAZSTREAM{0..7}_1_*` cover DCN HDA/Azalia controller global registers, CORB/RIRB rings, immediate command/response paths, DMA position base, wall-clock alias, endpoint/root aliases, and stream descriptor registers.

## Control Flow

This chunk has no local control flow. Runtime flow is created when DCN 4.2 display code includes this header with the matching `dcn_4_2_0_sh_mask.h` file and token-pastes register names into tables consumed by AMD display helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed variants.

Typical flow using these offsets is:

1. DCN 4.2 resource, IRQ, DMUB, audio, link, color, ABM, or HPO code selects the DCN 4.2 offset and shift/mask headers.
2. Register-list macros expand symbolic names into offset/base-index pairs and field shift/mask pairs.
3. Runtime display programming writes or polls hardware through those generated tables.
4. The numeric offsets in this chunk decide which hardware register receives each write or read.

Examples of indirect sequencing affected by this chunk include programming MPCC MCM LUT and gamut-remap state during color pipeline updates, locking MPC vertical-update domains around atomic plane updates, configuring HDMI/FRL/VPG/APG/DME packet paths during modeset, collecting ABM luma histograms and updating backlight PWM levels, resetting or monitoring DPIA ports during USB-C/DP tunnel activity, and programming Azalia command rings or output stream descriptors for HDMI/DP audio.

## State And Persistence Behavior

The header itself stores no software state and persists nothing to disk. It describes hardware-backed state:

- MPCC MCM state persists in color-management hardware: shaper LUT entries, 1D LUT curves, 3D LUT entries, output offsets, first/second gamut-remap matrices, memory power settings, and fast-load selection/status.
- MPC state includes clock/reset controls, CRC selection/results, DPP and miscellaneous pending state, vertical-update lock groups, HUBP fast-load configuration, and DWB mux routing.
- HPO HDMI/DP state includes stream encoder clocks, input muxing, audio control, packet control, ACR values/status, generic-packet line selection, data-buffer control, metadata control, active/blank timing, CRC, encryption, mode, FIFO status, FRL configuration, and stream-mapper routing.
- ABM state includes user/ambient/target/current/final/min PWM levels, ABM control, ACE/PWL table access, histogram/luma readouts, sample-rate programming, bin shift settings, and backlight master locks.
- DPIA state includes per-port clocks/resets/status, interrupt status/control/ack, timeout status, timing reference, adapter status, and performance counter index/data state.
- Azalia state includes controller global status/control, wake/status/interrupt registers, CORB/RIRB base addresses and pointers, immediate command/response state, DMA position base address, wall clock, and per-stream descriptor control, position, cyclic buffer length, last valid index, FIFO/format, BDL base, and position alias.

The access semantics are not encoded here. Many target registers are hardware latches, read-only status, sticky interrupt status, write-one-to-clear bits, indexed windows, or values only valid while a related clock/power domain is enabled. The matching shift/mask header and consuming driver code must supply field-level semantics and ordering.

## Dependencies And Integration Points

Direct dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h` must define fields for the register names listed here. Offsets without matching field definitions, or field definitions without matching offsets, break register-table construction or produce incomplete accessors.

Important integration points visible in the tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`, so DMUB DCN 4.2 support depends on the generated offset namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c` includes both generated headers for DCN 4.2 interrupt register setup.
- AMD display register helpers and component register-list macros depend on stable `reg...` names and `_BASE_IDX` companions.
- HDMI transport-block enum values in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h` describe semantic values for several `HDMI_TB_ENC_*` registers whose offsets are in this chunk.
- ABM, HPO, DPIA, Azalia/audio, color-management, and MPC code from adjacent DCN generations can share naming conventions. That makes the generated names look reusable, but the offsets must remain generation-specific for DCN 4.2.0.

## Risks And Edge Cases

- The chunk starts in the middle of a register pair. `regMPCC_MCM0_MPCC_MCM_FIRST_GAMUT_REMAP_MODE_BASE_IDX` is present here, but the corresponding offset line is in the previous chunk. Any per-chunk validator must account for that boundary exception.
- This is untyped generated metadata. A wrong offset or base index can compile cleanly and route a valid-looking register access to the wrong hardware address.
- The repeated `MPCC_MCM1`, `MPCC_MCM2`, and `MPCC_MCM3` blocks are copy-sensitive. A single instance offset error may only affect one pipe or plane color path and can be missed if testing exercises only instance 0.
- HPO HDMI/FRL, APG/VPG/DME, and DP stream-mapper offsets sit in adjacent but distinct blocks. Mixing similarly named stream, transport, link, FRL, packet, and mapper registers can cause black screens, invalid infoframes, bad ACR/audio behavior, or link-training failures.
- ABM offsets are repeated for four OPP instances with regular spacing. Misindexing can drive the wrong panel/backlight path or read the wrong histogram/luma statistics.
- DPIA MU registers include interrupts, timeout handling, and per-port reset/clock controls. Wrong offsets can leave a USB-C/DP tunnel port stuck, miss an interrupt, or acknowledge the wrong event.
- Azalia controller and stream descriptor registers share offsets for aliased subregisters such as version/capability fields, payload capability fields, wake/status, CORB/RIRB fields, immediate-command data/index, and stream FIFO/format. Consumers must use matching field masks to disambiguate aliases.
- Several status and clear registers are timing-sensitive. Reads while clocks are gated, writes before reset release, or acknowledgements with stale masks can produce intermittent display, audio, or hotplug failures.
- The file ends at this chunk. Merge tooling should not expect following lines after the `#endif`, but it must still reconcile the previous boundary line for a complete per-file report.

## Test Signals

Useful validation signals include:

- Build AMDGPU display support with DCN 4.2 enabled. Missing or renamed macros should fail in DCN 4.2 DMUB, IRQ, resource, audio, ABM, HPO, DPIA, or color register-table compilation.
- Mechanically verify every `reg...` offset macro in this range has a paired `_BASE_IDX` macro and that all visible base indexes are intentional for DCN 4.2.0. Allow the first-line boundary where only a `_BASE_IDX` half of the previous register appears in this chunk.
- Cross-check this offset range against AMD's authoritative DCN 4.2.0 register database and the matching `dcn_4_2_0_sh_mask.h` names.
- Exercise color-management paths on all MPCC MCM instances: shaper LUT load, 1D LUT load, 3D LUT load/fast load, first and second gamut-remap programming, memory power transitions, and multi-plane composition.
- Exercise modeset and atomic update paths that use MPC CRC, vupdate locks, pending status, HUBP fast-load configuration, and DWB mux routing.
- Exercise HDMI/DP output through the HPO path: stream encoder input mux/clock, HDMI transport packet and ACR programming, APG/VPG generic packets, DME, link encoder, FRL configuration, stream mapper, CRC, metadata packets, encryption mode, and suspend/resume.
- Exercise ABM on all available OPP instances: PWM level programming, ambient/user/target transitions, luma-stat/histogram collection, ACE/PWL table access, result index/data reads, and backlight lock behavior.
- Exercise DPIA ports 0-3 where hardware exposes them: clock/reset, TPI status, interrupt status/ack, timeout paths, adapter status, microsecond reference, and performance counter readback.
- Exercise HDMI/DP audio: HDA controller reset/interrupt, CORB/RIRB ring setup, immediate command/response, DMA position base, wall-clock reads, and stream descriptor programming for streams 0-7 including FIFO/format aliases and link-position aliases.
