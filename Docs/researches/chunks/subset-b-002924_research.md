# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 48778-51444

## Scope

This chunk covers generated AMD NBIO 2.3 shift/mask macros. It is data-only C preprocessor material: no functions, structs, variables, allocation, locking, persistence code, or executable control flow live here.

The range starts near the end of the `BIF_CFG_DEV0_EPF0_VF28` PCIe capability block, beginning with `PCIE_TLP_PREFIX_LOG3` and continuing through VF28 ATS and ARI fields. It then covers complete PCI/PCIe configuration-space bitfields for SR-IOV virtual functions `VF29` and `VF30`. The final address block starts `nbio_nbif0_pciemsix_0_usb_MSIXTDEC` and defines MSI-X table entry fields from vector 0 through `PCIEMSIX_VECT102_ADDR_LO`; the range ends on the `PCIEMSIX_VECT102_ADDR_HI` register comment before that register's shift/mask fields.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU hardware register metadata, not Ceph or distributed filesystem code.

## Purpose

The purpose of this header section is to publish the bit-level ABI for NBIO 2.3 PCIe configuration and MSI-X table registers. Each generated field is represented by the conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to pack or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or preserve the field in a 16-bit or 32-bit register value.

The companion `nbio_2_3_offset.h` header supplies register addresses and base indices. Runtime AMDGPU code combines offsets with these macros through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

## Important Macro Families

### VF28 Capability Tail

The opening lines continue the previous chunk's `BIF_CFG_DEV0_EPF0_VF28` configuration-space description. The covered fields are the tail of Advanced Error Reporting and extended capability state:

- `PCIE_TLP_PREFIX_LOG3`, carrying a full-width TLP prefix log word.
- `PCIE_ATS_ENH_CAP_LIST`, with capability ID, capability version, and next-pointer fields.
- `PCIE_ATS_CAP`, with invalidate queue depth, page-aligned request, and global invalidate support fields.
- `PCIE_ATS_CNTL`, with smallest translation unit and ATC enable fields.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, covering ARI enhanced capability linkage, function group capability, next function number, function group enables, and function group selection.

Because this chunk starts after most of VF28, it should be reconciled with the preceding chunk before making a complete VF28 statement.

### VF29 and VF30 PCI Configuration Space

The `nbio_nbif0_bif_cfg_dev0_epf0_vf29_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf0_vf30_bifcfgdecp` address blocks are structurally parallel. They expose generated bitfields for a virtual PCIe endpoint function:

- Standard PCI header fields: vendor/device IDs, command, status, revision, programming interface, subclass, base class, cache line size, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, subsystem/adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: capability list linkage, PCIe capability metadata, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- MSI capability fields: MSI capability list linkage, message control, message address low/high, message data, mask, pending, and 64-bit variants.
- MSI-X capability fields: MSI-X capability list linkage, message control, table location/BIR, and pending bit array location/BIR.
- Vendor-specific enhanced capability fields: enhanced capability list metadata, vendor-specific header, and two vendor-specific payload registers.
- Advanced Error Reporting fields: AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four TLP header log words, and four TLP prefix log words.
- ATS and ARI enhanced capability fields: capability list linkage, ATS capability/control, ARI capability/control, and related function group/next-function metadata.

The field names mirror PCIe-defined concepts closely. Examples include command bits for I/O, memory, bus mastering, SERR, and interrupt disable; device control bits for correctable/nonfatal/fatal/unsupported-request reporting, relaxed ordering, max payload, extended tag, phantom functions, aux power PM, no-snoop, max read request, bridge configuration retry, and FLR initiation; link fields for speed, width, ASPM, retrain, common clock, extended sync, hardware autonomous width disable, link bandwidth management interrupt, and automatic bandwidth interrupt; and Device/Link 2 fields for completion timeout, atomic operation support/control, LTR, OBFF, target link speed, equalization, selectable de-emphasis, and current de-emphasis.

The AER uncorrectable status/mask/severity families cover data link protocol, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked status. Correctable error fields cover receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory nonfatal, correctable internal error, and header log overflow.

### MSI-X Table Vector Fields

The `nbio_nbif0_pciemsix_0_usb_MSIXTDEC` block defines repeated MSI-X table entries. For each complete vector entry in this chunk, four logical registers are present:

- `PCIEMSIX_VECTn_ADDR_LO`, with `MSG_ADDR_LO` shifted by 2 and masked as `0xFFFFFFFC`, preserving the PCI MSI-X requirement that message addresses are naturally aligned.
- `PCIEMSIX_VECTn_ADDR_HI`, with a full-width high message-address field.
- `PCIEMSIX_VECTn_MSG_DATA`, with a full-width message-data field.
- `PCIEMSIX_VECTn_CONTROL`, with bit 0 as `MASK_BIT`.

The covered complete entries are vectors 0 through 101. The chunk includes `PCIEMSIX_VECT102_ADDR_LO` and the comment for `PCIEMSIX_VECT102_ADDR_HI`, but not the shift/mask definitions for `VECT102_ADDR_HI`, `VECT102_MSG_DATA`, or `VECT102_CONTROL`. Adjacent chunks must be merged to describe the full MSI-X table.

## Control Flow

There is no runtime control flow in this header. The operational flow belongs to AMDGPU NBIO, PCIe, interrupt, SR-IOV, and power-management code that includes the generated header:

1. Code selects a register address from `nbio_2_3_offset.h` or another generated offset header.
2. It reads or prepares a 16-bit or 32-bit register/config-space value through SOC15, PCIe, or KIQ-safe access helpers.
3. It uses the `__SHIFT` and `_MASK` constants, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to update or decode a specific field.
4. It writes the value back, polls hardware status, or records decoded state according to the owning PCIe/NBIO/MSI-X programming sequence.

Direct include sites in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, SMU11 power-management files such as `navi10_ppt.c` and `sienna_cichlid_ppt.c`, and DCN resource files that include the NBIO 2.3 offset namespace. The chunk itself does not decide policy or sequencing.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed PCIe configuration, capability, error-reporting, address translation, ARI, and MSI-X state whose lifetime is controlled by PCIe enumeration, driver initialization, guest/PF/VF ownership, FLR, hot reset, suspend/resume, runtime power management, interrupt setup, and hardware error handling.

The VF29/VF30 state represented here includes PCI command/status bits, BAR and ROM address fields, capability-chain pointers, MSI/MSI-X configuration, PCIe device/link negotiated state, AER error status/mask/severity/logs, ATS enablement and translation granularity, and ARI function grouping. Some fields are configuration that remains until reset or reprogramming; others are hardware-owned status, sticky error state, self-clearing command bits, write-one-to-clear bits, or fields owned by host/guest PCI configuration mechanisms. The header names the bits but does not encode access permissions, reset defaults, side effects, ordering, locking, or timeout rules.

The MSI-X table state is interrupt delivery state. Address and data fields are programmed by PCI/MSI-X setup paths, and each vector control field's `MASK_BIT` gates delivery for that vector. Incorrect handling can expose vectors before address/data are valid, leave interrupts masked, or deliver to the wrong CPU interrupt target.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register set staying synchronized:

- `nbio_2_3_offset.h` supplies matching offsets and base indices.
- `nbio_2_3_default.h` supplies reset/default values for related NBIO registers and VF PCI configuration images.
- AMDGPU helper macros consume the generated shift/mask names for typed-looking but preprocessor-only register composition.

The integration surface is AMDGPU's NBIO/BIF layer, SR-IOV PF/VF support, PCIe capability handling, MSI/MSI-X interrupt setup, AER/error-reporting paths, ATS/IOMMU-related enablement, ARI virtualization/function enumeration, and power-management code that reasons about NBIO/PCIe state. Generic Linux PCI code manages the architectural meaning of many of these fields, while AMDGPU uses these generated definitions for GPU-internal register/config-space access.

The MSI-X table fields are also an integration point with interrupt remapping and vector allocation. Address low/high, data, and per-vector mask bits must match PCI MSI-X semantics and the table layout supplied by the matching offset header.

## Risks And Edge Cases

- The assigned range has artificial boundaries. It starts mid-VF28 capability tail and ends mid-MSI-X-vector family at `PCIEMSIX_VECT102_ADDR_HI`; final per-file analysis must join adjacent chunks.
- These are untyped preprocessor constants. A stale mask, wrong shift, typo in a repeated VF name, or use with the wrong offset can compile cleanly while programming the wrong hardware bits.
- VF29 and VF30 are highly repetitive. A one-off mechanical error can affect only one VF's PCI command/status, BAR, MSI, AER, ATS, or ARI behavior and remain hidden unless high-numbered VFs are enumerated and exercised.
- PCIe command, device control, link control, and Device/Link 2 fields are protocol-sensitive. Incorrect masks can break enumeration, bus mastering, memory decoding, max payload/read request programming, FLR, completion timeout policy, ASPM, LTR, OBFF, target link speed, retraining, or equalization state handling.
- AER status/mask/severity fields may be sticky, write-one-to-clear, or hardware-owned. Incorrect use can hide real errors, create interrupt storms, clear forensic logs too early, or misclassify fatal versus nonfatal conditions.
- ATS and ARI fields affect address translation and function enumeration. Incorrect ATC enable/STU, invalidate capability, ARI next-function, or function-group fields can cause DMA translation faults, stale translations, or broken VF discovery/isolation.
- MSI/MSI-X fields are interrupt-delivery-sensitive. Programming address/data/mask fields out of sequence can lose interrupts, deliver them to the wrong target, or unmask vectors before the table entry is valid.
- The MSI-X table has many identical vector entries. Off-by-one vector addressing or copying the wrong vector number can affect a single interrupt source and be difficult to correlate with the generated macro error.

## Test And Validation Signals

Useful validation is mostly build, PCIe integration, interrupt, and SR-IOV hardware coverage:

- Build AMDGPU code that includes `nbio/nbio_2_3_sh_mask.h`; missing or renamed macros should fail in NBIO, SMU11, display, and virtualization consumers.
- Enumerate SR-IOV configurations that expose high-numbered VFs, especially VF29 and VF30, and verify PCI vendor/device IDs, class codes, BARs, capability-chain pointers, MSI/MSI-X capabilities, AER, ATS, and ARI visibility.
- Exercise guest VF bind/unbind, FLR, hot reset, suspend/resume, and bus-master/memory-enable transitions while checking that command/status and capability fields behave as expected.
- Run MSI and MSI-X interrupt tests with multiple vectors, including mask/unmask and pending-bit behavior, to catch table address/data/control regressions and vector-index mistakes.
- Run PCIe link-management tests across retrain, ASPM policy changes, payload/read-request changes, completion-timeout settings, LTR/OBFF paths, and error recovery.
- Use AER injection or platform diagnostics where available to confirm uncorrectable/correctable status, mask, severity, header log, and TLP prefix log behavior.
- Exercise ATS/IOMMU paths for VFs with address translation enabled, including invalidation and reset paths, to detect incorrect STU, ATC enable, or invalidate capability interpretation.
- In virtualization test matrices, validate ARI enumeration/function grouping and isolation for high-numbered VFs so VF29/VF30-specific macro drift is visible.

## Unresolved Cross-Chunk References

The first register family, `BIF_CFG_DEV0_EPF0_VF28_PCIE_TLP_PREFIX_LOG3`, began in the previous chunk with earlier VF28 PCIe/AER fields. The final MSI-X family continues after line 51444 with `PCIEMSIX_VECT102_ADDR_HI` field definitions and later vector entries. The merge/reconciliation lane should stitch those boundaries before producing the final `nbio_2_3_sh_mask.h` report.
