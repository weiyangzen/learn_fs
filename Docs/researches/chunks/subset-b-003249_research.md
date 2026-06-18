# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 7379-9808

## Scope

This chunk is part of the generated AMD NBIO 7.7.0 register-offset header used by the amdgpu driver. The selected range contains only preprocessor constants: it has no C functions, no structs, and no executable control flow. Its purpose is to give the driver stable symbolic names for NBIO/BIF PCI configuration-space register offsets and for the SOC15 base-index selector used by those registers.

The range starts in the tail of the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block, then defines complete blocks for `DEV0_EPF1` through `DEV0_EPF7`, and finally begins the next block, `DEV1_EPF0`. Every register constant in the chunk is paired with a `_BASE_IDX` constant whose value is `5`, indicating the same NBIO register base index for SOC15 register access macros.

## Address Blocks Covered

- `DEV0_EPF0` tail: lines 7379-7761, offsets `0x100bc` through `0x101bc`. This continues the endpoint function 0 PCIe extended-capability area rather than the normal PCI header.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`: lines 7764-8277, base address `0x10141000`, offsets `0x10400` through `0x1053c`. This is a full endpoint function 1 config-space map with a richer extended-capability set than EPF2-EPF7.
- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`: lines 8280-8525, base address `0x10142000`, offsets `0x10800` through `0x108cb`.
- `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`: lines 8528-8773, base address `0x10143000`, offsets `0x10c00` through `0x10ccb`.
- `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`: lines 8776-9021, base address `0x10144000`, offsets `0x11000` through `0x110cb`.
- `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`: lines 9024-9269, base address `0x10145000`, offsets `0x11400` through `0x114cb`.
- `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`: lines 9272-9517, base address `0x10146000`, offsets `0x11800` through `0x118cb`.
- `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`: lines 9520-9765, base address `0x10147000`, offsets `0x11c00` through `0x11ccb`.
- `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` start: lines 9768-9808, base address `0x10148000`, offsets `0x12000` through `0x1200b`.

The repeated spacing between endpoint-function blocks is significant. DEV0 EPF1 begins at `0x10400`, EPF2 at `0x10800`, EPF3 at `0x10c00`, and so on through EPF7 at `0x11c00`, with a `0x400` offset stride between functions. DEV1 EPF0 then starts at `0x12000`.

## Important Symbols And Register Families

This chunk contributes `1199` register-name macros and `1199` matching `_BASE_IDX` macros. The macros are consumed as compile-time constants by amdgpu register helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and PCIe indexed-access paths. The paired shift/mask details live in `nbio_7_7_0_sh_mask.h`; this header only provides addresses.

The main families are:

- PCI config common header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt fields, and latency/grant fields.
- Capability-list blocks: vendor capability, power management (`PMI_*`), PCI Express (`PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`), MSI, and MSI-X.
- PCIe error reporting: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable/correctable error status, masks, severities, AER control, header logs, and TLP prefix logs.
- BAR and address sizing: endpoint `BASE_ADDR_*`, `PCIE_BAR*_CAP`, `PCIE_BAR*_CNTL`, `PCIE_RESIZE_BAR*`, and EPF0/EPF1 VF resize BAR entries.
- Power and latency capabilities: `PCIE_LTR_*`, `PCIE_PWR_BUDGET_*`, and `PCIE_DPA_*` including DPA substate power allocation entries.
- Virtualization and isolation: `PCIE_SRIOV_*`, VF base-address entries, VF migration-state array offsets, `PCIE_ACS_*`, `PCIE_PASID_*`, and `PCIE_ARI_*`.
- Link training and signal integrity: data link feature (`DLF`), 16 GT/s PHY capability and status, lane equalization controls for lanes 0-15, and lane margining control/status for lanes 0-15.
- Miscellaneous or vendor-specific PCIe regions: `PCIE_VENDOR_SPECIFIC_*`, `FLADJ`, `DBESL_DBESLD`, and endpoint-specific capability-list anchors.

Several macros intentionally share the same offset because they name different bitfields inside the same DWORD. Examples in this range include `COMMAND`/`STATUS`, `DEVICE_CNTL`/`DEVICE_STATUS`, `LINK_CNTL`/`LINK_STATUS`, MSI address/data/mask variants, ARI cap/control, ACS cap/control, and DPA status/control. Consumers must combine these offset macros with the matching mask/shift macros rather than assuming one symbolic name equals one independent register storage location.

## Block-Specific Notes

The EPF0 tail is the broadest extended-capability slice in this chunk. It includes memory controller translation controls (`PCIE_MC_*`), latency tolerance reporting, ARI, SR-IOV, data-link features, 16 GT/s equalization, lane margining, VF resize BARs, ATS, PRI, resized BARs, secondary PCIe extended capability, protocol multiplexing, address translation service entries, and related virtualization/register-map features. Because the chunk starts on `regBIF_CFG_DEV0_EPF0_0_PCIE_PASID_CNTL_BASE_IDX`, it inherits the preceding PASID register definition from the previous chunk; merge/reconciliation should preserve that split.

The complete EPF1 block mirrors a normal PCI endpoint config-space header plus an extended capability tail. Unlike EPF2-EPF7, EPF1 includes the 16 GT/s PHY group, lane equalization entries for lanes 0-15, lane margining entries for lanes 0-15, VF resize BARs, ATS, PRI, and resize BAR controls. This suggests endpoint function 1 exposes a larger PCIe capability set than the later functions.

The EPF2 through EPF7 blocks are structurally compact and highly repetitive. Each has a standard PCI config header, vendor/PMI/PCIe/MSI/MSI-X capability entries, vendor-specific extended capability, AER logs, BAR controls, power budget, DPA, ACS, PASID, and ARI. Their offset layouts are identical apart from the `0x400` function stride.

The DEV1 EPF0 block begins only the standard config header through `ADAPTER_ID`. Later lines outside this chunk continue that address block. This chunk document should therefore not treat DEV1 EPF0 as fully covered.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is at compile time and driver initialization time:

1. `nbio_v7_7.c` includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. The amdgpu discovery path assigns `nbio_v7_7_funcs` and `nbio_v7_7_hdp_flush_reg` for NBIO IP versions `7.7.0` and `7.7.1`.
3. NBIO helper functions use generated offset macros with SOC15 and PCIe register-access helpers to read, write, or return hardware register offsets.
4. For registers in this chunk, any read/write state lives in the GPU's NBIO/BIF PCI configuration hardware, not in kernel memory owned by this header.

State persistence is therefore hardware-defined. Writes through consumers can persist until reset, function-level reset, power transition, or driver/firmware reprogramming depending on the register. The header itself stores no state, allocates no memory, performs no synchronization, and has no side effects.

## Dependencies And Integration Points

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` is the direct NBIO 7.7 consumer. It includes this header and the matching shift/mask header, then publishes the `amdgpu_nbio_funcs` table used by the broader amdgpu device initialization path.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c` selects the NBIO v7.7 function table for IP versions `7.7.0` and `7.7.1`, which makes these generated constants active on matching ASICs.
- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h` provides bitfield definitions for the same register names. Offset-only usage is unsafe when a symbolic register shares a DWORD with other named fields.
- SOC15 helper macros and accessors provide the addressing convention. The `_BASE_IDX` value `5` is part of that convention and must remain paired with these offsets.
- The PCI and PCIe capability names map to hardware-defined config-space structures. Linux PCI core concepts such as MSI/MSI-X, SR-IOV, ACS, PASID, ATS, AER, LTR, and DPA are represented here as hardware register offsets, although this header does not implement those subsystems.

## Risks And Review Considerations

- Generated-header drift is the main risk. Incorrect offsets or missing `_BASE_IDX` pairs would compile cleanly but direct register accesses to the wrong hardware locations.
- The chunk includes many aliased offsets where different fields share one DWORD. A consumer that writes a full register without masks can corrupt adjacent fields.
- EPF2-EPF7 are repetitive with fixed strides, so copy-generation mistakes can be hard to notice in review. Validate both the function prefix and offset range when comparing revisions.
- The line range starts mid-EPF0 and ends mid-DEV1 EPF0. Any final per-file summary must account for neighboring chunks before drawing conclusions about those two blocks.
- SR-IOV, PASID, ATS, ACS, and ARI definitions are security-sensitive because they affect isolation, address translation, and virtual-function behavior. A wrong register constant can break guest isolation or DMA/IOMMU behavior even though this header has no logic itself.
- Power-management and link-training registers affect resume, clock/power states, PCIe link speed, and signal margining. Incorrect constants may show up as intermittent link instability rather than deterministic build failures.
- This file is ASIC-generation-specific. Similar NBIO or NBIF headers define related names with different offsets, so code should include the header matched to the selected IP block rather than reusing constants across generations.

## Test And Validation Signals

Useful validation is mostly integration and hardware oriented:

- Build coverage: compile the amdgpu driver for configurations that include NBIO v7.7 support to catch missing or renamed macros.
- Register-table sanity: for this chunk, verify that every non-`_BASE_IDX` macro has a matching `_BASE_IDX` macro and that the base index remains `5`.
- Layout checks: compare EPF1-EPF7 address ranges against the ASIC register database or generated source, especially the `0x400` endpoint-function stride and the EPF2-EPF7 repeated layouts.
- Runtime smoke tests on NBIO IP `7.7.0` or `7.7.1`: device probe, PCIe link reporting, MSI/MSI-X interrupt operation, suspend/resume, SR-IOV capability exposure where supported, and AER logging.
- Targeted register access tests: use existing amdgpu debug paths or controlled driver instrumentation to read selected config-space offsets from EPF1-EPF7 and confirm expected PCI capability IDs/next pointers.
- Negative signal: unexplained PCI capability-list corruption, invalid BAR sizing, failed MSI/MSI-X setup, broken VF enumeration, ACS/PASID/ATS exposure mismatches, or AER logs with impossible header data can indicate offset mismatch in this family.
