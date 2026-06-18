# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 9752-12200

## Scope

This chunk covers a generated NBIO 6.1 register shift/mask header section for PCIe BIF configuration-space fields on SR-IOV virtual functions. The range starts inside the tail of the `BIF_CFG_DEV0_EPF0_VF5_0` block, covers full `BIF_CFG_DEV0_EPF0_VF6_0` and `BIF_CFG_DEV0_EPF0_VF7_0` blocks, covers most of `BIF_CFG_DEV0_EPF0_VF8_0`, and ends at the beginning of the `BIF_CFG_DEV0_EPF0_VF9_0_PCIE_CAP` field list.

The file is a generated hardware register bitfield map. It defines C preprocessor constants only: no functions, structs, variables, storage, persistence layer, or executable control flow are present in this chunk.

## Purpose

The purpose of this chunk is to provide bit offsets and masks for NBIO/BIF PCI configuration registers associated with GPU virtual functions. Each field follows the AMDGPU register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.

Driver code combines these constants with AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET`. The paired address definitions live in `nbio_6_1_offset.h`, where the same `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` register names map to PCI configuration offsets. This chunk supplies the field layout for those offsets.

## Covered Register Families

The covered virtual-function blocks are mostly repeated per VF, with the VF number embedded in each macro prefix:

- `BIF_CFG_DEV0_EPF0_VF5_0`: tail of PCIe capability v2, MSI/MSI-X, vendor-specific capability, advanced error reporting, ATS, and ARI definitions.
- `BIF_CFG_DEV0_EPF0_VF6_0`: full PCI configuration, PCIe capability, MSI/MSI-X, AER, ATS, and ARI definitions.
- `BIF_CFG_DEV0_EPF0_VF7_0`: full equivalent register map for VF7.
- `BIF_CFG_DEV0_EPF0_VF8_0`: full equivalent map through ARI control.
- `BIF_CFG_DEV0_EPF0_VF9_0`: start of the equivalent map through the first four `PCIE_CAP` field shifts.

The repeated layout covers standard PCI header fields (`VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class fields, `HEADER`, `BIST`, BARs, subsystem adapter IDs, ROM BAR, capability pointer, and interrupt line/pin) plus PCIe extended capabilities that are relevant when the device is exposed as a virtual function.

## Important Macros and Field Groups

### PCI Header and Command/Status Fields

For full VF blocks, the first section maps standard PCI configuration header fields:

- `COMMAND` fields: I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, palette snoop, parity response, SERR, fast back-to-back, and interrupt-disable bits.
- `STATUS` fields: interrupt status, capability-list presence, parity/target/master/system error bits, and `DEVSEL_TIMING`.
- Identification/class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- BAR and identity fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `ADAPTER_ID`, `ROM_BASE_ADDR`, and `CAP_PTR`.

These fields describe the PCI config-space ABI that host PCI enumeration, guest VF drivers, and virtualization management rely on.

### PCIe Capability Fields

The `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` families expose the normal PCIe capability structure. Notable fields include:

- Device capabilities such as maximum payload support, extended tags, accepted L0s/L1 latencies, role-based error reporting, captured slot power, and FLR capability.
- Device controls such as correctable/non-fatal/fatal error reporting enables, relaxed ordering, max payload size, max read request size, no-snoop, extended tags, and `INITIATE_FLR`.
- Link capability/control/status fields for link speed, width, ASPM/power management, retraining, common clock, link bandwidth notification, link training, slot clock, data-link active, and bandwidth status.

The v2 PCIe fields add completion-timeout controls, ARI forwarding, atomic operation support/control, ID-based ordering, LTR enablement, OBFF, TLP prefix support/blocking, supported link speeds, compliance controls, de-emphasis, and equalization status bits.

### MSI and MSI-X

The MSI section defines:

- `MSI_CAP_LIST` capability ID and next-pointer fields.
- `MSI_MSG_CNTL` enable, multi-message capability/enable, 64-bit capability, and per-vector masking capability.
- Message address/data registers and mask/pending registers for both 32-bit and 64-bit layouts.

The MSI-X section defines:

- `MSIX_CAP_LIST` capability ID and next pointer.
- `MSIX_MSG_CNTL` table size, function mask, and enable bits.
- `MSIX_TABLE` and `MSIX_PBA` BAR-indicator and offset fields.

These fields are central to interrupt setup for VFs. Incorrect masks or shifts would cause interrupt enablement, vector masking, table location, or pending-bit interpretation to break.

### Vendor-Specific and Advanced Error Reporting

The vendor-specific capability fields map `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and two scratch registers. The capability-list macros expose capability ID, version, next pointer, VSEC ID, revision, and length.

The AER section maps:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` capability metadata.
- Uncorrectable error status/mask/severity fields, including DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP prefix blocked bits.
- Correctable error status/mask fields for receiver errors, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, internal correctable error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`, including first-error pointer, ECRC generation/check capability and enable bits, multi-header recording, and TLP prefix log presence.
- Header log and TLP prefix log registers with full-width data masks.

This is the main diagnostic and reliability surface in the chunk. Consumers must distinguish status bits, mask bits, and severity bits, because they share nearly identical bit positions but change hardware behavior differently.

### ATS and ARI

The ATS capability macros define capability-list metadata, invalidate queue depth, page-aligned request support, global invalidate support, the smallest translation unit (`STU`), and `ATC_ENABLE`.

The ARI capability macros define capability-list metadata, MFVC/ACS function group capability and enable bits, next function number, and ARI function group selection.

These fields integrate with IOMMU/PCIe virtualization features. They are especially sensitive in VF contexts because ATS and ARI state affects address translation, function routing, and isolation behavior.

## Control Flow

There is no runtime control flow in this chunk. The only structure is the generated order of register comments followed by shift and mask definitions. Runtime behavior appears in downstream driver code that includes this header and uses the macros to compose or decode register values.

The implicit operational flow for consumers is:

1. Select a register address from `nbio_6_1_offset.h`.
2. Read or write it through an AMDGPU MMIO/PCI config helper.
3. Use this header's `__SHIFT` and `_MASK` constants directly or indirectly through field helpers.
4. Let hardware maintain the resulting PCIe/VF state.

## State and Persistence Behavior

This header stores no state. The state described by the macros lives in device hardware registers and PCI configuration space. Some fields are durable configuration until reset or reprogramming, such as BARs, command bits, MSI/MSI-X enables, AER masks/severity settings, ATS controls, and ARI controls. Other fields are live status or event-latch surfaces, such as PCI status errors, device/link status, AER status bits, MSI pending bits, and equalization status.

The chunk also includes command-like fields such as `INITIATE_FLR`, link retraining/compliance controls, AER ECRC enables, `ATC_ENABLE`, and ARI function-group enables. Writes to these fields can trigger hardware actions or alter VF-visible behavior, so they should not be treated as passive metadata.

## Dependencies and Integration Points

Primary dependencies and consumers are:

- `nbio_6_1_offset.h`, which supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. This chunk supplies the per-field masks for those offsets.
- `amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_sh_mask.h` and demonstrates the usual NBIO pattern of reading/writing registers with `RREG32*`, `WREG32*`, `WREG32_FIELD15`, and `REG_SET_FIELD`.
- `amdgpu/mxgpu_ai.c`, which includes the same NBIO headers for SR-IOV/MxGPU flows and mailbox handling around PF/VF coordination.
- Power-management include aggregators such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`, which include this generated header for ASIC-specific register access.

The macros in this exact range are most likely used where code needs VF-specific PCI configuration, error-reporting, interrupt, ATS, or ARI field manipulation. Even when direct references are sparse, the definitions are part of the generated public register vocabulary for NBIO 6.1 ASIC support.

## Risks

- **Generated-header drift:** Hand-editing masks or shifts can desynchronize this header from ASIC register XML/source generation and from `nbio_6_1_offset.h`.
- **VF isolation bugs:** Mistakes in ATS, ARI, BAR, bus-master, memory-access, or interrupt fields can affect guest-visible device behavior and isolation.
- **Interrupt misconfiguration:** MSI/MSI-X table, PBA, mask, pending, and enable fields use overlapping capability layouts; a wrong field width or offset can disable vectors or point tables at the wrong BAR offset.
- **AER semantic confusion:** AER status, mask, and severity registers have matching bit names and positions but different write semantics. Reusing the wrong macro family would change error masking or severity instead of observing/clearing status.
- **Partial chunk boundaries:** The assigned range starts in the middle of VF5 and ends in the middle of VF9. Any final per-file report must reconcile this chunk with neighboring chunks before making whole-file completeness claims.
- **Privilege/context assumptions:** Some registers describe VF-visible PCI config state, but PF, hypervisor, or firmware-managed paths may own parts of the actual programming sequence.

## Test Signals

Useful validation signals for this header chunk are mostly compile-time and hardware-integration oriented:

- Kernel build coverage for AMDGPU/NBIO 6.1 users that include `nbio_6_1_sh_mask.h`.
- Static checks that every `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offset used for these blocks has matching `__SHIFT`/`_MASK` macros in this header.
- SR-IOV smoke tests where VFs enumerate correctly, BARs are visible, bus mastering/memory access works, and FLR completes.
- Guest interrupt tests using both MSI and MSI-X paths, including vector masking and pending-bit behavior.
- PCIe AER injection or error-reporting tests that verify correctable/uncorrectable status, masks, severities, and header logs are interpreted correctly.
- ATS/ARI/IOMMU tests under virtualization, checking that address translation, function numbering, and function group controls remain isolated per VF.
- Link capability/status inspection with `lspci -vv` or equivalent diagnostic tooling to confirm advertised payload, link, LTR/OBFF, and capability-list fields match expected NBIO 6.1 hardware behavior.
