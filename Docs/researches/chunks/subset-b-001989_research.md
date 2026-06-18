# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 146571-149060

## Scope

This chunk is a generated DCN 3.2.0 register-field shift/mask slice for the AMD display C20 PHY `CR2` raw-lane always-on namespace. It contains C preprocessor constants only: each in-scope definition is a `_SHIFT` or `_MASK` macro for a named hardware register field, with `//<REGISTER>` comments grouping fields by register. There are no functions, structs, enums, direct MMIO reads/writes, allocation paths, locks, branches, or loops in this range.

The range starts in the middle of the `C20_PHY_CR2_RAWLANEAON1_DIG_RX_*` bank-0 adaptation readback area; preceding bank-0 `ATT`, `VGA`, `CTLE`, and early DFE tap definitions are outside this chunk. It ends in the middle of `C20_PHY_CR2_RAWLANEAON3_DIG_RX_CAL_IQ_MAX`; only the register comment and the first shift line for `HALF_RATE` are in this chunk, with the rest of that register continuing after line 149060. Final file-level reconciliation must merge adjacent chunks before treating either boundary register family as complete.

## Purpose And Hardware Surface

This header supplies bit-layout constants for AMDGPU Display Core code that programs DCN 3.2.0 C20 PHY registers. Companion generated register headers provide register offsets; this `*_sh_mask.h` file provides the bit positions and masks used by register helper macros to compose MMIO writes and decode MMIO reads.

The hardware surface in this chunk is concentrated on CR2 raw-lane always-on TX/RX training, adaptation, and calibration state:

- `C20_PHY_CR2_RAWLANEAON1_DIG_RX_*` completes part of always-on RX lane 1 adaptation readback and policy: DFE tap-1 offset slices for bank 0, bank-0 IQ/ref-error/adapt-done status, full bank-1 adaptation readbacks for ATT/VGA/CTLE/DFE taps/DFE offsets/IQ/ref-error/adapt-done, TX-equalization direction polarity and threshold controls, generic adaptation control words `RX_ADPT_CTL_0` through `RX_ADPT_CTL_28`, IQ margin range, CDR detector and recovery timing controls, RX override input/output, signal-detect filtering, PMA override output, and RX input/output status.
- `C20_PHY_CR2_RAWLANEAON2_DIG_TX_*` defines always-on TX firmware state, TX SRAM recovery controls, CCA loop/wait counters, TX startup/continuous algorithm skip controls, fast flags, high-power protection and lane-transceiver-mode overrides, initial power-up state, TX disable override input, MPLLA/MPLLB DCC calibration bank values, per-bank and aggregate calibration-done readback, DCC code readback, calibration-bank selection, and TX disable input.
- `C20_PHY_CR2_RAWLANEAON2_DIG_RX_*` defines always-on RX startup calibration skip controls, startup adaptation skip controls, continuous calibration/adaptation skip controls, fast flags, VGEN/signal-detect/AFE/reference/DFE/setup offset registers, per-bank RX DCC and IQ calibration values for banks 0-3, per-bank and aggregate calibration-done readback, DCC code readbacks, IQ controls, adaptation IQ limits and error-slicer mode, banked adaptation readbacks, TX-equalization threshold controls, generic adaptation control words, CDR/signal-detect/RX override controls, and RX input/output status.
- `C20_PHY_CR2_RAWLANEAON3_DIG_TX_*` repeats the always-on TX state, recovery, algorithm, fast-path, override, DCC calibration, calibration-done, DCC code, bank-select, and TX input definitions for CR2 raw lane 3.
- `C20_PHY_CR2_RAWLANEAON3_DIG_RX_*` begins the corresponding always-on RX startup/continuous calibration, fast flag, offset, DFE VDAC, and IQ calibration area for raw lane 3, ending partway through `RX_CAL_IQ_MAX`.

## Important Definitions

The generated interface follows the standard AMD display register convention:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's least-significant bit index.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for that field.
- `//<REGISTER>` comments identify the register whose field definitions follow.

Important macro families in this chunk:

- Banked RX adaptation readback for lane 1 and lane 2: `RX_ADPT_ATT_BANK_*`, `RX_ADPT_VGA_BANK_*`, `RX_ADPT_CTLE_BANK_*`, `RX_ADPT_DFE_TAP1_BANK_*` through `TAP5`, DFE tap-1 offset quadrants such as `DFE_DEH`, `DFE_DEL`, `DFE_DOH`, `DFE_DOL`, `DFE_EEH`, `DFE_EEL`, `DFE_EOH`, and `DFE_EOL`, plus `RX_ADPT_IQ_BANK_*`, `RX_ADPT_REF_ERR_BANK_*`, and `RX_ADAPT_DONE_BANK_*`. These expose the results of RX adaptation/calibration banks and the validity/done signals that make those results meaningful.
- TX coefficient steering from RX adaptation: `RX_TX_EQ_DIR_POLARITY_CTL`, `RX_TX_PRE_DIV`, `RX_TX_MAIN_ATT_THRESHOLD`, `RX_TX_MAIN_VGA_THRESHOLD`, `RX_TX_POST_BOOST_THRESHOLD`, and `RX_TX_POST_TAP1_THRESHOLD` define polarity, divider, and low/high threshold fields used when RX adaptation requests TX main/pre/post coefficient changes.
- Generic RX adaptation control words: `RX_ADPT_CTL_0` through `RX_ADPT_CTL_28` are full 16-bit `VAL` fields. Their semantics are hardware/firmware defined rather than decomposed into subfields in this generated header, so consumers must rely on the hardware specification or firmware contract for individual bit meanings.
- CDR, IQ, signal-detect, and RX override controls: `RX_IQ_MARGIN_RANGE`, `RX_CDR_DETECTOR_CTL`, `RX_CDR_RECOVERY_TIME`, `RX_OVRD_IN_0`, `RX_SIGDET_EN_MASK_CTL`, `RX_SIGDET_FILT_CTL`, `RX_OVRD_OUT_0`, `RX_PMA_OVRD_OUT_0`, `RX_IN_0`, and `RX_OUT_0` define fields for CDR detection/PPM mode, adaptation-time CDR disable, recovery timing, RX disable/termination/signal-detect/VREF override values, signal-detect filter/hold counts, PMA termination/VREF overrides, and LF/HF signal-detect readback.
- TX firmware, recovery, and algorithm controls for lanes 2 and 3: `TX_FW_STATES_0/1`, `TX_MEM_BREAKPOINT_2`, `TX_SRAM_REC_CTRL`, `TX_SRAM_REC_MAX_ITER`, `TX_SRAM_REC_BASE_ADDR`, `TX_SRAM_REC_ADDR`, `TX_SRAM_REC_ITER`, `TX_SRAM_REC_EN`, `TX_CCA_START_LOOP_CNT`, `TX_CCA_WAIT_CNT`, `TX_STARTUP_ALGO_CTL_0`, `TX_CONT_ALGO_CTL_0`, and `TX_FAST_FLAGS_0` define firmware state readback, SRAM recovery recording/replay controls, CCA waits, startup/continuous DCC skip bits, and fast supervisor/TX startup/power-up flags.
- TX mode and protection overrides: `TX_TX_HP_PROT_EN_OVRD_IN`, `TX_TX_HP_PROT_EN_IN`, `TX_LANE_XCVR_MODE_OVRD_IN`, `TX_LANE_XCVR_MODE_IN`, `TX_INIT_PWRUP_DONE`, `TX_OVRD_IN_0`, and `TX_IN_0` define high-power protection, transceiver mode, initial power-up status, and TX disable/override fields.
- TX DCC calibration storage and readback: `TX_MPLLA_DCC_CTRL_RANGE_BANK_0..3`, `TX_MPLLA_DCC_FULL_BANK_0..3`, `TX_MPLLA_DCC_HALF_BANK_0..3`, matching `MPLLB` banks, `TX_MPLLA_CAL_DONE_BANK_0..3`, `TX_MPLLB_CAL_DONE_BANK_0..3`, aggregate `TX_MPLLA_CAL_DONE`, `TX_MPLLB_CAL_DONE`, `TX_CAL_DONE`, `TX_DCC_CTRL_RANGE_CODE`, `TX_DCC_CODE`, `TX_DCC_DIFF_CODE`, `TX_DCC_CM_CODE`, and `TX_CAL_BANK_SEL` define full/half-rate common-mode and differential calibration values, selected recalibration bank, and done/status signals.
- RX startup and continuous algorithm skip controls: `RX_STARTUP_CAL_ALGO_CTL_0`, `RX_STARTUP_CAL_ALGO_CTL_1`, `RX_STARTUP_ADAPT_ALGO_CTL_0`, and `RX_CONT_ALGO_CTL` define skip bits for AFE/reference/ATT/VGA/CTLE/IQ/phase/DFE/error/bypass/VGEN/signal-detect/DCC/full-rate/half-rate calibrations, banked AFE/DFE/IQ adaptation, adaptation reload, TX increment/decrement, FOM, margining, and continuous calibration/adaptation phases.
- RX fast and offset calibration registers: `RX_FAST_FLAGS`, `RX_VGEN_VDAC_OFST`, `RX_SIGDET_CAL`, `RX_AFE_RTRIM`, `RX_REF_*_VDAC_OFST`, `RX_DFE_EE_VDAC_OFST`, `RX_DFE_EO_VDAC_OFST`, `RX_SETUP_REF_CTLE_IDAC_OFST`, `RX_SETUP_REF_VGA1_IDAC_OFST`, `RX_SETUP_SLC_VGA1_IDAC_OFST`, `RX_VDAC_RANGE_SEL`, `RX_AFE_*_IDAC_OFST`, and DFE phase/data/bypass/error VDAC offset registers define analog trim and calibration offsets used by RX bring-up and lab/debug flows.
- RX DCC/IQ calibration banks and code readbacks for lane 2: `RX_DCC_CTRL_RANGE_BANK_0..3`, `RX_DCC_FULL_DATA/BYP/PHASE_BANK_0..3`, `RX_DCC_HALF_DATA/BYP/PHASE_BANK_0..3`, `RX_IQ_CAL_BANK_0..3`, `RX_CAL_DONE_BANK_0..3`, `RX_CAL_BANK_SEL`, `RX_DCC_*_CODE`, `RX_IQ_CAL`, `RX_CAL_DONE`, `RX_IQ_CTL_0`, `RX_IQ_CTL_1`, `RX_ADPT_IQ_LIMIT`, and `RX_ADPT_ERR_SLC_MODE` define stored DCC/IQ calibration results, selected bank, readback codes, global done state, IQ adjustment controls, adaptation IQ bounds, and error slicer mode.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when AMDGPU Display Core and low-level PHY code combine these macros with generated register offsets and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or lower-level MMIO wrappers.

Typical runtime flow using this slice:

1. Link bring-up or retraining code programs TX/RX algorithm skip and fast flags for the active CR2 lane, optionally selecting reduced startup/continuous calibration paths.
2. TX calibration code chooses or reads MPLLA/MPLLB DCC calibration banks, monitors per-bank and aggregate calibration-done bits, and decodes DCC common-mode/differential full-rate and half-rate codes.
3. RX startup calibration code controls skip bits for AFE, reference, ATT, VGA, CTLE, IQ, phase, DFE, DCC, VGEN, signal-detect, full-rate/half-rate, and bypass/error calibration stages, then reads banked done/status/code values.
4. RX adaptation code reads banked ATT/VGA/CTLE/DFE tap values, DFE tap-1 offset quadrants, IQ values, reference errors, and adaptation done bits; it may also tune generic `RX_ADPT_CTL_*` words and IQ limits.
5. Firmware/debug flows read `TX_FW_STATES_*`, use SRAM recovery controls and memory breakpoint fields, inspect CDR/signal-detect/RX input/output status, and decode VDAC/IDAC offset or DCC/IQ calibration values.

The state described here is hardware register state:

- Persistent programmed state includes generic RX adaptation control words, TX-equalization polarity/threshold/divider settings, CDR detector/recovery settings, RX/TX override enables and values, signal-detect filtering, TX/RX algorithm skip bits, fast flags, SRAM recovery configuration, lane transceiver mode override, high-power protection override, TX disable override, DCC/IQ calibration bank selection, and analog trim/offset values.
- Volatile readback includes TX firmware states, SRAM recovery iteration/address state, TX/RX calibration done bits, DCC/IQ calibration codes, RX adaptation bank results, reference-error values, adaptation done bits, CDR and signal-detect status, RX input/output state, and VGEN/signal-detect/AFE/DFE offset calibration outputs.
- Side-effecting or sequencing-sensitive fields include skip/fast bits that alter calibration execution, SRAM recovery enable/control fields, breakpoint fields, TX/RX disable overrides, calibration bank selection, CDR disable-in-adaptation, signal-detect filter/hold controls, and done/status fields whose interpretation depends on hardware sequencing.

## Dependencies And Integration Points

This chunk depends on exact generated-name and numeric consistency across the DCN 3.2.0 register header family. It is normally consumed with the matching C20 PHY register offset header and AMD Display Core register access helpers. A missing macro is usually caught by compilation, but a wrong shift or mask can compile cleanly and only appear as PHY misprogramming on hardware.

Important integration points include:

- AMDGPU Display Core link encoder, PHY, and DisplayPort link-training paths that configure CR2 raw-lane power-up, transceiver mode, TX disable, TX equalization steering, RX adaptation, CDR, signal detect, and calibration policy.
- Firmware-assisted or DMUB-mediated display flows that observe TX firmware states, use firmware recovery/breakpoint state, and rely on hardware/firmware-defined adaptation control words.
- PHY calibration code for TX MPLLA/MPLLB DCC banks and RX DCC/IQ/VDAC/IDAC banks, including calibration-done polling and selected-bank readback.
- Hotplug, link retraining, suspend/resume, and power-management paths that may toggle fast paths, skip selected calibrations, reselect banks, disable lanes, or re-run calibration sequences.
- Diagnostic and lab bring-up tooling that dumps RX adaptation results, DFE offsets, DCC/IQ codes, CDR/signal-detect status, analog offsets, SRAM recovery state, and firmware state registers.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.2.0 hardware specification is the main risk. These macros form a hardware ABI; off-by-one shifts or masks can corrupt PHY lane bring-up, RX adaptation, TX equalization, DCC/IQ calibration, or low-power recovery.
- Repeated lane and bank families are particularly error-prone. Lane 1, lane 2, and lane 3 definitions are structurally similar, as are bank 0-3, MPLLA/MPLLB, full/half-rate, common-mode/differential, data/bypass/phase, and startup/continuous control families.
- Many fields are densely packed 16-bit registers. Incorrect reserved masks or overlapping fields can silently write reserved bits and cause failures that appear only at specific link rates, cable conditions, or resume/retrain paths.
- `RX_ADPT_CTL_0..28` are full-width opaque `VAL` fields; their bit-level meaning is not documented by this header. Manual edits to these names or masks are risky because firmware or hardware may treat those words as a private contract.
- Calibration skip and fast flags can change physical training order. Bad masks can skip required calibrations or force shortened paths, producing intermittent black screens, unstable links, or marginal eye openings.
- Boundary completeness is a chunking risk. The start excludes earlier lane-1 bank-0 adaptation registers, and the end cuts off `C20_PHY_CR2_RAWLANEAON3_DIG_RX_CAL_IQ_MAX`; final documentation should merge neighboring chunks before claiming complete CR2 lane coverage.

## Test Signals

Useful validation combines generated-header checks, builds, and hardware behavior:

- Build AMDGPU Display Core with DCN 3.2 support enabled and confirm all referenced `C20_PHY_CR2_RAWLANEAON1`, `RAWLANEAON2`, and `RAWLANEAON3` field macros resolve.
- Run generated-register consistency checks that each complete register in this range has paired `_SHIFT` and `_MASK` definitions, masks fit the expected 16-bit register width, fields do not overlap unexpectedly, and repeated lane/bank/MPLL families match the hardware specification.
- Compare numeric masks and shifts against the authoritative DCN 3.2.0 C20 PHY register spec, focusing on algorithm skip/fast bits, override enables, DCC/IQ bank/code fields, calibration-done flags, CDR/signal-detect fields, and boundary registers split across chunks.
- Exercise DisplayPort link training and retraining on CR2-backed links across supported rates and lane counts, including hotplug, link loss/recovery, suspend/resume, MST if available, and high-bandwidth modes; watch for link-training failures, black screens, flicker, or repeated PHY resets.
- Validate TX calibration by reading MPLLA/MPLLB per-bank and aggregate done bits, DCC range/full/half/common-mode/differential codes, and selected calibration bank during link-rate changes and resume.
- Validate RX calibration/adaptation by checking banked ATT/VGA/CTLE/DFE tap values, DFE offset quadrants, IQ/ref-error/adapt-done fields, DCC/IQ calibration banks, global `RX_CAL_DONE`, CDR detector status, and signal-detect LF/HF outputs.
- Use register dumps before and after power-up, link training, retraining, and power-down to confirm programmed persistent fields and volatile readback fields decode coherently through these masks.

## Chunk-Specific Summary

Lines 146571-149060 define DCN 3.2.0 C20 PHY CR2 raw-lane always-on register shifts and masks for lane-1 RX adaptation tail fields, full lane-2 TX/RX always-on calibration/adaptation/control families, and the start of lane-3 TX/RX always-on families. The content is generated register ABI, not executable driver logic. Correctness depends on exact mask/shift values, repeated lane/bank family consistency, careful treatment of calibration skip/fast/override fields, and hardware validation through link training, adaptation, CDR/signal-detect, DCC/IQ calibration, and suspend/resume flows.
