# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 88179-90536

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It provides C preprocessor constants that describe bit positions and masks for DPCS CR4 lane registers; it does not contain executable driver logic. AMDGPU display code uses these constants with companion register-offset headers and register-access helpers to program or decode PHY, lane, PLL, power, calibration, adaptation, interrupt, and debug/test fields without hard-coding bit arithmetic.

The requested range contains 2,358 lines, 2,141 `#define` statements, 1,072 `__SHIFT` macros, 1,069 `_MASK` macros, and 217 register comment boundaries. It starts in the middle of `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL`, completes the tail of CR4 lane 1 analog TX/RX field definitions, then covers a large CR4 lane 2 block: digital ASIC override/input/output mirrors, TX/RX power-control and calibration fields, CDR/DPLL/adaptation/statistics fields, MPHY controls, digital-to-analog override outputs, and the beginning of lane 2 analog TX/RX fields. The final lines start `DPCSSYS_CR4_LANE2_ANA_RX_SQ`; that register's remaining mask definitions continue in the next chunk.

Although the path is inside a local `ceph-client` source mirror, this file belongs to AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, memory allocations, locks, direct MMIO accesses, or exported symbols in this range. The public interface is the generated macro pair pattern:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit index for a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field in a register value.

The main macro groups in this chunk are:

- `DPCSSYS_CR4_LANE1_ANA_TX_*` and `DPCSSYS_CR4_LANE1_ANA_RX_*`: tail definitions for lane 1 analog TX termination, clock override, TX miscellaneous, TX reserved, RX CDR/deserializer, slicer, power, squelch, calibration, analog test bus measurement, forced ATB value, and reserved fields.
- `DPCSSYS_CR4_LANE2_DIG_ASIC_*_OVRD_IN_*`: digital ASIC override input fields for lane, TX, RX, RX EQ, and additional TX/RX override banks. These include request, pstate, rate, width, MPLLA/MPLLB selection/enables, data enable, detect-RX, reset, loopback, async enable, RX adaptation, RX termination, SQ threshold/response, CDR/VCO/DFE/CTLE/VGA/ATT, PH2 calibration, ATE, and override-enable fields.
- `DPCSSYS_CR4_LANE2_DIG_ASIC_*_ASIC_IN_*` and `*_ASIC_OUT*`: non-override ASIC input/output mirror fields for lane, TX, RX, RX EQ, CDR VCO, request/ack, data enable, detect-RX, pstate/rate/width, equalization, adaptation, and status observation.
- `DPCSSYS_CR4_LANE2_DIG_TX_PWRCTL_*`: TX pstate configuration, data-enable and request/reset behavior, RX-detect bypass and termination settings, power-up timing windows, DCC DAC bank/address/data/select/range/control, DAC acknowledgment, and TX clock-align/LBERT control fields.
- `DPCSSYS_CR4_LANE2_DIG_RX_PWRCTL_*`: RX pstate configuration and RX power-up timing fields, including request, data-enable, reset, DFE, deserializer, loopback, fast-start, clock-enable, and analog-front-end enable controls.
- `DPCSSYS_CR4_LANE2_DIG_RX_VCOCAL_*`, `DPCSSYS_CR4_LANE2_DIG_RX_CDR_*`, and `DPCSSYS_CR4_LANE2_DIG_RX_DPLL_*`: VCO calibration control/status/timing, CDR control/status, and digital PLL frequency and frequency-bound fields.
- `DPCSSYS_CR4_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation configuration/status fields for ATT, VGA, CTLE, DFE taps, slicer offsets, DAC-control muxes, adaptation reset, and CR-bank access.
- `DPCSSYS_CR4_LANE2_DIG_RX_STAT_*`: status match/mask/control/counter fields, sample counters, stop controls, and calibration-comparator clock controls used to observe or qualify RX state.
- `DPCSSYS_CR4_LANE2_DIG_MPHY_*`: MPHY RX PWM control, low-speed termination control, and analog PWM clock-stability count fields.
- `DPCSSYS_CR4_LANE2_DIG_ANA_*_OVRD_OUT*` and `DPCSSYS_CR4_LANE2_DIG_ANA_STATUS_*`: digital-to-analog output/readback masks for TX clock/data/reset/serial/rate, TX termination and EQ, RX control/power/VCO/calibration/DAC/scope/slicer/IQ/signal-change paths, MPHY, signal detect, DCC DAC, and analog status fields.
- `DPCSSYS_CR4_LANE2_ANA_TX_*` and `DPCSSYS_CR4_LANE2_ANA_RX_*`: lane 2 analog TX override/measurement, power override, alt bus, ATB, DCC DAC/control, termination code, clock, miscellaneous, reserved, RX clock, CDR/deserializer, slicer, power, and the beginning of squelch control definitions.

Several field-name patterns encode hardware semantics even though this header only describes layout: `*_OVRD_EN`, `ovrd_*`, `*_reg`, `*_REQ`, `*_ACK`, `*_DONE`, `*_STATUS`, `*_STAT`, `*_PSTATE_*`, `*_PWRUP_TIME_*`, `*_CAL*`, `*_DFE*`, `*_CTLE*`, `*_VGA*`, `*_ATT*`, `*_SLICER*`, `*_TERM*`, `*_LBERT*`, and `*_ATB*`.

## Control Flow

This header has no runtime control flow. It contributes to display-driver behavior through compile-time register descriptions:

1. The matching DPCS 4.2.2 offset header identifies the CR4 lane register addresses or indirect indexes.
2. This shift/mask header supplies field positions and masks for those register names.
3. AMD display code combines offsets, shifts, and masks through generated register tables or token-pasting helpers.
4. Runtime MMIO or indirect-register helpers perform read/modify/write, polling, or decode operations against DPCS hardware.

Actual sequencing lives outside this file. Examples include entering TX/RX pstate changes, asserting resets, enabling clocks/data, programming MPLL lane selection, forcing or releasing overrides, starting VCO/adaptation/calibration, waiting for request/ack or done bits, clearing/masking interrupt/status conditions, and collecting RX statistics.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible control and status fields that may be transient, latched, read-only, write-one-to-clear, self-clearing, or retained depending on the DPCS block, power state, and access path.

The named hardware state includes:

- Lane 1 analog tail state for TX termination, TX clocking, TX miscellaneous controls, RX CDR/deserializer, RX power, squelch, calibration, ATB measurement, and reserved/NC fields.
- Lane 2 digital ASIC override and mirror state for TX/RX request, pstate, rate, width, reset, data-enable, detect-RX, loopback, MPLL selection, RX equalization/adaptation, PH2 calibration, CDR/VCO, ATE, and analog-front-end controls.
- Lane 2 TX/RX power-control state, including pstate programming, power-up delays, DCC DAC state, DCC bank access, clock alignment, LBERT controls, RX VCO calibration, CDR/DPLL frequency, and RX adaptation controls.
- Lane 2 RX statistics and debug state, including match controls, masks, counters, stop controls, sample counts, and calibration-comparator clock controls.
- Lane 2 digital-to-analog output/readback state for TX analog controls, RX analog controls, termination, EQ, VCO, calibration, DAC selection, scope/slicer/IQ paths, MPHY, signal-detect, DCC DAC, and analog status.
- Lane 2 analog TX/RX control state for TX measurement/power/ATB/DCC/termination/clock/miscellaneous controls and RX clock/CDR/slicer/power/squelch fields.

Persistence is hardware-defined. Values may survive until the next modeset, link reconfiguration, suspend/resume, GPU reset, ASIC reset, power-gating transition, or firmware/hardware state-machine rewrite. The header does not describe reset values, legal write values, access width, ownership, volatility, or the ordering constraints needed to program these fields safely.

## Dependencies And Integration Points

This generated header must stay synchronized with its ASIC register database and with the matching DPCS 4.2.2 register-offset header. Consumers generally assume that register names in this file correspond to offset macros in the companion generated header and that field names match the token-pasted register-list definitions used by AMDGPU Display Core.

Integration points include:

- Companion AMD generated headers under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`, especially the DPCS 4.2.2 offset definitions and adjacent chunks of this same shift/mask file.
- AMDGPU Display Core resource, link, PHY, and encoder code that builds ASIC-specific register tables from offset and shift/mask headers.
- Register helper paths that program DisplayPort/HDMI lane bring-up, link training, pstate changes, RX adaptation, TX equalization, termination, signal detect, CDR/DPLL/VCO calibration, DCC calibration, and debug/test flows.
- Hardware/firmware state machines that interpret the same request/ack, override, calibration, status, and power-control fields.

The range crosses semantic regions. Lines 88179-88464 finish CR4 lane 1 analog fields, line 88465 begins CR4 lane 2 digital ASIC override/mirror fields, line 88937 begins lane 2 TX/RX power/calibration/clocking and RX adaptation/statistics fields, line 89855 begins lane 2 digital-to-analog override/status readback fields, and line 90236 moves into lane 2 analog TX/RX fields. Those boundaries should be preserved by the merge lane when building the final per-file report.

## Risks And Edge Cases

- These are untyped preprocessor constants. Incorrect masks or shifts can compile cleanly and produce subtle PHY or display-link failures at runtime.
- The file is generated. Manual edits can diverge from AMD's register source, companion offset headers, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first line continues `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL` from the previous chunk, and the final register `DPCSSYS_CR4_LANE2_ANA_RX_SQ` continues into the next chunk.
- Override/value and override-enable fields are easy to confuse. Misprogramming them can force resets, clocks, pstate/rate/width, data-enable, loopback, MPLL selection, termination, CDR/VCO behavior, RX adaptation, or analog controls away from hardware/firmware ownership.
- Request/ack, done, status, IRQ-like, and counter fields are sequencing-sensitive. A wrong field definition can cause false readiness, missed status, uncleared events, link-training timeouts, or hangs during lane bring-up/teardown.
- Analog and PHY tuning fields such as TX termination, TX EQ leg/pre/post controls, DCC DAC, RX ATT/VGA/CTLE/DFE/slicer offsets, CDR/DPLL/VCO controls, signal-detect thresholds, squelch response/threshold, and MPHY PWM/termination can fail only on specific link rates, boards, cable/sink combinations, or voltage/temperature corners.
- Reserved and `NC` masks appear throughout the range. Driver code should not repurpose them unless an authoritative programming guide explicitly defines them for the target ASIC stepping.
- Generated case and spelling are part of the API. Examples such as `sq_ctrl_tresh_reg`, mixed uppercase ASIC field names, and numbered split fields must remain exactly as generated for token-pasted users.
- Similar CR4 lane 1 and lane 2 macro names are structurally repeated. Using a lane 1 mask with a lane 2 offset, or mixing DPCS 4.2.2 with a neighboring DPCS-generation header, may compile if names overlap but program the wrong silicon layout.

## Test Signals

Useful validation should combine generated-header consistency checks with display hardware testing:

- Build AMDGPU display configurations that include DPCS 4.2.2 support. Missing, renamed, or malformed macros should surface in register table compilation.
- Mechanically compare this range against the authoritative DPCS 4.2.2 register database and verify that complete fields have matching `__SHIFT`/`_MASK` pairs; account for the split first and last registers.
- Cross-check complete register groups in this chunk against the matching DPCS 4.2.2 offset header so each shift/mask register has a corresponding offset definition.
- Run structural diffs across repeated lane 1/lane 2 and TX/RX override/status families to catch generator drift while allowing intentional lane- or block-specific differences.
- Exercise DisplayPort/HDMI link bring-up, link-rate changes, hotplug, modeset, blank/unblank, suspend/resume, and GPU reset on hardware using this DPCS generation.
- Watch runtime logs and register dumps for request/ack timeouts, stuck reset/data-enable/clock overrides, RX adaptation failures, CDR/DPLL/VCO calibration failures, unstable signal detect, DCC calibration issues, LBERT errors, and RX statistics counters that do not behave as expected.
- Decode known-good register dumps with these masks and compare against hardware documentation or reference tools for pstate, power-up timing, TX termination/EQ, RX ATT/VGA/CTLE/DFE/slicer, CDR/DPLL/VCO, DCC DAC, signal-detect, MPHY, and analog ATB/measurement fields.
- Treat ATE, OCLA/LBERT, and forced analog/debug override paths as controlled diagnostics only; forcing these bits can bypass normal PHY control.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL`, including the register comment and the first field definitions before `ovrd_reset_term`. This chunk completes that register and continues through lane 1 analog RX reserved fields before entering the lane 2 digital block.

The next chunk should complete `DPCSSYS_CR4_LANE2_ANA_RX_SQ` by adding the remaining masks after `afe_loopback_sel`, then continue lane 2 analog RX calibration and later CR4 lane definitions. The final merged per-file report should reconcile these split register groups before making whole-file coverage claims.
