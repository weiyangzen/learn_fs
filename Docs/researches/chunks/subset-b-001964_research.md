# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 85848-88287

## Scope

This chunk is a generated DCN 3.2.0 register-field shift/mask slice for the AMD display C20 PHY register namespace. It contains C preprocessor constants only: every in-scope definition is a `_SHIFT` or `_MASK` macro for a hardware register field, with `//<REGISTER>` comments grouping fields by register. There are no functions, structs, enums, allocations, branches, loops, syscalls, locking operations, or direct MMIO accesses here.

The range begins in the middle of `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_SLICER_CTRL`; the first field shift for `RX_ANA_SLICER_CTRL_E` is on the previous line and is outside this chunk, while its mask is inside this chunk. The range ends in the middle of `C20_PHY_CR0_RAWLANEAONX_DIG_RX_STARTUP_CAL_ALGO_CTL_0`; only the skip-field shifts and the first six masks are present here, with the remaining masks continuing after line 88287. Final file-level reconciliation must merge neighboring chunks before treating either boundary register as complete.

## Purpose And Hardware Surface

This header provides the bit-layout ABI used by AMDGPU Display Core and low-level PHY programming code for DCN 3.2.0 hardware. Companion generated headers provide register addresses; this file supplies bit positions and masks that register helper macros use to pack field values into MMIO writes and decode values from MMIO reads.

The hardware surface in this chunk is concentrated on the DisplayPort/PHY lane-control path:

- C20 per-lane RX analog controls under `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_*`, including slicer, IQ, IQ calibration bypass/data clocks, calibration DAC update triggers, loopback, AFE update, DFE/bypass/phase sample selection, termination-code override, RX status readback, AFE override input, and a dense set of analog configuration registers `RX_ANA_CREG00` through `RX_ANA_CREG11`.
- Raw lane TX PCS, TX firmware, TX IRQ, TX control, and TX PMA transfer controls under `C20_PHY_CR0_RAWLANEX_DIG_TX_*`, covering PCS lane override/input/output fields, firmware override/input/output fields, TX-rate/reset/request/loopback/retune/termination/lane-mode interrupts, TX FSM controls, clock controls, termination code, firmware power-up completion, MPLL recalibration controls, PMA lane and supervisor transfer controls, and rtune controls.
- Raw lane RX PCS, RX firmware, RX IRQ, RX control, RX PMA, and raw-lane FSM controls under `C20_PHY_CR0_RAWLANEX_DIG_RX_*` and `C20_PHY_CR0_RAWLANEX_DIG_FSM_*`, covering RX PCS override/input/output/context settings, firmware adaptation handshake and figure-of-merit controls, TX pre/main/post direction requests from RX adaptation, clock controls, RX reset/request/rate/p-state/adaptation/margin interrupts and clears, adaptation mode/status, CDR/PPM/misc PMA controls, margining deltas/status/errors, IQ and phase-adjust code access, FSM override/jump/status/breakpoint/scratch/lock controls, fast-path enables, skip-calibration controls, and RX calibration status.
- Raw lane always-on TX controls under `C20_PHY_CR0_RAWLANEAONX_DIG_TX_*`, including firmware state readback, SRAM recovery, startup/continuous algorithm skips, fast flags, high-power protection and transceiver mode overrides, initial power-up done, MPLLA/MPLLB DCC range/full/half-rate calibration banks, DCC code readback, calibration-done flags, selected recalibration bank, and `TX_DISABLE`.
- The beginning of raw lane always-on RX startup algorithm control under `C20_PHY_CR0_RAWLANEAONX_DIG_RX_STARTUP_CAL_ALGO_CTL_0`, which gates or skips specific RX startup calibration steps.

## Important Definitions

The generated interface follows the standard AMD display register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for that field.
- `//<REGISTER>` comments identify the register whose field definitions follow.

Important macro families in this range:

- `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_SLICER_CTRL`, `RX_ANA_IQ`, `RX_ANA_IQC_*`, `RX_ANA_CAL_DAC_CTRL_EN`, `RX_ANA_LOOPBACK_CTRL`, `RX_ANA_AFE_UPDATE_EN`, `RX_ANA_*_SAMP_SEL`, and `RX_TERM_CODE_*` define analog RX field locations for slicer control, IQ sync bypass/reset overrides, IQC bypass/data override values and self-clearing adjust clocks, DAC update triggering, loopback selection, AFE update forcing, sample source selection, and termination-code override/readout clocking.
- `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_STAT_OUT_0`, `RX_STAT_OUT_1`, and `RX_STAT_IN_0` expose RX analog enable/status and readback fields, including clock/DCC/vreg/bleeder/AFE/loopback/bypass/DFE/divider/data-rate state, CDR/VCO/reset/word-clock state, calibration result, scope data, and VCO counter data.
- `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_AFE_OVRD_IN_2` and `RX_ANA_CREG00` through `RX_ANA_CREG11` define AFE, CDR, VCO, calibration, sensing, divider, DFE, phase, IQ, bypass, DCC, and related analog tuning fields. These are dense hardware-tuning registers with many small adjacent fields, so numeric mask correctness is especially important.
- `C20_PHY_CR0_LANEX_DIG_ANA_XF_RX_ANA_CREG0_OVRD` and `RX_ANA_CREG1_OVRD` provide coarse override enable fields for the `CREG` banks.
- `C20_PHY_CR0_RAWLANEX_DIG_TX_PCS_XF_*` and `RX_PCS_XF_*` define PCS-facing transfer and context fields, including lane overrides, lane input/readback, mode/rate/request/reset/power-state signals, context configuration, and override output fields.
- `C20_PHY_CR0_RAWLANEX_DIG_TX_FW_XF_*` and `RX_FW_XF_*` define firmware-facing transfer fields for override controls, lane number, TX/RX request/ack/data handshakes, RX adaptation acknowledgement/FOM, TX coefficient direction requests, and firmware clock control.
- `C20_PHY_CR0_RAWLANEX_DIG_TX_IRQ_CTL_*` and `RX_IRQ_CTL_*` define interrupt mask, enable, status, and clear fields. TX interrupts include rate, reset, request, parallel loopback enable/disable, rtune, termination-control, and lane-transceiver-mode events. RX interrupts include reset, request, rate, p-state, adaptation request/disable, termination-control, and multiple margining events.
- `C20_PHY_CR0_RAWLANEX_DIG_TX_CTL_*` and `RX_CTL_*` define control-plane fields for TX/RX FSM command paths, clock enables, off-canonical/adaptation status, rate IRQ acknowledgement, termination code, MPLL restart calibration controls, adaptation mode/select, PPM drift, CDR detection, PMA miscellaneous controls, FOM values, reference errors, IQ/phase adjustment codes, margin deltas/status/errors, and phase-update enables.
- `C20_PHY_CR0_RAWLANEX_DIG_TX_PMA_XF_*` and `RX_PMA_XF_*` define PMA transfer override/input/output fields and PMA-lane rtune controls.
- `C20_PHY_CR0_RAWLANEX_DIG_FSM_*` defines raw-lane firmware/FSM debug and policy controls: FSM override and jump-bank fields, memory breakpoints, address/status monitors, firmware configuration stage, scratch registers, control-register lock, fast supervisor/TX/RX paths, and many one-bit skip controls for TX DCC, RX AFE/DFE/IQ/phase/DCC/VGA/CTLE/ATT/SIGDET/VGEN/margining calibration and adaptation phases.
- `C20_PHY_CR0_RAWLANEAONX_DIG_TX_*` defines always-on TX firmware state, SRAM recovery counters/addresses, CCA loop/wait counters, startup/continuous algorithm skip flags, fast flags, high-power protection, transceiver mode, initial power-up done, override input, MPLLA/MPLLB DCC calibration banks, calibration-done indicators, DCC range/code outputs, calibration bank selection, and TX disable.
- `C20_PHY_CR0_RAWLANEAONX_DIG_RX_STARTUP_CAL_ALGO_CTL_0` starts the always-on RX startup calibration skip bitmap for AFE, reference, reference extension, attenuator, VGA, VGA extension, CTLE, IQ, IQ delta, phase, phase extension, DFE, DFE extension, error, and bypass calibration.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core or PHY support code combines these macros with generated register addresses and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, field-composition macros, and low-level MMIO read/write wrappers.

Typical runtime flow using definitions from this chunk:

1. DCN 3.2 PHY bring-up and link training code writes raw-lane TX/RX PCS, PMA, firmware-transfer, and FSM policy fields to configure lane mode, rate, reset, requests, calibration bypass, firmware handshake behavior, and analog tuning.
2. RX analog calibration and adaptation code programs `RX_ANA_*` controls, optionally overrides selected AFE/CDR/VCO/IQ/DCC fields through `CREG` registers, triggers self-clearing update/adjust clocks, and then reads status/counter/result fields.
3. TX calibration code selects DCC calibration banks, reads or writes MPLLA/MPLLB DCC common-mode/differential full-rate and half-rate codes, monitors per-bank/global calibration-done fields, and can restart MPLL calibration through TX control fields.
4. Interrupt handling code masks, enables, acknowledges, and clears TX/RX PHY events for rate changes, resets, requests, adaptation, margining, loopback, retuning, termination, and transceiver-mode changes.
5. Debug, firmware, and manufacturing/bring-up paths use FSM monitor, breakpoints, scratch registers, SRAM recovery controls, firmware state readback, FOM/readback fields, CDR/PPM status, and margining status/error fields to inspect or steer low-level PHY state.

The state described here is hardware register state, not driver-owned persistent memory:

- Persistent programmed state includes analog RX tuning/override values, loopback and termination-code overrides, TX/RX PCS/FW/PMA override enables, IRQ masks/enables, TX/RX FSM command/control settings, adaptation mode selection, phase/IQ code write values, FSM skip/fast policy bits, SRAM recovery settings, startup/continuous algorithm skips, high-power protection, lane transceiver mode, DCC calibration bank selection, and TX disable.
- Volatile readback includes analog RX status, calibration results, VCO counters, PCS/FW/PMA output values, TX/RX interrupt status, off-canonical/adaptation status, CDR detection, PPM drift, FOM and reference-error values, margin status/error values, IQ/phase code reads, FSM status monitor, firmware state registers, SRAM recovery iteration count, DCC calibration codes, and calibration-done flags.
- Side-effecting fields include self-clearing IQC adjust clocks, DAC/AFE update triggers, IRQ clear registers, rate IRQ acknowledgements, FSM override/jump controls, memory breakpoints, CR lock, SRAM recovery enable/control, MPLL restart calibration controls, and calibration skip/fast flags that change the hardware training sequence.

## Dependencies And Integration Points

This chunk depends on exact generated-name consistency across the DCN 3.2.0 register header family. It is normally consumed with the matching C20 PHY register offset header and AMD Display Core register helper layer. C compilation catches missing symbols, but wrong numeric shifts or masks usually compile successfully and then surface as hardware misprogramming.

Important integration points include:

- DCN 3.2 link encoder, PHY, and link-training code in AMDGPU Display Core, which uses C20 PHY lane controls to configure DisplayPort/PHY link rate, lane state, resets, loopback, transceiver mode, termination, and TX/RX calibration.
- Firmware-facing and DMUB-assisted display flows that exchange PHY requests, acknowledgements, lane numbers, adaptation FOM, coefficient directions, and firmware state through the `*_FW_XF_*`, `*_FW_STATES_*`, and `*_FSM_*` register families.
- DC IRQ handling paths for PHY and link events, which depend on the TX/RX IRQ mask/enable/status/clear field names and values matching the hardware specification.
- PHY debug, diagnostics, and lab bring-up tooling that reads FSM monitors, scratch registers, breakpoints, RX analog status, CDR/VCO counters, margining state, calibration status, and DCC calibration codes.
- Power-management and modeset/link-reconfiguration paths that may toggle fast-path flags, skip calibration stages, disable TX, change lane transceiver mode, or restart TX/RX calibrations during hotplug, link retraining, suspend/resume, or display mode changes.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.2.0 hardware specification is the primary risk. A single incorrect field position can corrupt PHY lane bring-up, DisplayPort link training, RX adaptation, TX DCC calibration, interrupt handling, or low-power transitions.
- This range contains many dense 16-bit analog and control registers with adjacent fields. Off-by-one shifts or masks that overlap reserved bits may compile cleanly but cause unstable link training, marginal eye openings, intermittent blanking, or failures only at high link rates.
- Repeated and similarly named families are easy to mis-generate: TX vs RX, PCS vs PMA vs FW, `LANEX` vs `RAWLANEX` vs `RAWLANEAONX`, MPLLA vs MPLLB, full-rate vs half-rate, status vs clear registers, and startup vs continuous calibration flags.
- Side-effecting clear, ack, update, restart, enable, and skip fields require precise masks. Incorrect values can drop or repeatedly fire PHY interrupts, skip required calibration, leave stale status latched, trigger unintended recalibration, or lock out control-register updates.
- Boundary completeness is a chunking risk. `RX_SLICER_CTRL` and `RX_STARTUP_CAL_ALGO_CTL_0` are partial in this chunk, so final reconciliation must pull in adjacent chunks before documenting complete register layouts.
- Firmware and hardware contract compatibility matters. These generated constants are effectively an ABI between the driver, firmware-assisted flows, and the PHY hardware; local edits should come from regenerated register definitions or a verified hardware-spec update rather than manual cleanup.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU Display Core with DCN 3.2 support enabled and ensure all in-scope `C20_PHY_CR0_LANEX`, `C20_PHY_CR0_RAWLANEX`, and `C20_PHY_CR0_RAWLANEAONX` field names referenced by PHY, link, IRQ, firmware, and diagnostics code resolve.
- Run generated-register consistency checks that every complete in-scope register family has paired `_SHIFT` and `_MASK` definitions, masks fit within the expected register width, fields do not overlap unexpectedly, and repeated TX/RX/MPLLA/MPLLB/bank families match the hardware spec.
- Compare the numeric masks and shifts against the authoritative DCN 3.2.0 C20 PHY register specification, focusing on side-effecting IRQ clear/ack bits, calibration skip/fast bits, DCC bank/code fields, analog `CREG` fields, firmware handshakes, and boundary registers split across chunks.
- Exercise DisplayPort link training and retraining across supported link rates and lane counts, including hotplug, suspend/resume, MST if available, link loss/recovery, and high-bandwidth modes; watch for link-training failures, black screens, flicker, or repeated PHY resets.
- Stress RX adaptation and margining paths by checking adaptation request/disable interrupts, FOM readbacks, IQ/phase code read/write fields, margining status/error fields, CDR detection, PPM drift, and RX analog status after mode changes.
- Validate TX calibration by reading MPLLA/MPLLB per-bank and aggregate calibration-done flags, DCC range/full/half-rate codes, selected calibration bank, and restart-calibration behavior during link-rate changes and resume.
- Test interrupt behavior by masking/enabling/clearing TX and RX PHY IRQs and confirming rate/reset/request/adaptation/margining/loopback/retune/termination/lane-mode events are neither lost nor stuck.
- Use debug traces or register dumps before and after PHY power-up, link training, retraining, and power-down to confirm programmed persistent fields and volatile readback fields decode coherently through these masks.

## Chunk-Specific Summary

Lines 85848-88287 define DCN 3.2.0 C20 PHY register bit shifts and masks for per-lane RX analog controls, raw-lane TX/RX PCS/FW/PMA/control/IRQ/FSM paths, and raw-lane always-on TX calibration and startup controls, ending at the first masks for RX startup calibration skip control. The content is generated register ABI rather than executable logic. Correctness depends on exact mask/shift values, repeated-family instance correctness, careful handling of side-effecting clear/ack/update/restart/skip fields, and hardware validation across link training, adaptation, margining, DCC calibration, interrupts, firmware handshakes, and suspend/resume.
