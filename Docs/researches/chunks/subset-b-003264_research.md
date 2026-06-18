# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 12354-14862

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It defines C preprocessor constants for PCIe/NBIO configuration-space bitfields on several endpoint-function register images. The paired offset header supplies register addresses; this file supplies only field positions and masks.

The range begins inside `BIF_CFG_DEV0_EPF5_PCIE_UNCORR_ERR_STATUS`, at the tail of the AER uncorrectable-error status masks, then completes the rest of the `DEV0_EPF5` PCIe enhanced-capability tail. It then covers most of `DEV2_EPF6`, all of `DEV0_EPF6`, all of `DEV0_EPF7`, and starts `DEV1_EPF0` through the beginning of its PCIe capability block. The chunk contains 2,117 `#define` entries and four address-block markers across 2,509 source lines.

The generated macros describe PCI/PCIe config layout for:

- Advanced Error Reporting status, masks, severity controls, capability/control bits, TLP header logs, and TLP prefix logs.
- BAR enhanced capability metadata and BAR size/control fields.
- Power Budgeting and Dynamic Power Allocation capabilities.
- ACS, PASID, and ARI enhanced capabilities.
- Conventional PCI header fields, power management, PCIe capability, MSI, MSI-X, AMD vendor-specific capability, and interrupt-related metadata for repeated endpoint functions.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this chunk. Its exported interface is the macro namespace:

- `BIF_CFG_DEV*_EPF*_<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit position for a field.
- `BIF_CFG_DEV*_EPF*_<REGISTER>__<FIELD>_MASK` gives the field mask in the containing config register.

The macros are intended to be paired with `nbio_7_7_0_offset.h` names such as `cfgBIF_CFG_DEV0_EPF5_PCIE_UNCORR_ERR_MASK`, `cfgBIF_CFG_DEV0_EPF6_PCIE_BAR1_CNTL`, or `cfgBIF_CFG_DEV1_EPF0_PCIE_CAP`. The direct driver integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h` and uses generated fields with AMDGPU register helpers such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.

## Register Groups Covered

The `DEV0_EPF5` tail covers AER and enhanced PCIe capability state after the preceding chunk has already introduced the uncorrectable-error status register. This chunk includes uncorrectable-error mask and severity fields for Data Link Protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast-blocked TLP, AtomicOp egress block, TLP prefix block, and poisoned-TLP egress block. It also defines correctable-error status and mask fields for receiver, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, internal correctable, and header-log-overflow events.

The same `DEV0_EPF5` section defines AER capability/control fields (`FIRST_ERR_PTR`, ECRC generation/check capability and enable bits, multi-header recording, TLP prefix logging, and completion-timeout logging capability), four 32-bit TLP header log words, four 32-bit TLP prefix log words, six BAR capability/control pairs, Power Budgeting data selection/data/capability fields, DPA capability/status/control/power-allocation fields, ACS capability/control bits, PASID capability/control bits, and ARI capability/control bits.

The `nbio_nbif0_bif_cfg_dev2_epf6_bifcfgdecp` block starts a distinct endpoint-function image. In this chunk it provides conventional PCI header macros for vendor and device IDs, command bits, revision/class-code bytes, cache-line and latency registers, header/BIST, BARs, adapter IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, and PMI status/control. It then continues through PCIe capability fields, device/link capability and status fields, MSI and MSI-X programming fields, AMD vendor-specific enhanced capability words, AER correctable status and logs, BAR capability fields, Power Budgeting, DPA, ACS, PASID, and ARI.

The `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp` block is a fuller endpoint-function image for `DEV0_EPF6`. It includes conventional PCI header fields plus `STATUS`, `CARDBUS_CIS_PTR`, full Power Management capability fields, USB-style sideband registers (`SBRN`, `FLADJ`, and `DBESL_DBESLD`), PCIe capability/device/link fields including Device Capability 2, Device Control 2, Device Status 2, and Link Status 2, MSI/MSI-X fields, AMD vendor-specific fields, full AER uncorrectable and correctable status/mask/severity/control/log definitions, BAR controls, Power Budgeting, DPA, ACS, PASID, and ARI.

The `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp` block defines a similar but somewhat smaller `DEV0_EPF7` endpoint-function image. It has conventional PCI header fields, PMI status/control, PCIe capability/device/link fields, MSI/MSI-X, AMD vendor-specific capability fields, AER correctable status and logs, BAR capability fields, Power Budgeting, DPA, ACS, PASID, and ARI. Unlike the complete `DEV0_EPF6` block in this chunk, the visible `DEV0_EPF7` AER section does not include the full uncorrectable-error status/mask/severity group here.

The `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` block begins near the end of the chunk. It covers the conventional PCI header and PMI status/control fields for `DEV1_EPF0`, then starts the PCIe capability list and PCIe capability fields. The chunk ends after the `PCIE_CAP` masks, so later `DEV1_EPF0` PCIe device/link/interrupt/error fields belong to the next chunk.

## Control Flow

This header has no executable control flow. Runtime control flow is supplied by AMDGPU code that includes this generated file, selects the NBIO 7.7.0 register map for the detected ASIC, reads or writes a register through the SOC15 or PCIe-port accessors, and uses these constants to extract or compose fields.

Typical consumer flow is:

1. Select the matching `cfgBIF_CFG_*` or `reg*` offset from the paired NBIO 7.7.0 offset header.
2. Read the raw register value through the appropriate AMDGPU accessor.
3. Decode fields with `*_MASK` and `*__SHIFT`, or update a field with `REG_SET_FIELD`/equivalent read-modify-write logic.
4. Preserve unrelated and reserved bits, then write back only when the target field is writable.

The hardware behavior represented by these macros includes PCI command enablement, BAR sizing, power-management state and PME control, PCIe link/device capability reporting, MSI/MSI-X programming, AER policy and logging, power-budget and DPA controls, ACS isolation policy, PASID enablement, and ARI function-group behavior.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time register-layout description.

The state described by these macros lives in hardware PCIe/NBIO configuration registers. Identity and capability fields such as vendor/device IDs, class codes, supported link speeds/widths, MSI/MSI-X sizes, BAR size support, AER capability bits, DPA support, ACS support, PASID width/support, and ARI support are generally hardware- or firmware-defined. Control fields such as `COMMAND`, `PMI_STATUS_CNTL`, `DEVICE_CNTL`, `DEVICE_CNTL2`, MSI/MSI-X enables and masks, AER masks/severity/ECRC controls, BAR controls, DPA controls, ACS controls, PASID controls, and ARI controls are writable hardware state whose lifetime depends on PCI function reset, FLR, GPU reset, suspend/resume, and power-management domains.

Status fields such as PCI status bits, Device Status, Link Status, Link Status 2, MSI pending bits, AER correctable/uncorrectable status, AER header logs, TLP prefix logs, and DPA status are live hardware observations. The generated masks do not encode reset defaults, read-only/write-only access, write-one-to-clear semantics, side effects on read, or required access width.

## Dependencies And Integration Points

These macros depend on the matching NBIO 7.7.0 register address definitions in `nbio_7_7_0_offset.h`. A field macro is only meaningful when paired with the corresponding endpoint-function and register offset. For example, a `BIF_CFG_DEV0_EPF6_PCIE_ACS_CNTL__P2P_REQUEST_REDIRECT_EN_MASK` value may have the same bit position as other ACS instances, but it must still be applied to the `DEV0_EPF6` ACS control register, not a neighboring function's ACS control register.

Integration points include:

- `amdgpu/nbio_v7_7.c`, which includes the NBIO 7.7.0 offset and shift/mask headers and exposes `nbio_v7_7_funcs` plus NBIO register initialization, doorbell, interrupt, HDP flush, clock-gating, and remap operations.
- AMDGPU register helper macros such as `REG_SET_FIELD`, which rely on the generated `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- PCIe enumeration and diagnostics that read endpoint-function identity, class, command/status, BAR, capability-list, interrupt, MSI, MSI-X, and power-management fields.
- PCIe link-management and capability-reporting paths that decode device/link capability and negotiated link status.
- RAS/AER handling that decodes correctable and uncorrectable status, error masks, severity policy, first-error pointer, ECRC controls, TLP header logs, and TLP prefix logs.
- IOMMU, virtualization, and peer-to-peer isolation paths that care about ACS, PASID, and ARI capability/control state.
- Power-management paths that inspect or program PMI, Power Budgeting, and Dynamic Power Allocation fields.

## Risks

The main risk is silent hardware misprogramming if a generated mask or shift is wrong, incomplete because of a chunk boundary, or combined with an offset from the wrong endpoint-function block. The macro names differ mostly by `DEV*` and `EPF*`; a copy/paste mistake can compile cleanly while targeting the wrong function image.

Chunk boundaries split logical register groups. This chunk starts after the `DEV0_EPF5_PCIE_UNCORR_ERR_STATUS` shift definitions and early masks, so a complete analysis of that register must merge with the previous chunk. It also ends in the middle of the `DEV1_EPF0` PCIe capability area, so the following chunk is needed before treating `DEV1_EPF0` as complete.

Reserved and status fields require care. The presence of a mask does not imply that a bit is writable, stable, or safe to preserve blindly across resets. AER status and log fields may be latched or write-one-to-clear, MSI pending fields may reflect interrupt delivery state, and power-management/link fields may change asynchronously with hardware state.

Access width is another practical risk. The chunk mixes 8-bit, 16-bit, and 32-bit PCI configuration concepts under a generated macro namespace. Consumers need to use the access width, alignment, and read-modify-write policy expected by the surrounding driver and the hardware register block.

## Test Signals

Useful validation signals are hardware- and integration-oriented:

- The AMDGPU tree builds for NBIO 7.7.0, proving that generated macro names referenced by consumers resolve.
- Generator or static checks confirm that every register group in this chunk has a matching `nbio_7_7_0_offset.h` entry with the same `BIF_CFG_DEV*_EPF*_*` identity.
- PCIe enumeration on matching AMD hardware reports plausible `DEV0_EPF5`, `DEV2_EPF6`, `DEV0_EPF6`, `DEV0_EPF7`, and `DEV1_EPF0` identity, class, BAR, capability, MSI/MSI-X, and power-management data.
- Link diagnostics decode expected negotiated link speed/width and capability bits from the device/link fields covered here.
- MSI and MSI-X interrupt paths work while exercising enable, mask, pending, table, and PBA fields for the relevant endpoint functions.
- AER/RAS tests or fault injection produce correct decoding of correctable and uncorrectable errors, masks, severity fields, first-error pointer, header logs, and TLP prefix logs.
- Virtualization and peer-to-peer isolation testing validates ACS, PASID, and ARI capability/control handling without cross-programming adjacent endpoint functions.
- Suspend/resume, FLR, hot reset, and GPU reset testing verifies that writable PCIe, interrupt, AER, power-management, ACS, PASID, and ARI state is reinitialized by higher-level driver paths rather than relying on this header for defaults.
