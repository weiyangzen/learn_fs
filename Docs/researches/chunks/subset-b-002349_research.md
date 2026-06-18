# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 28637-30999

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for CR1 lane register fields. It contains only preprocessor constants: `__SHIFT` macros define bit positions and `_MASK` macros define field masks for DPCS hardware registers. The range has 2,135 `#define` entries across 228 register-comment groups: 1,071 shift constants and 1,073 mask constants. It starts in the middle of `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1`, covers the remainder of CR1 lane 1 RX statistic and analog TX/RX-related fields, then covers a broad CR1 lane 2 region from ASIC-facing controls through TX/RX power, calibration, CDR/DPLL, adaptation, statistics, MPHY, and the beginning of TX analog equalization override fields. It ends inside `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3`.

Although this file is located under a `ceph-client` source mirror, this chunk is AMDGPU display PHY register metadata. It has no Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header slice is to give AMDGPU display code a generated bitfield contract for DPCS 4.2.2 CR1 lane registers. Callers combine these constants with addresses from the matching `dpcs_4_2_2_offset.h` header and the AMD display register helper macros to read, update, and write DPCS registers without hard-coding numeric bit positions in driver logic.

The covered fields describe:

- CR1 lane 1 RX statistic controls, sample counters, statistic counters, pattern/mask continuation fields, statistic-stop behavior, MPHY low-speed controls, RX termination timing, and PWM clock-stability control.
- CR1 lane 1 digital analog TX/RX override outputs for TX clocks, refgen, VCM hold, reset, serial/data enable, data rate, div4/RX detect, termination code, driver source, equalization taps, RX power, RX VCO/CDR controls, RX calibration, AFE/VGA/CTLE/scope/slicer/IQ controls, signal detect, DCC DAC, and analog TX measurement/power/miscellaneous registers.
- CR1 lane 2 ASIC-facing lane/TX/RX override inputs and outputs, including request/ack handshakes, pstate/rate/width, data enable, reset, loopback, CDR/adaptation controls, equalization inputs, RX CDR/VCO values, cross-lane clock/shift controls, and OCLA enables.
- CR1 lane 2 TX power-control state fields for P0, P0S, P1, and P2, TX power-up timing fields, DCC CR-bank/DAC access, TX clock alignment, and TX LBERT controls.
- CR1 lane 2 RX power-control state fields, RX power-up timing, RX VCO calibration controls/status, RX alignment and LBERT status, CDR/DPLL configuration/status, RX adaptation configuration/status, DAC/slicer offsets, RX statistic counters, MPHY controls, and the start of lane 2 TX analog override/equalization fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocations, or direct MMIO operations in this range. The exported interface is the generated macro namespace:

- `DPCSSYS_CR1_LANE*_...__FIELD__SHIFT`: least-significant bit index for `FIELD`.
- `DPCSSYS_CR1_LANE*_...__FIELD_MASK`: bit mask for the same field.
- Register delimiter comments such as `//DPCSSYS_CR1_LANE2_DIG_RX_CDR_CDR_CTL_0`: field-group markers corresponding to register address names in the companion offset header.

Notable lane 1 macro groups:

- `DPCSSYS_CR1_LANE1_DIG_RX_STAT_*`: statistic counter enables, sample-count done bits, statistic counter values, comparator clock control, CR1A/CR1B pattern and mask fields, delayed-data/scope/sample-count controls, and statistic stop.
- `DPCSSYS_CR1_LANE1_DIG_MPHY_*`: RX PWM polarity/data polarity, low-speed termination count, and analog PWM clock stable count.
- `DPCSSYS_CR1_LANE1_DIG_ANA_TX_*`: TX analog override control for clock/data/refgen/VCM/reset/serial/rate, termination-code and driver-source override, termination clocking, EQ override pull-enable/pull-direction/pre/post controls, DCC DAC override controls, fast-start/loopback fields, and TX override outputs.
- `DPCSSYS_CR1_LANE1_DIG_ANA_RX_*`: RX data-rate/word-clock/div4/DFE/adaptation overrides, RX power enables, RX CDR/VCO frequency tune controls, RX calibration DAC and AFE update clocks, AFE ATT/VGA/CTLE, scope/slicer/IQ controls, RX termination override, MPHY squelch/PWM controls, signal-detect overrides, and analog status readbacks.
- `DPCSSYS_CR1_LANE1_ANA_TX_*` and `DPCSSYS_CR1_LANE1_ANA_RX_*`: raw analog-side register layouts for TX measurement, power override, alternate bus/ATB selection, TX DCC/termination/misc fields, RX clock/CDR/slicer/power/squelch/calibration/ATB fields, and reserved analog register fields.

Notable lane 2 macro groups:

- `DPCSSYS_CR1_LANE2_DIG_ASIC_*`: lane loopback and AC JTAG controls; TX/RX override inputs for request, pstate, rate, width, data enable, reset, polarity, low-power detect, HDMI mode, clock readiness, DCC/termination/PWM controls; TX/RX ack/status outputs; RX EQ and CDR/VCO input fields; cross-lane repeater/clock/shift/master controls; and OCLA clock/data enables.
- `DPCSSYS_CR1_LANE2_DIG_TX_PWRCTL_*`: per-power-state TX enables for refgen, VCM hold, analog/digital clocks, reset, serial, data, RX-detect, VBOOST, and DCC compensation; TX startup timing fields; DCC bank address/data/control/range/selection/ack/address; TX clock alignment; and TX LBERT mode/error injection controls.
- `DPCSSYS_CR1_LANE2_DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, and `DIG_RX_DPLL_*`: RX AFE/clock/CDR/deserializer/adaptation power controls, RX P-state control, RX power-up timing, VCO calibration mode/timing/status, XAUI comma mask, RX LBERT error count, CDR tracking/SSC/PI/slicer controls, CDR status, and DPLL frequency bounds.
- `DPCSSYS_CR1_LANE2_DIG_RX_ADPTCTL_*`: adaptation configuration words, reset control, ATT/VGA/CTLE/DFE tap status, even/odd VDAC offsets, slicer levels, DAC-control selection, and adaptation CR-bank address/data fields.
- `DPCSSYS_CR1_LANE2_DIG_RX_STAT_*` and `DIG_MPHY_*`: load-value/data-mask/pattern-match registers, statistic counter control and stop, sample/count done fields, PWM polarity, termination low-speed count, and PWM clock stability.
- `DPCSSYS_CR1_LANE2_DIG_ANA_TX_*`: beginning of lane 2 TX analog override controls, including TX clock/data/refgen/VCM/reset/serial/rate, termination-code override, termination clock, and the first EQ override registers for leg pull enable, EQ mux selection, pre-cursor, and the first post-cursor field.

## Control Flow

This generated header has no runtime control flow. It only supplies compile-time constants. The runtime flow belongs to AMD display code that:

1. Includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`.
2. Builds register offset/shift/mask tables through macros such as `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`/`DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. Uses register helper operations to clear masked fields, shift new values into position, and read or update hardware registers.

The implied hardware sequencing includes display link bring-up, lane power transitions, TX/RX request-acknowledge handshakes, TX DCC programming, RX VCO/CDR/DPLL setup, RX adaptation, statistic sampling, MPHY low-speed behavior, analog override/debug programming, and LBERT/OCLA diagnostics. This header does not enforce ordering, polling, timeouts, or access direction.

## State And Persistence Behavior

The macros themselves are stateless and persistent only as compile-time constants. The state they describe lives in volatile DPCS hardware registers. Register values may be modified by normal link training, modesets, hotplug handling, runtime PHY retuning, diagnostic paths, suspend/resume, power gating, GPU reset, or firmware/hardware state machines.

Several field families describe stateful hardware behavior:

- Request/ack, valid, done, calibration, and error fields reflect transient hardware handshakes and status.
- P-state, reset, clock-enable, serial-enable, data-enable, adaptation-enable, and override-enable fields influence lane operation until rewritten or reset by hardware.
- DCC, VCO, CDR, DPLL, CTLE, VGA, ATT, DFE, slicer, IQ phase, signal-detect, and termination fields encode analog tuning state that may be sensitive to lane rate, board, cable, sink, voltage, and temperature.
- Reserved masks represent hardware-owned or undocumented bits that consumers should preserve or avoid unless the authoritative programming guide says otherwise.

## Dependencies

This chunk depends on the DPCS 4.2.2 register-generation source staying synchronized with the target ASIC. The most important paired file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which supplies the matching `ixDPCSSYS_CR1_LANE*...` register addresses. A mask/shift macro from this file is meaningful only when paired with the corresponding DPCS 4.2.2 offset macro.

The concrete in-tree consumer for this generated header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`. That resource file builds DCN 3.1.5 link encoder register tables with `DPCS_DCN31_REG_LIST(id)` and appends `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` to the link encoder shift/mask structures.

Related integration patterns live in AMD display DIO/HPO link encoder headers, especially the DCN31 DPCS register-list and mask-list macros. Nearby generated DPCS versions such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` are useful for generator drift checks, but they are not interchangeable with this ASIC-specific 4.2.2 file.

## Integration Points

This chunk participates in AMDGPU display PHY programming for DCN 3.1.5 hardware using DPCS 4.2.2. The lane 1 portion is concentrated on late RX statistics and analog TX/RX controls. The lane 2 portion spans the main control surface for an entire CR1 lane: ASIC interface, TX/RX power sequencing, calibration, CDR/DPLL, receiver adaptation, statistics, low-speed MPHY behavior, and analog TX overrides.

These definitions feed register access helpers indirectly through generated tables. Consumers must maintain three alignments:

- ASIC-version alignment: use DPCS 4.2.2 offsets with DPCS 4.2.2 masks/shifts.
- Instance alignment: use `CR1` masks with `CR1` register addresses.
- Lane alignment: use `LANE1` and `LANE2` macros only with their matching lane addresses and physical lane programming paths.

## Risks And Edge Cases

- Chunk boundaries are not semantic. The first line is a continuation of `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1`, and the final lines stop before `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3` is complete.
- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly and only appear as hardware misprogramming at runtime.
- Manual edits to generated headers can diverge from AMD's register database, the companion offset header, firmware assumptions, and silicon documentation.
- Lane repetition is copy-sensitive. `LANE1` and `LANE2` fields often look structurally similar, but a wrong lane prefix can program the wrong physical lane or produce misleading register dumps.
- Request/ack, valid, done, calibration, and adaptation status fields are sequencing-sensitive. Incorrect masks can produce false readiness, timeouts, stuck training, or failure recovery loops.
- Override-enable fields can bypass normal hardware or firmware control. Leaving override bits asserted after diagnostics can break later link training, power management, hotplug, or suspend/resume.
- Analog tuning fields for DCC, CDR, DPLL, CTLE, VGA, ATT, DFE, slicer, termination, phase, and signal detect can fail only under specific rates, lane counts, sinks, boards, cables, or environmental corners.
- Reserved fields are widely present. Driver code should avoid writing reserved bits unless the programming guide explicitly requires it and should preserve them during read-modify-write sequences.
- Many registers are 16-bit shaped in this slice, but callers should still respect the generated mask rather than assuming a fixed register width across all DPCS generations.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`, especially `dcn315_resource.c` and DCN31 link encoder table initialization.
- Static generation checks that each complete field has matching `__SHIFT` and `_MASK` constants, that masks align with the shift and intended field width, and that the first and last split registers are reconciled with adjacent chunks.
- Cross-checks against `dpcs_4_2_2_offset.h` to ensure every register group in this range has a matching CR1 lane address macro.
- Repetition checks between CR1 lane 1 and lane 2 where the hardware model expects identical field layouts, while allowing intentional lane/position differences and chunk-boundary splits.
- Display bring-up, hotplug, modeset, blank/unblank, suspend/resume, and GPU reset recovery on hardware using DCN 3.1.5 / DPCS 4.2.2.
- Link-training stress across lane counts, rates, and protocols that exercise lane 2 TX/RX request/ack, pstate/rate/width, power sequencing, CDR/DPLL, adaptation, and signal-detect paths.
- PHY diagnostic coverage for RX/TX LBERT, OCLA, RX statistic counters, pattern match controls, DCC DAC selection/ack, VCO calibration status, CDR status, adaptation status, and analog override readback.
- Register dumps from failed link training decoded with these masks to confirm TX power state, RX power/adaptation, CDR/DPLL, DFE/CTLE/VGA/ATT, MPHY, signal-detect, and TX EQ fields match expected programming.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of `DPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1` and earlier CR1 lane 1 RX statistic fields. This chunk completes much of CR1 lane 1's statistic and analog control surface, then covers most of CR1 lane 2 through the start of TX analog EQ override output 3. The next chunk should complete `DPCSSYS_CR1_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_3` and continue the remaining CR1 lane 2 analog TX/RX definitions. The final per-file research document should reconcile these boundary splits before making whole-register or whole-file claims.
