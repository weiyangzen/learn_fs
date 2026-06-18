# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_sh_mask.h lines 32329-34751

## Scope

This chunk is a generated AMD NBIO 7.9.0 shift/mask header fragment. It contains C preprocessor constants only: `__SHIFT` and `_MASK` macros for fields in PCIe configuration-space style registers exposed through the NBIO/BIF device-function decode for `DEV0_EPF0` virtual functions.

The requested range starts in the middle of the VF2 PCIe capability block at `BIF_CFG_DEV0_EPF0_VF2_MSIX_MSG_CNTL`, covers the remainder of VF2's MSI-X/AER/vendor/ATS/ARI masks, covers complete VF3 and VF4 config-space mask blocks, and covers most of VF5 through `BIF_CFG_DEV0_EPF0_VF5_PCIE_ATS_CNTL`, ending at the start of `BIF_CFG_DEV0_EPF0_VF5_PCIE_ARI_ENH_CAP_LIST`. Adjacent chunks are needed for the earlier VF2 base/MSI definitions and the remainder of VF5 ARI plus later VFs.

There are no functions, structs, enums, storage definitions, locks, allocation paths, or runtime branches in this chunk. Its purpose is compile-time description of hardware bitfields.

## Purpose and Register Families

The macros describe how to extract or set individual fields in the NBIO 7.9.0 BIF PCI configuration register images for SR-IOV virtual functions. The register names follow AMDGPU's generated convention:

- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>_MASK`

The covered register families are:

- VF2 tail: MSI-X message control/table/PBA, vendor-specific extended capability, PCIe Advanced Error Reporting, header/TLP-prefix logs, Address Translation Services, and Alternative Routing-ID Interpretation masks.
- VF3 complete block: conventional PCI header fields, BARs, ROM, capability pointer, interrupts, PCIe capability/control/status, link capability/control/status, MSI/MSI-X, vendor-specific capability, AER, ATS, and ARI masks.
- VF4 complete block with the same PCI/PCIe/SR-IOV virtual-function layout as VF3.
- VF5 partial block: conventional PCI header through ATS control, plus the first ARI enhanced-capability comment and initial fields at the chunk boundary.

The generated content models the PCIe-visible configuration structure for GPU virtual functions rather than the higher-level Linux PCI core abstractions. It gives AMDGPU and diagnostics exact bit positions for fields such as command/status flags, link training state, MSI/MSI-X enablement, AER status/masks/severity, ECRC controls, ATS enablement, and ARI grouping.

## Important APIs, Types, and Macros

This chunk exports no callable API. The important interface is the macro naming contract consumed by AMDGPU register helpers:

- `REG_GET_FIELD(value, REGISTER, FIELD)` expects `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` to exist and extracts a field from a register value.
- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` uses the same generated macros to update a field without hand-coded shifts.
- `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and related helpers pair shift/mask headers with companion offset headers such as `nbio_7_9_0_offset.h`.

Representative field groups in this chunk:

- PCI command/status: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `INT_DIS`, `CAP_LIST`, `MASTER_DATA_PARITY_ERROR`, target/master abort flags, system error, and parity error.
- PCI identity and layout: `VENDOR_ID`, `DEVICE_ID`, class-code bytes, revision ID, cache line, latency, header type, BIST, BAR addresses, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability: `CAP_ID`, `NEXT_PTR`, `PCIE_CAP_VERSION`, `DEVICE_TYPE`, `SLOT_IMPLEMENTED`, `INT_MESSAGE_NUM`, maximum payload/read request sizes, relaxed ordering, no-snoop, phantom functions, extended tags, error reporting enables, aux power, FLR, and transaction-pending state.
- PCIe link capability/control/status: maximum speed/width, ASPM support/control, L0s/L1 exit latency, clock power management, hotplug-related bits, retrain/common-clock/extended-sync controls, negotiated link speed/width, slot clock, training, link bandwidth management/status, target link speed, speed disable, equalization, retimer presence, crosslink, current de-emphasis, and downstream component presence.
- MSI/MSI-X: capability-list pointers, MSI enable/multi-message fields, 64-bit support, per-vector masking, extended message-data support, message address/data/mask/pending fields, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability: VSEC capability id/version/next pointer, VSEC id/revision/length, and scratch registers.
- AER: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control including ECRC generation/check capability and enable bits, multi-header logging, TLP-prefix log presence, completion-timeout log capability, header logs, and TLP prefix logs.
- ATS and ARI: ATS enhanced capability list, invalidate queue depth, page-aligned requests, global invalidate support, relaxed ordering support, STU, ATC enable, ARI capability list, MFVC/ACS function-group capability, next function number, and ARI function-group controls where present in this range.

The complete VF3/VF4 blocks are useful as pattern anchors for merge-time validation because the same named registers and fields repeat with only the VF number changed.

## Control Flow and Data Flow

There is no direct control flow inside the header. Runtime behavior is indirect:

1. NBIO 7.9.0 driver code includes `nbio/nbio_7_9_0_sh_mask.h`.
2. Code reads a NBIO/BIF register or PCI configuration register image through AMDGPU's SOC15, PCIE-indexed, or config-space access path.
3. The read value is decoded with `REG_GET_FIELD()` using a macro pair from this header.
4. For writable fields, code builds a new value with `REG_SET_FIELD()` and writes it back through the matching offset/access helper.

The companion source `amdgpu/nbio_v7_9.c` demonstrates the general integration style for this header family: it includes `nbio_7_9_0_sh_mask.h`, uses generated masks with `REG_SET_FIELD()` for doorbell and interrupt-control programming, uses generated masks for HDP flush completion references, and registers `nbio_v7_9_funcs` callbacks used by the rest of AMDGPU. `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` also includes this header while wiring NBIO RAS interrupt sources.

This specific line range is dominated by virtual-function PCI config masks, so the main data flow is configuration/status interpretation rather than active initialization logic. Examples include decoding whether a VF has bus mastering enabled, whether link retraining is active, whether MSI-X is enabled or masked, whether an AER bit reports a poisoned TLP or completion timeout, and whether ATS/ARI features are advertised or enabled.

## State and Persistence

The header has no software state and no persistence. All constants are compile-time metadata.

The state described by these macros lives in hardware-maintained or PCIe configuration-space registers:

- Conventional PCI command/status bits represent enablement and error state for each virtual function and may be changed by firmware, hypervisor/PF management, or PCI configuration writes.
- BAR, ROM, class, subsystem, capability-list, and interrupt fields define the VF's PCI-visible identity and resources.
- PCIe device/link control and status bits track negotiated payload sizes, link speed/width, power-management policy, link training/equalization state, completion timeout behavior, and FLR/transaction-pending state.
- MSI/MSI-X registers hold interrupt-routing state including message addresses/data, vector masking, pending bits, table location, and PBA location.
- AER registers persist or latch PCIe error status until cleared according to hardware/PCIe semantics; mask and severity registers affect which errors are reported and how they are classified.
- ATS/ARI fields expose address-translation and routing capabilities that interact with IOMMU, virtualization, and PCIe hierarchy behavior.

Incorrect masks or shifts do not corrupt this header at runtime, but they make every compiled consumer extract or update the wrong hardware bits. Because the macros are compile-time constants, such errors are systematic and can survive normal type checking.

## Dependencies and Integration Points

This chunk depends on the generated AMD register database staying synchronized across:

- `nbio_7_9_0_sh_mask.h`, which supplies field encodings.
- `nbio_7_9_0_offset.h`, which supplies register addresses/base indices.
- AMDGPU's SOC15 register access macros and `REG_GET_FIELD`/`REG_SET_FIELD` helpers.
- NBIO 7.9.0 implementation files such as `amdgpu/nbio_v7_9.c`.
- NBIO RAS registration paths such as `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`.
- SR-IOV virtualization flows, where multiple VFs expose similar config spaces and field correctness must hold across VF numbers.

External integration is with PCIe-defined behavior: MSI/MSI-X, AER, ATS, ARI, link capability/control/status, and conventional PCI config header fields. Linux PCI core code may own many standard config-space writes, while AMDGPU/NBIO code and diagnostics need the hardware-specific generated masks to inspect, report, or manipulate NBIO-exposed fields.

## Risks and Edge Cases

- The chunk starts and ends on partial logical blocks. Merge logic must not treat this as a complete VF2 or complete VF5 report.
- VF3 and VF4 are highly repetitive. Generator drift can create a single wrong VF-numbered macro that still compiles but decodes the wrong VF field.
- Fields with the same bit numbers across status, mask, and severity registers are easy to confuse. For example, AER uncorrectable status, mask, and severity use parallel names but have different semantics.
- Some masks are 16-bit PCI config fields and others are 32-bit extended capability fields. Using a mask with the wrong access width can silently drop or misinterpret bits.
- MSI and MSI-X fields include overlapping address/data layouts for 32-bit and 64-bit modes. Wrong mask selection can misprogram vectors or pending masks.
- AER status fields can be sticky or write-one-to-clear depending on the underlying register. The masks only identify bits; driver code must still obey the hardware clear semantics.
- ATS and ARI enablement affects IOMMU and PCIe routing behavior. A wrong `ATC_ENABLE`, `STU`, function-group, or next-function-number interpretation can affect VF DMA translation or enumeration.
- Link control/status bits are live hardware state. Decoding retrain, equalization, bandwidth-management, and speed/width fields incorrectly can lead to misleading diagnostics or unsafe policy choices.
- Because this is a generated header, local manual edits are high risk unless regenerated from the authoritative hardware register specification.

## Test and Validation Signals

Useful validation is mostly compile-time plus hardware/SR-IOV behavior:

- Build AMDGPU with NBIO 7.9.0 enabled; missing or renamed macros fail at compile time in consumers using `REG_GET_FIELD()` or `REG_SET_FIELD()`.
- Compare this generated chunk against the authoritative NBIO 7.9.0 register spec and the matching `nbio_7_9_0_offset.h` entries for VF2 through VF5.
- Cross-check repeated VF3/VF4/VF5 macro sets mechanically: field names, shifts, and masks should match for equivalent registers unless the hardware spec intentionally differs.
- Exercise SR-IOV with multiple VFs enabled and confirm PCI config reads for VF3/VF4/VF5 report plausible vendor/device IDs, command/status bits, BARs, MSI/MSI-X capability structures, PCIe capability fields, AER capability structures, ATS, and ARI.
- Validate MSI and MSI-X interrupt delivery per VF, including masking/unmasking, pending bits, table/PBA location interpretation, and 64-bit MSI address/data layouts.
- Inject or observe PCIe/AER conditions where available and verify correct decoding of uncorrectable/correctable status, masks, severity, header logs, and TLP-prefix logs.
- Test link-state diagnostics on NBIO 7.9.0 hardware for negotiated speed/width, retrain/equalization state, ASPM-related controls, and bandwidth-management status.
- Run suspend/resume, FLR, GPU reset, and VF hot/unplug or rebind flows to verify VF config state is reinitialized or preserved as expected by firmware, PF management, and Linux PCI core.
