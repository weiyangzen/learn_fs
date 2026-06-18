# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 12318-14799

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2 shift/mask header. It defines C preprocessor constants for decoding and composing bitfields in NBIO/BIF PCI configuration-space register images. The source path sits under a Ceph client mirror, but the visible code is AMD GPU register metadata, not distributed-filesystem logic.

The range contains 2,126 `#define` entries across PCI/PCIe register comment blocks. The definitions follow the generated convention:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position of a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

At a high level, this chunk covers the tail of device 0 endpoint/function 5 (`BIF_CFG_DEV0_EPF5`), a complete visible device 0 endpoint/function 6 address block (`nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp` / `BIF_CFG_DEV0_EPF6`), and the first lines of the PCIe physical-layer/root-style block (`nbio_pcie0_bifplr0_cfgdecp` / `BIFPLR0`).

## Important APIs, Types, and Macros

There are no functions, structs, classes, typedefs, or enums in this chunk. Its only API surface is the exported macro namespace consumed by AMDGPU register access code.

The initial `DEV0_EPF5` section begins mid-register, with masks for `BIF_CFG_DEV0_EPF5_PMI_STATUS_CNTL` fields such as `POWER_STATE`, `NO_SOFT_RESET`, `PME_EN`, `DATA_SELECT`, `DATA_SCALE`, `PME_STATUS`, `B2_B3_SUPPORT`, `BUS_PWR_EN`, and `PMI_DATA`. The matching shift definitions for that register are in the previous chunk.

The visible `DEV0_EPF5` tail then defines field geometry for:

- PCIe and power-management capability headers: `SBRN`, `FLADJ`, `DBESL_DBESLD`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`.
- PCIe capability 2/control 2/status 2/link 2 registers, including completion-timeout, ARI forwarding, atomic operations, LTR, OBFF, ID ordering, E2E TLP prefix blocking, target link speed, autonomous speed disable, de-emphasis, equalization, and lane/equalization state fields.
- MSI and MSI-X capability fields: message control, message address/data, masks, pending bits, table offsets, BIR selectors, and PBA offsets.
- Vendor-specific enhanced capability fields.
- PCIe Advanced Error Reporting: uncorrectable status, masks, severity, correctable status, correctable masks, advanced error capability/control, TLP header logs, and TLP prefix logs.
- Enhanced BAR capability/control entries for BAR1 through BAR6.
- Power budgeting and Dynamic Power Allocation: base power, data scale, PM state/substate, rail/type, substate maximum, transition latency, control/status, and eight substate power allocation registers.
- Access Control Services, PASID, and ARI capability/control registers.
- TPH requester support: enhanced capability list, requester capability/control, steering mode selection, requester enable, and 64 steering table entries. Each steering table entry has lower and upper 8-bit fields.

The `DEV0_EPF6` address block starts at line 13459 and repeats the same generated PCI function shape for endpoint/function 6. It includes:

- Standard PCI configuration header fields: vendor ID, device ID, command, status, revision ID, class code, cache line, latency, header type, BIST, BAR1-BAR6, CardBus CIS pointer, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, minimum grant, maximum latency, vendor capability list, and writable adapter ID.
- Power-management fields: PMI capability list, version, PME clock/support, D1/D2 support, auxiliary current, power state, PME enable/status, data select/scale, bridge power bits, and PM data.
- PCIe endpoint capability/control/status and link capability/control/status blocks, plus the capability 2/control 2/status 2/link 2 extension blocks.
- MSI/MSI-X, vendor-specific enhanced capability, AER, header/prefix logs, enhanced BAR, power-budget, DPA, ACS, PASID, ARI, and TPH requester/steering table definitions.

The final `BIFPLR0` section begins at line 14775. This chunk only includes `BIFPLR0_VENDOR_ID`, `BIFPLR0_DEVICE_ID`, and the beginning of `BIFPLR0_COMMAND` through `PAL_SNOOP_EN_MASK`; remaining `BIFPLR0_COMMAND` masks and later BIFPLR0 fields are outside this work item.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It contributes constants at compile time. Runtime behavior appears only when consumers combine these constants with NBIO 7.2 register offsets and register read/modify/write helpers.

The implied hardware flows are:

1. PCI/PCIe enumeration or ASIC initialization reads identity, class, BAR, ROM, capability-list, interrupt, and header fields.
2. Driver setup writes command, PM, PCIe device control, link control, MSI/MSI-X, BAR, ACS, PASID, ARI, DPA, power-budget, and TPH policy bits.
3. Error handling reads or clears PCI/PCIe status and AER fields, applies mask/severity policy, and decodes logged TLP header/prefix dwords.
4. Power-management paths inspect or program ASPM, LTR, OBFF, PM D-states, power-budget records, and DPA substates.
5. Virtualization and isolation paths use ACS, PASID, ARI, and TPH fields to control request routing, process address spaces, and steering-tag behavior.

The file itself does not enforce legal values, sequence hardware operations, clear sticky bits, or serialize access. Those semantics live in AMDGPU/NBIO driver code and in the hardware specification.

## State and Persistence

The chunk owns no memory, no locks, no persistent files, and no runtime state. The state represented by these macros is hardware state in PCI configuration-space or NBIO/BIF register images.

State categories represented here include:

- Enumeration state: vendor/device IDs, revision and class codes, header type, BAR values, ROM base, capability pointers, and interrupt routing fields.
- Configuration policy: command enables, bus mastering, memory/IO enablement, error-reporting enables, MSI/MSI-X enablement, device/link controls, payload/read-request sizes, no-snoop, relaxed ordering, link retraining, ASPM, and target speed.
- Error state and policy: PCI status bits, AER uncorrectable/correctable status, error masks, severity selection, ECRC controls, first-error pointer, header logs, and TLP prefix logs.
- Power/performance state: PM D-state, PME enable/status, LTR/OBFF, power-budget descriptors, DPA substates, power allocation, and transition latency.
- Isolation/routing state: ACS controls, PASID enablement and width, ARI next-function/function-group fields, TPH requester enablement, steering table location/size, and steering table entries.

Persistence across FLR, GPU reset, suspend/resume, BACO, runtime power transitions, or PCI reset is not described by the header. If a shift or mask is wrong, the compiled driver will consistently decode or program the wrong bits until the generated header is fixed and rebuilt.

## Dependencies and Integration Points

The direct companion file in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, which supplies register offsets for the same NBIO 7.2 register map. No matching `nbio_7_2_0_default.h` or `nbio_7_2_0_smn.h` was present in the inspected `nbio` directory.

Likely integration areas include:

- AMDGPU NBIO 7.2 ASIC initialization and low-level register access paths.
- PCIe configuration and link-management code that decodes or programs endpoint/function PCI configuration images.
- Interrupt setup for MSI and MSI-X capabilities.
- RAS, PCIe AER, reset, and recovery paths that inspect error status, masks, severity, ECRC, and TLP logs.
- Power-management paths that handle PM capabilities, ASPM, LTR, OBFF, power-budgeting, and DPA controls.
- IOMMU/virtualization/isolation paths that depend on ACS, PASID, ARI, and TPH steering behavior.

Integration is by exact symbol spelling. `BIF_CFG_DEV0_EPF5_*`, `BIF_CFG_DEV0_EPF6_*`, and `BIFPLR0_*` are different register namespaces even when many fields have identical layouts.

## Risks

- Chunk boundaries split register definitions. This range starts with only `DEV0_EPF5_PMI_STATUS_CNTL` masks and ends partway through `BIFPLR0_COMMAND`; adjacent chunks are required for pair-completeness checks.
- The repeated endpoint/function layouts make copy/paste or wrong-prefix use easy. A valid-looking `DEV0_EPF5` mask applied to a `DEV0_EPF6` offset would target the wrong function image.
- AER status, mask, and severity registers use near-identical field names. Confusing them can suppress real errors, misclassify fatal/nonfatal conditions, or corrupt diagnostics.
- PCIe control fields such as payload size, read request size, relaxed ordering, no-snoop, ASPM, target speed, LTR, OBFF, ACS, PASID, ARI, and TPH alter bus behavior. Incorrect masks can cause enumeration failures, link instability, performance regressions, or DMA isolation problems.
- MSI/MSI-X table and PBA fields combine offset and BIR subfields. Bad decoding can point interrupt setup at the wrong BAR or vector table.
- TPH requester support includes dense, repetitive steering table entries. Off-by-one table indexing or wrong table-size interpretation can steer transactions incorrectly.
- `0xFFFFFFFFL` and other `L`-suffixed masks rely on normal C integer-width handling in consumers. Register code should continue using the unsigned 32-bit conventions used elsewhere in AMDGPU generated headers.

## Test and Validation Signals

Useful validation is mostly mechanical plus hardware/emulator coverage:

- Build AMDGPU configurations that include `nbio_7_2_0_sh_mask.h` to catch syntax errors, duplicate definitions, or missing macro references.
- After adjacent chunk merge, verify every field has a matching `__SHIFT` and `_MASK` pair. Expected local boundary exceptions are the starting `DEV0_EPF5_PMI_STATUS_CNTL` masks and the ending partial `BIFPLR0_COMMAND` masks.
- Cross-check visible register names against `nbio_7_2_0_offset.h` so each field macro has the expected address/offset macro.
- Run generated-header symmetry checks between the visible `DEV0_EPF5` tail and `DEV0_EPF6` block for common PCIe, MSI/MSI-X, AER, BAR, power, DPA, ACS, PASID, ARI, and TPH fields.
- Decode PCI config-space dumps from NBIO 7.2 hardware for `DEV0_EPF5`, `DEV0_EPF6`, and `BIFPLR0` and compare field extraction against expected capability chains.
- Exercise controlled PCIe AER paths and confirm status, mask, severity, first-error pointer, ECRC, header log, and prefix log decoding.
- Validate interrupt setup by checking MSI/MSI-X message control, address/data, vector masks, pending bits, table offsets, BIR values, and PBA values.
- Validate power-management and link-management flows across suspend/resume, runtime power transitions, FLR, and link retraining to confirm policy bits are restored and decoded as expected.
- Validate ACS/PASID/ARI/TPH paths under IOMMU or virtualization configurations, checking request isolation, PASID width/enablement, ARI function routing, and TPH steering table programming.

## Chunk Boundary Notes

Lines 12318-12326 are the end of `BIF_CFG_DEV0_EPF5_PMI_STATUS_CNTL`; their shifts are in the previous chunk. Lines 12327-13456 complete the visible `DEV0_EPF5` tail from `SBRN` through `PCIE_TPH_ST_TABLE_63`. Lines 13459-14772 cover the visible `DEV0_EPF6` block from `VENDOR_ID` through `PCIE_TPH_ST_TABLE_63`. Lines 14775-14799 start the next `BIFPLR0` address block and stop inside `BIFPLR0_COMMAND`.
