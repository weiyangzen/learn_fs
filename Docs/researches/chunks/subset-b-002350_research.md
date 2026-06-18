# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 31000-33363

## Scope

This chunk covers line 31000 through line 33363 of the generated AMD DPCS 4.2.2 shift/mask header. It is a hardware register-field description block, not executable C. The visible slice contains about 2,140 `#define` entries: paired `__SHIFT` and `_MASK` constants for 16-bit DPCS/PHY control registers. The chunk begins in the middle of `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3` mask definitions and ends in the middle of `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN`, so the adjacent chunks are needed for complete boundary-register coverage.

## Purpose

The purpose of this chunk is to expose bit positions and bit masks for display PHY control/status fields under `DPCSSYS_CR1`. Driver code can combine these field constants with register addresses from the sibling `dpcs_4_2_2_offset.h` header and with AMDGPU/DC register helper macros to read, write, or update specific hardware fields without hard-coding bit arithmetic.

The represented hardware areas are:

- Lane 2 digital-to-analog and analog TX/RX controls, including RX CDR/VCO, calibration, AFE, scope, slicer, signal-detect, DCC DAC, TX power, TX ATB, TX termination, and RX analog power/control fields.
- Lane 3 ASIC-facing lane/TX/RX overrides and status, including request/pstate/rate/width, data enable, loopback, reset, RX detect, MPLL selection, cursor/pre/post equalization, voltage boost, async driver, and handshake acknowledgement fields.
- Lane 3 TX power-control sequencing, including P0/P0S/P1/P2 state enable bits, power-up timing fields, DCC calibration bank/data/DAC controls, TX clock alignment, loopback BERT, and RX statistic/correlation counters.
- Lane 3 digital analog output and analog TX fields, largely mirroring lane 2 TX analog override/measurement/register controls.
- Raw common `CR1_RAWCMN` controls for PHY reset, MPLLA/MPLLB clock/SSC/bandwidth overrides, common MPLL state, SRAM/OCLA/support analog override, firmware/id-code reads, RTUNE values, SRAM built-in logic control, power-gate override/status, supply override, VREF stats, and resistance/reference range controls.
- Raw lane 0 PCS transfer (`CR1_RAWLANE0_DIG_PCS_XF`) TX/RX override, PCS input/output, adaptation, equalization feedback, lane number, reserved registers, and ATE override fields.

## Important Macros And Register Families

The public surface is preprocessor symbols named:

`<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`

Each register family is preceded by a `//<REGISTER>` comment. Within this chunk, 224 complete register-comment blocks are visible plus one boundary register carried from the previous chunk, for 225 unique register names.

Important visible families include:

- `DPCSSYS_CR1_LANE2_DIG_ANA_RX_*`: RX control, power, VCO, calibration, DAC, AFE, scope, slicer, IQ phase/sense, status, term code, MPHY, signal detect, and TX DCC DAC overrides.
- `DPCSSYS_CR1_LANE2_ANA_TX_*` and `DPCSSYS_CR1_LANE2_ANA_RX_*`: lower-level analog TX/RX register fields such as ATB measurement, DCC, term code, clocks, miscellaneous TX settings, RX CDR/deserializer, slicer, power, SQ, calibration, and ATB measurement.
- `DPCSSYS_CR1_LANE3_DIG_ASIC_*`: ASIC-facing lane/TX/RX override and status fields. These provide override-enable/value pairs for request, pstate, rate, width, MPLL select, data enable, reset, RX detect, cursor values, async driver, vboost, HDMI mode, RX/TX loopback, and acknowledgements.
- `DPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX state-machine fields for P-state output enables and timing. P0/P0S/P1/P2 fields expose analog refgen, VCM hold, clock, reset, serial, data, RX detect, vboost, and DCC compensation controls.
- `DPCSSYS_CR1_LANE3_DIG_RX_STAT_*`: RX statistic/correlation load values, masks, pattern-match controls, statistic counter enables, sample count and count outputs, calibration comparator clock controls, and stop controls.
- `DPCSSYS_CR1_RAWCMN_DIG_*`: raw common controls shared under CR1, including common PHY reset, PLL clock/SSC overrides for MPLLA/MPLLB, lane FSM extension, common control overrides, MPLL state, ID/status, RTUNE values for RX/TXDN/TXUP lanes 0-7, SRAM boot logic, power gate overrides, supply/resistance/reference overrides, and VREF stats.
- `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_*`: raw lane 0 PCS exchange fields for TX and RX override inputs, PCS inputs, override outputs, PCS outputs, RX adaptation ack/FOM, RX feedback to TX pre/main/post direction, lane number, reserved storage, and the beginning of ATE override input.

## Control Flow And Usage Model

There is no runtime control flow in this header. The effective flow is compile-time expansion into MMIO field operations elsewhere:

1. A caller chooses a register address macro, typically `ix<REGISTER>` from `dpcs_4_2_2_offset.h`.
2. The caller chooses the field's `__SHIFT` and `_MASK` constants from this header.
3. AMDGPU/DC helper macros shift a value into place, mask it, and perform a register read/modify/write or field read.
4. Hardware implements the actual state transition, acknowledgement, counter update, or self-clearing behavior.

Several field names encode hardware protocols even though no C logic appears here. Examples include `*_OVRD_EN` fields that gate corresponding override values, `*_ACK` status bits for override/PCS handshakes, `*_SELF_CLEAR_DISABLE` fields that alter hardware pulse behavior, `*_START`/`*_STOP` controls for statistic collection, and `*_DONE` bits for sample/counter completion. Driver code using these fields must respect those hardware semantics outside this header.

## State And Persistence Behavior

This file stores no software state. State resides in hardware registers addressed by DPCS MMIO or indirect register access paths. The constants define how software maps logical fields to persistent or transient hardware bits.

State categories visible in this chunk include:

- Power and reset state: PHY functional reset, TX/RX pstate controls, refgen/clock/serial/data enables, reset override bits, power-gate stable/request/acknowledge fields, and SRAM boot-logic start/bypass fields.
- Clock and PLL state: MPLLA/MPLLB word dividers, TX clock divider, div8/div10 enables, bandwidth override, SSC range/clock/enable/fractional controls, MPLL state override, bank select, and force/off timings.
- Analog calibration state: RTUNE readback values for RX/TX up/down, DCC DAC controls and acknowledgements, term-code overrides, VCO/ref load values, calibration mux selection, AFE attenuation/gain/CTLE, slicer controls, and VREF statistics.
- Diagnostic state: ATB measurement controls, OCLA probe selection, RX statistic sample/count registers, LBERT mode/error pattern controls, firmware/id-code read fields, and adaptation FOM/ack values.

Because many fields are override enables or direct analog controls, incorrect writes can persist until reset or until firmware/hardware state machines regain control.

## Dependencies And Integration Points

This generated header depends on normal C preprocessor inclusion and its include guard `_dpcs_4_2_2_SH_MASK_HEADER`. It has no includes of its own and defines no functions, structs, enums, or storage.

Primary integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which contains the matching `ix...` register offsets for these register names. For example, this chunk's lane 3 and raw common fields line up with offsets such as `ixDPCSSYS_CR1_LANE3_DIG_ASIC_TX_OVRD_IN_0`, `ixDPCSSYS_CR1_RAWCMN_DIG_CMN_CTL`, and `ixDPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`.
- AMD display/DC and AMDGPU register helper code that consumes `*_MASK` and `*__SHIFT` constants through generated register-field lists or direct macro use.
- Neighbor ASIC register versions such as `dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_3_sh_mask.h`, and DCN/DPCS generated headers. Similar macro names appear there, so version-specific include selection is important.
- Hardware/firmware tables that determine when override fields are safe to touch. The header only describes layout; it does not enforce sequencing, locking, or ownership between driver, firmware, and PHY state machines.

## Risks

- Header/version mismatch is the largest risk. Pairing this 4.2.2 shift/mask header with a different offset header or ASIC register block can write valid-looking bits to the wrong hardware fields.
- The chunk contains many reserved and `NC` fields. Driver code should preserve reserved bits during read/modify/write unless the hardware programming guide explicitly requires otherwise.
- Override fields can bypass normal PHY control. Setting `*_OVRD_EN`, PLL override, reset override, pstate override, DCC/term override, or power-gate override bits without corresponding value/timing discipline can break link training, display output, or power sequencing.
- Timing fields such as TX VCM hold, vboost disable, reset, serial enable, and RX detect timing are encoded as raw bitfields. Off-by-one shifts or masks would not be caught by C type checking.
- Several fields indicate hardware pulses or self-clearing behavior. Treating them as ordinary persistent bits can cause missed updates or repeated actions.
- This slice starts and ends mid-register. Any automated analysis or regeneration that operates only on this chunk must not conclude that `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3` or `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` are complete in this report.

## Test Signals

Useful validation signals for this chunk are mostly static or hardware-integration oriented:

- Compile coverage: configurations that include DPCS 4.2.2 headers should compile without undefined field or offset macros when lane 2, lane 3, raw common, and raw lane 0 PCS fields are referenced.
- Generated-header consistency: every complete register comment in this slice should have paired `__SHIFT` and `_MASK` macros for each field, and every register should have a matching `ix<REGISTER>` offset in `dpcs_4_2_2_offset.h` unless it is a documented alias or generated exception.
- Bitfield sanity: masks should match shifts and widths, remain within the expected 16-bit register payloads in this DPCS block, and avoid overlap within each register except for intentional aliases.
- Cross-version diffing: compare against adjacent versions (`dpcs_4_2_0`, `dpcs_4_2_3`, DCN generated headers) to identify intentional 4.2.2 differences versus generator drift.
- Runtime/hardware smoke tests: display link bring-up, link training, PHY power transitions, hotplug/RX detect, and mode changes exercise many pstate, PLL, DCC, calibration, and override fields indirectly.
- Diagnostic validation: debug paths that read RX stat counters, firmware/id codes, RTUNE values, adaptation FOM/ack, and ATB/OCLA controls can reveal field-address or mask mismatches without intentionally disturbing normal display operation.
