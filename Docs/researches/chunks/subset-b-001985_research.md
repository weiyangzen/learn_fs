# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 136748-139179

## Scope

This chunk is a generated DCN 3.2.0 register-field shift/mask slice for AMD Display Core C20 PHY control-register block 2 (`CR2`). It contains C preprocessor constants only. The definitions are `_SHIFT` and `_MASK` macros grouped by `//<REGISTER>` comments; there are no functions, structs, enums, runtime branches, locking operations, allocations, syscalls, or direct MMIO accesses in this range.

The chunk starts at the final two masks of `C20_PHY_CR2_LANE3_DIG_RX_STAT_STAT_CTL1`; the earlier shifts and masks for that register are in the previous chunk. It ends inside `C20_PHY_CR2_RAWLANE0_DIG_FSM_SKIP_RX_VGA_STARTUP_CAL`; its reserved-bit mask continues on the next line outside this chunk. Reconciliation with adjacent chunks is required before treating either boundary register as complete.

## Purpose And Hardware Surface

The file provides the bit-layout ABI for DCN 3.2.0 hardware registers. Companion generated headers define register addresses, while this header defines field positions and masks used by AMDGPU Display Core register helpers to compose MMIO writes and decode MMIO reads.

This slice covers two main C20 PHY surfaces:

- `C20_PHY_CR2_LANE3_DIG_RX_*` and `C20_PHY_CR2_LANE3_DIG_ANA_XF_RX_*`: Lane3 receive-side statistics, IQ calibration control/status, analog RX override/output/readback, signal detect calibration, VCO/calibration controls, DAC and AFE override controls, loopback, termination-code override, sample-selection controls, and dense analog configuration registers `RX_ANA_CREG00` through `RX_ANA_CREG11`.
- `C20_PHY_CR2_RAWLANE0_DIG_*`: RawLane0 TX/RX PCS, firmware-transfer, IRQ, control, PMA-transfer, and FSM policy/debug definitions. These cover TX/RX lane handshakes, rate/reset/request/power-state signals, firmware acknowledgement paths, adaptation and margining signals, PHY interrupts and clear bits, TX/RX control FSM command fields, PMA retuning, firmware scratch/debug state, fast-path enables, and many RX/TX calibration skip bits.

The `CR2` prefix identifies a generated register block instance, while `LANE3` and `RAWLANE0` are separate naming domains within that block. Consumers must not assume the lane index in one domain maps mechanically to the other without the matching address/register header.

## Important Definitions

The generated interface follows the AMD display register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field least-significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted field mask.
- `//<REGISTER>` comments delimit the register whose fields follow.

Important macro families in this range:

- `C20_PHY_CR2_LANE3_DIG_RX_STAT_*` defines Lane3 RX statistics and pattern-matching fields: sample count windows, statistic counters 0 through 6, comparator clock control, match-pattern/mask fields for CR1A/CR1B/CR2A, statistic freeze/stop controls, shadowed count readback, load-value extension, and valid-loss/status control bits.
- `C20_PHY_CR2_LANE3_DIG_RX_IQC_CTL_*` defines IQ calibration bypass/data adjustment, IQC step/jump/bypass/data-enable configuration, DFE-bypass use, and IQC FSM-state readback.
- `C20_PHY_CR2_LANE3_DIG_ANA_XF_RX_CTL_OVRD_OUT` and `RX_PWR_OVRD_OUT_*` define analog RX output override values and override enables for clocks, data rate, divider enables, DFE/tap/bypass enables, async reset, DCC/vreg/bleeder/AFE power and reset controls, CDR/VCO power, PFD reset, and word-clock reset.
- `C20_PHY_CR2_LANE3_DIG_ANA_XF_RX_SIGDET_*`, `RX_VCO_OVRD_OUT_*`, and `RX_CAL_*` define signal-detect calibration enables/results, high/low-frequency calibration fields, VCO counter controls/readback, and startup/rate/continuous calibration mode fields.
- `C20_PHY_CR2_LANE3_DIG_ANA_XF_RX_DAC_CTRL*`, `RX_DCC_CAL_DAC_CTRL_RANGE`, `RX_AFE_OVRD_IN_*`, `RX_SCOPE`, `RX_SLICER_CTRL`, `RX_ANA_IQ`, `RX_ANA_IQC_*`, `RX_ANA_CAL_DAC_CTRL_EN`, `RX_ANA_LOOPBACK_CTRL`, and `RX_ANA_AFE_UPDATE_EN` define analog RX tuning, override, trigger, sampling, scope, IQ, loopback, and AFE update fields.
- `C20_PHY_CR2_LANE3_DIG_ANA_XF_RX_TERM_CODE_*`, `RX_STAT_OUT_*`, and `RX_STAT_IN_0` expose termination-code override/readout, analog RX status for enabled/reset/power/calibration state, VCO counter data, signal-detect state, and scope data.
- `C20_PHY_CR2_LANE3_DIG_ANA_XF_RX_ANA_CREG00` through `RX_ANA_CREG11`, plus `RX_ANA_CREG0_OVRD` and `RX_ANA_CREG1_OVRD`, define dense analog control-register fields for AFE, slicer, CDR, VCO, divider, DFE, phase, IQ, bypass, DCC, calibration, sense, and override-bank selection.
- `C20_PHY_CR2_RAWLANE0_DIG_TX_PCS_XF_*`, `TX_FW_XF_*`, `TX_IRQ_CTL_*`, `TX_CTL_*`, and `TX_PMA_XF_*` define TX-side PCS/PMA/firmware transfer fields, lane override/input/output signals, firmware handshakes, lane number, TX rate/reset/request interrupts and clear bits, parallel loopback, retune, termination-control and lane-mode events, FSM control, clock control, termination code, firmware power-up done, MPLLA/MPLLB restart-calibration controls, and PMA lane/supervisor override fields.
- `C20_PHY_CR2_RAWLANE0_DIG_RX_PCS_XF_*`, `RX_FW_XF_*`, `RX_IRQ_CTL_*`, `RX_CTL_*`, and `RX_PMA_XF_*` define RX-side PCS/PMA/firmware transfer fields, RX mode/rate/request/reset/power-state/adaptation signals, PCS context configuration, firmware adaptation acknowledgement/FOM, TX coefficient direction requests from RX adaptation, RX interrupt mask/enable/status/clear fields, adaptation mode/status, PPM drift, CDR detection, PMA misc controls, FOM/readback/reference-error fields, IQ/phase code read/write fields, margining deltas/status/errors, and phase-update enables.
- `C20_PHY_CR2_RAWLANE0_DIG_FSM_*` defines raw-lane firmware/FSM debug and control fields: FSM override control, jump bank, FSM control, memory breakpoints, address/status monitors, firmware configuration stage, scratch registers 0 through 11, control-register lock, fast supervisor/TX/RX path bits, and skip bits for TX DCC and RX startup/continuous calibration/adaptation stages.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior emerges when AMDGPU Display Core and PHY support code combine these masks and shifts with generated register addresses and helpers such as register set/update/get/wait wrappers around MMIO access.

Typical runtime use of this chunk is:

1. Link bring-up or retraining code programs Lane3 RX statistic windows, match patterns, statistic enables/freezes, IQC settings, analog overrides, calibration modes, termination, and loopback fields, then reads status/count/result fields.
2. TX setup code configures RawLane0 PCS/PMA and firmware-transfer fields, asserts or releases reset/request/rate controls, tracks TX firmware power-up, handles TX IRQs, and can restart MPLL calibration through the TX control fields.
3. RX setup and adaptation code configures RawLane0 PCS/PMA and firmware-transfer fields, enables or acknowledges adaptation and margining events, reads FOM/reference-error/IQ/phase/margin status, and writes adaptation or margining code fields.
4. Interrupt code masks, enables, samples, and clears TX/RX PHY IRQ sources for rate, reset, request, loopback, retune, termination, lane mode, adaptation, p-state, and margining events.
5. Debug, lab bring-up, firmware, and manufacturing paths use the FSM monitor, memory breakpoints, scratch registers, CR lock, fast-path bits, and skip-calibration bits to inspect or steer low-level PHY sequencing.

The state represented here is hardware register state:

- Persistent programmed state includes statistic controls, match patterns and masks, IQC configuration, analog override values/enables, calibration-mode bits, DAC/AFE update controls, loopback and termination-code overrides, TX/RX PCS/FW/PMA override controls, IRQ masks/enables, TX/RX FSM control values, adaptation mode/selection, phase and IQ write-code fields, PMA misc controls, FSM fast/skip policy bits, breakpoints, scratch values, and CR lock.
- Volatile readback includes sample/statistic counters, done bits, shadow counts, IQC FSM state, signal-detect calibration result, VCO counter values, analog status outputs, scope data, termination readback, PCS/FW/PMA output signals, interrupt status bits, off-canonical and adaptation status, PPM drift, CDR detection, FOM values, reference errors, margin status/errors, IQ/phase read-code fields, FSM address/status monitors, firmware stage, and firmware scratch values.
- Side-effecting fields include statistic clear/freeze/stop controls, valid-loss clear, self-clearing IQC adjust clocks, DAC/AFE update triggers, IRQ clear registers, rate IRQ acknowledgements, MPLL restart-calibration controls, FSM override/jump controls, memory breakpoint controls, CR lock, and fast/skip bits that alter calibration sequencing.

## Dependencies And Integration Points

This chunk depends on exact consistency with the rest of the generated DCN 3.2.0 register header set. It is normally consumed together with the matching C20 PHY register-offset header and the AMD Display Core register helper layer. Missing names are compile-time failures, but wrong numeric shifts or masks usually compile and then become hardware behavior bugs.

Integration points include:

- AMDGPU Display Core link encoder, PHY, and link-training code for DCN 3.2 hardware, which uses C20 PHY lane and raw-lane fields to configure DisplayPort rate, lane state, resets, requests, loopback, termination, calibration, adaptation, and margining.
- Firmware-assisted and DMUB-facing display paths that exchange lane requests, acknowledgements, FOM, TX coefficient direction, lane number, and firmware/FSM state through the `*_FW_XF_*` and `*_FSM_*` register families.
- PHY interrupt handling paths that rely on the `TX_IRQ_CTL_*` and `RX_IRQ_CTL_*` mask/enable/status/clear fields to avoid lost, stuck, or spuriously repeated PHY events.
- Low-level diagnostics and lab tools that read statistic counters, analog RX status, signal-detect and VCO results, margining state, FSM monitors, scratch registers, CDR/PPM state, IQ/phase codes, and PMA/PCS transfer outputs.
- Power-management, hotplug, link-loss recovery, and modeset flows that can change lane rate/mode, retrain links, restart calibration, skip or accelerate calibration phases, and read calibration/adaptation status during suspend/resume or display reconfiguration.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.2.0 hardware specification is the central risk. A single wrong bit position or mask can misprogram PHY analog controls, skip required calibration, decode stale status as valid, or corrupt link-training state.
- The Lane3 analog `CREG` and override registers are dense 16-bit layouts with many adjacent fields. Overlapping masks, reserved-bit writes, or off-by-one shifts may only fail under specific link rates, boards, temperatures, or margining/adaptation paths.
- Similar names across instances are easy to confuse: `CR2` vs other control-register blocks, `LANE3` vs `RAWLANE0`, TX vs RX, PCS vs PMA vs FW, status vs clear registers, startup vs continuous calibration, and MPLLA vs MPLLB restart controls.
- Side-effecting clear, ack, update, restart, lock, fast, and skip fields require precise masks. Incorrect fields can leave interrupts stuck, drop one-shot events, trigger unintended recalibration, bypass mandatory startup steps, or prevent later control-register updates.
- Boundary completeness is a chunking risk. `STAT_CTL1` is only represented by its last two masks here, and `SKIP_RX_VGA_STARTUP_CAL` lacks its reserved-bit mask in this range; final file-level documentation must merge neighboring chunks before describing complete register layouts.
- Because this header is generated register ABI, manual edits should be avoided unless backed by regenerated definitions or a verified hardware-spec delta. Formatting-only changes can still create review noise and obscure meaningful generated changes.

## Test Signals

Useful validation signals combine build checks, generated-header consistency checks, and hardware behavior:

- Build AMDGPU with DCN 3.2 display support and confirm all referenced `C20_PHY_CR2_LANE3_*` and `C20_PHY_CR2_RAWLANE0_*` field symbols resolve in PHY, link-training, IRQ, firmware, and diagnostics code.
- Run generated-register consistency checks for paired `_SHIFT`/`_MASK` definitions, expected register width, non-overlapping fields, reserved-bit containment, repeated-family consistency, and boundary-register completion after chunk reconciliation.
- Compare masks and shifts against the authoritative DCN 3.2.0 C20 PHY register specification, prioritizing analog `CREG` fields, side-effecting IRQ clear/ack bits, calibration fast/skip bits, IQC update controls, MPLL restart controls, firmware handshakes, and margining/status fields.
- Exercise DisplayPort link training and retraining across supported link rates and lane counts, including hotplug, suspend/resume, link-loss recovery, MST where available, and high-bandwidth modes; watch for black screens, flicker, repeated PHY resets, and training failures.
- Stress RX adaptation and margining by observing adaptation request/disable IRQs, FOM and reference-error readbacks, IQ/phase code reads and writes, margin status/error fields, CDR detection, PPM drift, and analog RX status after mode changes.
- Validate TX behavior by checking rate/reset/request IRQs, loopback/retune/termination/lane-mode events, firmware power-up done, termination code programming, PMA transfer fields, and MPLLA/MPLLB restart-calibration behavior during rate changes and resume.
- Use register dumps before and after PHY power-up, retraining, margining, and power-down to confirm persistent programmed fields and volatile readback fields decode coherently through these masks.

## Chunk-Specific Summary

Lines 136748-139179 define DCN 3.2.0 C20 PHY `CR2` shift/mask macros for the tail of Lane3 RX statistics, Lane3 RX IQC and analog controls, RawLane0 TX/RX PCS/FW/IRQ/control/PMA transfer paths, and RawLane0 FSM debug/fast/skip policy fields. This is generated hardware register ABI, not executable logic. Correctness depends on exact bit positions, matching generated register addresses, careful handling of side-effecting fields, and hardware validation across link training, adaptation, margining, interrupts, calibration, firmware handshakes, and suspend/resume.
