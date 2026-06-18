# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 5186-7670

## Purpose

This chunk is generated register-address metadata for the AMD DCN 3.1.2 display engine. It contains C preprocessor `#define`s that map symbolic DCN display-block register names to MMIO offsets plus matching `*_BASE_IDX` segment selectors. The driver combines each register offset with `DCN_BASE__INST0_SEG<idx>` through register-list macros such as `SR`, `SRI`, `SRII`, and `SRII_MPC_RMU` in the DCN31 resource code.

The covered range starts in the tail of the DPP2 scaler (`DSCL2`) block, then defines most of DPP2 color-management (`CM2`), DPP3 converter/scaler/color-management/top/perfmon blocks, and a large part of the MPC composition pipeline: MPCC0-3 blending controls, MPC global configuration, MPC perfmon, per-MPCC output-gamma/gamut blocks, output mux/output CSC blocks, and the start of the RMU 3D-LUT block. It has no executable code, functions, structs, or algorithms. Its importance is that every macro is part of the hardware programming ABI for Yellow Carp/DCN 3.1.2 display support.

## Important APIs, Types, And Register Groups

- The chunk contains 2401 `#define`s. Each hardware register normally has a pair: `reg<NAME>` gives the register offset and `reg<NAME>_BASE_IDX` selects the DCN base segment used to form the final MMIO address.
- The opening lines are a chunk-boundary continuation of `dce_dc_dpp2_dispdec_dscl_dispdec`. They include `regDSCL2_SCL_BLACK_COLOR_BASE_IDX` and the remaining DPP2 scaler/window/output-buffer registers: `DSCL_UPDATE`, `DSCL_AUTOCAL`, overscan, OTG blanking, recout/MPC sizing, line-buffer format/memory control/status, scaler memory power control/status, and output-buffer control/power.
- `dce_dc_dpp2_dispdec_cm_dispdec` (`regCM2_*`, base address `0xb58`) defines DPP2 color-management registers. It covers CM bypass/update control, post-CSC matrix pairs and B-bank matrix pairs, gamut-remap matrix pairs and B-bank pairs, output bias, gamma-correction control, LUT index/data/control, RAMA/RAMB start/slope/base/end/offset controls, many RAMA/RAMB region tables, decompression and RGB-to-YUV style conversion tables, alpha/color-key related controls, and test/debug registers.
- `dce_dc_dpp2_dispdec_dpp_top_dispdec` (`regDPP_TOP2_*`, base `0xb58`) defines DPP2 top-level controls: DPP control, clock control, SRAM clock gating, DPP_CONTROL2, CRC control/readback, and host-read control.
- `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` (`regDC_PERFMON13_*`, base `0x43e8`) defines the DPP2 perfmon counter control, counter state, interrupt/status, and high/low readback offsets.
- `dce_dc_dpp3_dispdec_cnvc_cfg_dispdec` (`regCNVC_CFG3_*`, base `0x1104`) defines DPP3 converter-format configuration: surface pixel format, format control, alpha/2-bit-alpha LUT, expansion, keying, de-alpha, pre-CSC mode and coefficient pairs including B-bank coefficients, coefficient-format control, pre-degamma, and pre-realpha.
- `dce_dc_dpp3_dispdec_cnvc_cur_dispdec` (`regCNVC_CUR3_*`, base `0x1104`) defines DPP3 converter-side cursor controls: cursor enable/mode/control, cursor color registers, and cursor floating-point scale/bias.
- `dce_dc_dpp3_dispdec_dscl_dispdec` (`regDSCL3_*`, base `0x1104`) mirrors the DPP scaler block for pipe 3. It includes coefficient RAM selection/data, scaler and tap controls, sharpness, manual replicate factors, horizontal/vertical scale ratios and initial phases for luma/chroma/top/bottom, black color, update/autocal, overscan, OTG blanking, recout/MPC sizing, line-buffer state, scaler memory power, and OBUF state.
- `dce_dc_dpp3_dispdec_cm_dispdec` (`regCM3_*`, base `0x1104`) mirrors the DPP color-management set for pipe 3. Its register families match `CM2`: post-CSC, gamut-remap, bias, gamma LUT access, RAMA/RAMB piecewise regions, decompression/color-space conversion controls, and test/debug.
- `dce_dc_dpp3_dispdec_dpp_top_dispdec` (`regDPP_TOP3_*`, base `0x1104`) and `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` (`regDC_PERFMON14_*`, base `0x4994`) provide DPP3 top-level and perfmon offsets.
- `dce_dc_mpc_mpcc0_dispdec` through `dce_dc_mpc_mpcc3_dispdec` (`regMPCC0_*` ... `regMPCC3_*`, bases `0x0`, `0x80`, `0x100`, and `0x180`) define four MPCC blending/composition slices. Each slice has top/bottom selection, control, alpha, multiplied-alpha, background color, pre-multiplied alpha, output size, status/control, debug, line-buffer control, denorm, mux selection, mux status, and status registers.
- `dce_dc_mpc_mpc_cfg_dispdec` (`regMPC_*`, base `0x0`) defines global MPC controls: clock and memory power, output muxes, CRC control/results, gamut-remap memory power/status, debug-data mux/readback, ALU control, output-size programming, memory low-power/read-margin controls, and DWB muxing.
- `dce_dc_mpc_mpc_dcperfmon_dc_perfmon_dispdec` (`regDC_PERFMON15_*`, base `0x1901c`) defines the MPC perfmon control/status/readback registers.
- `dce_dc_mpc_mpcc_ogam0_dispdec` through `dce_dc_mpc_mpcc_ogam3_dispdec` (`regMPCC_OGAM0_*` ... `regMPCC_OGAM3_*`, bases `0x0`, `0x200`, `0x400`, and `0x600`) define per-MPCC output gamma and gamut-remap blocks. Each instance contains OGAM control, LUT index/data/control, RAMA/RAMB start/end/region registers, memory power control/status, B-state controls, and MPC gamut-remap matrix pairs for A/B banks.
- `dce_dc_mpc_mpc_ocsc_dispdec` (`regMPC_OUT*`, base `0x0`) defines four MPC output mux and output CSC groups. Each output has an `OUTn_MUX`, an `OUTn_CSC_MODE`, and A/B-bank CSC coefficient-pair registers for the 3x4 color matrix.
- `dce_dc_mpc_mpc_rmu_dispdec` (`regMPC_RMU*`, base `0x0`) begins the RMU global and RMU0 block. In this chunk it includes global RMU control and memory power, RMU0 shaper controls, shaper offsets/scales, shaper LUT index/data/write-enable mask, shaper RAMA/RAMB start/end/region tables, and the start of RMU0 3D-LUT programming through `MPC_RMU0_3DLUT_OUT_OFFSET_G_BASE_IDX`.

The public "API" surface here is purely macro-based. Callers do not invoke functions from this file; they include it alongside `dcn_3_1_2_sh_mask.h` so generated register-list macros can build address, shift, and mask tables for DC objects.

## Control Flow

There is no C control flow in this header. Runtime control flow occurs in the AMD display driver code that consumes these symbols:

1. DCN31 resource setup includes this offset header and the matching shift/mask header.
2. Register-list macros concatenate block names and instance IDs into symbols such as `regCM3_CM_CONTROL`, `regMPCC1_MPCC_CONTROL`, or `regMPC_RMU0_3DLUT_MODE`.
3. The macros calculate a final MMIO address as `BASE(reg..._BASE_IDX) + reg...`, where the base index maps to a DCN segment from the ASIC base-address header.
4. Hardware object constructors store those final addresses in typed register tables for DPP, MPC, MPCC, RMU, perfmon, DMUB, and IRQ/resource paths.
5. Runtime paths use register helpers to write configuration registers, poll status registers, or read debug/perf counters.

The hardware programming sequences implied by this chunk include DPP scaler setup before pipe enable, DPP post-CSC/gamut/gamma programming before color-managed output, MPCC top/bottom mux and alpha programming before MPC composition, output CSC programming before stream output, and RMU shaper/3D-LUT programming when advanced color blocks are enabled.

## State And Persistence Behavior

The macros are compile-time constants and do not store runtime state. The registers they name represent persistent device state until changed by MMIO writes, reset, power-gating transitions, suspend/resume, or display mode reprogramming.

Important hardware state represented in this range includes scaler ratios/phases/taps and coefficient RAM selection, line-buffer and OBUF memory state, color matrices and B-bank matrix state, gamma LUT indices/data/control, piecewise gamma region tables, DPP CRC/perfmon state, MPCC blend topology and alpha values, MPC output mux routing, MPC CRC results, MPC and RMU memory power controls/statuses, per-output CSC matrices, and RMU shaper/3D-LUT tables.

Many registers are not ordinary one-shot configuration. Names ending in `STATUS`, `READBACK`, `RESULT`, `DEBUG_DATA`, `PERFCOUNTER_*`, `UPDATE`, `LUT_DATA`, `LUT_INDEX`, or memory-power `STATUS` reflect readback, indexed state, counters, or asynchronous hardware state. The offset header does not encode read-only, write-one-to-clear, indexed-LUT, double-buffer, or power-state sequencing rules; those rules must come from the hardware spec and the corresponding driver logic.

## Dependencies And Integration Points

- `display/dc/resource/dcn31/dcn31_resource.c` includes `yellow_carp_offset.h`, this `dcn_3_1_2_offset.h`, and `dcn_3_1_2_sh_mask.h`. Its `SR`, `SRI`, `SRII`, `SRII_MPC_RMU`, and related macros are the main bridge from generated offsets to typed DC register tables.
- `display/dmub/src/dmub_dcn31.c` includes this header to build DMUB service register/field tables through `REG_OFFSET_EXP`, `DMUB_DCN31_REGS()`, and field-mask/shift helpers.
- `display/dc/irq/dcn31/irq_service_dcn31.c` includes this header with the shift/mask header so interrupt service code can use the correct DCN31 register map.
- The chunk's DPP2/DPP3 symbols integrate with DPP register-list macros such as `DPP_REG_LIST_DCN30` and the DPP color/scaler code that programs CNVC, DSCL, CM, top, CRC, and perfmon registers.
- The MPCC, MPC, OCSC, and RMU symbols integrate with MPC register-list macros such as `MPC_REG_LIST_DCN3_0`, `MPC_OUT_MUX_REG_LIST_DCN3_0`, `MPC_RMU_GLOBAL_REG_LIST_DCN3AG`, and `MPC_RMU_REG_LIST_DCN3AG`.
- The `*_BASE_IDX` values are as important as offsets. DPP2/DPP3 display-pipe registers use base index 2 in this chunk, while the MPC/MPCC/RMU registers use base index 3. A correct offset with the wrong base index would target the wrong MMIO segment.

This file also depends structurally on adjacent generated headers for the same ASIC family: the matching shift/mask header defines bit positions, and other offset chunks in this same file define earlier/later instances. Similar offset headers for DCN 3.1.4, 3.1.5, 3.1.6, 3.2.x, 3.5.x, and 4.x preserve many names but may differ in addresses or available blocks.

## Risks And Edge Cases

- This chunk starts in the middle of a generated register pair: it begins with `regDSCL2_SCL_BLACK_COLOR_BASE_IDX`, while the corresponding `regDSCL2_SCL_BLACK_COLOR` offset is in the previous chunk. The merge lane must reconcile this boundary before treating the DSCL2 group as complete.
- This chunk ends in the middle of the RMU0 block at `regMPC_RMU0_3DLUT_OUT_OFFSET_G_BASE_IDX`; later RMU0/RMU1 3D-LUT registers continue in the next chunk. Research consumers should not infer that only one RMU instance or only the visible 3D-LUT registers exist.
- The file is generated and highly repetitive. Copy-generation drift between DPP2 and DPP3, MPCC0-3, MPCC_OGAM0-3, or MPC_OUT0-3 can compile cleanly while routing MMIO writes to the wrong instance.
- Offset/base-index mistakes are high impact because the driver composes final addresses mechanically. A wrong `*_BASE_IDX` can move an otherwise plausible register offset into a different aperture.
- Indexed LUT registers such as gamma, shaper, and 3D-LUT index/data pairs require strict index/data ordering and bank selection. The offset constants cannot prevent stale indices, partial LUT programming, or writes to the wrong RAM bank.
- Double-buffered color matrices and B-bank registers must be synchronized with the hardware's update semantics. A valid address can still produce visual corruption if the caller flips banks or update controls at the wrong time.
- Memory power control registers appear for DSCL/OBUF, MPC gamut-remap memory, MPCC OGAM memory, and RMU memory. Callers must coordinate power state with active fetch/composition/LUT use; the offset header provides no readiness or polling policy.
- Output mux, MPCC topology, and output CSC programming are tightly coupled. Misrouting an MPCC or MPC output mux can produce blank output, swapped planes, or color conversion on the wrong output even when all individual register writes are valid.
- Perfmon and CRC/debug registers can be read or reset by diagnostic paths. Incorrect offsets may not be noticed in normal display operation but can break validation, telemetry, or automated bring-up diagnostics.

## Test Signals

- Build coverage: malformed or missing macros should break compilation in DCN31 resource, DMUB, IRQ, DPP, MPC, and register-list users.
- Generated-header validation: compare all offsets and base indices against the vendor register database for DCN 3.1.2, with special checks for duplicated instance families (`CM2`/`CM3`, `MPCC0-3`, `MPCC_OGAM0-3`, and `MPC_OUT0-3`).
- Modeset and plane-composition tests: multi-plane enable/disable, z-order changes, alpha blending, MPCC split/merge, MPC output mux routing, and multi-display output exercise the MPCC and MPC groups.
- Color-management tests: post-CSC, output CSC, gamut remap, gamma correction, OGAM, RMU shaper, and RMU 3D-LUT programming should be validated with known pixel-output patterns or CRC comparisons.
- Scaling tests: luma/chroma scaling, tap-count changes, overscan, recout size changes, line-buffer partition changes, and OBUF modes cover the DSCL2 tail and DSCL3 block.
- Power-management tests: display idle, memory low-power entry/exit, suspend/resume, and active-pipe power transitions should observe the DSCL, OBUF, MPC, OGAM, and RMU power-control/status registers.
- Debug/perf tests: DPP2/DPP3/MPC perfmon counters, DPP CRC, MPC CRC, debug-data muxes, and host-read control paths verify the diagnostic offsets that ordinary modeset tests may not touch.
