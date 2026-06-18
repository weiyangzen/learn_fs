# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 42956-45337

## Scope

This chunk covers lines 42956-45337 of the generated AMD DPCS 4.2.0 shift/mask header. It contains 2,131 `#define` entries: 1,065 `__SHIFT` macros and 1,086 `_MASK` macros, plus 249 register-block comments. The count imbalance is expected for this sliced range: it starts in the middle of `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1`, so some masks appear for fields whose shift definitions are above line 42956, and it ends after only the first shift for `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`.

The content is declarative only. It defines preprocessor constants for bit positions and masks in DPCS/RDPCS transmitter CR registers. There are no C functions, structs, enums, local variables, branches, loops, or runtime allocations in this range.

## Purpose

The header gives AMDGPU display code symbolic bitfield locations for programming ASIC display PHY and controller registers. Consumer code combines the `__SHIFT` and `_MASK` constants with memory-mapped register read/modify/write helpers, avoiding hard-coded bit numbers in link, PHY, clock, calibration, interrupt, and diagnostics paths.

This chunk covers the latter part of the `DPCSSYS_CR1` lane/RAWLANEX CR surface and the beginning of the `DPCSSYS_CR2` support CR surface:

- CR1 lane analog TX/RX controls: signal detect, DCC DAC calibration, TX power/clock/termination, analog test bus, RX CDR/SLC/power/squelch/calibration, and measurement muxes.
- CR1 RAWLANEX PCS/PMA crossbar fields: TX/RX override inputs, PCS/PMA input/output status, adaptation status, equalization controls, lane numbering, ATE controls, MPHY override, and lane RTUNE controls.
- CR1 lane FSM, interrupt, TX control, and RX control fields: fast calibration/adaptation/status monitors, CR lock, DCC flags/status, OCLA controls, IRQ status/clear/mask fields, and TX/RX FSM override knobs.
- CR2 support digital fields after the `addressBlock: dpcssys_cr2_rdpcstxcrind` marker: IDCODE, refclock overrides, MPLLA/MPLLB clock and PLL programming overrides, SSC peak/stepsize fields, supervisor overrides, prescaler, level, ASIC input mirrors, bandgap, and charge-pump fields.
- CR2 support analog fields: prescaler, RTUNE, bandgap, switch-power measurement, MPLLA controls, and the first MPLLB analog controls through the opening of `MPLLB_ATB3`.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace. Important families in this slice include:

- `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_*`: high-frequency and low-frequency signal-detect thresholds, filter enable, calibration tune, calibration enable, and per-field override-enable bits.
- `DPCSSYS_CR1_LANEX_DIG_ANA_TX_DCC_DAC_OVRD_OUT*` and `DPCSSYS_CR1_LANEX_ANA_TX_DCC_*`: TX duty-cycle-correction DAC range, comparator, control select, clock compensation, raw DAC register, and override gates.
- `DPCSSYS_CR1_LANEX_ANA_TX_*`: TX measurement override, power override, alternate bus, ATB measurement points, termination code/update/reset controls, MPLLA/MPLLB clock selection, LFPS/RXDET/boost/mode options, and reserved analog tuning registers.
- `DPCSSYS_CR1_LANEX_ANA_RX_*`: RX clock, CDR/deserializer, slicer control, RX power, squelch, calibration, ATB reference/measurement/force, and reserved RX analog fields.
- `DPCSSYS_CR1_RAWLANEX_DIG_PCS_XF_*`: PCS TX/RX override and PCS in/out fields, RX adaptation acknowledgement and figure-of-merit, transmitter pre/main/post cursor direction requests, lane number, ATE, RX equalization override, PH2 calibration, and TX/RX termination controls.
- `DPCSSYS_CR1_RAWLANEX_DIG_FSM_*`: FSM override control, memory address/status monitors, fast startup/adaptation/calibration phase controls, continuous calibration/adaptation states, flags, CR lock, TX DCC state, OCLA, CMNCAL status, and IQ phase offset.
- `DPCSSYS_CR1_RAWLANEX_DIG_IRQ_CTL_*`: RX/TX reset/request/rate/pstate/adaptation/PH2/loopback/DCC interrupt status, clear, and mask fields.
- `DPCSSYS_CR1_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*`: PMA lane/supervisor/TX/RX override fields, PMA input mirrors, RTUNE, MPHY, TX/RX FSM control, clock control, continuous status, loss-of-signal masking, data-enable override, and OCLA taps.
- `DPCSSYS_CR2_SUP_DIG_*`: CR2 support ID, refclock, MPLLA/MPLLB div/HDMI clock override, PLL override input groups, SSC peak/step-size fields, charge-pump override fields, supervisor/prescaler/level overrides, ASIC input mirrors, bandgap, and CP/CP_GS mirrors.
- `DPCSSYS_CR2_SUP_ANA_*`: CR2 prescaler and RTUNE analog controls, bandgap trims/overrides, power-measure switches, MPLLA/MPLLB misc and override controls, ATB measurement muxes, PLL control words, and reserved PLL/DLL bypass/tuning fields.

## Register Areas Covered

The CR1 lane analog area is centered on per-lane PHY bring-up and measurement. TX-side fields expose fast-start, loopback, AC JTAG, clock loopback, power gate enables, serial/data/refgen/clock enables, alternate bus routing, termination code programming, DCC calibration, MPLLA/MPLLB clock enable selection, LFPS behavior, RX detect override, vreg boost, and analog test-bus selectors. RX-side fields expose clock source/rate/divider selection, CDR/deserializer options, slicer control, RX power enables, squelch threshold/filter/calibration, reference controls, measurement muxes, forced analog test-bus values, and calibration-ready/status fields.

The CR1 RAWLANEX PCS/PMA area is a digital bridge between the PHY analog block and the PCS/PMA control plane. It defines override inputs, output mirrors, PCS input mirrors, RX adaptation controls, adaptation acknowledgements, figure-of-merit readback, TX pre/main/post cursor direction feedback, lane number programming/readback, equalization override fields, phase-2 calibration controls, ATE paths, and TX/RX termination controls. PMA fields mirror lane/supervisor/TX/RX control and status across override and ASIC-input style registers.

The CR1 FSM and IRQ area describes hardware state machines and event signaling. Fast calibration fields name startup, RX adaptation, AFE/DFE calibration, bypass calibration, reference-level calibration, IQ calibration, supervisor setup, TX common-mode, TX RXDET, RX power-up, VCO wait/calibration, and continuous calibration/adaptation/data/phase/AFE phases. Status fields include flags, lock state, TX DCC flags/status, CMNCAL MPLL/RCAL status, and RX IQ phase offset. IRQ fields are organized as status, clear, and mask registers for RX reset/request/rate/pstate/adaptation disable/request, lane transceiver mode, RX PH2 calibration request/disable, RX-to-TX serial loopback enable, DCC on-demand, and TX reset/request.

The CR2 support digital area begins a new address block. It covers shared/supervisory state rather than one CR1 lane: ID code, reference clock override, MPLLA/MPLLB divider and HDMI clock override, PLL override input bundles, SSC peak and step-size programming, charge-pump controls, supervisor override output, prescaler override, level override, and ASIC-input mirrors for MPLL, clocks, supervisor, level, bandgap, and charge-pump signals.

The CR2 support analog area exposes global support circuits: prescaler enable/division/source, RTUNE override/request/reference selection, bandgap trims and bypasses, switch-power measurement controls, and two parallel MPLL analog control surfaces. MPLLA is fully represented in this chunk from misc/override/ATB through control and reserved registers. MPLLB starts with misc, override, ATB1, ATB2, and the first `meas_iv_bias` shift of ATB3 before the chunk boundary.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior is created by AMDGPU display code that includes the header and writes the corresponding hardware registers.

The field names imply several hardware state machines and handshakes:

- PHY bring-up and clocking: enable/reset, reference-clock override, MPLLA/MPLLB clock enable, word-clock enable, prescaler, and clock input/status mirrors must be sequenced around link training and resume.
- TX analog calibration: DCC DAC range/control/select, DCC comparator, termination update/reset/code override, TX RXDET, LFPS, loopback, fast-start, and analog power bits influence transmitter electrical behavior.
- RX analog calibration and adaptation: signal-detect thresholds/filters/calibration, CDR/deserializer, slicer control, RX power, squelch, reference-level, IQ, AFE, DFE, and continuous adaptation fields reflect calibration phases and status.
- PCS/PMA override paths: many `OVRD_IN`, `OVRD_OUT`, `PCS_IN`, `PCS_OUT`, `PMA_IN`, and `ASIC_IN` groups separate software-forced values from hardware or firmware-generated values. Consumers must preserve the override-enable/value pairing.
- Interrupt handling: status/clear/mask triads expose latch-and-clear behavior for reset/request/rate/pstate/adaptation/PH2/loopback/DCC/TX events.
- PLL and support-circuit programming: CR2 MPLLA/MPLLB override, SSC, charge-pump, bandgap, RTUNE, and prescaler fields feed global link-clock generation and calibration.
- Diagnostics and factory paths: ATB, OCLA, ATE, JTAG, memory/status monitor, FOM, and raw reserved windows are intended for bring-up, validation, or low-level debug rather than normal high-level policy.

No software persistence is implemented here. Hardware register contents persist or reset according to ASIC power/reset domains. Fields named `RESERVED`, `SPARE`, `MEM_ADDR_MON`, status monitors, ATB selectors, and lock/status flags expose hardware storage or readback semantics, but this chunk does not define policy for saving/restoring them.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. These macros are normally paired with the generated DPCS 4.2.0 address/header files that define register offsets, and with AMDGPU/DC helper macros that compose field values from mask and shift constants.

Integration points visible from the naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC link encoder, DPCS/RDPCS PHY, DisplayPort, HDMI, clock, and PHY calibration paths.
- Register access helpers that use generated field names to perform read-modify-write operations against DPCS CR indirect registers.
- DisplayPort lane training and equalization code, reflected by TX pre/main/post cursor direction, RX EQ override, adaptation acknowledgement, FOM, RX rate/pstate, and per-lane PCS/PMA control fields.
- PHY analog bring-up and diagnostic code, reflected by ATB, ATE, OCLA, JTAG, DCC, RXDET, LFPS, RTUNE, bandgap, prescaler, and MPLL fields.
- Firmware or hardware state-machine coordination paths, reflected by `ASIC_IN`, `OVRD_IN`, `OVRD_OUT`, FSM status, IRQ mask/clear/status, and support-block override input/output fields.
- Generated register database tooling: this file should be treated as generated hardware metadata rather than a hand-authored algorithmic module.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently write adjacent hardware bits during read-modify-write sequences.
- This range has dense parallel namespaces: CR1 lane analog, CR1 RAWLANEX PCS/PMA/FSM/IRQ/TX/RX control, and CR2 support digital/analog. Prefix mistakes can cause code to use a field from the wrong instance or address block while still compiling.
- Many registers combine value fields with adjacent override-enable bits. Setting the value without the override enable, or leaving an override enable asserted accidentally, can produce hard-to-debug PHY behavior.
- Status, clear, and mask registers are adjacent in the IRQ namespace. Treating a clear bit like persistent state, or writing a status mirror as if it were control, can drop interrupts or leave stale latches.
- RX/TX analog controls, PLL charge-pump/SSC settings, bandgap, RTUNE, and reserved PLL/DLL fields can affect signal integrity and link stability. Consumer changes need hardware-spec validation, not just compile coverage.
- The chunk boundaries are partial. The beginning omits some `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1` shifts, and the end omits most of `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3`; merge tooling must combine adjacent chunks before deriving complete per-register counts.
- Full-width or reserved bit windows may be present in adjacent source regions. Consumers should preserve documented reset values and avoid treating reserved fields as general-purpose storage.

## Test Signals

Useful validation signals are build-time, generation-time, and hardware-integration oriented:

- Preprocess/compile AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static generated-header checks that every complete register block has matching `__SHIFT` and `_MASK` definitions and that masks correspond to width and shift. For this sliced chunk, the expected local count is 1,065 shifts and 1,086 masks because of partial boundaries.
- Diff or schema validation against the authoritative DPCS 4.2.0 register database, especially around CR1 RAWLANEX and CR2 support address-block boundaries.
- Grep/compile checks for consumers of `DPCSSYS_CR1_LANEX_ANA_TX`, `DPCSSYS_CR1_LANEX_ANA_RX`, `DPCSSYS_CR1_RAWLANEX_DIG_PCS_XF`, `DPCSSYS_CR1_RAWLANEX_DIG_FSM`, `DPCSSYS_CR1_RAWLANEX_DIG_IRQ_CTL`, `DPCSSYS_CR1_RAWLANEX_DIG_PMA_XF`, and `DPCSSYS_CR2_SUP_*` macros.
- Runtime display tests on ASICs using DPCS 4.2.0: DP and HDMI link training, hotplug, suspend/resume, link-rate changes, lane equalization/adaptation, RX/TX reset recovery, and interrupt clear/mask behavior.
- PHY bring-up readback for reset, clock enable/status, lane adaptation acknowledgement, FOM, CR lock, DCC status, CMNCAL MPLL/RCAL status, RX IQ phase offset, RTUNE, bandgap, prescaler, and MPLL override/status fields.
- Diagnostic coverage for ATB/OCLA/ATE paths when hardware validation or manufacturing flows depend on these fields.

## Chunk Notes For Merge

This document intentionally covers only lines 42956-45337 of `dpcs_4_2_0_sh_mask.h`. The previous chunk should provide the omitted start of `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1`, and the following chunk should complete `DPCSSYS_CR2_SUP_ANA_MPLLB_ATB3` and subsequent CR2 support fields. The later per-file merge should describe this source as a generated ASIC bitfield map, not handwritten driver logic, and should preserve the distinction between CR1 per-lane/RAWLANEX controls and CR2 support-block controls.
