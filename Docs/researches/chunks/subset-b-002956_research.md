# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 7549-10000

## Scope

This chunk is part of AMDGPU's generated NBIO 4.3.0 register-offset header. It contains C preprocessor constants that map NBIO/NBIF PCI configuration decoder register names to numeric register offsets, plus paired `_BASE_IDX` selectors for the SOC15/NBIO base-address table.

The covered range starts mid-block in the SR-IOV virtual-function 0 PCIe capability area and ends mid-block in virtual-function 15. It contains 2,392 `#define` lines: 1,196 register-offset constants and 1,196 base-index constants within the requested range, although the final visible `VF15_MSIX_PBA` offset at line 10000 has its `_BASE_IDX` pair just outside this chunk at line 10001. The chunk is declarative hardware metadata; it defines no functions, structs, enums, storage, branches, locks, allocations, or direct MMIO operations.

## Purpose

The purpose of this slice is to publish symbolic addresses for the NBIO 4.3.0 PCI/PCIe configuration-space windows for device 0, endpoint function 0 SR-IOV virtual functions. Driver code and generated register tables can use these `regBIF_CFG_DEV0_EPF0_VF<n>_*` names instead of embedding raw offsets such as `0x18400` or `0x1bc30`.

The repeated macro schema is:

- `regBIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>` for the register offset.
- `regBIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>_BASE_IDX` for the NBIO base selector, which is consistently `5` in this range.

For the complete VF blocks in this chunk, each VF advances by `0x400` in register-offset space. For example, `VF1_VENDOR_ID` is `0x18400`, `VF2_VENDOR_ID` is `0x18800`, and `VF15_VENDOR_ID` is `0x1bc00`. The address-block comments report matching decoded hardware base addresses from `0x10161000` through `0x1016f000`.

## Address Blocks and Register Coverage

The chunk begins in the tail of `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`. Lines 7549-7645 cover the later `VF0` PCIe capability registers from `DEVICE_CNTL`'s base-index pair through link, MSI/MSI-X, vendor-specific, AER, and ARI offsets.

Complete visible address-block starts are:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf1_bifcfgdecp`, base address `0x10161000`, starting at line 7648.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf2_bifcfgdecp`, base address `0x10162000`, starting at line 7808.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf3_bifcfgdecp`, base address `0x10163000`, starting at line 7968.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf4_bifcfgdecp`, base address `0x10164000`, starting at line 8128.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`, base address `0x10165000`, starting at line 8288.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf6_bifcfgdecp`, base address `0x10166000`, starting at line 8448.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf7_bifcfgdecp`, base address `0x10167000`, starting at line 8608.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, base address `0x10168000`, starting at line 8768.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf9_bifcfgdecp`, base address `0x10169000`, starting at line 8928.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf10_bifcfgdecp`, base address `0x1016a000`, starting at line 9088.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf11_bifcfgdecp`, base address `0x1016b000`, starting at line 9248.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp`, base address `0x1016c000`, starting at line 9408.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf13_bifcfgdecp`, base address `0x1016d000`, starting at line 9568.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf14_bifcfgdecp`, base address `0x1016e000`, starting at line 9728.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf15_bifcfgdecp`, base address `0x1016f000`, starting at line 9888.

For complete `VF1` through `VF14`, the repeated register families include:

- Standard PCI header identity/configuration: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, cache-line/latency/header/BIST fields, BARs `BASE_ADDR_1` through `BASE_ADDR_6`, CardBus CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X capability: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI message address/data/mask/pending forms, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- PCIe vendor-specific extended capability: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.
- PCIe Advanced Error Reporting: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable/correctable error status/mask/severity registers, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3`, and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`.
- ARI capability: `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.

The `VF15` block is partial in this chunk. It starts at `VENDOR_ID` and reaches `MSIX_PBA` at line 10000; vendor-specific, AER, and ARI `VF15` offsets continue immediately after the requested range.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or executable functions in this chunk. The interface is the macro namespace itself.

Important macro families are the `regBIF_CFG_DEV0_EPF0_VF<n>_*` offsets and their `_BASE_IDX` partners. Consumers normally pair these offsets with field definitions in `nbio_4_3_0_sh_mask.h`, where matching names such as `BIF_CFG_DEV0_EPF0_VF0_DEVICE_CNTL` and `BIF_CFG_DEV0_EPF0_VF15_MSIX_PBA` define bit shifts and masks.

The header-level dependency is the include guard established earlier in the file. No local macro in this range computes an address by itself; runtime code must combine the offset with the correct NBIO base/instance mechanism, such as SOC15 register helpers or display `NBIO_BASE(...)` table construction.

## Control Flow

This chunk has no runtime control flow. Compile-time behavior is limited to making the register symbols available to translation units that include `nbio_4_3_0_offset.h`.

The inferred runtime flow for any consumer of these VF offsets is:

1. Select an NBIO 4.3.0 target and include the offset header with the matching shift/mask header.
2. Choose the VF-specific config register symbol for the PCI/PCIe capability being read or programmed.
3. Combine `reg..._BASE_IDX` and `reg...` with the driver register-address helper.
4. Read, write, or update the hardware register using the companion field masks where bit-level access is needed.

In this repository snapshot, direct users of `nbio_4_3_0_offset.h` include `amdgpu/nbio_v4_3.c`, SMU 13.0.0/13.0.7 power-management tables, and DCN 3.2/3.2.1 resource code. The directly inspected implementation code mostly uses non-VF NBIO registers for HDP flush, doorbells, LTR, ASPM, interrupt control, and display NBIO-base table setup; the VF config-space offsets in this chunk are generated address metadata available to SR-IOV, diagnostics, and config-space decode paths rather than obvious direct call-site references in the inspected files.

## State and Persistence Behavior

The header stores no software state and performs no persistence. The state represented by these offsets lives in NBIO hardware and PCIe configuration registers for SR-IOV virtual functions.

Some referenced registers hold configuration that can persist until reset, function-level reset, PF-controlled VF teardown, or guest/host PCI core reprogramming: command bits, BARs, ROM BAR, MSI/MSI-X enable and table/PBA pointers, PCIe device control, link control, completion timeout controls, and ARI controls. Others are status or diagnostic registers, such as device/link status, AER correctable/uncorrectable status, header logs, and TLP prefix logs. The offset header does not encode access policy, read-clear/write-one-to-clear semantics, reset values, privilege restrictions, or PF/VF ownership rules.

Because this is VF config-space address metadata, runtime state can be affected by SR-IOV lifecycle events outside the code that includes this header: PF driver VF enablement, guest driver enumeration, PCI core capability negotiation, FLR, GPU reset, suspend/resume, and virtualization policy.

## Dependencies and Integration Points

The immediate dependency is the C preprocessor. Semantically, this generated file must match AMD's NBIO 4.3.0 register database and the companion `nbio_4_3_0_sh_mask.h` field layout header.

Integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which includes the NBIO 4.3.0 offset/mask pair and uses nearby NBIO registers through `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `WREG32_FIELD15_PREREG`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include the same NBIO 4.3.0 headers for SMU-side power-management programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c` and `dcn321_resource.c`, which include `nbio_4_3_0_offset.h` and construct NBIO register addresses with `NBIO_BASE(regBIF_BX0_*_BASE_IDX) + regBIF_BX0_*`.
- Linux PCIe/SR-IOV infrastructure, because these names mirror standard PCI header, PCIe capability, MSI/MSI-X, AER, and ARI register layouts for virtual functions.
- Interrupt routing and virtualization paths through MSI/MSI-X capability offsets and per-VF table/PBA pointers.
- PCIe error handling and diagnostics through AER status/mask/severity and log registers.

## Risks and Edge Cases

- Generated-header drift is the main risk. If an offset or `_BASE_IDX` differs from the NBIO 4.3.0 hardware database, code can compile cleanly while reading or writing the wrong hardware register.
- The chunk boundaries are partial. `VF0_DEVICE_CNTL`'s offset is immediately before this range while its `_BASE_IDX` is inside it, and `VF15_MSIX_PBA`'s `_BASE_IDX` is immediately after this range. The final per-file report should reconcile adjacent chunks before making completeness claims.
- The VF blocks are highly repetitive. A copy-generation error in a VF number, offset stride, or base index would be difficult to detect visually.
- Several registers share the same offset because PCI config registers expose multiple named fields in the same dword, such as `COMMAND`/`STATUS`, `DEVICE_CNTL`/`DEVICE_STATUS`, `LINK_CNTL`/`LINK_STATUS`, MSI address/data aliases, and ARI capability/control aliases. Consumers must use the correct companion masks and preserve unrelated fields.
- The all-`5` base-index pattern is part of the address contract. Accidentally using a PF, non-VF, or different-generation base index would address a different NBIO window.
- Registers named as control fields may trigger visible hardware behavior if written incorrectly, including VF FLR, MSI/MSI-X masking, link retraining/disable behavior, completion-timeout handling, AER masking/severity, and ARI routing.
- The header does not specify access type, privilege, ordering, reset value, or guest/PF ownership. SR-IOV code must respect the PCIe spec, AMD hardware rules, and Linux PCI core ownership.

## Test Signals

Useful validation signals for this chunk are primarily generated-header and integration checks:

- Compile coverage for AMDGPU configurations that include `nbio_4_3_0_offset.h`, especially `nbio_v4_3.c`, SMU 13.0.0/13.0.7, and DCN 3.2/3.2.1 resource code.
- Static consistency checks that every offset macro in the full file has the intended `_BASE_IDX` partner and that every consumed offset has a matching field group in `nbio_4_3_0_sh_mask.h`.
- Pattern checks across `VF1` through `VF14` confirming the expected `0x400` stride, identical register-family ordering, and base index `5`.
- Boundary checks during merge: pair line 7549 with the preceding `VF0_DEVICE_CNTL` offset and line 10000 with the following `VF15_MSIX_PBA_BASE_IDX`.
- Runtime SR-IOV smoke tests on NBIO 4.3.0 hardware: enable VFs, enumerate them, assign or bind drivers, verify BAR sizing, program MSI/MSI-X, and confirm interrupts and reset behavior.
- PCIe capability inspection through kernel logs, debugfs dumps, or tools such as `lspci -vv` to confirm VF PCIe, MSI/MSI-X, AER, and ARI capabilities decode as expected.
- Error-path validation that PCIe AER status/mask/severity and header-log offsets are decoded correctly when errors are injected or observed.

## Chunk Notes

This is only the source-tree-aligned chunk report for `subset-b-002956`. It intentionally does not create a final per-file research document for `nbio_4_3_0_offset.h`; the merge/reconciliation lane should combine this report with adjacent chunks before making complete-file statements.
