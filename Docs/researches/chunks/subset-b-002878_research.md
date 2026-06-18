# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 2469-4902

## Scope

This chunk covers generated shift and mask macros for the NBIF 6.3.1 PCIe configuration-space view of SR-IOV virtual functions. It starts in the middle of the `BIF_CFG_DEV0_EPF0_VF0_PCIE_UNCORR_ERR_STATUS` mask list, then finishes VF0's PCIe advanced error reporting and ARI fields. It then covers complete repeated config-space field maps for `VF1`, `VF2`, and `VF3`, and ends after the first field of `VF4_PCIE_CAP`.

The covered address blocks are:

- Tail of `nbif_bif_cfg_dev0_epf0_vf0_bifcfgdecp`: AER uncorrectable/correctable error masks and status, AER header/TLP-prefix logs, and ARI enhanced capability fields.
- Full `nbif_bif_cfg_dev0_epf0_vf1_bifcfgdecp`, `vf2_bifcfgdecp`, and `vf3_bifcfgdecp`: conventional PCI header fields, PCIe capability fields, MSI/MSI-X capability fields, vendor-specific enhanced capability fields, AER fields, header/TLP-prefix logs, and ARI fields.
- Beginning of `nbif_bif_cfg_dev0_epf0_vf4_bifcfgdecp`: conventional PCI header fields through `VF4_PCIE_CAP__VERSION__SHIFT`.

The file is a generated hardware register bitfield map. This chunk defines preprocessor constants only. It has no C functions, structs, variables, executable logic, dynamic allocation, or local persistence.

## Purpose

The purpose of this header section is to give AMDGPU/NBIF code symbolic access to bit positions in PCI/PCIe configuration registers exposed for virtual functions behind device 0, endpoint function 0. Each field is represented by the standard AMD generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field.

The sibling `nbif_6_3_1_offset.h` file supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_*` and `regBIF_CFG_DEV0_EPF0_VF*_*` register addresses. Driver code includes this mask header from `amdgpu/nbif_v6_3_1.c` and uses the broader AMD register-helper convention (`REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related helpers) to build or decode register values without hard-coding bit numbers.

## Important Macro Families

### Conventional PCI Header Fields

The complete VF1/VF2/VF3 blocks and the partial VF4 block define the basic PCI configuration header:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: `COMMAND` exposes IO, memory, bus-master, parity, SERR, fast back-to-back, and interrupt-disable bits; `STATUS` exposes interrupt status, capability-list presence, data parity, DEVSEL timing, abort, SERR, and parity status.
- Header and resource fields: `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, and `CAP_PTR`.
- Legacy interrupt hints: `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, and `MAX_LATENCY`.

These macros mirror PCI config-space layout for each VF. The VF blocks use the same field layout while the offset header assigns each VF a distinct register window.

### PCIe Capability and Link Fields

For VF1 through VF3, and the start of VF4, the chunk defines PCIe capability-list and device/link capability fields:

- `PCIE_CAP_LIST` and `PCIE_CAP` encode capability ID, next pointer, version, device type, slot-implemented state, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` describe payload size support and programming, error-reporting enables/status, relaxed ordering, extended tags, no-snoop behavior, read request size, FLR capability/initiation, auxiliary power, pending transactions, and emergency power-reduction status.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe link speed, width, power-management support, L0s/L1 latencies, clock power management, surprise-down reporting, data-link active reporting, bandwidth notifications, ASPM optionality, port number, link disable/retrain controls, common clock, extended sync, autonomous width control, DRS signaling, current negotiated speed/width, training state, slot clock, and link bandwidth status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion timeout ranges, ARI forwarding, AtomicOp capability and request controls, ID-based ordering, LTR, ten-bit tags, OBFF, TLP prefix support/blocking, emergency power-reduction fields, FRS support, supported link speeds, compliance controls, de-emphasis, equalization status, crosslink/RTM presence, downstream component presence, and DRS message receipt.

These are not policy code; they encode the bit ABI for PCIe capability state that the hardware exposes for each virtual function.

### MSI and MSI-X Fields

The VF1/VF2/VF3 blocks define both MSI and MSI-X capability registers:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MASK`, `MSI_MSG_DATA_64`, `MSI_EXT_MSG_DATA_64`, `MSI_MASK_64`, `MSI_PENDING`, and `MSI_PENDING_64`.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.

Important fields include MSI enable, multi-message capability/enable, 64-bit support, per-vector masking capability, extended message data capability/enable, message address/data masks, vector mask and pending bits, MSI-X table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

These definitions are integration points for interrupt routing and virtualization setup. Incorrect field definitions would misprogram message addresses/data, vector masking, or MSI-X table/PBA decoding.

### Vendor-Specific Enhanced Capability Fields

For VF1 through VF3, the chunk defines:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, with capability ID, version, and next pointer.
- `PCIE_VENDOR_SPECIFIC_HDR`, with VSEC ID, revision, and length.
- `PCIE_VENDOR_SPECIFIC1` and `PCIE_VENDOR_SPECIFIC2`, each exposing a full 32-bit data field.

These provide generic bit access for AMD/vendor-specific PCIe extended capability payloads associated with the VF config space.

### Advanced Error Reporting and ARI Fields

The chunk is heavily weighted toward AER fields for VF0 through VF3:

- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` encodes AER capability ID, version, and next pointer.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` cover DLP errors, surprise-down, poisoned TLP, flow-control errors, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, multicast-blocked TLP, AtomicOp egress blocking, TLP prefix blocking, and poisoned-TLP egress blocking.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver errors, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal errors, corrected internal errors, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL` exposes first-error pointer, ECRC generation/check capabilities and enables, multi-header-recording capability/enable, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3` expose full 32-bit header or prefix log words.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` expose ARI capability ID/version/next pointer, MFVC/ACS function-group capability/enables, next function number, and function group selection.

The VF0 portion is partial because the chunk begins after the first uncorrectable-error status shifts and lower mask bits. The AER/ARI layout is complete for VF1 through VF3.

## Control Flow and State Behavior

This header has no runtime control flow. Its only behavior is compile-time substitution of bit positions and masks into code that reads or writes NBIF registers.

The state represented by these macros lives in hardware PCIe configuration space and NBIF register windows. Some fields are stable descriptors, such as vendor/device IDs, class codes, capability IDs, next capability pointers, capability versions, BAR masks, link capability flags, and MSI-X table/PBA layout. Other fields are mutable controls, such as `COMMAND` memory and bus-master enables, PCIe error-reporting enables, payload/read-request size controls, FLR initiation, link retrain/disable, MSI/MSI-X enables, MSI vector masks, AER error masks/severity, ECRC enables, ARI forwarding, AtomicOp request enable, LTR enable, OBFF enable, and TLP prefix blocking.

Several fields are status or log surfaces rather than persistent software-owned configuration. Examples include PCI `STATUS`, `DEVICE_STATUS`, `LINK_STATUS`, `LINK_STATUS2`, MSI pending bits, AER uncorrectable/correctable status registers, AER header logs, and TLP prefix logs. These may be hardware-updated, sticky, clear-on-write, or consumed according to PCIe/AER semantics; the generated macros do not encode ordering, clear rules, or polling policy.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention:

- `nbif_6_3_1_offset.h` supplies matching config-space offsets and MMIO register addresses. The offset header shows repeated VF windows, for example `VF1` at the `0x184xx` register range, `VF2` at `0x188xx`, `VF3` at `0x18cxx`, and `VF4` beginning at `0x190xx` for this family.
- `nbif_6_3_1_sh_mask.h` supplies the bit positions and masks described here.
- `amdgpu/nbif_v6_3_1.c` includes both headers and is the direct NBIF 6.3.1 integration point in this source tree. That implementation primarily programs NBIF memory, doorbell, interrupt, and PCIe-related state through AMD register helpers; the VF config-space symbols are available to the same compilation unit when PF/VF configuration fields need to be decoded or programmed.
- Broader AMDGPU and Linux PCI/SR-IOV paths rely on the hardware presenting correct PCIe capability, MSI/MSI-X, AER, and ARI state for virtual functions.

The repeated VF layout also lines up with nearby generated NBIO/NBIF generations, but consumers must include the exact NBIF 6.3.1 offset/mask pair. Similar names in `nbio_*_sh_mask.h` or other NBIF versions are not safe substitutes because register bases, presence, and field layouts can drift across IP versions.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can write unrelated PCIe config-space bits, affecting VF enumeration, bus mastering, memory access, interrupts, link management, error reporting, or FLR.
- The repeated VF blocks are mechanically similar and easy to corrupt by copy/paste or generator mistakes. A single VF-specific typo can make only one virtual function misreport capabilities or mishandle interrupts/errors.
- The chunk boundaries are partial. It starts mid-register in VF0 and ends mid-register in VF4. A final merged report must stitch adjacent chunks to avoid presenting VF0 or VF4 as complete here.
- MSI/MSI-X fields are interrupt-sensitive. Misprogrammed message addresses/data, mask bits, MSI-X table offsets, or PBA offsets can cause lost interrupts, spurious interrupts, or interrupts delivered to the wrong vector.
- AER fields are diagnostic and recovery-sensitive. Incorrect uncorrectable/correctable status, mask, or severity bits can hide PCIe errors, classify recoverable events incorrectly, or leave sticky error state uncleared.
- FLR, bus-master, memory-space, ARI, AtomicOp, ACS, and TLP-prefix controls are virtualization-sensitive. Wrong values can break VF reset behavior, DMA authorization, function discovery, isolation, or PCIe transaction handling.
- Full-width log/data fields such as BARs, MSI addresses, vendor-specific payloads, AER header logs, and TLP prefix logs use `0xFFFFFFFFL` masks; callers must know whether a register is read-only, writeable, write-one-to-clear, or hardware-owned before writing.

## Test and Validation Signals

Useful validation is mostly build, enumeration, and hardware integration coverage:

- Build AMDGPU with NBIF 6.3.1 enabled so `amdgpu/nbif_v6_3_1.c` includes `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h` without missing or conflicting macros.
- SR-IOV enumeration should show VF1/VF2/VF3, and adjacent chunks' VF0/VF4, with expected vendor/device IDs, class codes, BAR layout, capability chains, PCIe capability values, and ARI capability state.
- PCIe link diagnostics should report expected link speed/width, training, DL active, bandwidth status, link-capability flags, and Gen3+ equalization fields where applicable.
- MSI/MSI-X tests should verify VF interrupt enable/disable, vector mask/pending behavior, MSI-X table and PBA decoding, and interrupt delivery under load.
- AER injection or error-path tests should validate uncorrectable/correctable status bits, masks, severity selection, first-error pointer, ECRC controls, header logs, and TLP-prefix logs.
- VF reset tests should cover `DEVICE_CNTL__INITIATE_FLR`, transaction-pending behavior, bus-master/memory enable transitions, and post-reset config-space restoration.
- Virtualization isolation tests should cover ARI forwarding/function-group fields, ACS violation reporting, AtomicOp egress/request behavior, and poisoned/TLP-prefix blocking status.

## Unresolved Cross-Chunk References

Line 2469 starts inside `BIF_CFG_DEV0_EPF0_VF0_PCIE_UNCORR_ERR_STATUS`; the lower masks and all shifts for that register are in the previous chunk. Line 4902 stops after `BIF_CFG_DEV0_EPF0_VF4_PCIE_CAP__VERSION__SHIFT`; the rest of `VF4_PCIE_CAP` and VF4's later PCIe/MSI/MSI-X/AER/ARI fields continue in the next chunk.
