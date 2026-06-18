# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 71762-74174

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask register-definition slice. It contains no executable C code, no functions, no structs, and no enums. Its exported interface is a large set of preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; AMDGPU Display Core code combines these field layouts with the matching DCN 4.1.0 register offsets to access individual MMIO fields through register helper macros.

The requested range contains 2,158 `#define` entries: 1,082 shift macros and 1,076 mask macros, plus 255 `//<REGISTER>` group comments. The line boundaries are artificial chunk boundaries rather than hardware-block boundaries. The first group starts with only the mask half of `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`; the shifts for that register are immediately before line 71762. The last group stops inside the shift half of `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_ATE_TX_OVRD_IN`; its remaining shift and mask definitions continue after line 74174.

Functionally, the chunk documents a large part of DPCS/display PHY control and status for DCN 4.1.0:

- Lane 3 digital ASIC TX/RX override, ASIC input/output, TX power-control, RX statistics, digital-to-analog TX override/status, and lane 3 analog TX trim/control fields.
- Raw common DPCS fields for PHY reset, MPLLA/MPLLB override, spread-spectrum/fractional controls, common MPLL state, SRAM/init/status, always-on common RTUNE values, power-gating overrides, resource handshakes, reference range, and support analog overrides.
- Raw lane 0 PCS, PMA, FSM, IRQ, TX control, and RX control field definitions, including ATE/test overrides and RX adaptation/equalization telemetry.

Although this source tree is under a `ceph-client` mirror, this file is AMDGPU Display Core hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important API surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit index of a field inside a 16-bit-style DPCS register word represented in the register tables.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.

Important register families in the chunk are:

- `DPCSSYS_CR0_LANE3_DIG_ASIC_*`: lane 3 digital ASIC-facing lane/TX/RX override and observation fields. These include loopback enables, TX request/ack, reset, power state, rate, width, MPLL select, data enable, main/pre/post cursor values, HDMI mode, detect-RX request/result, polarity inversion, low-power-disable, DC coupling, MPHY mode, IBOOST/RBOOST, lane transceiver mode, async/beacon controls, TX/RX ACK and adapt status, and master-lane/repeater/digital-clock coordination fields.
- `DPCSSYS_CR0_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX power-state and timing fields for P0, P0S, P1, and P2. Each power state encodes analog reference generator, VCM hold, analog/word clocks, analog reset, serial enable, digital clock, data enable, RX detect allowance, DCC compensation, and P2-only VBOOST allowance. The power-up timing registers encode refgen/clock delays, VCM hold timing, VBOOST disable timing, RX detect timing, reset timing, serial-enable timing, and fast RX detect.
- `DPCSSYS_CR0_LANE3_DIG_TX_PWRCTL_DCC_*`: DCC compensation control-bank address/data and DAC control/range/selection/ack/address fields.
- `DPCSSYS_CR0_LANE3_DIG_TX_CLK_ALIGN_TX_CTL_0` and `DPCSSYS_CR0_LANE3_DIG_TX_LBERT_CTL`: TX clock alignment and lane-BERT controls.
- `DPCSSYS_CR0_LANE3_DIG_RX_STAT_*`: RX statistic load/data/mask/match/control/counter fields, sample count, calibration comparison clock control, and statistic stop control.
- `DPCSSYS_CR0_LANE3_DIG_ANA_*` and `DPCSSYS_CR0_LANE3_ANA_TX_*`: digital-to-analog TX controls and analog TX trim/status. These cover analog clock/data/refgen/reset/serial enable, MPLLA/MPLLB clocks, data rate, RX detect, termination code and clocking, equalization leg-pull/pre/post/mux controls, DCC DAC calibration, fast start, AC JTAG, loopback, ATB measurement muxes, DCC controls, term-code update/reset, word-clock/MPLL clock overrides, VREG control, boost controls, VPTX power gate, and reserved trim fields.
- `DPCSSYS_CR0_RAWCMN_DIG_*`: raw common DPCS control for PHY function reset, MPLLA/MPLLB override values/enables, bandwidth override, SSC range/clock/enables, fractional controls, lane FSM extension, common reset/calibration/RTUNE requests, HDMI mode and PWM clock override, MPLL state timing/bank selection, SRAM init, OCLA probing, support analog overrides, raw/firmware ID code fields, and TX calibration code.
- `DPCSSYS_CR0_RAWCMN_DIG_AON_CMN_*`: always-on common RTUNE readbacks for RX/TXDN/TXUP values 0-7, SRAM bitline config, PMA/PCS power-gating overrides, common support override/ack signals, VREF calibration status, resource request/ack override and observation, reference range override, MPLL power-down timing, and support analog REXT override controls.
- `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_*`: raw lane 0 PCS transfer fields for TX/RX overrides and actual PCS inputs/outputs, reset/request/ack, pstate/rate/width/LPD, MPLL selection/enable/state, detect-RX, VBOOST/IBOOST/beacon, RX LOS threshold, adaptation control, CDR VCO/ref load values, RX equalizer AFE/DFE/CTLE telemetry and override, RX adaptation ACK/FOM, RX-directed TX pre/main/post requests, lane number, ATE override, termination control, phase-2 calibration, and PCS reserved words.
- `DPCSSYS_CR0_RAWLANE0_DIG_FSM_*`: raw lane 0 firmware/state-machine controls and monitors, including jump address, command start, override enable, break, memory address monitor, status monitor, many fast-state shortcut registers for RX startup/adapt/calibration/power-up/VCO/continuous adaptation, TX common-mode/RX detect, flags, CR lock, TX DCC flags/status, TX EQ update, calibration status, and RX IQ phase offset.
- `DPCSSYS_CR0_RAWLANE0_DIG_IRQ_CTL_*`: reset-return request, RX reset/request/rate/pstate/adapt/phase2/lane-loopback IRQ status and clear fields, DCC on-demand/TX reset/TX request IRQ status and clear fields, and IRQ mask fields.
- `DPCSSYS_CR0_RAWLANE0_DIG_PMA_XF_*`, `DPCSSYS_CR0_RAWLANE0_DIG_TX_CTL_*`, and `DPCSSYS_CR0_RAWLANE0_DIG_RX_CTL_*`: raw lane 0 PMA transfer overrides and PMA inputs, PMA lane and support override/ack, TX PMA reset/request/rate/width/pstate/data/loopback/term/mode/boost/DC coupling controls, RX PMA request/reset/data/termination/PWM/async/adaptation controls, retune request/ack, TX/RX FSM/control timing, DCC/adapt/offcan status, LOS mask timing, and UPCS OCLA data/clock fields.

## Control Flow

This header slice has no local control flow. Runtime control flow is supplied by AMDGPU Display Core and DCN401-specific code that includes this generated header:

1. DCN 4.1.0-specific modules include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register-table macros token-paste register and field names into ASIC-specific address/shift/mask tables.
3. DC register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the offset, shift, and mask entries to construct MMIO read/modify/write operations.
4. Link-encoder, PHY, IRQ, clock-manager, DMUB, GPIO, and resource code performs the actual sequencing for link bring-up, link training, power-state changes, IRQ masking/clearing, firmware or state-machine control, and diagnostic readback.

The macros themselves do not encode sequencing rules. Consumers must still observe hardware-required ordering around PHY reset, MPLL power and calibration, TX/RX request/ack handshakes, rate/width/pstate changes, RX adaptation, DCC/termination updates, IRQ clear/mask ordering, and test/ATE override enablement.

## State And Persistence Behavior

This chunk stores no software state. It defines the bit layout for persistent or observable hardware register state in the DCN 4.1.0 DPCS blocks.

State represented by these fields includes:

- Lane 3 TX/RX operating state: request/ack, reset, data enable, rate, width, power state, low-power disable, MPLL selection, data polarity, HDMI/MPHY mode, detect-RX request/result, async/beacon, loopback, and lane-master clock/shift coordination.
- Lane 3 analog TX state: refgen, VCM hold, clock enable, word clock, MPLLA/MPLLB clock enables, reset, serial enable, data rate, RX detect, termination code, driver source, equalization, DCC calibration, VREG, boost, ATB measurement, and AC JTAG/debug controls.
- Common DPCS state: PHY function reset, MPLLA/MPLLB override and state, spread spectrum, fractional controls, MPLL off/force-on timing, SRAM/init status, common RTUNE values, power-gating override/ack state, reference range, resource request/ack, support analog settings, firmware/raw IDs, and OCLA probe selection.
- Raw lane 0 PCS/PMA state: TX/RX reset/request/ack, pstate/rate/width, data enable, PMA term controls, PMA mode and boosts, RX adaptation and equalization, VCO/ref load values, phase-2 calibration, lane number, ATE overrides, FSM monitor/control state, IRQ status/clear/mask state, and TX/RX control FSM settings.

Persistence is hardware-defined. Configuration and override fields generally remain until driver reprogramming, link reset/retrain, modeset, suspend/resume, runtime power transition, GPU reset, or ASIC reset. Status, ACK, IRQ, calibration, counter, monitor, and clear fields can be read-only, sticky, self-clearing, write-one-to-clear, or only valid while the relevant power domain is active. This generated header does not identify access permissions or side effects; those rules must come from the hardware spec and the consuming driver sequence.

## Dependencies And Integration Points

- The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which supplies matching register addresses. The shift/mask macros are meaningful only when paired with the correct DCN 4.1.0 offsets and register-instance layout.
- DCN401 code includes this header from `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, `display/dc/gpio/dcn401/`, and `display/dc/resource/dcn401/dcn401_resource.c`.
- Link-encoder register descriptions in older DCN code demonstrate the integration pattern for these DPCS names: macros such as `LE_SF(...)` and `SRI_IX(...)` token-paste register names and fields like `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_2__VCO_LD_VAL_OVRD` into register table entries.
- The lane 3 definitions integrate with per-lane PHY/link programming for TX power-state sequencing, link training, RX detect, loopback, equalization, DCC calibration, analog trim, and debug/ATE support.
- The raw common definitions integrate with shared PHY services: MPLL control, common reset, clocking, spread-spectrum control, SRAM/init status, RTUNE, power-gating handshakes, common resource requests, and support analog calibration.
- The raw lane 0 PCS/PMA/FSM/IRQ definitions integrate with link bring-up, RX adaptation, IRQ service, firmware or micro-sequencer control, PMA/PCS test hooks, and diagnostics. Raw-lane prefixes are important because similar field shapes are repeated per lane or per generation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A bad mask or shift can compile successfully while silently programming the wrong MMIO bits.
- Offset/header drift is the main generated-metadata risk. A correct mask paired with a stale `dcn_4_1_0_offset.h` address, or the reverse, can corrupt unrelated PHY state.
- The chunk boundaries are not semantic. `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` is incomplete at the start, and `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_ATE_TX_OVRD_IN` is incomplete at the end. Whole-register conclusions require adjacent chunks.
- Many registers mix value bits with override-enable bits. Setting an override value without its enable has no effect; setting an enable with the wrong value can force invalid PHY/link state.
- Full-register writes are risky because packed registers include control, status, reserved, ACK, clear, monitor, and enable fields. Read/modify/write helpers are expected unless a caller intentionally owns the full word.
- Pstate/rate/width/MPLL fields are link-critical. Misprogramming them can produce link-training failures, blank displays, unstable high-bandwidth modes, or failures only on specific connector speeds.
- Power-state, reset, VCM hold, serial enable, and RX-detect timing fields are sequence-sensitive. Incorrect delays or state bits can produce intermittent failures during hotplug, resume, link retrain, or low-power transitions.
- Analog trim/equalization/DCC/termination fields are signal-integrity-sensitive. Wrong values can pass basic display tests but fail under long cables, high rates, marginal boards, or temperature/voltage variation.
- IRQ status/clear/mask fields can be edge-sensitive or write-one-to-clear. Treating clear registers like ordinary status registers can drop interrupts or leave storms masked.
- ATE, OCLA, FSM override, loopback, AC JTAG, and test controls should not leak into normal runtime paths; stale debug overrides can make failures highly board- or boot-order-dependent.
- Reserved and `NC` fields appear throughout the chunk. Drivers should preserve them unless the hardware database explicitly requires a write value.

## Test Signals

Useful validation combines generated-header integrity checks with DCN 4.1.0 hardware behavior:

- Build AMDGPU Display Core with DCN401 enabled. Missing, malformed, or renamed macros should fail in DCN401 DMUB, IRQ, clock-manager, GPIO, resource, and link/register-table compilation paths.
- Mechanically compare this chunk against the authoritative DCN 4.1.0 register database and `dcn_4_1_0_offset.h`, including adjacent chunks for the partial first and last register groups.
- Run static consistency checks that every complete register group in this range has matching `__SHIFT` and `_MASK` pairs and that masks align with their shifts and field widths.
- Exercise link training and modesets across supported connector types and link rates, with special attention to pstate/rate/width/MPLL selection, TX request/ack, RX detect, reset, data enable, and low-power transitions.
- Validate hotplug, unplug/replug, suspend/resume, runtime PM, and GPU reset paths while checking that TX/RX power-state and reset handshakes recover without stuck ACK, IRQ, or adaptation bits.
- Run high-bandwidth and marginal-link scenarios to expose equalization, DCC, termination, VBOOST/IBOOST/RBOOST, VREG, and RX adaptation field mistakes.
- Exercise IRQ service paths for RX reset/request/rate/pstate/adapt/phase2, lane loopback, DCC on-demand, TX reset, and TX request events; confirm masks and clear registers do not lose or storm interrupts.
- Use diagnostics or hardware validation tooling to read back RX statistic counters, FSM monitors, calibration status, RTUNE values, VREF status, OCLA selections, and ID fields.
- Verify that normal runtime paths leave ATE, loopback, FSM override, AC JTAG, OCLA, and other debug/test controls disabled unless an explicit diagnostic path enables them.

## Cross-Chunk Notes

The previous chunk contains the shift definitions for `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` and preceding lane 2 analog RX fields. The next chunk contains the remainder of `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_ATE_TX_OVRD_IN`, including its masks, and continues later DPCS register groups. The final per-file report should reconcile these boundaries before making complete-file claims about all DCN 4.1.0 DPCS lane/common/register coverage.
