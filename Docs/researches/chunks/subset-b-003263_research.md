# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 9853-12353

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for PCI and PCIe configuration-space bitfields in NBIO BIF configuration decode blocks.

The range starts one line after the `BIF_CFG_DEV0_EPF4_DEVICE_ID` shift definition, so it includes the `DEVICE_ID` mask and then the rest of the `DEV0_EPF4` endpoint/function block. It then covers complete generated blocks for `nbio_nbif0_bif_cfg_dev2_epf3_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev2_epf4_bifcfgdecp`, and ends in the beginning of `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`. The final line is inside `BIF_CFG_DEV0_EPF5_PCIE_UNCORR_ERR_STATUS`; several masks for that same register continue in the next chunk.

These definitions describe bit positions and masks only. Register offsets are supplied by the matching NBIO 7.7.0 offset header, while runtime access is performed by AMDGPU NBIO and register helper code.

## Major Register Groups

The `DEV0_EPF4` portion contains a near-complete endpoint/function PCI configuration image. It includes conventional PCI header fields such as device ID, command/status, revision and class-code bytes, cache line, latency, header type, BIST, BARs, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, and grant/latency bytes.

The same `DEV0_EPF4` block continues through PCI PM and PCIe capabilities: vendor capability list, PMI capability/list/status-control fields, serial bus release/FLADJ/DBESL bytes, PCIe capability metadata, Device Capability/Control/Status, Link Capability/Status, Device Capability 2, Device Control 2, Device Status 2, Link Status 2, MSI and MSI-X capability fields, AMD vendor-specific enhanced capability fields, PCIe AER status/mask/severity/capability/log fields, BAR enhanced capability fields, power-budgeting fields, Dynamic Power Allocation fields, ACS fields, PASID fields, and ARI fields.

The `DEV2_EPF3` and `DEV2_EPF4` blocks are repeated PCIe endpoint/function layouts for device 2 functions 3 and 4. They define vendor/device IDs, command and identity fields, BAR placeholders, subsystem IDs, capability pointers, interrupt metadata, vendor capability metadata, PM status/control, PCIe capability fields, MSI/MSI-X fields, vendor-specific enhanced capability fields, AER correctable-error and log fields, BAR enhanced capability fields, power-budgeting and DPA fields, ACS fields, PASID fields, and ARI fields. Compared with the `DEV0_EPF4` block in this chunk, these `DEV2` blocks omit several visible status/control groups such as full PCI status, PMI capability detail, Device Status, Device Capability 2, Device Control 2, Link Status 2, and uncorrectable AER status/mask/severity in the covered generated layout.

The `DEV0_EPF5` portion starts a following endpoint/function image. This chunk includes its vendor/device IDs, command/status, identity/class/header/BAR/subsystem/ROM/capability/interrupt fields, PM and PCIe capability fields, Device and Link Capability/Control/Status groups, MSI/MSI-X groups, vendor-specific enhanced capability groups, and the first part of `PCIE_UNCORR_ERR_STATUS`.

Across the chunk there are 2,126 `#define` entries. The visible register-comment groups cover 369 register names or address-block markers, with many field layouts repeated across endpoint/function instances.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or executable APIs in this range. The interface exported by the chunk is the generated macro namespace:

- `BIF_CFG_DEV0_EPF4_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV0_EPF4_<REGISTER>__<FIELD>_MASK`.
- `BIF_CFG_DEV2_EPF3_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV2_EPF3_<REGISTER>__<FIELD>_MASK`.
- `BIF_CFG_DEV2_EPF4_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV2_EPF4_<REGISTER>__<FIELD>_MASK`.
- `BIF_CFG_DEV0_EPF5_<REGISTER>__<FIELD>__SHIFT` and `BIF_CFG_DEV0_EPF5_<REGISTER>__<FIELD>_MASK` for the portion of `EPF5` present in this chunk.

The `__SHIFT` macros provide zero-based bit positions. The `_MASK` macros provide the field mask in the containing PCI configuration register. AMDGPU code normally combines these generated masks with helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, raw masking/shifting, and the matching `nbio_7_7_0_offset.h` register-offset macros.

`sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` directly includes both `nbio/nbio_7_7_0_offset.h` and this shift/mask header. That NBIO implementation provides the runtime integration layer for ASIC revision detection, memory-size reads, doorbell aperture setup, interrupt helper programming, PCIe index/data offset discovery, register remapping, and NBIO clock-gating controls. The specific endpoint/function macros in this chunk are compile-time register-layout data consumed by that broader NBIO register-access environment.

## Control Flow

This header has no executable control flow. Runtime behavior comes from consumers that include the header, choose a register offset for the detected NBIO 7.7.0 ASIC, read or write the target hardware register, and decode or update fields using these constants.

A typical consumer flow is:

1. Select the matching offset macro for the endpoint/function register, such as a `cfgBIF_CFG_DEV0_EPF4_*`, `cfgBIF_CFG_DEV2_EPF3_*`, `cfgBIF_CFG_DEV2_EPF4_*`, or `cfgBIF_CFG_DEV0_EPF5_*` name in the companion offset header.
2. Read the register through AMDGPU's SOC15, PCIe index/data, PCIe port, or configuration-space access path.
3. Decode a field by masking with `*_MASK` and shifting by `*__SHIFT`.
4. For writable controls, preserve unrelated and reserved bits, insert the new field value, and write the register back through the same access path.

The hardware flows represented by these fields include PCI command enablement, interrupt disablement, PM state and PME handling, PCIe device control, link reporting, completion-timeout and ARI controls, MSI/MSI-X programming, vendor-specific capability scratch data, AER reporting and logging, BAR-size capability reporting, power budget selection/reporting, DPA substate control, ACS peer-to-peer isolation controls, PASID enablement, and ARI function grouping.

## State And Persistence

The header itself is stateless and persists no runtime data. It is a compile-time register-layout description generated from AMD hardware definitions.

The described state lives in hardware PCI/NBIO configuration registers. Read-mostly identity and capability fields include vendor/device IDs, revision and class codes, PCIe capability metadata, supported payload/read-request sizes, supported link speed/width, MSI/MSI-X capability sizes, AER capability bits, power budget capabilities, DPA capabilities, ACS support, PASID support, and ARI support.

Writable control state includes PCI `COMMAND` bits, PM control/status bits such as power state and PME enable, PCIe Device Control fields, Device Control 2 fields, MSI/MSI-X enable and mask fields, AER masks and severity policy, DPA substate control, ACS control bits, PASID enable bits, and ARI control bits. The lifetime of those controls is governed by PCI function reset, FLR, GPU reset, suspend/resume, power-management transitions, and firmware or driver reinitialization; this header does not encode reset defaults.

Status and log state includes PCI status bits, Device Status, Link Status and Link Status 2, MSI pending bits, AER correctable and uncorrectable error status bits, AER header logs, TLP prefix logs, DPA status, and PME status. Some of these registers may latch hardware events or use write-one-to-clear behavior, but those access semantics are not represented by the generated masks.

## Dependencies And Integration Points

These macros depend on strict synchronization with `nbio_7_7_0_offset.h`. A field macro such as `BIF_CFG_DEV2_EPF4_PCIE_ACS_CNTL__P2P_REQUEST_REDIRECT_EN_MASK` is meaningful only when paired with the corresponding `DEV2_EPF4` register offset and the correct NBIO 7.7.0 instance. Reusing a mask with another ASIC generation or endpoint/function block can compile successfully while decoding or updating the wrong bits.

Important integration points include:

- AMDGPU NBIO 7.7 support in `amdgpu/nbio_v7_7.c`, which includes this generated header alongside the matching offset header.
- AMDGPU ASIC discovery, which selects `nbio_v7_7_funcs` for hardware using this NBIO generation.
- PCIe configuration and diagnostics paths that inspect function identity, command/status, BAR, capability-list, interrupt, PM, and PCIe capability fields.
- Interrupt setup paths that rely on MSI/MSI-X capability/control, message-address/data, mask, pending, table, and PBA fields.
- PCIe link-management and diagnostics code that decodes advertised and negotiated link speed/width, ASPM, clock power management, retrain state, data-link status, bandwidth status, and 8 GT/s equalization indicators.
- RAS and AER handling paths that decode error status, error masks, severity, ECRC controls, first-error pointer, header logs, and TLP prefix logs.
- IOMMU, virtualization, and peer-to-peer isolation paths that care about PASID, ACS, ARI, and BAR enhanced capability fields.
- Power-management paths that use PM capability/status-control, PCIe power budget, and DPA fields to report or program power substates.

## Risks

The highest risk is silent hardware misprogramming from mismatched generated definitions. A wrong shift or mask, or a mask paired with the wrong endpoint/function offset, can alter unrelated PCIe control bits, misreport link state, corrupt interrupt setup, hide or misclassify AER errors, or change ACS/PASID/ARI isolation behavior.

The chunk boundaries split logical groups. The first included line is only the `BIF_CFG_DEV0_EPF4_DEVICE_ID` mask; the associated block comment and shift are in the prior chunk. The final line is only part of `BIF_CFG_DEV0_EPF5_PCIE_UNCORR_ERR_STATUS`; the remaining masks for that register follow in the next chunk. Audits and generated documentation must merge adjacent chunks before treating either boundary register as complete.

The repeated endpoint/function naming is dense and copy/paste-prone. `DEV0_EPF4`, `DEV0_EPF5`, `DEV2_EPF3`, and `DEV2_EPF4` names differ by only a few characters, so consumer code can target the wrong function while still compiling cleanly.

Reserved fields and access-width details need care. The generated header includes masks for reserved fields and 8-, 16-, and 32-bit PCI configuration concepts, but it does not state whether a field is read-only, write-only, write-one-to-clear, sticky across resets, or sensitive to narrower PCI config access widths. Consumers must rely on hardware documentation and local AMDGPU access helpers for those semantics.

AER and interrupt fields are especially sensitive. Incorrect masks around `PCIE_UNCORR_ERR_STATUS`, `PCIE_CORR_ERR_STATUS`, MSI/MSI-X mask/pending registers, or table/PBA offsets can lead to lost diagnostics, interrupt delivery failures, or incorrect recovery policy.

## Test Signals

Useful validation signals are mostly build, generator, and hardware integration checks:

- The AMDGPU tree builds with `nbio_v7_7.c` including `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`, proving referenced macro names are syntactically valid.
- Generator or static checks confirm that every complete register group in this chunk has matching offset definitions for the same NBIO 7.7.0 endpoint/function name.
- Boundary validation confirms that `BIF_CFG_DEV0_EPF4_DEVICE_ID` is reconciled with the prior chunk and `BIF_CFG_DEV0_EPF5_PCIE_UNCORR_ERR_STATUS` is reconciled with the following chunk.
- PCIe enumeration on matching AMD hardware reports plausible vendor/device IDs, class codes, BAR layout, capability pointers, PM capability, PCIe capability, MSI/MSI-X capability, AER capability, ACS capability, PASID capability, and ARI capability for the relevant functions.
- MSI/MSI-X tests verify enable, function mask, per-vector mask, pending bits, table BIR/offset, PBA BIR/offset, and 32-bit versus 64-bit message data handling.
- Link diagnostics decode expected advertised and negotiated link speed/width, ASPM support, link training, slot clock configuration, bandwidth status, and 8 GT/s equalization fields.
- AER/RAS tests or fault injection decode correctable and uncorrectable status, masks, severity, header logs, and TLP prefix logs consistently with hardware documentation.
- Power-management testing verifies PM state, PME, power budget, and DPA fields across suspend/resume, runtime power transitions, FLR, hot reset, and GPU reset.
- Isolation and virtualization-oriented tests verify ACS, PASID, and ARI controls do not regress peer-to-peer routing, translated request behavior, or function-numbering behavior on supported platforms.
