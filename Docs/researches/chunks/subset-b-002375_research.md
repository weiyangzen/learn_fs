# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 90537-92913

## Scope And Purpose

This chunk is generated AMD DPCS 4.2.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to encode, update, and decode fields in the DPCS `CR4` PHY/control-register space. Runtime display-driver code pairs these `*_SHIFT` and `*_MASK` constants with the matching register offsets from `dpcs_4_2_2_offset.h` and AMD display register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, `SR`, and `SRI`.

The requested range starts inside the `DPCSSYS_CR4_LANE2_ANA_RX_SQ` field definitions and then covers the tail of lane 2 analog RX controls, a large lane 3 digital/analog TX/RX control section, raw common control and always-on common calibration fields, raw lane 0 PCS/PMA cross-interface fields, raw lane 0 FSM/status/IRQ fields, and the beginning of raw lane 0 TX control. Although this repository path is under `ceph-client`, the file is GPU display hardware register metadata, not distributed filesystem logic.

This slice contains 2,123 `#define` entries and 254 register comment markers. It is a chunk of a much larger generated header, so it intentionally documents only the visible `CR4` subset. Neighboring chunks are needed to complete the source-file-level report.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocation paths, or persistence APIs in this range. The public interface is the generated macro namespace:

- `DPCSSYS_CR4_<register>__<field>__SHIFT`: the low bit position for a field.
- `DPCSSYS_CR4_<register>__<field>_MASK`: the raw bitmask for the same field.
- `RESERVED_*`, `NC*`, and `RESERVED_REG_*` macros: generated reserved or not-connected bit ranges that should generally be preserved unless the ASIC programming guide explicitly defines a safe write value.

Major register families covered by this chunk:

- `DPCSSYS_CR4_LANE2_ANA_RX_*`: lane 2 analog RX squelch, DFE tap enable, calibration mux selection, ATB register reference and measurement controls, forced ATB calibration reference, and reserved analog RX fields.
- `DPCSSYS_CR4_LANE3_DIG_ASIC_*`: lane 3 ASIC-facing override inputs and status mirrors for lane loopback, TX request/pstate/rate/width/MPLL/data enable, TX cursor and pre/post-emphasis fields, HDMI mode, TX clock/reset/detect signals, RX AFE/CDR/equalization fields, and ASIC input/output mirrors.
- `DPCSSYS_CR4_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX power-state register fields for P0/P0S/P1/P2, TX power-up timing registers, DCC bank address/data and DAC controls, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR4_LANE3_DIG_RX_STAT_*`: lane 3 RX pattern/statistic support, including load values, data masks, match-control words, sample-count controls, statistic counters 0-6, stop control, and calibration comparator clock control.
- `DPCSSYS_CR4_LANE3_DIG_ANA_*` and `DPCSSYS_CR4_LANE3_ANA_TX_*`: digital-to-analog TX override outputs, TX termination code controls, TX equalization override words, analog status readback, DCC DAC override controls, analog TX power/loopback/clock/alternate-bus/ATB/DCC/termination/miscellaneous fields, and reserved analog TX registers.
- `DPCSSYS_CR4_RAWCMN_DIG_*`: raw common control for MPLL A/B override, bandwidth override, spread-spectrum controls, common lane FSM extension, common control/status, MPLL state control, TX calibration code, SRAM init done, OCLA debug, supervisor analog override, PCS and firmware ID codes, and always-on common RTUNE/power-gating/resource/vref/reference-range/miscellaneous controls.
- `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_*`: raw lane 0 PCS cross-interface TX/RX override, PCS input/output mirror, adaptation acknowledge/FOM, TX pre/main/post direction readbacks, lane number, ATE override, RX equalization override, TX/RX termination control, phase-2 calibration request/acknowledge, and reserved PCS fields.
- `DPCSSYS_CR4_RAWLANE0_DIG_FSM_*`: raw lane 0 firmware/FSM override, monitor, fast-start/calibration/adaptation flags, common calibration status, continuous calibration/adaptation status, CR lock, TX DCC status, OCLA debug, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE0_DIG_IRQ_CTL_*`: raw lane 0 interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation events, lane transceiver mode, phase-2 calibration, RX-to-TX loopback, DCC on-demand, TX reset/request, and related clear bits.
- `DPCSSYS_CR4_RAWLANE0_DIG_PMA_XF_*`: raw lane 0 PMA cross-interface lane/MPLL/supervisor/TX/RX override and mirror fields, RTUNE request/acknowledge, MPHY PWM/async override fields, and RX adaptation phase-adjust map.
- `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_*`: beginning of raw lane 0 TX control fields for MPLL-off wait timing, RX-detect allowance by power state, TX clock selection, async beacon wait timing, and TX DCC continuous status.

Most field masks describe low 16-bit CR-register fields but are emitted with `0x0000....L` 32-bit-looking constants in this 4.2.2 header. Adjacent `dpcs_4_2_3_sh_mask.h` uses shorter `0x....L` spellings for many corresponding masks, so consumers should treat the numeric value, not textual width, as the contract.

## Control Flow

This header has no runtime control flow. It participates in hardware programming through compile-time token-pasted register access:

1. DCN resource or link code includes the DPCS 4.2.2 offset header and this shift/mask header for a supported ASIC generation.
2. Register helper macros combine a register token with a field token, expanding to the offset, mask, and shift constants.
3. Display link encoder, PHY, clock, power-management, calibration, debug, and interrupt paths read-modify-write hardware registers or poll status fields using those constants.
4. The DPCS hardware, PHY firmware, or autonomous finite-state machines perform the actual sequencing: PLL enable/disable, power-state transitions, clock selection, TX/RX request/ack handshakes, RX adaptation, calibration, interrupt latching, and status generation.

The chunk does not encode sequencing rules. Software must still order operations correctly around reference clocks, MPLL state, lane power, TX/RX reset and request handshakes, RX adaptation/calibration, DCC adjustment, RTUNE, power gating, and IRQ clear/mask behavior.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO or indirect CR-backed hardware state.

State represented by these fields includes:

- Analog RX/TX state: lane 2 RX squelch/calibration/ATB settings and lane 3 TX analog power, clock, loopback, DCC, termination, EQ, ATB, alternate-bus, and status fields.
- Digital lane state: lane 3 ASIC-facing TX/RX overrides and mirrors for rates, widths, p-states, MPLL selection, data enable, reset, request/acknowledge, loopback, RX adaptation, CDR/VCO load values, AFE/DFE/EQ settings, and TX de-emphasis/cursor values.
- Common PHY state: raw common MPLL A/B configuration and SSC fields, common control/status bits, firmware ID fields, OCLA debug selection, SRAM initialization, always-on RTUNE values for lanes 0-7, power-gating overrides, supervisor overrides, resource handshakes, VREF calibration status, reference range override, and MPLL powerdown time.
- Raw lane 0 PCS/PMA state: PCS and PMA TX/RX cross-interface controls, reset/request/data-enable overrides, RX detect/adaptation controls, TX/RX term controls, MPHY PWM/async controls, supervisor and lane MPLL enable mirrors, RTUNE request/acknowledge, and RX adaptation phase-adjust maps.
- Firmware/FSM and interrupt state: FSM override/jump/control fields, monitor/status flags, fast calibration/adaptation status bits, CR lock, DCC status, OCLA capture controls, TX EQ update flags, RX IQ phase offsets, IRQ status bits, IRQ clear bits, and IRQ masks.
- TX control state: raw lane 0 TX wait timers, per-pstate RX detect allowance, TX clock enable/selection, async beacon wait time, and DCC continuous enable status.

Persistence is hardware-defined. Configuration fields typically retain values until driver reprogramming, PHY or display-core reset, power gating, suspend/resume restore, firmware reinitialization, or ASIC reset. Status, interrupt, calibration, ack, monitor, and counter-like fields may be read-only, sticky, write-one-to-clear, self-clearing, or side-effect-sensitive. This mask header does not encode access policy, so runtime code must rely on the register specification and existing AMD display access conventions.

## Dependencies And Integration Points

This chunk depends on generated DPCS register metadata staying internally consistent:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the `ixDPCSSYS_CR4_*` register offsets that pair with these field masks.
- Adjacent DPCS headers such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` expose near-identical register families for related hardware revisions, making cross-version diffs a practical consistency signal.
- AMD display register-helper code consumes these macros through token-pasted field descriptors, so macro spelling and field names are part of the compile-time ABI for the driver source.

Functional integration points include DC link encoder and PHY programming, DisplayPort and HDMI link bring-up, high-speed lane power management, TX/RX equalization and adaptation, RX detect and hotplug-adjacent PHY behavior, spread-spectrum and MPLL clocking setup, firmware or microcode handoff, RTUNE and VREF calibration, power-gating entry/exit, suspend/resume restore, debug capture through OCLA/ATB/LBERT-style paths, and interrupt clear/mask handling for lane reset/request/rate/pstate/adaptation events.

The range is tightly coupled to neighboring chunks. It starts after the `DPCSSYS_CR4_LANE2_ANA_RX_SQ` shifts were already introduced and ends after only the first field of `DPCSSYS_CR4_RAWLANE0_DIG_TX_CTL_TX_DCC_CONT_STATUS`, so complete register-family conclusions require the previous and next chunk reports.

## Risks And Edge Cases

- Mask or shift drift is the primary risk. These are untyped preprocessor constants, so incorrect generated values can compile cleanly while corrupting a different hardware field.
- The lane and raw-lane namespaces are repetitive. A generation, lane index, power state, TX/RX direction, or MPLLA/MPLLB copy error may affect only one connector, lane, link rate, or power transition.
- Override enables are hazardous when firmware or hardware FSMs own the same signal. Incorrect use of `*_OVRD_EN`, `*_OVRD_VAL`, `ASIC_*_OVRD_*`, `PMA_XF_*_OVRD_*`, or `PCS_XF_*_OVRD_*` fields can force resets, requests, clocks, data enables, power, loopback, adaptation, or calibration into a stale state.
- Interrupt clear and mask fields are side-effect-sensitive. Using the wrong clear mask can drop or preserve stale IRQ status, causing missed adaptation/reset/request events or repeated interrupt handling.
- Reserved and not-connected fields are named but should not be treated as writable feature fields. Read-modify-write helpers must preserve unrelated bits, especially in analog, common, and power-gating registers.
- Analog calibration, RTUNE, VREF, DCC, and equalization fields can produce failures that are intermittent or hardware-revision-specific. Bad masks may appear only at high link rates, after resume, under hotplug churn, or during factory/debug modes.
- TX/RX PCS/PMA handshake fields are sequencing-sensitive. Wrong request, acknowledge, reset, data-enable, power-state, or MPLL-state fields can cause link training timeouts, stuck low-power states, failed RX detect, or blank/flickering displays.
- Header width conventions differ across generated revisions. Local code should not assume that a `0x0000....L` spelling implies a 32-bit hardware register when the active field is a 16-bit DPCS CR field.

## Test Signals

Useful validation signals are mostly compile-time, static, and hardware-integration oriented:

- Build coverage for the AMD display resource/link code that includes `dpcs_4_2_2_sh_mask.h`, catching missing, renamed, or malformed macros.
- Static consistency checks that every visible field has a matching `__SHIFT` and `_MASK`, active masks stay within the expected low 16-bit DPCS CR width, and shift/mask pairs agree on field width and position.
- Cross-version generated-header diffs against `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` to find unexpected changes in corresponding `CR4` lane/common/raw-lane fields.
- Display smoke tests on the ASIC generation that uses DPCS 4.2.2: HDMI and DisplayPort modesets, hotplug, EDID/DPCD access, link training across rates and lane counts, multi-monitor operation, suspend/resume, and power-state cycling.
- PHY debug evidence: successful MPLL state transitions, stable TX/RX request and acknowledge handshakes, expected RTUNE and VREF calibration status, correct RX adaptation/FOM behavior, sane DCC and EQ status, no unexpected FSM error/status bits, and no repeated or missing lane IRQ events.
- Regression signals include blank or flickering displays, DP training failures, HDMI clocking issues, wake/resume failures, stuck PHY power states, RX detect failures, unexpected IRQ storms, timeout logs around register polling, and failures isolated to lane 3 or raw lane 0 paths covered by this chunk.
