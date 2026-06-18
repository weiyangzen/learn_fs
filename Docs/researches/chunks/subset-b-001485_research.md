# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_sh_mask.h

Chunk: `subset-b-001485`
Covered source range: lines 8564-11496 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_sh_mask.h`

## Purpose

This chunk is the final portion of AMD's generated BIF 5.0 register field mask header. It contains C preprocessor constants for bit masks and shift counts used by low-level AMDGPU and PowerPlay code when composing, extracting, or polling fields in BIF, PIF, PCIe port, PCIe link-control, MSI-X, RFE reset/power, and impedance-calibration registers.

The range is not executable code. It defines 2,931 `#define` lines and closes the header with `#endif /* BIF_5_0_SH_MASK_H */`. It pairs with address definitions in `bif_5_0_d.h`, including indexed PIF/PCIE port registers such as `ixPB0_PIF_CTRL`, `ixPCIEP_PORT_CNTL`, and `ixPCIE_LC_SPEED_CNTL`, and MMIO registers such as `mmPCIEMSIX_VECT0_ADDR_LO` and `mmBIF_RFE_SNOOP_REG`.

The covered range includes:

- the tail of `PB1_TX_LANE14_*` and full `PB1_TX_LANE15_*` TX lane control/status macros;
- duplicated `PB0_PIF_*` and `PB1_PIF_*` scratch, debug, strap, PLL/power, RX/TX, lane override, command bus, and BIF command status fields;
- `PCIEP_*` port, debug, SR-IOV, strap, hot-plug, error-injection, and scratch fields;
- `PCIE_TX_*`, `PCIE_RX_*`, flow-control, credit, sequence, replay, requester-id, vendor-specific, and error-control fields;
- `PCIE_LC_*` link-controller state, training, width, speed, equalization, CDR, bandwidth-change, and previous-state fields;
- MSI-X table fields for vectors 0-3 and the pending-bit array;
- BIF RFE snoop, warm reset, soft reset, client/master reset trigger, power-down, timeout, MM config, and impedance calibration fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or normal exported symbols in this chunk. The API surface is the generated macro namespace:

- `<REGISTER>__<FIELD>_MASK` isolates or updates a field in a 32-bit hardware register.
- `<REGISTER>__<FIELD>__SHIFT` gives the corresponding right-shift count for extracting or positioning the field.

Important macro families in the range:

- `PB1_TX_LANE14_OVRD_REG0`, `PB1_TX_LANE14_SCI_STAT_OVRD_REG0`, `PB1_TX_LANE15_CTRL_REG0`, `PB1_TX_LANE15_OVRD_REG0`, and `PB1_TX_LANE15_SCI_STAT_OVRD_REG0`: per-lane TX clock/data/power/frontend override controls, PRBS/debug controls, and SCI status fields such as TX power, margin, de-emphasis, coefficient ID, and coefficient value.
- `PB0_PIF_*` and `PB1_PIF_*`: two physical-bus-interface instances with parallel field layouts. These cover PIF scratch/debug, strap interpretation, PLL power-down/status/votes, TX/RX power states for S2/speed-change/off/degraded/unused/init/PLL-off states, L1/unused gating, PHY status delays, electrical-idle detection, CDR extension, RX-detect override, lane-width overrides, command bus scheduling, lane disables, and per-lane override enables/values for lanes 0-7 in this chunk.
- `PB[01]_PIF_BIF_CMD_STATUS`: per-lane `TXPHYSTATUS`, `RXPHYSTATUS`, `BPHY_CORE_TX_RDY`, and `BPHY_CORE_RX_RDY` status bits for lanes 0-7.
- `PCIEP_PORT_CNTL`, `PCIE_TX_CNTL`, `PCIE_RX_CNTL`, and `PCIE_RX_CNTL3`: PCIe port behavior, transaction-layer transmit/receive controls, error-ignore policy, completion timeout policy, TPH disable, PASID-related unsupported-request handling, and packet/flush/flow-control behavior.
- `PCIE_TX_CREDITS_*`, `PCIE_RX_CREDITS_*`, `PCIE_FC_*`, and `PCIE_TX_CREDITS_STATUS`: advertised, initialized, allocated, current, and error credit fields for posted, non-posted, and completion traffic.
- `PCIE_ERR_CNTL`, `PCIEP_ERROR_INJECT_PHYSICAL`, and `PCIEP_ERROR_INJECT_TRANSACTION`: AER/error-reporting controls and deliberate physical/transaction-layer error injection hooks for validation.
- `PCIE_LC_CNTL` through `PCIE_LC_CNTL6`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_BW_CHANGE_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PCIE_LC_CDR_CNTL`, `PCIE_LC_FORCE_COEFF`, `PCIE_LC_FORCE_EQ_REQ_COEFF`, `PCIE_LC_BEST_EQ_SETTINGS`, and `PCIE_LC_STATE0`-`PCIE_LC_STATE5`: link-controller state machine, ASPM/L0s/L1/L23 policy, link reset, training, speed changes, width negotiation, Gen2/Gen3 support, equalization, CDR, FTS count, bandwidth-change interrupts/status, lane reversal, and state-history fields.
- `PCIEP_STRAP_LC` and `PCIEP_STRAP_MISC`: strap-derived capabilities and defaults, including TS counts, skip interval, receiver-detect bypass, compliance, lane reversal, auto speed negotiation, lane negotiation, extended format, OBFF, and LTR support.
- `PCIEP_HPGI` and `PCIEP_HPGI_PRIVATE`: hot-plug/presence-detect enable and status fields routed to SMI/SCI.
- `PCIEMSIX_VECT[0-3]_*` and `PCIEMSIX_PBA`: MSI-X vector address, message data, vector mask bit, and pending bits.
- `BIF_RFE_*`, `BIF_PWDN_*`, and `BIF_RFE_MST_*_CMDSTATUS`: RFE snoop behavior, warm/soft/impedance reset enables, client/master reset triggers, block power-down commands/status, clock gate/setup/timeout timers, and master timeout status.
- `BIF_CC_RFE_IMP_OVERRIDECNTL` and `BIF_IMPCTL_*`: PLL RX/TX impedance override straps, sample period/setup/threshold controls, RX/TX pull-down/pull-up adjustment fields, lock/readback/comparator ambiguity status, calibration-done status, and continuous calibration period.

The range starts on `PB1_TX_LANE14_OVRD_REG0__TX_DRV_DATA_EN_OVRD_VAL_14__SHIFT`; its matching `_MASK` definition is immediately before the assigned range. A local mask/shift-pair check therefore reports this one expected `shift_only` boundary artifact. The remaining mask/shift pairs inside the assigned range are locally paired.

## Control Flow

This header has no runtime control flow. The only control-like structure in this chunk is the closing include-guard `#endif`.

Runtime control flow appears in consumers that use these macros for register programming. A typical driver sequence is:

1. Read a BIF/PIF/PCIe register through `RREG32`, `RREG32_PCIE_PORT`, indexed-register helpers, or PowerPlay table operations.
2. Clear one or more fields with `~<REGISTER>__<FIELD>_MASK`.
3. Shift a desired value by `<REGISTER>__<FIELD>__SHIFT`.
4. OR the shifted value into the register word.
5. Write the result back, or poll a status field until it changes.

The link-controller and PIF fields are commonly involved in state-machine sequencing: link-speed changes set force/disable/initiate bits and then poll current data rate or initiate bits; width negotiation and training inspect link-width/current-state fields; lane power and PHY-status handling inspect PIF status bits; reset/power paths set trigger bits and then wait for status/timeout fields.

## State And Persistence Behavior

The file itself has no mutable state and no persistence. It contributes numeric constants at compile time to translation units that include it.

The affected state is hardware state in memory-mapped or indexed registers. Writes using these masks may persist until overwritten by the driver, firmware, PCIe link retraining, hot reset, FLR, BACO/power transition, suspend/resume, or full device reset.

Stateful hardware areas represented in this chunk include:

- per-lane PIF override enables and override values for lane power, electrical idle, CDR enable, gang mode, link speed, coefficient selection, and training requests;
- link-controller status/history such as current data rate, negotiated width, link-speed-change status, bandwidth-change status, illegal/timed-out state status, and previous LTSSM state entries;
- error-control and error-injection fields that can change AER/reporting behavior or deliberately inject invalid physical/transaction-layer conditions;
- MSI-X vector message address/data/mask fields and pending bits;
- RFE reset/power-down commands and status bits;
- impedance calibration adjustment, lock, readback, ambiguity, and done fields.

Scratch registers such as `PB0_PIF_SCRATCH`, `PB1_PIF_SCRATCH`, and `PCIEP_SCRATCH` are explicitly general-purpose register state. Their retention rules are hardware-specific and are not encoded in the header.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The register address companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_d.h`

Known include sites in this tree include:

- `drivers/gpu/drm/amd/amdgpu/vi.c`
- `drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c`
- `drivers/gpu/drm/amd/amdgpu/gmc_v8_0.c`
- `drivers/gpu/drm/amd/amdgpu/mxgpu_vi.c`
- `drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c`
- `drivers/gpu/drm/amd/amdgpu/sdma_v3_0.c`
- PowerPlay/SMU and BACO paths such as `fiji_baco.c`, `polaris_baco.c`, `smu7_baco.c`, `tonga_baco.c`, `smu7_common.h`, and generation-specific SMU manager files.

Concrete consumers in nearby generation code show the expected use of `PCIE_LC_SPEED_CNTL` fields. For example, `amdgpu/cik.c`, `amdgpu/si.c`, and `pm/legacy-dpm/si_dpm.c` read `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE_MASK` and shift by `PCIE_LC_SPEED_CNTL__LC_CURRENT_DATA_RATE__SHIFT`; `cik.c` and `si.c` also program `LC_FORCE_EN_SW_SPEED_CHANGE`, `LC_FORCE_DIS_HW_SPEED_CHANGE`, `LC_FORCE_DIS_SW_SPEED_CHANGE`, and `LC_INITIATE_LINK_SPEED_CHANGE`. `bif_5_0_sh_mask.h` supplies the same-named BIF 5.0 layout for VI-era paths.

The macros integrate with AMDGPU register accessor conventions, PCIe-port indexed access, PowerPlay BACO command tables, reset/power-management code, SR-IOV virtualization support, interrupt/MSI-X setup, and hardware validation/debug tooling.

## Risks And Edge Cases

The major risk is silent hardware misprogramming. The compiler cannot prove that a mask belongs to the register being accessed, that the matching shift is used, or that a value fits in the field width.

Boundary risk is present in this chunk: the assigned range begins after the mask for `PB1_TX_LANE14_OVRD_REG0__TX_DRV_DATA_EN_OVRD_VAL_14`, so this chunk alone has one apparent shift without a local mask. The full header should be reconciled across adjacent chunks before file-level conclusions.

PB0 and PB1 register families are structurally similar but target distinct PIF instances. Accidentally using `PB0_*` fields with `PB1_*` register addresses, or vice versa, can compile cleanly and affect the wrong physical interface.

Lane-indexed macros are highly repetitive. Off-by-one lane mistakes in `LANE0`-`LANE7`, command-bus lane-disable bits, TX/RX PHY status bits, or coefficient fields are difficult to catch in review and may only appear as link training failures or degraded PCIe width/speed.

Several fields are disruptive when written incorrectly: link reset, LTSSM/training control, speed-change initiation, width negotiation, ASPM/L1/L23 behavior, receiver detect overrides, TX/RX power states, PLL power-down/votes, CDR/electrical-idle controls, RFE reset triggers, block power-down commands, MSI-X vector mask/address/data, and error-injection controls. Mistakes can cause PCIe link loss, failed resume, missed interrupts, corrupted error handling, or a GPU reset requirement.

Register layouts are generation-specific. Some same-named fields have different masks/shifts in later NBIO headers or locally defined newer SMU code. Mixing BIF 5.0 constants with another ASIC generation is unsafe even when macro names look familiar.

Many fields are status, strap, or write-one/control bits with hardware-defined side effects that are not documented in this header. Callers must rely on the ASIC register spec and existing sequencing code, not only on the mask names.

## Test Signals

Useful validation signals are mostly generated-header consistency, build coverage, and hardware behavior:

- Compile all VI-era AMDGPU and PowerPlay paths that include `bif_5_0_sh_mask.h`.
- Run generated-header checks that each `_MASK` has a matching `__SHIFT`, allowing for the known chunk-boundary artifact in this isolated range.
- Check that register prefixes in this chunk map to address macros in `bif_5_0_d.h`, especially `PB[01]_PIF_*`, `PCIEP_*`, `PCIE_*`, `PCIEMSIX_*`, and `BIF_RFE_*`.
- Exercise PCIe link-speed reporting and speed changes on supported hardware, validating `PCIE_LC_SPEED_CNTL` current data rate, target override, force, status, and initiate bits.
- Exercise link width negotiation, lane reversal, ASPM/L0s/L1/L23 transitions, hot reset, FLR, suspend/resume, and BACO/low-power transitions to cover `PCIE_LC_*`, `PB[01]_PIF_*`, and RFE reset/power fields.
- Validate interrupt delivery with MSI-X enabled, including vector masking/unmasking and pending-bit behavior for vectors 0-3.
- Run SR-IOV/MxGPU smoke tests where applicable, especially VF mapping/save fields, function routing, reset behavior, and MSI-X behavior under virtualization.
- Use hardware debug or lab tests for PIF lane overrides, RX detect, electrical idle, CDR, TX coefficients, error-injection fields, and impedance calibration, because these fields are too hardware-specific for ordinary unit tests.
- Compare regenerated constants against the authoritative ASIC register database before accepting any changes to this header.
