# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h

Chunk: `subset-b-002917`
Covered source range: lines 31772-34201 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h`

## Purpose

This chunk is a generated AMD NBIO 2.3 register field mask header section. It contains C preprocessor constants for PCI/PCIe configuration-space register fields exposed through the NBIO/NBIF block; it is not executable driver logic.

The covered range contains 2,143 `#define` lines and 281 comment lines. It spans the tail of the `BIF_CFG_DEV0_EPF0_VF4` virtual-function configuration block, complete `BIF_CFG_DEV0_EPF0_VF5` and `BIF_CFG_DEV0_EPF0_VF6` blocks, and nearly all of `BIF_CFG_DEV0_EPF0_VF7` through the first two `PCIE_ARI_CNTL` shift definitions. The `addressBlock` comments identify the covered VF blocks as `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`, `vf6_bifcfgdecp`, and `vf7_bifcfgdecp`; VF4 began in the previous chunk.

The chunk starts mid-register: line 31772 is only the `BIF_CFG_DEV0_EPF0_VF4_LINK_CAP2__DRS_SUPPORTEDRESERVED_MASK`, while the matching register comment and most `LINK_CAP2` fields are in the prior chunk. It also ends mid-register: `BIF_CFG_DEV0_EPF0_VF7_PCIE_ARI_CNTL__ARI_FUNCTION_GROUP__SHIFT` and the three ARI control masks are in the next lines after this chunk. File-level reconciliation should treat both boundaries as expected split points.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The interface is the generated macro contract consumed by AMDGPU register helpers:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit shift used to encode or decode a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask, usually as a 16-bit or 32-bit literal with `L` suffix.
- The matching configuration-space offsets live in companion offset headers, notably `nbio_2_3_offset.h` for this NBIO generation and the closely related `nbif_6_3_1_offset.h` VF configuration-space layout.

Important register families in this chunk include:

- `BIF_CFG_DEV0_EPF0_VF4_LINK_CNTL2` and `LINK_STATUS2`, covering target link speed, compliance entry, autonomous speed disable, de-emphasis, PCIe 8 GT/s equalization phase status, downstream presence, and DRS message status.
- `VF4`, `VF5`, `VF6`, and `VF7` MSI/MSI-X capability fields: capability-list IDs and next pointers, MSI enable/multiple-message/64-bit/per-vector masking fields, message address/data, mask and pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset.
- Complete `VF5`, `VF6`, and `VF7` standard PCI configuration fields: vendor/device IDs, command/status, revision/class code bytes, cache line, latency, header, BIST, six BARs, CIS pointer, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- `VF5`, `VF6`, and `VF7` PCIe capability fields: PCIe capability list/header, device capability/control/status, link capability/control/status, device capability 2/control 2/status 2, and link capability 2/control 2/status 2.
- Vendor-specific enhanced capability fields: VSEC capability ID/version/next pointer, VSEC ID/revision/length, and two 32-bit scratch registers.
- Advanced Error Reporting fields: enhanced capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- ATS fields: capability header, invalidate queue depth, page-aligned request, global invalidate support, smallest translation unit (`STU`), and `ATC_ENABLE`.
- ARI fields: enhanced capability header, MFVC/ACS function group capability bits, next function number, and the beginning of ARI control for MFVC and ACS function group enables.

The repeated VF5/VF6/VF7 blocks each expose 26 basic PCI configuration register comments and 53 PCIe/extended capability register comments in this chunk. The field layouts are intentionally near-identical across those virtual functions; only the VF prefix changes.

## Control Flow

This header has no internal control flow. At compile time, consumers include the header and use the macros in register read/modify/write expressions. Runtime control flow lives in AMDGPU/NBIO code that:

1. Includes `nbio/nbio_2_3_offset.h` and `nbio/nbio_2_3_sh_mask.h`.
2. Reads a 16-bit or 32-bit NBIO/PCIe register through helper APIs such as `RREG32_SOC15`, `RREG32_PCIE`, or `RREG32_NO_KIQ`.
3. Extracts fields by masking and shifting, or constructs values with helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.
4. Writes back via `WREG32_SOC15`, `WREG32_PCIE`, or related helpers when the field is writable.

Direct local include sites for this NBIO mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which programs NBIO doorbell ranges, interrupt controls, memory aperture state, PCIe LTR, link/strap behavior, and HDP remap registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which uses NBIO register definitions while implementing SR-IOV/MxGPU mailbox communication between a VF and PF.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include the header for NBIO/PCIe strap and link-related power-management interactions.

The exact VF4-VF7 macros in this chunk are configuration-space field definitions rather than active logic. They become behaviorally relevant when SR-IOV, virtualization, PCIe capability setup, MSI/MSI-X programming, AER reporting, ATS, or ARI paths address the corresponding virtual-function configuration registers.

## State And Persistence Behavior

The header itself is stateless. It does not allocate memory, perform I/O, or persist data. Its only persistence is as compile-time constants embedded into object code.

The hardware state described by these macros lives in PCI/PCIe configuration registers for virtual functions under device 0, endpoint function 0. That state persists until changed by the driver, PCI core, host PF/hypervisor, firmware, FLR, bus reset, GPU reset, suspend/resume, or hardware error handling. Important state categories include:

- VF identity and configuration header state, including vendor/device IDs, class code, BAR decode fields, command enables, status flags, capability pointer, ROM BAR, and interrupt pin/line fields.
- PCIe capability state, including max payload/read-request capabilities, relaxed ordering, phantom functions, no-snoop, extended tag, L0s/L1 exit latencies, link width/speed capability, active link status, slot clock, bandwidth management, and autonomous bandwidth status.
- Link-control 2 and link-status 2 state for target speed, compliance mode, de-emphasis, and equalization progress/failure signals.
- MSI/MSI-X state such as enable bits, vector count, message address/data, per-vector mask and pending bits, MSI-X table location, PBA location, and function mask.
- AER state, including uncorrectable/correctable status latches, masks, severity policy, first-error pointer, ECRC controls, multi-header controls, header logs, and TLP prefix logs.
- ATS and ARI state, including ATC enable, STU, invalidate queue depth, page-aligned request support, global invalidate support, next function number, and ARI function group controls.

These macros do not encode access type or ordering. Status fields may be read-only or write-one-to-clear depending on the hardware specification; control fields may be owned by the PF, VF, PCI core, IOMMU setup, or firmware. Consumers must respect the register spec and virtualization ownership model.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor. The practical dependencies are the AMDGPU register helper conventions and the matching offset headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h`

`nbio_2_3_offset.h` contains matching `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` offsets for VF4-VF7 configuration registers. The related NBIF 6.3.1 offset header exposes similar `cfgBIF_CFG_DEV0_EPF0_VF*_*` names without the `_0` instance suffix. These offset macros pair with this chunk's masks/shifts when code needs to access a VF's config-space fields through NBIO/NBIF register windows.

Integration points in the driver stack include:

- AMDGPU NBIO initialization and management in `amdgpu/nbio_v2_3.c`.
- SR-IOV/MxGPU VF-PF mailbox flows in `amdgpu/mxgpu_nv.c`.
- SMU 11 power-management code for Navi10 and Sienna Cichlid ASICs, which uses NBIO and PCIe-related register definitions while managing DPM, link, and strap-related behavior.
- Linux PCI/MSI/MSI-X/AER/ATS/ARI semantics, because these fields mirror standard and extended PCIe capability layouts.
- GPU virtualization infrastructure, where VF configuration-space fields may be shadowed, trapped, or mediated by a PF driver, hypervisor, or host PCI subsystem.

## Risks And Edge Cases

The main implementation risk is silent hardware misprogramming. These are untyped preprocessor constants, so the compiler cannot verify that a mask belongs to the register being read, that the field value fits the mask, or that a VF5 macro is not accidentally used for VF6/VF7.

Chunk boundaries are a real reconciliation risk. `VF4_LINK_CAP2` is incomplete at the start of this chunk, and `VF7_PCIE_ARI_CNTL` is incomplete at the end. Pair-completeness checks must account for adjacent chunks before reporting missing masks or shifts.

Repeated VF blocks are easy to confuse. VF5, VF6, and VF7 carry identical layouts with only the virtual-function prefix changed. A copy/paste instance error can compile cleanly but address or interpret the wrong VF's configuration state, which is especially dangerous for MSI/MSI-X, AER, ATS, and ARI fields.

Configuration-space width matters. Many fields are 8-bit or 16-bit PCI configuration fields, while others are 32-bit extended capability registers. Using 32-bit helpers against narrower fields or assuming natural alignment without checking the offset header can corrupt neighboring config bytes.

Virtualization ownership matters. A VF driver may not be allowed to write all PCIe capability, AER, ATS, ARI, MSI-X table, or BAR fields directly. Some values may be emulated, filtered, or reset by the PF or hypervisor. Code that treats these masks as normal MMIO ownership can break SR-IOV isolation.

Error-reporting fields have side effects. AER status and header-log registers may latch first-error information; clearing, masking, or changing severity at the wrong time can hide root-cause data or change whether an error is fatal/nonfatal/correctable.

ATS and ARI fields affect IOMMU and PCIe routing behavior. Incorrect `ATC_ENABLE`, `STU`, invalidate queue, ARI next-function, or function-group programming can lead to stale translations, isolation failures, bad requester IDs, or enumeration issues.

High-bit masks such as `0x80000000L` should be handled as unsigned 32-bit quantities by consumers. Ad hoc signed arithmetic or implicit narrowing can produce incorrect comparisons or shifts on some build configurations.

## Test Signals

Useful validation signals include:

- build coverage for translation units that include `nbio_2_3_sh_mask.h`, especially `amdgpu/nbio_v2_3.c`, `amdgpu/mxgpu_nv.c`, `pm/swsmu/smu11/navi10_ppt.c`, and `pm/swsmu/smu11/sienna_cichlid_ppt.c`;
- generated-header consistency checks across the complete file, verifying that every field has a matching `__SHIFT`/`_MASK` pair after adjacent chunks are merged;
- offset/mask consistency checks against `nbio_2_3_offset.h` and `nbif_6_3_1_offset.h`, especially for VF4-VF7 standard PCI, PCIe capability, MSI/MSI-X, AER, ATS, and ARI registers;
- duplicate-layout checks confirming that VF5, VF6, and VF7 field masks/shifts are identical where expected and differ only by prefix;
- SR-IOV boot and teardown tests with multiple VFs enabled, checking VF enumeration, BAR sizing, class/vendor/device IDs, command/status behavior, and FLR/reset recovery;
- MSI and MSI-X tests for VF interrupt delivery, vector enable/disable, masking, pending bits, function mask behavior, and table/PBA address interpretation;
- PCIe AER injection or fault-observation tests that confirm correct uncorrectable/correctable status bits, masks, severity fields, first-error pointer, and header/TLP-prefix logging;
- ATS/IOMMU validation with VF DMA enabled, including ATC enable/disable, invalidation behavior, page-aligned request handling, and suspend/resume reset behavior;
- ARI/SR-IOV enumeration tests confirming next-function number and function-group controls do not confuse PCI core routing or VF discovery;
- register readback tests using the normal AMDGPU register helpers, confirming that shifted values occupy only the intended masked bits and that no adjacent config fields change unexpectedly.
