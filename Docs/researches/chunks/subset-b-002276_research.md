# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 41437-43854

## Scope

This chunk is a middle slice of the generated AMD DPCS 3.1.4 register shift/mask header. It covers lines 41437 through 43854 inside the `dpcssys_cr2_rdpcstxcrind` address block. The range contains 2,145 `#define` constants across 273 register comment blocks: 1,070 `__SHIFT` definitions and 1,075 `_MASK` definitions. The five extra masks are the tail of `DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_MPHY_OVRD_OUT`, whose matching shifts and first masks are immediately before the chunk. The final line is the comment for `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN_1`; that register's fields begin after the chunk.

The content is declarative only. It has no functions, structs, storage, branches, or local side effects. Its API surface is preprocessor constants used by AMDGPU display code to compose and decode 16-bit DPCS/PHY control-register fields.

## Purpose

The header gives display-driver code symbolic bitfield locations for DPCS CR2 raw-lane digital PCS, PMA, FSM, interrupt, TX control, and RX control registers. This chunk mainly completes raw lane 0 control definitions, then provides large repeated raw lane 1 and raw lane 2 field maps, and starts raw lane 3 PCS TX override coverage.

The fields describe low-level Display PHY behavior: lane reset/request handshakes, link rate and lane width, power state, low-power detect, PLL and master PLL selection, TX/RX data enables, loopback enables, receiver adaptation/calibration state, DFE/AFE/IQ calibration controls, interrupt status and clear bits, termination and equalization overrides, PMA/PWM/MPHY controls, and OCLA/UPCS observation controls.

## Exported API Surface

There are no C-callable APIs or types. The exported interface is macro naming of this form:

- `DPCSSYS_CR2_RAWLANE<N>_<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `DPCSSYS_CR2_RAWLANE<N>_<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Important register families in this chunk:

- `DPCSSYS_CR2_RAWLANE0_DIG_*`: tail coverage for lane 0 PMA MPHY output masks, RX adaptation override output, TX/RX control, ATE RX/TX overrides, master MPLL loop enables, RX validity override, and TX data/async-data override fields.
- `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_*` and `DPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_*`: parallel PCS transfer interface definitions for TX override/input/output status, RX override/input/output status, RX adaptation acknowledgement and figure-of-merit fields, directed TX pre/main/post cursor values, lane numbering, ATE override, RX equalization and delta-IQ controls, termination controls, phase-2 calibration, and secondary RX/TX override registers.
- `DPCSSYS_CR2_RAWLANE1_DIG_FSM_*` and `DPCSSYS_CR2_RAWLANE2_DIG_FSM_*`: FSM override, status, monitor, fast-state, calibration/adaptation, lock, DCC, OCLA, TX EQ update, RCAL status, and RX IQ phase offset fields.
- `DPCSSYS_CR2_RAWLANE1_DIG_IRQ_CTL_*` and `DPCSSYS_CR2_RAWLANE2_DIG_IRQ_CTL_*`: lane-local interrupt status, clear, and mask fields for RX/TX reset and request events, RX rate and pstate changes, adaptation request/disable, lane transceiver mode, phase-2 calibration, loopback, DCC on-demand, and TX request events.
- `DPCSSYS_CR2_RAWLANE1_DIG_PMA_XF_*` and `DPCSSYS_CR2_RAWLANE2_DIG_PMA_XF_*`: PMA lane/supervisor/TX/RX override and input fields, RTUNE controls, MPHY controls, and RX adaptation override output fields.
- `DPCSSYS_CR2_RAWLANE1_DIG_TX_CTL_*`, `DPCSSYS_CR2_RAWLANE2_DIG_TX_CTL_*`, `DPCSSYS_CR2_RAWLANE1_DIG_RX_CTL_*`, and `DPCSSYS_CR2_RAWLANE2_DIG_RX_CTL_*`: lane TX/RX control FSM, clock, loss-of-signal mask, data-enable override counters, continuous DCC/off-cancellation/adaptation status, and OCLA/UPCS observation fields.
- `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN`: first lane 3 PCS TX override register, covering pstate, low-power detect, width, rate, MPLLB selection, MPLL enable, override enable, master MPLL states, and TX async enable override.

The lane 1 and lane 2 blocks are intentionally near-identical. Their shifts and masks encode the same per-lane hardware semantics with only the `RAWLANE1` versus `RAWLANE2` instance prefix changed.

## Register Areas Covered

PCS transfer-interface registers define the interface between lane PCS control logic and PHY-facing TX/RX signals. TX-side fields include pstate, low-power detect, width, rate, reset/request, DETRX request, VBOOST, IBOOST, TX beacon, async enable/data, loopback, TX data enable, and MPLL state/selection. RX-side fields include reset/request, rate, width, pstate, loss-of-signal threshold and LFPS handling, adaptation requests, continuous adaptation/off-cancellation, RX validity, RX data enable, RX2TX loopback, and several RX status/input mirrors.

RX adaptation and equalization registers expose training/control details: RX adaptation acknowledgement bits, adaptation done status, figure of merit, directed transmitter pre/main/post cursor values, RX EQ delta-IQ override values, coefficient override enables, AFE/DFE/IQ calibration entry points, VCO/reference load override values, and phase-2 calibration controls.

FSM registers expose micro-state controls and monitors for startup calibration, RX adaptation, AFE/DFE/bypass/reference-level/IQ calibration, supervisor and TX common-mode flows, RX detect, power-up, VCO wait/calibration, continuous calibration/adaptation, CR lock, TX DCC flags/status, OCLA, TX EQ update flags, RCAL status, and RX IQ phase offset. These are not executable state machines in this header; the macros describe the register fields used to observe or override hardware FSM behavior.

Interrupt-control registers define both status and write-clear/mask fields. Covered events include RX reset, RX request, RX rate, RX pstate, RX adaptation request/disable, lane transceiver mode, RX phase-2 calibration request/disable, lane RX2TX serial loopback, DCC on-demand, TX reset, and TX request. The `_CLR` and `_MASK` registers share similar event names but have different runtime semantics in consumers.

PMA transfer-interface registers define lane/PMA-side override and input/status bits: TX/RX data enable, resets, request/ack, pstate, rates and widths, PLL/MPLL enable and state, DETRX, VBOOST/IBOOST, termination control, TX common-mode, LFPS and loss-of-signal status, RTUNE request/ack, MPHY PWM controls, RX PWM/async controls, and RX PMA IQ phase adjustment override.

TX/RX control registers define lane-local controller behavior: TX wait time for MPLL off, which power states allow RX detection, TX clock enable/select and async beacon wait timing, DCC continuous status, OCLA FSM/data/clock enables, RX control FSM enable and rate-change behavior, RX loss-of-signal mask counters, RX data-enable override/reference tracking counters, and continuous off-cancellation/adaptation enable status.

## Control Flow And State Behavior

This chunk has no software control flow. Runtime control flow is in consumer code that includes this header and uses these constants with register read/modify/write helpers.

The bitfields nevertheless model several hardware control paths:

- Link and lane bring-up: reset/request/ack, pstate, rate, width, low-power detect, TX/RX data enable, and clock enable fields must be sequenced by the display link-management code.
- PLL and clocking: MPLLA/MPLLB state, MPLLB selection, MPLL enable, master MPLL override, TX clock selection, and VCO/reference load override fields participate in link-rate and PHY-clock configuration.
- RX training and adaptation: adaptation request/ack, continuous adaptation, off-cancellation, AFE/DFE/IQ calibration, phase-2 calibration, EQ override, and figure-of-merit fields expose training state and manual override hooks.
- Interrupt handling: status, clear, and mask registers require consumers to distinguish readable event state from write-one-to-clear and interrupt-mask semantics.
- Debug and observation: FSM monitors, fast-state registers, OCLA/UPCS enable bits, CR lock, DCC status, and IQ phase offset fields are intended for diagnostics, hardware validation, or tightly controlled bring-up flows.

No persistence is implemented in software. Register values persist only according to ASIC register reset and power domains. Some fields are status-only mirrors, some are writable controls, and some are override-enable/value pairs; the header itself does not encode access permissions.

## Dependencies And Integration Points

This file depends only on the C preprocessor, but it is meant to be included with companion generated DPCS 3.1.4 register address headers. Address headers select the register offset; this shift/mask header supplies field encodings.

Integration points include:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially display core and PHY/link-training paths that program DPCS CR registers.
- Common AMD register helper macros that combine masks and shifts for read/modify/write operations.
- DisplayPort/USB-C alternate-mode and HDMI-related PHY programming paths, inferred from field names such as `RATE`, `WIDTH`, `PSTATE`, `MPLL`, `DETRX`, `VBOOST`, `IBOOST`, `LFPS`, and lane loopback controls.
- Hardware diagnostics, bring-up, and validation tooling that reads FSM, interrupt, OCLA, DCC, calibration, and adaptation status fields.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask can corrupt adjacent hardware fields during read/modify/write, particularly because most registers are dense 16-bit bitfields.
- Chunk boundaries split register definitions. This range starts after the shifts for `RAWLANE0_DIG_PMA_XF_MPHY_OVRD_OUT` and ends at the comment before `RAWLANE3_DIG_PCS_XF_TX_OVRD_IN_1`; merge tooling must reconcile adjacent chunks to avoid treating these as complete per-register summaries.
- Lane copy/paste errors are high impact. Raw lane 1 and raw lane 2 should remain parallel; a mismatched lane prefix or field mask can route programming to the wrong lane or decode status incorrectly.
- Status, clear, and mask registers share event vocabulary. Consumers must not treat `_IRQ`, `_IRQ_CLR`, and `IRQ_MASK` fields as interchangeable.
- Override value and override enable fields are paired throughout the chunk. Setting an override value without its enable, or leaving an enable asserted after training, can produce confusing PHY state.
- Reserved fields are explicitly named and masked. Driver code should preserve reserved bits unless the hardware specification for this ASIC explicitly requires otherwise.
- Several fields influence PHY calibration, PLL state, RX adaptation, and termination. Incorrect values can cause link-training failures, unstable display output, hotplug regressions, or suspend/resume issues that only reproduce on specific ASIC/display combinations.

## Test Signals

Useful validation signals for this chunk are mostly generated-header, build, and hardware-integration checks:

- Compile AMDGPU display code that includes `dpcs_3_1_4_sh_mask.h`.
- Compare this header against the authoritative DPCS 3.1.4 register database for exact field names, shifts, masks, and lane-instance repetition.
- Static checks that every complete register field in the chunk has matching `__SHIFT` and `_MASK` constants, while accounting for the deliberate boundary imbalance at lines 41437-41441.
- Grep/build checks for `DPCSSYS_CR2_RAWLANE1`, `DPCSSYS_CR2_RAWLANE2`, and `DPCSSYS_CR2_RAWLANE3` consumers after any rename or regeneration.
- Runtime display validation on ASICs using DPCS 3.1.4: DP link training at multiple rates and lane widths, HDMI mode if routed through these PHY blocks, hotplug, suspend/resume, display clock changes, lane disable/reenable, and error recovery.
- Register readback during bring-up to verify reset/request/ack, rate/width/pstate, MPLL state, TX/RX data enable, RX adaptation done/ack, calibration/FSM status, IRQ clear/mask behavior, and OCLA/debug status transitions.

## Chunk Notes For Merge

This chunk belongs to the CR2 raw-lane section of `dpcs_3_1_4_sh_mask.h`. Earlier chunks define the beginning of the CR2 block and the first part of lane 0; later chunks continue lane 3 and the rest of the file. The final per-file research document should describe the whole file as a generated ASIC bitfield map, not handwritten driver logic, and should merge the repeated lane 0-3 patterns rather than treating each lane as independent code.
