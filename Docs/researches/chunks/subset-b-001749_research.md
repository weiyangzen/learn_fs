# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h lines 12974-15568

## Scope

This chunk is a generated AMD DCN 3.0.2 register-offset header segment. It contains preprocessor register address macros only: each memory-mapped register normally has a `mm...` offset macro plus a matching `..._BASE_IDX`, while indexed legacy/VGA/Azalia codec spaces use `ix...` register-index macros without base-index companions. The slice spans 2,595 source lines and contains 2,398 `#define` lines: 1,410 register/index macros and 988 `BASE_IDX` macros.

The chunk begins in the middle of the `MPCC_OGAM1` block, covers several complete MPC/OPP/HDA/VGA/Azalia blocks, and ends in the middle of `azf0endpoint1_endpointind`. The file-level merge must therefore combine this note with adjacent chunks before drawing whole-file completeness conclusions.

## Purpose

The purpose of this header segment is to provide symbolic register offsets for AMDGPU DCN 3.0.2 display, color, backlight, audio, and legacy display register programming. Driver code can use these names with generated register lists and register access helpers instead of embedding numeric offsets or indirect register indexes.

This chunk is data-like source rather than executable logic. Correctness depends on exact agreement with AMD hardware register specifications and with the companion DCN 3.0.2 field mask/header files. A single wrong offset can redirect a read-modify-write operation to a different hardware register.

## Address Blocks And Register Surface

Covered or partially covered address blocks:

- Partial `dce_dc_mpc_mpcc_ogam1_dispdec`: tail of MPCC output gamma instance 1. The slice starts at `mmMPCC_OGAM1_MPCC_OGAM_RAMA_REGION_12_13`, continues through RAMA/RAMB piecewise-linear region, start, slope, base, end, and offset registers, then includes gamut remap format/mode and matrix coefficient registers.
- `dce_dc_mpc_mpcc_ogam2_dispdec`, `dce_dc_mpc_mpcc_ogam3_dispdec`, `dce_dc_mpc_mpcc_ogam4_dispdec`: complete MPCC output gamma instances at bases `0x400`, `0x600`, and `0x800`. Each has 88 register offsets covering OGAM control, LUT index/data/control, RAMA/RAMB curve programming, and A/B gamut-remap matrices.
- `dce_dc_mpc_mpc_cfg_dispdec`: MPC top-level configuration, including clock, soft reset, pending/status, host read, bypass background, CRC selection/result/control, vupdate/cursor/address locks, DPP pending status, perfmon event selection, and DWB muxing.
- `dce_dc_mpc_mpc_ocsc_dispdec`: output color-space conversion for MPC outputs 0 through 4. Each output has a mux, denorm controls, coefficient format, mode, and A/B matrix coefficient offsets.
- `dce_dc_mpc_mpc_rmu_dispdec`: RMU shaper and 3D LUT register surface for RMU instances 0 through 2. It exposes RMU control/memory registers and repeated shaper/3D LUT index, data, control, start/end/offset/region, and output offset offsets.
- `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec`: DC perfmon 25 counter-control/counter/high/low offsets plus adjacent `DME5_DME_CONTROL` and `DME5_DME_MEMORY_CONTROL`.
- `dce_dc_hpo_hdmi_stream_enc0_hdcp2_hdcp2_dispdec`: declared at base `0x264f8` in this chunk, but no register macros appear before the next address-block marker.
- `dce_dc_hpo_hpo_top_dispdec`: HPO top clock control and DC perfmon 26 control/counter/high/low offsets.
- `dce_dc_opp_abm0_dispdec` through `dce_dc_opp_abm4_dispdec`: five Adaptive Backlight Modulation instances at bases `0x0`, `0x104`, `0x208`, `0x30c`, and `0x410`. Each instance has 60 register offsets for BL1 PWM/ambient-light inputs and DC ABM1 configuration, lookup tables, thresholds, current/min/max/backlight state, debug, and master lock.
- `dce_dc_hda_azcontroller_azdec`: HDA/Azalia controller registers for CORB/RIRB pointers, DMA position, immediate command output/input interfaces, response queues, wall clock, state-change status, and codec-pin control response paths.
- `dce_dc_hda_azendpoint_azdec` and `dce_dc_hda_azinputendpoint_azdec`: immediate command output/input data and index register offsets.
- Legacy indexed VGA blocks: `vga_vgaseqind`, `vga_vgacrtind`, `vga_vgagrphind`, and `vga_vgaattrind` define sequencer, CRT controller, graphics controller, and attribute controller indexes.
- Azalia indexed codec blocks: `azendpoint_f2codecind`, descriptor and sink-info blocks, input/output CRC result blocks, `azinputendpoint_f2codecind`, root codec parameters, 16 `azf0stream*_streamind` stream-latency/fifo counter blocks, full `azf0endpoint0_endpointind`, and partial `azf0endpoint1_endpointind`.

## Important Macros And Register Families

`mmMPCC_OGAM*_...` is the dominant color-pipeline register family in the opening portion. The registers describe MPCC output gamma LUT access, piecewise-linear curve memory (`RAMA` and `RAMB`), per-channel start/end/slope/base/offset controls, region pairs from 0-1 through 32-33, and gamut-remap coefficient matrices. Instances 2, 3, and 4 are complete in this slice; instance 1 is continued from the prior chunk.

`mmMPC_*` covers top-level Multi-Plane Compositor controls. The configuration block contains global reset, clock, pending, CRC, vupdate-lock, cursor-lock, address-lock, DPP pending, and DWB mux offsets. The OCSC block exposes per-output color conversion for five outputs. The RMU block exposes shaper and 3D LUT programming paths for three RMU instances, which are used by color-management flows that need more than simple gamma/gamut matrices.

`mmDC_PERFMON25_*` and `mmDC_PERFMON26_*` provide display performance counter controls and counter readout offsets. They integrate with diagnostics and performance monitoring rather than normal scanout setup.

`mmABM*_...` covers OPP adaptive backlight modulation. Important families include `BL1_PWM_*` ambient/backlight observation registers and `DC_ABM1_*` registers for algorithm control, IIR filters, hysteresis, backlight min/max/current, target/current pixel luminance, master override, debug select, and LUT programming.

`mmCORB_*`, `mmRIRB_*`, `mmAZALIA_*`, `mmIMMEDIATE_COMMAND_*`, `mmDMA_POSITION_*`, `mmWALL_CLOCK_*`, and `mmAZENDPOINT_*` cover the HDA controller-facing register surface. These offsets are used for command/response ring buffers, immediate codec commands, DMA position tracking, wall-clock timing, stream synchronization, codec state-change interrupts, and endpoint immediate command access.

`ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` are indexed legacy VGA register constants. They are not MMIO offsets with base-index metadata; they are selector values used through the VGA indirect access mechanism.

`ixAZALIA_F2_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, `ixAZALIA_INPUT_CRC*`, `ixAZALIA_CRC*`, `ixAZF0STREAM*`, and `ixAZF0ENDPOINT*` describe indexed Azalia codec and stream state. They include converter format, stream/channel IDs, pin capabilities, ELD/sink information, audio descriptors, CRC readbacks, FIFO/latency counters, pin widget controls, channel speaker mapping, HBR/lipsync, multichannel mode, codec status overrides, LPIB snapshots, coding type, wireless display identification, keepalive, and audio enable/format-change interrupt status.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime behavior is indirect: AMDGPU display code includes generated register-offset headers and passes these symbols to register access macros/tables. For `mm...` macros, the companion `..._BASE_IDX` value identifies the register base segment used by the access helper. For `ix...` macros, the value is an indirect register index in a legacy VGA or Azalia codec/register space.

The hardware-oriented flows represented by these offsets are:

- Color programming: MPCC OGAM and MPC RMU paths expose LUT index/data/control registers, curve segment parameters, 3D LUT access, and matrix coefficient registers. Driver code programs these while enabling color transforms, HDR/gamut remap, or per-plane/output correction.
- MPC composition and output routing: MPC mux, OCSC, denorm, bypass background, DPP pending, DWB mux, and vupdate-lock registers coordinate compositor output routing and synchronized register updates.
- Validation and diagnostics: MPC CRC and DC perfmon registers expose hardware counters, CRC results, and event selection used to validate display output or collect performance data.
- Backlight modulation: ABM registers carry ambient-light/PWM inputs and algorithm state used to compute or clamp panel backlight values.
- Audio command and stream handling: HDA/Azalia controller and indexed endpoint registers support codec command submission, response retrieval, stream format/channel setup, audio descriptors, ELD/sink reporting, CRC checks, latency counters, and audio enable/disable/format-change notification.
- Compatibility access: VGA indexed constants preserve access to legacy sequencer, CRT, graphics, and attribute controller registers where the hardware still exposes or emulates those spaces.

## State And Persistence

The macros themselves hold no mutable state and allocate no storage. They describe persistent hardware registers or indirect register indexes. Writes through consumers of these macros can remain effective until the display block is reprogrammed, reset, power-gated, or restored after suspend/resume.

Several represented register groups have stateful or handshake behavior:

- LUT and curve programming registers are index/data based. Consumers must program indexes and data in the correct order and select the intended RAM bank or color channel via companion field definitions.
- Vupdate, cursor, and address lock registers gate when pending display state becomes visible to scanout hardware. Incorrect lock/unlock sequencing can leave pending state unapplied or applied at the wrong frame boundary.
- RMU/OGAM and gamut-remap coefficient sets have A/B register banks in several places, implying double-buffered or selectable coefficient sets whose active bank is controlled by fields outside this offset-only chunk.
- ABM registers include live sensor/algorithm state, current backlight values, min/max constraints, and master-lock controls. These are persistent hardware control values and also carry runtime observations.
- CORB/RIRB and immediate-command registers are queue/handshake state for HDA command transport. Pointer and response registers must be synchronized with hardware ownership rules.
- Azalia endpoint, stream, CRC, and interrupt-status indexed registers expose latched stream status, counter values, sink data, pin state, and audio enable/format-change conditions.

## Dependencies And Integration Points

This chunk depends on the broader generated DCN 3.0.2 register header set:

- Companion `dcn_3_0_2_sh_mask.h` field definitions provide bit shifts and masks for the offsets named here.
- Register-list tables in AMDGPU DC code combine offset macros, base indices, masks, and shifts into typed per-block access structures.
- ASIC-version dispatch code chooses the DCN 3.0.2 layout for compatible GPUs.
- Enumeration headers such as AMD GPU SOC enum headers define symbolic values for MPCC OGAM, RMU, ABM, and Azalia fields that are programmed through these offsets.

Likely consumers include AMDGPU display color-management code, MPC/OPP resource setup, ABM/backlight management, display diagnostics/perfmon paths, HDMI/DP audio setup, Azalia codec command handling, and low-level VGA/HDA compatibility access paths. The generated names are compile-time API surface: renaming or deleting a macro breaks any consumer that references that register symbol, while changing a numeric value can compile cleanly but misprogram hardware.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A stale or wrong offset can read or write the wrong MMIO location or indirect register, with failures ranging from subtle color errors to blank display, broken audio, bad backlight behavior, or stuck hardware queues.
- This slice has partial block boundaries. `MPCC_OGAM1` is already in progress at line 12974, and `azf0endpoint1_endpointind` continues after line 15568. Reviewers must not treat those two blocks as complete based only on this chunk.
- Instance parity matters. `MPCC_OGAM2`, `MPCC_OGAM3`, and `MPCC_OGAM4` are structurally parallel with 88 register offsets each, and ABM0 through ABM4 are structurally parallel with 60 register offsets each. Any off-by-one generation error in one instance would be easy to miss in manual review but can affect only a subset of outputs/pipes.
- `BASE_IDX` values are part of the access contract. Most DCN MMIO macros in this chunk use base index `3`, but several nearby HPO/perfmon macros use other base indices. Consumers that assume a single base for the whole chunk would be wrong.
- The HPO HDCP2 address-block marker appears without register definitions in this slice. That may be a valid empty generated block or a boundary artifact; the merge lane should verify against adjacent chunks and generated source metadata.
- Indexed `ix...` constants are semantically different from `mm...` offsets. Tooling that expects every register macro to have a `BASE_IDX` partner will falsely flag VGA and Azalia indexed entries.
- HDA queue pointers, interrupt statuses, ABM locks, and color LUT index/data registers have hardware-specific ordering and acknowledgement semantics that are not expressible in an offset-only header. Consumers must rely on the companion masks and hardware programming sequence.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generation-time, and hardware/display regression signals:

- Compile AMDGPU DCN 3.0.2 display paths to catch missing or renamed offset macros.
- Generated-header checks should verify that every `mm...` register in this slice has the expected `..._BASE_IDX`, while `ix...` indexed registers are exempt.
- Cross-check offsets against `dcn_3_0_2_sh_mask.h` and register-list tables so each used register has matching field masks and no consumer points at a missing symbol.
- Instance-parity tests can compare MPCC OGAM2/3/4 and ABM0/1/2/3/4 layouts where hardware is expected to be repeated, while allowing documented base-address differences.
- Display color tests should exercise OGAM, gamut remap, OCSC, RMU shaper, and 3D LUT programming on multiple pipes/outputs.
- Backlight and panel tests should cover ABM enable/disable, ambient-light input handling, PWM/backlight min/max/current transitions, master lock, suspend/resume restore, and debug/status readbacks.
- Audio tests should cover HDA CORB/RIRB command transport, immediate codec commands, audio stream format/channel assignment, ELD/audio descriptor reads, HBR/lipsync/multichannel paths, CRC counters, latency counters, and audio enable/disable/format-change interrupts.
- Diagnostics should read MPC CRC results and DC perfmon 25/26 counters and verify event selection and counter rollover behavior.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the start of `MPCC_OGAM1` and that the next chunk completes `azf0endpoint1_endpointind`.
- Verify whether the empty `dce_dc_hpo_hdmi_stream_enc0_hdcp2_hdcp2_dispdec` block is intentionally empty for this generated header or split by a generation/chunking boundary.
- Identify concrete AMDGPU call sites for the OGAM/RMU/ABM/Azalia groups before the final per-file report names specific functions or structs.
