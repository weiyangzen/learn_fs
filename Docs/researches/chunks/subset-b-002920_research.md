# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 39062-41493

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, allocation paths, locks, loops, branches, or direct register accesses in this range.

The slice starts at the tail of `BIF_CFG_DEV0_EPF0_VF14_PCIE_ARI_ENH_CAP_LIST`, covers the ARI capability/control masks for VF14, then defines complete repeated PCIe configuration-space field layouts for `BIF_CFG_DEV0_EPF0_VF15`, `BIF_CFG_DEV0_EPF0_VF16`, and `BIF_CFG_DEV0_EPF0_VF17`. It then begins the `BIF_CFG_DEV0_EPF0_VF18` block and stops inside `BIF_CFG_DEV0_EPF0_VF18_DEVICE_CNTL2`; the remaining VF18 PCIe extended capability, MSI/MSI-X, AER, ATS, and ARI fields continue after this chunk.

Although this file is under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bitfield positions for NBIO 2.3 SR-IOV virtual-function PCI configuration-space images. Each generated hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

The companion address file, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, provides the matching `cfgBIF_CFG_DEV0_EPF0_VF*_*` register locations. Runtime AMDGPU code combines those offsets with this shift/mask header through helpers such as `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF14 fragment completes the end of a virtual-function extended capability chain. It includes `PCIE_ARI_ENH_CAP_LIST` masks for capability ID/version/next pointer, `PCIE_ARI_CAP` fields for MFVC/ACS function-group capability and next-function number, and `PCIE_ARI_CNTL` fields for enabling MFVC/ACS function groups and selecting an ARI function group. The matching VF14 ATS capability and most of its preceding PCIe block are outside this chunk.

The full VF15 through VF17 blocks repeat a standard SR-IOV VF PCI Type 0 configuration image. Each block starts with identity and header fields: vendor ID, device ID, command, status, revision, programming interface, subclass, base class, cache line, latency, header type/device type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line/pin, and min-grant/max-latency bytes.

The PCIe capability portions for VF15 through VF17 define `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, FLR capability/initiation, completion timeout controls, ARI forwarding, atomic operation enables, ID-based ordering, LTR, OBFF, 10-bit tag support, link speed/width, ASPM/power-management controls, link disable/retrain, common clock, autonomous width/speed disables, target link speed, de-emphasis, compliance controls, equalization status, and downstream/component presence status.

The MSI and MSI-X portions of VF15 through VF17 cover capability-list linkage, MSI enable/multiple-message/64-bit/per-vector masking controls, MSI address/data/mask/pending fields, 64-bit MSI aliases, MSI-X table size/function mask/enable fields, MSI-X table BIR/offset, and PBA BIR/offset fields. These constants describe how the VF interrupt capability appears in config space and how address/data/mask/pending state is packed.

The vendor-specific and AER portions define PCIe vendor-specific enhanced capability list/header fields, two vendor-specific payload dwords, AER enhanced capability list fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header log dwords, and four TLP prefix log dwords. Covered AER bits include DLP, surprise down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked conditions.

The ATS and ARI portions at the end of each full VF block define enhanced capability list entries plus ATS capability/control fields and ARI capability/control fields. ATS fields include invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable. ARI fields expose function-group support, next-function number, function-group enable bits, and selected function group.

The VF18 block begins another repeated VF config-space map. This chunk covers VF18 from vendor/device ID through `DEVICE_CNTL2` masks, including the standard header, BARs, PCIe capability, device/link capability and control/status, and the start of PCIe capability 2 control. It does not include VF18 `DEVICE_STATUS2`, link capability 2, MSI/MSI-X, vendor-specific, AER, ATS, or ARI fields.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes the generated constants:

1. AMDGPU code selects a `cfgBIF_CFG_DEV0_EPF0_VF*_*` offset from `nbio_2_3_offset.h`.
2. It reads or composes a 16-bit or 32-bit PCIe config-space value through the AMD register access layer.
3. It applies this header's `__SHIFT` and `_MASK` macros directly or via `REG_SET_FIELD`/`REG_GET_FIELD`.
4. It writes a control value, decodes a capability/status value, polls a hardware-owned bit, clears a sticky status, or exposes decoded state to a higher-level PCIe, SR-IOV, reset, interrupt, or diagnostics path.

Typical flows that can consume these fields include VF PCI capability presentation, VF MSI/MSI-X setup, AER error logging and clearing, function-level reset, PCIe link/power policy, ATS/ARI virtualization support, and PF/hypervisor inspection of VF config state.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU's PF/SR-IOV management code.

The represented state includes identity/header values, BAR and ROM address windows, command/status bits, capability-list pointers, PCIe capability/control/status fields, link capability and link training state, MSI/MSI-X programming state, vendor-specific capability payloads, AER error status/mask/severity/log data, ATS enablement and invalidation capability state, and ARI function-group controls. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The generated masks do not encode access permissions, reset defaults, side effects, polling rules, or ownership boundaries.

VF15 through VF17 are complete within this chunk, so their repeated config-space layout can be reasoned about locally. VF14 and VF18 are boundary fragments and require adjacent chunks before making whole-VF or whole-register claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 2.3 register database. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies the matching config-space addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies reset/default values for the same register families where generated.
- AMDGPU register helper macros and accessors, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Direct in-tree consumers of the NBIO 2.3 generated headers include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`. The most relevant integration surfaces are AMDGPU NBIO/BIF setup, PCIe link control, SR-IOV VF lifecycle, MXGPU virtualization paths, VF interrupt delivery, ATS/ARI capability handling, AER diagnostics, reset/FLR flows, and suspend/resume or runtime power transitions.

These fields also overlap generic PCIe concepts managed by platform firmware and the Linux PCI core: command/status, BARs, MSI/MSI-X, device/link control, AER, ATS, ARI, LTR, OBFF, completion timeout, and FLR. AMDGPU must pair the generated masks with the correct register address and with the ownership rules for the specific hardware access path.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts in the middle of VF14's extended capability tail and stops in the middle of VF18 `DEVICE_CNTL2`; adjacent chunks are required for complete VF14 and VF18 analysis.
- These are untyped preprocessor constants. A stale mask or shift can compile cleanly while decoding or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Off-by-one suffix mistakes around VF15, VF16, VF17, and VF18 could silently target the wrong virtual function and break SR-IOV isolation or diagnostics.
- Register-address and field-mask mismatches are easy in generated headers. A valid `VF16_LINK_CNTL` mask applied to a `VF17` or non-VF offset may still produce plausible bit operations while corrupting unrelated config state.
- PCIe control fields are interoperability-sensitive. Incorrect FLR, max payload, max read request, completion timeout, relaxed-ordering, no-snoop, LTR, OBFF, ARI, ATS, or link-control values can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Width, aliasing, table offset/BIR, mask, or pending-bit mistakes can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, mask, severity, header log, and TLP prefix log fields can be sticky, write-one-to-clear, or hardware-owned. Generic read/modify/write treatment can clear diagnostic evidence or leave errors masked incorrectly.
- BAR and ROM fields affect resource exposure. Incorrect masks can expose invalid apertures or confuse VF resource sizing.
- ATS and ARI fields are virtualization and addressing sensitive. Incorrect ATC enable/STU, invalidate capability interpretation, next-function number, or function-group controls can affect translation caching, VF enumeration, and function isolation.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 2.3 support enabled; missing, renamed, or duplicated macros should surface in `nbio_v2_3.c`, `mxgpu_nv.c`, SMU11 files, or other generated-header include paths.
- Compare the VF15 through VF17 field layouts against `nbio_2_3_offset.h` and `nbio_2_3_default.h` to confirm the register names, order, and repeated VF stride remain synchronized.
- Boot affected hardware and confirm PCIe config exposure remains sane: VF identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, AER, ATS, and ARI should decode consistently.
- In SR-IOV or MXGPU configurations, create and remove VFs around the VF15-VF18 range, bind guest drivers, exercise VF FLR, and verify that VF isolation, config-space access, ATS/ARI behavior, and mailbox/reset flows remain stable.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion timeout behavior, LTR/OBFF state, and FLR completion.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.
- For ATS-capable configurations, exercise IOMMU/ATS enablement and invalidation paths; translation faults, stale DMA mappings, or inconsistent ATC behavior can point to ATS control/capability field issues.

## Chunk Notes

- Lines 39062-39079 are only the end of VF14, specifically the ARI enhanced capability and ARI cap/control fields.
- Lines 39080-41167 are complete `BIF_CFG_DEV0_EPF0_VF15`, `VF16`, and `VF17` PCIe VF config-space shift/mask blocks.
- Lines 41168-41493 begin `BIF_CFG_DEV0_EPF0_VF18` and end inside `BIF_CFG_DEV0_EPF0_VF18_DEVICE_CNTL2`, after the `IDO_COMPLETION_ENABLE_MASK` line in the assigned slice; subsequent VF18 fields are outside this work item.
