# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 41335-43782

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice. It contains C preprocessor constants for register-field bit positions and masks; it does not contain executable driver logic. AMDGPU display code consumes these constants with companion DPCS register-offset headers and register helpers to program or decode low-level Display Core PHY, PCS/PMA, PLL, power, calibration, interrupt, and debug fields without embedding numeric bit layouts in C code.

The requested range contains 2,448 lines, 2,156 `#define` statements, 1,229 `__SHIFT` macros, 927 `_MASK` macros, and 289 register comment boundaries. It starts in the middle of `DPCSSYS_CR1_LANEX_ANA_TX_PWR_OVRD`, covers CR1 generic lane analog TX/RX fields, CR1 raw-lane PCS/PMA/FSM/IRQ/control fields, and a large CR2 supervisor block for ref clocks, MPLLA/MPLLB overrides, SSC, analog supervisor registers, MPLL power/control/timer/calibration fields, RTUNE, and digital-to-analog PLL override outputs. It ends after the complete `DPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_2` definition.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, memory allocations, locks, direct MMIO operations, or exported symbols in this range. The interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field in the register value.
- `//DPCSSYS_*` comments: generated register-group boundaries that correspond to offset/index definitions in companion DPCS 4.2.3 headers.

The main macro groups in this chunk are:

- `DPCSSYS_CR1_LANEX_ANA_TX_*`: generic-lane analog TX power override, alternate bus, analog test bus selection, DCC DAC/control, termination code/control, clock override, miscellaneous TX tuning, and reserved/NC fields.
- `DPCSSYS_CR1_LANEX_ANA_RX_*`: generic-lane analog RX clock, CDR/deserializer, slicer, power, squelch, calibration, ATB measurement, forced analog-test values, and reserved fields.
- `DPCSSYS_CR1_RAWLANEX_DIG_PCS_XF_*`: PCS crossing override, input, output, adaptation, equalization, lane-number, ATE, PH2 calibration, TX/RX termination, loopback, request/ack, pstate, rate, width, data-enable, reset, and training/status mirrors for a raw lane.
- `DPCSSYS_CR1_RAWLANEX_DIG_FSM_*`: finite-state-machine override and monitor fields, fast-path RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration controls, TX common-mode/RX-detect controls, continuous calibration/adaptation controls, CR-lock, DCC status, OCLA, TX EQ update, common calibration status, and RX IQ phase offset fields.
- `DPCSSYS_CR1_RAWLANEX_DIG_IRQ_CTL_*`: RX/TX reset, request, rate, pstate, adaptation, PH2 calibration, lane mode, serial loopback, DCC on-demand, clear, mask, and return-request interrupt fields.
- `DPCSSYS_CR1_RAWLANEX_DIG_PMA_XF_*`: PMA-side lane/supervisor/TX/RX/MPHY override and PMA input/output mirrors, RTUNE control, and RX adaptation override outputs.
- `DPCSSYS_CR1_RAWLANEX_DIG_TX_CTL_*` and `DPCSSYS_CR1_RAWLANEX_DIG_RX_CTL_*`: TX/RX FSM and clock control, DCC continuous status, loss-of-signal masking, data-enable override, offset-cancel/adaptation continuous status, and OCLA/UPCS debug fields.
- `DPCSSYS_CR2_SUP_DIG_*`: supervisor digital controls for ID code, refclk, MPLLA/MPLLB div/HDMI clocks, PLL override inputs, spread-spectrum peak/stepsize, charge-pump controls, supervisor/prescaler/lane-level overrides, debug, ASIC input mirrors, bandgap and CP input mirrors, MPLL power-control status/timers/calibration/analog DAC output, bandgap/ref power-up timing, RTUNE debug/config/status/set/stat values, and digital PLL override outputs.
- `DPCSSYS_CR2_SUP_ANA_*`: supervisor analog prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB misc/override/ATB/control/reserved fields.

Common field-name patterns encode the intended hardware semantics: `OVRD`, `OVRD_EN`, `ASIC_IN`, `PMA_IN`, `PCS_IN`, `PCS_OUT`, `PMA_OUT`, `REQ`, `ACK`, `IRQ`, `IRQ_CLR`, `MASK`, `PSTATE`, `RATE`, `WIDTH`, `RESET`, `DATA_EN`, `CAL`, `ADAPT`, `DFE`, `AFE`, `CDR`, `PH2`, `MPLL`, `SSC`, `RTUNE`, `OCLA`, `ATB`, `LB`, `TERM`, and `RESERVED`/`NC`.

## Control Flow

This header has no runtime control flow. It contributes to display-driver behavior at compile time:

1. A consumer selects a DPCS 4.2.3 register offset or indirect index from the matching generated offset header.
2. The consumer uses this shift/mask header to clear, insert, read, or test specific bit fields.
3. AMDGPU register helpers perform MMIO or indexed DPCS CR read/modify/write, polling, or decode operations.
4. Hardware and firmware state machines perform the actual sequencing for PHY bring-up, lane reset, PLL programming, calibration, adaptation, interrupt handling, and debug flows.

The sequencing implied by these fields lives outside this file. Examples include forcing or releasing TX/RX overrides, programming raw-lane PCS/PMA request and status paths, acknowledging adaptation or calibration events, masking or clearing lane IRQs, managing MPLLA/MPLLB clock enables and resets, setting SSC parameters, waiting for MPLL lock/timer status, and reading RTUNE or analog status.

## State And Persistence Behavior

The macros are stateless compile-time constants. They define the shape of hardware-visible state, but the register values themselves live in DPCS hardware and can be volatile, latched, self-clearing, write-one-to-clear, read-only, or retained depending on the register and access path.

Hardware state named by this chunk includes:

- CR1 generic-lane analog TX/RX state for power overrides, clock enables, loopback, DCC, termination, slicer, squelch, calibration, analog-test-bus measurement, and reserved analog storage.
- CR1 raw-lane PCS/PMA state for TX/RX requests, resets, pstate/rate/width, data-enable, RX adaptation, RX equalization, lane mode, loopback, ATE, PH2 calibration, termination, and request/ack/status mirrors.
- CR1 raw-lane FSM/debug state for fast startup, calibration/adaptation phases, continuous calibration/adaptation, DCC status, CR lock, common calibration status, OCLA, and IQ phase offset.
- CR1 raw-lane interrupt state for reset/request/rate/pstate/adaptation/PH2/lane-mode/loopback/DCC/TX events, including clear and mask registers.
- CR2 supervisor clock/PLL state for ref clocks, MPLLA/MPLLB override inputs, ASIC input mirrors, div/HDMI clocks, spread-spectrum configuration, charge-pump settings, MPLL power status, timers, calibration, analog DAC output, and digital-to-analog override outputs.
- CR2 supervisor analog and calibration state for prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB ATB/control/misc/override, RTUNE set/stat values, and TX/RX termination tuning.

Persistence is hardware-defined. Values may be reset by modeset/link reconfiguration, HPD retraining, suspend/resume, GPU reset, display-engine reset, power-gating, firmware ownership changes, or PHY state-machine transitions. The header does not define reset values, legal enumerations, ownership rules, access widths, polling timeouts, or ordering requirements.

## Dependencies And Integration Points

This generated header must stay synchronized with the DPCS 4.2.3 hardware register database, the matching DPCS 4.2.3 offset header, and AMDGPU Display Core register tables that token-paste register, field, mask, and shift names.

Integration points include:

- Companion generated headers under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`, especially DPCS 4.2.3 register offsets and adjacent chunks of this same shift/mask file.
- AMDGPU display resource/link/PHY/encoder code that configures DisplayPort/HDMI lane operation, link training, PHY power sequencing, PLL setup, and ASIC-specific register tables.
- DPCS CR access helpers that perform read/modify/write and polling using generated offsets plus these shift/mask macros.
- Hardware/firmware lane and supervisor state machines that own PCS/PMA handshakes, calibration/adaptation, MPLLA/MPLLB operation, spread-spectrum behavior, RTUNE, bandgap, and interrupt/status handling.
- Diagnostic and validation flows for ATE, OCLA, ATB measurement, raw-lane status, RX adaptation status, DCC status, IRQ observation, and PLL/RTUNE readback.

The range crosses major hardware domains. It begins in CR1 generic-lane analog TX/RX definitions, moves into CR1 raw-lane PCS/PMA/FSM/IRQ/control definitions, and then enters CR2 supervisor digital/analog PLL and calibration definitions. A final merged per-file report should preserve those boundaries rather than treating all macros as one flat lane block.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while silently programming the wrong PHY bit.
- The file is generated. Manual edits risk diverging from AMD's source register database, silicon documentation, firmware expectations, and companion offset headers.
- The first line starts after the `DPCSSYS_CR1_LANEX_ANA_TX_PWR_OVRD` register comment and its first fields; the previous chunk is needed for the complete register context.
- Many one-bit fields have only `__SHIFT` definitions in this generated style, while wider or reserved fields often also have `_MASK` definitions. Consumers must follow existing helper conventions and not assume every shift has a nearby explicit mask.
- Override-enable and override-value fields are easy to confuse. Misprogramming them can force clocks, resets, pstate/rate/width, data-enable, loopback, RX adaptation, PH2 calibration, termination, MPLL control, SSC, RTUNE, or analog controls away from hardware/firmware ownership.
- IRQ, clear, mask, request, ack, done, and status fields are sequencing-sensitive. Bad definitions can cause missed events, false readiness, repeated interrupts, stuck clears, link-training timeouts, or failures during suspend/resume and hotplug recovery.
- PLL, SSC, charge-pump, bandgap, RTUNE, DCC, termination, RX equalization, slicer, squelch, and analog-test fields are silicon- and board-sensitive. Errors may appear only at specific link rates, voltage/temperature corners, cable/sink combinations, or after repeated retraining.
- Reserved and `NC` fields occur throughout the chunk. Driver code should preserve them or leave them untouched unless authoritative programming documentation for the target ASIC stepping says otherwise.
- Repetitive names across DPCS generations and lanes can hide copy/paste mistakes. Using a DPCS 4.2.3 mask with a neighboring generation's offset, or mixing CR1 raw-lane and CR2 supervisor names, may compile but target the wrong hardware semantics.

## Test Signals

Useful validation for this generated header and its consumers includes:

- Build AMDGPU display configurations that include DPCS 4.2.3 support; missing or renamed macros should break generated register-table compilation.
- Mechanically compare this range against the authoritative DPCS 4.2.3 register database and check that complete fields have expected shifts/masks within the intended register width.
- Cross-check every complete register group in this chunk against the matching DPCS 4.2.3 offset header.
- Diff repeated PCS/PMA/FSM/IRQ, MPLLA/MPLLB, and analog-control families against neighboring DPCS-generation headers to catch generator drift while allowing intentional generation differences.
- Exercise DisplayPort/HDMI boot display, hotplug, modeset, link-rate changes, lane-count changes, blank/unblank, suspend/resume, and GPU reset on hardware using this DPCS generation.
- Monitor logs and register dumps for link-training failures, request/ack timeouts, stuck reset/data-enable/clock overrides, repeated or missing lane IRQs, RX adaptation/PH2 calibration failures, DCC status anomalies, PLL lock failures, SSC misconfiguration, RTUNE failures, unstable signal detect, and analog calibration drift.
- Decode known-good register dumps with these masks and compare against hardware documentation or reference tools for raw-lane PCS/PMA status, IRQ state, fast calibration/adaptation controls, MPLLA/MPLLB override/status/timer/calibration fields, RTUNE values, and analog ATB/bandgap/termination fields.
- Treat ATE, OCLA, ATB, forced analog, PLL override, and raw-lane debug paths as controlled diagnostics. They can bypass normal PHY control and should be validated with hardware-aware procedures.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR1_LANEX_ANA_TX_PWR_OVRD`, including the register comment and early shift definitions for `OVRD_TX_LOOPBACK`, `LOOPBACK_EN_REG`, `REFGEN_EN_REG`, `CLK_DIV_EN_REG`, `DATA_EN_REG_INT`, and `CLK_EN_REG`. This chunk resumes at `SERIAL_EN_REG` and completes that register before continuing through CR1 generic-lane analog RX, raw-lane PCS/PMA/FSM/IRQ/control, and CR2 supervisor definitions.

This chunk ends cleanly at the complete `DPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_2` register definition. The next chunk should start with the following register group, so merge/reconciliation only needs to stitch the split first register for this range.
