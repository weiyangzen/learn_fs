# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 41605-43979

## Scope And Purpose

This chunk is part of the generated AMDGPU NBIO 6.1 shift/mask header. It defines bit-field extraction and packing metadata for DWC E12MP PHY X4 lane registers: the tail of lane 0 RX adaptation configuration, lane 0 RX status/statistics and analog TX/RX controls, and the beginning of lane 1 ASIC, power, RX adaptation, statistics, and analog controls.

The file does not implement runtime logic. Its exported contract is a large set of C preprocessor macros named `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Consuming AMDGPU code combines these constants with the corresponding register offsets from `nbio_6_1_offset.h`, defaults from `nbio_6_1_default.h`, and register access helpers to write individual PHY fields without hard-coding bit positions.

## Register Families Covered

The opening lines finish `DWC_E12MP_PHY_X4_NS_X4_0_LANE0_DIG_RX_ADPTCTL_ADPT_CFG_7`, then cover lane 0 adaptation configuration registers `ADPT_CFG_8` and `ADPT_CFG_9`. These expose DFE adaptation step sizes (`DFE1_MU` through `DFE5_MU`) and initial error slicer values (`ERR_SLE_ADPT_INIT`, `ERR_SLO_ADPT_INIT`) alongside the previous VGA saturation/level fields.

The lane 0 `DIG_RX_ADPTCTL` status and reset block defines reset bits for ATT, VGA, CTLE boost, CTLE pole, and DFE tap1 adaptation, plus status fields for ATT, VGA, CTLE, and DFE taps 1 through 5. These status registers report adapted codes and `ASM1_DONE` style completion bits. Additional fields describe DFE data/error/bypass VDAC offsets for even and odd slicers, even/odd RX slicer controls, and error slicer levels.

The lane 0 `DIG_RX_STAT` block defines receiver statistics and pattern-match controls. It includes load/start values, data masks, pattern match controls, statistic-control registers, sample count, seven statistic counters, calibration-comparator clock control, and extra match/statistic controls. These fields are used to configure and inspect PHY-side RX measurement windows rather than driver-owned software counters.

The lane 0 `DIG_ANA` and `ANA` blocks expose analog TX/RX controls and status. Digital-to-analog TX override outputs cover TX power enables, polarity, common-mode, boost, termination code override, and equalization overrides. RX analog override/status fields cover AFE/VCO/CDR power controls, calibration mux and DAC controls, AFE ATT/VGA/CTLE controls, scope/slicer controls, IQ phase/sense controls, self-clearing update enables, loss-of-signal and calibration status, and VCO counters. The lower-level lane 0 analog registers then expose TX measurement, power override, alternate bus, ATB monitor selections, vboost, termination, iboost, override clocks, TX misc fields, RX DCC/power/CDR/mux/measurement/termination/slicer/vreg controls.

The lane 1 section starts at the ASIC interface boundary. It covers lane, TX, and RX override input/output fields and corresponding ASIC input/output fields, including TX detect, electrical idle, swing/de-emphasis/equalization, polarity, loopback, RX CDR/VCO, DFE/equalization override, status, and ready/done bits. It then defines lane 1 TX/RX power-state timing fields, LBERT controls and error status, RX CDR controls, DPLL frequency and bounds, RX adaptation configuration/status blocks, RX statistics, digital analog TX/RX overrides, analog RX controls/status, and begins lane 1 analog TX measurement and power override fields.

## APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this chunk. The important exported interface is the generated macro set:

- `...__SHIFT` constants identify each field's low bit position in its 16-bit PHY register.
- `..._MASK` constants identify each field's occupied bits after shifting.
- `RESERVED_*` masks document unused or reserved bit ranges that consumers should preserve unless the hardware programming sequence explicitly requires otherwise.

The generated names are intentionally verbose because the register name encodes the PHY instance (`DWC_E12MP_PHY_X4_NS_X4_0`), lane (`LANE0` or `LANE1`), sub-block (`DIG_RX_ADPTCTL`, `DIG_RX_STAT`, `DIG_ANA`, `ANA`, `DIG_ASIC`, `DIG_TX_PWRCTL`, `DIG_RX_PWRCTL`, `DIG_RX_CDR`, and related groups), register, and field. Typical consumers use these with AMDGPU field helpers such as register read-modify-write macros, `REG_SET_FIELD`-style packing, or equivalent SOC/SMN indexed register utilities.

## Control Flow

This header has no control flow. It affects runtime behavior only by resolving symbolic field positions and masks at compile time.

The implied hardware control flow lives in callers. RX adaptation code may program adaptation thresholds, mu values, slicer levels, reset bits, and then poll completion/status fields such as `ASM1_DONE`. PHY statistics code may load a sample or pattern configuration, start capture, then read statistic counters. Analog calibration paths may select calibration muxes, enable DAC or AFE update pulses, and then read calibration result or VCO counter status. Power-management paths may program TX/RX p-state timing and power-up controls before changing link state. Diagnostic or bring-up paths may enable LBERT, scope, ATB, loopback, or override fields and then read error/status fields.

Because the header only provides masks, it does not enforce the ordering between these operations. Sequencing requirements, delays, timeouts, and preserve-mask behavior must be supplied by the consuming driver code or by hardware firmware flows.

## State And Persistence Behavior

The state represented here is persistent hardware register state inside the NBIO PCIe/PHY lane block until reset, power transition, firmware reprogramming, or an explicit driver write changes it. The macros themselves store no software state.

Important state categories include RX adaptation coefficients and control thresholds, DFE tap status, CTLE/VGA/ATT adapted codes, slicer offset/level state, RX statistic capture configuration and counters, TX equalization and termination override state, analog RX AFE/CDR/VCO/calibration state, lane 1 ASIC override inputs and outputs, TX/RX p-state timing, LBERT diagnostic state, and analog measurement/ATB selections.

Several fields imply edge-triggered or self-clearing behavior. `START` style statistic/adaptation fields, `RX_ANA_CAL_DAC_CTRL_EN`, `RX_ANA_AFE_UPDATE_EN`, `RX_ANA_IQ_PHASE_ADJUST_CLK`, and related `*_SELF_CLEAR_DISABLE` bits require care: preserving or forcing self-clear behavior changes whether a write is a pulse or a latched override. Status fields such as loss-of-signal, calibration result, VCO counter, LBERT errors, statistic counters, and adaptation done bits are hardware-produced values and should not be treated as driver-owned cached state.

## Dependencies And Integration Points

This chunk depends on the rest of the generated NBIO 6.1 register set:

- `nbio_6_1_offset.h` supplies the register addresses for the same `DWC_E12MP_PHY_X4_NS_X4_0_LANE*` names.
- `nbio_6_1_default.h` supplies reset/default values for many of these registers.
- Earlier and later portions of `nbio_6_1_sh_mask.h` define adjacent fields for the same lane blocks, including the beginning of lane 0 adaptation configuration and the continuation of lane 1 analog TX/RX fields.
- AMDGPU SOC15/SMN register access helpers provide the actual read, write, poll, and read-modify-write mechanisms.

Integration points are hardware-facing. These fields sit under PCIe/NBIO PHY bring-up, link training, lane power-state transitions, PHY calibration, lane margining/diagnostics, LBERT testing, RX adaptation, analog override handling, and low-level debug paths. They also integrate with generated default tables and ASIC-specific initialization sequences that may restore known PHY defaults or apply board/ASIC workarounds.

## Risks And Edge Cases

The macros describe 16-bit hardware fields, but many consumers operate through wider MMIO or SMN accesses. Callers must preserve unrelated and reserved bits when modifying one field, especially in mixed control/status registers and analog override registers.

Lane identity is part of the contract. This chunk straddles lane 0 and lane 1; the field names are often structurally identical across lanes. Accidentally using a lane 0 mask with a lane 1 offset, or vice versa, may compile if the numeric layout happens to match, but it obscures intent and can break when generated layouts diverge.

Analog and PHY override fields are high-risk because they can force power, loopback, CDR/VCO, termination, equalization, calibration, or slicer behavior away from normal hardware control. Incorrect writes can prevent link training, cause intermittent PCIe errors, hide loss-of-signal conditions, or leave a diagnostic override active after a bring-up path exits.

Status and counter fields should be read with hardware semantics in mind. Adaptation completion bits, statistic counters, VCO counters, calibration results, and LBERT errors may be sampled, latched, clear-on-read, or dependent on a start/load sequence described outside this generated header. The masks alone do not reveal those side effects.

Self-clearing update fields require exact write policy. Setting `*_SELF_CLEAR_DISABLE` changes pulse behavior into persistent state for DAC, AFE update, or phase-adjust controls; preserving a stale value across read-modify-write can change later calibration behavior.

## Test Signals

The header is primarily validated through build coverage and hardware/simulator execution. Useful signals include:

- Successful compilation of NBIO 6.1 AMDGPU code using the generated shift/mask names with matching offset/default headers.
- Register traces showing field writes preserve reserved and unrelated bits when configuring adaptation, statistics, analog override, and power-state registers.
- PCIe link bring-up and retrain tests that verify lane 0 and lane 1 PHY programming does not regress link width, link speed, equalization, or error rate.
- RX adaptation tests or logs showing ATT/VGA/CTLE/DFE completion bits, adapted codes, slicer offsets, and error levels progress as expected.
- PHY statistics and LBERT tests that can start captures, observe statistic counters or LBERT errors, and reset/reconfigure the measurement path.
- Power-management validation across P0/P0s/P1/P2 and power-up timing transitions, including resume paths that may reapply defaults.
- Analog calibration diagnostics confirming DAC, AFE update, IQ phase, VCO counter, loss-of-signal, and calibration-result fields behave correctly after read-modify-write sequences.

Merged file-level research should connect this chunk with the matching offset/default chunks and with adjacent shift/mask chunks so the full DWC E12MP PHY X4 lane map is represented coherently.
