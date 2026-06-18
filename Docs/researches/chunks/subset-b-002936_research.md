# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 78433-80987

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains only C preprocessor constants and grouping comments; it declares no functions, structs, variables, inline helpers, storage, locks, or executable code.

The line range starts in the middle of the `BIF_CFG_DEV0_EPF0_VF29_0_MSI_MSG_CNTL` field set, completes the tail of VF29 PCIe interrupt/error/ATS/ARI capability metadata, defines the complete `BIF_CFG_DEV0_EPF0_VF30_0_*` PCI configuration-space field map, and then switches to repeated per-VF backend register blocks for VF0 through the beginning of VF6 under `BIF_BX_DEV0_EPF0_VF*` and `RCC_DEV0_EPF0_VF*`.

## Purpose

`nbio_2_3_sh_mask.h` is the bitfield-layout half of the NBIO 2.3 hardware ABI used by AMDGPU. The companion `nbio_2_3_offset.h` file supplies register/config-space addresses and `nbio_2_3_default.h` supplies reset/default values. This chunk lets driver code and virtualization support use symbolic field names when decoding or programming PCIe and NBIO/BIF virtual-function registers instead of hard-coding raw bit positions.

The major hardware areas represented here are:

- VF29 PCIe MSI/MSI-X, vendor-specific capability, Advanced Error Reporting, header/TLP-prefix logging, Address Translation Services, and Alternative Routing-ID Interpretation fields.
- A complete VF30 PCI configuration map: IDs, command/status, class/header bytes, BAR-like base address fields, subsystem IDs, ROM/capability/interrupt fields, PCIe device and link capabilities/controls/status, MSI/MSI-X, vendor-specific extended capability, AER, ATS, and ARI.
- Per-VF backend/register-control blocks for VF0 through VF5, plus the first VF6 registers: MM index/data windows, RCC SR-IOV error and doorbell/config fields, BIF bus-master/atomic-error logging, doorbell GPA aperture fields, HDP coherency flush request/done controls, BIF transaction pending status, address LUT bypass, mailbox buffers and control bits, VM/hypervisor mailbox bits, and four GFX MSI-X vectors plus a pending-bit array.

## Important APIs, Types, And Constants

The public interface is the generated macro convention used across AMD register headers:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- `// addressBlock: ...` comments identify generated hardware address blocks.
- `//<REGISTER>` comments group subsequent field definitions by register.

There are no C types in this chunk. Integer width and access semantics are supplied by the register helper layer and by the hardware register definition. Important macro families visible in the chunk include:

- VF29 tail fields: `BIF_CFG_DEV0_EPF0_VF29_0_MSI_MSG_CNTL`, MSI address/data/mask/pending registers, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, `MSIX_PBA`, vendor-specific capability/header/scratch registers, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, AER uncorrectable/correctable status/mask/severity fields, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG[0-3]`, `PCIE_TLP_PREFIX_LOG[0-3]`, `PCIE_ATS_*`, and `PCIE_ARI_*`.
- VF30 PCI config identity and base fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_[1-6]`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.
- VF30 PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- VF30 interrupt and extended capability fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, MSI address/data/mask/pending aliases including 64-bit layout aliases, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, `MSIX_PBA`, vendor-specific extended capability registers, AER status/mask/severity/control/log fields, ATS, and ARI.
- Per-VF system/backend fields for VF0-VF5 and the start of VF6: `MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, `RCC_ERR_LOG`, `RCC_DOORBELL_APER_EN`, `RCC_CONFIG_MEMSIZE`, `RCC_CONFIG_RESERVED`, `RCC_IOV_FUNC_IDENTIFIER`, `BIF_BME_STATUS`, `BIF_ATOMIC_ERR_LOG`, `DOORBELL_SELFRING_GPA_APER_BASE_{HIGH,LOW}`, `DOORBELL_SELFRING_GPA_APER_CNTL`, `HDP_REG_COHERENCY_FLUSH_CNTL`, `HDP_MEM_COHERENCY_FLUSH_CNTL`, `GPU_HDP_FLUSH_REQ`, `GPU_HDP_FLUSH_DONE`, `BIF_TRANS_PENDING`, `NBIF_GFX_ADDR_LUT_BYPASS`, mailbox transfer/receive DWORDs, `MAILBOX_CONTROL`, `MAILBOX_INT_CNTL`, `BIF_VMHV_MAILBOX`, `GFXMSIX_VECT[0-3]_*`, and `GFXMSIX_PBA`.

## Control Flow

This header chunk has no runtime control flow. Its control-flow role is compile-time substitution into code that performs register access:

1. AMDGPU source includes the NBIO 2.3 offset/default/sh-mask headers.
2. Caller code selects the correct register address from the offset header and the correct field macro from this header.
3. Helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE` compose, extract, read, and write values.
4. Hardware, firmware, PF/VF, or hypervisor state changes according to the targeted register and the register's side-effect rules.

The repeated VF backend blocks are mechanically similar but target distinct virtual functions. For example, `BIF_BX_DEV0_EPF0_VF0_GPU_HDP_FLUSH_REQ__CP0_MASK` and `BIF_BX_DEV0_EPF0_VF5_GPU_HDP_FLUSH_REQ__CP0_MASK` describe the same bit position in different VF-specific registers. The macro names encode the VF number; no runtime loop or abstraction is present in the header.

## State And Persistence Behavior

The macros themselves are compile-time constants and persist no local state. They describe hardware-visible state in PCIe configuration registers and NBIO/BIF virtualization/backend registers.

State represented by this chunk includes:

- PCI config presentation state for VF29/VF30, including IDs, BAR-like address fields, capability list pointers, PCIe device/link capabilities, MSI/MSI-X capability data, AER capability state, ATS enablement, and ARI group/next-function data.
- Mutable PCIe control state such as command register bits, bus-master and memory-space enables, interrupt disable, payload/read-request sizing, error-reporting enables, relaxed ordering, no-snoop, FLR initiation, completion timeout controls, LTR/OBFF/IDO/atomic-operation controls, link retrain/common-clock/link-disable controls, MSI enable/mask/pending bits, MSI-X function mask/enable, ATS ATC enable, and ARI function group enables.
- Diagnostic and latch state such as PCI status bits, device/link status, AER uncorrectable/correctable status, AER header logs, TLP prefix logs, RCC invalid SR-IOV access status, doorbell read access status, BIF bus-master-low status, unsupported atomic-operation logs, and BIF transaction pending bits.
- Per-VF backend state for register aperture selection, doorbell GPA apertures, HDP coherency flush requests and completions, mailbox transfer/receive buffers, mailbox valid/ack handshake bits, VM/hypervisor mailbox bits, and GFX MSI-X vector address/data/control and pending-bit state.

Persistence depends on hardware ownership. Many capability fields are read-only or read-mostly strap/firmware-defined values. Control and mailbox fields are mutable hardware state controlled by PF, VF, firmware, or hypervisor paths. Error/status bits may be sticky until explicit clear, FLR, VF teardown, GPU reset, power transition, or another hardware-defined reset path.

## Dependencies

Direct dependencies and assumptions:

- The matching `nbio_2_3_offset.h` file must provide the corresponding register/config-space offsets for the same NBIO 2.3 address blocks.
- The matching `nbio_2_3_default.h` file must agree with the same hardware revision's reset/default values.
- AMDGPU register helper macros provide the actual read/modify/write behavior and field extraction/composition.
- Linux PCI/PCIe semantics define many of the capability fields mirrored here: command/status, PCIe device/link capability and control, MSI/MSI-X, AER, ATS, ARI, and function-level reset.
- SR-IOV, PF/VF, hypervisor, and firmware ownership rules determine which agent may program the per-VF config, mailbox, doorbell, and backend registers.

Observed integration in this source tree includes `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, and SMU11 platform files including `navi10_ppt.c` and `sienna_cichlid_ppt.c`, all of which include the NBIO 2.3 sh-mask header. `nbio_v2_3.c` also references NBIO/BIF offset names for HDP flush and PCIe access plumbing, showing how this header family is consumed with the offset definitions.

## Integration Points

This chunk integrates primarily with AMDGPU NBIO, PCIe, and virtualization code:

- NBIO 2.3 setup and service paths use generated field definitions to access PCIe/NBIO registers through SOC15 and PCIe register helpers.
- SR-IOV and MXGPU paths depend on per-VF field names to present, configure, reset, and service virtual functions without confusing VF-specific register instances.
- Linux PCI core and guest drivers interact with overlapping VF PCI configuration state, especially command/status, BARs, capabilities, MSI/MSI-X, AER, ATS, ARI, and FLR.
- Doorbell aperture and mailbox fields connect GPU virtualization resource routing and PF/VF/hypervisor communication.
- HDP coherency flush fields connect VM/VF-visible backend registers with cache/coherency maintenance for command processor and SDMA clients.
- GFX MSI-X vector fields provide per-VF interrupt routing metadata for four graphics MSI-X vectors plus pending bits.

## Risks

- **Generated-header drift:** A wrong shift or mask compiles cleanly but can read or write the wrong hardware bit. For repeated VF families, a single copy-generation error can affect one VF while adjacent VFs appear correct.
- **Register/address mismatch:** This file only defines fields. Pairing a VF30 field with a VF29 offset, or a VF5 backend mask with a VF4 register address, can silently corrupt unrelated state.
- **Partial chunk boundaries:** The range begins after the first VF29 MSI message-control shift definitions and ends at the first VF6 BME status register. The full file-level report must reconcile this document with neighboring chunks before making complete VF29 or VF6 claims.
- **PCI core ownership conflicts:** Command/status, MSI/MSI-X, AER, ATS, ARI, BAR, FLR, and link-control fields overlap with Linux PCI subsystem policy. AMDGPU direct writes need tight ownership and ordering.
- **Virtualization isolation:** Per-VF doorbell apertures, mailbox state, MM index windows, BIF transaction status, interrupt vectors, and function identifiers affect guest isolation. Incorrect programming can expose registers, misroute interrupts, lose mailbox messages, or break VF assignment.
- **Side-effectful status bits:** AER, PCI status, BIF atomic error logs, BME-low clear bits, mailbox ACK/VALID bits, HDP flush request/done bits, and interrupt pending/mask bits are not generic storage. Blind read/modify/write can clear evidence, acknowledge messages, or wedge a flush handshake.
- **MSI layout ambiguity:** MSI address/data/mask/pending registers have normal and `_64` layout aliases. Callers must respect the enabled 32-bit versus 64-bit MSI format.
- **Link and transaction controls:** VF30 link-control and transaction-related fields can affect PCIe training, error reporting, payload sizing, ordering, and completion behavior.

## Test Signals

Useful validation signals for code touching these macros or their generated source:

- Build AMDGPU configurations that include `nbio_2_3_sh_mask.h`, especially NBIO 2.3, MXGPU, and SMU11 paths.
- Compare generated mask/shift names against `nbio_2_3_offset.h` for VF29, VF30, and BIF/RCC VF0-VF6 to catch missing, duplicated, or mis-numbered fields.
- Static consistency checks should verify repeated VF backend blocks have identical layouts where the hardware spec expects only the VF number to vary.
- SR-IOV enumeration should show sane VF29/VF30 PCI IDs, command/status defaults, BAR/capability layout, PCIe capability values, MSI/MSI-X capability data, AER, ATS, and ARI.
- VF lifecycle testing should cover VF creation/removal, FLR, guest driver load/unload, command/status reset, MSI/MSI-X interrupt delivery, and preserved isolation between adjacent VFs.
- Mailbox and doorbell tests should exercise valid/ack handshakes, interrupt enables, GPA aperture programming, and invalid-access logging.
- HDP flush tests should verify request/done bits for CP0-CP9 and SDMA0/SDMA1 are observed correctly across VF0-VF5 paths that use these registers.
- PCIe error diagnostics or injection should map to the expected AER uncorrectable/correctable status, mask, severity, header log, TLP prefix log, RCC error-log, and BIF atomic-error bits.
- Suspend/resume, GPU reset, and VF teardown tests should confirm sticky status/control bits return to expected defaults and do not leak state between VF assignments.

## Chunk Notes

- The chunk starts mid-register: earlier lines likely contain `BIF_CFG_DEV0_EPF0_VF29_0_MSI_MSG_CNTL__MSI_EN__SHIFT` and `MSI_MULTI_CAP__SHIFT`.
- The VF30 PCI configuration-space map is complete within this line range.
- The BIF/RCC backend blocks are complete for VF0 through VF5 except that completeness must be confirmed against the offset/default headers; VF6 is only started here and continues in the next chunk.
- Because this is generated register metadata, the most important reconciliation gate is source-family consistency across `nbio_2_3_sh_mask.h`, `nbio_2_3_offset.h`, and `nbio_2_3_default.h`.
