# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 7227-9584

## Purpose

This chunk is a middle slice of AMD's generated DPCS 4.2.0 shift/mask register-field header. It contains no executable C logic; it publishes preprocessor constants for bit positions and masks in the DPCS control-register space used by AMDGPU Display Core. The matching address constants live in `dpcs_4_2_0_offset.h`, and both headers are included by `display/dc/resource/dcn31/dcn31_resource.c` for DCN 3.1 hardware resource construction.

The range covers 2,139 `#define` entries and 219 register comment groups. It starts inside `DPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_CTL2` at the `SCOPE_DLY_2` mask, continues through lane 0 digital/analog transmit override and status registers, then covers most of lane 1 digital ASIC, TX/RX power, CDR, adaptation, statistics, MPHY, digital-to-analog override, analog TX, and the start of analog RX clock registers. It ends after the first two `DPCSSYS_CR0_LANE1_ANA_RX_CLK_2` shift definitions; that register's remaining fields and masks are outside this chunk.

Although this repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, or callbacks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for packing, unpacking, or updating a register field.
- `<REGISTER>__<FIELD>_MASK`: mask used to isolate the field in a 16-bit-style DPCS register value represented as a C integer literal.

Major register families in this chunk are:

- `DPCSSYS_CR0_LANE0_DIG_RX_STAT_*`: tail of lane 0 receive-statistics control, including sample-count disable and `SC1_STOP`.
- `DPCSSYS_CR0_LANE0_DIG_ANA_TX_*`: lane 0 digital outputs into analog TX controls. Fields cover TX clock shift, data/refgen/VCM/word-clock/MPLL enables, reset, serial enable, data rate, div4, RX detect, override enable, termination-code override, EQ override, TX DCC DAC override, fast start, clock loopback, and AC JTAG enable.
- `DPCSSYS_CR0_LANE0_DIG_ANA_STATUS_0`: lane 0 analog status bits for TX clock-shift acknowledgement, RX detect results, loopback state, RX calibration/scope data, TX DCC calibration result, and EQ mux status.
- `DPCSSYS_CR0_LANE0_ANA_TX_*`: lane 0 direct analog TX control and diagnostics, including measurement override, power override, alternate bus/JTAG data, ATB measurement selectors, DCC DAC and control, termination code, clock override, miscellaneous peaking/slew/vreg/ring controls, and reserved registers.
- `DPCSSYS_CR0_LANE1_DIG_ASIC_*`: lane 1 ASIC-facing override and live signal registers. These expose lane-level reset, TX/RX power states, TX EQ and termination inputs, RX CDR/VCO, AFE/DFE/adaptation, slicer, signal-detect, MPHY, and OCLA-related fields.
- `DPCSSYS_CR0_LANE1_DIG_TX_PWRCTL_*`: lane 1 TX power-state configuration for P0/P0S/P1/P2, power-up timers, DCC CR bank access, DCC DAC control/range/selection/ack/address, TX clock alignment control, and TX LBERT controls.
- `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_*`, `DPCSSYS_CR0_LANE1_DIG_RX_VCOCAL_*`, `DPCSSYS_CR0_LANE1_DIG_RX_CDR_*`, and `DPCSSYS_CR0_LANE1_DIG_RX_DPLL_*`: lane 1 RX power-state, VCO calibration, CDR, DPLL frequency and frequency-bound controls/status.
- `DPCSSYS_CR0_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX adaptation configuration and status for ATT, VGA, CTLE, DFE taps, data/error VDAC offsets, slicer controls, reset, DAC control selection, and CR bank access.
- `DPCSSYS_CR0_LANE1_DIG_RX_STAT_*`: lane 1 receive pattern/statistics controls, sample counters, match/mask registers, statistics counters, calibration comparator clock control, and stop control.
- `DPCSSYS_CR0_LANE1_DIG_MPHY_*`: lane 1 MPHY low-speed PWM, termination, and analog PWM clock-stable count fields.
- `DPCSSYS_CR0_LANE1_DIG_ANA_*`: lane 1 digital override outputs to analog TX/RX, including TX EQ/termination/DCC/fast-start controls, RX control/power/VCO/calibration/DAC/AFE/scope/slicer/IQ/signal-change/status controls, RX termination-code override, MPHY override, and signal-detect override.
- `DPCSSYS_CR0_LANE1_ANA_TX_*`: lane 1 analog TX measurement, power, ATB, DCC, termination, clock, miscellaneous, and reserved registers.
- `DPCSSYS_CR0_LANE1_ANA_RX_CLK_1` and partial `DPCSSYS_CR0_LANE1_ANA_RX_CLK_2`: start of lane 1 analog RX clock controls such as CDR VCO startup, temperature compensation, CDR override, clock enable override, IQ phase-adjust shift, and RX loopback clock shift.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes the header and passes the constants into register-helper macros:

1. DCN 3.1 resource code includes `dpcs_4_2_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste register names into offset, shift, and mask table initializers.
3. DCN resource constructors wire those tables into display/link/PHY-related objects.
4. Runtime paths use register helpers such as read, write, update, get, and set operations; the helpers combine the offset constants with these field masks and shifts to touch individual hardware bits.

The macros do not define sequencing. Consumers must still order lane reset release, TX/RX power transitions, PLL/CDR/VCO programming, DCC/termination/EQ calibration, receive adaptation, statistic sampling, loopback or LBERT diagnostics, and suspend/resume restoration according to silicon requirements.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes DPCS hardware state in CR0 lane registers:

- TX state for lane 0 and lane 1: enable/reset/serial/data-rate controls, word/MPLL clocks, termination code, EQ pre/post/leg-pull settings, DCC DAC calibration controls, fast start, RX detect, and loopback/AC-JTAG paths.
- RX state for lane 1: power states and timers, VCO calibration controls/status, CDR/DPLL programming, adaptation configuration/status, AFE/DFE/slicer/DAC/IQ/scope controls, signal-detect and MPHY low-speed controls.
- Diagnostic state: LBERT enable/error controls, OCLA, ATB measurement selectors, statistics sample/match/count registers, calibration comparator clocking, and status bits for calibration, RX detect, scope, DCC, and analog acknowledgements.
- Override state: many fields explicitly select between ASIC-driven signals and software/debug override values. Incorrectly leaving override-enable bits set can decouple the PHY lane from normal display link training and power management.

Persistence is hardware-defined. Programmed control fields generally last until modeset/link reprogramming, lane power-down, power-gating, suspend/resume, GPU reset, or ASIC reset. Status, acknowledgement, calibration, statistic, and error fields may be read-only, sticky, self-clearing, write-one-to-clear, or only valid while the relevant DPCS clocks and power domains are active. This generated header does not encode those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.0 register database and especially with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides matching `ixDPCSSYS_*` register addresses for the field masks in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which directly includes both DPCS 4.2.0 headers.
- The AMD Display Core register-helper layer, which expects consistent register, shift, and mask naming when building register tables and performing read-modify-write operations.
- Neighboring DPCS generated headers such as `dpcs_4_2_2_*`, `dpcs_4_2_3_*`, and older `dpcs_3_1_4_*`, which indicate related ASIC generations and are useful comparison points when validating generated-field drift.

The most direct behavioral integration is display-link PHY handling: DisplayPort/USB-C style lane bring-up, lane power management, link training, RX/TX calibration, loopback and production diagnostics, and low-level PHY debug or characterization flows.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask compiles cleanly but can write the wrong DPCS bit, corrupt an adjacent field, or silently break link training, lane power, calibration, or diagnostics.
- The file is generated metadata. Manual edits risk divergence from AMD's register database, the matching offset header, firmware assumptions, and silicon documentation.
- The chunk boundary is artificial. It starts after the `DATA_DLY_SEL_2` mask for `LANE0_DIG_RX_STAT_STAT_CTL2`, so full pair accounting for that register requires the previous chunk. It ends before the remaining `LANE1_ANA_RX_CLK_2` shifts and all masks, so full pair accounting for that register requires the next chunk.
- Lane 0 and lane 1 register families are highly repetitive but not identical. Assuming lane 0 field names or semantics apply to lane 1 can miss lane-specific RX, MPHY, VCO, adaptation, or analog additions.
- Override-enable fields are high risk. Debug overrides for TX/RX power, CDR, VCO, EQ, termination, clock, loopback, DCC, and MPHY can leave the PHY in a state normal display code does not expect.
- Reserved and `NC*` fields are exposed as masks. Consumer code should avoid writing non-reset values to those bits unless directed by validated hardware sequences.
- Calibration and status fields are timing-sensitive. Polling before clocks or power are stable can produce false failures; clearing sticky/statistic fields with the wrong mask can lose diagnostic evidence.

## Test Signals

Useful validation is a mix of generated-header checks and hardware behavior:

- Build AMDGPU display support for DCN 3.1. Include or token-paste regressions should surface where `dcn31_resource.c` and register helpers consume DPCS 4.2.0 symbols.
- Mechanically verify that fields in this range have matching `__SHIFT` and `_MASK` definitions where the complete register lies within the range, while allowing the known boundary exceptions at `LANE0_DIG_RX_STAT_STAT_CTL2` and `LANE1_ANA_RX_CLK_2`.
- Compare this slice with the matching `dpcs_4_2_0_offset.h` address range from `ixDPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_CTL2` through `ixDPCSSYS_CR0_LANE1_ANA_RX_CLK_2`.
- Diff against adjacent generated DPCS versions when an ASIC stepping claims compatible lane-register layout.
- On hardware, exercise display link bring-up, retraining, hotplug, suspend/resume, GPU reset, low-power state entry/exit, high link rates, multiple lane counts, and USB-C/DP alternate-mode paths where DPCS lane programming is active.
- For diagnostics, run loopback or LBERT paths where available, inspect DCC/VCO/CDR/adaptation status convergence, confirm RX statistic counters and stop controls behave as expected, and watch kernel logs for link training timeouts, stuck power-state transitions, calibration failures, and resume-only display loss.

## Cross-Chunk Notes

This chunk is part of the larger `dpcs_4_2_0_sh_mask.h` generated header. Earlier chunks define the header prologue and prior DPCS/CR0 lane 0 RX-stat fields; later chunks continue lane 1 analog RX controls and the rest of the DPCS 4.2.0 field namespace. The final per-file research document should merge adjacent chunks before making whole-file claims about all DPCS registers or complete lane coverage.
