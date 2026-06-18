# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 14600-17033

## Scope

This chunk is a generated AMDGPU NBIO 7.4 shift/mask header slice for PCIe configuration-space fields. It starts inside the `BIF_CFG_DEV0_EPF0_VF8_0_PCIE_CORR_ERR_STATUS` definitions, completes the tail of the `VF8` PCIe advanced-error, ATS, and ARI capability masks, then covers complete PCI configuration images for `BIF_CFG_DEV0_EPF0_VF9_0`, `BIF_CFG_DEV0_EPF0_VF10_0`, and `BIF_CFG_DEV0_EPF0_VF11_0`. It ends inside the `BIF_CFG_DEV0_EPF0_VF12_0_DEVICE_CAP2` shift definitions after covering the conventional header, PCIe capability, and link control/status fields for `VF12`.

The file is not executable logic. It is a hardware layout contract: paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros define how AMDGPU code decodes or composes register values after selecting the matching address from `nbio_7_4_offset.h`.

## Purpose

`nbio_7_4_sh_mask.h` describes bit positions for NBIO 7.4 registers. This chunk focuses on SR-IOV-style endpoint virtual-function PCIe config blocks under `DEV0_EPF0`, specifically virtual functions 8 through 12. These fields mirror standard PCI/PCIe capability layouts and AMD/vendor-specific enhanced capability space for each VF.

The macros support code that needs to:

- decode PCI identity, command, status, class, header, BAR, interrupt, and capability-pointer fields;
- program or inspect PCIe Device/Link Capability, Control, and Status registers;
- configure or diagnose MSI and MSI-X capability registers for VFs 9-11;
- decode Advanced Error Reporting status, masks, severity, header logs, and TLP prefix logs;
- inspect or control ATS and ARI enhanced capabilities.

The source path matters because these definitions are ASIC-generation-specific. A field name that is correct for `nbio_7_4_sh_mask.h` must be paired with the corresponding NBIO 7.4 offset/base definitions and not with a similar register from another NBIO generation.

## Major Register Groups

The chunk opens with the tail of `BIF_CFG_DEV0_EPF0_VF8_0`. The covered VF8 registers are PCIe AER correctable error status/mask, AER capability/control, four TLP header log DWORDs, four TLP prefix log DWORDs, ATS enhanced capability list/capability/control, and ARI enhanced capability list/capability/control. Important VF8 fields include receiver, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, internal correctable, header-log-overflow status/mask bits, ECRC generation/check enable bits, ATS `STU` and `ATC_ENABLE`, and ARI function-group controls.

`BIF_CFG_DEV0_EPF0_VF9_0`, `VF10_0`, and `VF11_0` each receive a complete repeated PCIe VF config-layout block in this range. Each block includes:

- Conventional PCI header fields: vendor ID, device ID, command, status, revision ID, programming interface, subclass, base class, cache line size, latency timer, header type, BIST, six BARs, subsystem vendor/device ID, ROM base address, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: capability list ID/next pointer, PCIe capability version/device type/slot/interrupt metadata, Device Capability, Device Control, Device Status, Link Capability, Link Control, Link Status, Device Capability 2, Device Control 2, Device Status 2, Link Capability 2, Link Control 2, Link Status 2, and second-generation slot registers.
- Interrupt capabilities: MSI capability list/control, MSI message address/data, 32-bit and 64-bit mask/pending layouts, MSI-X capability list/control, MSI-X table offset/BIR, and MSI-X PBA offset/BIR.
- Vendor-specific enhanced capability registers: enhanced capability list header, vendor-specific header, and two vendor-specific payload registers.
- PCIe Advanced Error Reporting registers: AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- ATS and ARI enhanced capability registers: capability IDs/versions/next pointers, ATS invalidate queue depth, page-aligned request and global invalidate support, ATS control `STU` and `ATC_ENABLE`, ARI multi-function/ACS function group support, next-function number, enable bits, and function-group selection.

The `VF12_0` portion begins at its address-block marker and covers the same conventional PCI header and first PCIe capability sections through the start of Device Capability 2. It includes Device/Link Capability, Control, and Status, then the `DEVICE_CAP2` shift fields through `MAX_END_END_TLP_PREFIXES`. The chunk boundary stops before the matching `VF12_0_DEVICE_CAP2` mask fields and before later VF12 MSI, AER, ATS, and ARI groups.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this range. The important public surface is the macro naming convention:

- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit position.
- `BIF_CFG_DEV0_EPF0_VF<N>_0_<REGISTER>__<FIELD>_MASK` gives the field mask in the logical register value.

Consumers typically combine these masks with AMDGPU register helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, or with explicit mask/shift operations, after reading a raw value through the relevant PCI config, MMIO, or SOC15 access path. The paired address macros live in `nbio_7_4_offset.h`, for example `cfgBIF_CFG_DEV0_EPF0_VF9_0_DEVICE_CNTL`, `cfgBIF_CFG_DEV0_EPF0_VF10_0_PCIE_UNCORR_ERR_STATUS`, and corresponding entries for VF11/VF12.

The field groups are mostly standard PCIe concepts rather than AMD-specific types. Examples include `BUS_MASTER_EN`, `INT_DIS`, `MAX_PAYLOAD_SIZE`, `MAX_READ_REQUEST_SIZE`, `INITIATE_FLR`, `CURRENT_LINK_SPEED`, `NEGOTIATED_LINK_WIDTH`, `MSI_EN`, `MSIX_EN`, AER error bits, ECRC controls, ATS `ATC_ENABLE`, and ARI forwarding/function-group controls.

## Control Flow

This header has no runtime control flow. Runtime behavior is created in consumers that:

1. Detect an ASIC using the NBIO 7.4 register set.
2. Choose a VF register address from `nbio_7_4_offset.h`.
3. Read a PCIe configuration or NBIO register value using AMDGPU access helpers.
4. Decode fields using these `SHIFT` and `MASK` constants.
5. For writable controls, update only the intended field and preserve reserved or unrelated bits on writeback.

The fields in this chunk affect hardware flows such as VF PCI command enablement, function-level reset initiation, link training/retraining, link bandwidth interrupt reporting, MSI/MSI-X programming, AER error masking/severity classification, AER log capture, ATS enablement for translated requests, and ARI function enumeration/control. The macros themselves do not enforce access width, side-effect rules, or write ordering; those rules come from the PCIe spec, AMD register documentation, and existing driver access paths.

## State And Persistence

The header is compile-time-only and has no stored state. It persists no values and performs no initialization.

The state described by these macros lives in hardware PCIe configuration registers for virtual functions. Some fields are effectively static capability state, such as capability IDs, versions, next pointers, supported payload sizes, link speed/width capability, MSI/MSI-X capability layout, AER capability bits, ATS queue depth/support bits, and ARI next-function metadata. Other fields are live controls, including command bits, Device Control, Link Control, MSI/MSI-X enable/mask bits, AER masks/severity controls, ECRC enables, ATS `ATC_ENABLE`, and ARI function-group enables.

Status fields can be transient, sticky, or write-one-to-clear depending on the register. Examples include conventional PCI status error bits, PCIe Device Status, Link Status, AER correctable and uncorrectable status, MSI pending bits, and AER header/prefix logs. This generated header does not encode reset defaults, read-only/write-only permissions, write-one-to-clear behavior, or persistence across FLR, hot reset, GPU reset, suspend/resume, or power-gating. Consumers must preserve reserved bits and follow the hardware-defined reset domain.

## Dependencies And Integration Points

The closest dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`, which supplies the matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets. This shift/mask header is only meaningful when its field macros are paired with the matching offset symbol for the same VF and register.

The header is included by NBIO and power-management code in this tree, including `drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c` and several SMU/powerplay files. Those consumers use the broader NBIO 7.4 definition set for ASIC-specific register access. This particular chunk is most relevant to VF PCIe configuration, SR-IOV diagnostics, PCIe link setup/status reporting, interrupt setup, AER/RAS handling, ATS/IOMMU integration, and ARI function enumeration.

Other integration points include:

- Linux PCI/PCIe enumeration expectations for VF capability layout.
- SR-IOV VF enablement and reset paths that rely on stable VF config-space layout.
- Interrupt setup code that programs MSI or MSI-X message address/data, masks, pending bits, table offsets, and PBA offsets.
- RAS/AER paths that decode uncorrectable/correctable error status, severity, masks, header logs, and prefix logs.
- IOMMU/ATS paths that need ATS capability/control fields to agree with the rest of the GPU memory-translation stack.
- Link-management paths that inspect or write speed, width, retrain, common-clock, autonomous bandwidth, and completion-timeout controls.

The repeated `VF9`, `VF10`, and `VF11` sections share identical field layouts but target distinct VF config images. Exact macro spelling is part of the ABI between generated headers and driver code.

## Risks And Edge Cases

The largest risk is silent misprogramming from a one-bit mask or shift error. In this chunk, that could enable bus mastering or memory access on the wrong bit, hide or misclassify AER errors, corrupt MSI/MSI-X programming, initiate FLR unintentionally, misreport link speed/width, or enable ATS/ARI behavior contrary to the platform policy.

The repetitive generated layout makes copy/generation drift plausible. VF9, VF10, and VF11 should have the same field definitions for equivalent registers; a mismatch in one VF would only surface when that VF number is configured or diagnosed. VF12 is partial in this chunk, so the merge lane must not infer that the VF12 Device Capability 2 block is complete at line 17033.

Register width is another risk. Some macros describe 8-bit or 16-bit PCI config fields, while others describe 32-bit BARs, AER logs, capability headers, or table offsets. Callers must use the correct access size and preserve reserved bits. MSI registers also have overlapping 32-bit and 64-bit layouts, for example message data and mask offsets that differ depending on whether 64-bit MSI addressing and per-vector masking are active.

AER and status registers can have side effects. The presence of a `_MASK` macro does not imply that a field is safe to write as an ordinary read-modify-write. Error status may be sticky or write-one-to-clear, and log registers may be meaningful only after a captured error. Similar caution applies to link retraining, FLR initiation, MSI/MSI-X enablement, and ATS/ARI enable controls.

The chunk starts and ends inside repeated generated blocks. Chunk-local analysis should account for the missing earlier VF8 uncorrectable-error context and the missing later VF12 Device Control 2, MSI, AER, ATS, and ARI context. A final per-file report should reconcile this chunk with adjacent chunks before making claims about the whole `VF8` or `VF12` register set.

## Test Signals

Useful validation signals are mostly compile-time and hardware-integration oriented:

- Build AMDGPU code paths that include `nbio_7_4_sh_mask.h` with `nbio_7_4_offset.h`, confirming the generated macro names referenced by NBIO 7.4 consumers still resolve.
- Compare every covered `BIF_CFG_DEV0_EPF0_VF9_0`, `VF10_0`, `VF11_0`, and partial `VF12_0` register name against `nbio_7_4_offset.h` to ensure matching offsets exist for the same VF/register names.
- Cross-check repeated VF9/VF10/VF11 field definitions for identical masks and shifts on equivalent registers.
- On matching hardware, enable SR-IOV VFs and verify PCI enumeration reports plausible vendor/device/class, BAR, PCIe capability, MSI/MSI-X, AER, ATS, and ARI information.
- Exercise VF reset paths, especially `INITIATE_FLR`, and confirm command/status, device status, link status, MSI/MSI-X, AER, ATS, and ARI controls settle to expected values afterward.
- Validate MSI/MSI-X delivery, masking, pending-bit behavior, table offset/BIR, and PBA offset/BIR for VFs covered by this chunk.
- Use PCIe/AER fault injection or hardware error telemetry to verify correctable and uncorrectable error bits, masks, severity fields, header logs, and TLP prefix logs decode consistently with PCIe documentation and AMD expectations.
- Check link diagnostics under normal boot, reset, and power-management transitions: negotiated speed/width, link training, data-link active, common-clock, bandwidth-management status, and autonomous-bandwidth status should decode correctly.
- Exercise ATS/ARI-aware configurations with IOMMU enabled and disabled, checking that `ATC_ENABLE`, STU, queue-depth support, ARI next-function, and function-group controls are interpreted consistently.
