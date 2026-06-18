# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 141011-143502

## Scope

This chunk covers a generated section of AMD NBIO 7.2.0 shift/mask definitions for PCIe/BIF configuration-space registers. The slice begins in the tail of `BIF_CFG_DEV0_EPF5_1_LINK_STATUS2`, covers the remainder of the `EPF5_1` capability blocks, covers a complete `addressBlock: nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`, and ends in the early PCIe link-control portion of `addressBlock: nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`.

The chunk contains only preprocessor constants: no functions, structs, runtime control flow, allocation, locking, or persistence logic. Its purpose is to give driver code stable symbolic names for bit positions and masks when decoding or programming NBIO PCI configuration registers through the paired offset header and AMDGPU register-access helpers.

## Purpose

`nbio_7_2_0_sh_mask.h` is the bitfield companion to `nbio_7_2_0_offset.h`. The offset header names registers such as `regBIF_CFG_DEV0_EPF6_1_COMMAND`; this header names fields inside those registers, using the pattern:

- `BIF_CFG_DEV0_EPF*_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF*_1_<REGISTER>__<FIELD>_MASK`

The definitions in this chunk model PCI configuration-space fields for endpoint functions 5, 6, and the beginning of 7. They cover standard PCI/PCIe configuration, power management, MSI/MSI-X interrupt configuration, Advanced Error Reporting, BAR capability/control registers, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, and TPH requester steering-table fields.

## Important APIs, Types, And Register Groups

There are no C APIs or types in this chunk. The exported interface is a large set of macros consumed by NBIO, PCIe, and display/resource code that includes `nbio/nbio_7_2_0_sh_mask.h`.

Important macro groups:

- `BIF_CFG_DEV0_EPF5_1_LINK_STATUS2`: tail of PCIe Link Status 2, including equalization status, RTM presence detection, crosslink resolution, downstream component presence, and DRS message-received bits.
- `BIF_CFG_DEV0_EPF5_1_MSI_*` and `BIF_CFG_DEV0_EPF5_1_MSIX_*`: MSI/MSI-X capability list, enable/control, message address/data, mask/pending, MSI-X table and PBA BIR/offset fields.
- `BIF_CFG_DEV0_EPF5_1_PCIE_ADV_ERR_*`, `PCIE_UNCORR_ERR_*`, `PCIE_CORR_ERR_*`, `PCIE_HDR_LOG*`, and `PCIE_TLP_PREFIX_LOG*`: Advanced Error Reporting capability headers, status/mask/severity bits, first-error pointer/ECRC controls, header logs, and TLP prefix logs.
- `BIF_CFG_DEV0_EPF5_1_PCIE_BAR{1..6}_{CAP,CNTL}`: BAR capability and control masks for memory address size, BAR size support, resize requests, and BAR size assignment.
- `BIF_CFG_DEV0_EPF5_1_PCIE_PWR_BUDGET_*` and `PCIE_DPA_*`: power budgeting and Dynamic Power Allocation capability fields, including selected data, power scale/value, system allocation, substate control, and per-substate power allocations.
- `BIF_CFG_DEV0_EPF5_1_PCIE_ACS_*`, `PCIE_PASID_*`, `PCIE_ARI_*`: access control services, PASID support/enablement, and ARI next-function/function-group fields.
- `BIF_CFG_DEV0_EPF5_1_PCIE_TPH_*` and `PCIE_TPH_ST_TABLE_0..63`: TPH requester capability/control plus a 64-entry steering table, each table entry carrying `LOWER_ST` and `UPPER_ST` fields.
- `BIF_CFG_DEV0_EPF6_1_*`: complete endpoint-function 6 configuration-space field map in the same layout: identity/class code, command/status, BARs, adapter IDs, ROM base, interrupt pins, vendor/PMI/PCIe capabilities, link and device capabilities/control/status, MSI/MSI-X, AER, BAR controls, power budgeting, DPA, ACS, PASID, ARI, and TPH steering table.
- `BIF_CFG_DEV0_EPF7_1_*`: beginning of endpoint-function 7 configuration-space field map through `LINK_CNTL`, including standard PCI identity/configuration fields, BARs, PMI, PCIe capability, device capability/control/status, link capability, and link control.

## Control Flow

This header has no executable control flow. At compile time, C preprocessor expansion substitutes numeric shifts and masks into register code. Runtime behavior comes from the caller:

1. Caller selects a register address from `nbio_7_2_0_offset.h`.
2. Caller reads or writes the register using AMDGPU helpers such as `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, or SOC15 register-offset helpers.
3. Caller extracts or composes fields with the `__SHIFT` and `_MASK` macros from this header.

The macros are therefore declarative hardware metadata. Any side effects occur only when including code performs register I/O.

## State And Persistence Behavior

The header stores no software state. The state represented by these constants lives in NBIO PCI configuration registers and device capability structures exposed by the GPU hardware. Some fields are status-like and may reflect hardware events (`*_ERR_STATUS`, `LINK_TRAINING`, `DL_ACTIVE`, MSI pending bits). Others are control/configuration fields (`MSI_EN`, `MSIX_EN`, `BUS_MASTER_EN`, BAR resize controls, PASID enable, ACS control, ARI control, DPA control).

Persistence depends on the hardware register class rather than this header. Configuration writes may persist until function reset, device reset, FLR, suspend/resume reinitialization, or PCIe hot/reset events. Status and error bits may be sticky or write-one-to-clear according to the PCIe/NBIO register definition; this header only gives masks and does not encode access semantics.

## Dependencies

Primary dependencies are structural:

- Paired offsets in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, where matching `regBIF_CFG_DEV0_EPF*_1_*` symbols define register addresses and base indices.
- AMDGPU NBIO code, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes this header and uses NBIO register access helpers.
- SOC15 and PCIe register access infrastructure that translates NBIO register IDs/base indices to MMIO/PCIe port accesses.
- PCI/PCIe architectural semantics for capability lists, MSI/MSI-X, AER, ACS, PASID, ARI, TPH, BAR resizing, and power-management fields.

The macros themselves depend only on the C preprocessor and the header guard `_nbio_7_2_0_SH_MASK_HEADER`.

## Integration Points

This generated header integrates into the AMDGPU driver as a low-level hardware contract. Code can include it to avoid hard-coded bit positions when:

- enabling, masking, or diagnosing MSI/MSI-X interrupt state for NBIO endpoint functions;
- decoding AER uncorrectable/correctable error status and severity fields;
- configuring or reporting PCIe link capabilities, link control, and equalization state;
- programming function BAR sizing and resize controls;
- exposing or configuring advanced PCIe capabilities such as ACS, PASID, ARI, DPA, power budgeting, and TPH steering;
- correlating endpoint-function config-space definitions across repeated EPF5, EPF6, and EPF7 blocks.

Because the slice repeats a common capability layout for multiple endpoint functions, merge/reconciliation work should preserve the function-specific prefixes. Replacing `EPF6_1` with another endpoint prefix or deduplicating names would break existing register call sites that expect exact generated identifiers.

## Risks

- Incorrect shift or mask values can silently corrupt hardware register programming. For example, a wrong BAR control mask could change resize behavior, and a wrong MSI/MSI-X enable or mask field could break interrupt delivery.
- This chunk starts and ends inside larger endpoint-function sequences. Research consumers should not infer that `EPF5_1` or `EPF7_1` is complete from this chunk alone; earlier/later chunks contain adjacent register fields.
- Many fields are architecturally similar across EPF5, EPF6, and EPF7. Copy/paste or generator drift between endpoint functions is easy to miss because names differ only by the endpoint prefix.
- Status, mask, severity, and write-one-to-clear fields are all represented as plain masks. Callers must know the register access semantics; this header cannot prevent clearing sticky error bits or writing read-only capability fields.
- The TPH steering table exposes 64 nearly identical entries. Off-by-one use of table register names or steering indices would compile cleanly but program the wrong table entry.
- Some fields have full-width masks such as `0xFFFFFFFFL`, and some narrower PCI capability fields share 32-bit registers. Callers must combine masks carefully to avoid overwriting neighboring fields.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Full AMDGPU build with `nbio_7_2_0_sh_mask.h` included by `amdgpu/nbio_v7_2.c` verifies macro syntax, header guard behavior, and identifier availability.
- Compile tests for any code using `BIF_CFG_DEV0_EPF5_1_*`, `BIF_CFG_DEV0_EPF6_1_*`, or `BIF_CFG_DEV0_EPF7_1_*` fields should catch renamed or missing generated symbols.
- Static comparison against the paired `nbio_7_2_0_offset.h` should confirm that every mask/shift register group used by code has a corresponding `reg...` address definition.
- Hardware smoke tests should include PCIe link training/status reporting, MSI/MSI-X interrupt delivery, suspend/resume, FLR/reset, and error-reporting paths, since these are the feature areas represented by this chunk.
- AER-focused tests or diagnostics should verify that uncorrectable/correctable error status, masks, severity, first-error pointer, ECRC controls, and header/TLP prefix logs decode consistently with PCIe expectations.
- For SR-IOV or multi-function configurations, endpoint-function specific behavior should be checked so that EPF5, EPF6, and EPF7 register definitions are not accidentally interchanged.
