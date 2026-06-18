# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 62004-64392

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for display PHY register fields. It contains no executable C logic; its public surface is a dense set of preprocessor constants that encode bit positions (`__SHIFT`) and field masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,119 `#define` entries across 2,389 lines and describes 268 register groups. It starts in the middle of `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`: lines 62004-62006 provide masks whose shift definitions are in the previous chunk. It then covers CR2 lane-X RX adaptation/status, RX statistic counters, MPHY controls, digital analog TX/RX override/status registers, raw analog TX/RX registers, raw memory placeholders, raw lane PCS/PMA/FSM/IRQ/TX/RX control registers, and ATE PCS override registers. Near the end it switches address blocks to `dpcssys_cr3_rdpcstxcrind` and begins CR3 supervisor/reference-clock/MPLLA/MPLLB override fields. The range ends inside `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`: only the first two masks are in this chunk, with the remaining masks in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface follows the generated register-field convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, compose, or update the field.

The main register-field families in this chunk are:

- CR2 RX adaptation status and controls: `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS` through `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_CR_BANK_DATA` expose DFE tap adaptation status, adaptation-done flags, even/odd DFE data and error VDAC offsets, slicer controls, error slicer levels, adaptation reset, DAC control selects, and CR bank address/data access.
- CR2 RX statistic collection: `DPCSSYS_CR2_LANEX_DIG_RX_STAT_*` defines sample load/start, data masks, pattern match controls, statistic/correlation source selectors, counter enables, clocking and pause controls, valid-loss clear/control, sample and statistic counters, calibration comparison clock control, extended match controls, statistic control, and stop behavior.
- CR2 MPHY and digital analog override/status surfaces: `DPCSSYS_CR2_LANEX_DIG_MPHY_RX_*`, `DIG_ANA_TX_*`, `DIG_ANA_RX_*`, `DIG_ANA_STATUS_*`, `DIG_ANA_MPHY_*`, `DIG_ANA_SIGDET_*`, and `DIG_ANA_TX_DCC_*` cover MPHY PWM and low-speed termination, TX analog enable/clock/reset/serial/data override outputs, TX termination and EQ override banks, RX CTLE/VCO/power/slicer/scope/DAC/calibration controls, signal-detect overrides, term-code clocks, DCC DAC overrides, and status bits such as PLL lock, receive detect, clock ACK, calibration outputs, and RX signal-detect state.
- CR2 raw analog lane registers: `DPCSSYS_CR2_LANEX_ANA_TX_*` and `DPCSSYS_CR2_LANEX_ANA_RX_*` describe analog TX power, measurement overrides, alternate/test buses, ATB controls, DCC DAC and control fields, termination code programming, override clocking, miscellaneous slew/vreg/peaking/reserved controls, RX clocks, CDR/deserializer, slicer controls, RX power, squelch, calibration, ATB measurement/reference selection, and reserved analog fields.
- CR2 raw memory and raw lane PCS transfer fields: `DPCSSYS_CR2_RAWMEM_DIG_ROM_CMN0_B0_R0`, `RAM_CMN0_B0_R0`, and `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_*` describe raw ROM/RAM words plus PCS TX/RX override inputs, PCS inputs/outputs, RX adaptation controls and acknowledgements, figure-of-merit reporting, directed TX pre/main/post cursor feedback, lane number, ATE overrides, RX EQ delta/IQ controls, TX/RX termination control overrides, and PH2 calibration.
- CR2 raw lane FSM and fast-flow controls: `DPCSSYS_CR2_RAWLANEX_DIG_FSM_*` includes FSM override, memory/status monitors, fast RX startup/adapt/AFE/DFE/bypass/reference-level/IQ calibration controls, fast supervisor/TX common-mode/RX detect/RX power-up/VCO wait/VCO calibration controls, common MPLL and RCAL status, continuous adaptation/calibration flags, CR lock, TX DCC flags/status, TX EQ update flags, OCLA selection, and RX IQ phase offset.
- CR2 raw lane IRQ controls: `DPCSSYS_CR2_RAWLANEX_DIG_IRQ_CTL_*` defines RX/TX reset and request IRQ status, RX rate/pstate/adaptation IRQs, clear registers, IRQ masks, lane transceiver-mode interrupts, PH2 calibration request/disable IRQs, serial loopback IRQs, and DCC on-demand IRQ status.
- CR2 raw lane PMA, TX control, RX control, and ATE fields: `DPCSSYS_CR2_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and late `PCS_XF_ATE_*` registers expose PMA lane and supervisor override signals, TX/RX PMA handshakes, lane RTUNE, MPHY override paths, RX adaptation override output, TX FSM and clock controls, DCC continuous status, TX/RX OCLA probes, RX FSM/rate-change controls, LOS mask timing, RX data-enable override timing, off-cancel and adaptation continuous status, and ATE RX/TX override banks for manufacturing or debug flows.
- CR3 supervisor and MPLL fields: after `// addressBlock: dpcssys_cr3_rdpcstxcrind`, the chunk defines CR3 supervisor ID code, reference-clock override, MPLLA/MPLLB divider and HDMI clock overrides, MPLLA/MPLLB main override inputs, multiplier controls, SSC controls, SSC peak/stepsize high and low words, fractional numerator/remainder/denominator words, charge-pump overrides, gain-scheduled charge-pump overrides, and the beginning of supervisor override input fields for prescaler, RTUNE, TX calibration, and alternate low-power reference-clock selection.

Most field masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these lane, raw-lane, raw-analog, supervisor, and MPLL blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. AMD display code for the matching DCN/DPCS generation includes the DPCS 4.2.0 offset header and this shift/mask header.
2. Register-list, shift-list, and mask-list setup code token-pastes generated register and field names into tables used by hardware sequencing, link encoder, PHY, AUX/link-training, clock-source, diagnostic, and interrupt paths.
3. Runtime driver code uses helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables.
4. The real sequencing for PLL programming, lane power, RX adaptation, RX statistic capture, DCC/RTUNE calibration, IRQ handling, PMA/PCS handshakes, test overrides, and debug readback lives outside this generated header.

The macros only describe bit layout. They do not encode access type, ordering constraints, reset values, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, or power-domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR2 lane-X and CR3 supervisor DPCS registers:

- RX adaptation state includes DFE tap status, adaptation done bits, slicer controls, even/odd data and error offsets, adaptation reset, DAC selection, CR bank address/data, CTLE/VGA/attenuation-adjacent status from the previous boundary, and RX calibration/scope/phase/signal-detect controls.
- RX statistic state includes loaded sample counts, pattern masks and matches, statistic/correlation source selectors, sample and statistic counters, done bits, counter enable bits, pause/clock controls, valid-loss handling, calibration-comparison clock controls, and stop controls.
- TX/RX analog lane state includes TX/RX power, clocks, reset, termination codes, EQ/peaking/slew/vreg controls, DCC DAC values, RX clock/CDR/deserializer/slicer settings, squelch and calibration values, ATB/test-bus selection, signal-detect status, PLL lock/readback, receive-detect readback, and reserved analog latches.
- Raw PCS/PMA state includes TX/RX pstate, rate, width, MPLL select/enable, reset/request/data-enable/loopback/beacon/async signals, RX adaptation request/disable/ACK/FOM, directed TX coefficient feedback, termination-control overrides, PH2 calibration, PMA supervisor and lane handshakes, lane RTUNE, MPHY PWM/termination, and RX adaptation override outputs.
- FSM and IRQ state includes lane state-machine override and monitor fields, fast-path calibration/adaptation enables and status, continuous adaptation/calibration flags, CR lock, TX DCC flags/status, TX EQ update flag, RX IQ phase offset, RX/TX reset/request/rate/pstate/adaptation/PH2/lane-mode/loopback/DCC IRQ status, clear, and mask fields.
- CR3 supervisor state includes ID-code readback, reference-clock override, MPLLA/MPLLB clock divider and HDMI divider override selection, PLL enable/divider/VCO/standby/calibration/fractional/clock-sync overrides, SSC enable and spread parameters, fractional PLL quotient/remainder/denominator words, charge-pump values, gain-scheduled charge-pump override enables, and the leading supervisor RTUNE/TX calibration/reference-clock override bits.

Persistence is hardware-defined. Configuration fields usually remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, IRQ, statistic, calibration, and handshake fields may be latched, sampled, clear-on-write, self-clearing, or valid only while the relevant lane/common clock and power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies matching `ixDPCSSYS_*` offsets. In the companion offset header, this chunk's CR2 groups map across offsets such as `0x9070` for `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`, `0x9080` for `RX_STAT_LD_VAL_1`, `0x90a0` for digital analog TX overrides, `0x90e0` for raw analog TX, `0xe000` for raw lane PCS transfer registers, `0xe020` for raw lane FSM registers, `0xe040` for raw lane IRQ registers, `0xe060` for raw lane PMA transfer registers, and `0xe0c0` for ATE PCS override registers.
- The same offset header marks the transition to `addressBlock: dpcssys_cr3_rdpcstxcrind`, where CR3 supervisor registers begin at offsets `0x0000` through the MPLLA/MPLLB and supervisor override region covered here.
- AMD display DCN/DPCS resource code consumes these generated constants through version-specific register, shift, and mask tables rather than by open-coding bit values.
- Link training, PHY bring-up, clock-source programming, display mode set, hotplug, suspend/resume, diagnostics, and interrupt code interact with the hardware fields described here through the register helpers and generated tables.
- Firmware/hardware state machines also interact with the same fields, especially for RX adaptation, DCC calibration, RTUNE, PMA/PCS handshakes, fast calibration/adaptation flows, IRQ latching, and MPLL/SSC/fractional PLL setup.

Behaviorally, this range is below the user-facing display stack. It defines the bit layout used when the driver or firmware powers and configures CR2 lane-X PHY components, programs CR3 supervisor/MPLL state, handles raw lane PCS/PMA handshakes, clears or masks low-level lane interrupts, and reads or controls diagnostics.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. The first register in this range, `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`, is split: its `__SHIFT` lines are immediately before line 62004. The last register, `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN`, is also split: most of its masks follow line 64392.
- The range crosses an address-block boundary from CR2 lane/raw-lane fields into CR3 supervisor fields. Consumers must pair these macros with the correct offset block and register table; treating all names as one lane-local block would be wrong.
- RX adaptation and statistic fields are sequencing-sensitive. Incorrect masks around DFE taps, slicers, VDAC offsets, adaptation reset, pattern masks, sample counters, source selectors, valid-loss handling, or stop controls can cause link-training failures, poor equalization, misleading diagnostics, or stuck polling loops.
- Analog TX/RX fields can affect electrical behavior. Wrong masks for termination, EQ, DCC, VCO, CDR, slicer, power, signal-detect, ATB, or calibration fields may produce blank displays, unstable links, compliance failures, or debug traces that do not match hardware state.
- Raw PCS/PMA override and ATE fields can bypass normal state-machine behavior. Misprogramming reset/request/data-enable/loopback/MPLL/termination/RTUNE/PH2 fields can leave a lane in a state that higher-level display code cannot easily reason about.
- IRQ status, clear, and mask registers are easy to confuse because many field names repeat across status, clear, and mask groups. Wrong masks can drop events, leave stale status latched, or cause repeated interrupts.
- CR3 MPLLA/MPLLB fields control clocks. Bad masks for dividers, HDMI dividers, VCO frequency, SSC, fractional PLL words, charge-pump overrides, calibration force, standby, or clock-sync override can cause clock instability, link retraining loops, black screens, or mode-specific regressions.
- Repeated A/B PLL and TX/RX register patterns are copy-sensitive. A generator or merge error can affect only MPLLA, only MPLLB, only RX, only TX, or only a single lane while nearby fields look correct.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.0. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has the expected `__SHIFT` and `_MASK` pair, allowing the known boundary exceptions for `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS` at the start and `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN` at the end.
- Cross-check every complete register group in this chunk against `dpcs_4_2_0_offset.h`, including the CR2-to-CR3 address-block transition.
- Diff against AMD's source register database and nearby generated variants such as DPCS 3.1.4, 4.0.x, or DCN integrated shift/mask headers where hardware layout is expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, power states, and PHY lanes. Expected signals are stable link training, correct RX adaptation completion, correct MPLL selection, no stuck ACK/status bits, and no unexpected lane IRQs.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in adaptation, statistic, analog, PMA/PCS, IRQ, and CR3 supervisor/MPLL fields.
- Validate high-bandwidth and clock-sensitive modes that stress MPLLA/MPLLB divider, HDMI divider, SSC, fractional PLL, charge pump, reference-clock, and clock-sync controls. Watch for black screens, PHY lock failures, retraining loops, display corruption, audio/video timing instability, or rate-specific failures.
- Use register dumps or PHY debug traces during failing links to confirm DFE tap status, VDAC offsets, slicer levels, RX statistic counters, DCC status, VCO/CDR state, RTUNE handshakes, FSM status, IRQ clear/mask bits, and MPLL/SSC fields decode correctly.
- Exercise diagnostic paths where available: OCLA, RX statistic match/count controls, analog test bus/readback fields, directed TX coefficient feedback, PH2 calibration, loopback controls, ATE overrides, and MPHY low-speed controls.

## Cross-Chunk Notes

The previous chunk owns the `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_DFE_TAP3_STATUS` shift definitions and earlier RX adaptation setup/status fields. This chunk begins with that register's masks, then covers a large CR2 lane-X/raw-lane section and the beginning of the CR3 supervisor/MPLL address block. The next chunk should finish `DPCSSYS_CR3_SUP_DIG_SUP_OVRD_IN` masks and continue CR3 supervisor/prescaler/output/MPLL power-control fields. The final per-file research document should reconcile these boundaries before making whole-file claims about all DPCS 4.2.0 register groups.
