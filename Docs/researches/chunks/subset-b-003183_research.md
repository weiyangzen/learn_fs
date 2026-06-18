# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 56064-58546

## Scope

This chunk covers a generated AMD NBIO 7.2.0 shift/mask slice for PCI/PCIe configuration-space fields. The selected range starts at the `BIF_CFG_DEV0_EPF2_0_MSIX_MSG_CNTL` mask tail, covers the remaining `DEV0_EPF2` extended capability masks, covers a complete `DEV0_EPF3` endpoint-function mask block, and ends inside `BIF_CFG_DEV0_EPF4_0_DEVICE_CAP2`, after `LN_SYSTEM_CLS_MASK`.

The range contains 2,118 preprocessor definitions: 1,062 `__SHIFT` constants and 1,116 `_MASK` constants. It is generated register-description data only. There are no C functions, structs, enums, variables, loops, branches, or direct register accesses in this chunk.

## Purpose

The purpose of this header section is to define the bit layout for NBIO 7.2 PCI configuration registers associated with device 0 endpoint functions 2, 3, and the beginning of function 4. Each field is represented by the standard generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to extract, test, or compose the field value.

The sibling `nbio_7_2_0_offset.h` file supplies the matching register addresses and base indices. For example, the offset header maps `regBIF_CFG_DEV0_EPF2_0_PCIE_UNCORR_ERR_STATUS` to `0x10855`, `regBIF_CFG_DEV0_EPF3_0_PCIE_TPH_ST_TABLE_63` to `0x10cfe`, and `regBIF_CFG_DEV0_EPF4_0_DEVICE_CAP2` to `0x11022`, all with base index `5`. This chunk supplies the field shifts and masks within those registers.

## Public Surface

The public API in this chunk is the macro namespace itself. Consumer code includes this header and uses the generated names with AMDGPU bitfield helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, or related NBIO/PCIE indirect register access paths. The header does not enforce access width, read-only/write-only semantics, clear-on-write behavior, or reserved-bit preservation.

The covered macro families are source-tree-aligned with these address blocks:

- Tail of `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`: MSI-X table/PBA, vendor-specific PCIe extended capability, Advanced Error Reporting, enhanced BAR capability, power budget, Dynamic Power Allocation, ACS, PASID, ARI, TPH requester, and 64 TPH steering-table entries.
- Complete visible `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`: standard PCI endpoint header fields plus PM, USB-style `SBRN`/`FLADJ`/`DBESL_DBESLD`, PCIe device/link capabilities, MSI/MSI-X, vendor-specific capability, AER, enhanced BAR, power budget, DPA, ACS, PASID, ARI, TPH requester, and 64 TPH steering-table entries.
- Beginning of `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`: standard PCI endpoint header fields, PM capability, USB-style fields, PCIe capability/device/link fields, and the first half of `DEVICE_CAP2`.

## Important Macro Families

### MSI-X and Vendor-Specific Capability Fields

The chunk begins in the `DEV0_EPF2` MSI-X capability area. `MSIX_MSG_CNTL` exposes table size, function mask, and MSI-X enable fields, while `MSIX_TABLE` and `MSIX_PBA` split the BAR indicator and table/PBA offset fields. These masks define the PCI MSI-X capability layout, but Linux PCI interrupt setup and interrupt-remapping policy own most programming decisions.

The `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2` definitions expose the extended capability ID/version/next pointer, vendor-specific ID/revision/length, and scratch dwords. These are AMD/vendor extension points whose semantics are not described by the mask names beyond field position and width.

### Advanced Error Reporting

`DEV0_EPF2` and `DEV0_EPF3` both include complete AER field groups:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` for the AER extended capability header.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` for uncorrectable error status, masking, and fatal/non-fatal classification.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` for correctable receiver, bad TLP, bad DLLP, replay, advisory non-fatal, internal, and header-log-overflow errors.
- `PCIE_ADV_ERR_CAP_CNTL` for first-error pointer, ECRC generation/check capability and enables, multi-header receive capability/enable, TLP prefix log presence, and completion-timeout logging capability.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` for captured error context.

The uncorrectable status/mask/severity fields cover DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked cases. These are diagnostic and policy-sensitive fields: incorrect masks or severity bits can hide real PCIe failures or promote recoverable failures into fatal handling.

### Enhanced BAR, Power Budget, and DPA

`PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR1_CAP` through `PCIE_BAR6_CAP`, and `PCIE_BAR1_CNTL` through `PCIE_BAR6_CNTL` define enhanced BAR size capability and control fields. The control registers include BAR index, selected BAR size, total BAR count, and upper BAR-size-supported bits. These masks are relevant to config-space BAR sizing and may affect peer-to-peer, atomic, or function resource presentation depending on endpoint policy.

The power-budget block defines `DATA_SELECT`, `BASE_POWER`, `DATA_SCALE`, `PM_SUB_STATE`, `PM_STATE`, `TYPE`, `POWER_RAIL`, and `SYSTEM_ALLOCATED`. The DPA block defines dynamic power allocation capability, transition latency, substate status/control, and substate power allocation entries 0 through 7. Several DPA fields share packed registers in the matching offset header: status and control share one register, and the eight substate allocation fields are packed four per dword.

### ACS, PASID, and ARI

`PCIE_ACS_CAP` and `PCIE_ACS_CNTL` define source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-control vector size. These are isolation and routing controls; they interact with IOMMU policy, peer-to-peer access, and virtualization expectations.

`PCIE_PASID_CAP` and `PCIE_PASID_CNTL` define execution-permission support, privileged-mode support, max PASID width, and enable bits. `PCIE_ARI_CAP` and `PCIE_ARI_CNTL` define next-function number, multi-function/ACS function group support, function group selection, and related enables. These fields are identity and function-routing controls and should only be decoded or programmed for the endpoint function that owns the capability chain.

### TPH Requester and Steering Tables

The `PCIE_TPH_REQR_*` fields define TPH requester capability and control: no-ST, interrupt-vector, device-specific, and extended TPH modes; steering-table location and size; enable state; and steering table mode selection.

Both `DEV0_EPF2` and `DEV0_EPF3` include `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63`. Each table macro pair splits a lower and upper steering-tag entry, matching the packed dword layout in the offset header where two adjacent table entries often share one register offset. This pattern is a useful generated-data consistency check because a missing or shifted table entry can silently corrupt steering-tag programming.

### Standard PCI Endpoint Header and PCIe Capability Fields

The complete `DEV0_EPF3` block and the beginning of `DEV0_EPF4` define ordinary endpoint config-space fields: vendor/device ID, command/status, revision and class-code bytes, cache line size, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability list, and adapter ID word.

The `COMMAND` masks expose I/O space, memory space, bus mastering, special cycles, memory-write-invalidate, palette snoop, parity response, stepping, SERR, fast back-to-back, and interrupt disable. The `STATUS` masks expose interrupt status, capability-list presence, 66 MHz/fast-back-to-back capability, master data parity error, DEVSEL timing, target/master aborts, signaled system error, parity error, and immediate readiness.

The PM and PCIe capability sections define power-management capability/status/control, serial bus release/frame-length/BESL fields, PCIe capability header, device capability/control/status, link capability/control/status, and the start of device capability 2 for `DEV0_EPF4`. The selected chunk ends before the remaining `DEV0_EPF4_DEVICE_CAP2` masks and before `DEV0_EPF4_DEVICE_CNTL2`, so the later merge lane must combine adjacent chunks for a complete EPF4 analysis.

## Control Flow and State Behavior

There is no runtime control flow in this chunk. Its effective flow is compile-time substitution:

1. A C translation unit includes `nbio_7_2_0_sh_mask.h` and the matching offset header.
2. Code selects a `regBIF_CFG_*` offset and a `BIF_CFG_*__FIELD__SHIFT`/`_MASK` pair for the same NBIO generation.
3. AMDGPU helper code reads, writes, or updates a hardware register through the chosen MMIO, SOC15, or PCIe config access path.
4. Hardware or the PCI core observes the resulting config-space state.

The header owns no runtime state and persists nothing. The persistent state represented by these masks lives in NBIO PCI/PCIe configuration registers. Some fields are immutable capabilities, some are OS/firmware-owned control bits, some are sticky error status or log fields, and some trigger link, interrupt, power, routing, or function-level behavior when written. The macros do not express side effects such as write-one-to-clear AER status, write-preserve reserved bits, link retraining, FLR initiation, MSI/MSI-X delivery changes, PME status clearing, or BAR sizing probes.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.2 header set:

- `nbio_7_2_0_offset.h` supplies the register offsets and `BASE_IDX` values for the field names defined here.
- `nbio_7_2_0_sh_mask.h` supplies the bit positions and masks consumed by AMDGPU bitfield helpers.
- There is no observed `nbio_7_2_0_default.h` in this source tree, so reset-value validation must come from hardware documentation, register dumps, or other generated material outside the local NBIO 7.2 files.

Observed direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both the offset and mask headers, and DCN resource files that include the offset header. `amdgpu_discovery.c` selects `nbio_v7_2_funcs` for matching IP discovery, so these macros are valid only when the runtime ASIC uses the NBIO 7.2 register map.

The semantic dependencies are the PCI and PCI Express specifications for endpoint config space, PM capability, MSI/MSI-X, PCIe device/link capabilities, AER, enhanced BAR, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, and TPH requester behavior. Similar macro names appear in other NBIO generations, but the generated field set and offsets must be treated as generation-specific.

## Risks and Maintenance Notes

- Register-generation mismatch: using these NBIO 7.2 masks with another generation's offsets can decode or update the wrong bits even when names look similar.
- Endpoint-function confusion: `DEV0_EPF2`, `DEV0_EPF3`, and `DEV0_EPF4` share repeated field names but refer to different endpoint-function config spaces.
- Chunk boundary risk: the range starts after the first `DEV0_EPF2_MSIX_MSG_CNTL` shifts and ends mid-`DEV0_EPF4_DEVICE_CAP2`, so adjacent chunks are required for complete per-function reconciliation.
- Reserved-bit and access-width hazards: PCI config registers pack byte, word, and dword fields into shared storage; callers must preserve unrelated bits and use access widths appropriate to the target path.
- Interrupt regressions: MSI-X enable, function mask, table, and PBA fields can affect interrupt routing and must stay coordinated with PCI core and AMDGPU interrupt setup.
- Error-reporting regressions: AER status/mask/severity/log fields affect error visibility, clearing, and fatal classification.
- Isolation and virtualization risk: ACS, PASID, ARI, TPH, and enhanced BAR fields influence request identity, routing, P2P behavior, and IOMMU assumptions.
- Power and link instability: PM, DPA, completion timeout, LTR-related capability bits, OBFF-related `DEVICE_CAP2` bits, and link control/status fields interact with platform power management and PCIe link negotiation.
- Generated-header drift: manual edits are high risk because the apparent source of truth is an AMD register database; regenerated headers may overwrite local changes or expose one-line drift inside large repeated blocks.

## Test Signals

Useful validation signals for changes involving this chunk include:

- Build coverage for `amdgpu/nbio_v7_2.c` with both `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h` included.
- Static checks that every field macro used by NBIO 7.2 code has a matching register offset and base index in `nbio_7_2_0_offset.h`.
- Generated-data checks that `DEV0_EPF2` and `DEV0_EPF3` TPH steering tables include entries 0 through 63 with the expected lower/upper entry packing.
- Cross-header sanity checks that packed aliases in the offset header, such as DPA status/control, ACS capability/control, PASID capability/control, ARI capability/control, and paired TPH table entries, have non-overlapping masks in this header.
- Hardware or emulator register dumps on an NBIO 7.2 ASIC comparing decoded config-space values with `lspci -vvxxx`, AMDGPU debugfs register access, or known PCIe capability-chain layouts.
- Runtime testing that PCI enumeration, BAR assignment, MSI/MSI-X delivery, AER reporting/clearing, suspend/resume, FLR or GPU reset, and PCIe link training remain stable.
- Virtualization or IOMMU-oriented tests, where applicable, that validate ACS/PASID/ARI behavior and peer-to-peer routing assumptions.
- Error-injection or stress signals showing no new AER errors such as completion timeout, malformed TLP, receiver overflow, ECRC, unsupported request, ACS violation, or surprise down under GPU workloads.
