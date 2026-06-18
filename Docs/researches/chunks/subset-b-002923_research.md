# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 46354-48777

## Scope

This chunk is a generated AMD NBIO 2.3 register field shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, allocation, locking, or executable control flow.

The range starts inside `BIF_CFG_DEV0_EPF0_VF25_DEVICE_CNTL2`, after several shift definitions for that register already appeared in the previous chunk. It then finishes the VF25 PCIe capability tail, covers complete PCI configuration-space layouts for virtual functions VF26 and VF27, and covers VF28 from the standard PCI header through `BIF_CFG_DEV0_EPF0_VF28_PCIE_TLP_PREFIX_LOG2`. The chunk ends before the mask for VF28 TLP prefix log 2 and before VF28 TLP prefix log 3, ATS, and ARI fields; those are in the following chunk.

Although the repository prefix is `sources/distributed-fs/ceph-client`, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header section is to publish the bitfield ABI for NBIO 2.3 PCIe virtual-function configuration images. Each register field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when encoding or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

The companion address metadata is in `nbio_2_3_offset.h`, where this same virtual-function range maps to config offsets such as `cfgBIF_CFG_DEV0_EPF0_VF25_0_DEVICE_CNTL2`, `cfgBIF_CFG_DEV0_EPF0_VF26_0_VENDOR_ID`, `cfgBIF_CFG_DEV0_EPF0_VF27_0_PCIE_UNCORR_ERR_STATUS`, and `cfgBIF_CFG_DEV0_EPF0_VF28_0_PCIE_TLP_PREFIX_LOG2`. Runtime code combines offset symbols with these field masks through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The VF25 portion completes the second-generation PCIe device/link capability tail. It includes `DEVICE_CNTL2` control bits for completion timeout, ARI forwarding, atomic operation requests, ID-based ordering, LTR, emergency power reduction, 10-bit tags, OBFF, and TLP-prefix blocking. It then defines VF25 status/control fields for `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, covering supported/target link speed, crosslink and SKP ordered-set support, equalization phases, retimer presence, compliance controls, downstream component presence, and DRS message state.

VF25 also includes MSI and MSI-X capability fields: capability IDs, next pointers, MSI enable/multiple-message/64-bit/per-vector masking state, MSI address/data/mask/pending registers, MSI-X table size, function mask, enable bit, table BIR/offset, and PBA BIR/offset. The vendor-specific enhanced capability follows with VSEC capability ID/version/next pointer, VSEC ID/revision/length, and two scratch payload registers.

The VF25 AER section defines advanced error reporting capability header fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control bits, four TLP header log registers, and TLP prefix logs. Error fields include data-link protocol, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, AtomicOp egress blocked, and TLP-prefix blocked state. Correctable fields include receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, correctable internal, and header-log overflow state. VF25 ends with ATS and ARI enhanced capabilities, including ATS page-size granularity/enable fields and ARI next-function/function-group controls.

The VF26 and VF27 blocks are complete and mechanically parallel. Each begins with standard PCI configuration header fields: vendor/device ID, command, status, revision/class-code bytes, cache-line/latency/header/BIST fields, BAR1 through BAR6, CardBus CIS pointer, adapter ID/subsystem IDs, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. The command and status masks cover I/O, memory, bus master, special cycles, memory-write-invalidate, VGA snoop, parity/error response, SERR, fast back-to-back, interrupt disable, capability-list presence, 66 MHz, user-definable feature, fast back-to-back, master abort/target abort, parity, and detected parity state.

The complete VF26/VF27 PCIe capability groups include PCIe capability list/capability headers, device capability/control/status, link capability/control/status, device capability 2/control 2/status 2, and link capability 2/control 2/status 2. These describe payload size, phantom functions, extended tags, acceptable L0s/L1 latency, attention/power indicators, role-based error reporting, FLR, max payload/read request, relaxed ordering, no-snoop, auxiliary power, unsupported request, link speed/width, ASPM, RCB, common clock, extended sync, link disable/retrain, clock power management, link bandwidth notification, completion timeout ranges, atomic operations, OBFF, LTR, 10-bit tags, equalization phases, compliance controls, retimer presence, crosslink state, and DRS status.

The complete VF26/VF27 interrupt, vendor, AER, ATS, and ARI groups mirror the VF25 tail. They define MSI/MSI-X capability registers, vendor-specific enhanced capability header/payload fields, AER status/mask/severity/control/log fields, ATS enhanced capability/capability/control fields, and ARI enhanced capability/capability/control fields.

The VF28 block is complete from `VENDOR_ID` through the start of AER TLP-prefix logging. It carries the same standard PCI header, PCIe capability, MSI/MSI-X, vendor-specific, and AER register families as VF26/VF27, but this chunk stops immediately after `BIF_CFG_DEV0_EPF0_VF28_PCIE_TLP_PREFIX_LOG2__TLP_PREFIX__SHIFT`. The rest of VF28 TLP prefix logging and the VF28 ATS/ARI tail are outside this chunk.

## Control Flow

There is no runtime control flow in this header. Runtime sequencing is supplied by AMDGPU NBIO, PCIe, SR-IOV, interrupt, reset, and power-management code that includes it:

1. Driver code selects a register offset from `nbio_2_3_offset.h` or an SMN/MMIO constant.
2. It reads or constructs a 16-bit or 32-bit PCI config-space value with PCIe or SOC15 access helpers.
3. It uses these `__SHIFT` and `_MASK` constants directly or through helper macros to update or decode a field.
4. It writes the value back, polls status, clears sticky status, reports capability state, or lets hardware/firmware update status-owned fields.

For this chunk, common runtime flows include SR-IOV virtual function config image exposure, PCIe capability enumeration, VF interrupt capability setup, AER status collection and clearing, link control/status reporting, function reset coordination, ATS/ARI virtualization setup, and guest-visible capability/status emulation or passthrough.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes GPU-owned PCI configuration and enhanced-capability state for virtual functions.

The represented state includes PCI command/status bits, identity/class/header fields, BAR and ROM aperture fields, capability pointers, PCIe device/link capability and control bits, MSI/MSI-X programming state, vendor-specific VSEC payload scratch registers, AER status/mask/severity and logs, ATS translation controls, and ARI next-function/function-group controls. Some fields are static capability descriptions, some are host or guest programmed controls, some are hardware-updated status, and some are sticky error/log fields with clear-on-write behavior. The generated constants do not encode those side effects; consumers must follow PCIe and ASIC-specific semantics.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database and must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`. The offset header provides the config-space addresses for VF25 through VF28, while this file provides the bit layouts for values stored at those addresses.

Direct AMDGPU include users of `nbio_2_3_sh_mask.h` include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c`, and `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c`. Those files rely on generated masks for NBIO programming, SR-IOV/MXGPU behavior, and power-management interactions rather than duplicating bit positions.

The virtual-function PCI config macros integrate with Linux PCI enumeration, SR-IOV VF creation and teardown, guest passthrough or mediated access paths, function-level reset, interrupt delivery, AER error handling, PCIe link management, ATS address-translation services, and ARI routing/function-number expansion. The standardized field names also make this ASIC revision comparable with other generated AMD register headers.

## Risks And Edge Cases

- The chunk boundaries are artificial. The first line is mid-`DEVICE_CNTL2` for VF25, and the last line is mid-`PCIE_TLP_PREFIX_LOG2` for VF28. Adjacent chunks are needed for complete whole-register analysis at those boundaries.
- These macros are untyped integer constants. Wrong masks or shifts can compile cleanly while targeting the wrong hardware bit.
- VF26 and VF27 are highly repetitive, and VF28 largely repeats them. Copy-generation drift can produce off-by-one VF naming, wrong register prefixes, or mismatched offset/mask pairs that are difficult to notice in review.
- PCIe command, BAR, bus mastering, memory enable, interrupt disable, and ROM base fields are enumeration-sensitive. Bad field definitions can break VF discovery, resource assignment, DMA enablement, or interrupt routing.
- PCIe link, payload, read-request, ordering, no-snoop, completion timeout, atomic operation, LTR, OBFF, and TLP-prefix controls affect host/device interoperability. Incorrect values can cause link instability, ordering violations, timeouts, or performance regressions.
- MSI/MSI-X address, data, mask, pending, table, and PBA fields have interrupt-delivery side effects. Width, alignment, or aliasing mistakes can cause lost, misrouted, masked, or unexpectedly unmasked interrupts.
- AER status and log fields may be sticky or write-one-to-clear. Treating them like ordinary retained configuration can erase diagnostic evidence or leave error state uncleared.
- ATS and ARI controls affect address translation and VF routing/isolation. Wrong masks can expose invalid translation enablement, stale ATC state, or incorrect function-group behavior in SR-IOV environments.
- Some fields represent guest-visible PCI config state. In SR-IOV or virtualization, incorrect exposure can create compatibility failures that are only visible with VFs enabled and guest drivers loaded.

## Test Signals

Useful validation is mostly build, boot, PCIe, and hardware-integration oriented:

- Build AMDGPU with NBIO 2.3 support enabled; missing or renamed macros should fail in NBIO, MXGPU, SMU, PCIe, or interrupt code.
- Boot affected ASICs and confirm Linux PCI enumeration shows stable VF vendor/device IDs, class codes, BARs, capability pointers, PCIe capabilities, MSI/MSI-X capabilities, vendor-specific capability, AER capability, ATS capability, and ARI capability.
- Enable SR-IOV with enough VFs to cover VF25 through VF28; inspect `lspci -vv` output for those VFs and compare capability offsets and decoded fields against expected hardware documentation.
- Exercise VF MSI and MSI-X interrupt delivery under graphics, compute, reset, and guest passthrough workloads; lost interrupts or stuck pending/mask state indicate mask/offset problems.
- Trigger or inject PCIe/AER paths where available and verify uncorrectable/correctable status, severity, masks, header logs, and TLP prefix logs are reported and cleared correctly.
- Test VF FLR, suspend/resume, runtime reset, link retraining, and error recovery paths; hangs, failed enumeration, or unexpected link-speed/width changes can reveal incorrect PCIe control/status fields.
- In virtualization runs, validate ATS/ARI behavior and isolation with guest drivers loaded, including DMA translation, function routing, and teardown/recreate cycles for high-numbered VFs.
