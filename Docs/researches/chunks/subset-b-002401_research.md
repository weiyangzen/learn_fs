# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 36434-38923

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice for CR1 display PHY registers. It has no executable C logic; its interface is a set of preprocessor constants that describe bit positions (`__SHIFT`) and field masks (`_MASK`) for DPCS indirect hardware registers.

The requested range spans 2,490 lines and contains 2,115 `#define` entries: 1,127 shift constants and 988 mask constants. It covers 375 explicit register comments plus the tail of the opening `DPCSSYS_CR1_RAWAONLANE1_DIG_INIT_PWRUP_DONE` group whose comment is immediately before the chunk. The range starts inside the raw always-on lane 1 adaptation/status area, continues through complete raw always-on lane 2, lane 3, and lane-X replicated register families, then enters the CR1 supervisor (`SUPX`) digital and analog control space through `DPCSSYS_CR1_SUPX_ANA_MPLLA_OVRD`.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO accesses in this range. The exported surface follows AMD's generated register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: field least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used by register helpers to isolate, compose, or update the field.

Important macro families in this chunk are:

- `DPCSSYS_CR1_RAWAONLANE1_DIG_*`: the chunk starts after lane 1 RX IQ, coarse-tune, and early `INIT_PWRUP_DONE` context. Covered lane 1 fields include RX adaptation readbacks (`ATT`, `VGA`, `CTLE`, DFE taps 1-5), adaptation-done and fast-flow flags, even/odd slicer controls, MPLL/RCAL calibration status, adaptation control words 0-7, MPLL disable, TX/RX disable overrides, LOS and signal-detect filters, RX override outputs, signal-detect calibration and HF/LF codes, RX VREF/calibration code storage, RX DCC calibration code banks, TX DCC bank address/data/continuous control, MPLL bandgap control, firmware MM/adaptation/calibration config, lane transceiver mode override/input, RX signal-detect config, and TX DCC config.
- `DPCSSYS_CR1_RAWAONLANE2_DIG_*`, `DPCSSYS_CR1_RAWAONLANE3_DIG_*`, and `DPCSSYS_CR1_RAWAONLANEX_DIG_*`: these repeat the raw always-on lane pattern for concrete lanes 2 and 3 and for the lane-X broadcast/indexed form. The repeated groups include AFE attenuation and CTLE IDAC offsets, RX adaptation IQ/FOM, DFE summer/phase/reference/data/bypass/error VDAC offsets, RX phase adjust mapping, MPLLA/MPLLB coarse tune, initial power-up done, adaptation readbacks, slicer controls, calibration status, override outputs, DCC and signal-detect controls, firmware configuration, and lane mode controls.
- `DPCSSYS_CR1_SUPX_DIG_IDCODE_*` and `REFCLK_OVRD_IN`: supervisor identity and reference-clock override fields. The reference-clock group exposes override enable/value fields for reference clock enable, reference pad selection, alternate low-power reference-clock selection, and test TX reference-clock enable.
- `DPCSSYS_CR1_SUPX_DIG_MPLLA_*` and `DPCSSYS_CR1_SUPX_DIG_MPLLB_*`: digital supervisor override and ASIC-input views for MPLLA/MPLLB. These cover divider clock and HDMI clock overrides, PLL enable/reset/standby/calibration/feedback-clock controls, reference/feedback divider and VCO settings, SSC enable/spread/peak/stepsize fields, fractional-N numerator/remainder/denominator word fields, clock sync, charge-pump and gain-scheduled charge-pump overrides, and corresponding ASIC input mirrors.
- `DPCSSYS_CR1_SUPX_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `DEBUG`, `ASIC_IN`, `LVL_ASIC_IN`, and `BANDGAP_ASIC_IN`: supervisor-level controls for PHY reset, reference clocks, burn-in/powerdown tests, RTUNE request/ack, MPLLA/MPLLB state, TX calibration inhibit/done, prescaler fast-start, RX VREF level, TX boost level, RX VCO VREF selection, bandgap enable, and debug readout.
- `DPCSSYS_CR1_SUPX_ANA_*`: analog supervisor controls for prescaler measurement and fast-start, RTUNE analog test-bus/reference controls, bandgap/reference selection, power measurement switches, VPHUD/VPLL/RX calibration references, and MPLLA analog miscellaneous and override controls.

Most field masks are 16-bit values with an `L` suffix, matching the DPCS indirect register width used by these raw lane and supervisor blocks. Some single-bit fields define shifts only and rely on consumer macros or generated tables to use the expected bit position; this is normal in this generated family and is visible across the analog supervisor groups where only reserved masks may be emitted.

## Control Flow

This header has no runtime control flow. It contributes to compile-time register metadata:

1. AMD display resource code for DCN 3.1.6 includes `dpcs_4_2_3_offset.h` and this shift/mask header.
2. Version-specific register, shift, and mask tables token-paste these generated names into the AMD display register-helper layer.
3. Runtime code elsewhere uses helpers such as register read, write, get, set, and update wrappers to program or inspect DPCS CR1 raw-lane and supervisor hardware fields.
4. Actual sequencing for PHY power-up, link training, RX adaptation, DFE/AFE calibration, signal detect, DCC, MPLL programming, RTUNE, test overrides, and debug readback is implemented outside this generated header and by hardware/firmware state machines.

The macros only describe bit layout. They do not encode reset values, access width beyond the visible masks, read-only/write-only status, write-one-to-clear semantics, clock-domain restrictions, power-domain validity, self-clearing behavior, or required ordering between fields.

## State And Persistence Behavior

No software state is stored or persisted by this chunk. The names describe hardware-visible CR1 DPCS state:

- Raw lane adaptation state includes AFE/CTLE/DFE offsets, RX phase adjustment, adaptation figure of merit, adaptation completion, DFE tap readbacks, slicer controls, adaptation control words, RX DCC calibration code banks, RX VREF/calibration code storage, signal-detect calibration and filtering, and fast calibration/adaptation flags.
- Raw lane power and control state includes initial power-up done, phase-2 power-up done, MPLLA/MPLLB coarse tune, MPLL disable, lane common MPLL/RCAL calibration done/init bits, TX/RX disable override enable/value bits, lane transceiver-mode override/input fields, and firmware MM/adaptation/calibration configuration latches.
- Raw lane diagnostics and override state includes RX override output banks, statistics, signal-detect output override/input, TX DCC bank address/data and continuous mode, MPLL bandgap control, RX signal-detect config, and TX DCC config.
- Supervisor clock state includes reference-clock overrides, MPLLA/MPLLB dividers, HDMI clock dividers, PLL enable/reset/standby/calibration/feedback controls, VCO frequency and divider programming, SSC configuration, fractional-N words, charge-pump values, clock sync, and A/B PLL ASIC input mirrors.
- Supervisor analog and support state includes PHY reset/reference/test/powerdown/RTUNE controls, TX calibration status/override, RX VREF and TX boost levels, bandgap enable/reference selection, prescaler and RTUNE analog controls, analog test-bus selection, and MPLLA analog override/miscellaneous controls.

Persistence is entirely hardware-defined. Configuration fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, done, calibration, statistics, handshake, and input mirror fields may be latched, sampled, valid only in active power domains, or overwritten by hardware state machines. The header itself does not define those semantics.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependencies are AMD's DPCS 4.2.3 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies the corresponding `ixDPCSSYS_*` register offsets. For this chunk, examples include `ixDPCSSYS_CR1_RAWAONLANE1_DIG_RX_ADPT_ATT` at `0x4117`, `ixDPCSSYS_CR1_RAWAONLANE2_DIG_AFE_ATT_IDAC_OFST` at `0x4200`, `ixDPCSSYS_CR1_SUPX_DIG_IDCODE_LO` at `0x8000`, and `ixDPCSSYS_CR1_SUPX_ANA_MPLLA_OVRD` at `0x8048`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`, tying these generated constants to the DCN 3.1.6 resource implementation.
- Consumer code is expected to combine this shift/mask header with AMD display register tables and register helper macros, not include it as an independent behavioral module.

Integration points implied by these fields include DisplayPort/HDMI PHY bring-up, link training, lane power management, raw always-on lane diagnostics, RX adaptation and equalization, signal-detect calibration, TX/RX DCC programming, MPLL A/B setup, spread-spectrum and fractional PLL programming, RTUNE, analog test-bus/debug flows, firmware-assisted calibration, hotplug and modeset transitions, suspend/resume, and GPU reset recovery.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware field, corrupting reserved bits, or decoding a status bit incorrectly.
- The file is generated metadata. Manual changes risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- The chunk starts inside the `DPCSSYS_CR1_RAWAONLANE1_DIG_INIT_PWRUP_DONE` area: the group comment is immediately before the requested line range, and earlier lane 1 raw AON context is in the previous chunk. Merge/reconciliation should not treat this range as the complete lane 1 description.
- Lane 2, lane 3, and lane-X blocks are highly repetitive. Generator or merge errors can affect only one concrete lane or only the broadcast/indexed lane-X form while nearby fields look correct.
- Many registers pair override value bits with override enable bits. Setting a value without enabling it may have no effect; leaving an enable bit asserted after debug or test use can force hardware away from normal PHY state-machine control.
- RX adaptation, DFE/AFE offsets, slicers, DCC, VREF, and signal-detect fields are link-quality sensitive. Bad masks can produce unstable training, false loss-of-signal, misleading diagnostics, or intermittent blank displays.
- MPLLA/MPLLB supervisor fields control clocks. Incorrect dividers, VCO, SSC, fractional-N, charge-pump, calibration, reset, or clock-sync masks can cause PHY lock failures, retraining loops, timing instability, or mode-specific display failures.
- Analog supervisor and test-bus controls may affect electrical behavior. Incorrect masks around bandgap, RTUNE, prescaler, VPHUD/VPLL references, or MPLLA analog override fields can break validation flows or low-level calibration.
- Reserved masks are common and often cover large bit ranges. Register writes should preserve reserved bits according to the register-helper pattern and hardware documentation.

## Test Signals

Useful validation combines build-time generated-header checks with hardware behavior:

- Build AMDGPU display support for DCN 3.1.6 code that includes `dpcs_4_2_3_sh_mask.h` through `dcn316_resource.c`. Missing or renamed macros should fail in generated register, shift, and mask table initialization.
- Static-check this line range for expected generated shape: 2,115 `#define` entries, 1,127 `__SHIFT` constants, 988 `_MASK` constants, and 375 explicit register comments, with the known opening boundary inside `DPCSSYS_CR1_RAWAONLANE1_DIG_INIT_PWRUP_DONE`.
- Cross-check complete register groups in this chunk against `dpcs_4_2_3_offset.h`, especially the raw lane 1/2/3/lane-X windows and the CR1 supervisor offsets beginning at `0x8000`.
- Compare against adjacent generated DPCS versions such as `dpcs_4_2_0_sh_mask.h` or `dpcs_4_2_2_sh_mask.h` where register layout is expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across lane counts, rates, power states, and hotplug/modeset transitions. Expected signals include stable link training, correct RX adaptation completion, no false LOS, and no stuck calibration or fast-flow status.
- Run suspend/resume and GPU reset paths to ensure lane raw AON and supervisor/MPLL state is reinitialized correctly rather than relying on stale hardware latches.
- Validate high-bandwidth and clock-sensitive modes that stress MPLLA/MPLLB divider, HDMI divider, SSC, fractional PLL, charge pump, reference-clock, and clock-sync controls. Watch for black screens, PHY lock failures, retraining loops, display corruption, or audio/video timing drift.
- Use register dumps or PHY debug traces on failing links to confirm DFE tap values, RX VREF/calibration codes, DCC calibration banks, signal-detect state, lane transceiver mode, RTUNE handshakes, supervisor debug fields, and MPLL/SSC/fractional fields decode as expected.
- Exercise diagnostic/manufacturing paths where available: analog test bus, firmware calibration configuration, signal-detect override, TX DCC bank access, MPLLA analog override, and supervisor prescaler/RTUNE controls.

## Chunk Notes For Merge

This document intentionally covers only lines 36434-38923 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks own the beginning of raw always-on lane 1 fields, including the comment and preceding fields for the opening `INIT_PWRUP_DONE` context. Later chunks continue CR1 supervisor analog MPLLA/MPLLB ATB, VCO, SSC, charge-pump, RTUNE, output, and remaining analog/debug fields. The final per-file report should describe the whole file as generated DPCS 4.2.3 ASIC bitfield metadata and reconcile this range with neighboring chunks before making whole-file claims.
