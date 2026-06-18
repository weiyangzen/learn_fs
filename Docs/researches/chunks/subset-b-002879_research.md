# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 4903-7323

## Purpose

This chunk is part of AMDGPU's generated NBIF 6.3.1 register bitfield mask header. It provides C preprocessor constants for bit shifts and masks used to access PCI configuration-space and PCIe extended-capability fields exposed through NBIF BIF config decoder address blocks. The macros are data definitions only: they do not execute logic, allocate state, or declare functions. Driver code includes this header alongside matching register-offset headers and uses the `*_SHIFT` and `*_MASK` constants to pack, unpack, set, and test fields in MMIO/config-register values.

The visible range covers virtual-function-oriented register definitions under `BIF_CFG_DEV0_EPF0_VF*`:

- The start of the chunk continues `VF4` PCIe capability definitions from a previous chunk, beginning at `BIF_CFG_DEV0_EPF0_VF4_PCIE_CAP__DEVICE_TYPE__SHIFT`.
- It completes the rest of `VF4` PCIe capability, MSI/MSI-X, vendor-specific, advanced error reporting, header log, TLP prefix log, and ARI mask definitions through `BIF_CFG_DEV0_EPF0_VF4_PCIE_ARI_CNTL`.
- It fully covers `addressBlock: nbif_bif_cfg_dev0_epf0_vf5_bifcfgdecp`.
- It fully covers `addressBlock: nbif_bif_cfg_dev0_epf0_vf6_bifcfgdecp`.
- It begins `addressBlock: nbif_bif_cfg_dev0_epf0_vf7_bifcfgdecp` and runs through the first `BIF_CFG_DEV0_EPF0_VF7_MSIX_MSG_CNTL__MSIX_TABLE_SIZE__SHIFT` macro; later `VF7` MSI-X and extended capability masks continue in the next chunk.

## Important Definitions

The exported API surface in this chunk is entirely macro names. Each register field usually has two macros:

- `...__FIELD__SHIFT`: bit index to shift a raw field value into or out of the register word.
- `...__FIELD_MASK`: bit mask for the encoded field within the register word.

Major register families in this chunk are:

- Standard PCI config header fields for `VF5`, `VF6`, and partially `VF7`: vendor/device IDs, command/status, revision/class, cache line, latency, header type, BIST, BARs, CardBus pointer, subsystem adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.
- PCI command/status fields: I/O, memory, bus mastering, special cycles, memory write invalidate, VGA palette snoop, parity/error enables, SERR, fast back-to-back, interrupt disable, and status bits such as capability list, interrupt status, devsel timing, target/master aborts, system error, parity error, and immediate read readiness.
- PCIe capability set for `VF4`-`VF7`: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI and MSI-X definitions: capability list headers, MSI enable and multi-message controls, 32/64-bit message address/data registers, per-vector masks and pending bits, MSI-X table/PBA BIR and offset fields, and function mask / enable bits.
- Vendor-specific PCIe enhanced capability headers and scratch registers.
- Advanced Error Reporting definitions for `VF4`-`VF6`: AER capability list headers, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- ARI enhanced capability definitions for `VF4`-`VF6`: MFVC function groups, ACS function groups, next-function number, and ARI forwarding controls.

No structs, enums, typedefs, or functions are defined in this range.

## Control Flow

There is no runtime control flow in this chunk. The practical "flow" is compile-time selection by macro name:

1. A consumer reads a register using the corresponding NBIF register offset from sibling generated headers.
2. It extracts a field with `(value & FIELD_MASK) >> FIELD_SHIFT`, or prepares an update by clearing `FIELD_MASK` and ORing a shifted field value.
3. It writes the resulting register value back through AMDGPU register access helpers.

The repetition across `VF5`, `VF6`, and `VF7` implies table-like hardware layout, but the header itself does not encode loops or iteration. Any iteration over virtual functions is handled by driver code that chooses the proper register offset and mask macro family.

## State and Persistence Behavior

This header does not hold software state. The state described by the macros lives in GPU/NBIF hardware registers and PCI configuration space. Many fields represent persistent or semi-persistent hardware configuration until reset, function-level reset, power transition, or firmware/hardware update, including BAR base addresses, command enables, link controls, MSI/MSI-X configuration, and AER masks/severity selections.

Several status/log fields are hardware-owned observations rather than driver-owned state:

- `DEVICE_STATUS`, `LINK_STATUS`, and `LINK_STATUS2` expose current PCIe link and transaction state.
- AER status registers report correctable and uncorrectable error conditions.
- header log and TLP prefix log registers capture error context.
- MSI pending registers expose pending interrupt-vector state.

Some fields can be write-one-to-clear or otherwise have PCIe-defined side effects in the underlying hardware, but this header does not document those semantics. Consumers must rely on PCIe/NBIF programming rules and existing AMDGPU access wrappers.

## Dependencies and Integration Points

The chunk depends only on the C preprocessor. It is intended to be included by AMDGPU NBIF and PCIe code together with generated register-offset headers for the same ASIC generation, commonly named in the same `asic_reg/nbif` area. The mask names are tightly coupled to the register names in those offset headers; using a mask with the wrong offset family can silently target the wrong bits.

Integration points include:

- AMDGPU NBIF initialization and reset paths that configure PCIe device, link, and function-level behavior.
- SR-IOV / virtual function handling, because the covered register blocks are `VF4` through `VF7`.
- PCIe error reporting paths that inspect or mask AER status for DLP, surprise-down, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, atomic-op egress blocking, TLP prefix blocking, and poisoned TLP egress blocking.
- Interrupt setup paths for MSI/MSI-X message address/data, vector masks, pending bits, table location, PBA location, and enable/function-mask control.
- Link-management diagnostics and policy code that reads current speed/width/training state or adjusts target speed, compliance mode, autonomous speed/width disable, ASPM/power management, common clock, extended sync, DRS signaling, and equalization-related status.

Because this is generated ASIC data, the source of truth is likely an AMD register database rather than handwritten driver logic. Edits should be treated as hardware contract changes.

## Risks

- Boundary risk: this chunk starts after the `VF4_PCIE_CAP__VERSION__SHIFT` macro and ends before the rest of `VF7_MSIX_MSG_CNTL`; the final merged report must combine adjacent chunks to avoid presenting partial VF4/VF7 coverage as complete.
- Copy/paste or generation drift can be severe. `VF5` and `VF6` are structurally identical in this span, while `VF7` is partial here. A single wrong mask width, shift, or suffix can cause register writes to corrupt adjacent PCIe fields.
- Several mask names include repeated semantic words, such as `...PCIE_UNCORR_ERR_MASK__DLP_ERR_MASK_MASK`; this is expected from `register__field_MASK` naming and should not be "cleaned up" manually.
- Width differences matter. Some fields are 16-bit PCI config words (`0xFFFFL`-style masks), while others are 32-bit capability or log dwords (`0xFFFFFFFFL`). Consumers must use access widths matching the actual register definition.
- AER and status/log fields may have side effects on write or clear operations. The macros do not protect against unsafe read-modify-write behavior.
- MSI/MSI-X fields affect interrupt delivery. Incorrect enable, function mask, table BIR, table offset, PBA BIR, or message address/data masks can produce lost interrupts, spurious interrupts, or device isolation issues under virtualization.
- SR-IOV-specific register access must respect function isolation. Accidentally applying a `VF5` macro to a `VF6`/`VF7` offset, or vice versa, is syntactically valid C but semantically wrong.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Build coverage for AMDGPU with this generated header included, especially configurations that enable SR-IOV, NBIF, PCIe AER, MSI, and MSI-X paths.
- Static checks that every `__SHIFT`/`_MASK` pair has consistent field width and no overlap within a register block unless overlapping is hardware-intended.
- Generated-header consistency checks against the ASIC register database or against sibling `nbif_6_3_1` offset/default headers.
- Runtime smoke tests that enumerate the GPU and its virtual functions, read PCI config capability lists, and verify expected PCIe/PCI capability traversal.
- MSI/MSI-X interrupt tests under physical and virtualized GPU configurations.
- PCIe link-state diagnostics confirming reported speed, width, training, equalization, and DRS bits match hardware/firmware expectations.
- AER injection or fault-observation tests, where available, confirming uncorrectable/correctable status, masks, severity, header logs, and TLP prefix logs decode to the expected bit names.

## Chunk-Specific Notes for Merge

This chunk should be merged with adjacent chunks for the same source file before producing the final source-tree-aligned per-file research document. The merge should preserve that the source file as a whole is a generated NBIF 6.3.1 shift/mask catalog, while this chunk specifically represents `VF4` tail coverage, full `VF5`/`VF6` coverage, and `VF7` early coverage through the start of MSI-X message control.
