# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 73586-76008

## Scope

This chunk covers a generated NBIO 2.3 shift/mask header range for AMDGPU PCIe/NBIO configuration-space registers. It starts in the middle of the `BIF_CFG_DEV0_EPF0_VF22_0` MSI/MSI-X and PCIe extended capability definitions, covers complete virtual-function configuration mask blocks for `VF23`, `VF24`, and `VF25`, and ends at the `BIF_CFG_DEV0_EPF0_VF26_0_PROG_INTERFACE` comment after defining the first `VF26` standard PCI configuration fields.

The file is a preprocessor-only register bitfield map. This chunk defines constants only: no C functions, structs, variables, storage, or executable control flow are present here.

## Purpose

The purpose of this section is to expose bit positions and masks for NBIO/BIF PCI configuration registers associated with SR-IOV virtual functions. Each field follows the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the mask for extracting or composing that field.

The sibling offset header supplies register addresses; this `*_sh_mask.h` header supplies the field encodings used with AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`. Local includes of `nbio/nbio_2_3_sh_mask.h` appear in `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`, so these macros can be consumed by NBIO control, SR-IOV, and platform/power code that needs SOC15 register field encodings.

## Important Macro Families

### VF22 Tail: MSI-X, Vendor Capability, AER, ATS, and ARI

The chunk begins at line 73586 with the tail of `BIF_CFG_DEV0_EPF0_VF22_0`. Covered `VF22` definitions include:

- MSI pending and 64-bit pending/mask fields.
- MSI-X capability list, message control, table, and pending bit array fields, including table size, function mask, enable bit, BAR indicator register fields, and table/PBA offsets.
- PCIe vendor-specific enhanced capability list/header fields with `CAP_ID`, `CAP_VER`, `NEXT_PTR`, `VSEC_ID`, `VSEC_REV`, and `VSEC_LENGTH`.
- Vendor scratch registers `PCIE_VENDOR_SPECIFIC1` and `PCIE_VENDOR_SPECIFIC2`.
- PCIe Advanced Error Reporting capability list plus uncorrectable status, uncorrectable mask, uncorrectable severity, correctable status, correctable mask, advanced error capability/control, TLP header logs, and TLP prefix logs.
- ATS enhanced capability, ATS capability/control, ARI enhanced capability, ARI capability, and ARI control fields.

The AER groups use the standard PCIe error bit families: data link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic operation egress blocked, and TLP prefix blocked. For each field, this header provides the same bit position across status, mask, and severity registers.

### Complete VF23, VF24, and VF25 Blocks

Lines 73860-75947 define full `addressBlock` sections for `nbio_nbif0_bif_cfg_dev0_epf0_vf23_bifcfgdecp`, `vf24_bifcfgdecp`, and `vf25_bifcfgdecp`. These three blocks are structurally repetitive and map a virtual function's PCI/PCIe configuration-space view.

The standard PCI header fields include:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: I/O access, memory access, bus mastering, special cycle, memory write invalidate, palette snoop, parity response, SERR, fast back-to-back, interrupt disable, interrupt status, capability-list presence, target/master abort status, system error, parity error, and DEVSEL timing.
- Header/runtime fields: cache line, latency, header type, BIST, six base address registers, CardBus CIS pointer, adapter/subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.

The PCIe capability portions include:

- `PCIE_CAP_LIST` and `PCIE_CAP`, with capability ID/next pointer, PCIe capability version, device/port type, slot/interrupt-message number, and related capability metadata.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS`, covering max payload, phantom functions, extended tag, endpoint L0s/L1 latency, attention/button/power indicators, role-based error reporting, captured slot power limits, correctable/non-fatal/fatal/unsupported-request error enables, relaxed ordering, max payload/request sizing, no-snoop, auxiliary power, transactions pending, and related status bits.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`, covering supported link speed/width, ASPM and L0s/L1 exit latency, clock power management, surprise-down reporting, data-link active reporting, port number, common clock, retraining, disable, link bandwidth management, negotiated speed/width, training state, slot clock, and bandwidth notification state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, covering completion timeout support/control, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, 10-bit tag support, end-to-end TLP prefixes, emergency power reduction, supported/current/deemphasis link speeds, equalization controls, compliance/SOS vectors, and equalization phase completion bits.

### Interrupt Capability Fields

For `VF23` through `VF25`, the chunk defines MSI and MSI-X register masks:

- MSI capability list and message control fields encode capability ID, next pointer, MSI enable, multi-message capable/enable, 64-bit address capability, per-vector masking capability, and extended message data capability.
- MSI message address low/high, message data, mask, mask64, pending, pending64, and 64-bit message-data fields are represented as full-width payload masks where appropriate.
- MSI-X capability list and message control fields encode table size, function mask, and MSI-X enable.
- MSI-X table and PBA fields split BAR indicator register bits from table/PBA offsets.

These masks are the low-level contract used when driver code reads, mirrors, masks, or composes virtual-function interrupt capability registers. The header does not decide policy such as whether MSI/MSI-X is enabled; it only describes field layout.

### PCIe Advanced Error Reporting

For each complete VF block, the chunk defines:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, with enhanced capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`, sharing the same uncorrectable error bit layout.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`, with receiver, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal, and header-log-overflow fields.
- `PCIE_ADV_ERR_CAP_CNTL`, including first error pointer, ECRC generation/check capability and enable bits, multiple-header recording capability/enable bits, TLP-prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3`, each exposing full 32-bit captured log words.

AER status and log registers are hardware stateful: status bits may be sticky or clear-on-write according to PCIe/NBIO behavior, while log registers capture error context. These macros do not encode clear semantics or ordering; consumers must follow the PCIe/AER handling code and hardware specification.

### ATS and ARI

For `VF23` through `VF25`, ATS definitions include:

- `PCIE_ATS_ENH_CAP_LIST`, with enhanced capability ID/version/next pointer fields.
- `PCIE_ATS_CAP`, with invalidate queue depth, page-aligned request, and global invalidate support.
- `PCIE_ATS_CNTL`, with smallest translation unit and ATC enable.

ARI definitions include:

- `PCIE_ARI_ENH_CAP_LIST`, with enhanced capability ID/version/next pointer fields.
- `PCIE_ARI_CAP`, with MFVC and ACS function-group capability bits plus next function number.
- `PCIE_ARI_CNTL`, with MFVC/ACS function-group enables and function group selection.

These fields integrate NBIO virtual functions with PCIe address translation and alternate routing capabilities. Incorrect interpretation can affect IOMMU/ATS enablement, function enumeration, or virtual-function routing behavior.

### VF26 Prefix

Lines 75948-76008 begin the `VF26` address block and define its first standard configuration fields:

- `VENDOR_ID` and `DEVICE_ID`.
- `COMMAND`, with I/O, memory, bus-master, special-cycle, memory-write-invalidate, palette-snoop, parity-response, SERR, fast-back-to-back, and interrupt-disable fields.
- `STATUS`, with interrupt/status, capability-list, error, abort, DEVSEL, readiness, and parity fields.
- `REVISION_ID`.

The chunk ends at the `PROG_INTERFACE` comment before that field's `SHIFT` and `MASK` definitions, so the remainder of the `VF26` block belongs to the next chunk.

## APIs, Types, and Functions

There are no callable APIs, types, or functions in this chunk. The exported interface is the macro namespace itself. Its naming encodes register ownership:

- `BIF_CFG_DEV0_EPF0` identifies the bus interface configuration space for device 0, endpoint function 0.
- `VF22`, `VF23`, `VF24`, `VF25`, and `VF26` identify SR-IOV virtual-function configuration blocks.
- The trailing register and field names identify the PCI, PCIe, MSI/MSI-X, AER, ATS, ARI, or vendor-specific register field.

The macros are compile-time constants. They are normally paired with register offsets from the matching NBIO 2.3 offset header and with common AMDGPU register manipulation helpers.

## Control Flow and State Behavior

This header section has no runtime control flow. Its effect is indirect: driver C code includes it, then uses the constants to read or write individual bitfields in NBIO/PCIe hardware registers.

The state represented here is hardware or PCI configuration-space state, not persistent software state in the header. Important state classes include:

- VF identity, class, command, status, BAR, ROM, interrupt, and capability-pointer fields.
- PCIe link/device capabilities and controls, including link speed/width, payload sizes, ASPM, retraining, error reporting, ordering, atomics, LTR, OBFF, and equalization.
- MSI/MSI-X address/data/mask/pending/table/PBA configuration.
- AER status, masks, severity, capability control, and captured TLP/prefix logs.
- ATS and ARI capability/control state.
- Vendor-specific capability metadata and scratch fields.

Some fields are ordinary read/write controls, some are read-only capabilities, and some are status/log fields with hardware-defined clear or latch behavior. The macro file does not distinguish access type; that knowledge must come from the hardware specification and the driver paths that use the fields.

## Dependencies and Integration Points

The chunk depends only on the C preprocessor and the broader AMDGPU register-header convention. It has no include dependencies beyond the guard surrounding the full header.

Integration points visible in the tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes the NBIO 2.3 register headers for NBIO programming.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes the same header family for SR-IOV/MxGPU paths.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include NBIO 2.3 masks alongside SMU11 power-management code.
- Matching NBIO offset headers, which provide register addresses for the mask/shift names defined here.
- AMDGPU register helper macros that consume `__SHIFT` and `_MASK` values to compose and extract fields.

Because this range is deeply repetitive across virtual functions, generated consistency with adjacent `VF` blocks is part of the integration contract. A wrong value in one VF block can make code touch or decode a different bit than the same-named field in neighboring VFs.

## Risks

- Generated-header drift is the main risk. If the mask header and matching offset/header generation are out of sync with the ASIC register database, driver code will compile but program the wrong bitfields.
- The chunk starts and ends mid-block. Merge/reconciliation must preserve that `VF22` is partial at the start and `VF26` is partial at the end; whole-file research should not infer that those VF blocks are complete from this chunk alone.
- Many fields describe privileged or virtualized PCIe state. Misprogramming `COMMAND`, bus mastering, BARs, MSI/MSI-X, ATS, ARI, or AER masks can break VF enumeration, interrupt delivery, DMA, IOMMU translation, error handling, or isolation.
- AER and interrupt status fields may have sticky or write-one-to-clear behavior in hardware. The macros alone cannot prevent unsafe read-modify-write sequences.
- Repetition across `VF23`, `VF24`, and `VF25` makes copy/generation errors hard to notice in review; automated comparisons against the source register database or neighboring VF blocks are more reliable than manual inspection.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Kernel/driver build coverage for files including `nbio_2_3_sh_mask.h`; macro spelling or duplicate-definition problems should surface at compile time.
- Static checks or generated-header comparison against AMD's NBIO 2.3 register source data, especially for repeated VF blocks.
- SR-IOV smoke tests that enumerate VFs around this range and verify PCI config space identity, command/status, BARs, MSI/MSI-X capability layout, and capability-list traversal.
- Interrupt tests that exercise MSI and MSI-X enable/mask/pending paths for VFs.
- PCIe AER tests or fault-injection diagnostics that confirm correct decoding of correctable/uncorrectable status, masks, severity, and header-log fields.
- ATS/ARI enablement tests under IOMMU/SR-IOV configurations, checking that ATC enable, STU, next-function, and ARI function-group fields are interpreted consistently.
- Register readback tests comparing `REG_GET_FIELD` extraction against expected raw config-space values for representative `VF23`, `VF24`, and `VF25` registers.
