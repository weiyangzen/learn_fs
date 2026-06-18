# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 36779-39243

## Scope

This chunk is a generated AMD NBIO 6.1 register shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, memory allocations, locks, reference counts, or direct hardware reads/writes in this range.

The assigned range starts in the tail of `BIF_CFG_DEV0_EPF0_VF15_1_DEVICE_CAP2`, covers the remaining PCIe capability, MSI/MSI-X, vendor-specific, Advanced Error Reporting, ATS, and ARI field masks for virtual function `VF15_1`, then moves into the `nbio_nbif_pciemsix_amdgfx_MSIXTDEC` and `MSIXPDEC` address blocks. It then covers a large `nbio_pcie_pswusp0_pciedir_p` PCIe port/link-control block, the start of the shared `nbio_pcie_pciedir` block, and ends at `PCIE_PERF_COUNT0_SLV_S_C_CLK__COUNTER0_MASK`. The following lines continue performance counter register definitions, so this chunk ends mid-family.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU hardware register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to expose bit positions and masks for NBIO 6.1 PCIe configuration, interrupt, link-control, error-diagnostic, sideband, and performance-monitoring registers. Each exported field is represented as generated macros:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset used to encode or extract a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used to isolate, clear, preserve, or set that field.

Consumers pair these masks with register offsets from `nbio_6_1_offset.h`, default/reset values from `nbio_6_1_default.h`, and AMDGPU register helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

## Important Macro Families

The opening `BIF_CFG_DEV0_EPF0_VF15_1_*` section finishes a virtual-function PCI configuration-space view. It includes Device Capability 2 and Device Control 2 fields for completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, end-to-end TLP prefixes, extended format, and TPH completer support. Link Capability 2, Link Control 2, and Link Status 2 cover supported/target link speeds, compliance entry, selectable de-emphasis, transmit margin, equalization phase status, and link equalization requests.

The same VF15 block defines reserved Slot Capability/Control/Status 2 masks, MSI capability header and message-control fields, MSI low/high address, data, mask, and pending fields, and 64-bit MSI data/mask/pending variants. The MSI-X capability fields define table size, function mask, MSI-X enable, table BIR/offset, and PBA BIR/offset.

The VF15 vendor-specific and AER fields cover enhanced-capability headers, vendor-specific scratch payloads, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, four header-log dwords, four TLP-prefix-log dwords, ATS enhanced capability/capability/control, and ARI enhanced capability/capability/control. AER fields include data-link, surprise-down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked, atomic-op egress blocked, and TLP-prefix blocked bits; correctable fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal error, and header-log overflow.

The `PCIEMSIX_VECT0` through `PCIEMSIX_VECT31` block defines the physical MSI-X table decode for AMD graphics. Every vector has low address, high address, message data, and control masks. Low address fields start at bit 2 (`MSG_ADDR_LO_MASK` is aligned to `0xFFFFFFFC`), high address and message data are full-width, and control exposes a single `MASK_BIT`. `PCIEMSIX_PBA` then provides 32 per-vector pending bits.

The `nbio_pcie_pswusp0_pciedir_p` block defines PCIe port-side controls. Important groups include `PCIEP_PORT_CNTL`, `PCIE_TX_CNTL`, requester ID, transmit sequencing/replay/ack latency, advertised and initial flow-control credits, credit status and thresholds, physical lane status, `PCIE_FC_*` flow-control monitors, `PSWUSP0_PCIE_ERR_CNTL`, `PSWUSP0_PCIE_RX_CNTL`, expected sequence number, RX vendor-specific controls, RX allocated credits, physical and transaction error injection, SR-IOV privilege control, NAK counter, and extensive link-controller registers.

The link-controller portion is the densest part of the chunk. `PCIE_LC_CNTL`, `PCIE_LC_TRAINING_CNTL`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_N_FTS_CNTL`, `PSWUSP0_PCIE_LC_SPEED_CNTL`, `PCIE_LC_STATE0` through `STATE5`, `PCIE_LINK_MANAGEMENT_CNTL2`, `PSWUSP0_PCIE_LC_CNTL2`, bandwidth-change controls, CDR/lane controls, `PCIE_LC_CNTL3` through `CNTL7`, equalization coefficient controls, best-equalization settings, link-management status/mask/control, strap registers, L1 PM substate controls, port order, and BCH ECC control describe link training, lane reversal and lane count, L0s/L1/L1 substates, recovery, speed changes, de-emphasis/equalization, quiesce/retrain behavior, power-down policy, error handling, and link-management notifications.

The `nbio_pcie_pciedir` block starts with shared PCIe controls and status: reserved/scratch registers, RX NAK counters, `PCIE_CNTL`, `PCIE_CONFIG_CNTL`, TX tracking address/control/status, bandwidth by unit ID, `PCIE_CNTL2`, `PCIE_RX_CNTL2`, TX attribute controls for function 0 and SWUS traffic, `PCIE_CI_CNTL`, bus control, additional link-controller state registers (`STATE6` through `STATE11`), LC status registers, write-protect control, captured RX/TX last TLP dwords, I2C register address/data, config control, PM control, port-order control, physical-layer control/status registers, RX advisory/drop/unsupported-request policy, SDP control, SWUS slave attribute overrides, and the beginning of PCIe performance counter controls for TXCLK, MST_R_CLK, MST_C_CLK, SLV_R_CLK, and SLV_S_C_CLK domains.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is the macro namespace in `nbio_6_1_sh_mask.h`.

Direct NBIO 6.1 include sites include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c` and PowerPlay aggregator headers such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. `nbio_v6_1.c` includes the matching default, offset, shift/mask, and SMN headers and uses these masks for NBIO setup, doorbell programming, interrupt setup, clock gating, HDP flush offsets, PCIe indirect access, ASPM/LTR programming, and register remapping. Related AMDGPU generations use the same macro names for similar link and performance-counter fields, so broad searches show cross-generation use of `PCIE_LC_CNTL__*`, `PSWUSP0_PCIE_LC_CNTL2__*`, and `PCIE_PERF_COUNT_CNTL__*`.

## Control Flow

This header has no executable control flow. Runtime behavior occurs in including driver code:

1. A driver path selects a register offset or SMN address from the generated offset headers or a local `smn*` constant.
2. It reads a PCIe/NBIO register through AMDGPU's register access layer.
3. It extracts a field using a generated mask/shift pair or updates a field with `REG_SET_FIELD`.
4. It writes the composed value back, decodes status, clears sticky status, programs interrupt table state, configures link power policy, triggers training/recovery behavior, or samples performance counters.

For this chunk, the most visible control-flow integration is PCIe link and power setup. In `nbio_v6_1_program_aspm()`, the driver clears `PCIE_LC_CNTL__LC_L1_INACTIVITY_MASK` and `PCIE_LC_CNTL__LC_L0S_INACTIVITY_MASK`, sets or clears `PCIE_LC_CNTL__LC_PMI_TO_L1_DIS_MASK`, updates `PCIE_LC_CNTL7`, `PCIE_LC_CNTL3`, `PSWUSP0_PCIE_LC_CNTL2`, and `PCIE_LC_CNTL6`, and optionally enables LTR when the PCI path supports it. This chunk provides several of the involved bit definitions, while adjacent chunks and local definitions provide the rest.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes hardware-backed and PCI configuration-space-backed state owned by NBIO, the PCIe link controller, the PCIe endpoint/port, firmware defaults, Linux PCI policy, and AMDGPU runtime code.

The represented state includes VF15 capability/control/status bits, interrupt message configuration, MSI-X vector table entries, MSI-X pending bits, AER masks/severities/status/logs, ATS and ARI capability/control fields, TX/RX sequence and credit accounting, link-training state, negotiated and target link properties, ASPM/L1 substate policy, equalization settings, error-injection controls, captured last-TLP diagnostics, sideband/SDP behavior, no-snoop/relaxed-ordering/IDO overrides, and performance counter selector/count state. Some fields are static capabilities, some are programmable controls, some are live hardware status, and some AER/status fields are likely sticky or clear-on-write in the underlying device. The masks alone do not encode reset defaults, read/write permissions, clear semantics, required delays, or ordering constraints.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` provides matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides matching reset/default values for many register families.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` provides related SMN addresses.
- AMDGPU register helper macros provide field extraction and read/modify/write mechanics.

Integration points include AMDGPU NBIO initialization and power-management code, Vega10/Vega12 PowerPlay include aggregation, Linux PCIe enumeration and capability scanning, SR-IOV/MxGPU virtual-function configuration exposure, MSI/MSI-X interrupt delivery, AER diagnostics, ATS/IOMMU behavior, ARI function numbering, ASPM/LTR policy, PCIe link training/recovery, error injection or debug tooling, and performance counter sampling.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line is already inside `BIF_CFG_DEV0_EPF0_VF15_1_DEVICE_CAP2`, and the last line stops before the complete performance-counter family ends.
- These are untyped preprocessor constants. A wrong mask, stale shift, or wrong register-family prefix can compile cleanly and still manipulate the wrong hardware bits.
- The VF15 PCI configuration names are highly repetitive relative to earlier VF blocks. Copy/generation drift can create subtle per-VF differences, and applying a `VF15_1` mask to a different VF offset may appear mathematically valid while targeting the wrong configuration image.
- MSI-X vector entries have interrupt-delivery side effects. Incorrect low-address alignment, message data, mask-bit, or PBA handling can cause lost, stuck, duplicated, or misrouted interrupts.
- AER fields are diagnostic and may be sticky or write-one-to-clear in hardware. Naive read/modify/write can erase failure evidence or unintentionally mask serious link/device errors.
- Link-controller fields affect PCIe interoperability. Bad values in ASPM, L1 substates, speed-change, lane-width, retrain, recovery, de-emphasis, equalization, power-down, or notification controls can cause link instability, hangs, enumeration failure, power regressions, or bandwidth loss.
- Error-injection registers should only be used by controlled diagnostics. Accidentally enabling physical or transaction error injection can create false hardware failures.
- TX/RX credit, sequence, replay, and NAK fields are protocol-sensitive. Incorrect manipulation can break PCIe transaction progress or hide flow-control problems.
- Attribute override fields for no-snoop, relaxed ordering, ID-based ordering, and sideband behavior interact with DMA ordering, cache coherency, and IOMMU isolation assumptions.
- Performance counter controls span several clock domains. Counter reset, shadow write, enable, selector, and upper-bit handling must be coordinated, or sampled data can be inconsistent.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware integration testing:

- Build AMDGPU with NBIO 6.1, Vega10/Vega12, ASPM, MSI/MSI-X, SR-IOV/MxGPU, and relevant debug options enabled. Missing or renamed macros should surface in include users and register helper call sites.
- Diff generated `nbio_6_1_sh_mask.h` against `nbio_6_1_offset.h` and `nbio_6_1_default.h` for the same register names to ensure offsets, defaults, masks, and address-block ordering stay synchronized.
- On NBIO 6.1 hardware, enumerate PCIe capabilities and SR-IOV virtual functions and verify VF15 configuration space exposes expected Device/Link Capability 2, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields.
- Run MSI-X interrupt stress with all 32 table entries where supported, checking vector masking/unmasking, pending-bit behavior, address/data programming, and interrupt routing.
- Exercise ASPM/LTR enable and disable flows, suspend/resume, runtime power transitions, link retraining, and speed changes while monitoring link speed, width, training state, equalization status, AER logs, and driver timeouts.
- Use AER injection or platform diagnostics where available to validate status, mask, severity, first-error pointer, header-log, and TLP-prefix-log behavior.
- Sample PCIe performance counters around known traffic patterns, verifying counter reset, enable, shadow write, event selector, and multi-clock-domain counter behavior.
- Run PCIe error-path and recovery tests that touch NAK counters, replay/sequence diagnostics, RX/TX last-TLP capture, and link-management status/mask/control registers.

## Chunk Notes

- Lines 36779-37176 finish `BIF_CFG_DEV0_EPF0_VF15_1` from Device Capability 2 through ARI Control.
- Lines 37177-37569 cover AMD graphics MSI-X table and PBA decode: 32 vectors plus PBA bits.
- Lines 37570-38673 cover `nbio_pcie_pswusp0_pciedir_p`, including TX/RX, credits, error injection, SR-IOV privilege, link controller, link-management, strap, L1 PM substate, and ECC masks.
- Lines 38674-39243 cover the start of `nbio_pcie_pciedir`, from shared PCIe controls through the beginning of performance counter registers.
