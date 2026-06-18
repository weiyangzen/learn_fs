# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 124777-127187

## Scope

This chunk is a generated DCN 3.2.0 shift/mask header slice for AMD display C20 PHY CR2 registers. It contains C preprocessor constants only: register comments of the form `//<REGISTER>` and paired `#define` values for `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no functions, structs, enums, branches, locks, allocations, persistence APIs, or direct MMIO accesses in this range.

The range starts in the middle of `C20_PHY_CR2_SUP_DIG_ANA_XF_MPLLB_ANA_CREG05`; several shift definitions for that register appear before line 124777, while the final shifts and all masks are in this chunk. It ends in the middle of `C20_PHY_CR2_LANE0_DIG_RX_PWRCTL_RX_CTL`; the first RX control masks are present through `RX_DCC_FORCE_DAC_WRITE_MASK`, while the remaining masks and following RX status/VCO calibration fields continue after line 127187. The later merge lane must treat both boundary registers as incomplete here.

## Purpose And Hardware Surface

The file as a whole is the bit-layout ABI for DCN 3.2.0 display hardware. This chunk specifically describes fields for the C20 PHY CR2 common/supervisor and lane0 digital PHY programming surface. The values are consumed by AMD display register helper macros that combine a register offset from the matching offset header with a field shift and mask from this header to compose MMIO writes or decode MMIO reads.

Major hardware areas covered by this slice:

- `C20_PHY_CR2_SUP_DIG_ANA_XF_MPLLB_ANA_*`: the tail of MPLLB analog control registers, including PLL regulation, charge-pump/reference, comparator trim, phase/spo latch, DLL resistance, reset alignment, PLL DAC, phase lock, and reserved override slots.
- `C20_PHY_CR2_RAWCMN_DIG_*`: common raw digital PHY control and status, including common reset, clock-gating override, MPLLA/MPLLB init calibration and spread-spectrum override, HDMI mode override, rtune request, ATE ALU access, firmware/static configuration status, MPLL async clock and recalibration-bank override, fractional update controls, context selection, common/supervisor/MPLLA/MPLLB context configuration, and common firmware/AON metadata.
- `C20_PHY_CR2_RAWCMN_DIG_AON_*`: always-on common PHY firmware and SRAM controls, MPLLA/MPLLB tuning banks and recalibration state, power-gating and supervisor handshake overrides, rtune value readbacks for RX/TXDN/TXAVG lanes 0-7, SRAM boot/recovery addresses, firmware and raw version readbacks, APB/supervisor status, and metadata location.
- `C20_PHY_CR2_LANE0_DIG_ASIC_*`: ASIC-facing lane0 override, input, and output transfer registers for lane-level control plus TX/RX analog request/status buses. These expose fields for lane mode, loopback, TX/RX rates, resets, requests, power states, width, inversion, LFPS/flyover, signal detect thresholds, VCO/CDR, equalization, DCC, termination, and analog control override enables.
- `C20_PHY_CR2_LANE0_DIG_TX_*`: lane0 TX power-state templates, power-up timing, TX control/status, DCC offset/status, statistic counters, clock alignment, LBERT pattern control, FIFO control, TX analog override/status buses, TX termination-code override, TX analog DCC calibration controls/data, TX equalization override/readback, and TX analog configuration registers.
- `C20_PHY_CR2_LANE0_DIG_RX_*`: lane0 RX ASIC override/input/output and early RX power-control fields, including RX P-state templates, RX power-up timing, and the start of RX control fields.

## Important Definitions

The generated naming convention is the main API:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit number for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.
- The driver helper `FD(reg_field)` expands a generated field name to its shift and mask; `get_reg_field_value()` and `set_reg_field_value()` use the same `reg_name ## __ ## reg_field` convention.

Important macro families in this chunk:

- `C20_PHY_CR2_SUP_DIG_ANA_XF_MPLLB_ANA_CREG05` through `CREG07` define MPLLB PLL analog tuning fields such as `MPLLB_ANA_CTR_SPO_PLL_*`, `MPLLB_ANA_CTR_CP_*`, `MPLLB_ANA_CTR_PFD`, `MPLLB_ANA_CTR_DIV45_N`, comparator trim, DLL resistance, PLL DAC, phase selection lock, vreg gain, and test boost. `CREG0_OVRD` and `CREG1_OVRD` are all-reserved override registers in this slice.
- `C20_PHY_CR2_RAWCMN_DIG_CMN_CTL`, `CMN_CLK_GATE_CTL`, and `CMN_CTL_1` define common PHY reset, CREG clock-gating override, MPLLA/MPLLB initial calibration and SSC overrides, HDMI mode enable override, and rtune request override.
- `C20_PHY_CR2_RAWCMN_DIG_ATE_ALU_*` defines a small test/ATE ALU surface: opcode, address, data, accumulator sign flag, and accumulator value.
- `C20_PHY_CR2_RAWCMN_DIG_FW_*`, `STATIC_CONFIG_STATUS`, and `CMN_STATUS_1` provide firmware power-up, internal/static configuration, common calibration, external rtune, and vgen calibration done bits.
- `C20_PHY_CR2_RAWCMN_DIG_MPLL_*` and `MPLLA/MPLLB_FRAC_UPDATE` cover MPLL off/force-on timing, input state, async clock overrides, recalibration bank/force/skip override values for MPLLA/MPLLB, and atomic fractional configuration update enables.
- `C20_PHY_CR2_RAWCMN_DIG_*_CNTX_CFG_*` defines context data for supervisor settings and MPLLA/MPLLB programming. MPLLA fields include multiplier, dividers, bandwidth threshold/low/high, SSC peak/step values, fractional enable, LC frequency select, reference clock divider, fractional denominator/quotient/remainder. MPLLB has analogous fields plus CP/V2I/frequency, calibration DAC code, and HDMI divider/pixel clock divider fields.
- `C20_PHY_CR2_RAWCMN_DIG_AON_MPLLA/MPLLB_*` defines always-on tune control, four tune banks per MPLL, calibration bank selection, tune done, in-recalibration indicators, and PMA recalibration bank selection.
- `C20_PHY_CR2_RAWCMN_DIG_AON_RTUNE_*` exposes per-lane rtune readback values for RX, TXDN, and TXAVG for lanes 0 through 7.
- `C20_PHY_CR2_RAWCMN_DIG_AON_SRAM_*`, `AON_FW_VERSION_*`, `AON_RAW_VERSION`, `AON_SUP_CTL_*`, `AON_APB_CFG_*`, and `AON_SUP_STATUS_0` define always-on firmware/SRAM boot, bypass, init done, recovery address, firmware version, raw version, supervisor clock/power/ref-clock override, APB address mode, and power/clock status fields.
- `C20_PHY_CR2_LANE0_DIG_ASIC_LANE_*`, `TX_*`, and `RX_*` define lane0 ASIC transfer and override buses. Most override registers pair a value field with an `_OVRD_EN` bit, allowing lab/firmware/driver paths to force signals that normally come from PHY automation.
- `C20_PHY_CR2_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2` and `RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2` define per-power-state enable templates for analog bleeders, AFE/clock/vreg/divider/CDR/DFE blocks, VCO resets, continuous calibration, digital clock, bypass paths, data enables, refgen, and low-power or request behavior.
- `C20_PHY_CR2_LANE0_DIG_TX_PWRCTL_TX_PWRUP_TIME_*` and `RX_PWRCTL_RX_PWRUP_TIME_*` define sequencer timing fields for rate changes, voltage regulator startup, reference generator, divider/clock enable/disable, serial/data paths, DCC, resets, low-power request, and fast-start flags.
- `C20_PHY_CR2_LANE0_DIG_TX_PWRCTL_TX_CTL`, `TX_STATUS`, `RX_PWRCTL_RX_CTL`, and the following RX continuation define manual control/status for TX/RX clocks, calibration DAC writes, skip paths, rate IRQs, request FSM state, and power FSM state.
- `C20_PHY_CR2_LANE0_DIG_TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, `TX_LVL_CALC_STAT`, and `TX_FIFO_CTL` define TX DCC offset/status, test/statistic counters, calibration compare clock control, clock alignment control/status, loopback BERT controls and patterns, level-calculation status, and FIFO reset.
- `C20_PHY_CR2_LANE0_DIG_ANA_XF_TX_*` defines TX analog transfer registers: override outputs for analog enables/resets/data rate/ref selection/vboost/rxdet, termination code override, DCC calibration enable/config/selection/range/data, EQ override/readback, TX status in/out, and analog configuration registers `TX_ANA_CREG00` through `TX_ANA_CREG05`.
- `C20_PHY_CR2_LANE0_DIG_ASIC_RX_OVRD_*`, `RX_ASIC_*`, and `RX_EQ_ASIC_*` define RX ASIC override and readback fields for reset/request/data/rate/width/pstate/CDR/DFE/flyover/signal detect, RX VCO and reference load values, ACK/adaptation status, CDR frequency, DCC, EQ adaptation, CTLE, IQ, phase, VGA, DFE, AFE bias, and AFE CTLE offset.

## Control Flow And State Behavior

This header has no executable control flow. Runtime behavior comes from code that includes the generated header and passes these macros to helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `get_reg_field_value()`, `set_reg_field_value()`, or DMUB register helpers. Those helpers read a register value, clear bits under a `_MASK`, shift a field value by `__SHIFT`, and write or return the resulting field.

The state represented by this chunk is hardware register state:

- Persistent programmed state includes MPLLB analog tuning values, common reset and clock-gate overrides, calibration-disable/SSC/HDMI/rtune override bits, MPLL context registers, supervisor context fields, tune-bank data, SRAM/APB/supervisor controls, lane0 TX/RX ASIC override values, power-state templates, power-up timers, TX/RX manual controls, TX DCC and EQ override values, analog configuration registers, and RX EQ/AFE override values.
- Volatile readback includes firmware power-up/configuration/calibration done bits, AON firmware/raw version, SRAM init done, in-recalibration state, rtune values, supervisor power/clock status, lane0 ASIC TX/RX output state, TX/RX status FSM state, DCC/stat/clock-align/LBERT/FIFO status, TX analog status, RX ACK/adaptation/CDR/EQ/VCO status, and calibration result fields.
- Side-effecting fields are present despite the header being declarative. They include common reset, fractional update enables, recalibration force/skip overrides, SRAM boot/recovery controls, supervisor firmware stop and clock requests, self-clearing TX load/term/update controls, TX/RX DCC DAC write enables, TX/RX calibration override gates, TX FIFO reset, clock alignment controls, and skip/force fields that can change PHY training behavior.

Typical runtime flows using these definitions:

1. PHY common bring-up programs `RAWCMN_DIG_*` context and AON controls, waits for firmware/static/common calibration done fields, and uses version/status readbacks to confirm firmware/SRAM readiness.
2. MPLLA/MPLLB configuration writes context fields, fractional denominator/quotient/remainder, SSC parameters, reference dividers, and tune-bank controls, then monitors tune done, in-recalibration, and selected bank fields.
3. Lane0 TX bring-up selects power-state template values, sequences power-up timing fields, enables TX clocks/data/refgen/serial paths, programs DCC/EQ/termination/analog settings, and reads TX status or clock-align status.
4. Lane0 RX bring-up selects RX power-state templates and timing values, configures signal-detect/CDR/VCO/EQ/DFE/CTLE/AFE override paths as needed, then reads ACK/adaptation/EQ/AFE status.
5. Debug and manufacturing paths use the ATE ALU, LBERT patterns, TX statistic counters, analog status buses, rtune readbacks, firmware version fields, and broad override registers to isolate PHY behavior without changing higher-level DC display logic.

## Dependencies And Integration Points

This chunk depends on exact consistency with the rest of the generated DCN 3.2.0 register database. The shift/mask names here are meaningful only with the matching register offsets, generated field lists, and display register helper layer. The top of this header identifies it as `dcn_3_2_0_sh_mask.h`; DCN 3.2 display code includes it together with `dcn_3_2_0_offset.h`.

Important integration points:

- AMD Display Core register helpers in `drivers/gpu/drm/amd/display/dc/dm_services.h`, where `get_reg_field_value()`, `set_reg_field_value()`, and `FD()` expect the exact generated `__SHIFT` and `_MASK` suffixes used here.
- DMUB register helpers in `drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h`, which use the same shift/mask pairing pattern for display microcontroller register access.
- DCN 3.2 display modules that include this header, including clock manager, resource construction, IRQ, GPIO, hubbub, link encoder, stream encoder, timing, and DMUB support code. Even when ordinary C code does not directly name these CR2 PHY fields, the generated header is part of the same compiled register ABI used by platform-specific and low-level PHY sequences.
- The matching `dcn_3_2_0_offset.h` C20 PHY CR2 offset namespace. This chunk supplies field layouts; the offset header supplies register addresses such as the CR2 lane and raw-lane address space.
- Firmware and hardware contracts for PHY bring-up, link training, retuning, recalibration, suspend/resume, and lab diagnostics. Many fields here mirror firmware-facing handshakes or AON firmware status.

## Risks And Maintenance Notes

- Numeric correctness is the core risk. Wrong shifts or masks compile cleanly but can write adjacent PHY fields, reserved bits, or side-effecting bits, producing link training failures, intermittent blanking, unstable high-rate links, bad HDMI/DP clocking, or resume-only faults.
- The range is dense with 16-bit analog and PHY-control fields. Adjacent one-bit and small multi-bit fields are common, so off-by-one masks can corrupt PLL, DCC, VCO, CTLE, DFE, IQ, phase, and termination controls.
- Similar names are easy to confuse: MPLLA vs MPLLB, common vs lane0, ASIC vs analog transfer buses, override input vs ASIC input vs ASIC output, TX vs RX, status vs control, full-rate vs half-rate, and P0/P0S/P1/P2 power-state templates.
- Side-effecting update, reset, force, skip, self-clear, and write-enable fields require extra care. A bad mask can leave calibration skipped, repeatedly trigger DAC writes, hold common reset, disable firmware/SRAM paths, or hide PHY status from interrupt/training code.
- Chunk boundaries are incomplete. `C20_PHY_CR2_SUP_DIG_ANA_XF_MPLLB_ANA_CREG05` and `C20_PHY_CR2_LANE0_DIG_RX_PWRCTL_RX_CTL` should not be treated as fully documented from this slice alone.
- Manual edits should be avoided unless backed by an authoritative hardware-spec or generated-register update. This file is effectively an ABI between AMDGPU, display firmware/DMUB-facing flows, and DCN 3.2.0 hardware.

## Test Signals

Useful validation is mostly build-time generated-header checking plus hardware exercise:

- Build AMDGPU Display Core with DCN 3.2 support and confirm the matching offset and shift/mask headers compile anywhere DCN 3.2 register field lists are instantiated.
- Run generated-register consistency checks that each complete in-scope register has paired `_SHIFT` and `_MASK` definitions, masks fit the expected 16-bit or wider register width, adjacent fields do not overlap unexpectedly, and repeated families match the hardware spec.
- Compare numeric values against the authoritative DCN 3.2.0 C20 PHY CR2 register specification, prioritizing common reset, AON firmware/SRAM status, MPLL context/fractional/tune-bank fields, TX/RX power-state templates, power-up timers, DCC/EQ/AFE controls, and side-effecting write/clear/update bits.
- Exercise display hotplug, link training, retraining, suspend/resume, and mode changes on DCN 3.2 hardware. Watch for black screens, flicker, link-rate fallback, repeated PHY resets, firmware calibration timeouts, or unstable high-bandwidth modes.
- For TX validation, inspect TX power FSM status, rate IRQs, DCC status, statistic counters, clock alignment status, termination code, EQ override/readback, analog status out, and LBERT operation when available.
- For RX validation, inspect RX request/ack/adaptation status, CDR/VCO/DFE/EQ/CTLE/AFE readbacks, signal-detect threshold behavior, RX power FSM state, and calibration DAC/write paths across link-rate and power-state transitions.
- For common/AON validation, read firmware version, raw version, SRAM init done, configuration/calibration done, rtune values, supervisor status, and MPLL tune/recalibration fields before and after PHY power-up and resume.

## Chunk-Specific Summary

Lines 124777-127187 define generated shift/mask constants for the DCN 3.2.0 C20 PHY CR2 MPLLB analog tail, raw common digital and always-on firmware/SRAM/MPLL/rtune controls, lane0 ASIC TX/RX transfer registers, lane0 TX power/control/calibration/stat/debug/analog fields, and the beginning of lane0 RX power-control fields. The content is declarative register ABI, not executable logic. Correctness depends on exact generated values, matching offset-header integration, and hardware validation of PHY bring-up, MPLL tuning, TX/RX calibration, status readback, and power-state transitions.
