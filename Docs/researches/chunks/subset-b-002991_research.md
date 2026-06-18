# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 74048-76466

## Scope

This chunk is a generated AMD NBIO 4.3.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, allocations, locks, branches, loops, or direct register accesses in this range.

The slice starts at the final mask for the `BIF_CFG_DEV0_EPF0_VF9_1_PCIE_VENDOR_SPECIFIC_HDR` register and then covers the tail of the VF9 PCIe extended capability block: vendor-specific scratch dwords, AER status/mask/severity/log fields, ARI capability/control fields, and Readiness Time Reporting fields. It then defines complete repeated PCIe configuration-space field layouts for `BIF_CFG_DEV0_EPF0_VF10_1`, `BIF_CFG_DEV0_EPF0_VF11_1`, and `BIF_CFG_DEV0_EPF0_VF12_1`. The range ends after the first seven `BIF_CFG_DEV0_EPF0_VF13_1_COMMAND` shift definitions, so VF13 is only a beginning fragment.

Although this path is under a local `ceph-client` source mirror, this file is AMDGPU hardware metadata rather than Ceph or distributed filesystem logic.

## Purpose

The purpose of this header range is to publish bitfield layouts for NBIO 4.3.0 SR-IOV virtual-function PCI configuration-space images. Each generated hardware field follows the usual AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for isolating, clearing, preserving, or updating that field.

The companion address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, supplies matching `cfgBIF_CFG_DEV0_EPF0_VF*_*` offsets. Runtime code combines those offsets with this shift/mask header through AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening VF9 fragment completes the end of a virtual-function extended capability chain. It includes `PCIE_VENDOR_SPECIFIC1/2` scratch dwords, `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, AER uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header-log dwords, four TLP prefix-log dwords, ARI enhanced capability/capability/control fields, and Readiness Time Reporting list/data fields.

The full VF10 through VF12 blocks repeat a standard SR-IOV VF PCI Type 0 configuration image. Each block starts with identity and header fields: vendor ID, device ID, command, status, revision ID, programming interface, subclass, base class, cache line, latency, header type/device type, BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem vendor/device adapter ID, ROM base address, capability pointer, interrupt line/pin, and min-grant/max-latency bytes.

The PCIe capability portions for VF10 through VF12 define `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`. Important fields include max payload support/size, max read request size, relaxed ordering, no-snoop, extended tag, function-level reset capability/initiation, completion timeout controls, ARI forwarding, atomic operation capability/enables, ID-based ordering, LTR, OBFF, 10-bit tag support, link speed/width, ASPM/power-management controls, link disable/retrain, common clock, autonomous bandwidth/speed disables, target link speed, de-emphasis, compliance controls, equalization status, and component presence status.

The MSI and MSI-X portions of VF10 through VF12 cover capability-list linkage, MSI enable/multiple-message/64-bit/per-vector masking controls, MSI message address/data/mask/pending fields, 64-bit MSI aliases, MSI-X table size/function mask/enable fields, MSI-X table BIR/offset, and PBA BIR/offset fields. These masks describe how interrupt capability state is packed in the VF config-space image.

The vendor-specific and AER portions define PCIe vendor-specific enhanced capability list/header fields, two vendor-specific payload dwords, AER enhanced capability list fields, uncorrectable error status/mask/severity bits, correctable error status/mask bits, advanced error capability/control bits, four TLP header-log dwords, and four TLP prefix-log dwords. Covered AER bits include DLP, surprise down, poisoned TLP, flow-control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked conditions.

The ARI and RTR portions at the end of each full VF block define enhanced capability list entries plus ARI capability/control and readiness-time reporting fields. ARI fields expose MFVC/ACS function-group support, next-function number, function-group enable bits, and selected function group. RTR fields expose reset, data-link-up, FLR, and D3hot-to-D0 timing values plus a valid bit for the first RTR timing dword.

The VF13 fragment begins another repeated VF config-space map. This chunk covers VF13 only through vendor ID, device ID, and the first seven command-register shift definitions; the command masks and all later VF13 fields continue after this work item.

## Control Flow

There is no executable control flow in this header. Its effect is compile-time: it gives C code the constants needed to produce or decode the exact PCIe config-space bit patterns expected by NBIO 4.3.0 hardware.

Typical runtime flow in consuming code is:

1. Select a `cfgBIF_CFG_DEV0_EPF0_VF*_*` offset from `nbio_4_3_0_offset.h`.
2. Read or compose a 16-bit or 32-bit PCIe configuration value through the AMD register access layer.
3. Apply this header's `__SHIFT` and `_MASK` macros directly or through `REG_SET_FIELD` and `REG_GET_FIELD`.
4. Write a control value, decode a capability/status value, poll a hardware-owned bit, clear sticky diagnostic status, or expose decoded state to PCIe, SR-IOV, reset, interrupt, virtualization, or diagnostics code.

Flows that can consume these fields include VF PCI capability presentation, VF MSI/MSI-X setup, AER error logging and clearing, function-level reset, PCIe link and power policy, ARI VF enumeration support, readiness-time reporting, PF or hypervisor inspection of VF config state, and suspend/resume or reset validation.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration-space state owned by the GPU, firmware, host PCIe fabric, Linux PCI core policy, and AMDGPU PF/SR-IOV management code.

The represented state includes identity/header values, BAR and ROM address windows, command/status bits, capability-list pointers, PCIe capability/control/status fields, link capability and link training state, MSI/MSI-X programming state, vendor-specific capability payloads, AER error status/mask/severity/log data, ARI function-group controls, and RTR timing capability data. Some fields are static capability descriptions, some are software-programmed controls, some are hardware-updated status, and some are sticky or write-one-to-clear diagnostics. The masks do not encode access permissions, reset defaults, ordering requirements, side effects, polling rules, or ownership boundaries.

VF10 through VF12 are complete within this chunk, so their repeated config-space layout can be reasoned about locally. VF9 and VF13 are boundary fragments and require adjacent chunks before making whole-VF claims.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 4.3.0 register database. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h`, which supplies the matching config-space offsets.
- Other generated NBIO 4.3.0 headers, including defaults or related register maps when present.
- AMDGPU register helper macros and accessors, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Observed direct C-file includes of this exact NBIO 4.3.0 shift/mask header in this source tree are SMU13 power-management files `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`. Even where these VF-specific macros are not referenced directly by name, the generated header participates in the common AMDGPU NBIO register ABI used by PCIe, link, power, SR-IOV, reset, and diagnostics paths.

Relevant integration surfaces are AMDGPU NBIO/BIF setup, PCIe link control, SR-IOV VF lifecycle, VF interrupt delivery, AER diagnostics, FLR and readiness-time reporting, ARI capability handling, power-management transitions, and platform firmware or Linux PCI core interactions over command/status, BARs, MSI/MSI-X, PCIe device/link control, AER, ARI, LTR, OBFF, completion timeout, and FLR fields.

## Risks And Edge Cases

- The chunk boundaries are artificial. The range starts at only one remaining VF9 vendor-specific-header mask and ends before VF13 command masks are emitted; adjacent chunks are required for complete VF9 and VF13 analysis.
- These are untyped preprocessor constants. A stale shift or mask can compile cleanly while decoding or programming the wrong hardware bit.
- The VF blocks are mechanically repetitive. Off-by-one suffix mistakes around VF9 through VF13 could silently target the wrong virtual function and break SR-IOV isolation, interrupt routing, diagnostics, or reset handling.
- Register-address and field-mask mismatches are easy in generated headers. A valid `VF11_LINK_CNTL` mask applied to a `VF12` or non-VF offset may still produce plausible bit operations while corrupting unrelated config state.
- PCIe control fields are interoperability-sensitive. Incorrect FLR, max payload, max read request, completion timeout, relaxed-ordering, no-snoop, LTR, OBFF, ARI, or link-control values can cause DMA ordering bugs, enumeration failures, link instability, reset failures, or platform-specific hangs.
- MSI/MSI-X fields carry interrupt-delivery side effects. Width, aliasing, table offset/BIR, mask, pending, or enable mistakes can cause lost interrupts, misrouted interrupts, or unexpectedly unmasked vectors.
- AER status, mask, severity, header log, and TLP prefix log fields can be sticky, write-one-to-clear, or hardware-owned. Generic read/modify/write treatment can clear diagnostic evidence or leave errors masked incorrectly.
- BAR and ROM fields affect resource exposure. Incorrect masks can expose invalid apertures, confuse VF resource sizing, or conflict with Linux PCI resource management.
- ARI and RTR fields affect VF enumeration and reset/power timing assumptions. Incorrect next-function numbers, function-group controls, reset timing, DL-up timing, FLR timing, or D3hot-to-D0 timing values can mislead virtualization and recovery paths.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 4.3.0 and SMU13 support enabled; missing, renamed, or duplicated macros should surface in include paths such as `smu_v13_0_0_ppt.c`, `smu_v13_0_7_ppt.c`, or shared AMDGPU register code.
- Compare VF10 through VF12 field layouts against `nbio_4_3_0_offset.h` to confirm register names, order, widths, and repeated VF layout remain synchronized.
- Boot affected hardware and confirm PCIe config exposure remains sane: VF identity/header fields, BARs, capability list, PCIe capability, MSI/MSI-X, AER, ARI, and RTR fields should decode consistently.
- In SR-IOV configurations, create and remove VFs around the VF9-VF13 range, bind guest drivers, exercise VF FLR, and verify VF isolation, config-space access, ARI enumeration behavior, interrupt delivery, and reset/recovery timing.
- Exercise graphics, compute, and DMA workloads with MSI/MSI-X enabled; lost interrupts, stuck pending bits, or unexpected vector masking can indicate MSI field layout or offset drift.
- Run PCIe reset, suspend/resume, runtime power, and link retraining tests while monitoring link speed/width, completion timeout behavior, LTR/OBFF state, FLR completion, and RTR timing assumptions.
- Use AER/error-injection or platform diagnostics where available to verify uncorrectable/correctable status, masks, severity fields, header logs, and TLP prefix logs map to expected PCIe errors.

## Chunk Notes

- Line 74048 is only the final `VSEC_LENGTH_MASK` for `BIF_CFG_DEV0_EPF0_VF9_1_PCIE_VENDOR_SPECIFIC_HDR`; the rest of that register's shifts and masks are in the previous chunk.
- Lines 74049-74257 cover the remaining VF9 vendor-specific, AER, ARI, and RTR field definitions.
- Lines 74260-76254 define complete `BIF_CFG_DEV0_EPF0_VF10_1`, `VF11_1`, and `VF12_1` PCIe VF config-space shift/mask blocks.
- Lines 76257-76466 begin `BIF_CFG_DEV0_EPF0_VF13_1` and stop inside the command register after `PARITY_ERROR_RESPONSE__SHIFT`; VF13 command masks and subsequent fields continue in the next chunk.
