# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 110170-112901

## Scope

This chunk covers a generated AMD Display Core DPCS 4.2.3 register shift header range. It contains 793 register comment blocks and 1,939 `#define ...__SHIFT` macros, not executable C. The covered slice starts in the `C20_PHY_CR0_RAWLANE3_DIG_FSM_*` RX fast/skip calibration controls and then spans repeated always-on raw-lane (`RAWLANEAON0`, `RAWLANEAON1`, `RAWLANEAON2`, and the beginning of `RAWLANEAON3`) TX/RX PHY register fields.

## Purpose

The header provides compile-time bit-position constants for manipulating DPCS/PHY control and status registers on AMD DCN 3.1.6-class display hardware. These constants are consumed with companion register-offset and mask headers by AMDGPU display code, especially register helper macros that combine register addresses, field masks, and field shifts to build MMIO values.

The definitions in this range mainly describe:

- RX digital FSM fast-path and skip controls for raw lane 3.
- Per-lane always-on TX firmware state, SRAM recovery, common calibration algorithm controls, fast flags, overrides, MPLL A/B DCC calibration banks, calibration completion bits, DCC result codes, bank selection, and TX disable input fields.
- Per-lane always-on RX startup/continuous calibration and adaptation controls, fast flags, VDAC/IDAC offsets, DFE offsets, DCC full/half-rate bank fields, adaptation result banks, RX-to-TX equalization thresholds, generic adaptation-control words, CDR detector/recovery controls, signal-detect filter controls, override inputs/outputs, PMA override outputs, live input bits, and live output bits.

## Important Definitions

There are no functions, structs, or runtime APIs in this chunk. The important API surface is the naming convention:

- `C20_PHY_CR0_RAWLANE3_DIG_FSM_*__FIELD__SHIFT` names bit positions for lane-3 digital FSM flags.
- `C20_PHY_CR0_RAWLANEAON{0,1,2,3}_DIG_TX_*__FIELD__SHIFT` names per-lane TX fields.
- `C20_PHY_CR0_RAWLANEAON{0,1,2}_DIG_RX_*__FIELD__SHIFT` names per-lane RX fields; the chunk ends before the matching RX section for `RAWLANEAON3`.
- `_BANK_0` through `_BANK_3` groups represent calibration/adaptation result banks. Most banked fields use the same field layout in each bank and each lane.
- `__VAL__SHIFT` indicates an entire field or opaque control word starting at bit 0. Many `RX_ADPT_CTL_N` registers use this shape.
- `RESERVED_*__SHIFT` definitions mark reserved bit ranges and are useful when generated mask companions exist, but driver logic should not intentionally program reserved bits.

Representative field groups:

- RX skip/startup controls: `SKIP_RX_*_STARTUP_CAL`, `SKIP_RX_*_STARTUP_ADAPT`, `SKIP_RX_*_CONT_CAL`, `SKIP_RX_*_CONT_ADAPT`, `SKIP_RX_MARGINING`.
- TX algorithm controls: `SKIP_TX_DCC_CAL_STARTUP`, `SKIP_TX_DCC_RANGE_CAL_STARTUP`, `SKIP_TX_DCC_CAL_RATE`, `SKIP_TX_DCC_RANGE_CAL_RATE`, and continuous `SKIP_TX_DCC_CAL_CONT`.
- TX fast flags: `FAST_SUP`, `FAST_TX_CMN_MODE`, `FAST_TX_RXDET`, `FAST_TX_STARTUP_CAL`, `FAST_TX_PWRUP`.
- TX DCC/MPLL storage: `MPLLA`/`MPLLB` `DCC_CTRL_RANGE_BANK_N`, `DCC_FULL_BANK_N`, `DCC_HALF_BANK_N`, and `CAL_DONE_BANK_N` fields.
- RX calibration/adaptation storage: `RX_CAL_DONE_BANK_N`, `RX_ADAPT_DONE_BANK_N`, `RX_DCC_*_BANK_N`, `RX_IQ_CAL_BANK_N`, `RX_ADPT_*_BANK_N`, and DFE tap offset/valid banks.
- RX signal/control: `RX_OVRD_IN_0`, `RX_OVRD_OUT_0`, `RX_PMA_OVRD_OUT_0`, `RX_IN_0`, `RX_OUT_0`, `RX_SIGDET_EN_MASK_CTL`, and `RX_SIGDET_FILT_CTL`.

## Control Flow

This chunk has no local control flow. Runtime control flow is indirect:

1. AMD display-resource code includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. Register helper macros in AMD display services use token-pasted names like `REG__FIELD__SHIFT` and corresponding masks to encode or decode register fields.
3. Higher-level link, PHY, stream encoder, and resource logic performs MMIO reads/writes through the AMD DC register access layer.

Within this file slice, the ordering is hardware-register-table order: lane-3 FSM fields, then repeated `RAWLANEAON` lane blocks. No macro expands to executable statements.

## State And Persistence

The header itself is stateless and contributes no persistence. The state represented by these macros lives in hardware registers:

- Calibration skip bits and fast flags can change how PHY firmware/hardware sequences execute during lane startup, rate changes, recovery, and continuous adaptation.
- Banked calibration and adaptation fields hold hardware or firmware-produced values such as DCC codes, VDAC/IDAC offsets, IQ values, DFE tap offsets, and completion flags.
- Override fields can force TX/RX disable, termination, signal-detect, VREF, PMA termination, or lane transceiver mode values while their paired override-enable bits are set.
- Status fields such as calibration done, adaptation done, signal-detect outputs, and input mirrors are volatile hardware observations rather than kernel-owned durable state.

Any persistence across modesets, hotplug, suspend/resume, or link retraining depends on the surrounding AMDGPU/DC code reprogramming or reading these hardware registers, not on this header.

## Dependencies And Integration Points

Primary dependencies:

- Companion generated address and mask headers, especially `dpcs_4_2_3_offset.h` and the mask definitions in this same `dpcs_4_2_3_sh_mask.h`.
- AMD display register helper macros that expect the `REG__FIELD__SHIFT` naming form.
- DCN 3.1.6 resource code: `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes this DPCS header alongside `dcn_3_1_6_*` register headers.
- Hardware programming paths in AMDGPU display/DC that access DPCS/PHY registers through MMIO or indirect CR-address/data mechanisms.

The same register families also appear in generated DCN headers, showing that these definitions are part of the broader generated ASIC register-description set. This chunk is not Ceph-specific despite living under the repository's imported `sources/distributed-fs/ceph-client` tree; it belongs to the Linux AMDGPU display driver source snapshot.

## Risks

- Bit-shift drift is the main risk. If these generated constants do not match the actual ASIC register specification, driver code may write the wrong bit field and destabilize link training, calibration, signal detection, or lane power sequencing.
- Lane-copy mistakes are easy to miss because `RAWLANEAON0`, `1`, `2`, and `3` blocks are highly repetitive. A typo in a lane number or bank number would compile but target the wrong generated symbol or fail only on specific lane configurations.
- Reserved fields should not be programmed as feature bits. Their presence is for generated completeness and mask construction, not for driver policy.
- Override-enable fields are hazardous: setting an override value without the intended enable bit, or leaving an override enabled after debug/recovery, can force persistent bad PHY behavior until the register is restored or hardware reset.
- This chunk includes only `__SHIFT` definitions for the selected lines. Callers generally also need matching masks and offsets; using shifts without masks can corrupt adjacent fields.
- The file is generated. Manual edits are likely to be overwritten and should be avoided unless the register generator/source specification is being repaired.

## Test Signals

Useful validation signals for code relying on this chunk:

- Build coverage for `dcn316_resource.c` and AMDGPU display code that includes `dpcs_4_2_3_sh_mask.h`; missing or renamed macros should fail at compile time.
- Register-table consistency checks comparing each `__SHIFT` against its matching `*_MASK` definition in the same generated header, where present.
- Hardware display/link tests across all physical lanes: hotplug, modeset, DisplayPort link training, link retraining, suspend/resume, and multi-monitor configurations.
- Debugfs or trace-based inspection of PHY/DPCS registers during link bring-up to confirm calibration done/adaptation done bits transition as expected and override bits are not left asserted unintentionally.
- Regression tests around marginal links or high-rate modes are especially relevant because this range contains DCC, CDR, signal-detect, IQ, DFE, CTLE, VGA, ATT, and TX equalization threshold fields.
