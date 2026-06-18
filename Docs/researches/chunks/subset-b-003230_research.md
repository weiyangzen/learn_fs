# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_sh_mask.h lines 9745-12178

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.4 register shift/mask header. It defines preprocessor constants for bitfield extraction and composition in NBIF/BIF PCI configuration-space registers exposed by NBIO. The file is a hardware register contract: it contains no executable logic, but downstream AMDGPU code depends on these names, shifts, and masks matching the ASIC register map exactly.

The requested range contains 2,434 source lines and 2,138 `#define` entries. Of those definitions, 1,070 are `__SHIFT` constants and 1,068 are `_MASK` constants. The slight imbalance comes from chunk boundaries: the range starts partway through `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`, after some earlier shifts were defined in the previous chunk, and ends partway through `BIF_CFG_DEV0_EPF0_VF5_0_LINK_CAP`, before the matching masks appear in the next chunk.

At a high level, the chunk covers:

- The tail of virtual function 1 (`BIF_CFG_DEV0_EPF0_VF1_0`) PCIe AER, TLP logging, ATS, and ARI field definitions.
- Complete visible register-field layouts for `VF2_0`, `VF3_0`, and `VF4_0` under `nbio_nbif0_bif_cfg_dev0_epf0_vf*_bifcfgdecp`.
- The beginning of `VF5_0`, from standard PCI identity/header fields through PCIe device control/status and the first `LINK_CAP` shifts.

Despite the repository path containing `ceph-client`, this source is AMD GPU driver register metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based starting bit for a field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

The most important macro groups are organized by PCIe virtual function.

The `VF1_0` tail continues from the previous chunk and includes:

- `PCIE_UNCORR_ERR_MASK`: remaining uncorrectable-error mask shifts plus masks for data link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast-blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors.
- `PCIE_UNCORR_ERR_SEVERITY`: severity classification fields for the same uncorrectable PCIe error sources.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`: corrected-error observation and masking for receiver error, bad TLP, bad DLLP, replay counter rollover, replay timeout, advisory nonfatal error, corrected internal error, and header-log overflow.
- `PCIE_ADV_ERR_CAP_CNTL`: first-error pointer, ECRC generation/check capability and enable bits, multi-header-recording capability and enable bits, TLP prefix log presence, and completion-timeout logging capability.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`: full-dword AER diagnostic log fields.
- `PCIE_ATS_*`: ATS enhanced capability list, invalidate queue depth, page-aligned request, global invalidate support, STU, and ATC enable fields.
- `PCIE_ARI_*`: ARI enhanced capability, next-function number, MFVC/ACS function-group support, enable bits, and function group selector.

The `VF2_0`, `VF3_0`, and `VF4_0` sections repeat a complete PCI/PCIe virtual-function configuration shape. Each block includes standard PCI header and capability fields:

- Identity and header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST`.
- Resource fields: `BASE_ADDR_1` through `BASE_ADDR_6`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, and `INTERRUPT_PIN`.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.
- MSI and MSI-X fields: capability list pointers, message control, 32-bit and 64-bit message address/data fields, mask and pending fields, MSI-X table BIR/offset, and MSI-X PBA BIR/offset.
- Vendor-specific extended capability fields: enhanced capability list header, vendor-specific header, and two scratch payload dwords.
- AER fields: enhanced capability header, uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, and TLP prefix logs.
- ATS and ARI fields: enhanced capability headers plus control/capability fields for address translation services and alternative routing-ID interpretation.

The `VF5_0` portion begins at line 11975 and is incomplete within this chunk. It defines `VF5_0` identity, standard PCI command/status, class/header/BIST, BARs, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, PCIe capability header, device capability/control/status, and the start of `LINK_CAP` shifts through `DL_ACTIVE_REPORTING_CAPABLE`. The remaining `LINK_CAP` shifts and masks continue after line 12178.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It is consumed at compile time by AMDGPU and power-management code that reads or writes NBIO registers with generated address constants from the companion offset header and field helpers such as `REG_SET_FIELD` or equivalent mask/shift operations.

The implied runtime flow in consumers is:

1. Select the NBIO/BIF config register address for a virtual function using the matching offset header.
2. Read the register through an AMDGPU MMIO, SMN, or PCIe-port access helper.
3. Decode a field with the generated `_MASK` and `__SHIFT`, or compose a new register value by clearing the mask and inserting a shifted field value.
4. Write the modified value back when the field is writable, or use the decoded value for diagnostics, link state, interrupt setup, or virtualization policy.

Hardware behavior represented by these fields includes PCI enumeration, BAR/resource reporting, bus-master and memory-space enablement, interrupt masking, MSI/MSI-X programming, PCIe link capability/control/status, AER policy and diagnostic capture, ATS translation enablement, and ARI function routing.

The header does not encode access permissions, reset values, write-one-to-clear behavior, timing requirements, or side effects. For example, AER status bits and PCIe device status bits may be sticky or clear-on-write in hardware, while capability bits are generally read-only. Callers must use the hardware specification and existing driver sequencing.

## State and Persistence

The file owns no state, allocates no memory, and persists nothing. It describes hardware register state that exists in NBIO/BIF PCI configuration-space images for SR-IOV-like virtual functions.

State represented by this chunk includes:

- Enumeration and identity state: vendor/device IDs, revision and class codes, header type, BIST, capability pointer, interrupt line/pin, subsystem IDs, ROM base, and BAR encodings.
- Control policy state: PCI command enables, parity/SERR/interrupt-disable settings, PCIe error-report enables, relaxed ordering, no-snoop, maximum payload size, maximum read request size, extended tags, phantom functions, function-level reset initiation, ASPM/link controls, completion-timeout policy, and link disable/retrain controls.
- Interrupt state: MSI enablement, multi-message capability/enable fields, 64-bit addressing, per-vector masking, pending bits, MSI-X enable/function mask, table offsets/BIRs, and PBA offsets/BIRs.
- Error state and policy: AER uncorrectable/correctable status bits, error masks, severity classification, first-error pointer, ECRC controls, header-log overflow, and captured TLP header/prefix logs.
- Translation and routing state: ATS invalidate queue depth, ATC enable/STU, ARI next-function information, and ARI function-group controls.
- Link state: advertised speed/width, power-management support, exit latencies, surprise-down reporting, data-link active reporting, current negotiated speed/width, link training, slot clock configuration, link bandwidth status, target speed, equalization status, de-emphasis, and autonomous speed/width controls.

Persistence of these hardware fields across reset, FLR, suspend/resume, runtime power transitions, or BACO is not defined by this header. A wrong macro value, however, persists in the compiled driver until the generated header is regenerated or fixed and the driver is rebuilt.

## Dependencies and Integration Points

The direct companion headers in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_offset.h`, which supplies the register address/offset constants corresponding to these field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_4_0_smn.h`, which supplies NBIO 7.4 SMN-level register definitions used by some NBIO code.

Files in this tree that include `nbio_7_4_sh_mask.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_inc.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_hwmgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/arcturus_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/aldebaran_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_6_ppt.c`

Several display and PSP files include the NBIO 7.4 offset header without this shift/mask header, so they may use raw offsets or different field definitions for their limited needs. The main low-level integration point for the full mask namespace is `amdgpu/nbio_v7_4.c`, while power-management code uses the same generated register contract for ASIC-specific setup and telemetry paths.

The macros in this chunk are tightly coupled to exact symbol names. `BIF_CFG_DEV0_EPF0_VF2_0_*`, `VF3_0_*`, `VF4_0_*`, and `VF5_0_*` describe different virtual-function configuration images even when the field layout is mechanically identical. A consumer must pair the correct function-prefixed mask with the matching function-prefixed offset.

## Risks and Edge Cases

- The chunk starts and ends inside register definitions. `VF1_0_PCIE_UNCORR_ERR_MASK` is missing some earlier shifts from the previous chunk, and `VF5_0_LINK_CAP` is missing its later shifts and all masks in this chunk. Pair-completeness checks must be done after adjacent chunks are merged.
- Generated names such as `PCIE_UNCORR_ERR_MASK__DLP_ERR_MASK_MASK` are easy to misread. The first `MASK` is part of the hardware register/field name and the final `_MASK` is the generated macro suffix.
- Repeated VF layouts create cross-function hazards. A `VF2_0` mask may have the same numeric value as a `VF3_0` mask, but using it with the wrong offset hides the fact that code is accessing the wrong virtual function.
- PCI command and device-control fields affect memory decoding, bus mastering, parity/SERR response, interrupt disable, relaxed ordering, no-snoop, FLR, maximum payload, and maximum read request size. Incorrect masks can break enumeration, DMA, interrupts, or PCIe transaction sizing.
- AER status/mask/severity fields have similar names but different semantics. Confusing status with mask or severity can suppress errors, misclassify fatal/nonfatal events, or lose diagnostic context.
- Header and TLP prefix logs are full-dword fields. They look simple, but decoding the wrong VF's log can send debugging toward the wrong function or transaction.
- MSI/MSI-X offset and BIR fields are packed into the same registers. Bad extraction can point interrupt setup at the wrong BAR aperture or table.
- ATS and ARI controls affect address translation, invalidation behavior, function routing, and virtualization isolation. Incorrect field definitions or wrong-function usage can cause IOMMU/PASID integration failures or routing bugs.
- Link capability/control/status bits are timing-sensitive when used for retrain, target speed, ASPM, and link status polling. The existence of a mask does not mean the driver may freely write the field.
- The macros use C integer literals with `L` suffixes and mixed logical widths (`0xFFL`, `0xFFFFL`, `0xFFFFFFFFL`). Consumers should preserve unsigned register-width handling when composing 32-bit values.

## Test and Validation Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU configurations that include NBIO 7.4 headers and the known consumers listed above. This catches malformed macro names, duplicate definitions, and missing symbols used by driver code.
- After merging adjacent chunks, mechanically verify every field has a matching `__SHIFT` and `_MASK` pair. Expected local boundary exceptions are the partial `VF1_0_PCIE_UNCORR_ERR_MASK` at the start and partial `VF5_0_LINK_CAP` at the end.
- Cross-check every `BIF_CFG_DEV0_EPF0_VF[2-5]_0_*` register name in this range against `nbio_7_4_offset.h` so field macros have corresponding address definitions where expected.
- Run symmetry checks across `VF2_0`, `VF3_0`, and `VF4_0`; their common standard PCI, PCIe, MSI/MSI-X, vendor-specific, AER, ATS, and ARI field layouts should match unless the generated register database intentionally differs.
- Validate PCI configuration-space dumps on NBIO 7.4 hardware by decoding VF2/VF3/VF4 and the visible VF5 fields with these masks and comparing identity, BAR, capability-list, MSI/MSI-X, link, AER, ATS, and ARI values against expected hardware documentation.
- Exercise MSI and MSI-X interrupt setup, including masking and pending-bit behavior, for virtual functions whose config images are represented here.
- Exercise PCIe error handling with controlled correctable and uncorrectable errors and confirm decoded status, mask, severity, first-error pointer, header log, and TLP prefix log fields.
- Validate link-management paths by checking reported current speed/width, negotiated width, link-training status, data-link-layer active, bandwidth status, ASPM controls, target link speed, and equalization-related fields where present.
- Validate virtualization and IOMMU paths involving ATS and ARI, including ATC enable/STU programming, invalidate queue-depth interpretation, next-function number decoding, and ARI function-group controls.
- Run suspend/resume, FLR, hot reset, and GPU reset coverage to ensure policy fields are restored by driver code and status fields still decode correctly after reset-domain transitions.

## Chunk Boundary Notes

The range begins at line 9745 inside `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_MASK`, starting with `UNEXP_CPL_MASK__SHIFT`. The earlier uncorrectable-error mask shifts are in the previous work item, while this range includes all masks for that register and then continues through the rest of the visible `VF1_0` AER/ATS/ARI tail.

Lines 9923, 10607, and 11291 introduce complete address blocks for `VF2_0`, `VF3_0`, and `VF4_0`. Each full block runs from standard PCI identity fields through ARI control fields.

Line 11975 introduces `nbio_nbif0_bif_cfg_dev0_epf0_vf5_bifcfgdecp`. The range covers `VF5_0_VENDOR_ID` through the first part of `VF5_0_LINK_CAP`, ending at line 12178 with `DL_ACTIVE_REPORTING_CAPABLE__SHIFT`. The remaining `VF5_0_LINK_CAP` shifts, all `LINK_CAP` masks, and later `VF5_0` fields belong to the next chunk.
