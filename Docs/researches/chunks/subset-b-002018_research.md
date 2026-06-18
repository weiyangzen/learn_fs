# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h - subset-b-002018

## Scope

- Chunk id: `subset-b-002018`
- Source lines: 217137-219522
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`
- Observed content: 2,386 lines, 2,172 `#define` entries, 1,089 `__SHIFT` macros, 1,083 `_MASK` macros, and 214 register block comments.

This chunk is part of the generated AMD DCN 3.2 register shift/mask header. It contains no executable logic; it publishes bit-field locations for the C20 PHY CR4 lane-X analog TX/RX, lane-X RX digital/calibration/statistics, and raw-lane-X TX PCS/FW register families. Most fields are 16-bit register fields represented by paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants.

## Purpose

The chunk starts at the tail of the `C20_PHY_CR4_LANEX_DIG_ANA_XF_TX_STAT_EQ_OUT_*` status family, defines TX analog CREG controls, then covers a long CR4 lane-X RX path: ASIC override/input/output bridges, RX power states, VCO calibration, CDR/DPLL, receiver adaptation, statistic counters, IQ correction, RX analog crossbar/control surfaces, and RX analog CREGs. The final section starts `C20_PHY_CR4_RAWLANEX_DIG_TX_PCS_XF_*` and reaches into `C20_PHY_CR4_RAWLANEX_DIG_TX_FW_XF_OVRD_IN_1`.

The practical purpose is to let DCN 3.2 display and amdgpu code address ASIC register fields by generated names instead of hard-coded bit positions. Consumers combine these macros with matching register offsets from `dcn_3_2_0_offset.h` and the AMDGPU/DC register helper layer to construct read-modify-write masks, extract status, and issue low-level MMIO programming for display PHY link bring-up, calibration, diagnostics, and firmware handoff.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or storage declarations in this chunk. The public interface is the generated preprocessor namespace.

- TX analog status and controls:
  - `C20_PHY_CR4_LANEX_DIG_ANA_XF_TX_STAT_EQ_OUT_4` and `C20_PHY_CR4_LANEX_DIG_ANA_XF_TX_STAT_IN_0`
  - `C20_PHY_CR4_LANEX_DIG_ANA_XF_TX_ANA_CREG00` through `_CREG05`
  - `C20_PHY_CR4_LANEX_DIG_ANA_XF_TX_ANA_CREG0_OVRD` and `_CREG1_OVRD`
  - Fields include TX equalization leg pull enables, clock-shift ACK, RX detect and DCC-cal results, TX analog clock/data/serial/reference/loopback enable bits, VCM hold, VBOOST, IBOOST, termination, ring/VREG controls, ATB measurement muxes, pull-up/pull-down controls, DCC-cal analog taps, MPLLA/MPLLB clock enables, and CREG override placeholders.
- RX ASIC bridge and override inputs:
  - `C20_PHY_CR4_LANEX_DIG_ASIC_RX_OVRD_IN_0` through `_IN_4`
  - `C20_PHY_CR4_LANEX_DIG_ASIC_RX_OVRD_SIGDET_IN`, `_OVRD_VCO_IN`, `_OVRD_EQ_IN_0` through `_OVRD_EQ_IN_11`
  - `C20_PHY_CR4_LANEX_DIG_ASIC_RX_OVRD_OUT_0`
  - `C20_PHY_CR4_LANEX_DIG_ASIC_RX_ASIC_IN_0` through `_ASIC_IN_3`, `_CDR_VCO_ASIC_IN`, `_EQ_ASIC_IN_0` through `_EQ_ASIC_IN_2`, and `_ASIC_OUT_0`
  - These groups expose forced and normal ASIC-to-RX control fields for resets, requests, power state, data enable, inversion, CDR SSC/track, div clocks, VCO configuration, loopback, EQ AFE/VGA/ATT/CTLE/DFE/IQ settings, adaptation status, and ACK output.
- RX power, VCO, CDR, DPLL, and loopback:
  - `C20_PHY_CR4_LANEX_DIG_RX_PWRCTL_RX_PSTATE_P0`, `_P0S`, `_P1`, `_P2`, `_RX_PWRUP_TIME_0`, `_RX_PWRUP_TIME_1`, `_RX_CTL`, and `_RX_STATUS`
  - `C20_PHY_CR4_LANEX_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0` through `_CTRL_2`, `_TIME_0`, `_TIME_1`, and `_STAT_0` through `_STAT_2`
  - `C20_PHY_CR4_LANEX_DIG_RX_LBERT_CTL`, `_LBERT_ERR`
  - `C20_PHY_CR4_LANEX_DIG_RX_CDR_CDR_CTL_0` through `_CTL_4`, `_CDR_STAT`
  - `C20_PHY_CR4_LANEX_DIG_RX_DPLL_FREQ`, `_FREQ_BOUND_0`, and `_FREQ_BOUND_1`
  - These fields describe per-power-state analog enables, clock and DFE/slicer enables, VCO frequency/calibration reset and continuous-calibration flags, power-up delays, forced powerdown, power status, VCO calibration tuning and observed codes, loopback BERT enable/error, CDR gain/divider/jump/SSC settings, and DPLL frequency bounds.
- RX adaptation and statistic collection:
  - `C20_PHY_CR4_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0` through `_ADPT_CFG_12`
  - `C20_PHY_CR4_LANEX_DIG_RX_ADPTCTL_RST_ADPT_CFG`, `_ATT_STATUS`, `_VGA_STATUS`, `_CTLE_STATUS`, `_DFE_TAP*_STATUS`
  - `C20_PHY_CR4_LANEX_DIG_RX_ADPTCTL_DFE_*_VDAC_OFST`, `_RX_SLICER_CTRL_*`, `_RX_DCC_*_IDAC_OFST`, `_RX_FAST_FLAGS`, and `_SSM_*`
  - `C20_PHY_CR4_LANEX_DIG_RX_STAT_*`
  - Fields include adaptation enable/mu/threshold controls for ATT, VGA, CTLE, and DFE taps; adaptation reset timing; current adaptation codes; slicer levels; DCC offsets; fast-settle flags; startup state-machine configuration; match/stat counter masks, sample counters, shadow counters, stat-stop, compare-clock controls, and extended load values.
- RX IQ correction and analog crossbar/control:
  - `C20_PHY_CR4_LANEX_DIG_RX_IQC_CTL_RESET_ADJUST`, `_CONFIG`, `_STAT`
  - `C20_PHY_CR4_LANEX_DIG_ANA_XF_RX_CTL_OVRD_OUT`, `_RX_PWR_OVRD_OUT_0`, `_RX_PWR_OVRD_OUT_1`
  - RX analog calibration/control blocks such as `_SIGDET_CAL_EN`, `_SIGDET_HF_CAL`, `_SIGDET_LF_CAL`, `_VCO_OVRD_OUT_*`, `_CAL_0`, `_CAL_1`, `_VDAC_RANGE_SEL`, `_DAC_CTRL`, `_ANA_RTRIM`, `_DCC_CAL_DAC_CTRL_RANGE`, `_AFE_OVRD_IN_*`, `_SCOPE`, `_SLICER_CTRL`, `_ANA_IQ`, IQC bypass/data adjust clocks, loopback control, AFE update enable, DFE/bypass/phase sample select, term-code outputs, and RX status inputs/outputs.
  - These groups carry low-level analog state and override routing for signal detect, VCO, DAC ranges, RTUNE, calibration, IQ correction, and RX sample path controls.
- RX analog CREG tail:
  - `C20_PHY_CR4_LANEX_DIG_ANA_XF_RX_ANA_CREG00` through `_CREG11`
  - `C20_PHY_CR4_LANEX_DIG_ANA_XF_RX_ANA_CREG0_OVRD` and `_CREG1_OVRD`
  - Fields cover bandgap/regulator, VREG, CDR, VCO, common-mode, boost, termination, DCC, slicer/scope, loopback, clocking, bias, IQ, and calibration-related analog controls. The exact field names are hardware-register contracts rather than code behavior.
- Raw-lane-X TX PCS and firmware start:
  - `C20_PHY_CR4_RAWLANEX_DIG_TX_PCS_XF_LANE_OVRD_IN_0`, `_LANE_IN_0`
  - `C20_PHY_CR4_RAWLANEX_DIG_TX_PCS_XF_OVRD_IN_0` through `_OVRD_IN_3`
  - `C20_PHY_CR4_RAWLANEX_DIG_TX_PCS_XF_IN_0` through `_IN_2`, `_OVRD_OUT_0`, `_OUT_0`, and `_CNTX_CFG_0` through `_CNTX_CFG_2`
  - `C20_PHY_CR4_RAWLANEX_DIG_TX_FW_XF_OVRD_IN_0` and the beginning of `_OVRD_IN_1`
  - These fields describe TX PCS loopback/link-number overrides, reset/request handshakes, pstate, low-power detect, data enable, inversion, clock-ready, beacon, MPLL enable/state, RX-detect request/result, deskew, recalibration force/skip, context select, rate, width, VREG/VBOOST/IBOOST, KR driver enable, DCC range/bypass, term control, TX unique ID, and firmware override inputs.

## Control Flow

This header chunk has no local control flow. Runtime sequencing is supplied by including code and by the C20 PHY hardware:

1. A DCN 3.2 component includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. The component selects the register offset plus the generated field mask/shift pair for a target lane or PHY block.
3. Register helper macros/functions such as the DC `REG_*` helpers use the constants to insert or extract field values.
4. MMIO reads and writes program the PHY, observe status, clear latched events, or force override/debug behavior.

The register names imply common hardware flows: override registers pair forced values with `*_OVRD_EN` bits; request/ack registers model PCS/FW/ASIC handshakes; power-state registers choose different RX analog enable sets; calibration blocks expose enable, reset, timing, and status fields; statistic registers separate match/mask/sample/count controls; and raw TX PCS context registers bind a selected context to rate/width/electrical settings.

## State and Persistence Behavior

The macros are compile-time constants and do not store state. They describe state in hardware registers:

- Configuration state persists in the PHY until reset or reprogramming: TX analog CREG values, RX power-state enable maps, RX calibration timing/tuning, CDR/DPLL settings, adaptation thresholds/mu values, statistic match masks, analog calibration controls, raw TX PCS context fields, lane link number, and firmware override values.
- Handshake/status state is transient or latched: TX/RX detect results, DCC/VCO calibration status, RX power status, CDR detect/status, loopback BERT error, adaptation codes/status, statistic counters, IQC status, RX analog status inputs, PCS/FW request and ACK bits, and RX-detect results.
- Override state is high impact. Many groups provide value plus enable bits (`*_OVRD_EN`, `*_OVRD`, `OVRD_IN`, `OVRD_OUT`, CREG override fields). If a diagnostic or bring-up path leaves an override enabled, normal ASIC/firmware/PCS control can remain pinned.
- Statistic and counter fields require sequencing by the consumer: load values, sample counts, match masks, stat controls, shadow counters, and stop/freezing fields are only meaningful relative to the hardware counter lifecycle.
- Reserved fields are defined so generated field math remains complete, but they should generally be preserved on read-modify-write and not treated as policy-authorized writable fields.

## Dependencies

This chunk depends on AMDGPU/DCN generated-register conventions:

- Matching register offsets in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`.
- AMDGPU and DC register-access helpers that expect `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming.
- DCN 3.2 C20 PHY hardware semantics for CR4 lane-X and raw-lane-X blocks.
- Include sites observed in this tree: `display/dmub/src/dmub_dcn32.c`, `amdgpu/gmc_v11_0.c`, `display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, and `display/dc/resource/dcn32/dcn32_resource.c`.

The field definitions appear generated from an ASIC register database. Correctness depends on that generator and database staying synchronized with the actual DCN 3.2 hardware register map.

## Integration Points

- Display link bring-up and link maintenance can use these definitions for TX PCS rate/width/pstate/deskew/recalibration, TX analog electrical controls, RX power-state enables, RX CDR/VCO/DPLL setup, signal-detect thresholds, and RX adaptation controls.
- Firmware and hardware handoff paths interact with the ASIC RX bridge and raw TX FW/PCS interfaces through request, reset, pstate, ACK, and override fields.
- Calibration flows use VCO, DCC, RTUNE, signal-detect, DAC, IQ correction, CDR, and adaptation definitions to tune receiver and transmitter analog behavior.
- Diagnostic and validation tooling can read status and statistic blocks for adaptation codes, DFE tap status, CDR status, VCO calibration codes, BERT errors, match counters, sample counters, and RX analog status.
- Low-level debug code may use CREG override, analog crossbar override, PCS override, and FW override registers to force hardware states during PHY bring-up or failure analysis.
- Merge/reconciliation should combine this chunk with adjacent `dcn_3_2_0_sh_mask.h` chunks before making per-file conclusions, because this slice starts mid-TX-status family and ends mid-`TX_FW_XF_OVRD_IN_1`.

## Risks and Edge Cases

- Generated mask/shift drift can silently corrupt hardware programming. Errors in reset, request, pstate, rate, width, CDR, VCO, DCC, power-state, EQ, or override-enable fields can cause link training failures, unstable links, or power-management regressions.
- Similar names across TX/RX, ASIC/ANA/RAWLANE, `IN`/`OUT`, and override/non-override blocks make copy/paste mistakes easy. A field with the same conceptual name can belong to a different crossbar direction or control owner.
- Value/enable pairs are easy to misuse. Writing the forced value without enabling the override may have no effect; leaving the enable set after test code can block automatic firmware or hardware control.
- RX power-state registers duplicate many enable fields for P0/P0S/P1/P2. A lane may behave correctly in one power state while failing in another if only one map is updated.
- Statistic and calibration registers can return stale or partial data if read without respecting reset/load/sample/done/status semantics.
- Full-register writes are risky because many registers include reserved high bits. Consumers should prefer generated field-update helpers or preserve reserved bits with read-modify-write.
- The raw-lane-X naming abstracts the lane index in this portion. Consumers must pair these masks with the correct offset macros for the intended lane or instance.
- Analog CREG and CREG override fields are close to hardware electrical limits. Incorrect values can produce hard-to-debug signal-integrity failures rather than obvious software errors.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for all DCN 3.2 include sites to catch missing, renamed, or malformed generated macros.
- Generated-header consistency checks that every field has expected `__SHIFT` and `_MASK` pairs, masks align to shifts, and fields do not unintentionally overlap within each register block.
- Register-helper unit or compile-time tests for representative field insertion/extraction: RX power-state enable maps, VCO calibration controls/status, CDR control/status, RX adaptation config/status, statistic counter controls, RX analog override fields, TX PCS rate/width/context, and TX FW override fields.
- Hardware or emulator link tests covering mode set, hotplug, link training, retraining, suspend/resume, low-power states, and high-bandwidth link rates to catch bad pstate, rate, width, clock, and calibration programming.
- Diagnostic tests that verify request/ACK handshakes, RX-detect results, VCO/DCC done bits, CDR status, BERT error reporting, statistic counter load/freeze/stop behavior, and adaptation-code readback.
- Regression checks ensuring debug paths clear override enables and restore automatic control after forced analog, PCS, or firmware states are used.
