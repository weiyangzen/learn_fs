# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 12995-15259

## Scope And Purpose

This chunk is the final large section of AMD's generated DCN 3.5.1 register offset header. It contains C preprocessor constants only: each hardware register offset macro is paired with a matching `_BASE_IDX` macro that selects a segment from `ctx->dcn_reg_offsets[]` when DCN351 display code builds runtime MMIO addresses.

The requested range contains 2,140 `#define reg...` lines: 1,070 register offset macros and 1,070 base-index macros. The first 26 register offsets are the tail of the preceding `dce_dc_mpc_mpc_cfg_dispdec` address block because the chunk starts after that block's comment header. After that tail, the range includes complete address blocks for MPC output color-space conversion, MPC perfmon, HPO HDMI/DP support, ABM instances 0-3, MPCC MCM instances 0-3, DLPC, DPIA MU, HDA audio controller/endpoint aliases, DIO DPIA muxes, and DIG stream mapper registers. The range ends with the file's closing `#endif`.

This header is not executable driver logic. Its purpose is to bind DCN 3.5.1 register names to generated numeric offsets so higher-level display code can construct register tables for MPC composition/color, adaptive backlight management, audio/stream encoders, high-performance output paths, DisplayPort-over-USB4 DPIA plumbing, and low-level diagnostics.

## Important Register Areas

The initial tail of `dce_dc_mpc_mpc_cfg_dispdec` covers MPC global controls after the block header from the prior chunk: bypass background color registers, host read control, DPP/MPC pending status, VUPDATE lock sets 0-3, and `MPC_DWB0_MUX`. These support MPC-wide clock/reset/CRC/status programming and synchronization between address/config/cursor updates and vertical update timing.

`dce_dc_mpc_mpc_ocsc_dispdec` provides MPC output mux and output color-space conversion registers. It defines `MPC_OUT0` through `MPC_OUT3` muxes, denorm controls, clamp registers, one shared `MPC_OUT_CSC_COEF_FORMAT`, and full CSC mode/coefficient bank A/B registers for all four MPC outputs. These offsets back output mux selection and post-blend color conversion before OPP/stream output.

`dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec` and `dce_dc_hpo_hpo_dcperfmon_dc_perfmon_dispdec` expose display performance monitor instances 15 and 23. Each includes perfcounter control, state, high/low counter values, counter-off controls, interrupt status/acknowledge, and high/low perfmon readback. They are diagnostic counters rather than normal scanout programming registers.

The HPO/HDMI blocks cover stream encoder support for the high-performance output path. `AFMT5`, `VPG5`, and `DME5` provide audio/infoframe packet, generic packet, and metadata engine registers for HPO HDMI stream encoder 0. `HDMI_LINK_ENC`, `HDMI_FRL_ENC`, `HDMI_STREAM_ENC`, and `HDMI_TB_ENC` cover link control, fixed-rate link encoding, stream clock/character counter control, test bus controls, CRC controls, and status. `HPO_TOP_CLOCK_CONTROL`, `HPO_TOP_HW_CONTROL`, and `DP_STREAM_MAPPER_CONTROL0-3` connect HPO stream/link routing and top-level HPO enablement.

`dce_dc_opp_abm0_dispdec` through `abm3` define four repeated ABM instances, each with 60 offsets. They cover ambient-light/PWM input state, minimum and target backlight, current gain, manual gain, hysteresis and variance controls, histogram bins/thresholds, debug/select registers, BL/ABM memory power controls, software lock registers, and master lock registers. DCN351 resource setup allocates four ABM register tables even though actual panel/backlight availability is platform dependent.

`dce_dc_mpc_mpcc_mcm0_dispdec` through `mcm3` are the largest part of this chunk. Each MPCC MCM instance contributes 139 offsets for movable color management after MPCC blending: shaper control, shaper offset/scale/LUT index/data/write mask, shaper RAM A/B region programming, 3D LUT index/data/read-write/out normalization and offset registers, 1D LUT index/data/control registers, 1D LUT RAM A/B start/slope/base/end/offset/region registers, and `MPCC_MCM_MEM_PWR_CTRL`. These offsets allow DCN32/DCN35 MPC code reused by DCN351 to program per-MPCC shaper, 3DLUT, 1DLUT, and gamut/color management memories.

The final display/output plumbing blocks include `DLPC_*` display low-power counter/resync registers; `DPIA_MU_*` clock, reset, TPI status, credit, interrupt, RBBMIF timeout/status, microsecond reference, ADP status, glue, and perf-counter registers for the DPIA microcontroller interface; HDA `AZCONTROLLER1`, `AZENDPOINT1`, and `AZINPUTENDPOINT1` aliases for command/response rings and immediate command/data paths; four `DIO_DPIA_MUX*_DIO_DPIA_MUX_CONTROL` registers; and five `DIG*_STREAM_MAPPER_CONTROL` registers for mapping DIG stream encoders to link targets.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The public interface is the generated macro namespace:

- `regNAME` is the register's generated offset within the ASIC register database.
- `regNAME_BASE_IDX` selects the base-address segment used by `BASE(regNAME_BASE_IDX)`.
- Address block comments preserve the hardware IP block and nominal base address that produced the generated offsets.

The main consumers are compile-time register-list macros in the AMD display stack. `display/dc/resource/dcn351/dcn351_resource.c` includes this header with `dcn_3_5_1_sh_mask.h`, defines `BASE(seg)` as `ctx->dcn_reg_offsets[seg]`, and expands helper macros such as `SR`, `SRI`, `SRII`, `VUPDATE_SRII`, and `SRII_DWB` into concrete `uint32_t` MMIO addresses stored in resource-specific register structs.

Important consumer structures initialized from this chunk include `struct dcn30_mpc_registers` through `MPC_REG_LIST_DCN3_2_RI`, `MPC_OUT_MUX_REG_LIST_DCN3_0_RI`, and `MPC_DWB_MUX_REG_LIST_DCN3_0_RI`; `struct dce_abm_registers` through `ABM_DCN32_REG_LIST_RI`; `struct dce_audio_registers` through `AUD_COMMON_REG_LIST_RI`; `struct dcn31_vpg_registers` and `struct dcn31_afmt_registers` for packet/audio metadata; `struct dcn10_stream_enc_registers` through `SE_DCN35_REG_LIST_RI`; and HPO stream/link encoder register tables through DCN31 HPO macros.

The paired `dcn_3_5_1_sh_mask.h` supplies field shifts and masks. This offset chunk only identifies where registers live; field layout, legal values, and side effects are defined by the shift/mask header, common display block headers, and hardware documentation.

## Control Flow And Runtime Behavior

This file has no local control flow. Runtime behavior starts when DCN351 resource construction expands the register-list macros and passes the resulting tables into hardware object constructors such as `dcn32_mpc_construct`, `dce_audio_create`, `dcn35_dio_stream_encoder_construct`, `dcn31_hpo_dp_stream_encoder_construct`, and `hpo_dp_link_encoder31_construct`.

The implied MPC programming flow is table driven. Resource initialization builds the MPC register table; MPC functions then use the offsets to control MPCC blending topology, MPC output muxes, output CSC matrices, VUPDATE locking, DWB muxing, and MCM color blocks. MPCC MCM programming is index/data-register heavy: software selects LUT indices or RAM regions, writes data/control values, and coordinates memory power and active bank state through the MPC register helper layer.

ABM control is similarly table driven. DCN351 creates four ABM register tables from the repeated ABM offset blocks, and the ABM/DMUB backlight path uses those addresses to coordinate histogram collection, gain/backlight targets, PWM behavior, and lock/update registers. Higher-level ABM commands and panel policy decide whether the registers are actively used.

Stream output construction maps stream encoder instances to VPG, AFMT, DME, DIG stream mapper, HPO, and audio blocks. For regular DIG encoders, `DIG*_STREAM_MAPPER_CONTROL` participates in mapping a stream encoder to a link target. For HPO paths, `DP_STREAM_MAPPER_CONTROL0-3`, HPO top controls, HPO HDMI stream/link/FRL/test-bus registers, and AFMT/VPG/DME instance 5 offsets support HDMI/DP high-bandwidth output programming.

The DPIA and DIO mux registers are low-level plumbing for DP-over-USB4/USB-C style routing. Clock/reset controls, TPI credit/status, local interrupts, RBBMIF timeout/status, and DIO DPIA mux controls are programmed by display link and hardware sequencing code outside this header.

## State And Persistence

The header stores no mutable state. It defines addresses for state that persists in hardware registers and internal memories while the display IP is powered.

Persistent hardware state represented in this chunk includes MPC output mux selection, output denorm/clamp and CSC coefficient banks, VUPDATE lock selection, ABM histogram/gain/backlight state, HPO packet/audio/link/FRL/test-bus state, MPCC MCM shaper/3DLUT/1DLUT RAM contents, memory power controls, DLPC counter/resync state, DPIA MU interrupt/status/perf counter state, HDA command/response ring pointers and immediate command state, and stream-to-link routing state.

Several areas have side-effecting or timing-sensitive behavior. Perfmon interrupt acknowledge registers clear status. HDA CORB/RIRB pointers and immediate command/status registers participate in hardware command queues. MPCC MCM LUT index/data registers mutate internal SRAM or staged LUT data. VUPDATE lock registers synchronize updates with scanout timing. Memory power controls can affect whether LUT or shaper memory contents are retained.

The generated offsets themselves are static build-time data. Their correctness depends on the DCN 3.5.1 register database and the runtime base arrays supplied by the DC context; changing either side without the other can produce valid C code that points at the wrong MMIO address.

## Dependencies And Integration Points

This chunk depends on the enclosing include guard from `dcn_3_5_1_offset.h` and on the matching generated `dcn_3_5_1_sh_mask.h` for bitfield access. It is DCN351-specific and should not be mixed with DCN 3.5.0, DCN 3.2, or DCN 4.x shift/mask headers without a full generated-register validation.

Primary integration points observed in the tree are:

- `display/dc/resource/dcn351/dcn351_resource.c`, which includes the header and expands most of these offsets into DCN351 resource register tables.
- `display/dc/irq/dcn351/irq_service_dcn351.c`, which includes the header for interrupt register address construction, although the IRQ table mostly uses other OTG/HPD/HUBP/DMUB registers outside this exact chunk.
- `display/dmub/src/dmub_dcn351.c`, which includes the header and initializes DMUB-visible DCN35/DCN351 register offsets through `DMUB_DCN35_REGS()` and related macros.
- Common DCN32/DCN35 headers such as `display/dc/resource/dcn32/dcn32_resource.h`, `display/dc/dio/dcn35/dcn35_dio_stream_encoder.h`, `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, `display/dc/dce/dce_audio.h`, and ABM helper headers, which define the register-list macros that concatenate `reg...` symbols.

The base-index values in this chunk are not uniform. Most MPC, HPO, ABM, MPCC MCM, and DPIA MU offsets use base index 3; DLPC and DIO/DIG mapper offsets use base index 2; HDA AZ controller/endpoint aliases in this chunk use base index 0 or 1 depending on the alias. Correct `ctx->dcn_reg_offsets[]` initialization is therefore part of the address contract.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong offset or `_BASE_IDX` compiles successfully but redirects register writes into unrelated hardware, leading to display corruption, missing backlight control, broken audio packet programming, lost HPO routing, invalid DPIA muxing, or hard-to-debug power and interrupt failures.

The chunk starts in the middle of an address block. The first 26 macros should be interpreted as the continuation of `dce_dc_mpc_mpc_cfg_dispdec`, not as an anonymous block. Whole-file reconciliation must merge this with the preceding chunk to document the full MPC config block cleanly.

Repeated-instance consistency is a useful validation signal and a likely failure mode. ABM0-3 should be structurally parallel with offsets spaced by their block bases, and MPCC_MCM0-3 should each expose the same 139-register MCM layout. Any one-instance mismatch can show up only on a particular pipe, plane blend path, or panel backlight instance.

Index/data and memory-power registers require sequencing discipline. MPCC MCM shaper/3DLUT/1DLUT data paths, ABM histogram/backlight controls, HDA ring pointers, perfmon ack registers, and DPIA interrupt/status registers can have write-side effects. Direct ad hoc access to these macros outside existing register helpers risks stale banks, lost acknowledgements, or scanout-visible artifacts.

HPO and DPIA support is platform and policy dependent. Resource caps in DCN351 report five stream encoders, four HPO DP stream encoders, two HPO DP link encoders, and five DIG link encoders; not every board or connector exposes every route. Tests need to cover both active and inactive-path behavior.

## Test And Validation Signals

Compile coverage should include DCN351 resource construction, MPC, ABM, audio, DIG stream encoder, HPO stream/link encoder, IRQ, and DMUB register initialization. Missing or renamed offset macros usually fail at compile time through the register-list macros.

Static validation should compare this chunk against the authoritative DCN 3.5.1 generated register database, verify every non-`_BASE_IDX` macro has exactly one matching `_BASE_IDX`, check base-index values against address block expectations, and diff repeated ABM and MPCC MCM instances for layout consistency.

Runtime validation signals include successful modesets across all four timing/OPP/MPC paths, correct plane blending and MPC output CSC behavior, working DWB mux selection if writeback is enabled, correct color output with MPCC MCM shaper/3DLUT/1DLUT paths, stable ABM/backlight behavior on supported panels, audio packet/infoframe correctness, working HPO DP/HDMI routing, reliable DPIA/USB-C display bring-up, stable suspend/resume and runtime power transitions, valid perfmon readback/interrupt acknowledgement, and no register-access faults from incorrect base-index computation.

## Research Notes

This is source-tree-aligned chunk research only for `subset-b-002086`. It intentionally writes only `Docs/researches/chunks/subset-b-002086_research.md`; the later merge/reconciliation lane should combine it with adjacent chunks before producing whole-file research for `dcn_3_5_1_offset.h`.
