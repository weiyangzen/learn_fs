# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 34202-36635

## Scope

This chunk covers a generated AMD NBIO 2.3 register shift/mask header segment for PCIe configuration-space fields on device 0, endpoint function 0 virtual functions. The range begins with the final four macros for `BIF_CFG_DEV0_EPF0_VF7_PCIE_ARI_CNTL`, then contains complete `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`, `vf9`, and `vf10` address blocks, and ends partway through `vf11` at `BIF_CFG_DEV0_EPF0_VF11_LINK_CAP2`.

The chunk contains only C preprocessor definitions. There are no functions, structs, enums, variables, executable statements, or in-file storage. In this range there are 2,147 `#define` entries, mostly paired as `__SHIFT` and `_MASK` constants, covering 276 register/comment groups.

## Purpose

The purpose of this header chunk is to encode bit positions and bit masks for NBIO/BIF PCI and PCIe configuration registers exposed for SR-IOV virtual functions. Driver code uses this file together with the corresponding `nbio_2_3_offset.h` register-address header and AMDGPU register helper macros to compose, read, and decode hardware register fields without hard-coding bit constants in C logic.

The macro naming convention is:

- `BIF_CFG_DEV0_EPF0_VF<N>_<REGISTER>__<FIELD>__SHIFT` for a field's least-significant bit.
- `BIF_CFG_DEV0_EPF0_VF<N>_<REGISTER>__<FIELD>_MASK` for the field mask in the register value.

The repeated virtual-function blocks make the same PCIe capability model available for each VF number. In this chunk, VF8, VF9, and VF10 are complete; VF11 is truncated by the chunk boundary after `LINK_CAP2`; VF7 appears only as the tail of the previous chunk's ARI control register.

## Important Macro Families

### PCI Configuration Header

Each complete VF block starts with PCI configuration header fields:

- `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS` describe device identity and class-code metadata.
- `COMMAND` exposes standard enable/control bits such as I/O access, memory access, bus mastering, SERR, parity response, and interrupt disable.
- `STATUS` exposes readiness, interrupt status, capability-list presence, parity/error reporting, abort status, and DEVSEL timing.
- `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST` encode standard PCI header fields.
- `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, and min/max latency model the rest of the type-0 PCI header layout.

These fields are mostly 8-bit, 16-bit, or 32-bit PCI config-space fields with masks such as `0xFFL`, `0xFFFFL`, and `0xFFFFFFFFL`. Multi-field registers use masks that match standard PCI bit allocation, for example `ADAPTER_ID` splits subsystem vendor ID and subsystem ID into low and high 16-bit halves.

### PCIe Capability Registers

The `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` groups define the PCI Express capability structure for each VF.

Important fields include:

- Device capabilities such as max payload support, phantom functions, extended tags, L0s/L1 acceptable latency, role-based error reporting, slot power fields, and function-level reset capability.
- Device control bits for enabling corrected/non-fatal/fatal/unsupported-request reporting, relaxed ordering, extended tags, no-snoop, maximum payload size, maximum read request size, and initiating FLR.
- Device status bits for corrected, non-fatal, fatal, and unsupported request errors, auxiliary power, pending transactions, and emergency power-reduction detection.
- Link capability, control, and status fields for link speed, link width, ASPM/PM support, exit latencies, clock power management, bandwidth notification, link disable/retrain, common-clock configuration, data link active state, and bandwidth status.

These macros are the bit-level ABI for any NBIO code that needs to inspect or program per-VF PCIe link/device behavior. Many fields are capability or status bits read from hardware, while control fields can trigger visible PCIe behavior such as FLR or link retraining when written through the matching register address.

### PCIe Capability 2 / Link 2

`DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover later PCIe capability extensions.

The chunk includes fields for completion-timeout ranges and disable support, ARI forwarding, atomic operations, ID-based ordering, latency tolerance reporting, ten-bit tags, OBFF, end-to-end TLP prefixes, emergency power reduction, and FRS support. Link 2 fields include supported link speeds, crosslink support, SKP ordered-set generation/receive support, retimer presence-detect support, target link speed, compliance controls, transmit margin, de-emphasis, equalization completion/phase status, and downstream component presence.

The VF11 section ends inside this family. It includes `VF11_LINK_CAP2` definitions in full through `DRS_SUPPORTEDRESERVED_MASK` at the chunk boundary context, while later VF11 Link Control 2, Link Status 2, MSI/MSI-X, AER, ATS, and ARI fields belong to a later chunk.

### MSI and MSI-X

The complete VF8, VF9, and VF10 blocks include MSI and MSI-X capability structures:

- `MSI_CAP_LIST` and `MSI_MSG_CNTL` encode the capability header and MSI enable/control fields, including multiple-message capability, 64-bit address capability, vector mask capability, and pending-enable behavior.
- `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_PENDING`, and their 64-bit layout aliases expose message address, data, mask, and pending bits.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` define MSI-X capability header, table size, function mask, MSI-X enable, table BIR/offset, and pending-bit-array BIR/offset.

These fields are integration points for interrupt routing and virtualization. The header only provides the encodings; actual interrupt enablement, vector allocation, and guest/PF ownership rules are implemented elsewhere in AMDGPU, PCI core, and virtualization code.

### Vendor-Specific and Advanced Error Reporting

For VF8 through VF10, the chunk defines:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`.
- `PCIE_ADV_ERR_CAP_CNTL`.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3`.
- `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`.

The uncorrectable error groups cover data link protocol errors, surprise down, poisoned TLP, flow-control protocol errors, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, MC blocked TLP, atomic egress block, TLP prefix blocked, and poisoned TLP egress block. Correctable error groups cover receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal errors, correctable internal error, and header-log overflow. The `ADV_ERR_CAP_CNTL` fields expose first-error pointer, ECRC capabilities/enables, multi-header recording, TLP prefix log presence, and completion-timeout logging capability.

This is the most diagnostic-heavy area in the complete VF blocks. It supports PCIe AER decoding and masking, but status clear/write-one-to-clear semantics are determined by the hardware register specification and calling code, not by this header.

### ATS and ARI Extended Capabilities

The complete VF8 through VF10 blocks end with Address Translation Service and Alternative Routing-ID Interpretation definitions:

- `PCIE_ATS_ENH_CAP_LIST`, `PCIE_ATS_CAP`, and `PCIE_ATS_CNTL` include extended capability header fields, invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` include capability header fields, MFVC/ACS function-group capabilities, next function number, enable bits, and function group selection.

The chunk also starts with the final `VF7_PCIE_ARI_CNTL` masks, confirming this file repeats the same capability model across VF blocks. ATS and ARI fields matter for PCIe virtualization and IOMMU-facing behavior; incorrect enablement can affect DMA address translation and function routing.

## Control Flow

There is no C control flow in this chunk. The effective control flow is external:

1. A driver source includes `nbio_2_3_sh_mask.h`, usually alongside `nbio_2_3_offset.h`.
2. Driver code selects a register address from the offset header or through an AMDGPU NBIO helper.
3. It uses field masks and shifts from this header with helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, `RREG32_PCIE`, or related SOC15/NBIO access wrappers.
4. The resulting read or write operation affects the NBIO hardware register or PCIe configuration-space shadow for the selected virtual function.

Because this segment is generated constants, correctness depends on exact alignment between the hardware generation scripts, the offset header, and the ASIC register specification. There is no local runtime validation.

## State and Persistence Behavior

The header itself has no mutable state and persists nothing. State lives in NBIO/PCIe hardware registers and in whatever kernel or firmware layers read or write them.

Field semantics vary by register family:

- Identity and capability fields are generally hardware-defined or firmware-populated and read mostly as stable configuration.
- Control fields such as `COMMAND`, `DEVICE_CNTL`, `DEVICE_CNTL2`, `LINK_CNTL`, `LINK_CNTL2`, `MSI_MSG_CNTL`, `MSIX_MSG_CNTL`, `ATS_CNTL`, and `ARI_CNTL` can alter hardware behavior until reset, reinitialization, or another writer changes them.
- Status and error fields such as `STATUS`, `DEVICE_STATUS`, `LINK_STATUS`, `LINK_STATUS2`, AER status, and MSI pending fields reflect transient hardware events and may have clear-on-write or write-one-to-clear behavior outside this header.
- Log registers such as PCIe header and TLP prefix logs persist captured error context until cleared or overwritten according to PCIe AER hardware behavior.

In SR-IOV systems, access policy is also stateful: the PF, guest VF, PCI core, IOMMU, firmware, or hypervisor may own different subsets of these registers.

## Dependencies and Integration Points

Direct dependencies are minimal because this is a header of macros guarded by `_nbio_2_3_SH_MASK_HEADER`. Important surrounding files and users include:

- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_offset.h`, which supplies matching register offsets such as the `cfgBIF_CFG_DEV0_EPF0_VF*_...` names. The masks here are not useful without a matching address source.
- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_default.h`, which supplies generated defaults for the same NBIO IP generation.
- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, the primary NBIO 2.3 implementation. It includes this header and provides the `amdgpu_nbio_funcs` implementation for revision ID, memory access, doorbell apertures, interrupt helper setup, clock gating, ASPM/LTR programming, and register remapping. This chunk's VF-specific PCI config macros are not directly referenced in the searched C sources, but they are part of the same generated include surface.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, which includes `nbio_2_3_offset.h` and `nbio_2_3_sh_mask.h` for multi-vGPU/SR-IOV support paths.
- SMU power-management files such as `pm/swsmu/smu11/navi10_ppt.c` and `sienna_cichlid_ppt.c`, which include NBIO 2.3 generated register headers for platform-specific register access.

The common register helper macros are defined elsewhere in the AMDGPU tree. This file provides only numeric constants, so all type checking, access width selection, locking, reset sequencing, and privilege checks are implemented by callers.

## Risks

- Bitfield drift: if these generated masks do not match the actual NBIO 2.3 hardware register layout, field extraction and writes can silently target the wrong bits.
- Offset/mask mismatch: using masks from this header with an offset from another NBIO version or another VF instance can corrupt unrelated PCIe config state.
- Write-sensitive fields: macros for FLR, link retraining, MSI/MSI-X enable, ATS enable, ARI enable, AER masks, and completion timeout controls describe fields that can have immediate system-visible effects when written.
- Virtualization ownership: per-VF config registers may be visible through PF emulation, guest config access, or hypervisor paths. Using the wrong access path risks breaking isolation or racing guest/host ownership.
- Status clearing semantics: AER and PCI status fields often use write-one-to-clear behavior. Generic read/modify/write code must preserve or clear bits intentionally.
- Chunk boundary risk: this work item ends in the middle of the VF11 capability block. A final per-file report must merge with adjacent chunks before drawing complete conclusions about VF11.
- Generated-code maintenance: manual edits to this file are high risk. Changes should come from the register database/generator or be verified against hardware documentation.

## Test Signals

Since this chunk is a generated macro table, meaningful tests are mostly compile-time, integration, and hardware/VM validation rather than unit tests inside the header.

Useful signals include:

- Kernel build coverage for AMDGPU configurations that include `nbio_v2_3.c`, MXGPU/SR-IOV code, and SMU 11 power-management files.
- Compile-time detection of missing or renamed macros in code that uses `REG_SET_FIELD`/`REG_GET_FIELD` with NBIO 2.3 fields.
- Static comparison against `nbio_2_3_offset.h` to ensure every register family has matching offset and mask definitions for each VF block.
- SR-IOV smoke testing with multiple VFs enabled, confirming guest enumeration, BAR sizing, MSI/MSI-X delivery, FLR, reset recovery, and PF/VF isolation.
- PCIe AER injection or fault-observation tests checking that uncorrectable/correctable error status, mask, severity, header log, and TLP prefix log fields decode as expected.
- ATS/ARI validation under an IOMMU-enabled setup, confirming address translation enablement and function routing remain correct.
- ASPM/link-state diagnostics that read link speed, width, training, equalization, and bandwidth notification fields before and after power-management transitions.
