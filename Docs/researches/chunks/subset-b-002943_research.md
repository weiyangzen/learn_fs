# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 96045-98522

## Scope

This chunk is a generated AMD NBIO 2.3 shift/mask header segment. It contains C preprocessor constants only: no functions, structs, enums, variables, locks, allocations, or direct register accesses are defined here.

The line range starts in the tail of the `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` scheduler descriptor dwords, then covers a full `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` PCI configuration-space map, and then covers most of `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` through `BIF_CFG_DEV0_EPF3_1_PCIE_TPH_ST_TABLE_18`.

The public interface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.

## Purpose

`nbio_2_3_sh_mask.h` is the bit-layout side of the NBIO 2.3 hardware ABI used by AMDGPU. The matching offset header supplies register addresses/config offsets, and this header supplies the bit positions and masks used by AMDGPU register helpers to compose writes and decode reads.

This chunk focuses on multifunction PCIe endpoint functions `EPF2` and `EPF3`, plus the trailing EPF1 GPU IOV scheduler data. The generated constants describe standard PCI configuration fields, PCIe capability structures, message-signaled interrupt programming, vendor-specific capability dwords, Advanced Error Reporting, resizable/enhanced BAR capabilities, power budgeting, dynamic power allocation, access-control/address-translation capabilities, PASID/ARI, and TPH requester steering tables.

These definitions matter because NBIO/BIF PCIe state is shared between GPU driver policy, Linux PCI core behavior, firmware defaults, hypervisor/SR-IOV handling, and hardware diagnostic paths. A symbolic mask lets code use the correct bitfield without open-coding raw PCIe bit positions at each call site.

## Important Macro Families

### EPF1 GPUIOV Scheduler Tail

The range begins after the comment for `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VCESCH_DW7`; the visible EPF1 portion includes:

- `VCESCH_DW8` for the final visible VCE scheduler descriptor dword.
- `GFXSCH_DW0` through `GFXSCH_DW8`.
- `UVD1SCH_DW0` through `UVD1SCH_DW8`.

Each of these exposes a single full-width field (`DWn`) with shift `0x0` and mask `0xFFFFFFFFL`. The values are opaque AMD vendor-specific GPUIOV scheduler descriptor dwords rather than standard PCIe fields. Their interpretation belongs to the GPUIOV/PF virtualization stack and related firmware/hypervisor contracts.

### EPF2 Base PCI Configuration

The `EPF2` block starts at `BIF_CFG_DEV0_EPF2_1_VENDOR_ID` and defines the normal PCI configuration header:

- Identity and class fields: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status fields: IO and memory access enables, bus mastering, parity/SERR behavior, interrupt disable, readiness, capability-list presence, abort reporting, and parity error state.
- Header and BAR fields: cache-line size, latency timer, header type, BIST, `BASE_ADDR_1` through `BASE_ADDR_6`, CardBus CIS pointer, subsystem/vendor adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency.
- Vendor and power-management capability fields: `VENDOR_CAP_LIST`, `ADAPTER_ID_W`, `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- USB-like support registers visible in this generated PCI config map: `SBRN`, `FLADJ`, and `DBESL_DBESLD`.

The command/status fields are especially sensitive because the masks target PCI config control and sticky/error status bits. The header only names the bits; ownership and write-clear behavior are determined by PCIe/NBIO hardware and the caller's access path.

### EPF2 PCIe, MSI, and Vendor Capabilities

The EPF2 PCIe capability block includes:

- `PCIE_CAP_LIST` and `PCIE_CAP` for capability ID, next pointer, version, device/port type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` for max payload, phantom functions, extended tag support, endpoint L0s/L1 latency, role-based error reporting, captured slot power, function-level reset, error-reporting enables, relaxed ordering, max payload/read request, no-snoop, auxiliary power, transactions pending, and unsupported request state.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` for supported/current link speed and width, ASPM, L0s/L1 exit latency, clock power management, hot-plug/surprise-down reporting, retrain/disable/common-clock controls, bandwidth management, link training, slot clock, data-link active, and autonomous bandwidth state.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for completion timeout ranges, timeout disable, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, TPH completer support, end-to-end TLP prefix controls, emergency power reduction, ten-bit tags, target link speed, compliance/de-emphasis controls, equalization, retimer presence, and link margining status.
- MSI and MSI-X programming fields: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, 64-bit layout aliases, pending-bit registers, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- SATA/IDP capability fields: `SATA_CAP_0`, `SATA_CAP_1`, `SATA_IDP_INDEX`, and `SATA_IDP_DATA`.
- Vendor-specific extended capability fields: `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.

The MSI `_64` fields reflect alternate layout interpretation when 64-bit MSI address support is enabled. They should not be treated as independent storage separate from the underlying PCI capability layout.

### EPF2 Error, BAR, Power, and Translation Capabilities

The EPF2 extended capability area includes:

- Advanced Error Reporting: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four header-log dwords, and four TLP-prefix-log dwords.
- Enhanced BAR controls: `PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR1_CAP` through `PCIE_BAR6_CAP`, and `PCIE_BAR1_CNTL` through `PCIE_BAR6_CNTL`.
- Power budgeting: `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, and `PCIE_PWR_BUDGET_CAP`.
- Dynamic Power Allocation: `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0` through `_7`.
- Access and routing features: `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, `PCIE_PASID_CNTL`, `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.
- TPH requester fields: `PCIE_TPH_REQR_ENH_CAP_LIST`, `PCIE_TPH_REQR_CAP`, `PCIE_TPH_REQR_CNTL`, and the full `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63`.

The TPH steering-table entries each expose lower and upper 8-bit entries inside a 16-bit mask pair. This is a repeated mechanical family where index drift is easy to miss in review.

### EPF3 PCIe Map Through TPH Table 18

The `EPF3` block repeats the same generated layout as EPF2 from `VENDOR_ID` through `PCIE_TPH_ST_TABLE_18`:

- Complete base PCI header, PM, PCIe device/link, MSI/MSI-X, SATA/IDP, vendor-specific, AER, enhanced BAR, power-budget, DPA, ACS, PASID, ARI, and TPH requester capability fields are present through the visible range.
- The chunk ends at `BIF_CFG_DEV0_EPF3_1_PCIE_TPH_ST_TABLE_18__TPH_ST_UPPER_ENTRY_MASK`; `PCIE_TPH_ST_TABLE_19` through `_63` continue in the next chunk.

EPF2 and EPF3 are intentionally distinct macro namespaces. A caller can compile successfully while using an EPF2 mask with an EPF3 offset or vice versa, so code review must verify both the register address and the field macro prefix.

## Important APIs, Types, and Functions

There are no C functions or types in this chunk. The important "API" is the preprocessor symbol surface consumed by AMDGPU register-access code.

Typical consumers combine these masks with:

- Matching NBIO 2.3 offset symbols from `nbio_2_3_offset.h`.
- Matching reset/default symbols from `nbio_2_3_default.h`.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`.

The macro values are mostly 8-bit, 16-bit, or 32-bit PCI/PCIe fields represented as C integer constants with an `L` suffix. The generated names imply register width and field semantics, but the header does not enforce access size, read-only/write-only status, write-one-to-clear behavior, or PF/VF permissions.

## Control Flow

This header has no runtime control flow. Runtime behavior occurs in callers:

1. AMDGPU, PCIe, firmware-facing, or virtualization code includes the NBIO 2.3 offset/default/mask headers.
2. The caller selects an EPF1, EPF2, or EPF3 register offset and the corresponding field mask/shift from this header.
3. Helper macros shift and mask values when composing a register write or decoding a register read.
4. PCIe/NBIO hardware, firmware-owned state, or hypervisor-mediated config space observes the resulting read/write.

Because this is PCI configuration-space metadata, the actual access path may be PCI config access, NBIO index/data registers, SMN access, or PF-mediated virtualization control. The header does not decide which path is legal for a given field.

## State and Persistence Behavior

The macros are compile-time constants and hold no software state. They describe hardware-visible PCIe/NBIO state.

State represented by this chunk includes:

- EPF1 GPUIOV scheduler descriptor dwords for VCE, GFX, and UVD1 scheduling/resource descriptors.
- EPF2 and EPF3 identity, class, BAR, ROM, subsystem, interrupt, and capability-chain presentation.
- PCI command/status and PM state, including memory/bus-master enables, interrupt disable, power state, PME controls, and status/error latches.
- PCIe device and link capability/control/status state, including payload size, read request size, relaxed ordering, no-snoop, FLR, completion timeout, LTR, OBFF, target/current link speed, negotiated width, retrain/disable, equalization, retimer, and bandwidth status.
- MSI/MSI-X programming state for EPF2 and EPF3, including message address/data, vector count/enablement, mask/pending bits, MSI-X table location, and PBA location.
- AER diagnostic state: uncorrectable/correctable status, masks, severity, capability/control bits, header logs, and TLP prefix logs.
- Enhanced BAR and power-management state: BAR size/enable controls, power budget data selection and values, DPA capability/status/control, and DPA substate power allocations.
- Interconnect and isolation controls: ACS, PASID, ARI, and TPH requester enablement/steering-table entries.

Persistence is hardware-defined. These fields can be reset or reinitialized by GPU reset, PCI function reset, FLR, secondary bus reset, suspend/resume, power-state transitions, firmware actions, hypervisor operations, or explicit driver writes. Status and log fields may be transient or write-one-to-clear, while capability fields are usually hardware/firmware-defined and read-only or read-mostly.

## Dependencies and Integration Points

Direct dependencies:

- `nbio_2_3_offset.h` supplies the register/config-space offsets that must be paired with these masks.
- `nbio_2_3_default.h` supplies reset/default values for the same NBIO 2.3 register families.
- AMDGPU register helpers provide the C-side read/modify/write and field extraction mechanics.
- Linux PCI/PCIe semantics define the standard capability behavior mirrored by many of these masks: PM, MSI/MSI-X, AER, ACS, PASID, ARI, TPH, BAR sizing, DPA, link control/status, and device control/status.
- AMD GPUIOV/SR-IOV firmware or hypervisor interfaces define the opaque vendor-specific scheduler dwords and function ownership rules.

Observed source-tree integration:

- `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c` includes `nbio/nbio_2_3_sh_mask.h` with the matching generated headers for NBIO 2.3 register programming.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c` includes this header in virtualization-oriented AMDGPU code.
- `drivers/gpu/drm/amd/pm/swsmu/smu11/navi10_ppt.c` and `drivers/gpu/drm/amd/pm/swsmu/smu11/sienna_cichlid_ppt.c` include the same NBIO generated header family for PCIe/NBIO-related SMU platform behavior.

Integration is name-based and compile-time. The generated masks do not identify whether Linux PCI core, AMDGPU, firmware, or a hypervisor owns a field at runtime. Callers must respect subsystem ownership when touching shared PCI config fields such as MSI/MSI-X, AER, ACS/PASID/ARI, link controls, power controls, and BAR controls.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can silently alter adjacent PCIe config bits, misreport a capability, break endpoint enumeration, corrupt MSI/MSI-X setup, or hide PCIe errors.
- EPF namespace drift is easy to introduce. EPF2 and EPF3 have near-identical generated families, so an EPF2 field macro paired with an EPF3 register address can compile while targeting the wrong function layout.
- GPUIOV scheduler dwords are opaque full-width fields. Treating them as generic scratch registers can corrupt virtualization resource/scheduler state owned by firmware, PF management code, or a hypervisor.
- PCI command/status, PM, link control, FLR, AER, MSI/MSI-X, and TPH fields may have side effects. Generic read/modify/write code can clear sticky diagnostics, retrain links, reset a function, disable interrupt delivery, or change DMA permissions.
- MSI and MSI-X state overlaps Linux PCI core ownership. Direct AMDGPU writes must not race PCI core vector allocation, masking, table programming, or teardown.
- AER fields are diagnostic and often write-one-to-clear. Incorrect masks or careless writes can erase first-error evidence or suppress critical/nonfatal/fatal reporting.
- ACS, PASID, ARI, and TPH affect isolation, address tagging, routing, and host interconnect behavior. Enabling unsupported or policy-disallowed combinations can create protocol errors or weaken virtualization isolation.
- Power-budget and DPA controls affect platform power/latency behavior. Incorrect power data or substate allocation can cause performance regressions, latency spikes, or power-policy mismatches.
- The chunk boundaries are partial. The EPF1 scheduler family starts before this range, and the EPF3 TPH steering table continues after this range; file-level conclusions need neighboring chunks.

## Test and Validation Signals

Useful signals for changes touching this chunk or code that consumes it:

- Build AMDGPU paths that include `nbio_2_3_sh_mask.h`, especially `nbio_v2_3.c`, `mxgpu_nv.c`, and the SMU11 platform files.
- Static generated-header checks should compare `nbio_2_3_sh_mask.h`, `nbio_2_3_offset.h`, and `nbio_2_3_default.h` for matching EPF2/EPF3 register families, mask widths, and repeated table indexes.
- PCIe enumeration should continue to show sane EPF2/EPF3 identity, class, BAR, PM, PCIe, MSI/MSI-X, AER, ACS/PASID/ARI, TPH, power-budget, DPA, and vendor-specific capability structures where exposed.
- Runtime PCIe tests should validate link speed/width reporting, retraining behavior, ASPM/LTR/OBFF policy, payload/read-request sizes, completion timeout settings, and link status/equalization bits.
- MSI/MSI-X tests should validate vector enablement, message address/data programming, mask/pending behavior, MSI-X table/PBA interpretation, interrupt delivery, and teardown.
- AER error-injection or hardware error diagnostics should verify uncorrectable/correctable status, mask, severity, header log, TLP prefix log, and clear semantics.
- SR-IOV/GPUIOV validation should cover PF-managed resource partitioning, scheduler descriptor programming, VF lifecycle, guest load/unload, function reset, and hypervisor mailbox/resource ownership.
- Power-management validation should cover suspend/resume, runtime power transitions, D3/D0 transitions, DPA substate behavior, and power-budget reporting.
- TPH validation should ensure steering-table indexes decode coherently for EPF2 table entries 0-63 and EPF3 entries 0-18 in this chunk, with EPF3 entries 19-63 reconciled against the next chunk.

## Cross-Chunk Notes

- The range begins in the middle of the EPF1 GPUIOV scheduler descriptor area; earlier EPF1 `VCESCH_DW0` through part of `VCESCH_DW7` are outside this chunk.
- The EPF2 address block appears complete in this chunk, including all visible TPH steering-table entries 0-63.
- The EPF3 address block is incomplete at the end of the range. `PCIE_TPH_ST_TABLE_19` through `PCIE_TPH_ST_TABLE_63` continue after line 98522.
- The final per-file research merge should reconcile this chunk with neighboring generated-header chunks before making complete claims about EPF1 GPUIOV scheduler coverage or EPF3 TPH requester coverage.
