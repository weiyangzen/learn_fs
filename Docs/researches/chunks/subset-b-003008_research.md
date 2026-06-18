# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 7315-9751

## Scope

This chunk is a generated AMD NBIO 6.1 register shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, allocations, locks, reference counts, or direct register accesses in this range.

The assigned range starts inside `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`, after the preceding VF1 uncorrectable-error status block has already begun. It then finishes the VF1 advanced error reporting tail and ATS/ARI extended-capability fields, covers complete `BIF_CFG_DEV0_EPF0_VF2_0`, `VF3_0`, and `VF4_0` virtual-function PCI configuration layouts, and ends partway through `BIF_CFG_DEV0_EPF0_VF5_0_DEVICE_CNTL2`. The next lines after this chunk continue VF5 with Device Status 2, Link Capability 2, Link Control 2, AER, ATS, and ARI fields.

Although this file is located under a local `ceph-client` source mirror, this path is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions and masks for NBIO 6.1 PCIe configuration-space fields for SR-IOV/MxGPU virtual functions on device 0, endpoint function 0. Each field is represented by a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for extracting or composing the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for isolating, preserving, clearing, or setting the field.

Consumers combine these constants with register addresses from `nbio_6_1_offset.h` and reset/default values from `nbio_6_1_default.h`. Runtime code normally reaches them through AMDGPU register helpers and field helpers such as `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`, depending on the register aperture and call site.

## Important Macro Families

The opening VF1 tail covers the mask/severity/status portions of PCIe Advanced Error Reporting. The `PCIE_UNCORR_ERR_MASK` and `PCIE_UNCORR_ERR_SEVERITY` fields describe DLP, surprise-down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast-blocked TLP, atomic-op egress blocked, and TLP-prefix blocked conditions. The `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` fields cover receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal error, correctable internal error, and header-log overflow.

The VF1 AER tail also includes `PCIE_ADV_ERR_CAP_CNTL`, four TLP header log dwords, and four TLP prefix log dwords. These define first-error pointer, ECRC generation/check capabilities and enables, multi-header recording support, and full-width diagnostic log payload masks. The VF1 part then defines ATS and ARI enhanced-capability headers, ATS capability/control fields, and ARI capability/control fields.

The `addressBlock: nbio_nbif_bif_cfg_dev0_epf0_vf2_bifcfgdecp` section begins a complete virtual-function PCI configuration image for VF2. VF2 includes identity and header fields: vendor ID, device ID, command, status, revision ID, class code bytes, cache-line size, latency timer, header type, BIST, six BAR registers, adapter ID, ROM base address, capability pointer, interrupt line, and interrupt pin.

The VF2 PCIe capability fields define capability-list linkage, PCIe capability version/type/message number, Device Capability, Device Control, Device Status, Link Capability, Link Control, and Link Status. Important programmable or status-bearing fields include I/O and memory enables, bus mastering, special cycles, interrupt disable, payload and read request size, relaxed ordering, no-snoop, extended tags, phantom functions, FLR initiation/capability, link speed and width, ASPM/power-management policy, retrain/link-disable, common clock, extended sync, autonomous width disable, bandwidth interrupt enables, current negotiated speed/width, link training, slot clock configuration, and data-link active state.

The VF2 PCIe Capability 2 family covers completion timeout, ARI forwarding, atomic operation routing/completion support, ID-based ordering, LTR, TPH completer support, OBFF, extended format, end-to-end TLP prefixes, supported link speeds, crosslink support, target link speed, compliance entry, selectable de-emphasis, transmit margin, enter-modified-compliance, compliance SOS, 8 GT/s equalization control/status, current de-emphasis, and autonomous bandwidth status. Slot Capability/Control/Status 2 are present as reserved full-width fields for this VF layout.

The VF2 interrupt capability section includes MSI and MSI-X capability-list headers, MSI message control, low/high message address, message data, mask and pending registers for both 32-bit and 64-bit forms, MSI-X table descriptor, and MSI-X PBA descriptor. These masks define the configuration-space view used by software to program virtual-function interrupt delivery.

The VF2 vendor-specific and AER sections include a vendor-specific enhanced-capability header, vendor-specific header and two full 32-bit payload dwords, AER enhanced-capability header, uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, and TLP prefix logs. This mirrors the VF1 AER tail but is complete for VF2 in this chunk.

The VF2 ATS and ARI enhanced-capability sections expose capability IDs, versions, next pointers, ATS invalidate queue depth/page-aligned/global-invalidate support, ATS STU and ATC enable control, ARI MFVC/ACS function group capability bits, next function number, function-group enables, and function-group selector.

The VF3 and VF4 sections repeat the same generated PCI configuration layout as VF2 under `BIF_CFG_DEV0_EPF0_VF3_0_*` and `BIF_CFG_DEV0_EPF0_VF4_0_*`. The repetition is significant: each virtual function gets distinct macro names even though most field positions and masks are identical. Consumers must use the macro family matching the target virtual function's offset block.

The VF5 section begins another copy of the same virtual-function layout. This chunk includes VF5 identity/header fields, BARs, capability pointer and interrupt-line/pin fields, PCIe capability header, Device Capability/Control/Status, Link Capability/Control/Status, Device Capability 2, and Device Control 2. The range ends at `BIF_CFG_DEV0_EPF0_VF5_0_DEVICE_CNTL2__END_END_TLP_PREFIX_BLOCKING_MASK`; VF5 Device Status 2 and later capability fields are outside this work item.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is a macro namespace consumed by AMDGPU source files that include `nbio/nbio_6_1_sh_mask.h` or `asic_reg/nbio/nbio_6_1_sh_mask.h`.

Direct include sites for the NBIO 6.1 shift/mask header include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and PowerPlay include aggregators such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. Related NBIO 6.1 offset headers are also included by PSP and display resource code. These include sites do not imply that every macro in this chunk is referenced directly; generated hardware headers intentionally expose a larger register database than any one driver path uses.

## Control Flow

There is no executable control flow in this header. Runtime behavior happens in including code:

1. Driver code selects an NBIO 6.1 register offset from `nbio_6_1_offset.h`.
2. It reads a hardware or configuration register through the AMDGPU register access layer.
3. It extracts a field with the relevant `__SHIFT` and `_MASK` macro, often through a helper macro.
4. It composes and writes a new control value, decodes status for diagnostics, clears sticky error bits, or compares hardware state against policy/default expectations.

For this range, likely runtime contexts are SR-IOV virtual-function setup, MxGPU virtualization behavior, PCIe capability exposure, virtual-function interrupt programming, PCIe link capability/status handling, FLR/reset behavior, AER diagnostics, ATS/ARI capability policy, and power-management interactions that depend on PCIe link state.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes bit layout for hardware-backed and configuration-space-backed state owned by NBIO, the GPU virtualization stack, platform firmware, Linux PCI core policy, the host PCIe fabric, and AMDGPU runtime code.

The represented state includes PCI identity/header registers, command/status bits, BAR aperture descriptors, ROM and adapter ID fields, capability-list topology, PCIe device/link capability and control state, MSI/MSI-X programming state, vendor-specific capability payloads, AER status/mask/severity/log state, ATS enablement and translation unit parameters, ARI capability and function-group control, and VF-specific link/device status. Some fields are static capabilities, some are software-programmed controls, some are hardware-updated status, and some AER fields may be sticky or write-one-to-clear in the underlying hardware. The masks do not encode reset defaults, ownership rules, read/write permissions, side effects, timing, or ordering requirements.

The paired `nbio_6_1_default.h` contains reset/default values for the same VF register families, including nonzero defaults for interrupt line, PCIe capability-list pointers, PCIe capability version, Device Capability, Device Control, Link Capability, Link Status, Link Capability 2, Link Control 2, MSI message control, vendor-specific and AER enhanced capability headers, AER severity/mask defaults, ATS and ARI enhanced-capability headers, and zeroed BAR/message/log payloads. This chunk's masks must remain aligned with those defaults and the matching offset declarations.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` provides matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides reset/default values for the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` provides related NBIO SMN address definitions.
- AMDGPU register and field helper macros provide read/modify/write and field extraction mechanics.

Integration points include `nbio_v6_1.c` NBIO setup and query logic, `mxgpu_ai.c` virtualization paths, Vega10/Vega12 PowerPlay code that includes NBIO register definitions, PSP code that uses NBIO offsets for firmware/security flows, and display resource code that references NBIO offset state. Broader integration is with Linux PCI enumeration, SR-IOV virtual-function exposure, MSI/MSI-X interrupt routing, PCIe Advanced Error Reporting, PCIe link training and power policy, ATS/IOMMU behavior, ARI function numbering, and reset/FLR paths.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line is already inside VF1 `PCIE_UNCORR_ERR_MASK`, and the last line stops before VF5 `DEVICE_STATUS2`; a reader must merge adjacent chunks for a complete per-file view.
- The macros are untyped preprocessor constants. A wrong mask, stale shift, or VF-number mismatch can compile cleanly while manipulating the wrong hardware field.
- VF2, VF3, VF4, and VF5 use highly repetitive generated names. Copy/generation drift can create subtle per-VF differences that are hard to catch by visual inspection.
- Register names must be paired with matching offsets from the same VF block. Applying a `VF4` mask to a `VF3` offset may produce plausible bit arithmetic while touching the wrong virtual function's configuration state.
- PCI command, Device Control, Device Control 2, Link Control, and Link Control 2 fields are interoperability-sensitive. Incorrect I/O, memory, bus-master, interrupt-disable, relaxed-ordering, no-snoop, payload, read-request, FLR, completion-timeout, ARI, atomic-op, IDO, LTR, OBFF, TLP-prefix, ASPM, retrain, link-disable, target-speed, de-emphasis, or equalization settings can break enumeration, DMA, ordering, reset, link stability, or power behavior.
- MSI and MSI-X fields have interrupt-delivery side effects. Incorrect address/data, mask, pending, table, PBA, 64-bit, or multiple-message fields can cause lost, stuck, or misrouted interrupts for a virtual function.
- BAR, ROM, and adapter ID masks affect resource exposure. Bad masks can confuse PCI resource sizing, virtual BAR emulation, or guest/host visibility in virtualized paths.
- AER status, mask, severity, first-error pointer, header log, and TLP prefix log fields may be sticky or clear-on-write in hardware. Naive read/modify/write can destroy diagnostic evidence or leave important errors masked.
- ATS and ARI fields cross driver, IOMMU, firmware, and PCIe fabric policy. Incorrect ATC enablement, STU programming, invalidation capability interpretation, ARI next-function number, or function-group controls can cause translation, isolation, or enumeration bugs.
- Capability-list and enhanced-capability `NEXT_PTR` fields define how configuration-space scanners discover capabilities. Incorrect masks or defaults can hide capabilities or send scanners through invalid capability chains.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware/virtualization integration testing:

- Build AMDGPU with NBIO 6.1, Vega10/Vega12, MxGPU, and SR-IOV relevant options enabled. Missing or renamed macros should surface in `nbio_v6_1.c`, `mxgpu_ai.c`, PowerPlay include users, or register helper call sites.
- Compare this chunk against `nbio_6_1_offset.h` and `nbio_6_1_default.h` to confirm VF1 through VF5 register names, ordering, defaults, and address-block transitions remain synchronized.
- On NBIO 6.1 hardware, enumerate SR-IOV virtual functions and verify VF2/VF3/VF4 PCI config space exposes expected identity, command/status, BAR, PCIe capability, MSI/MSI-X, vendor-specific, AER, ATS, and ARI capability fields.
- Exercise VF enable/disable and FLR/reset flows while monitoring Device Status, transactions-pending, Link Status, Link Status 2, AER status, and guest-visible PCI configuration state.
- Run MSI and MSI-X interrupt stress tests for multiple VFs to catch message-control, address/data, mask/pending, table, and PBA field regressions.
- Use AER injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severities, first-error pointer, header logs, and TLP prefix logs for each VF.
- Validate ATS/ARI behavior with IOMMU and SR-IOV enabled: translation enablement, invalidation support, function numbering, and capability-chain discovery should match platform policy.
- Exercise PCIe link policy changes, suspend/resume, runtime power transitions, and bandwidth notifications while checking link speed/width, training status, ASPM behavior, LTR/OBFF controls, and autonomous bandwidth status.

## Chunk Notes

- Lines 7315-7342 are the middle of VF1 uncorrectable-error mask definitions; the corresponding section comment and earlier fields are above this chunk.
- Lines 7343-7484 finish VF1 AER severity/correctable/logging plus ATS and ARI field definitions.
- Lines 7493-8143 cover a complete VF2 generated configuration-space map.
- Lines 8147-8797 cover a complete VF3 generated configuration-space map.
- Lines 8801-9451 cover a complete VF4 generated configuration-space map.
- Lines 9455-9751 cover the beginning of VF5 through `DEVICE_CNTL2`; the rest of VF5 is in the following chunk.
