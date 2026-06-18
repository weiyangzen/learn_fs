# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 98890-101311

## Scope

This chunk is part of AMDGPU's generated NBIO 6.1 register bitfield header. It contains C preprocessor constants for register-field shifts and masks, not executable code. The covered range starts in the `DWC_E12MP_PHY_X4_NS_X4_2_RAWLANE1` digital PHY register definitions, fully covers equivalent `RAWLANE2` and `RAWLANE3` lane definitions, and begins the shared `DWC_E12MP_PHY_X4_NS_X4_2_SUPX` supervisor/PLL register block.

The file is consumed by other AMDGPU NBIO/PCIe code through register access helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and field helpers that combine `REG`/`FIELD` names with `__SHIFT` and `__MASK` definitions. The nearby source search shows related PCIe link-control masks are used in ASIC setup, ASPM, link-speed, and link-width paths under `drivers/gpu/drm/amd/amdgpu` and `drivers/gpu/drm/amd/pm`.

## Purpose

The chunk defines bit encodings for Synopsys/DWC E12MP PCIe PHY lane and supervisor registers inside NBIO 6.1. These constants let driver code read, modify, and test specific PHY fields without hard-coding numeric bit positions. The fields model low-level PCIe PHY behavior: RX/TX adaptation, equalization, DFE/AFE calibration values, reset and interrupt handshakes, PCS/PMA lane interface overrides, lane FSM state, reference clock controls, MPLLA/MPLLB controls, rtune controls, and PLL status.

Because this is a hardware-description header, its correctness is coupled to the ASIC register specification. The kernel driver does not persist data here; the constants describe hardware state that lives in memory-mapped registers.

## Important Definitions

The chunk follows the generated naming convention:

- `DWC_E12MP_PHY_X4_NS_X4_2_<block>_<register>__<field>__SHIFT` gives the field's least-significant bit.
- `DWC_E12MP_PHY_X4_NS_X4_2_<block>_<register>__<field>_MASK` gives the field mask.
- `RAWLANE1`, `RAWLANE2`, and `RAWLANE3` identify per-lane PHY register windows.
- `SUPX` identifies shared supervisor and PLL register windows for the x4 PHY instance.

Major register groups in the covered lines:

- `RAWLANE1_DIG_FSM_*` tail: includes `FAST_RX_VCO_CAL` masks carried over from the previous chunk and `CMNCAL_STATUS` with `CMNCAL_INIT` and `CMNCAL_DONE`.
- `RAWLANE{1,2,3}_DIG_AON_*`: always-on lane calibration and adaptation registers. These include AFE IDAC offsets (`AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `AFE_VGA1_IDAC_OFST`), DFE summer/phase/data/bypass/error offsets for even/odd paths, RX phase adjust mapping, IQ phase adjust, MPLLA/MPLLB coarse tune readouts, rtune values, power-up done flags, RX adaptation values for ATT/VGA/CTLE/DFE taps 1-5, RX adaptation done, fast calibration flags, slicer controls, lane common calibration status, and generic `ADPT_CTL_0` through `ADPT_CTL_7` words.
- `RAWLANE{1,2,3}_DIG_IRQ_CTL_*`: lane interrupt request, interrupt clear, and interrupt mask fields for reset return, RX reset, RX request, RX rate, RX pstate, RX adapt request, and RX adapt disable events.
- `RAWLANE{1,2,3}_DIG_PCS_XF_*`: PCS transfer/interface controls and status for TX/RX override inputs and outputs, PCS inputs and outputs, RX adapt acknowledge, RX adapt figure-of-merit, directed TX pre/main/post values, and lane number. For lane 1 the PCS group is mostly in the preceding chunk; lanes 2 and 3 are fully represented here.
- `RAWLANE{1,2,3}_DIG_FSM_*`: lane FSM override, memory address monitor, status monitor, fast RX/TX calibration controls, and common calibration status. These fields include jump address/enable, command start, override enable, state, command ready, ALU flags, wait-counter state, and read/write mask disabled indicators.
- `RAWLANE{1,2,3}_DIG_PMA_XF_*`: PMA transfer/interface override and PMA input registers for lane, supervisor, TX, RX, and lane rtune control.
- `RAWLANE{1,2,3}_DIG_TX_CTL_*` and `RAWLANE{1,2,3}_DIG_RX_CTL_*`: TX FSM/clock controls, RX FSM control, LOS mask control, RX data-enable override control, and continuous status words for offset cancellation and adaptation.
- `SUPX_DIG_*`: shared supervisor registers beginning with `IDCODE_LO`/`IDCODE_HI`, reference-clock overrides, MPLLA/MPLLB override inputs, supervisor and level override inputs/outputs, ASIC-side MPLLA/MPLLB inputs, aggregate ASIC input bits, level inputs, analog override outputs, rtune override output, RX termination override output, analog status, and the start of MPLLA power-control calibration/override/status definitions.

Representative fields carry hardware semantics:

- Calibration/status: `CMNCAL_INIT`, `CMNCAL_DONE`, `LANE_CMNCAL_INIT`, `LANE_CMNCAL_DONE`, `INIT_PWRUP_DONE`, `RX_ADAPT_DONE`, `FSM_STATE`, `MPLL_CAL_RDY`, `CHKFRQ_DONE`.
- Fast training/calibration: `FAST_RX_STARTUP_CAL`, `FAST_RX_ADAPT`, `FAST_RX_AFE_CAL`, `FAST_RX_DFE_CAL`, `FAST_RX_BYPASS_CAL`, `FAST_RX_REFLVL_CAL`, `FAST_RX_IQ_CAL`, `FAST_RX_PWRUP`, `FAST_RX_VCO_WAIT`, `FAST_RX_VCO_CAL`, `FAST_TX_CMN_MODE`, `FAST_TX_RXDET`.
- RX equalization/adaptation: `ATT_ADPT_VAL`, `VGA_ADPT_VAL`, `CTLE_BOOST_ADPT_VAL`, `CTLE_POLE_ADPT_VAL`, `DFE_TAP*_ADPT_VAL`, `RX_ADAPT_FOM`, directed TX pre/main/post fields.
- Interface overrides: `*_OVRD_IN`, `*_OVRD_OUT`, `OVRD_SEL`, `PHY_RESET`, `REF_CLK_EN`, `REF_USE_PAD`, `MPLLA_*`, `MPLLB_*`, `RTUNE_*`, and RX/TX PMA/PCS handoff fields.

## Control Flow

There is no runtime control flow in this header. The effective control flow is in driver code that includes this generated file:

1. Driver code reads a 16-bit or 32-bit PHY/NBIO register through the ASIC register access layer.
2. It extracts a field with the matching `__MASK` and `__SHIFT`.
3. It modifies the field by clearing the mask and ORing a shifted value.
4. It writes the resulting register value back to hardware, or polls status masks until hardware clears/sets a bit.

For the fields in this chunk, likely flows include polling calibration completion (`*_DONE`), driving override paths (`OVRD_SEL`, `*_OVRD_*`), reacting to lane IRQ status/clear bits, and interpreting RX adaptation/FSM status during PCIe link training or low-level diagnostics. The lane 2 and lane 3 definitions mirror lane 1 so driver code can apply the same logical flow to each lane register aperture.

## State And Persistence

The constants are compile-time-only and have no memory, locking, allocation, or persistence behavior. The state they describe is hardware state:

- Per-lane transient state: RX adaptation outputs, DFE/AFE calibration results, power-up completion, lane FSM state, IRQ latch/clear state, PMA/PCS interface status.
- Shared PHY state: ID code, reference clock selection, PLL controls/status, analog rtune and RX termination override/status.
- Strap/firmware influence: Some fields are likely initialized by straps, firmware, or earlier boot stages before the Linux driver observes or overrides them.

Persistence across suspend/resume, BACO, GPU reset, or PCIe link retraining depends on the hardware domain and the AMDGPU reset/resume path that reapplies register programming. This header only supplies the bit encodings for those paths.

## Dependencies And Integration Points

Direct dependencies are the C preprocessor and the generated AMD register naming scheme. Functional dependencies are the AMDGPU register access stack and ASIC-specific include ordering:

- Register address headers provide `reg*`, `mm*`, `ix*`, or `smn*` addresses; this chunk provides field masks/shifts.
- `amdgpu` NBIO/PCIe code uses these masks to configure link power management, training, speed/width, reset, and diagnostic handling.
- `pm` and SMU code reads related link width and speed fields to report or manage PCIe performance state.
- The field names must match helper macro conventions such as `REG_GET_FIELD` and `REG_SET_FIELD` when those helpers are used.

The chunk is source-tree-aligned with `drivers/gpu/drm/amd/include/asic_reg/nbio`, so merge/reconciliation should combine it with the other chunks of the same header rather than treating it as a standalone module.

## Risks

- Mask/shift drift from the hardware spec can silently corrupt register programming. A one-bit error in these low-level masks can break link training, PHY calibration, power management, or interrupt handling.
- The repeated lane definitions are easy to edit inconsistently. Lane 2 and lane 3 should remain structurally aligned with lane 1 unless the hardware spec intentionally differs.
- Reserved fields are explicitly defined with masks. Driver code should avoid writing nonzero values to reserved fields unless the hardware specification requires a documented sequence.
- Override fields such as `OVRD_SEL`, `PHY_RESET`, `MPLLA_*`, `MPLLB_*`, and PMA/PCS override bits can put hardware into nonstandard paths; incorrect writes can hang link training or require a device reset.
- Status and clear semantics are hardware-specific. Fields named `*_IRQ_CLR` may be write-one-to-clear or otherwise edge-sensitive; using generic read-modify-write logic without checking semantics can lose events.
- This file is generated and very large. Manual edits are high risk because formatting-only or partial regeneration differences can obscure real register changes during review.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware smoke testing:

- Build the AMDGPU driver with NBIO 6.1 support enabled to catch missing or misspelled macros and helper-name mismatches.
- Run static searches for lane symmetry across `RAWLANE1`, `RAWLANE2`, and `RAWLANE3`; repeated register groups should have matching fields and masks unless a spec exception exists.
- Compare generated output against the authoritative ASIC register database for this NBIO version.
- Exercise PCIe link bring-up, suspend/resume, GPU reset, ASPM, and link speed/width reporting on NBIO 6.1 hardware.
- Check kernel logs for PCIe link-training failures, AER errors, GPU reset storms, or AMDGPU timeout messages after changes touching these masks.
- For diagnostics paths, verify polling of `*_DONE`, `FSM_STATUS_MON`, `RX_ADAPT_DONE`, `MPLL_CAL_RDY`, and IRQ clear/mask fields behaves as expected on real hardware.
