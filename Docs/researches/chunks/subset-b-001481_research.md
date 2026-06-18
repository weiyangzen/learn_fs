# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h

Chunk: `subset-b-001481`
Covered source range: lines 8505-10252 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_sh_mask.h`

## Purpose

This chunk is the final portion of AMD's generated BIF 4.1 register field mask header. It is not executable driver logic; it supplies C preprocessor constants for extracting and updating bitfields in BIF/PIF/RFE registers on ASICs that use the BIF 4.1 register layout.

The header pairs with `bif_4_1_d.h`, which defines the corresponding register addresses. In this chunk the paired address macros include indexed PIF PHY registers such as `ixPB0_PIF_PDNB_OVERRIDE_*`, `ixPB1_PIF_CNTL`, `ixPB1_PIF_SEQ_STATUS_*`, and MMIO registers such as `mmBIF_RFE_SOFTRST_CNTL`, `mmBIF_IMPCTL_RXCNTL`, `mmBIF_RESET_EN`, and `mmBIF_RESET_CNTL`.

The range starts in the middle of the `PB0_PIF_PDNB_OVERRIDE_3` field family, completes the remaining PB0 lane powerdown override and sequence-status definitions, defines the PB1 PIF control/status/powerdown/override families, and ends with BIF RFE, powerdown, impedance calibration, clock, link counter, reset, TX clock switch, BACO, and access-mode field definitions. The final line closes the `BIF_4_1_SH_MASK_H` include guard.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or runtime objects in this chunk. The API surface is entirely generated macro constants:

- `<REGISTER>__<FIELD>_MASK` isolates or clears a field in a 32-bit register value.
- `<REGISTER>__<FIELD>__SHIFT` gives the bit position used when packing or unpacking a field.
- `PB0_*` and `PB1_*` prefixes distinguish the two physical bus interface instances.
- Register names align with address macros in `bif_4_1_d.h`, while this file supplies the field-level masks and shifts.

Major register families in this chunk:

- `PB0_PIF_PDNB_OVERRIDE_3` through `PB0_PIF_PDNB_OVERRIDE_15`: per-lane TX/RX powerdown, RX enable, TX power, and RX power override enable/value fields for PB0 lanes. The chunk begins after the first `TX_PDNB_OVERRIDE_EN_3` pair, so `PB0_PIF_PDNB_OVERRIDE_3` is incomplete in this work item.
- `PB0_PIF_SEQ_STATUS_0` through `PB0_PIF_SEQ_STATUS_15`: per-lane sequence status bits for calibration, RX detect, L1/L0s/L0 entry/exit, speed change, and 3-bit sequence phase.
- `PB1_PIF_SCRATCH`, `PB1_PIF_HW_DEBUG`, and `PB1_PIF_PRG0` through `PB1_PIF_PRG7`: scratch/debug bits and programmable timing fields for RX detect sampling, PLL ramp-up, service step delays, speed-change delays, and LS2 exit timing.
- `PB1_PIF_CNTL` and `PB1_PIF_CNTL2`: PIF-level controls for serial configuration, FIFO reset modes, PHY command modes, electrical idle detection, PLL binding, calibration behavior, LS2 exit timing, RX enable gating, RX detect overrides for lanes 0-15, staggering, PLL1 always-on, and long speed-change delays.
- `PB1_PIF_PAIRING`: lane-pairing and width grouping fields for x2, x4, x8, x16, and multi-PIF configurations.
- `PB1_PIF_PWRDOWN_0` through `PB1_PIF_PWRDOWN_3`: per-group TX/RX/PLL power states, TX 2.5 clock gating, PLL ramp-up time, and PLL power override fields.
- `PB1_PIF_TXPHYSTATUS`, `PB1_PIF_SC_CTL`, and `PB1_PIF_SC_CTL2`: per-lane TX PHY status, sequence-control phase/resume bits, and serial configuration per-lane disable bits.
- `PB1_PIF_PDNB_OVERRIDE_0` through `PB1_PIF_PDNB_OVERRIDE_15` and `PB1_PIF_SEQ_STATUS_0` through `PB1_PIF_SEQ_STATUS_15`: PB1 equivalents of the lane power override and sequence-status fields.
- `BIF_RFE_*`: register front-end snoop, warm reset, soft reset, impedance reset, client/master reset trigger, master command status, timeout status, and MM-to-config controls.
- `BIF_PWDN_COMMAND` and `BIF_PWDN_STATUS`: powerdown command/status bits for BU, RWREG/RFEWDBIF, and BX blocks.
- `BIF_CC_RFE_IMP_OVERRIDECNTL`, `BIF_IMPCTL_SMPLCNTL`, `BIF_IMPCTL_RXCNTL`, `BIF_IMPCTL_TXCNTL_pd`, `BIF_IMPCTL_TXCNTL_pu`, and `BIF_IMPCTL_CONTINUOUS_CALIBRATION_PERIOD`: impedance override, sampling, RX/TX adjustment, lock/readback, comparator ambiguity, calibration done, and continuous calibration period fields.
- `BIF_CLOCKS_BITS`, `BIF_LNCNT_RESET`, `LNCNT_CONTROL`, `NEW_REFCLKB_TIMER`, `NEW_REFCLKB_TIMER_1`, `BIF_CLK_PDWN_DELAY_TIMER`, and `BIF_PIF_TXCLK_SWITCH_TIMER`: reference-clock, link-counter, PHY PLL powerdown, clock powerdown delay, and PLL switch timer fields.
- `BIF_RESET_EN` and `BIF_RESET_CNTL`: reset source enables, pulse widths, delay selectors, PIF reset/strap controls, BIF core reset, function-level reset enables, reset-done, link-train, strap-valid, and warm-reset recapture controls.
- `BIF_BACO_MSIC` and `BIF_RFE_CNTL_MISC`: BACO clock/link reset selection and RFE access-mode adaptation for PIF0, PIF1, power registers, and PCIe core.

## Control Flow

The chunk has no runtime control flow. The only compile-time structure is the closing `#endif` for the file include guard.

Runtime control flow appears in callers that use these constants in normal register read/modify/write sequences. A typical pattern is:

1. read a BIF or PIF register with an MMIO or indexed-register helper;
2. clear a field with `value &= ~REGISTER__FIELD_MASK`;
3. optionally set a new value with `value |= encoded << REGISTER__FIELD__SHIFT`;
4. write the register back;
5. poll a status field until it reflects the requested hardware transition.

The source tree shows BIF 4.1 definitions included by CIK-era amdgpu and PowerPlay code, including `amdgpu/cik.c`, `amdgpu/cik_ih.c`, `amdgpu/cik_sdma.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/gfx_v7_0.c`, `pm/powerplay/hwmgr/ci_baco.c`, and `pm/powerplay/smumgr/ci_smumgr.c`. The same naming pattern is used by code that adjusts PIF power and timing fields; for example, related SI/CIK paths clear `PB*_PIF_PWRDOWN_*__PLL_RAMP_UP_TIME_*_MASK` and update `PB*_PIF_CNTL__LS2_EXIT_TIME__SHIFT` through PIF PHY access helpers.

## State And Persistence Behavior

This header has no mutable software state and performs no persistence itself. Its values are compiled into translation units that include it.

The affected state is hardware register state. Writes made with these masks can alter PCIe/BIF behavior until the register is changed again, the GPU is reset, the PCIe link is retrained, BACO or suspend/resume changes the power island state, or firmware/hardware reinitializes the block. This is especially relevant for:

- lane powerdown and RX/TX enable override fields, which can force per-lane electrical behavior;
- PIF sequence-control and status fields, which reflect or influence link training and low-power transitions;
- RFE soft/warm reset and master/client reset triggers, which can reset internal register-front-end clients or masters;
- BIF powerdown command/status fields, which coordinate block-level power gating;
- impedance calibration controls, which tune RX and TX electrical impedance and expose lock/readback status;
- reset enable/control fields, which determine how hot reset, link disable/down reset, driver reset, FLR, PIF reset, strap valid, and BIF core reset propagate.

Scratch and status fields may be observed across driver/firmware handoff or diagnostics depending on hardware retention rules, but this header does not define those rules.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The constants are meaningful only when used with the matching BIF 4.1 register address definitions in:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_4_1_d.h`
- adjacent generation-specific headers only when a caller intentionally targets that generation's register layout

Important address pairings from `bif_4_1_d.h` include:

- `ixPB0_PIF_PDNB_OVERRIDE_3` through `ixPB0_PIF_PDNB_OVERRIDE_15` and `ixPB0_PIF_SEQ_STATUS_0` through `ixPB0_PIF_SEQ_STATUS_15`;
- `ixPB1_PIF_SCRATCH`, `ixPB1_PIF_CNTL`, `ixPB1_PIF_CNTL2`, `ixPB1_PIF_PAIRING`, `ixPB1_PIF_PWRDOWN_*`, `ixPB1_PIF_SC_CTL*`, `ixPB1_PIF_PDNB_OVERRIDE_*`, and `ixPB1_PIF_SEQ_STATUS_*`;
- `mmBIF_RFE_SNOOP_REG`, `mmBIF_RFE_WARMRST_CNTL`, `mmBIF_RFE_SOFTRST_CNTL`, `mmBIF_PWDN_COMMAND`, `mmBIF_PWDN_STATUS`, `mmBIF_RFE_MMCFG_CNTL`;
- `mmBIF_IMPCTL_SMPLCNTL`, `mmBIF_IMPCTL_RXCNTL`, `mmBIF_IMPCTL_TXCNTL_pd`, `mmBIF_IMPCTL_TXCNTL_pu`, and `mmBIF_IMPCTL_CONTINUOUS_CALIBRATION_PERIOD`;
- `mmBIF_RESET_EN`, `mmBIF_RESET_CNTL`, `mmBIF_BACO_MSIC`, `mmBIF_CLOCKS_BITS`, `mmNEW_REFCLKB_TIMER`, and related clock/link-counter registers.

The included users are low-level GPU initialization, interrupt, memory-controller, graphics, SDMA, display, ATOM BIOS, BACO, and SMU management code. These consumers typically access registers through AMDGPU helper macros rather than through typed wrappers, so the register prefix and field macro names are the primary contract.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped numeric macros; the compiler cannot prove that `PB1_PIF_CNTL__LS2_EXIT_TIME_MASK` is used only with `ixPB1_PIF_CNTL`, or that a PB0 field is not accidentally applied to a PB1 register.

The assigned range starts in the middle of `PB0_PIF_PDNB_OVERRIDE_3`. The first pair for `TX_PDNB_OVERRIDE_EN_3` is outside the work item, while the rest of the lane-3 override value and RX/TX power fields are inside it. Final file-level analysis must merge this with the preceding chunk before treating PB0 lane 3 as complete.

Lane-indexed definitions are repetitive and easy to misuse. PB0/PB1, lane 0-15, and grouped powerdown registers all compile cleanly even if a caller selects the wrong lane, wrong PIF instance, or wrong group register.

Many fields control disruptive link and device behavior. Bad writes to PIF powerdown overrides, RX detect overrides, sequence-control resume bits, PLL timers, RFE reset triggers, BIF powerdown commands, impedance force/reset fields, or `BIF_RESET_EN` can hang PCIe access, break link retraining, lose MMIO/config reachability, or require a full GPU reset.

Mask/shift pairs must remain synchronized. Errors are particularly dangerous for multi-bit fields such as lane pairing, power states, ramp-up timers, reset pulse widths, function reset delay selectors, impedance thresholds/readbacks, and RFE timeout timers.

Generation drift is a real concern. BIF 5.0 contains closely related names but not identical fields, such as additional RFE master/powerdown fields in some places. Code should not mix BIF 4.1 masks with another generation's `*_d.h` address header unless the compatibility is explicitly known.

## Test Signals

Useful validation signals are mostly build, static consistency, and hardware behavior checks:

- Compile all translation units that include `bif_4_1_sh_mask.h`, especially CIK amdgpu, GMC/GFX/SDMA, PowerPlay BACO, and SMU manager paths.
- Run a generated-header consistency check that every `_MASK` has a matching `__SHIFT` and that both use the same register/field prefix. This range has an intentional boundary exception for the start of `PB0_PIF_PDNB_OVERRIDE_3`.
- Cross-check field register prefixes against `bif_4_1_d.h` address macros so every `PB1_PIF_*` and `BIF_*` field family maps to a corresponding address definition.
- Exercise PCIe link bring-up, lane width changes, speed changes, ASPM/L0s/L1/LS2 transitions, and suspend/resume on BIF 4.1 hardware to cover PIF control, sequence status, powerdown, PLL timer, and reset fields.
- Validate BACO entry/exit and clock/reference-clock behavior where `BIF_BACO_MSIC`, `BIF_CLOCKS_BITS`, `NEW_REFCLKB_TIMER*`, and reset controls may be involved.
- Test FLR, hot reset, link-disable reset, link-down reset, driver reset, and BIF core reset paths to catch incorrect `BIF_RESET_EN` or `BIF_RESET_CNTL` masks.
- Use controlled lab or bring-up tests for impedance calibration fields: force/suspend/reset behavior, `RX_IMP_LOCKED`, `TX_IMP_LOCKED_*`, readback selectors, comparator ambiguity, and `CAL_DONE`.
- For any regenerated version of this header, compare macro names and values against the authoritative register database and perform representative readback/writeback tests on single-bit and multi-bit fields.
