# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 120746-123298

## Purpose

This chunk is generated AMD DPCS 4.2.3 register bitfield metadata. It contains no executable C logic; it publishes preprocessor `__SHIFT` constants that identify bit positions within 16-bit DPCS PHY control/status registers. Consumers pair these field shifts with the matching register indices in `dpcs_4_2_3_offset.h` and, elsewhere in this header, companion mask definitions to compose MMIO or indirect DPCS register updates through AMD display-core register helpers.

The selected range covers the tail of `C20_PHY_CR1_LANE1` analog TX definitions, the lane 1 ASIC RX interface, lane 1 RX power/calibration/statistics/analog receive metadata, and then the start through midsection of `C20_PHY_CR1_LANE2` definitions. The lane 2 portion includes lane/TX ASIC controls, TX power and analog TX metadata, RX ASIC controls, RX power/VCO/CDR/DPLL/adaptation metadata, and RX statistic counters through `C20_PHY_CR1_LANE2_DIG_RX_STAT_LD_VAL_EXT_1`. Although this repository subtree is named `ceph-client`, this file is AMDGPU display-driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or callbacks in this range. The exposed interface is the generated macro namespace:

- `C20_PHY_CR1_LANE1_<REGISTER>__<FIELD>__SHIFT` for lane 1 bit positions.
- `C20_PHY_CR1_LANE2_<REGISTER>__<FIELD>__SHIFT` for lane 2 bit positions.
- Matching register offset macros are supplied by `dpcs_4_2_3_offset.h` as `ixC20_PHY_CR1_LANE*_...` names.

Major register families in this chunk:

- Lane 1 analog TX handoff fields: `DIG_ANA_XF_TX_OVRD_OUT_*`, termination-code override and clock strobes, TX analog DCC enable/config/calibration controls, TX EQ override/status fields, and TX analog CREG debug/trim controls. These describe clocks, resets, serial/data enable, data rate, RX detect, ref selection, VBoost, word clock, termination, post/pre-cursor EQ, leg-pull controls, and analog debug buses.
- Lane 1 ASIC RX interface fields: `DIG_ASIC_RX_OVRD_IN_*`, `ASIC_RX_ASIC_IN_*`, `ASIC_RX_EQ_ASIC_IN_*`, `ASIC_RX_OVRD_EQ_IN_*`, and status/output blocks. These expose reset, invert, data enable, request/ack, low-power detect, pstate, rate, width, DFE bypass, CDR track/SSC, signal-detect thresholds, VCO configuration, CTLE/VGA/ATT/DFE tap overrides, IQ and AFE bias/zero/offset fields, and RX valid/adaptation status.
- Lane 1 RX power, calibration, and diagnostics: RX pstate profiles for `P0`, `P0S`, `P1`, and `P2`; power-up timing; RX control/status; VCO calibration control/time/status; LBERT control/error reporting; CDR and DPLL control/status/bounds; adaptation control/status for ATT, VGA, CTLE, DFE taps, slicers, DCC IDAC offsets, fast flags, and SSM final code; and RX statistic sample/counter/match controls.
- Lane 1 analog RX handoff fields: RX analog control and power overrides, signal-detect calibration, VCO override, calibration mux/DAC/range controls, AFE overrides, scope and slicer controls, IQC bypass/data adjustment controls, loopback, termination, analog status outputs, signal-change enable bits, and RX analog CREG debug/configuration fields.
- Lane 2 digital TX and analog TX metadata: lane loopback and transceiver-mode override, TX ASIC override and live ASIC input/output fields, TX pstate profiles and timing, TX control/status, TX DCC offsets/status, TX statistic counter controls, clock alignment, LBERT pattern generation, FIFO control, analog TX override/status/DCC/EQ/CREG fields.
- Lane 2 RX metadata visible before the chunk ends: ASIC RX overrides and live inputs, RX power pstate/timing/control/status, VCO calibration, LBERT/CDR/DPLL, adaptation controls/status/offset registers, SSM controls, and RX statistic load/match/counter/control fields.

Field naming conventions are meaningful. `*_OVRD_EN` fields enable forced values; `*_OVRD_VAL` or bare control fields provide the forced value; `*_SELF_CLEAR_DISABLE` changes pulse behavior; `*_START`, `*_STOP`, `*_DONE`, `*_ACK`, `*_RESULT`, and `*_FSM_STATE` fields participate in hardware sequencing and polling; `RESERVED_*` fields document occupied or unused bit positions that normal driver code should preserve.

## Control Flow

This header has no runtime control flow. Runtime behavior is imposed by consumers in AMD display code:

1. DCN316 resource setup includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. Register tables and field lists token-paste register/field names into offset, shift, and mask constants.
3. Register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and polling helpers perform MMIO or indirect DPCS accesses.
4. Link encoder, PHY, diagnostics, and training code sequence clocks, resets, pstate changes, rate/width changes, VCO/DCC calibration, CDR/DPLL control, RX adaptation, LBERT, loopback, and statistics collection.

The chunk itself encodes only bit positions. It does not define ordering, delays, retries, timeouts, locking, or read/write access type. Any safe sequence around `REQ`/`ACK`, reset deassertion, calibration start/done, statistic start/stop, self-clearing pulses, or status polling must come from the consuming display driver and hardware programming guide.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes hardware state reachable through DPCS CR1 lane 1 and lane 2 registers.

The represented hardware state includes persistent configuration fields, live status bits, pstate profiles, power-up timing values, calibration settings, counter load values, statistic counters, loopback/test controls, analog override values, adaptation coefficients, DFE/slicer offsets, VCO/CDR/DPLL state, and RX/TX handshake signals. Persistence is hardware-defined: values may survive until a modeset, link reconfiguration, power-gate event, suspend/resume transition, or ASIC reset; status/counter bits may be sticky, self-clearing, latch-on-read, read-only, or write-one-to-clear depending on the underlying register. The `__SHIFT` macros alone do not communicate those access semantics.

## Dependencies And Integration Points

This generated chunk depends on consistency with the rest of the AMD register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` provides the matching `ixC20_PHY_CR1_LANE1_*` and `ixC20_PHY_CR1_LANE2_*` register indices.
- Other regions of `dpcs_4_2_3_sh_mask.h` provide companion mask macros for this same generated register set.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes the DPCS 4.2.3 offset and shift/mask headers for DCN316 hardware.
- AMD display-core register helper layers combine offsets, masks, and shifts into field reads, writes, updates, and polls.

Integration points are PHY/link bring-up, DisplayPort or USB-C lane programming, link training, low-power entry/exit, pstate transitions, receiver adaptation, DCC/VCO calibration, CDR/DPLL tracking, loopback and compliance modes, link diagnostics, and debug tooling. The lane 1 and lane 2 repetition is intentional: the same logical controls are replicated per physical lane, while offsets select the concrete lane instance.

## Risks And Edge Cases

- Header/offset version mismatch is the main correctness risk. Pairing this `dpcs_4_2_3_sh_mask.h` range with a different offset header can compile while programming the wrong register or field.
- These are untyped preprocessor constants. A generated shift error, a copy/paste issue between lane 1 and lane 2, or a consumer typo can silently affect only one lane, one link width, or one rate path.
- Override-enable fields are hazardous. Enabling `*_OVRD_EN` without the matching value field, or leaving overrides enabled after diagnostics, can force analog/RX/TX state and cause blank display, link training failure, unstable low-power transitions, or elevated error counters.
- Calibration and handshake fields are sequencing-sensitive. VCO calibration, DCC DAC writes, CDR/DPLL controls, adaptation reset/start/status, SSM start/final-code, `REQ`/`ACK`, RX detect, statistic start/stop/done, and self-clearing clock/update pulses need explicit polling and timeout handling in consumers.
- Reserved fields appear throughout. Register updates should use read-modify-write helpers and masks that preserve reserved bits unless an ASIC programming guide explicitly requires otherwise.
- Lane-local fields can interact with board routing and link width. A bug may manifest only on lanes using `C20_PHY_CR1_LANE1` or `LANE2`, only when lane reversal is active, or only on multi-lane links.
- The chunk boundary is artificial. It begins mid-register at the end of `LANE1_DIG_ANA_XF_TX_OVRD_OUT_1` and ends at the start of `LANE2_DIG_RX_STAT_LD_VAL_EXT_1`; adjacent chunks are required for complete per-file analysis.

## Test Signals

Useful validation is mostly build, static, and hardware integration coverage:

- Build coverage for AMDGPU/DCN316 display code that includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static checks that generated field shifts and masks match the register database, that fields within a 16-bit register do not overlap unexpectedly, and that each used field has a matching offset and mask.
- Display bring-up and link-training tests across rates, lane counts, lane mappings, and suspend/resume paths, especially on hardware that exercises CR1 lane 1 and lane 2.
- Hotplug, modeset, power-gating, and low-power idle tests that cover reset, pstate, timing, request/ack, RX/TX enable, VCO/DCC calibration, CDR/DPLL, and receiver adaptation fields.
- PHY diagnostics and compliance signals: LBERT pattern/error behavior, loopback modes, RX statistic counters, SSM completion, DCC/VCO calibration status, RX valid/adaptation status, and error-counter stability on known-good links.
- Regression indicators include blank or unstable displays, intermittent DP retraining, AUX/link-training timeouts, failed VCO or DCC calibration, unexpected RX adaptation status, high bit-error/statistic counters, or failures isolated to a specific lane or connector mapping.
