# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 9809-12228

## Chunk Scope

- Work item: `subset-b-003250`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, lines 9809-12228
- Parent file role: generated AMDGPU NBIO 7.7.0 register offset map.
- Chunk shape: 2,420 source lines containing 2,396 `#define` entries, 1,198 register-offset symbols, and 1,198 `*_BASE_IDX` definitions. Every base-index value in this span is `5`.

This is generated hardware ABI data, not executable driver logic. The constants are consumed by AMDGPU NBIO code through SOC15 register access helpers and paired with `nbio_7_7_0_sh_mask.h` when callers need bitfield-safe reads or writes.

## Purpose

This chunk defines symbolic register indexes for several NBIF/BIF PCI configuration-space windows and PCIe logical-root-port windows in NBIO 7.7.0 hardware. The values identify where standard PCI header fields, PCIe capability structures, MSI/MSI-X state, Advanced Error Reporting, virtualization capabilities, lane diagnostics, power-management capabilities, and root-port error-containment registers live inside AMD's generated register map.

The covered address blocks are:

- Continuation of `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` from the previous chunk, starting at `regBIF_CFG_DEV1_EPF0_0_ADAPTER_ID_BASE_IDX` and then `ROM_BASE_ADDR` through ARI control.
- Complete visible `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, base address `0x10149000`, from endpoint identity through ARI control.
- Complete visible `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, base address `0x10150000`, from endpoint identity through ARI control.
- Complete visible `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, base address `0x10151000`, from endpoint identity through ARI control.
- Complete visible `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp`, base address `0x10152000`, from endpoint identity through ARI control.
- Complete visible `nbio_pcie0_bifplr0_cfgdecp`, base address `0x11100000`, from logical root-port identity through 32 GT/s link status.
- Beginning of `nbio_pcie0_bifplr1_cfgdecp`, base address `0x11101000`, from logical root-port identity through `PCIE_RP_PIO_HDR_LOG2`; the rest of that root-port block continues in the next chunk.

## Public Surface

There are no C functions, structs, enums, callbacks, variables, or inline helpers in this range. The public surface is entirely preprocessor macros:

- `reg...` macros, such as `regBIF_CFG_DEV2_EPF0_0_PCIE_UNCORR_ERR_STATUS`, `regBIF_CFG_DEV1_EPF1_0_PCIE_PASID_CNTL`, `regBIFPLR0_0_PCIE_DPC_STATUS`, and `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2`, define register indexes.
- Matching `reg..._BASE_IDX` macros define the SOC15 base-table index for the register. In this chunk all are `5`, which means consumers rely on NBIO base slot 5 when computing the final MMIO address.
- Many logical names intentionally share the same numeric register index because PCI config-space fields are narrower than a DWORD or because a single DWORD has status/control or capability/control views. Examples include vendor/device ID pairs, command/status pairs, MSI data/address overlays, capability/control pairs, lane pairs, and DPA substate allocation groups.

The register-index range visible in this chunk starts at `0x1200c` for `regBIF_CFG_DEV1_EPF0_0_ROM_BASE_ADDR` and reaches `0x4004ea` for `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2`. The chunk has two deliberate cross-boundary incompletenesses: line 9809 is only the `BASE_IDX` for `regBIF_CFG_DEV1_EPF0_0_ADAPTER_ID` from the previous line, and line 12228 defines `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2` while its `_BASE_IDX` appears just after the requested range.

## Important Register Families

The endpoint-function blocks under `BIF_CFG_DEV1_*` and `BIF_CFG_DEV2_*` map PCI endpoint configuration images. They include standard header registers such as vendor/device ID, command/status, revision/class code, cache-line/latency/header/BIST, BARs, ROM BAR, capability pointer, interrupt line/pin, and adapter/vendor capability fields.

Their PCIe capability areas include:

- Power management capability and status/control registers.
- PCIe device, link, and device/link capability 2 controls and status.
- MSI and MSI-X structures, including message control, address/data, masks, pending bits, MSI-X table, and PBA offsets.
- Vendor-specific enhanced capabilities and virtual-channel capability/resource registers.
- Advanced Error Reporting status, masks, severity, capability/control, header logs, and TLP prefix logs.
- BAR enhanced capability/control, power budget, dynamic power allocation substate allocation, secondary PCIe capability, ACS, PASID, and ARI controls.

The `DEV1_EPF0` part starts mid-block, so its earliest identity/header/BAR macros are in the previous chunk. `DEV1_EPF1`, `DEV2_EPF0`, `DEV2_EPF1`, and `DEV2_EPF2` are visible from their `VENDOR_ID` definitions onward. The `DEV2` endpoint blocks follow the same repeated generated layout pattern with offsets shifted by endpoint/function window.

The `BIFPLR0_0` block is a PCIe logical-root-port configuration image. It includes bridge-oriented PCI fields such as bus-number and window registers, root/slot controls, PM/PCIe/MSI/SSID/MSI-map capability structures, vendor-specific capability, VC resources, device serial number, AER/root-error status, secondary PCIe equalization controls, ACS, multicast capability, L1 PM substates, DPC, RP PIO error reporting and logs, ESM capability/status/control, data-link feature capability/status, 16 GT/s PHY controls and per-lane equalization, margining port/lane controls, CCIX transaction capability/control, ESM 20 GT/s and 25 GT/s per-lane equalization controls, and 32 GT/s link capability/control/status registers.

The `BIFPLR1_0` block begins the same root-port pattern for the second logical root port. This chunk covers its standard bridge header, PM/PCIe/MSI/SSID/MSI-map capability area, VC resources, device serial number, AER/root-error logging, secondary PCIe equalization for lanes 0-15, ACS, multicast controls, L1 PM substates, DPC, and the start of RP PIO logging through header log 2.

## Control Flow

This header has no runtime control flow. The operational flow is external:

1. NBIO 7.7.0 driver code includes `nbio_7_7_0_offset.h` and the sibling shift/mask header.
2. Code selects a `reg...` symbol for a hardware operation.
3. SOC15 helpers combine the offset, the `*_BASE_IDX`, NBIO hardware instance, and generated base table into an MMIO address.
4. Driver code reads, writes, or polls that address through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, or PCIe-port accessors.
5. Field composition or decoding uses `REG_SET_FIELD` and masks/shifts from `nbio_7_7_0_sh_mask.h`.

The values in this chunk can therefore alter runtime behavior only through consumers. Incorrect constants can redirect an otherwise correct driver operation to the wrong register.

## State And Persistence

The file owns no mutable state, allocates no memory, performs no I/O, and persists nothing. It names hardware state in NBIO/NBIF PCI configuration and logical-root-port windows.

The represented hardware state includes:

- Endpoint identity, class, BAR, ROM, capability-list, interrupt, PM, MSI, MSI-X, AER, VC, ACS, PASID, ARI, power-budget, and DPA state.
- Root-port bridge windows, bus numbering, root/slot controls, link controls, link status, negotiated link width/speed, L1 PM substate controls, DPC state, RP PIO error state, and AER root-error logs.
- Lane-level state for equalization, 16 GT/s PHY training/status, margining control/status, ESM 20/25 GT/s equalization, and 32 GT/s link control/status.
- Error-observation and error-policy state, including correctable/uncorrectable masks, severities, header logs, TLP prefix logs, DPC status, RP PIO masks/severity/sys-error/exception bits, and error source IDs.

Persistence across FLR, GPU reset, PCIe hot reset, suspend/resume, runtime power transitions, or BACO is not encoded here. Those behaviors are defined by hardware and by the driver code that uses these offsets.

## Dependencies And Integration Points

The direct companion header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h`, which supplies bit positions and masks for many registers named here. Offsets alone are sufficient for raw reads/writes but not for safe field manipulation.

The direct source-tree user found for this header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That implementation uses the generated register macros for NBIO 7.7 operations such as HDP register remapping, revision-ID reads, framebuffer access enablement, memory-size reads, SDMA/VCN/IH doorbell range programming, doorbell aperture setup, PCIE/RSMU index/data offset lookup, interrupt control, and NBIO initialization.

The specific endpoint and root-port macros in this chunk are likely used indirectly by common AMDGPU PCIe/NBIO access paths, diagnostics, dumps, or future feature code rather than all being referenced directly in `nbio_v7_7.c`. Their integration contract is the generated naming convention plus the SOC15 base-index convention.

These definitions also integrate conceptually with PCI and PCIe configuration-space specifications: PM, MSI, MSI-X, PCIe device/link/slot/root capabilities, VC, AER, ACS, PASID, ARI, power budget, DPA, multicast, L1 PM substates, DPC, RP PIO, data-link feature, 16 GT/s and 32 GT/s link capabilities, and lane margining.

## Risks And Edge Cases

- Chunk boundaries split two macro pairs. `regBIF_CFG_DEV1_EPF0_0_ADAPTER_ID_BASE_IDX` lacks its register macro inside this exact range, and `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2` lacks its `_BASE_IDX` until the next line after the range. Pair-completeness checks must be performed after adjacent chunks are reconciled.
- Generated aliases are intentional. Removing duplicate numeric values or assuming one unique register per macro would break PCI config fields that share DWORDs or have multiple semantic views.
- The endpoint blocks are repetitive across devices/functions. Accidentally mixing `DEV1` and `DEV2`, or `EPF0`, `EPF1`, and `EPF2`, can compile cleanly while targeting a different PCI function image.
- Root-port blocks are similarly repetitive. Using a `BIFPLR0_0` macro for a `BIFPLR1_0` access can misread or reprogram the wrong logical root port.
- Base index `5` is part of the ABI. Copying a macro name or offset into code that bypasses the matching `*_BASE_IDX` can compute the wrong SOC15 address.
- AER, DPC, RP PIO, and root-error registers are error-handling critical. Wrong offsets can mask fatal errors, fail to clear sticky status, misattribute PCIe faults, or produce misleading diagnostics.
- Link-control, 16 GT/s, 25 GT/s ESM, margining, and 32 GT/s registers affect link stability and performance. Incorrect writes can disrupt training, power management, equalization, or recovery.
- ACS, PASID, ARI, multicast, VC, and MSI/MSI-X controls affect routing, isolation, interrupt delivery, and virtualization behavior. Mistakes can cause security, enumeration, or interrupt-routing failures.
- Status/log registers may have hardware side effects such as write-one-to-clear semantics. This header does not encode access width or side-effect policy; consumers must use the matching hardware programming guide and driver conventions.

## Test And Validation Signals

Useful validation for this chunk is mostly generated-data and hardware integration coverage:

- Build AMDGPU with NBIO 7.7.0 support so `nbio_v7_7.c` and dependent headers resolve all referenced offset and mask symbols.
- Static generated-header checks should verify that every visible `reg...` has a matching `reg..._BASE_IDX` after adjacent chunks are merged, and that all base indices in this range remain `5`.
- Cross-check register families against `nbio_7_7_0_sh_mask.h` so field-level users have matching mask/shift definitions for endpoint, root-port, AER, DPC, MSI/MSI-X, link, ACS, PASID, ARI, and lane diagnostics registers.
- Compare generated endpoint layouts across `DEV1_EPF1`, `DEV2_EPF0`, `DEV2_EPF1`, and `DEV2_EPF2` for expected structural symmetry and offset deltas.
- Compare `BIFPLR0_0` and `BIFPLR1_0` common root-port layouts where both are visible, while accounting for this chunk ending before `BIFPLR1_0` is complete.
- Runtime smoke tests on matching hardware should cover GPU probe, NBIO revision read, framebuffer access enable/disable, doorbell aperture/range setup, HDP flush remap paths, interrupt setup, reset, suspend/resume, and PCIe link stability.
- PCIe validation should include AER/DPC/RP PIO error injection or controlled error paths, checking status/mask/severity/log decoding and clearing behavior.
- Virtualization and IOMMU tests should validate PASID, ARI, ACS, MSI/MSI-X, BAR, and endpoint-function enumeration behavior when the relevant functions are exposed.
- Link diagnostics should exercise lane equalization, L1 PM substates, 16 GT/s status, ESM 20/25 GT/s lane controls, margining, and 32 GT/s link capability/status paths where supported by hardware or simulation.

## Notes For Merge/Reconciliation

This is one chunk of the larger `nbio_7_7_0_offset.h` file. It should remain source-tree-aligned under `Docs/researches/chunks/` and should not be treated as a final per-file report.

The merge lane should preserve the fact that lines 9809-10200 continue `DEV1_EPF0` from the previous chunk, lines 10202-11371 cover additional endpoint-function blocks, lines 11374-11923 cover complete visible `BIFPLR0_0`, and lines 11926-12228 start but do not complete `BIFPLR1_0`.
