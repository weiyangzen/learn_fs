# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 34345-36778

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 2,133 `#define` entries across 2,434 source lines: 1,069 `__SHIFT` constants and 1,064 `_MASK` constants. There are no functions, structs, enums, global variables, locks, allocations, branches, loops, or direct register accesses in this range.

The slice starts in the tail of `BIF_CFG_DEV0_EPF0_VF11_1`, beginning at Advanced Error Reporting uncorrectable-error status fields. It then covers complete repeated PCIe virtual-function configuration-space layouts for `BIF_CFG_DEV0_EPF0_VF12_1`, `VF13_1`, and `VF14_1`. It begins `BIF_CFG_DEV0_EPF0_VF15_1` and stops inside `VF15_1_DEVICE_CAP2`, after `MAX_END_END_TLP_PREFIXES_MASK`; the remaining VF15 control/status, MSI/MSI-X, vendor-specific, AER, ATS, and ARI fields continue after this chunk.

The `// addressBlock:` comments identify generated address blocks for `nbio_nbif_bif_cfg_dev0_epf0_vf12_bifcfgdecp`, `vf13_bifcfgdecp`, `vf14_bifcfgdecp`, and `vf15_bifcfgdecp`. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem logic.

## Purpose

`nbio_6_1_sh_mask.h` publishes bit positions for NBIO 6.1 registers and PCI configuration-space words. For each field, the generator emits:

- `<REGISTER>__<FIELD>__SHIFT`, the bit index used when packing or extracting a value.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update that field.

Runtime AMDGPU code pairs these constants with the matching register/config offsets from `nbio_6_1_offset.h` and, where useful, reset values from `nbio_6_1_default.h`. Callers typically consume the constants through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

This chunk specifically describes SR-IOV virtual-function PCIe config-space field layouts for late VF11, all of VF12 through VF14, and early VF15. The fields cover standard PCI identity/resource registers, PCIe base capability state, MSI/MSI-X interrupt state, vendor-specific enhanced capability words, Advanced Error Reporting, Address Translation Services, and Alternative Routing-ID Interpretation.

## Important Macro Families

The opening VF11 fragment covers the latter part of a VF PCIe extended capability chain:

- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` expose AER uncorrectable conditions and policy bits for data-link protocol errors, surprise down, poisoned TLPs, flow-control protocol errors, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC error, unsupported request, ACS violation, internal error, multicast-blocked TLP, atomic-op egress blocking, and TLP-prefix blocking.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal error, internal correctable error, and header-log overflow bits.
- `PCIE_ADV_ERR_CAP_CNTL` defines first-error pointer, ECRC generation/check capability and enable bits, multi-header recording capability/enable, and TLP-prefix-log presence.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3` provide full-dword masks for captured TLP header and prefix log data.
- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, `PCIE_ATS_CNTL`, `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` complete VF11 ATS and ARI capability/control metadata.

The complete VF12, VF13, and VF14 blocks repeat the same Type 0 VF config-space structure:

- Standard PCI header fields include vendor/device ID, command, status, revision, programming interface, subclass, base class, cache-line size, latency, header type/device type, BIST, BAR1 through BAR6, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line, and interrupt pin.
- `COMMAND` and `STATUS` fields describe I/O access, memory access, bus mastering, special cycles, memory-write-invalidate, VGA palette snoop, parity response, IDSEL stepping, SERR, fast back-to-back, interrupt disable, interrupt status, capability-list presence, immediate readiness, DEVSEL timing, target/master aborts, system error, and parity error reporting.
- PCIe base capability fields include capability-list linkage, PCIe version/device type, slot implementation, interrupt message number, device capability/control/status, link capability/control/status, device capability/control/status 2, link capability/control/status 2, and empty slot capability/control/status 2 words.
- Device and link control fields include error-reporting enables, relaxed ordering, max payload, extended tags, phantom functions, auxiliary-power PM, no-snoop, max read request size, FLR initiation, ASPM/power-management controls, link disable/retrain, common clock, extended sync, clock power management, autonomous width/speed disables, bandwidth-management interrupts, target link speed, compliance controls, selectable de-emphasis, transmit margin, completion-timeout controls, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, and end-to-end TLP prefix blocking.
- MSI/MSI-X fields include capability-list pointers, MSI enable/multiple-message/64-bit/per-vector mask controls, MSI address/data registers, mask and pending bits, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific enhanced capability fields provide capability ID/version/next pointer values, VSEC ID/revision/length, and two scratch payload dwords.
- AER fields mirror the VF11 fragment for each complete VF: uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, four header-log dwords, four TLP-prefix-log dwords, plus capability-list metadata.
- ATS fields cover enhanced capability metadata, invalidate queue depth, page-aligned request support, global invalidate support, STU, and ATC enable.
- ARI fields cover enhanced capability metadata, MFVC and ACS function-group capabilities, next-function number, MFVC/ACS function-group enables, and selected ARI function group.

The VF15 fragment starts the same repeated VF image and includes identity/header, BAR, PCIe capability, device/link capability/control/status, and `DEVICE_CAP2` capability bits through completion-timeout range support, timeout-disable support, ARI forwarding, atomic completion support, CAS128 completion support, no-RO-enabled P2P passing, LTR, TPH completer support, OBFF support, extended format support, end-to-end TLP prefix support, and maximum end-to-end TLP prefixes.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace itself. Consumers rely on exact spelling and exact numeric values for the `BIF_CFG_DEV0_EPF0_VF*_1_*` register-field constants.

The constants are untyped C preprocessor integer literals, usually with an `L` suffix on masks. They encode bit layout only. They do not encode register width, reset value, access permissions, W1C behavior, sticky status behavior, polling requirements, side effects, locking requirements, PF/VF ownership, or ordering constraints. Those semantics must come from the hardware specification, companion generated files, and the AMDGPU code using the fields.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU, MXGPU/SR-IOV, PCIe, power-management, reset, or diagnostics code selects a VF config-space register offset from `nbio_6_1_offset.h`.
2. The code reads or composes a 16-bit or 32-bit value through AMDGPU's PCIe or SOC15 register access layer.
3. It applies the `__SHIFT` and `_MASK` macros directly or through field helpers.
4. The decoded value drives policy or diagnostics, or the composed value is written back to hardware.

Typical flows using these fields include VF PCI enumeration, VF BAR/resource exposure, memory access and bus-mastering control, MSI/MSI-X programming, PCIe link policy, completion-timeout and FLR handling, AER collection/masking/clearing, ATS enablement, ARI routing, and PF/hypervisor inspection of VF config state.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state in NBIO virtual-function images. Persistence and reset behavior are determined by GPU reset domains, PCI config reset, function-level reset, SR-IOV PF/VF lifecycle, platform firmware, suspend/resume save-restore, and explicit driver or hypervisor writes.

Represented state includes static identity and capability data, host-programmed command bits, BAR and ROM address windows, capability-list pointers, device/link controls, link/device status, MSI/MSI-X message and mask state, AER status/mask/severity/log data, vendor-specific scratch fields, ATS control state, and ARI function-group/routing state. Some fields are read-only capability descriptions, some are software-owned controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics.

Important side-effect fields include `MEM_ACCESS_EN` and `BUS_MASTER_EN`, which gate MMIO decode and DMA; `INITIATE_FLR`, which requests function-level reset; link retrain/disable and target-speed controls; MSI/MSI-X enable and mask bits; AER status/log bits; ATS `ATC_ENABLE`; and ARI function-group enables. The generated masks only identify bit positions, so call sites must supply the correct ownership, ordering, and reset handling.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 6.1 register database. This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h`, which supplies matching config-space offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h`, which supplies generated reset/default values for the same VF register families.
- AMDGPU register helper and access macros, including `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

In-tree include users for the NBIO 6.1 generated headers include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, `drivers/gpu/drm/amd/amdgpu/psp_v3_1.c`, display resource code that includes NBIO offsets, and Vega power-management include bundles such as `vega10_inc.h` and `vega12_inc.h`. The most relevant integration surfaces for this chunk are NBIO/BIF setup, MXGPU/SR-IOV VF management, PCIe config-space access, VF interrupt delivery, AER diagnostics, ATS/ARI virtualization behavior, reset/FLR flows, and suspend/resume or runtime power transitions.

## Risks And Edge Cases

- Chunk boundaries are artificial. The slice starts after earlier VF11 header/MSI/vendor fields and stops before most VF15 fields; adjacent chunks are required for whole-VF11 and whole-VF15 conclusions.
- Generated shift/mask drift can compile cleanly while causing software to read, preserve, clear, or set the wrong hardware bit.
- The VF12 through VF14 blocks are mechanically repetitive. Suffix mistakes can silently target the wrong virtual function and break SR-IOV isolation or diagnostics.
- Applying a valid field mask to the wrong offset can still produce plausible values while corrupting unrelated VF config state.
- PCI command and BAR fields affect MMIO decode, resource sizing, and DMA enablement. Incorrect masks can expose invalid apertures, prevent enumeration, or enable bus mastering at the wrong time.
- MSI/MSI-X fields affect interrupt delivery. Width, address/data, table/PBA offset, function mask, or pending-bit mistakes can cause lost, repeated, or misrouted interrupts.
- AER status, severity, mask, header-log, and TLP-prefix-log fields can be sticky, write-one-to-clear, or hardware-owned. Treating them as ordinary read/write state can lose diagnostic evidence or fail to clear a fault.
- FLR, completion-timeout, relaxed-ordering, no-snoop, LTR, OBFF, link-control, and atomic-operation fields are PCIe interoperability-sensitive and may expose platform-specific failures.
- ATS and ARI fields are virtualization and address-routing sensitive. Incorrect ATC enable/STU, invalidate capability, next-function number, or function-group interpretation can affect IOMMU behavior, VF enumeration, and function isolation.
- VF15 is incomplete in this chunk. Its `DEVICE_CAP2` bits are present, but the corresponding `DEVICE_CNTL2`, link status 2, MSI/MSI-X, AER, ATS, and ARI fields must be read from the next chunk before making complete VF15 claims.

## Test Signals

- Build AMDGPU with NBIO 6.1 support enabled. Missing, renamed, or duplicated macros should surface through `nbio_v6_1.c`, `mxgpu_ai.c`, Vega power-management include paths, or other NBIO 6.1 users.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset-to-field pairing, shift/mask width checks, non-overlap checks within registers, repeated-VF layout checks, and default-value alignment against `nbio_6_1_default.h`.
- On affected hardware, verify stable VF PCI enumeration, vendor/device/class fields, capability-list traversal, BAR sizing, command-bit transitions, and VF resource visibility.
- In SR-IOV or MXGPU configurations, create and remove VFs across the VF11-VF15 range, bind guest drivers, exercise VF FLR, and confirm isolation, config-space access, ATS/ARI behavior, and reset recovery.
- Exercise MSI and MSI-X interrupt delivery with masking/unmasking and pending-bit observation; lost interrupts or unexpected vector routing can indicate layout or offset drift.
- Use PCIe/AER diagnostics or error injection where available to validate uncorrectable/correctable status, masks, severities, ECRC controls, header logs, and TLP-prefix logs.
- Test suspend/resume, runtime power transitions, link retraining, and completion-timeout behavior while monitoring link speed/width/status and absence of unexpected AER storms.
- For ATS-capable and ARI-capable configurations, validate IOMMU/ATS enablement, invalidation behavior, function routing, and guest-visible VF enumeration.

## Chunk Notes

- Lines 34345-34517 are only the VF11 AER/ATS/ARI tail.
- Lines 34519-36581 are complete `BIF_CFG_DEV0_EPF0_VF12_1`, `VF13_1`, and `VF14_1` PCIe VF config-space shift/mask blocks.
- Lines 36583-36778 begin `BIF_CFG_DEV0_EPF0_VF15_1` and end inside `BIF_CFG_DEV0_EPF0_VF15_1_DEVICE_CAP2`; later VF15 fields are outside this work item.
