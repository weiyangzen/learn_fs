# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 5825-8711

## Scope

This chunk is part of AMDGPU's generated NBIO 7.0 default-register header. It contains C preprocessor constants only: every exported item in the range is a `#define` ending in `_DEFAULT`, and there are no functions, structs, enums, variables, branches, locks, allocations, or direct MMIO operations.

The range starts inside `addressBlock: nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, whose header is on line 5764 before this chunk. It then covers complete NBIF PCI configuration blocks for `DEV1_EPF0`, `DEV1_EPF1`, and `DEV1_EPF2`; MSI-X table and pending-bit-array default blocks for AMDGFX, PSP, USB3, MP2, and GBE functions; PCIe physical root-port configuration defaults for BIFPLR0 through BIFPLR6; and per-port PCIe direction defaults for BIFP0, BIFP1, BIFP2, plus the beginning of BIFP3.

Although the repository path is under `distributed-fs/ceph-client`, this file is AMD GPU hardware register metadata, not Ceph or filesystem logic.

## Purpose

`nbio_7_0_default.h` publishes reset/default values for NBIO 7.0 registers. This chunk describes the default configuration image for PCIe/NBIF endpoint functions, MSI-X table apertures, PCIe bridge/root-port configuration spaces, and low-level PCIe port/link-controller registers. Driver code can include these constants alongside the matching offset and shift/mask headers to compare hardware state against expected reset values, initialize registers, preserve documented defaults, or generate ASIC-specific register tables.

The chunk is hardware-description data. Its correctness is tied to AMD's NBIO 7.0 register specification and to the generated sibling headers that assign addresses and bitfields for the same register names.

## Important APIs, Types, Functions, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the macro namespace:

- `smnBIF_CFG_DEV0_EPF7_1_*_DEFAULT`: tail of a device 0, embedded physical function 7 PCIe configuration block. The visible part covers MSI/MSI-X capability defaults, SATA capability placeholders, vendor-specific enhanced capability defaults, AER defaults, BAR capability/control defaults, power-budget/DPA defaults, ACS defaults, and ARI defaults.
- `smnBIF_CFG_DEV1_EPF0_1_*_DEFAULT`, `smnBIF_CFG_DEV1_EPF1_1_*_DEFAULT`, and `smnBIF_CFG_DEV1_EPF2_1_*_DEFAULT`: default PCI configuration-space values for device 1 functions. EPF0 is the most complete block in this range, including normal PCI header registers, PCIe capability, MSI/MSI-X, virtual channel, AER, BAR, power-budget, DPA, secondary PCIe, lane equalization, ACS, LTR, ARI, SR-IOV, PASID, resizable BAR, and TPH requester defaults. EPF1 and EPF2 carry a smaller but similar function capability/default surface.
- `smnPCIEMSIX_*_MSIX_TABLE_*_DEFAULT`: 128 default table entries each for `AMDGFX`, `PSP`, `USB3_0`, `USB3_1`, `MP2`, `GBE0`, and `GBE1`. The entries are all zero in this chunk, meaning message address/data/vector-control table storage has no nonzero generated reset value here.
- `smnPCIEMSIX_*_MSIX_PBA_DEFAULT`: one pending-bit-array default for each of the same MSI-X functions, also zero.
- `smnBIFPLR0_1_*_DEFAULT` through `smnBIFPLR6_1_*_DEFAULT`: repeated PCIe physical root-port configuration defaults. Each complete BIFPLR block has 169 definitions, with nonzero capability-chain, PCIe capability, link, MSI, SSID, vendor-specific, VC, AER, BAR, power-budget, DPA, secondary PCIe, lane equalization, ACS, LTR, ARI, SR-IOV, PASID, resizable BAR, and TPH defaults.
- `smnBIFP0_*_DEFAULT`, `smnBIFP1_*_DEFAULT`, `smnBIFP2_*_DEFAULT`, and partial `smnBIFP3_*_DEFAULT`: PCIe port/direct-register defaults for transaction-layer, data-link, flow-control, error, RX/TX, link-control, lane-control, clock/data recovery, equalization, link-management, strap, L1 PM substate, BCH ECC, HPGI, descriptor, and TX clock performance-counter registers.

The full range contains 2,803 `#define` rows. The address-block counts are useful validation anchors: seven 128-entry MSI-X table blocks, seven single-entry MSI-X PBA blocks, seven 169-definition BIFPLR blocks, three complete 72-definition BIFP port-direct blocks, and a partial BIFP3 block ending at `smnBIFP3_PCIE_LC_SPEED_CNTL_DEFAULT`.

## Control Flow And Runtime Behavior

This header has no executable control flow. It affects runtime only when included by code that uses these constants while programming or checking NBIO 7.0 hardware.

The implied runtime pattern is:

1. Caller code selects a register address from `nbio_7_0_offset.h` or `nbio_7_0_smn.h`.
2. It uses field geometry from `nbio_7_0_sh_mask.h` when only part of a register should change.
3. It may compare against, preserve, or write the `_DEFAULT` value from this header.
4. The actual read/write happens through AMDGPU accessors such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD` in the including driver code.

The hardware behavior represented by this chunk is PCIe/NBIF enumeration and link behavior rather than software branching: PCI config capability chains, MSI/MSI-X interrupt-vector storage, AER reporting defaults, BAR sizing/control defaults, root-port bridge capabilities, link speed/width/training defaults, lane equalization defaults, ASPM/L1-substate-related defaults, and port flow-control/error/link-management defaults.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. Its constants describe hardware reset/default state.

State classes represented in the chunk include:

- PCI configuration-space defaults for endpoint and root-port functions: vendor/device/header registers, BARs, capability pointers, command/status words, PCIe device/link capability/control/status registers, MSI/MSI-X, SSID, SR-IOV, PASID, resizable BAR, TPH, ACS, ARI, LTR, DPA, and power-budget capability blocks.
- MSI-X table/PBA state for function-specific interrupt delivery. The generated default table entries and PBA values are zero, so runtime vector programming must come from OS/driver interrupt setup.
- Link and port controller state in `BIFP*` blocks: TX/RX control, replay and credit controls, flow-control advertised/allocation state, error controls, link-control/training registers, lane controls, equalization forcing/best-settings registers, link-management status/masks, straps, L1 PM substates, BCH ECC, HPGI, and performance-counter defaults.
- Hardware-updated status fields are represented as default values only. For example, link status, AER status, MSI-X pending bits, lane status, link-management status, and RX captured LTR status can change at runtime after hardware initialization, firmware programming, PCI enumeration, link training, interrupt delivery, or error handling.

Persistence across warm reset, GPU reset, suspend/resume, BACO, PCIe retraining, or function-level reset is not defined here. AMDGPU reset/resume code and platform firmware decide when hardware is reinitialized and whether these defaults are restored, overridden, or merely used as reference values.

## Dependencies And Integration Points

The direct dependencies are the C preprocessor and the generated AMD register naming scheme. Functional use depends on sibling generated headers:

- `nbio_7_0_offset.h` for register offsets and base indices.
- `nbio_7_0_sh_mask.h` for field masks and shifts.
- `nbio_7_0_smn.h` for SMN-addressed register definitions.

In-tree include sites for `nbio_7_0_default.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`

Those consumers integrate NBIO 7.0 data with ASIC initialization, PCIe register access, memory-controller access enablement, doorbell ranges, interrupt handling, HDP flush offsets, clock gating, light sleep, power-management headers, and common SOC15 device setup. The exact macros in this chunk may not all be referenced by normal C code paths, but they are part of the generated ASIC register ABI and can be used by bring-up code, diagnostics, debug tooling, future driver paths, or generated register-table checks.

## Risks And Edge Cases

- The chunk boundaries are artificial. Line 5825 begins mid-`DEV0_EPF7` block, and line 8711 ends inside the `BIFP3` port-direct block. Whole-block conclusions must be merged with adjacent chunks.
- Generated default drift can compile cleanly while changing hardware behavior. A wrong nonzero default for PCIe capability, AER severity/mask, BAR control, link speed/width, lane equalization, or L1 substate register can affect enumeration, link training, power management, or error reporting.
- Many blocks are dense repetitions with only suffix changes. MSI-X tables repeat 128 zero entries per function, BIFPLR root ports repeat the same 169-definition pattern, and BIFP ports repeat the same 72-definition pattern. Off-by-one suffix or missing-row errors are easy to miss in review.
- Zero defaults are not proof that a register is unused. MSI-X table entries, PBA bits, BARs, AER status, lane status, and link-management status are normally programmed or updated dynamically after reset.
- PCIe capability-chain defaults encode offsets between capabilities and enhanced capabilities. Bad values can break OS PCI capability traversal or hide advertised features such as MSI, AER, ACS, ARI, SR-IOV, PASID, resizable BAR, LTR, or TPH.
- Status, clear, and mask registers often have side effects or hardware-updated semantics. Treating a `_DEFAULT` value as a safe writeback value without preserving live status can clear events, drop interrupts, or mask errors.
- Port/link-control defaults such as `PCIE_LC_CNTL*`, `PCIE_LC_LINK_WIDTH_CNTL`, `PCIE_LC_SPEED_CNTL`, `PCIE_LC_CDR_CNTL`, equalization controls, and L1 PM substate values are link-stability sensitive and may vary by board, straps, firmware, or ASIC revision.

## Test And Validation Signals

Useful validation is mostly generated-header consistency plus hardware smoke testing:

- Build AMDGPU configurations that include NBIO 7.0 headers to catch missing, malformed, or renamed macros.
- Compare each macro name in this chunk against `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h` so defaults, addresses, and field definitions stay aligned.
- Run generation checks for the repeated structures: seven 128-entry MSI-X table blocks should remain all-zero unless the hardware spec changes; seven PBA blocks should remain present; BIFPLR0-6 should retain aligned register lists and defaults; BIFP0-2 should match each other for the complete port-direct subset.
- Validate nonzero PCIe capability defaults against the hardware specification, especially capability-list pointers, `PCIE_CAP`, `DEVICE_CNTL`, `LINK_CAP`, `LINK_STATUS`, `LINK_CAP2`, `LINK_CNTL2`, AER severity/mask, BAR controls, DPA status, secondary PCIe lane equalization, LTR, ARI, SR-IOV, PASID, resizable BAR, and TPH fields.
- On NBIO 7.0 hardware, exercise PCI enumeration, MSI/MSI-X interrupt setup, AER reporting, suspend/resume, GPU reset, ASPM/L1 substates, link retraining, and link speed/width reporting while watching kernel logs for PCIe errors, AMDGPU reset storms, interrupt failures, or unexpected bandwidth drops.
- For low-level debug paths, read back representative `BIFPLR*` and `BIFP*` registers after reset and after driver initialization to distinguish hardware reset defaults from firmware or driver overrides.

## Chunk Boundary Notes

The previous chunk owns the start of `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`; this chunk begins at its MSI-X and enhanced-capability tail. The next chunk owns the remainder of `nbio_pcie0_bifp3_pciedir_p`, starting after `smnBIFP3_PCIE_LC_SPEED_CNTL_DEFAULT`, and then any later BIFP port-direct blocks. The final per-file research document should reconcile these boundaries before making whole-file statements about all NBIO 7.0 defaults.
