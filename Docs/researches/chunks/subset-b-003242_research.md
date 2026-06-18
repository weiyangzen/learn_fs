# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 39093-41521

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 shift/mask header. It defines C preprocessor constants for PCIe/NBIO configuration-space bitfields in the `BIF_CFG_DEV0_EPF0` SR-IOV virtual-function register blocks.

The range starts in the middle of the `VF11` block, at the mask definitions for `BIF_CFG_DEV0_EPF0_VF11_0_LINK_CAP2`, continues through the rest of `VF11`, covers complete `VF12`, `VF13`, and `VF14` configuration images, and ends at the first command-field shifts for `VF15`. The constants encode bit offsets and masks only; register addresses are supplied by the paired NBIO offset header and runtime accessors elsewhere in AMDGPU.

## Major Register Groups

The `VF11` portion covers the PCIe capability tail for a virtual function. It includes Link Capability 2, Link Control 2, Link Status 2, reserved slot capability/control/status 2 fields, MSI/MSI-X capability fields, AMD vendor-specific enhanced capability fields, AER fields, ATS fields, and ARI fields.

The `VF12`, `VF13`, and `VF14` blocks are full repeated virtual-function PCI configuration images under address blocks named like `nbio_nbif0_bif_cfg_dev0_epf0_vf12_bifcfgdecp`. Each complete VF block defines:

- Conventional PCI header fields: vendor/device IDs, command/status, revision and class-code bytes, cache line, latency, header type, BIST, BAR placeholders, adapter ID, ROM BAR, capability pointer, interrupt line, and interrupt pin.
- PCIe capability fields: capability-list metadata, PCIe capability version/type/slot/interrupt-message fields, Device Capability/Control/Status, Link Capability/Control/Status, Device Capability 2, Device Control 2, Device Status 2, Link Capability 2, Link Control 2, and Link Status 2.
- Interrupt capability fields: MSI list/control, MSI message address/data, mask and pending registers, 64-bit MSI variants, MSI-X list/control, MSI-X table, and MSI-X PBA.
- Vendor-specific and AER enhanced capability fields: enhanced capability headers, AMD vendor scratch fields, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- IOMMU/SR-IOV-adjacent PCIe capabilities: ATS capability/control and ARI capability/control, with enhanced capability list headers for each.

The final `VF15` portion only begins the next repeated block. It includes vendor ID, device ID, and the first `COMMAND` shifts through `FAST_B2B_EN`; the corresponding `COMMAND` mask definitions and following status fields are outside this chunk.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The exported interface is the generated macro namespace:

- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit position for a field.
- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>_MASK` gives the field mask in the containing PCI config register.

The macros are intended for use with AMDGPU register helpers or direct bit manipulation after the caller has selected the matching NBIO 7.4 register offset. The chunk contains 2,133 `#define` entries across 285 register-name groups, with most layouts repeated exactly for `VF12`, `VF13`, and `VF14`.

## Control Flow

This header has no executable control flow. Runtime behavior is supplied by code that includes this header, chooses the NBIO 7.4 register table for the detected ASIC, reads or writes a PCIe/NBIO configuration register, and combines the raw value with these shift and mask constants.

Typical consumer flow is:

1. Use the paired offset/base-index macro for a `BIF_CFG_DEV0_EPF0_VF*_0_*` register.
2. Read the register through AMDGPU MMIO, indexed register, or PCI configuration access paths.
3. Decode fields with the `*_MASK` and `*__SHIFT` constants.
4. For writable controls, preserve unrelated and reserved bits, insert the shifted field value, and write the result back.

The hardware flows represented by the fields include PCI command enablement, PCI status reporting, BAR decode metadata, PCIe payload/read-request sizing, relaxed ordering and no-snoop control, FLR and completion-timeout control, link training and retraining, 8 GT/s equalization status, MSI/MSI-X programming, AER reporting and masking, ATS address-translation cache control, and ARI function-group control.

## State And Persistence

The header itself is stateless and persists no data. It is a compile-time description of register layout.

The state described by the macros lives in hardware PCIe/NBIO configuration registers. Capability fields such as vendor/device IDs, class codes, PCIe capability metadata, supported link speeds/widths, MSI/MSI-X capability sizes, AER capability bits, ATS queue depth, and ARI support are generally hardware- or firmware-defined. Control fields such as `COMMAND`, `DEVICE_CNTL`, `LINK_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL2`, MSI/MSI-X enables and masks, AER masks/severity, ATS `ATC_ENABLE`, and ARI function-group enables are writable hardware state whose lifetime depends on the relevant PCIe function reset, FLR, GPU reset, suspend/resume, and power-management domains.

Status fields such as PCI status error bits, Device Status, Link Status, Link Status 2 equalization flags, MSI pending bits, uncorrectable/correctable AER status, AER header logs, TLP prefix logs, and ATS/ARI status-like capability data are live hardware observations. This header does not encode reset defaults, access width, read-only/write-only behavior, write-one-to-clear semantics, or whether reads have side effects.

## Dependencies And Integration Points

These definitions must remain synchronized with the matching NBIO 7.4 register offset header. A macro such as `BIF_CFG_DEV0_EPF0_VF14_0_PCIE_UNCORR_ERR_STATUS__CPL_TIMEOUT_STATUS_MASK` is only meaningful when paired with the corresponding `VF14` register address; using the same field mask with a different VF or ASIC register map can silently decode or update the wrong bits.

Integration points include:

- AMDGPU NBIO 7.4 ASIC support that includes generated `asic_reg/nbio` headers for register access.
- PCIe configuration and diagnostics paths that inspect virtual-function vendor/device identity, class code, command/status, BAR, capability-list, and interrupt metadata.
- SR-IOV virtual-function setup and reset paths, where repeated `VF11` through `VF15` register layouts distinguish individual virtual-function config images.
- PCIe link-management code that decodes link capability/control/status, negotiated speed/width, retrain state, bandwidth status, and 8 GT/s equalization fields.
- Interrupt setup code that programs or verifies MSI/MSI-X enablement, address/data, masks, pending bits, table BIR/offset, PBA BIR/offset, function mask, and table size.
- RAS/AER handling paths that decode uncorrectable/correctable errors, masks, severity policy, first-error pointer, ECRC controls, header logs, and TLP prefix logs.
- IOMMU and PCIe feature integration that uses ATS controls and ARI capability/control fields for translated requests and alternative function numbering.

## Risks

The main risk is silent hardware misprogramming if generated masks or shifts are wrong, truncated at a chunk boundary, or combined with an offset from the wrong virtual-function block. A single bit-position error can enable the wrong PCI command bit, misdecode link training status, corrupt MSI/MSI-X setup, suppress the wrong AER error, or toggle ATS/ARI controls unexpectedly.

The repeated VF layouts are useful but easy to misuse. `VF12`, `VF13`, and `VF14` field names often differ only by the VF number; copy/paste errors in consumers can target the wrong virtual function while compiling cleanly. The chunk boundaries also split logical register groups: it begins after the `VF11_LINK_CAP2` shift definitions and ends before the `VF15_COMMAND` masks, so generated documentation or audits must merge adjacent chunks before treating either register group as complete.

Reserved fields and status registers need special care. Many `RESERVED` masks are present only so generated layouts cover the full register; software should not infer that reserved bits are writable. AER status, PCI status, Device Status, MSI pending, and log registers may have hardware-specific clear or latch semantics that are not represented by these macros.

Access width is another risk. Several fields describe 8- or 16-bit PCI configuration concepts inside generated 32-bit macro naming, while AER logs, BARs, MSI-X table/PBA offsets, and vendor scratch registers use 32-bit masks. Consumers must use the access width and read-modify-write rules expected by the hardware and surrounding driver code.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- The AMDGPU tree builds with NBIO 7.4 headers included, proving that the generated macro names referenced by consumers resolve.
- Static checks or generator validation confirm that each register in this chunk has a matching NBIO 7.4 offset/base-index definition for the same `BIF_CFG_DEV0_EPF0_VF*_0_*` name.
- PCIe enumeration of matching AMD hardware reports plausible virtual-function vendor/device/class data, PCIe capabilities, MSI/MSI-X capabilities, AER capability, ATS capability, and ARI capability.
- SR-IOV enable/disable and VF reset paths can configure `VF12`, `VF13`, and `VF14` independently without cross-programming neighboring VF blocks.
- MSI/MSI-X interrupts for virtual functions work under enable, mask, pending, table, and PBA scenarios.
- Link diagnostics decode expected negotiated speed/width and equalization status from the Link Status and Link Status 2 fields.
- AER/RAS tests or fault injection decode correctable and uncorrectable error status, masks, severity, and logged TLP headers/prefixes consistently with hardware documentation.
- Suspend/resume, FLR, hot reset, and GPU reset testing verifies that writable PCIe controls, interrupt controls, AER policy, ATS enablement, and ARI controls are restored or reinitialized by higher-level driver paths rather than relying on this header for defaults.
