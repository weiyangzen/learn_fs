# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 43920-46353

## Scope

This chunk is a generated AMD NBIO 2.3 register shift/mask header segment. It contains C preprocessor constants only: no functions, structs, storage, locks, allocation, persistence, or executable control flow.

The range starts in the tail of the `BIF_CFG_DEV0_EPF0_VF21_PCIE_ATS_CAP` field layout, continues through the last VF21 ATS/ARI capability fields, covers complete `BIF_CFG_DEV0_EPF0_VF22_*`, `BIF_CFG_DEV0_EPF0_VF23_*`, and `BIF_CFG_DEV0_EPF0_VF24_*` virtual-function PCI configuration layouts, and then covers the beginning of `BIF_CFG_DEV0_EPF0_VF25_*` through the first fields of `BIF_CFG_DEV0_EPF0_VF25_DEVICE_CNTL2`. Adjacent chunks are required for the full VF21 ATS capability and the remainder of VF25 extended capability, MSI/MSI-X, AER, ATS, and ARI definitions.

Although this path is under a local `ceph-client` source mirror, the content is AMDGPU hardware metadata for NBIO/NBIF PCIe configuration space. It does not implement Ceph or distributed filesystem behavior.

## Purpose

This header publishes bitfield positions for NBIO 2.3 PCIe configuration registers. Each hardware field is represented by a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK` gives the mask for preserving, clearing, setting, or decoding the field.

The matching register address/offset constants live in `nbio_2_3_offset.h`, and reset/default values live in `nbio_2_3_default.h`. Runtime AMDGPU code combines these masks with generated offsets and register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and related NBIO accessors.

## Important Macro Families

The small VF21 tail covers PCIe Address Translation Service and Alternative Routing-ID Interpretation fields. `BIF_CFG_DEV0_EPF0_VF21_PCIE_ATS_CAP` contributes ATS queue/page/global-invalidate capability masks, `PCIE_ATS_CNTL` provides small translation unit and ATC enable fields, and `PCIE_ARI_*` provides enhanced capability list metadata plus ARI next-function/function-group capability and control bits.

The complete VF22, VF23, and VF24 blocks are repeated per-virtual-function PCI configuration images under endpoint function 0. Each block begins with conventional PCI header fields: vendor/device ID, command, status, revision, class code bytes, cache line, latency, header type, BIST, six BARs, CIS pointer, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, and min grant/max latency. The command/status fields include I/O, memory, bus mastering, special cycle, memory write invalidate, parity/SERR behavior, interrupt disable, capability-list presence, parity/system/error status, target/master abort, and DEVSEL timing masks.

The VF22-VF24 PCIe capability sections describe device and link capability/control/status. `DEVICE_CAP` and `DEVICE_CNTL` include max payload support/size, phantom functions, extended tags, relaxed ordering, no-snoop, auxiliary power PM, max read request size, role-based error reporting, captured slot power, and FLR capability/initiation. `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` describe link speed, width, ASPM/PM support, exit latencies, common clock, retrain/link disable, hardware autonomous width disable, bandwidth-management interrupts, DRS signaling, current negotiated speed/width, link training, slot clock, data-link active, and bandwidth status bits. The PCIe capability v2 registers add completion timeout, ARI forwarding, atomic operation, ID-based ordering, LTR, TPH completer, 10-bit tags, OBFF, end-to-end TLP prefix, emergency power reduction, FRS, supported link speeds, equalization/compliance/de-emphasis, crosslink, RTM presence, and DRS message/status fields.

The MSI and MSI-X capability fields in VF22-VF24 define capability IDs/next pointers and interrupt-programming fields. MSI macros include enable, multiple-message capable/enable, 64-bit capable, per-vector masking capable, address low/high, data, mask, 64-bit data/mask, pending, and 64-bit pending fields. MSI-X macros define table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

The vendor-specific and AER capability sections expose extended capability list metadata and error reporting fields. `PCIE_VENDOR_SPECIFIC_*` describes the vendor-specific enhanced capability header and two payload words. `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` identifies the AER extended capability. `PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY` define the standard uncorrectable error classes, including data-link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multi-cast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header log overflow. `PCIE_ADV_ERR_CAP_CNTL` covers first-error pointer, ECRC generation/check capability and enable bits, multi-header received capability/enablement, TLP prefix log presence, and completion timeout log capability.

The AER log macros define four 32-bit TLP header log words and four 32-bit TLP prefix log words for each complete VF block. These fields are diagnostic capture surfaces rather than normal configuration values.

The ATS and ARI sections at the end of each complete VF22-VF24 block repeat enhanced capability list metadata, ATS capability/control, and ARI capability/control. ATS fields describe invalidate queue depth, page-aligned request support, global invalidate support, small translation unit, and ATC enable. ARI fields describe MFVC/ACS function group capability, next function number, corresponding enables, and function group selection.

The VF25 section begins another instance of the same per-VF template. In this chunk, VF25 includes the conventional PCI header, PCIe capability, device/link capability/control/status, `DEVICE_CAP2`, and the first `DEVICE_CNTL2` field definitions through `ATOMICOP_EGRESS_BLOCKING__SHIFT`. The remaining `DEVICE_CNTL2` fields and later VF25 registers are outside this chunk.

## Control Flow

There is no control flow in the header itself. A typical runtime path using these constants is:

1. Driver code chooses the generated offset for a PCI config register from `nbio_2_3_offset.h`.
2. It reads or prepares a 16-bit or 32-bit register value through an AMDGPU PCIe/NBIO access helper.
3. It applies these `__SHIFT` and `_MASK` constants directly or via helper macros to extract, set, clear, or preserve individual fields.
4. It writes the value back, polls status, clears sticky error bits, or records hardware-updated diagnostic fields depending on the register's hardware semantics.

Flows that may use these fields include SR-IOV virtual-function config-space exposure, PCI command/status programming, BAR/resource setup, PCIe link/device capability negotiation, function-level reset, MSI/MSI-X interrupt setup, AER status collection and masking, ATS/PASID/IOMMU-related setup, ARI enumeration, and virtualization feature validation. This chunk only supplies bit layouts; ordering, locking, privilege checks, and hardware sequencing live in AMDGPU/NBIO, PCI, IOMMU, SR-IOV, reset, and interrupt code.

## State And Persistence Behavior

This file has no software state and persists nothing. The macros describe externally visible hardware state in PCI configuration space for SR-IOV-style virtual functions under `BIF_CFG_DEV0_EPF0`.

The represented state includes static identity and capability fields, driver-programmed control bits, host PCI configuration state, hardware-updated link and device status, interrupt address/data/mask/pending registers, AER sticky status and severity/mask configuration, captured AER TLP headers/prefixes, ATS translation-control state, and ARI function-routing state. Some fields are read-only capabilities, some are read/write controls, some are write-one-to-clear error status, and some are command bits with side effects such as FLR initiation or link retraining. The generated macro names and masks do not encode those side-effect rules.

No state survives because of this header. Persistence depends on the GPU's PCI config registers, reset domains, firmware initialization, host PCI core save/restore, and AMDGPU suspend/resume or SR-IOV reset paths. Any driver path using these macros must still follow hardware documentation for reset, sticky status clearing, interrupt masking, and capability programming.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus the AMD generated register database that produced `nbio_2_3_sh_mask.h`. The constants must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which maps the same register names to PCI config-space offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which maps the same register names to default values.
- AMDGPU NBIO, PCIe, SR-IOV, interrupt, reset, and power-management code that includes generated NBIO 2.3 headers.

The closest integration pattern in this tree is AMDGPU code such as `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, which includes generated NBIO default, offset, and shift/mask headers and then reads/writes NBIO and PCIe registers through AMDGPU helper macros. Virtualization-related consumers may also include these definitions through MXGPU/SR-IOV code paths. The field families in this chunk integrate with PCI enumeration, virtual-function config-space emulation/exposure, BAR sizing, MSI/MSI-X delivery, AER reporting, IOMMU/ATS translation behavior, ARI routing, link capability negotiation, and function-level reset behavior.

## Risks And Edge Cases

- The range has artificial chunk boundaries. It begins after the first VF21 ATS capability fields and ends before most of VF25 `DEVICE_CNTL2`; adjacent chunks are needed before making complete-register claims for those registers.
- The constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while changing the wrong hardware bit.
- VF22, VF23, and VF24 are mechanically repeated. A single generation skew in one VF block could create subtle per-VF behavior differences that normal single-VF smoke tests may miss.
- PCI command bits such as memory access and bus mastering are security and DMA sensitive. Incorrect masks can leave a VF unable to DMA or able to access resources unexpectedly.
- FLR, link retrain, link disable, ASPM/clock power management, completion timeout, max payload, max read request, relaxed ordering, and no-snoop fields affect PCIe ordering and liveness. Misprogramming can produce hangs, failed resets, data corruption, or poor interoperability with root complexes.
- MSI/MSI-X fields have direct interrupt-delivery side effects. Width, address, mask, pending, or enable mistakes can cause lost, repeated, or misrouted interrupts.
- AER status and log fields are often sticky or clear-on-write. Treating them like ordinary read/write configuration can erase diagnostic evidence or fail to clear real errors.
- ATS and ARI fields affect IOMMU translation, address caching, and function routing. Incorrect capability or enable handling can break isolation, translation invalidation, or VF enumeration.
- VF25 is incomplete in this chunk; tools that compare repeated VF templates must account for the truncated end rather than reporting a false structural mismatch.

## Test Signals

Useful validation is mostly generated-header, kernel-build, and hardware-integration oriented:

- Build AMDGPU code that includes NBIO 2.3 generated headers; missing, duplicate, or renamed macros should surface as compile errors.
- Compare VF22, VF23, and VF24 field sets after replacing the VF number with a placeholder. They should be structurally identical unless the hardware database intentionally differentiates a VF.
- Compare this shift/mask header against `nbio_2_3_offset.h` and `nbio_2_3_default.h` for matching register-name coverage and expected chunk boundary exceptions.
- Boot affected AMDGPU/NBIO 2.3 hardware and verify PCI config-space enumeration for VF22-VF24: vendor/device IDs, BARs, capability pointers, PCIe capability, MSI/MSI-X, AER, ATS, and ARI capability chains.
- Exercise SR-IOV or multi-function setups with multiple VFs enabled; confirm VF22-VF24 expose consistent capabilities and that VF25 behavior is validated using the following chunk as well.
- Exercise FLR, link retraining, suspend/resume, and PCI error recovery; failures in reset completion, link training, AER logging, or completion timeout paths are strong signals of field-layout drift.
- Exercise MSI/MSI-X interrupt delivery and masking under graphics, compute, reset, and error-injection workloads.
- In IOMMU/ATS-capable configurations, validate translation invalidation and ATC enable/disable paths; stale translations or isolation failures point to ATS field or sequencing problems.
