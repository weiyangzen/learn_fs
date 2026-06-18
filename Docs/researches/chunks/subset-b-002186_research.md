# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 86301-88683

## Scope And Purpose

This chunk is a generated AMD DCN 4.1.0 register bitfield header section. It contains only preprocessor definitions: each hardware register field is represented as a `__SHIFT` macro and a matching `_MASK` macro. Driver code does not call functions here directly; it includes this file so DC register helpers can pack, unpack, update, and read fields by symbolic name instead of hard-coded bit positions.

The selected lines cover the middle of the `DPCSSYS_CR1` block. The chunk starts after the base `DPCSSYS_CR1_SUP_DIG_RTUNE_CONFIG` register and continues through `DPCSSYS_CR1_LANE1_DIG_RX_ADPTCTL_DFE_TAP2_STATUS`, ending before additional lane 1 DFE/slicer/adaptation registers. The content is mostly 16-bit control-register field descriptions with `0x....L` masks, plus reserved field masks that preserve or isolate unused bits.

Functionally, these definitions describe DisplayPort/PHY support logic for one DPCS control-register instance:

- super-digital resistor tuning, calibration timing, PLL override/status, analog bandgap/reference, and MPLL PMIX controls;
- lane 0 TX ASIC override inputs/outputs, TX power-state programming, DCC DAC access, TX clock alignment, LBERT test control, RX statistic counters, and analog TX override/status fields;
- lane 1 ASIC TX/RX override inputs/outputs, TX power-state programming, RX power/VCO calibration, RX alignment/LBERT, CDR/DPLL controls, and the first RX adaptation-control configuration/status fields.

## APIs, Types, And Macros

There are no C types or executable functions in this chunk. The public surface is the generated macro naming convention:

- `DPCSSYS_CR1_<register>__<field>__SHIFT` gives the field's least-significant bit.
- `DPCSSYS_CR1_<register>__<field>_MASK` gives the unshifted bit mask in the register word.
- `RESERVED_*` fields document bits that should not be treated as functional programming fields.

These macros are consumed by display register helper families such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_UPDATE`, and indexed-register helpers in AMD display code. `dmub_reg.h` defines `FD_SHIFT(reg, field)` and `FD_MASK(reg, field)` as token-pasting expressions over exactly this macro shape. `reg_helper.h` provides direct and indexed read/update helpers that rely on the generated masks and shifts to avoid corrupting adjacent bits.

For this chunk, the corresponding indexed register offsets are not in `dcn_4_1_0_offset.h`; matching `ixDPCSSYS_CR1_*` offsets appear in DPCS offset headers such as `dpcs_4_2_0_offset.h`, `dpcs_4_2_2_offset.h`, and `dpcs_4_2_3_offset.h`. Examples include `ixDPCSSYS_CR1_SUP_DIG_RTUNE_TXDN_SET_VAL`, `ixDPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0`, `ixDPCSSYS_CR1_LANE1_DIG_RX_CDR_CDR_CTL_0`, and `ixDPCSSYS_CR1_LANE1_DIG_RX_ADPTCTL_DFE_TAP2_STATUS`.

## Register Families Covered

`DPCSSYS_CR1_SUP_DIG_RTUNE_*` fields describe resistor/termination tuning state. The visible registers include TXDN/TXUP set values and status values, RX status, calibration timing counters (`RT_RESULT_TIME`, `RT_EVAL_TIME`, `RT_RST_TIME`, `RT_ACK_TIME`, `RT_TXDN_SETTLE_TIME`, `RT_PWRUP_TIME`), and TX calibration code fields. These are low-level analog calibration knobs used when the link PHY tunes receive and transmit termination values.

`DPCSSYS_CR1_SUP_DIG_ANA_*` fields cover MPLLA/MPLLB override outputs and status. The large `_MPLLA_OVRD_OUT_0` and `_MPLLB_OVRD_OUT_0` registers expose bitfields for word/HDMI/div/output clocks, output enables, analog enable, reset, calibration, feedback clock, gearshift, standby, and override select. `_OVRD_OUT_1` and `_OVRD_OUT_2` carry analog integrator and charge-pump fields. RTUNE, bandgap, reference regulator, async reset, MPLL PMIX, and analog status fields complete the super-digital/analog control group.

`DPCSSYS_CR1_LANE0_DIG_ASIC_*` and `DPCSSYS_CR1_LANE1_DIG_ASIC_*` describe digital bridge signals between per-lane logic and PHY/ASIC controls. The override-input registers usually pair a value bitfield with an override-enable bitfield, letting software or debug logic force lane enable, TX data/async/data-enable paths, power-state requests, serializer loopback, beacon/VBOOST/IBOOST, RX detect, RX termination, RX adaptation, LFPS/loss-of-signal thresholds, CDR/VCO load values, and RX valid behavior. The ASIC input/output/status variants expose the non-overridden hardware-facing state.

`DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_*` and `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_*` define TX power-state behavior. The P0/P0S/P1/P2 registers carry power enables, termination enables, reset enables, serializer enables, data enable, idle/power-good selectors, and per-state on/off behavior. `TX_PWRUP_TIME_*` registers provide timing constants for power-up sequencing, PLL/clock/data/serializer phases, and related settle intervals.

`DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_DCC_*` and `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_DCC_*` define DCC DAC control path fields: bank address/data, DAC control, DAC range/selection, ACK, and DAC address. These are calibration/programming fields used by the lane's duty-cycle correction or DAC calibration path.

`DPCSSYS_CR1_LANE0_DIG_RX_STAT_*` exposes lane 0 receive-statistic and match/filter controls. The block includes load values, data masks, match controls, statistic controls, sample count, status counters, calibration compare clock control, and stat-stop controls. This is a diagnostic and validation surface for observing RX patterns or internal counters.

`DPCSSYS_CR1_LANE0_DIG_ANA_TX_*` and related `DPCSSYS_CR1_LANE0_ANA_TX_*` fields expose analog TX override, TX termination code, EQ override, DCC DAC override, measurement, power override, alternate bus, ATB, DAC, VREG, mux, misc, and reserved analog register fields. These are direct PHY analog controls and observability points for lane 0 TX.

`DPCSSYS_CR1_LANE1_DIG_RX_*` expands the chunk into the lane 1 receive side. It covers RX power states and power-up timing, VCO calibration controls/timing/status, XAUI common-mask alignment, LBERT control/error, CDR controls/status, DPLL frequency and frequency bounds, and adaptation controller configuration. The adaptation fields configure CTLE/VGA/ATT/DFE enables, thresholds, step sizes, adaptation reset selectors, and status results for ATT, VGA, CTLE, and DFE tap 1/tap 2.

## Control Flow And Data Flow

The header has no runtime control flow. Its data flow is compile-time token expansion:

1. A DCN401 source file includes `dcn/dcn_4_1_0_sh_mask.h`.
2. Hardware object register lists or helper macros name a register and field.
3. Token-pasting helpers expand that pair into a field mask and shift from this header.
4. Register access helpers read a register, clear the masked field, shift and mask the new value, then write the register back; read helpers mask and shift the raw register value into a field value.

For indexed DPCS control registers, the mask/shift from this file must be paired with the matching `ixDPCSSYS_CR1_*` offset through the indexed CR address/data path. In older or adjacent DCN link-encoder code, `RDPCS_TX_CR_ADDR` and `RDPCS_TX_CR_DATA` style fields are used for this kind of indirect access; the DPCS offset headers provide the index numbers for the `DPCSSYS_CR1_*` registers.

## State And Persistence Behavior

This chunk does not allocate memory or persist software state. The state it describes is hardware register state inside the display/link PHY. Writes to override, calibration, PLL, power-state, and adaptation fields persist in the hardware block until changed by software, reset by a power/reset sequence, or overwritten by firmware/hardware state machines.

The most important persistence property is bit preservation. Many registers combine functional fields with reserved bits or adjacent fields owned by other hardware flows. Correct masks allow read-modify-write helpers to update one field without disturbing the rest of the register. Incorrect masks can silently leave a lane in a forced override state, corrupt calibration results, misprogram PLL/power timing, or break later link training because stale values remain in hardware.

## Dependencies And Integration Points

Primary include users of `dcn_4_1_0_sh_mask.h` in the DCN401 display stack include DMUB service code, IRQ service, clock manager, GPIO factory/translation, and DCN401 resource construction. The source chunk itself is lower-level than most of those files; it supplies generated field constants to the common register abstraction used throughout the AMD display driver.

Important dependency boundaries are:

- `dcn_4_1_0_offset.h` for direct DCN register addresses used by the same generated helper style.
- DPCS offset headers such as `dpcs_4_2_0_offset.h`, `dpcs_4_2_2_offset.h`, and `dpcs_4_2_3_offset.h` for `ixDPCSSYS_CR1_*` indirect control-register indices matching this chunk's field definitions.
- `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h` for direct and indexed `REG_*`/`IX_REG_*` field access.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h` for DMUB-side `FD_MASK` and `FD_SHIFT` token expansion.
- Link encoder, clock, resource, and hardware-sequencer code that must keep register-list macros synchronized with the generated mask/shift names for the ASIC generation.

Because these are generated ASIC definitions, the integration contract is name stability and numerical correctness. Consumers assume the macro names match hardware documentation and that masks align exactly with the corresponding shift values.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A one-bit error in a mask or shift can compile cleanly but write the wrong PHY field. In this chunk that could affect RTUNE termination, MPLL enable/reset/calibration, bandgap/reference control, TX power sequencing, serializer/data enables, VCO/CDR/DPLL setup, or RX adaptation thresholds.

Override fields are particularly sensitive because many pairs use a value bit and an enable bit. Setting an override value without its enable has no effect; setting enable with a stale value can force hardware away from its normal state machine. The same pattern appears across TX, RX, lane, and analog override registers.

Reserved masks must not be treated as writable capability bits. They exist so helper-generated code can preserve or document unused regions. A caller that writes full literal register values instead of field updates risks toggling reserved bits.

Lane and instance naming is another edge case. This chunk mixes lane 0 and lane 1 fields under `DPCSSYS_CR1`; copying register-list entries between lanes or CR instances can target a valid-looking macro with the wrong lane semantics.

The chunk also starts and ends mid-family. Reconciliation with adjacent chunks is required before producing a final per-file report so the complete `DPCSSYS_CR1_SUP_DIG_RTUNE_CONFIG` context and the remaining lane 1 adaptation/slicer fields are not lost.

## Test Signals

There are no unit tests for this header as a standalone artifact. Useful validation signals are build-time and hardware/integration oriented:

- C compilation of DCN401 display, DMUB, GPIO, IRQ, clock-manager, and resource files confirms that register-list token pasting can find the expected `__SHIFT` and `_MASK` names.
- Static consistency checks can verify each field has both a shift and a mask and that masks do not overlap unexpectedly within a register, aside from documented reserved fields.
- Link bring-up and display hotplug tests on DCN401-class hardware are the real behavioral signal for PLL, RTUNE, TX power, RX CDR, and adaptation fields.
- DisplayPort link-training logs, HPD/HPDRX interrupt behavior, vblank/vupdate stability, and DMUB firmware initialization are downstream symptoms if these generated constants are wrong.
- Debug or lab tests that read back DPCS indexed registers after programming are the most direct way to catch mask/shift mismatches for this specific `DPCSSYS_CR1` block.
