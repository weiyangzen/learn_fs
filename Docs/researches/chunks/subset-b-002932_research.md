# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 68740-71163

## Scope

This chunk covers a generated AMD NBIO 2.3 register shift/mask header segment for PCIe configuration-space registers exposed for SR-IOV virtual functions. The range contains 2,137 `#define` entries across 275 register names. It starts in the middle of the `BIF_CFG_DEV0_EPF0_VF15_0_MSIX_PBA` field definitions, continues through the remaining VF15 PCIe extended capability definitions, covers complete generated PCI configuration bitfields for VF16, VF17, and VF18, and ends at `BIF_CFG_DEV0_EPF0_VF19_0_BASE_ADDR_1`.

The file is data-only C preprocessor material. It defines bit offsets and masks, not executable code. There are no functions, structs, enums, global variables, allocation sites, locks, or direct MMIO operations in this chunk.

## Purpose

The purpose of this header section is to provide the bit-level ABI used by AMDGPU NBIO/PCIe code when composing or decoding NBIO 2.3 BIF configuration registers for virtual functions. Each register field is represented with the usual generated-pair convention:

- `<REGISTER>__<FIELD>__SHIFT`, identifying the field's low bit.
- `<REGISTER>__<FIELD>_MASK`, identifying the field's bit mask in the register value.

The matching `nbio_2_3_offset.h` file supplies configuration offsets such as `cfgBIF_CFG_DEV0_EPF0_VF16_0_COMMAND`, `cfgBIF_CFG_DEV0_EPF0_VF18_0_PCIE_UNCORR_ERR_STATUS`, and `cfgBIF_CFG_DEV0_EPF0_VF19_0_BASE_ADDR_1`. This `*_sh_mask.h` file supplies the field encodings consumed by helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe/SMN register accessors in the AMDGPU tree.

## Important Macro Families

### Cross-Chunk VF15 Tail

The chunk begins after the VF15 MSI-X table fields and includes the tail of `BIF_CFG_DEV0_EPF0_VF15_0_MSIX_PBA`, whose fields describe the MSI-X pending bit array BAR indicator and table offset. It then covers VF15 vendor-specific and advanced PCIe capabilities:

- Vendor-specific enhanced capability list fields: `CAP_ID`, `CAP_VER`, and `NEXT_PTR`.
- Vendor-specific header fields: `VSEC_ID`, `VSEC_REV`, and `VSEC_LENGTH`.
- Two 32-bit vendor-specific scratch registers.
- Advanced Error Reporting (AER) capability list, uncorrectable/correctable error registers, AER capability/control, header log, and TLP prefix log registers.
- Address Translation Services (ATS) capability/control fields.
- Alternative Routing-ID Interpretation (ARI) capability/control fields.

Because the chunk starts mid-register at line 68740, the full VF15 MSI/MSI-X and basic PCIe capability story belongs partly to the previous chunk.

### Complete VF16, VF17, and VF18 PCI Header Fields

For VF16, VF17, and VF18, this chunk repeats a complete Type 0 PCI configuration header field layout. The basic header definitions include:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: `COMMAND` and `STATUS`.
- Header and timing fields: `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `MIN_GRANT`, and `MAX_LATENCY`.
- BAR and pointer fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, and `CAP_PTR`.
- Interrupt routing fields: `INTERRUPT_LINE` and `INTERRUPT_PIN`.

Important command/status bits include IO access, memory access, bus mastering, special cycles, memory-write-invalidate, parity response, SERR, fast back-to-back, interrupt disable, interrupt status, capability-list presence, target/master abort indications, system error, and parity-detected status.

### PCIe Capability and Link Management

For VF16, VF17, and VF18, the `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` families model standard PCIe capability structure fields. The chunk also includes the PCIe 2.0+ companion registers `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.

These definitions cover device capabilities and controls such as payload size, phantom function support, extended tag support, L0s/L1 latency, attention/power indicators, role-based error reporting, FLR support, completion timeout support/control, ARI forwarding support, atomic operation routing/completer support, TPH completer support, end-end TLP prefix support, emergency power reduction fields, IDO request/completion enablement, LTR enablement, OBFF, and atomic operation egress blocking. Link fields cover link speed, width, ASPM, read completion boundary, clock management, retrain/link disable, common clock, extended sync, hardware autonomous width/speed disable, link bandwidth management/status, and current/de-emphasized speed reporting.

### MSI and MSI-X

VF16, VF17, and VF18 each include MSI and MSI-X capability definitions:

- MSI capability list and message control fields such as message enable, multi-message capability/enable, 64-bit address support, per-vector masking, extended data capability, and extended data enable.
- MSI address/data, mask, and pending-register fields for both 32-bit and 64-bit layouts.
- MSI-X capability list and message control fields, including table size, function mask, and MSI-X enable.
- MSI-X table and pending bit array fields, each split into BAR indicator and offset fields.

These are configuration-space definitions for interrupt delivery resources. The actual interrupt setup is implemented elsewhere; this chunk only supplies field positions.

### Vendor-Specific and Advanced Error Reporting

For VF16, VF17, and VF18, and for the VF15 tail, this chunk defines PCIe vendor-specific and AER fields:

- Vendor-specific capability list and header fields for capability ID/version/next pointer, VSEC ID/revision/length, and scratch registers.
- AER capability list fields.
- Uncorrectable error status, mask, and severity fields for data link protocol, surprise down, poisoned TLP, flow control, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors.
- Correctable error status/mask fields for receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, internal correctable error, and header-log overflow.
- AER capability/control fields for first error pointer, ECRC generation/checking capability and enable bits, multiple header recording, TLP prefix log presence, and completion timeout log capability.
- Four 32-bit header-log registers and four 32-bit TLP-prefix-log registers.

The status/mask/severity triad is especially important because the same bit positions are intentionally repeated across status, mask, and severity registers.

### ATS and ARI

The chunk includes ATS and ARI enhanced capability definitions for VF15 through VF18:

- ATS enhanced capability list: capability ID, version, and next pointer.
- ATS capability: invalidate queue depth, page-aligned request support, and global invalidate support.
- ATS control: smallest translation unit (`STU`) and address translation cache enable (`ATC_ENABLE`).
- ARI enhanced capability list: capability ID, version, and next pointer.
- ARI capability: MFVC function group capability, ACS function group capability, and next function number.
- ARI control: MFVC/ACS function group enables and function group selection.

These fields are relevant to IOMMU/translation behavior and PCIe function enumeration in virtualized configurations.

### VF19 Beginning

The final portion starts `nbio_nbif0_bif_cfg_dev0_epf0_vf19_bifcfgdecp` and includes VF19 definitions through `BASE_ADDR_1`. Covered fields include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class fields, cache line, latency, header type/device type, BIST, and the first BAR. The rest of VF19 continues in the next chunk.

## Control Flow and State Behavior

This header has no runtime control flow. It affects generated object code only through C preprocessor constants that become operands to AMDGPU register-helper macros.

The state described by this chunk is hardware PCIe/NBIO configuration state, not persistent software state in the header. Important state categories include VF command enables, error/status bits, class and BAR configuration, interrupt capability state, MSI/MSI-X table/PBA locations, link capability/control/status, AER status/mask/severity/log registers, ATS enablement, and ARI function grouping.

Some defined fields represent writable controls, some represent read-only capabilities, and some represent sticky or clear-on-write hardware status bits depending on the PCIe specification and NBIO implementation. The generated masks do not encode those access semantics. Callers must rely on the surrounding NBIO, PCI core, SR-IOV, and hardware sequencing rules when reading, writing, clearing, or polling these fields.

## Dependencies and Integration Points

This chunk depends on the generated AMD register header set:

- `nbio_2_3_offset.h` provides the matching `cfgBIF_CFG_DEV0_EPF0_VF*` register offsets.
- `nbio_2_3_default.h` provides default values for the same NBIO generation where generated defaults exist.
- AMDGPU register helper macros consume these `__SHIFT` and `_MASK` definitions to avoid hard-coded bit positions.

Observed local include sites for NBIO 2.3 headers include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes `nbio_2_3_default.h`, `nbio_2_3_offset.h`, and `nbio_2_3_sh_mask.h` and implements NBIO register access, memory-controller access enablement, doorbell aperture setup, interrupt control, clock gating, link control, and SR-IOV-aware behavior.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes the NBIO 2.3 offset and mask headers for Navi SR-IOV mailbox and virtualization support.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include NBIO 2.3 headers from SMU policy code.
- Display resource files such as `dcn20_resource.c` and `dcn303_resource.c`, which include the matching NBIO offset header where display bring-up needs NBIO register addresses.

Direct textual references to the exact VF15-VF19 field names in this chunk were not found in the nearby AMDGPU, SMU, or display C files during this pass. That is expected for generated config-space VF definitions: they may be used by generic helper code, diagnostics, firmware-facing tooling, out-of-tree consumers, or retained as a complete hardware register map even when a particular in-tree path does not touch every generated field.

## Risks

- Bitfield drift is high impact. An incorrect shift or mask can program the wrong PCIe configuration bits for a VF, affecting bus mastering, memory decoding, interrupts, AER behavior, ATS, ARI, or link controls.
- The repeated VF16/VF17/VF18 blocks are mechanically similar but must remain exactly aligned with their matching offsets. Copy/paste or generator errors can silently make one VF's field constants point at another VF's semantics.
- AER status, mask, and severity registers intentionally share many field positions. Mixing status/mask/severity macro names can hide real errors, over-report errors, or classify fatal/non-fatal conditions incorrectly.
- MSI and MSI-X offsets, table BAR indicators, and PBA fields are sensitive because interrupt routing depends on exact table placement and masking behavior.
- ATS and ARI controls are virtualization- and IOMMU-sensitive. Incorrect `ATC_ENABLE`, `STU`, function group, or next-function-number handling can break address translation, enumeration, or isolation assumptions.
- PCIe capability fields include both capability bits and control bits. Treating read-only capability fields as writable policy fields can result in ineffective writes or confusing diagnostics.
- The chunk starts and ends across register-family boundaries. VF15 is incomplete at the start, and VF19 is incomplete at the end; final analysis must merge adjacent chunks before making per-file completeness claims.

## Test and Validation Signals

Useful validation is mainly build, register-access, and hardware integration coverage:

- Compile AMDGPU with NBIO 2.3 users enabled; this catches missing, renamed, or syntactically malformed generated macros.
- Exercise NBIO v2.3 initialization paths in `nbio_v2_3.c`, including memory access enablement, interrupt setup, doorbell aperture/range programming, clock-gating policy, and PCIe link handling.
- Run SR-IOV VF bring-up and teardown on Navi/NBIO 2.3 hardware, checking that VFs enumerate with expected vendor/device/class fields, command/status behavior, BARs, and capability chains.
- Validate MSI and MSI-X interrupt delivery for VFs, including vector masking, function masking, table/PBA placement, and pending-bit behavior.
- Inject or observe PCIe AER correctable and uncorrectable conditions, then confirm status, mask, severity, header log, and TLP prefix log decoding matches hardware expectations.
- Validate ATS and ARI behavior under an IOMMU with SR-IOV enabled, including ATC enablement, invalidate queue depth reporting, function grouping, and enumeration.
- Compare the generated masks against the vendor register specification or a known-good generated NBIO 2.3 header when updating the file, especially across the repeated VF16-VF18 blocks.

## Unresolved Cross-Chunk References

The first complete comment in this chunk is `BIF_CFG_DEV0_EPF0_VF15_0_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, but the actual line range begins with the final `BIF_CFG_DEV0_EPF0_VF15_0_MSIX_PBA` shift/mask entries. The preceding VF15 header, PCIe, MSI, and MSI-X definitions belong to the previous chunk.

The range ends after `BIF_CFG_DEV0_EPF0_VF19_0_BASE_ADDR_1`. The remaining VF19 BARs, capability lists, PCIe capability fields, MSI/MSI-X, vendor-specific, AER, ATS, and ARI definitions continue in the next chunk.
