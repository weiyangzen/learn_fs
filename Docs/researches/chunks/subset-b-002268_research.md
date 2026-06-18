# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 21928-24369

## Scope

This chunk is part of AMD's generated DPCS 3.1.4 register shift/mask header. It contains only preprocessor constants for DisplayPort/PHY control-system bitfields: every field is represented by a `...__SHIFT` bit position and a matching `..._MASK` value. There are no functions, structs, enums, variables, includes, branches, locks, allocations, or direct MMIO operations in this range.

The requested slice contains 2,144 `#define` lines: 1,072 shift macros and 1,072 mask macros across 292 distinct register-name prefixes. It starts at an artificial boundary with two trailing masks for `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT`, covers lane-2 analog control tail, the lane-3 ASIC/TX/RX-stat/analog subset, CR1 raw common PLL/AON controls, and the beginning of rawlane0 PCS/FSM/IRQ/PMA interfaces. It ends inside `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`, after the first two RX PMA override shift fields.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Purpose

The purpose of this range is to publish exact bitfield metadata for DPCS CR1 lane and raw PHY registers used by AMD display link/PHY code. Runtime code pairs these field constants with matching register offsets from `dpcs_3_1_4_offset.h` and AMD display register helpers to perform masked reads, writes, updates, polls, and status extraction without hard-coded bit arithmetic.

Important covered surfaces:

- Lane-2 analog TX/RX controls: TX analog override outputs, termination code override, equalization/pre/post cursor fields, DCC DAC override, TX power/ATB/misc controls, RX analog power/control overrides, CDR/VCO tuning, calibration DAC controls, AFE attenuation/VGA/CTLE, slicer/scope controls, IQ phase/sense controls, signal-detect overrides, and analog status mirrors.
- Lane-3 digital ASIC and analog TX controls: lane override inputs, TX override inputs and ASIC input mirrors, RX override output/status mirrors, lane-3 TX power-state programming, TX power-up timing, DCC controls, clock alignment, LBERT, RX statistic match/counter controls, and analog TX override/direct analog fields.
- CR1 raw common controls: common enable bits, MPLLA/MPLLB override and spread-spectrum controls, lane FSM extension, CMN control, MPLL state, TX calibration code, SRAM init status, OCLA, supervisor analog overrides, PCS/FW ID words, AON RTUNE RX/TXDN/TXUP values, AON SRAM/power-gate/supervisor/resource overrides, VREF status, reference range, and miscellaneous common configuration.
- Rawlane0 PCS transfer controls: TX/RX PCS override inputs, live PCS input/output mirrors, RX adaptation acknowledge/FOM and TX pre/main/post direction fields, lane number/reserved fields, ATE override, RX equalization override, TX/RX termination controls, and phase-2 calibration controls.
- Rawlane0 FSM/IRQ/PMA controls: FSM override/status and fast-state monitors, TX DCC flags/status, calibration status, RX IQ phase offset, RX/TX request/rate/pstate/adaptation/loopback/DCC interrupt status and clear fields, IRQ masks, PMA lane/supervisor override inputs/outputs, TX PMA override output, TX PMA acknowledge, and the beginning of RX PMA override output.

## Important APIs, Types, And Macros

There are no typed C APIs in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used by register helpers to preserve unrelated fields during read-modify-write.
- Register comments such as `//DPCSSYS_CR1_RAWCMN_DIG_MPLLA_OVRD_IN` delimit generated register blocks and match `ixDPCSSYS_...` names in the offset header.

Major macro families include:

- `DPCSSYS_CR1_LANE2_DIG_ANA_*` and `DPCSSYS_CR1_LANE2_ANA_*` for lane-2 analog TX/RX override, direct analog, DCC, termination, equalization, calibration, and status fields.
- `DPCSSYS_CR1_LANE3_DIG_ASIC_*`, `DPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_*`, `DPCSSYS_CR1_LANE3_DIG_RX_STAT_*`, and `DPCSSYS_CR1_LANE3_DIG_ANA_*` for lane-3 ASIC-facing signal handoff, power control, RX statistics, and analog TX controls.
- `DPCSSYS_CR1_RAWCMN_DIG_*` and `DPCSSYS_CR1_RAWCMN_DIG_AON_CMN_*` for common raw DPCS PLL, spread-spectrum, SRAM, firmware identity, OCLA, supervisor, RTUNE, VREF, power-good, reset, isolation, resource-request, reference-range, and REXT fields.
- `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_*` for rawlane0 PCS-side TX/RX override, PCS input/output mirrors, adaptation feedback, term-control, ATE, equalization, and phase-2 calibration fields.
- `DPCSSYS_CR1_RAWLANE0_DIG_FSM_*` for rawlane0 FSM override, memory address/status monitoring, fast calibration/adaptation state flags, TX DCC flags/status, TX EQ update flag, CMN calibration status, and RX IQ phase offset.
- `DPCSSYS_CR1_RAWLANE0_DIG_IRQ_CTL_*` for lane IRQ status, clear, and mask bits covering RX reset/request/rate/pstate/adaptation, lane transceiver mode, phase-2 calibration, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request events.
- `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_*` for PMA-side lane/MPLL supervisor handshakes, TX PMA request/reset/beacon/async/data-enable overrides, TX acknowledge, and the start of RX request override metadata.

The instance prefixes are semantically significant. Lane-2 and lane-3 fields describe different physical lanes, `RAWCMN` describes shared common PHY resources, and `RAWLANE0` describes the first raw lane interface. The same-looking bit layouts must remain paired with their matching offsets and resource instances.

## Control Flow

This header has no executable control flow. Runtime flow is created by consumers that include this file with the matching offset header and expand register/field names into register tables.

Typical use is:

1. DPCS 3.1.4-aware AMD display code includes `dpcs_3_1_4_offset.h` for `ixDPCSSYS_*` register addresses and `dpcs_3_1_4_sh_mask.h` for field positions and masks.
2. Register-list macros or block-specific tables token-paste register and field names into descriptors.
3. Runtime paths call AMD register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, or polling/wait helpers.
4. Link, PHY, diagnostics, and power-management code uses the generated constants while programming DisplayPort lanes, PLLs, analog tuning, calibration, statistics, interrupts, and PMA/PCS handshakes.

The hardware programming order is not encoded here. Consumers must still sequence resets, power states, reference clocks, MPLLA/MPLLB selection, analog overrides, calibration, RX adaptation, statistic sampling, IRQ clearing, and PMA/PCS handshakes according to the DPCS hardware model.

## State And Persistence Behavior

The file itself stores no mutable or persistent software state. All represented state lives in hardware registers.

Hardware-backed state described by this chunk includes:

- Lane-2 analog TX/RX override and status state: clocks, data enable, reference generator, VCM hold, PLL clock enables, resets, serial enable, data rate, RX detect, termination, equalization leg pull controls, pre/post cursor controls, DCC DAC values, power controls, CDR/VCO settings, calibration modes, AFE/CTLE settings, slicer/scope controls, signal-detect settings, and ATB measurement selections.
- Lane-3 lane/ASIC and TX/RX state: TX request/reset/pstate/rate/width, MPLL selects/enables, low-power disable, beacon/async controls, VBOOST/IBOOST, RX detect/valid/signal-detect, TX power-state and timing controls, RX statistic counters and match controls, and analog TX override/direct state.
- Raw common state: common enables, MPLLA/MPLLB overrides and acknowledgements, spread-spectrum control, firmware/PCS IDs, SRAM init, supervisor analog overrides, RTUNE values for RX and TX termination, AON power-good/reset/isolation overrides, VREF status, resource request/ack, reference range, and miscellaneous common configuration.
- Rawlane0 PCS/FSM/IRQ/PMA state: PCS TX/RX request/rate/width/pstate and override state, adaptation feedback and FOM, termination controls, phase-2 calibration, FSM fast-state flags, TX DCC status, CMN calibration status, IRQ status/clear/mask bits, PMA lane/supervisor state, TX PMA overrides, TX acknowledge, and the first RX PMA override fields.

Persistence is hardware-defined. Configuration and override fields generally remain programmed until another link-training, modeset, diagnostics, suspend/resume, power-gating, display-engine reset, GPU reset, or ASIC reset path rewrites them. Status, ack, done, pending, interrupt, clear, and calibration fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant common/lane clocks and power domains are active. This generated header does not encode those access semantics.

## Dependencies And Integration Points

Direct dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies the matching `ixDPCSSYS_*` register offsets, including lane-2 analog registers around `0x12a0`, lane-3 registers around `0x1300`, raw common registers around `0x2000`, and rawlane0 PCS/FSM/IRQ/PMA registers starting around `0x3000`.
- AMD display register-helper infrastructure supplies the masked register access macros that consume `__SHIFT` and `_MASK` symbols.
- AMD's DPCS 3.1.4 register database is the authoritative source for the generated names and bit positions.

Important integration points:

- DisplayPort link and PHY programming paths use the lane and rawlane fields for lane enablement, rate/width selection, TX/RX requests, reset handshakes, power-state transitions, PLL selection, and PMA/PCS signal handoff.
- PHY analog tuning and calibration paths use termination, DCC DAC, equalization, AFE, CTLE, CDR/VCO, slicer, phase, VREF, RTUNE, and calibration-status fields.
- Diagnostics, bring-up, and factory/test flows use RX statistic counters, pattern match controls, LBERT, OCLA, ATB controls, ATE overrides, DCC status, TX EQ update flags, and raw FSM monitors.
- Interrupt and event handling paths use the rawlane0 IRQ status, clear, and mask fields for RX/TX requests, resets, pstate/rate changes, adaptation requests/disables, phase-2 calibration events, lane transceiver mode events, loopback events, and DCC on-demand events.
- Low-power, suspend/resume, hotplug, and reset flows depend on correct power-good, isolation, reset, resource request/ack, SRAM init, MPLL, and PMA/PCS supervisor fields.

## Risks And Failure Modes

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting an adjacent hardware field in the same register.
- Chunk boundaries are not semantic. This range begins with masks whose shifts are in the previous chunk and ends before the masks for `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`; final per-file reconciliation must merge neighboring chunks.
- Lane instance alignment is critical. Accidentally pairing `LANE2`, `LANE3`, `RAWCMN`, or `RAWLANE0` field constants with the wrong offset can program a different physical lane or a shared common resource.
- Override-enable fields are high risk. Leaving TX/RX analog, PCS, PMA, PLL, power, or supervisor overrides asserted after test or training can force stale state and break later hotplug, retraining, suspend/resume, or modeset paths.
- PLL, reference-clock, power-good, isolation, and reset fields are sequencing-sensitive. Writes while the target block is off or unstable can be ignored, produce stuck waits, or create transient hardware states not represented in this header.
- Analog tuning fields are hardware-sensitive. Bad termination, DCC DAC, equalization, AFE/CTLE, CDR/VCO, VREF, RTUNE, slicer, or phase masks can cause link training failures, high-rate signal integrity problems, or lane-specific display instability.
- Status, clear, and IRQ fields need correct access semantics in callers. Misusing write-one-to-clear, self-clearing, sticky, or read-only fields can lose events or leave stale interrupts asserted.
- RX statistic and diagnostic fields can produce false validation if counters, stop bits, match masks, or sample status are read while clocks are gated or while the lane is not in the expected state.

## Test Signals

Useful validation signals include:

- Build AMDGPU display support with DPCS 3.1.4 headers enabled. Missing or renamed macros should fail in register-table, link, PHY, diagnostics, or interrupt code that references these DPCSSYS fields.
- Mechanically verify shift/mask pairing for lines 21928-24369, allowing the known boundary cases at `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT` and `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`.
- Diff this range against AMD's authoritative DPCS 3.1.4 register database and the matching `dpcs_3_1_4_offset.h` so every field name maps to the intended register offset and instance.
- Exercise DisplayPort link training/retraining across lane counts that include lanes 2 and 3, multiple rates, hotplug, HPD IRQ, suspend/resume, display-engine reset, GPU reset, and low-power transitions.
- Validate analog and calibration paths by monitoring DCC, termination, EQ, AFE/CTLE, CDR/VCO, signal-detect, VREF, RTUNE, CMN calibration, and phase-2 calibration status on real hardware.
- Exercise rawlane0 PCS/PMA handshakes and IRQ flows: RX/TX request/reset, rate and pstate changes, adaptation request/disable, phase-2 calibration request/disable, lane transceiver mode, RX-to-TX loopback, DCC on-demand, IRQ mask/unmask, and clear behavior.
- Use diagnostics such as RX statistic counters, match controls, LBERT, OCLA, ATB, TX DCC status, TX EQ update flag, and FSM fast-state monitors. Expected signals are no stuck waits, no unexpected IRQ storms, stable link training, correct lane power state, and no failures isolated to lane 2, lane 3, or rawlane0.

## Cross-Chunk Notes

This is a source-tree-aligned chunk report only. The previous chunk is needed for the complete `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT` register, and the next chunk is needed for the rest of `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT` and later rawlane0 PMA/TX/RX control fields. The final per-file report should merge adjacent chunks before making complete claims about the full `dpcs_3_1_4_sh_mask.h` namespace.
