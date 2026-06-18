# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 100820-103204

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask slice for DPCSSYS CR1 PHY-related registers. It contains no executable C logic; its exported surface is a set of C preprocessor constants that describe bit positions and bit masks for fields in DisplayPort/PHY control, PLL, supervisor, lane, calibration, and adaptation registers.

The range contains 2,181 `#define` entries across 204 register names. There are 1,089 `__SHIFT` constants and 1,092 `_MASK` constants; the imbalance is a chunking artifact because the first three lines are masks from the prior `DPCSSYS_CR1_SUPX_DIG_SUP_OVRD_OUT` register block. The chunk ends on the comment for `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_DAC_CTRL_SEL_3`, so that register's fields are in the next chunk.

Although this file sits under a local `ceph-client` source tree, the content is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The API is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the field's mask within the register value.

The register groups covered here are:

- `DPCSSYS_CR1_SUPX_*`: shared PHY supervisor, PLL, bandgap, analog, reference-clock, RTUNE, and MPLL A/B control/status fields. Important fields include `MPLLA_EN`, `MPLLB_EN`, PLL multipliers, SSC peak/stepsize fields, HDMI/divider clock controls, `PHY_RESET`, `REF_CLK_EN`, `RTUNE_REQ`, `RTUNE_ACK`, bandgap and VREF controls, MPLL charge-pump and gain settings, lock/power timers, calibration controls, spread-spectrum type, and analog override/status fields.
- `DPCSSYS_CR1_LANEX_DIG_ASIC_*`: per-lane digital ASIC TX/RX override and actual input/output fields. These cover lane reset/power state, TX swing/pre-driver/de-emphasis, TX/RX electrical overrides, PLL/CDR and VCO controls, RX termination, CTLE/VGA/DFE-related inputs, EQ overrides, and observed override outputs.
- `DPCSSYS_CR1_LANEX_DIG_TX_*`: TX power-control states and timing fields, DCC calibration bank address/data controls, DCC DAC range/selection/ack/address fields, TX clock alignment, and TX LBERT controls.
- `DPCSSYS_CR1_LANEX_DIG_RX_*`: RX power-control state/timing fields, RX VCO calibration controls/status, XAUI alignment mask, RX LBERT control/error, CDR control/status, DPLL frequency/bounds, and RX adaptation control configuration/status.
- `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_*`: receiver adaptation controls for CTLE, VGA, ATT, DFE taps, error slicers, adaptation reset, current/voltage DAC selection, and status readbacks for adapted CTLE/VGA/ATT/DFE values.

Most values are 16-bit register masks with an `L` suffix, for example `0x0001L`, `0x03E0L`, `0x7FFFL`, and `0xFFFFL`. Consumers normally combine these field constants with register offsets and AMD display register helpers such as `REG_GET`, `REG_SET`, and `REG_UPDATE`, or with generated register-field tables.

## Control Flow

This header has no runtime branches or call graph. Its control-flow role is compile-time token expansion:

1. DCN 4.1 display/DMUB code includes `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register-list macros expand symbolic field names into mask and shift tables. `dmub_dcn401.c` demonstrates this pattern with `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
3. Runtime register helpers use the paired offset and shift/mask metadata to read, update, or decode MMIO/indirect register fields.
4. For DPCSSYS CR1 specifically, the DCN offset header exposes `regDPCSSYS_CR1_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR1_DPCSSYS_CR_DATA`; detailed DPCS-style register offsets exist in the DPCS offset headers. This chunk provides the bit layouts that are meaningful once the correct indirect register is selected.

Any sequencing requirements for PLL bring-up, reference clocks, power states, RX adaptation, DCC calibration, CDR lock, or status polling live in the hardware programming code and silicon spec. This generated header only names the fields and their bit positions.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes hardware-visible state in several categories:

- Shared PHY/PLL state: MPLL A/B enable, divider, VCO frequency, fractional-N/SSC, charge-pump, lock, calibration, standby, and clock-selection fields.
- Analog and reference state: bandgap, VREF, prescaler, RTUNE, PMIX, voltage regulator, ATB/probe, and override controls.
- Lane TX state: lane power modes, TX reset/powerup timing, swing/de-emphasis/pre-driver settings, DCC calibration DACs, clock alignment, and loopback/bit-error-test controls.
- Lane RX state: RX power modes, VCO calibration, CDR/DPLL configuration, equalization and adaptation parameters, CTLE/VGA/ATT/DFE thresholds, mu values, slicer offsets, and adapted-code status.
- Status/handshake state: RTUNE status, PLL lock/power-state status, analog status, DCC DAC acknowledgements, VCO status, LBERT error status, CDR status, and RX adaptation completion/status bits.

Persistence is hardware-defined. Control fields typically remain until changed by link training, modeset, PHY bring-up/tear-down, power-management transitions, suspend/resume, or GPU reset. Status and acknowledgement fields may be read-only, sticky, self-clearing, latched, or valid only while the relevant PHY lane, PLL, or clock domain is powered. The header does not encode access permissions or side effects.

## Dependencies And Integration Points

The direct dependency is the C preprocessor and AMD's generated register-header convention. Correct use requires synchronization with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` for the DCN 4.1 register offsets used by display/DMUB code.
- DPCS offset headers, which contain the detailed `ixDPCSSYS_CR1_SUPX_*` and `ixDPCSSYS_CR1_LANEX_*` indirect-register addresses corresponding to these field layouts.
- AMD's authoritative DCN 4.1.0 register database, because these macros are silicon ABI metadata.
- DCN401 and DMUB register-table construction, where mask and shift arrays are populated from generated `FD_MASK`/`FD_SHIFT` expansions.

Integration points are low-level display PHY and link-management paths: DisplayPort/HDMI PHY bring-up, PLL programming, spread-spectrum clock setup, transmitter electrical parameter programming, receiver calibration/adaptation, CDR/DPLL lock handling, lane power transitions, DCC calibration, loopback/BERT diagnostics, and reset/power sequencing. A mismatch between this header and the matching offsets or silicon version can make register helpers read or update the wrong field while still compiling successfully.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly but write adjacent hardware fields, misdecode status, or leave a PHY sequence waiting on the wrong bit.
- The file is generated. Manual edits risk divergence from the register database, the matching offset headers, firmware assumptions, and the hardware specification.
- The chunk boundaries are not semantic. It starts in the tail of `DPCSSYS_CR1_SUPX_DIG_SUP_OVRD_OUT` and ends immediately before the fields for `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_DAC_CTRL_SEL_3`.
- Many fields are power, reset, calibration, PLL, CDR, and adaptation controls. Misprogramming them can cause link bring-up failures, unstable clocks, failed CDR lock, excessive bit errors, black screens, intermittent hotplug/link-training failures, or bad behavior only after suspend/resume or retraining.
- Status and acknowledgement fields are timing-sensitive. Reading while a lane or shared PHY block is powered down, clock-gated, or mid-transition may produce stale or transient values; writing reserved or status-adjacent fields can have hardware-specific side effects.
- Repeated MPLL A/B and TX/RX lane patterns make copy/paste or token-paste mistakes difficult to spot. The wrong instance can still compile if a similarly named register exists.
- The masks include many reserved fields. Register update helpers must preserve reserved bits unless the hardware programming guide explicitly says otherwise.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware/display behavior:

- Build DCN401/DMUB AMDGPU display code with `dcn_4_1_0_offset.h` and this shift/mask header together. Missing or renamed symbols should fail at compile time in generated field-list expansion or register-helper use sites.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0 register source, treating the first and last registers as partial chunk boundaries.
- Run static checks that every complete register block has matching `__SHIFT` and `_MASK` entries, masks align with shifts, and reserved fields cover the expected remaining bits.
- Cross-check `DPCSSYS_CR1_SUPX_*` and `DPCSSYS_CR1_LANEX_*` field layouts against the matching DPCS indirect offsets to ensure names, instances, and register widths agree.
- Exercise DisplayPort and HDMI link bring-up across supported link rates, lane counts, spread-spectrum settings, suspend/resume, hotplug, and GPU reset. Watch for PLL lock timeouts, CDR lock failures, bad DPLL bounds, link-training retries, or black-screen regressions.
- Validate PHY power sequencing and lane power states with runtime diagnostics where available. Signals include stable power-state transitions, expected RTUNE acknowledgements, expected DCC calibration acknowledgements, no stuck reset bits, and no unexpected LBERT/error counters.
- Stress receiver adaptation-sensitive cases: marginal cables, high link rates, retraining, low-power entry/exit, and multi-monitor configurations. Look for CTLE/VGA/DFE adaptation completion, stable slicer/VDAC settings, and absence of intermittent bit errors.

## Cross-Chunk Notes

The previous chunk contains the start of `DPCSSYS_CR1_SUPX_DIG_SUP_OVRD_OUT`, including the shift fields and early masks whose final three masks appear at this chunk's start. The next chunk starts with the fields for `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_DAC_CTRL_SEL_3` and continues later RX adaptation, RX status-load, analog lane, and ATB/VDAC/VREG field definitions. The final per-file research document should merge adjacent chunks before making whole-file claims about all DPCSSYS CR1 definitions or all DCN 4.1.0 shift/mask coverage.
