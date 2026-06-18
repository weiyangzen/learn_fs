# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 53723-56188

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It exports C preprocessor constants that describe field bit positions and masks for NBIF/BIF PCIe configuration-space registers. The matching register addresses are in `nbio_7_7_0_offset.h`; this header only describes how to interpret or compose values inside those registers.

The range begins inside the `BIF_CFG_DEV0_EPF4_0` PCIe Advanced Error Reporting area, covers the tail of EPF4's AER and extended capability fields, then fully covers the `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp` address blocks. It ends at the first field definition for `BIF_CFG_DEV0_EPF7_0_DBESL_DBESLD`, so EPF7 is only partially represented here. The complete EPF5 and EPF6 blocks expose conventional PCI configuration-space fields, PCIe capability and link controls, MSI/MSI-X metadata, AMD vendor-specific registers, AER status/mask/severity/logs, BAR enhanced capability controls, power budgeting, dynamic power allocation, access control services, PASID, and ARI definitions.

## Important APIs, Types, And Functions

There are no functions, structs, enums, storage objects, or inline helpers in this chunk. The API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask for that field in the containing register value.

This line range contains 2,130 `#define` entries: 1,064 `__SHIFT` definitions and 1,066 `_MASK` definitions. The imbalance is caused by chunk boundaries: the range starts after several `BIF_CFG_DEV0_EPF4_0_PCIE_CORR_ERR_STATUS` shifts from the previous line range and ends after only the first `BIF_CFG_DEV0_EPF7_0_DBESL_DBESLD__DBESL__SHIFT`.

Important register families covered by the chunk:

- EPF4 tail: `BIF_CFG_DEV0_EPF4_0_PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, AER capability/control, TLP header logs, TLP prefix logs, BAR enhanced capability and BAR1-BAR6 resize controls, power-budget data, DPA, ACS, PASID, and ARI.
- EPF5 conventional config header: vendor/device ID, command/status, revision/class bytes, cache line, latency, header type, BIST, BAR1-BAR6, CardBus CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, max latency, vendor capability list, and writable adapter ID mirror.
- EPF5 power/USB-style fields: PM capability list, PM capability, PM status/control, `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- EPF5 PCIe capability fields: PCIe capability list/header, Device Capability/Control/Status, Link Capability/Control/Status, Device Capability 2, Device Control 2, Device Status 2, Link Capability 2, Link Control 2, and Link Status 2.
- EPF5 interrupt capability fields: MSI capability list/control, MSI message address/data/mask/pending registers, 64-bit MSI variants, MSI-X capability list/control, MSI-X table, and MSI-X PBA.
- EPF5 vendor and error-reporting fields: vendor-specific enhanced capability header/payload, AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, TLP prefix logs, BAR enhanced capability, power-budgeting, DPA, ACS, PASID, and ARI.
- EPF6 complete mirror: the same conventional config-space, PM, PCIe capability, MSI/MSI-X, vendor-specific, AER, BAR enhanced capability, power budget, DPA, ACS, PASID, and ARI field families are repeated under `BIF_CFG_DEV0_EPF6_0_*`.
- EPF7 beginning: conventional PCI config-space and PM-related fields through the first `DBESL_DBESLD` shift. Its later PCIe capability, MSI/MSI-X, AER, BAR, power, DPA, ACS, PASID, and ARI definitions are in the following chunk.

The dominant EPF5 and EPF6 groups are highly regular. For example, `COMMAND` exposes enable bits for I/O, memory, bus mastering, SERR, and interrupt disable; `STATUS` exposes PCI status/error bits; `DEVICE_CNTL` exposes PCIe error reporting enables, relaxed ordering, payload size, no-snoop, read-request size, and FLR initiation; `LINK_CNTL` exposes ASPM, retrain, common clock, extended sync, bandwidth management, and hardware autonomous width disable bits; and AER groups expose PCIe uncorrectable and correctable error bitfields such as DLP, poisoned TLP, completion timeout, unexpected completion, ECRC, ACS violation, internal errors, replay timeout, advisory nonfatal, and header-log overflow.

## Control Flow And Data Flow

The header has no executable control flow. Runtime behavior appears in consumers that include the generated offset and mask headers and perform hardware reads or writes.

Typical use is:

1. Include `nbio/nbio_7_7_0_offset.h` for register addresses and `nbio/nbio_7_7_0_sh_mask.h` for field geometry.
2. Select a register such as `regBIF_CFG_DEV0_EPF5_0_DEVICE_CNTL`, `regBIF_CFG_DEV0_EPF6_0_PCIE_UNCORR_ERR_STATUS`, or the corresponding EPF4/EPF7 register from the offset header.
3. Read the hardware register through an AMDGPU accessor such as `RREG32_SOC15`, `RREG32_PCIE_PORT`, or a related NBIO/PCIe config access path.
4. Decode values with `REG_GET_FIELD` or raw mask/shift operations, using the generated `*_MASK` and `*__SHIFT` macros.
5. For writable controls, perform read-modify-write with `REG_SET_FIELD` or equivalent arithmetic and write back through `WREG32_SOC15`, `WREG32_PCIE_PORT`, or the appropriate indexed access helper.

The field flow represented here is mostly PCI/PCIe configuration-space state. Capability-list headers link capability structures through `CAP_ID`, `CAP_VER`, and `NEXT_PTR` fields. Control fields feed hardware policy, such as command decoding, bus mastering, PCIe error reporting, FLR, link retraining, MSI/MSI-X interrupt setup, AER masking/severity, DPA power allocation, ACS isolation features, PASID enablement, and ARI forwarding. Status and log fields flow in the opposite direction: hardware sets negotiated link attributes, error status, TLP header logs, DPA active state, MSI pending bits, and capability support bitmaps for software to inspect.

## State And Persistence

The macros are stateless compile-time constants. The state they describe resides in NBIO/PCIe hardware configuration registers.

Identity and capability fields such as vendor/device IDs, class code, capability IDs, PCIe capability version, maximum payload support, link speed/width support, MSI/MSI-X table metadata, BAR size support, DPA capability, ACS capability, PASID capability, and ARI capability are typically hardware-, firmware-, or strap-defined. Control fields such as `COMMAND`, `PMI_STATUS_CNTL`, `DEVICE_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL`, `LINK_CNTL2`, MSI/MSI-X enables, AER masks/severity, BAR resize controls, DPA control, ACS control, PASID control, and ARI control are writable hardware state whose lifetime depends on reset domain, FLR, GPU reset, suspend/resume, power gating, and firmware or PCI core policy.

Status/log fields such as PCI status, Device Status, Link Status, Link Status 2, MSI pending bits, AER uncorrectable/correctable status, TLP header logs, TLP prefix logs, DPA status, and PME status are live hardware observations. Many status bits in PCI/PCIe config space are sticky or write-one-to-clear by specification or hardware convention. This generated header does not encode access permissions, reset values, write-one-to-clear behavior, read side effects, reserved-bit constraints, or sequencing requirements.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, which supplies the matching register address and base-index macros. A mask such as `BIF_CFG_DEV0_EPF6_0_PCIE_UNCORR_ERR_STATUS__CPL_TIMEOUT_STATUS_MASK` is meaningful only when paired with the NBIO 7.7 offset for `BIF_CFG_DEV0_EPF6_0_PCIE_UNCORR_ERR_STATUS`.

The direct C include site in this source tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That file provides the NBIO v7.7 operations table and uses generated register constants with AMDGPU access helpers for revision identification, memory-controller access, doorbell aperture programming, interrupt handling setup, HDP flush/remap offsets, PCIe index/data offset reporting, clock gating, light sleep, initialization, and register remapping. This chunk's EPF4-EPF7 PCIe configuration-space masks are part of the same generated map and are available to NBIO code, PCIe diagnostics, RAS/AER handling, interrupt setup, virtualization/isolation paths, or future endpoint-function support.

Other semantic dependencies are PCI and PCIe specifications for conventional config space, PM capability, PCIe capability, MSI/MSI-X, Advanced Error Reporting, resizable BAR/BAR enhanced capability, Power Budgeting, Dynamic Power Allocation, Access Control Services, PASID, and Alternative Routing-ID Interpretation. AMD's NBIO 7.7 register database determines the exact endpoint-function coverage and any hardware-specific reserved or implementation-defined fields.

## Risks

- Address/mask mismatch is the central risk. These macros must be used with NBIO 7.7 offsets for the same `BIF_CFG_DEV0_EPF*_0_*` register name; using a different ASIC generation or endpoint-function prefix can compile cleanly while targeting the wrong field.
- Chunk boundaries split logical register groups. The first visible lines continue `BIF_CFG_DEV0_EPF4_0_PCIE_CORR_ERR_STATUS` from the previous chunk, and the last visible line starts `BIF_CFG_DEV0_EPF7_0_DBESL_DBESLD`; per-file synthesis must merge adjacent chunks before treating EPF4 or EPF7 as complete.
- EPF5 and EPF6 are near-identical repeated layouts. Copying a macro from the wrong endpoint function can read or alter a sibling function with no compiler warning.
- Status and error-log registers are side-effect sensitive. AER, PCI status, Device Status, Link Status, MSI pending, PME status, and header/prefix logs may require write-one-to-clear or read/clear sequencing; this header does not express those rules.
- Link and device controls can affect hardware availability. Fields for bus mastering, memory decode, FLR, max payload/read request size, link retraining, ASPM, link disable, equalization request, MSI/MSI-X enablement, BAR sizing, ACS, PASID, and ARI can change DMA reachability, interrupt delivery, isolation, or link stability.
- Reserved-bit preservation matters. The generated masks expose known fields but do not tell consumers which adjacent bits must be left untouched on writes.
- Power and virtualization features are policy-heavy. PM, power budget, DPA, ACS, PASID, ARI, and BAR enhanced controls need coordination with PCI core, IOMMU, firmware, and platform policy.

## Test Signals

Useful validation signals for changes touching this chunk or its consumers include:

- The AMDGPU tree builds with `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` including `nbio_7_7_0_sh_mask.h`; renamed or missing generated macros should fail at compile time.
- Static generated-header checks confirm each complete EPF5 and EPF6 register block has paired `__SHIFT` and `_MASK` definitions, masks align with shifts, and corresponding register offsets exist in `nbio_7_7_0_offset.h`.
- Boundary checks account for the partial EPF4 and EPF7 groups, specifically the starting `PCIE_CORR_ERR_STATUS` masks and ending `DBESL_DBESLD` split.
- Runtime bring-up on NBIO 7.7 hardware shows normal PCIe enumeration, stable GPU load/unload, valid doorbell and interrupt behavior, and no unexpected failures in NBIO initialization paths.
- PCIe diagnostics report plausible command/status, PM, PCIe Device/Link Capability, Link Status, Link Status 2, negotiated speed/width, MSI/MSI-X capability, BAR sizing, ACS/PASID/ARI capability, and DPA/power budget fields for the relevant endpoint functions.
- Error-path or RAS testing observes expected AER correctable/uncorrectable status, masks, severity policy, header-log and prefix-log capture, and correct clear behavior without losing evidence or leaving interrupts asserted.
- Reset and power-management testing across FLR, GPU reset, suspend/resume, and power gating verifies writable controls are restored by higher-level code rather than assumed from this header.
