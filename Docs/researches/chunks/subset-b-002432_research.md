# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 112902-115499

## Purpose

This chunk is generated AMD DPCS 4.2.3 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used by AMDGPU display/PHY code when packing and unpacking DPCS C20 PHY control/status registers.

The requested range is a middle-to-late slice of `dpcs_4_2_3_sh_mask.h`. It starts inside the `RAWLANEAON3` always-on lane-3 transmitter DCC calibration area, covers a large `RAWLANEAON3` receiver calibration/adaptation block, then transitions into generic `LANEX` lane register fields for ASIC RX, analog TX/RX, RX adaptation/statistics/IQC, and finally `RAWLANEX` transmitter PCS/firmware/IRQ/PMA handshakes. The range includes 523 commented register groups: 198 `RAWLANEAON3` groups, 269 `LANEX` groups, and 56 `RAWLANEX` groups.

Although this repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It is unrelated to Ceph or distributed filesystem behavior except by source-tree placement.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or memory-management APIs in this chunk. The public interface is the generated macro namespace:

- `C20_PHY_CR0_<register>__<field>__SHIFT`: bit position of a field inside a DPCS register.
- In adjacent/generated paired lines outside or near this range, matching `__MASK` macros generally provide the field mask for the same register field. This chunk itself is the shift/mask header slice, but the selected lines predominantly show `__SHIFT` definitions.

Major register families in this chunk:

- `C20_PHY_CR0_RAWLANEAON3_DIG_TX_*`: lane-3 TX MPLLA/MPLLB DCC full/half-bank calibration values, calibration-done bits, global TX calibration done, DCC range/code fields, recalibration bank selection, and TX disable input.
- `C20_PHY_CR0_RAWLANEAON3_DIG_RX_STARTUP_*`, `RX_CONT_ALGO_CTL`, and `RX_FAST_FLAGS`: per-lane controls for skipping startup calibration/adaptation stages, continuous calibration/adaptation stages, fast startup/adaptation/power-up paths, VCO calibration/wait acceleration, and margining-related controls.
- `C20_PHY_CR0_RAWLANEAON3_DIG_RX_*_OFST`, `RX_SIGDET_CAL`, `RX_AFE_*`, and `RX_VDAC_RANGE_SEL`: calibrated offsets and trims for VGEN, signal detect, AFE resistor trim, reference VDACs, CTLE/VGA/ATT/BUF IDACs, DFE phase/data/bypass/error VDACs, and VDAC range selection.
- `C20_PHY_CR0_RAWLANEAON3_DIG_RX_DCC_*`, `RX_IQ_*`, and `RX_CAL_DONE*`: RX DCC range/code/data/bypass/phase fields across banks 0-3, IQ calibration min/max/reset/adjust fields, per-bank IQ values, bank-select fields, and per-bank/full calibration completion flags.
- `C20_PHY_CR0_RAWLANEAON3_DIG_RX_ADPT_*` and `RX_DFE_*_OFST_BANK_*`: RX adaptation output fields for ATT, VGA, CTLE, DFE taps 1-5, DFE tap1 offsets for even/odd and high/low paths, IQ adaptation results, reference error, and adaptation-done flags. The selected range includes banks 0 and 1 explicitly, with the surrounding file owning the rest of the repeated family.
- `C20_PHY_CR0_LANEX_DIG_ASIC_RX_*`: generic lane ASIC RX override and live-input/output fields for reset, invert, data enable, request/ack, low-power detect, power state, rate, width, DFE bypass, CDR track/SSC, disable, div16.5 clock, loopback, signal-detect thresholds, RX DCC controls, VCO load/config, EQ/AFE/DFE tap settings, adaptation status, validity, and miscellaneous override values.
- `C20_PHY_CR0_LANEX_DIG_ANA_XF_TX_*`: analog TX cross-interface override/status/config fields for clocks, resets, serial/data/refgen enables, loopback, VREG/bias/boost controls, termination code clocks, DCC calibration controls, static equalization override/output fields, analog status inputs, and TX analog control registers `CREG00` through `CREG05` plus override registers.
- `C20_PHY_CR0_LANEX_DIG_RX_ADPTCTL_*`, `RX_STAT_*`, and `RX_IQC_CTL_*`: RX adaptation-controller config fields, DCC IDAC offset overrides, fast flags, slicer/search state-machine (`SSM`) config/final-code fields, statistic pattern matching, sample/stat counters, comparator clock controls, shadow counters, extended load values, and IQC reset/config/status fields.
- `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_*`: analog RX override/status/config fields for RX clock/power/VCO/signal-detect/calibration/DAC/AFE/CTLE/VGA controls, slicer controls, IQC bypass/data adjustment, loopback, termination, status in/out, and analog RX control registers `CREG00` through `CREG11`.
- `C20_PHY_CR0_RAWLANEX_DIG_TX_*`: generic raw-lane TX PCS, firmware, IRQ, FSM, clock, termination, power-up, MPLL restart-calibration, and PMA cross-interface fields.

## Control Flow

This header has no runtime control flow. The control flow lives in AMDGPU display PHY and link-management code that includes the generated register headers and uses these macros through register helpers:

1. Driver code selects a lane-specific register address from the matching DPCS offset header, usually by token-pasting a lane or instance into a generated register-list macro.
2. It uses the `__SHIFT` and corresponding `__MASK` constants to pack values into a 16-bit-style DPCS register field or to extract fields from a register read.
3. Firmware/driver sequencing then programs or polls calibration, adaptation, override, status, IRQ, and handshake fields according to PHY bring-up, link training, power-management, loopback, debug, or recovery flow.

The macros do not encode ordering. Consumers must still know when a field is read-only, sticky, self-clearing, write-one-to-clear, gated by an override enable, valid only for a selected bank, or unsafe while the lane is powered down or reset.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO or indirect-register state in the DPCS C20 PHY hardware.

The represented hardware state includes:

- Per-lane TX DCC and MPLLA/MPLLB calibration state, with separate full/half-rate and banked values.
- RX startup, continuous, and fast calibration/adaptation controls, including skip bits that can materially change PHY tuning behavior.
- Banked RX calibration outputs for DCC, IQ, DFE/AFE/CTLE/VGA offsets, signal-detect trims, reference levels, and adaptation results.
- ASIC RX interface live and override state for reset/request/ack/power/rate/width/CDR/EQ/DFE/DCC/VCO/signal-detect behavior.
- Analog TX/RX interface controls and status, including clock enables, power enables, loopback, DCC calibration, termination, equalization, VREG, VCO, AFE, slicer, IQC, and debug/control-register fields.
- RX statistic and search state-machine state, including pattern-match controls, counters, sample-done bits, shadow counts, comparator clocking, and final-code/done/abort/state fields.
- RAWLANEX TX firmware, IRQ, PCS, PMA, and FSM handshake state for reset/request/ack, rate and term-control interrupts, RX-to-TX parallel loopback, retune, lane mode, MPLL selection/state, and power-up completion.

Persistence is hardware-defined. Configuration and override registers usually retain values until lane reset, PHY reset, power gating, suspend/resume, or reinitialization. Calibration/adaptation result registers are hardware outputs and may be overwritten by the next calibration, bank switch, rate change, or adaptation cycle. IRQ, clear, status, clock-strobe, and self-clear-disable fields are especially sequencing-sensitive; this generated header does not identify those semantics beyond field names.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 4.2.3 register database and must stay synchronized with companion generated headers in the same directory, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`
- Adjacent lines in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h` that provide preceding/following parts of repeated lane and bank families.

The integration contract is numeric and preprocessor-based. Display PHY code builds register addresses from offset macros and uses these shift/mask macros with low-level register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_FIELD_VALUE`, and related AMDGPU/DCN/DPCS accessors. These macros are also commonly consumed by generated register-list structs and initialization tables for PHY bring-up, link training, debug, and firmware handoff.

Important hardware integration points represented by this slice:

- Link training and PHY initialization: TX/RX reset, request/ack, power state, lane rate/width, TX disable, MPLL selection/state, clock enables, VCO and DCC calibration, and calibration-done polling.
- Receiver adaptation: startup skip controls, continuous adaptation controls, AFE/DFE/CTLE/VGA/IQ/DCC calibration and adaptation result fields, and banked recalibration state.
- Firmware and interrupt handshake: RAWLANEX TX firmware override/input/output fields plus IRQ mask/enable/status/clear fields for rate, reset, request, loopback, retune, termination, and lane transceiver mode.
- Debug/diagnostics: RX statistic counters, pattern matchers, search state-machine fields, analog status outputs, CREG debug/control fields, and scope/status selections.
- Analog front-end/back-end: TX/RX analog power, clock, VREG, termination, loopback, signal-detect, slicer, VCO, AFE, EQ, DCC, IQC, and calibration controls.

## Risks And Edge Cases

- Generated numeric drift is the central risk. A wrong shift or mask compiles cleanly but writes the wrong bitfield, which can break PHY bring-up, link training, calibration, or power management.
- The range starts and ends inside larger generated families. The first line is a tail of `RAWLANEAON3_DIG_TX_MPLLB_DCC_FULL_BANK_3`, and the later merge lane must combine adjacent chunks before making complete file-wide claims.
- Many fields are paired value/override-enable bits. Setting an override value without the matching `*_OVRD_EN`, or leaving an override enabled after a diagnostic flow, can force stale PHY behavior.
- Banked calibration fields are easy to mix up. `BANK_0` through `BANK_3`, full/half-rate, common-mode/differential, data/bypass/phase, and even/odd/high/low variants must be addressed consistently with the selected recalibration bank and lane rate.
- IRQ clear/status fields are side-effect-sensitive. Confusing `*_IRQ`, `*_IRQ_CLR`, mask, enable, or ack fields can cause stuck interrupts, missed handshakes, or repeated lane recovery.
- Some fields are likely read-only hardware status or self-clearing strobes by convention, but the header does not type them. Callers must rely on register programming guides and existing driver sequences.
- Analog and PHY controls are power/clock/reset sensitive. Writes while the lane is gated, reset, or in the wrong P-state may be ignored or may leave calibration/adaptation in an inconsistent state.
- The generic `LANEX` and lane-specific `RAWLANEAON3`/`RAWLANEX` namespaces are similar but not interchangeable; using the wrong macro family can silently target a different register layout.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU display code that includes DPCS 4.2.3 register headers; missing, renamed, or malformed macros should fail during register-table and field-helper expansion.
- Mechanically verify that each field in this range has a consistent `__SHIFT`/`__MASK` pair in the complete header and that repeated bank/lane families use identical bit positions where the hardware pattern requires it.
- Diff this range against AMD's authoritative DPCS 4.2.3 register database and neighboring generated DPCS versions to catch accidental field movement, truncation, or copy/paste errors.
- Exercise display modes that use the covered PHY paths: cold boot, modeset, DP/HDMI link training, link-rate changes, lane-count changes, suspend/resume, hotplug, retune, and recovery from link failure.
- Validate RX calibration/adaptation by checking for successful calibration-done/adaptation-done status, stable EQ/DFE/IQ results, no repeated recalibration loops, and no lane-specific failures across rates.
- Test firmware and IRQ handshakes around TX request/reset/rate changes, loopback enable/disable, termination-control changes, lane mode changes, and MPLLA/MPLLB restart calibration.
- Use debug counters/status where available: RX statistic counters, SSM final-code/done/abort fields, analog status inputs/outputs, IRQ status/clear behavior, and kernel logs for AUX/link-training/PHY errors.
- Watch for user-visible failures such as blank display, link training timeouts, hotplug storms, audio/video instability, DSC or high-bandwidth mode failures caused by unstable PHY tuning, resume failures, and persistent GPU/display error logs.

## Cross-Chunk Notes

This is only the research document for `subset-b-002432`. Earlier chunks own the beginning of the DPCS 4.2.3 generated shift/mask header and the leading part of the `RAWLANEAON3` TX calibration family. Later chunks continue after the `RAWLANEX` TX PMA cross-interface fields. The final per-file research should merge this document with adjacent chunks before summarizing complete DPCS 4.2.3 coverage.
