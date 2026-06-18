# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 129582-131967

## Purpose

This chunk is generated AMD DCN 3.2 register field metadata. It contains no executable driver logic; it publishes preprocessor constants that describe bit shifts and bit masks for fields in `C20_PHY_CR2` DisplayPort/PHY lane registers. The constants are consumed with the matching DCN 3.2 offset header and AMDGPU display register helpers to read, update, and decode hardware fields safely.

The requested range covers 2,174 `#define` lines: 1,087 `__SHIFT` constants and 1,087 matching `_MASK` constants across 213 commented register groups. The chunk starts in the tail of `C20_PHY_CR2_LANE1_DIG_ANA_XF_TX_ANA_CREG03`, then covers lane 1 TX analog control-register tail, lane 1 RX ASIC override/input/output, lane 1 RX power, VCO calibration, CDR/DPLL, adaptive equalization, statistic, IQ correction, RX analog override/calibration/status/control registers, and then enters lane 2 TX ASIC and TX power-control state registers through `TX_PWRUP_TIME_0`.

Although this path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, locks, or callbacks in this range. The API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position for a field within a C20 PHY CR2 indirect register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the same field.

Every `__SHIFT` macro visible in this chunk has a paired `_MASK` macro in the same requested range. Important macro families are:

- `C20_PHY_CR2_LANE1_DIG_ANA_XF_TX_ANA_CREG04`, `CREG05`, and TX `CREG*_OVRD`: lane 1 TX analog voltage regulator, boost, oscillator, MPLL clock enable, ring-control, pull-up/down, iboost, and override fields.
- `C20_PHY_CR2_LANE1_DIG_ASIC_RX_OVRD_*`: lane 1 RX software override fields for reset, invert, data enable, request, low-power detect, pstate, rate, width, CDR tracking/SSC, disable, loopback, DCC, signal-detect thresholds, VCO configuration, and many equalizer/adaptation controls.
- `C20_PHY_CR2_LANE1_DIG_ASIC_RX_ASIC_*`: lane 1 RX ASIC-facing input/output fields for clock-ready/reset/data/request/pstate/rate/width, VCO load values, CDR, DFE/equalizer settings, lock/ack, calibration status, calibration done, error detect, and stable RX-valid status.
- `C20_PHY_CR2_LANE1_DIG_RX_PWRCTL_*`: lane 1 RX power-state definitions for P0, P0S, P1, and P2, plus power-up timing, control, and status fields. These include analog enable/reset, CDR enable, DFE/CTLE/VGA enable, VCO and IQC enable, calibration enable, data-enable timing, request gating, and power-state machine status.
- `C20_PHY_CR2_LANE1_DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`: VCO calibration controls/status, calibration timing, CDR loop controls/status, DPLL frequency, and DPLL bounds.
- `C20_PHY_CR2_LANE1_DIG_RX_ADPTCTL_*`: adaptive receiver configuration/status fields for attenuation, VGA, CTLE, DFE taps, slicers, VDAC offsets, DCC IDAC offsets, reset, fast flags, and SSM state.
- `C20_PHY_CR2_LANE1_DIG_RX_STAT_*` and `DIG_RX_IQC_CTL_*`: statistic/match/sample/counter controls and IQ correction reset/config/status fields.
- `C20_PHY_CR2_LANE1_DIG_ANA_XF_RX_*`: analog transfer fields for RX power/ctl override outputs, signal-detect calibration, VCO override, calibration DACs, AFE override, scope/slicer controls, IQ and IQC bypass/data controls, loopback, DFE/bypass/phase sample selection, termination-code outputs, status inputs/outputs, and RX analog CREG fields.
- `C20_PHY_CR2_LANE2_DIG_ASIC_*` and `C20_PHY_CR2_LANE2_DIG_TX_PWRCTL_*`: the beginning of lane 2 TX ASIC override/input/output and TX power-state/timing masks, mirroring the lane 1 TX-side pattern from earlier chunks.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by AMDGPU display code:

1. DCN 3.2 source files include `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register-table helper macros such as `SR`, `SRI`, `BASE`, `REG_OFFSET_EXP`, `DMUB_SF`, and field helpers expand generated offset, shift, and mask symbols into typed register tables.
3. Driver code later performs reads, writes, field updates, polling, or DMUB register programming against those tables.
4. For these C20 PHY fields, the actual hardware access is indirect PHY/register access; this chunk only describes field layout, not the access protocol, training sequence, or side effects.

The macros do not encode ordering rules. Consumers must still coordinate PLL/clock readiness, lane reset, rate and width changes, pstate transitions, RX/TX power-up timing, VCO calibration, CDR tracking, DFE/CTLE/VGA adaptation, DCC calibration, signal detection, loopback, and suspend/resume restoration in the right order.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes MMIO/indirect-register hardware state in the DCN 3.2 C20 PHY CR2 block.

The represented hardware state includes:

- Lane 1 RX/TX analog and digital control fields, including voltage regulation, ring controls, pull-up/down controls, iboost, MPLL clock enables, CDR/VCO/DPLL state, and analog test bus selection.
- Lane 1 RX override state used to force or bypass normal hardware/firmware behavior for reset, pstate, rate, width, signal-detect, loopback, DCC, VCO, CDR, DFE, CTLE, VGA, slicers, termination, and IQ correction.
- Lane 1 calibration and adaptation state, including VCO calibration, signal-detect calibration, DCC offsets, DFE tap offsets/status, adaptation reset/configuration, statistics counters, and IQC status.
- Lane 1 RX and lane 2 TX power-control state, including per-pstate enable/reset bits, power-up delays, fast-mode shortcuts, request-disable controls, and power-state machine status.
- Lane 2 TX ASIC control fields at the end of the chunk for reset/data/request/rate/width, iboost/vboost, main/pre/post cursor values, DCC control range, detect-RX result, calibration status, and TX misc override.

Persistence is hardware-defined. Configuration fields generally remain until changed by modeset/link training, PHY reprogramming, power gating, suspend/resume, or ASIC reset. Status, IRQ, calibration, counter, and acknowledgement fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header does not identify those semantics; they come from hardware documentation and the code that sequences the PHY.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.2 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, especially the `ixC20_PHY_CR2_*` indirect offsets exposed for C20 PHY CR2 lanes.
- The rest of `dcn_3_2_0_sh_mask.h`, because this requested range begins after the start of lane 1 TX analog fields and ends before the rest of lane 2 TX/RX fields.
- DCN/SOC15 base-address and register-helper infrastructure used by AMDGPU display code.

Direct DCN 3.2 include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`

The exact `C20_PHY_CR2_LANE1` and `C20_PHY_CR2_LANE2` field names are not broadly hand-referenced outside the generated offset and mask headers in this source tree. Their integration value is as generated field metadata available to lower-level PHY access, diagnostics, DMUB-facing register packing, or future register-table consumers.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask can compile cleanly while causing the driver or firmware to read, preserve, or overwrite the wrong PHY bits.
- The chunk boundaries are artificial. The first visible lines are the tail of `LANE1` TX analog `CREG03`, and the final lines stop in lane 2 TX power-up timing. Adjacent chunks are required before making complete per-lane or per-file claims.
- Lane copy/paste symmetry is risky. Lane 1 and lane 2 fields are structurally similar, but a lane-number or register-name mismatch can affect only one physical lane or connector configuration.
- Override fields are high impact. Many fields intentionally bypass hardware-controlled values; using stale masks for `*_OVRD_EN`, pstate, rate, width, CDR, VCO, DCC, DFE, CTLE, or signal-detect controls can leave a link trained with forced or inconsistent PHY state.
- Calibration/status fields are timing-sensitive. Misdecoded VCO calibration, CDR lock, DFE tap status, IQC status, calibration-done, RX-valid, or power-state-machine fields can produce bad polling decisions and intermittent link failures.
- Reserved fields appear frequently. Accidental writes through an overly broad mask can modify reserved bits; read-modify-write helpers must use the exact generated field masks.
- Power-state and power-up timing masks affect reliability across modesets, hotplug, low-power states, and resume. Bad values can appear as link-training timeouts, blank displays, high bit-error rates, or failures only at specific rates and lane widths.

## Test Signals

Useful validation signals are mostly generated-header consistency checks plus hardware display behavior:

- Build AMDGPU/DC with DCN 3.2 support enabled; missing or renamed macros should fail in DCN 3.2 resource, IRQ, GPIO, clock-manager, and DMUB register setup.
- Mechanically verify that every `__SHIFT` macro in lines 129582-131967 has exactly one matching `_MASK` macro and that field names match between the two sets.
- Compare this range against AMD's authoritative DCN 3.2 register database and adjacent generated C20 PHY lane blocks, especially lane 0 and lane 2/3 equivalents, where layout symmetry is expected.
- Exercise DP links that use the CR2 PHY block across lane counts, link rates, training patterns, hotplug, suspend/resume, and display power-state transitions.
- Validate PHY-sensitive features: link training stability, CDR lock, VCO calibration completion, signal detect, RX-valid status, DFE/CTLE/VGA adaptation, DCC calibration, loopback/diagnostic paths, and lane-specific error counters.
- Watch kernel logs and display diagnostics for AUX/link-training failures, repeated retrains, blank displays, CRC or bit-error reports, stuck calibration/status polling, power-state transition timeouts, and resume-only failures.

## Cross-Chunk Notes

Previous chunks own the start of the `C20_PHY_CR2_LANE1` TX and RX field map, including `LANE1_DIG_ASIC_LANE_OVRD_IN`, lane 1 TX ASIC override/input/output, TX power-control, TX DCC, TX IRQ, and the beginning of lane 1 TX/RX analog CREG groups. Later chunks continue lane 2 TX power timing/control/status, lane 2 TX DCC/IRQ, lane 2 analog and RX groups, and the remaining C20 PHY CR2 lane field metadata. The final per-file research document should merge these neighboring chunks before describing the full `dcn_3_2_0_sh_mask.h` C20 PHY coverage.
