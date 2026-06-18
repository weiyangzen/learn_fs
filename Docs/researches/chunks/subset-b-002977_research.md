# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 39245-41680

## Scope

This chunk covers generated shift and mask definitions for part of AMD NBIO 4.3.0 PCIe configuration-space register fields. The covered range starts in the tail of the `BIF_CFG_DEV0_EPF0_VF3` Advanced Error Reporting/ARI definitions, contains the full visible `BIF_CFG_DEV0_EPF0_VF4` virtual-function register field map, continues through `BIF_CFG_DEV0_EPF0_VF5` and `VF6` field groups, and ends at the beginning of `BIF_CFG_DEV0_EPF0_VF7_LINK_CAP`. The source is a pure C preprocessor header: it declares no functions, storage, structs, or executable control flow.

The file belongs to the AMDGPU driver register-description layer. It is included with `nbio/nbio_4_3_0_offset.h` by `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c` and SMU13 PPT code, where address macros from the offset header are paired with field macros from this header for typed bit manipulation.

## Purpose

The purpose of this chunk is to provide stable symbolic names for bit positions and bit masks in SR-IOV virtual function PCI/PCIe configuration registers on NBIO 4.3.0 ASICs. The names encode:

- The target PCI config block, such as `BIF_CFG_DEV0_EPF0_VF4`.
- The register or capability dword/word, such as `DEVICE_CNTL`, `LINK_STATUS2`, `MSI_MSG_CNTL`, `PCIE_UNCORR_ERR_STATUS`, or `PCIE_ARI_CNTL`.
- The individual field, such as `MAX_PAYLOAD_SIZE`, `LTR_EN`, `MSIX_EN`, `CPL_TIMEOUT_STATUS`, or `ARI_FUNCTION_GROUP`.
- Whether the macro is a bit shift (`__SHIFT`) or an already shifted mask (`_MASK`).

This lets C code avoid literal bit numbers when reading, updating, or testing PCIe configuration fields through MMIO/config-space accessors.

## Register Groups Covered

The chunk includes these major groups:

- `VF3` tail: correctable error status/mask, AER capability control, TLP header/prefix log registers, and ARI enhanced capability fields.
- `VF4` base PCI header: vendor/device ID, command/status, revision/class fields, cache-line/latency/header/BIST fields, BARs, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency.
- `VF4` PCIe capability: capability list, `PCIE_CAP`, device capability/control/status, link capability/control/status, device capability/control/status 2, and link capability/control/status 2.
- `VF4` MSI/MSI-X capability: MSI message control, MSI address/data/mask/pending fields for 32-bit and 64-bit forms, MSI-X table/PBA fields, and MSI-X enable/function-mask/table-size fields.
- `VF4` vendor-specific and AER extended capabilities: VSEC header/scratch fields, AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability control, header log dwords, TLP prefix log dwords, and ARI capability/control fields.
- `VF5` and `VF6`: the same virtual-function PCIe capability layout continues for later VFs in the visible chunk. These are structurally repetitive field maps for per-VF config-space instances.
- `VF7` beginning: base PCI header through device capability/control/status and the start of `LINK_CAP` fields. The chunk boundary ends after `VF7_LINK_CAP__LINK_SPEED`, `LINK_WIDTH`, power-management/latency/reporting bits, and `PORT_NUMBER` masks.

## Important APIs, Types, and Macros

There are no functions or C types in this range. The important interface is the generated macro naming convention:

- `BIF_CFG_DEV0_EPF0_VF<n>_<REG>__<FIELD>__SHIFT` gives the low bit of a field.
- `BIF_CFG_DEV0_EPF0_VF<n>_<REG>__<FIELD>_MASK` gives the shifted mask suitable for clearing, testing, or extracting field bits.
- Full-register payload fields use `0xFFFFFFFFL`, for example TLP header logs, TLP prefix logs, BARs, MSI pending/mask, and VSEC scratch registers.
- Smaller config-space fields use natural PCI/PCIe widths: byte fields often use `0xFFL`, 16-bit fields use `0xFFFFL`, and packed capability/control/status fields use narrower masks within 16-bit or 32-bit registers.

In normal AMDGPU code, these macros are consumed through helper macros and register accessors, including:

- `REG_GET_FIELD(value, REG, FIELD)` to extract a field using the `REG__FIELD_MASK` and `REG__FIELD__SHIFT` definitions.
- `REG_SET_FIELD(value, REG, FIELD, new_value)` to update one field while preserving the other bits.
- `RREG32_SOC15()` and `WREG32_SOC15()` to read and write NBIO registers by the corresponding `reg...` address macro from `nbio_4_3_0_offset.h`.
- `WREG32_FIELD15_PREREG()` and related helpers for direct field writes where supported by the local driver code.

The matching address definitions are not in this header. For example, `nbio_4_3_0_offset.h` maps `regBIF_CFG_DEV0_EPF0_VF4_DEVICE_CNTL` to `0x1901b` with base index `5`, `regBIF_CFG_DEV0_EPF0_VF4_PCIE_UNCORR_ERR_STATUS` to `0x19055`, and `regBIF_CFG_DEV0_EPF0_VF7_LINK_CAP` to `0x19c1c`. This chunk supplies the field layout for those addresses.

## Control Flow

This chunk has no runtime control flow. It is compile-time metadata that affects generated machine code only when included by C sources. The effective control flow is in callers:

1. A caller reads a register or configuration dword using an offset macro from `nbio_4_3_0_offset.h`.
2. It uses this header's mask/shift macros directly or indirectly through `REG_GET_FIELD`/`REG_SET_FIELD`.
3. It conditionally interprets status bits or constructs a modified value.
4. It writes the result back if configuration needs to change.

Examples elsewhere in the NBIO 4.3 implementation show this pattern for NBIO fields in general. `nbio_v4_3_program_ltr()` and `nbio_v4_3_program_aspm()` read device control and link/power registers, clear or set named masks, and write back only when the value changes. The exact VF4/VF7 macros in this chunk are not directly referenced in the searched C files, but they provide the same interface for SR-IOV virtual-function config-space handling, diagnostics, and future feature code.

## State and Persistence Behavior

The header itself has no state. The fields it describes map to hardware and PCIe configuration state:

- Command/status and device/link control bits can enable bus mastering, memory access, interrupts, relaxed ordering, no-snoop, max payload size, max read request size, LTR, completion timeout behavior, ARI forwarding, AtomicOp behavior, OBFF, and function-level reset initiation.
- Device/link status bits expose transient link state, link training, data-link active state, pending transactions, device errors, and equalization state.
- MSI/MSI-X registers hold interrupt routing state programmed by the PCI core or device driver, including MSI address/data, masks, pending bits, MSI-X table location, PBA location, and enable/mask controls.
- AER status registers represent latched hardware error state. AER mask and severity registers persist until software or firmware changes them. Header and TLP-prefix logs capture diagnostic packet context for errors.
- BAR, ROM, adapter ID, capability-pointer, and VSEC fields represent per-VF PCI config-space identity and resource layout.

Persistence depends on the underlying hardware reset domain. Values may be reset by PCI function reset, GPU reset, power state transitions, or firmware initialization. Because many status bits are write-one-to-clear or hardware-owned in PCIe-style registers, callers must use register-specific semantics rather than treating every mask as a normal read-modify-write field.

## Dependencies

This chunk depends on generated AMD register metadata consistency:

- The include guard and file-level register family identify NBIO 4.3.0.
- Address macros from `nbio_4_3_0_offset.h` are required to locate the registers described here.
- AMDGPU SOC15 accessors and field helpers need the `REG__FIELD_MASK` and `REG__FIELD__SHIFT` naming convention.
- PCI/PCIe architectural semantics define the meaning of many fields: standard PCI command/status, PCIe device/link capability and control, MSI/MSI-X, AER, VSEC, and ARI.
- SR-IOV integration depends on VF-specific register windows: this chunk covers fields for `VF3`, `VF4`, `VF5`, `VF6`, and the beginning of `VF7`.

The header is generated from ASIC register descriptions, so hand edits would be risky unless synchronized with the source register database and offset header.

## Integration Points

The most direct integration points are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, which includes this header and uses NBIO field masks for register programming, HDP remap/flush setup, doorbell aperture setup, ROM offset handling, ASPM/LTR programming, and SR-IOV register remap behavior.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include this NBIO register metadata along with SMU/MP register metadata for power-management paths.
- The Linux PCI core and AMDGPU SR-IOV support, which may interact with the same VF config-space concepts even when not directly referencing these exact generated names.
- Error handling and RAS/diagnostic paths that interpret AER error status, mask, severity, and TLP/header logs.

The register names also align with other generated families such as `nbif_6_3_1_sh_mask.h` and older `nbio_*_sh_mask.h` headers. That alignment allows common driver patterns to be carried across ASIC generations while selecting the correct per-generation offsets and masks.

## Risks and Edge Cases

- Boundary risk: this chunk begins mid-register group with `VF3_PCIE_UNCORR_ERR_SEVERITY` masks already in progress, and it ends mid-`VF7` capability group. Any final merged file-level research must reconcile this with adjacent chunks to avoid claiming the range contains complete VF3 or VF7 coverage.
- Width and aliasing risk: PCI config registers pack byte, word, and dword fields into the same 32-bit MMIO/config dword. Offset headers show aliases such as `DEVICE_CNTL` and `DEVICE_STATUS` sharing an address. Callers must use the correct field masks and access width/semantics.
- Status-clearing risk: AER and PCIe status bits often have write-one-to-clear behavior. Generic read-modify-write code can accidentally clear latched errors if it writes back a value containing status bits.
- Capability-chain risk: `CAP_ID`, `NEXT_PTR`, enhanced capability `CAP_VER`, and `NEXT_PTR` fields define discoverability. Incorrect masks or offsets can break capability traversal or cause software to misidentify MSI, MSI-X, AER, VSEC, or ARI capabilities.
- SR-IOV isolation risk: VF-specific control, BAR, MSI/MSI-X, and AER fields affect virtual functions. Using a PF or wrong VF register name can corrupt another function's configuration or expose incorrect state to a guest/host boundary.
- Generated-header drift: field names are repeated across VF instances and ASIC-generation headers. Copy/paste or generator defects can be hard to see in review because most lines differ only by VF number or mask suffix.
- Hardware-version risk: this is NBIO 4.3.0 metadata. Reusing these masks with a different NBIO/NBIF generation may silently address the wrong bit layout even when names look similar.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver integration signals:

- Build coverage: AMDGPU builds that include `nbio_v4_3.c` and the SMU13 PPT files should compile without undefined `BIF_CFG...` field macros or naming mismatches.
- Register helper coverage: code using `REG_GET_FIELD` or `REG_SET_FIELD` with registers from this range should expand successfully to the expected `__SHIFT` and `_MASK` names.
- Offset/mask consistency: each field group in this header should have a corresponding `regBIF_CFG_DEV0_EPF0_VF<n>_<REG>` entry in `nbio_4_3_0_offset.h`; spot checks show VF4 device control, VF4 AER status, and VF7 link capability are present.
- SR-IOV smoke tests: VF creation, VF reset, guest driver probe, BAR assignment, and MSI/MSI-X interrupt delivery should work without PCI config-space corruption.
- PCIe capability visibility: `lspci -vv` or equivalent config-space reads on supported hardware/VFs should show coherent PCIe, MSI/MSI-X, AER, VSEC, and ARI capability fields.
- Error-path diagnostics: injected or naturally occurring PCIe correctable/uncorrectable errors should set expected AER bits, preserve header/TLP-prefix logs, and respect mask/severity programming.
- Power/link behavior: link speed/width, ASPM/LTR, completion-timeout, and link-status reporting should match expected values across boot, runtime PM, reset, and resume.

## Summary

Lines 39245-41680 of `nbio_4_3_0_sh_mask.h` are generated register field metadata for NBIO 4.3.0 SR-IOV VF PCIe configuration space. The chunk is dominated by repeated per-VF masks and shifts for PCI header fields, PCIe device/link capabilities, MSI/MSI-X, vendor-specific capability, AER, TLP/header logs, and ARI. It has no runtime behavior on its own, but it is a critical compile-time contract between AMDGPU NBIO/SMU code, SOC15 register access helpers, PCIe config semantics, and hardware register offsets.
