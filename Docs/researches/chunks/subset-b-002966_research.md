# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 12478-14939

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header segment. It covers 2,462 source lines and contains 2,119 preprocessor definitions: 1,068 `__SHIFT` constants and 1,051 `_MASK` constants. There are no C functions, structs, enums, variables, memory allocations, locks, or executable statements in this range.

The source boundary is artificial. The chunk opens at the tail of `BIF_CFG_DEV0_EPF0_0_DATA_LINK_FEATURE_STATUS`, then covers EPF0 PCIe extended capability maps for 16 GT/s PHY, lane margining, VF resizable BARs, 32 GT/s PHY, alternate protocol, and routing/transport-related data. It then crosses into `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, covering the full endpoint-function 1 PCI/PCIe configuration template through SR-IOV, VF resize BAR, and RTR fields. The final section starts `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and reaches EPF2 PCIe `DEVICE_CAP2`; EPF2 later PCIe capability, interrupt, AER, and extended-capability fields continue after this chunk.

## Purpose

`nbio_4_3_0_sh_mask.h` is the field-layout half of the generated NBIO 4.3.0 hardware interface. For each NBIO or PCI configuration register, it provides:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to pack or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update that field.

The companion generated address header, `nbio_4_3_0_offset.h`, supplies register/config-space offsets. Runtime AMDGPU code combines the offsets with these field constants through helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and related NBIO/PCI config access paths.

This chunk specifically describes PCI Express configuration-space capability layout for NBIO device 0 endpoint functions 0, 1, and 2. EPF0 content is focused on high-speed PHY/link features and newer extended capabilities. EPF1 content is a broad endpoint configuration image, including conventional PCI header fields, power management, PCIe device/link controls, MSI/MSI-X, AER, BAR resizing, DPA, ACS, PASID, multicast, LTR, ARI, SR-IOV, and RTR. EPF2 begins the same conventional PCI and PCIe capability pattern.

Although the repository path sits under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

### EPF0 high-speed PCIe capabilities

The chunk begins with the remaining `DATA_LINK_FEATURE_STATUS` fields for remote data-link feature support and validity, then maps the 16 GT/s PHY enhanced capability:

- `BIF_CFG_DEV0_EPF0_0_PCIE_PHY_16GT_ENH_CAP_LIST` supplies the extended capability ID, version, and next-pointer fields.
- `LINK_CAP_16GT` and `LINK_CNTL_16GT` are fully reserved in this generated layout.
- `LINK_STATUS_16GT` exposes equalization completion, equalization phase 1/2/3 success, and link equalization request status.
- `LOCAL_PARITY_MISMATCH_STATUS_16GT`, `RTM1_PARITY_MISMATCH_STATUS_16GT`, and `RTM2_PARITY_MISMATCH_STATUS_16GT` define 16-bit parity mismatch status fields.
- `LANE_0_EQUALIZATION_CNTL_16GT` through `LANE_15_EQUALIZATION_CNTL_16GT` define downstream/upstream 16 GT/s transmit preset fields per lane.

The margining enhanced capability is represented by:

- `PCIE_MARGINING_ENH_CAP_LIST`, with standard extended-capability ID/version/next-pointer fields.
- `MARGINING_PORT_CAP` and `MARGINING_PORT_STATUS`, indicating software-based margining support/readiness.
- `LANE_0_MARGINING_LANE_CNTL` through `LANE_15_MARGINING_LANE_CNTL`, each carrying receiver number, margin type, usage model, and margin payload.
- `LANE_0_MARGINING_LANE_STATUS` through `LANE_15_MARGINING_LANE_STATUS`, which mirror receiver, type, usage, and payload status fields.

The EPF0 VF resizable BAR capability includes:

- `PCIE_VF_RESIZE_BAR_ENH_CAP_LIST`.
- `PCIE_VF_RESIZE_BAR1_CAP` through `PCIE_VF_RESIZE_BAR6_CAP`, each exposing the resizable BAR size capability mask.
- `PCIE_VF_RESIZE_BAR1_CNTL` through `PCIE_VF_RESIZE_BAR6_CNTL`, each exposing BAR index, BAR size, and VF BAR offset fields.

The 32 GT/s PHY enhanced capability includes:

- `PCIE_PHY_32GT_ENH_CAP_LIST`, `LINK_CAP_32GT`, `LINK_CNTL_32GT`, and `LINK_STATUS_32GT`.
- `LINK_CAP_32GT` fields for equalization bypass-to-highest-rate support, no-equalization-needed support, modified transmission support, DRS support, and flit support.
- `LINK_CNTL_32GT` fields for equalization bypass, equalization-method selection, modified TS usage, DRS, and flit controls.
- `LINK_STATUS_32GT` fields for equalization bypassed, no-equalization-needed received, modified TS received, retimer DRS message receipt, and flit status.
- Modified TS capture fields in `RECEIVED_MODIFIED_TS_DATA1/2` and `TRANSMITTED_MODIFIED_TS_DATA1/2`, covering link-valid, number of lanes, lane number, N_FTS, pre-code request, DRS, speed-change/auto-speed/auto-lane capability, and lane margining fields.
- `LANE_0_EQUALIZATION_CNTL_32GT` through `LANE_15_EQUALIZATION_CNTL_32GT`, again encoding downstream/upstream per-lane transmit presets.

The remaining EPF0 extended capability families are:

- `PCIE_AP_ENH_CAP_LIST`, `AP_CAP`, `AP_CNTL`, `AP_DATA1`, `AP_DATA2`, and `AP_SEL_EN_MASK`, which describe alternate-protocol capability, control, protocol ID/data, and selection masks.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`, which expose routing/transport related capability payload fields including feature bits, segment ID, protocol ID, and lane/lane-margining data.

### EPF1 endpoint configuration block

The `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` address block is a full endpoint-function configuration template.

Conventional PCI header fields include:

- Identity and class: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS`.
- Command/status controls: `COMMAND` exposes I/O space, memory space, bus master, special cycle, memory write/invalidate, VGA palette snoop, parity response, wait cycle, SERR, fast back-to-back, interrupt disable, and capability enable bits; `STATUS` exposes immediate readiness, interrupt status, capability-list presence, DEVSEL timing, target/master abort, system error, parity error, and reserved bits.
- Header and resource fields: `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `MIN_GRANT`, `MAX_LATENCY`, `VENDOR_CAP_LIST`, and `ADAPTER_ID_W`.

Power-management and PCIe base capability fields include:

- `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, covering capability ID/next pointer, version, PME clock/support, D-state support, power state, no-soft-reset, PME enable/status, data select/scale, bus power enable, and PMI data.
- `PCIE_CAP_LIST` and `PCIE_CAP`, covering PCIe capability ID, next pointer, capability version, device type, slot implementation, and interrupt message number.
- `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS`, with payload/read-request sizing, relaxed ordering, extended tag, no-snoop, FLR initiation, error reporting enables/statuses, slot power limits, and pending transactions.
- `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`, with link speed/width, ASPM/PM support, exit latency, clock power management, surprise-down/DL-active/bandwidth reporting, port number, link disable/retrain, common clock, extended sync, bandwidth interrupts, DRS signaling, negotiated width/speed, training, and data-link active status.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, with completion timeout, ARI, atomic operations, LTR, TPH, ten-bit tags, OBFF, TLP prefix support/blocking, emergency power reduction, target link speed, compliance/de-emphasis, equalization status, lane-error status, and equalization phase indicators.

Interrupt capability fields include:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_EXT_MSG_DATA`, `MSI_MASK`, 64-bit data/mask aliases, and `MSI_PENDING`/`MSI_PENDING_64`.
- `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`, covering MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

Error-reporting, diagnostic, and vendor-specific fields include:

- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, and `PCIE_VENDOR_SPECIFIC2`.
- `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `PCIE_DEV_SERIAL_NUM_DW2`.
- `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`.
- `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY`, covering data-link protocol errors, surprise down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP prefix blocked.
- `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK`, covering receiver, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header-log-overflow classes.
- `PCIE_ADV_ERR_CAP_CNTL`, including first-error pointer, ECRC generation/check capability/enables, multi-header logging capability/enables, TLP prefix log presence, and completion-timeout log capability.
- `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3` and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3`.

Resource sizing, power, and secondary PCIe capabilities include:

- `PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR1_CAP/CNTL` through `PCIE_BAR6_CAP/CNTL`, describing resizable BAR size capability and selected BAR size.
- `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, and `PCIE_PWR_BUDGET_CAP`, describing power-budget table select/readback and system allocation.
- `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0` through `_7`, describing dynamic power allocation capability, transition latency, substate status/control, and per-substate power allocations.
- `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`, covering secondary PCIe capability metadata, perform equalization, lane error status, and per-lane equalization presets.

Isolation, address translation, routing, and virtualization fields include:

- `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`, covering source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, egress-control vector size, and related controls.
- `PCIE_PASID_ENH_CAP_LIST`, `PCIE_PASID_CAP`, and `PCIE_PASID_CNTL`, covering execute-permission, privileged-mode support, maximum PASID width, and enable bits.
- `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, `PCIE_MC_ADDR0/1`, `PCIE_MC_RCV0/1`, `PCIE_MC_BLOCK_ALL0/1`, and `PCIE_MC_BLOCK_UNTRANSLATED_0/1`, covering multicast capability, enablement, group count, address, receiver, and block masks.
- `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP`, covering max snoop/no-snoop latency value and scale fields.
- `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`, covering MFVC/ACS function-group capability, next-function number, forwarding, MFVC, ACS function groups, and function group selection.
- `PCIE_SRIOV_ENH_CAP_LIST`, `PCIE_SRIOV_CAP`, `PCIE_SRIOV_CONTROL`, `PCIE_SRIOV_STATUS`, `PCIE_SRIOV_INITIAL_VFS`, `PCIE_SRIOV_TOTAL_VFS`, `PCIE_SRIOV_NUM_VFS`, `PCIE_SRIOV_FUNC_DEP_LINK`, `PCIE_SRIOV_FIRST_VF_OFFSET`, `PCIE_SRIOV_VF_STRIDE`, `PCIE_SRIOV_VF_DEVICE_ID`, `PCIE_SRIOV_SUPPORTED_PAGE_SIZE`, `PCIE_SRIOV_SYSTEM_PAGE_SIZE`, `PCIE_SRIOV_VF_BASE_ADDR_0` through `_5`, and `PCIE_SRIOV_VF_MIGRATION_STATE_ARRAY_OFFSET`.
- `PCIE_VF_RESIZE_BAR_ENH_CAP_LIST`, `PCIE_VF_RESIZE_BAR1_CAP/CNTL` through `PCIE_VF_RESIZE_BAR6_CAP/CNTL`, describing VF BAR resize capability and selected sizes.
- `PCIE_RTR_ENH_CAP_LIST`, `RTR_DATA1`, and `RTR_DATA2`, mirroring the RTR-style payload used in the EPF0 block.

### EPF2 partial endpoint configuration block

The `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` block begins near the end of the chunk. It repeats the early endpoint template:

- Conventional PCI fields from `VENDOR_ID` through `MAX_LATENCY`, including command/status, BARs, ROM BAR, capability pointer, interrupts, and adapter ID.
- `VENDOR_CAP_LIST` and `ADAPTER_ID_W`.
- Power-management fields `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`.
- USB-related conventional fields `SBRN`, `FLADJ`, and `DBESL_DBESLD`.
- PCIe base fields `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, and the first part of `DEVICE_CAP2`.

Because the source range ends in `BIF_CFG_DEV0_EPF2_0_DEVICE_CAP2`, no complete conclusions should be drawn about EPF2's later PCIe, MSI/MSI-X, AER, or extended capability coverage from this chunk alone.

## APIs, Types, And Functions

There are no callable APIs or C types in this segment. The public interface is the macro namespace itself. The generated macro names are part of AMDGPU's hardware register ABI inside the driver source: consumers rely on the exact spelling, shift values, and masks matching the corresponding register offsets and the hardware register database for NBIO 4.3.0.

The constants do not encode access width, read/write permission, reset defaults, volatile behavior, write-one-to-clear behavior, or side effects. Those semantics are supplied by the PCIe specification, AMD hardware definitions, firmware setup, and the runtime driver code that chooses when and how to access the fields.

## Control Flow

This header has no local control flow. Runtime flow is external and typically follows this shape:

1. AMDGPU code selects an NBIO 4.3.0 register/configuration offset from `nbio_4_3_0_offset.h`.
2. It reads or composes a register value using these `__SHIFT` and `_MASK` constants, usually through register helper macros.
3. It writes, polls, decodes, logs, or preserves the value according to PCIe/NBIO semantics.

Likely call-path categories include NBIO initialization, PCIe capability discovery, link and equalization handling, GPU power management, SR-IOV PF/VF setup, interrupt routing, AER collection, resizable BAR configuration, ATS/PASID/IOMMU-related enablement, ACS isolation, ARI routing, and device display/power code that needs NBIO capability or register data.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. It names hardware-visible PCI configuration and extended-capability state owned by the NBIO block.

Represented state includes static identity and capability fields, driver or firmware configured control bits, host-assigned resource BARs, MSI/MSI-X message routing state, power-management status/control, PCIe link state, equalization and lane-margining status, AER sticky error state and logs, resizable BAR selections, SR-IOV VF layout, ACS/PASID/ARI isolation/routing controls, multicast state, DPA power allocations, and endpoint-function capability-chain topology.

Persistence is governed outside this file by GPU/NBIO reset domains, PCI config save/restore, firmware initialization, suspend/resume, function-level reset, SR-IOV PF/VF lifecycle, and explicit driver writes. Many fields are not ordinary memory-like storage:

- Error status and AER fields may be sticky and may require write-one-to-clear handling.
- `INITIATE_FLR` starts reset behavior rather than storing a passive bit.
- Link disable/retrain and equalization controls can disturb link training and device availability.
- MSI/MSI-X enable, mask, pending, table, and PBA fields affect interrupt delivery.
- ACS, PASID, ARI, and SR-IOV controls affect isolation, enumeration, and routing.
- BAR sizing and VF resize fields interact with PCI resource assignment and virtualization layout.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 4.3.0 register family:

- `nbio_4_3_0_offset.h` provides matching register/configuration offsets.
- `nbio_4_3_0_default.h`, when present in the generated header set, provides reset/default values for adjacent register families.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` definitions for field extraction and updates.

Observed in-tree include-level integration for `nbio_4_3_0_sh_mask.h` includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c`, the NBIO 4.3 implementation.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_0_ppt.c`.
- `drivers/gpu/drm/amd/pm/swsmu/smu13/smu_v13_0_7_ppt.c`.

Related display resource files include `nbio_4_3_0_offset.h` for address data without directly including this shift/mask header. The generated names also align with other NBIO generation headers, but values and feature coverage are generation-specific; consumers should use the header selected by the active ASIC/IP block.

The endpoint-function and SR-IOV fields integrate with Linux PCI enumeration, resource assignment, MSI/MSI-X setup, virtualization/PF management, IOMMU/PASID flows, AER reporting, power management, and PCIe link training. The file does not implement those policies; it supplies the bit layout used by policy code.

## Risks And Edge Cases

- Generated field drift can compile cleanly while making the driver touch the wrong hardware bit. High-risk fields include command/bus-master bits, BAR sizes, MSI/MSI-X enables, FLR, AER clear/status bits, ACS/PASID/ARI controls, SR-IOV controls, and link retrain/equalization controls.
- The chunk starts and ends inside larger logical regions. EPF0 `DATA_LINK_FEATURE_STATUS` begins before the chunk, and EPF2 `DEVICE_CAP2` continues after it. Merge/reconciliation should avoid treating those partial boundaries as complete register-family coverage.
- EPF0 16 GT/s and 32 GT/s per-lane definitions are mechanically repeated for lanes 0-15. Any lane-specific mismatch may be meaningful, but repeated definitions alone are intentional generator output.
- Reserved fields such as the 16 GT/s link cap/control masks should not be assumed writable just because a mask exists. Reserved bit preservation matters when composing register writes.
- Link equalization, margining, modified TS, DRS, and flit controls can change link-training behavior; incorrect masks can cause downtraining, failed retraining, or intermittent PCIe link failures.
- Resizable BAR and VF BAR controls affect host PCI resource layout. Wrong size masks or selected-size encodings can break BAR probing, memory windows, or VF exposure.
- MSI/MSI-X table, PBA, mask, and pending fields can cause lost, repeated, or misrouted interrupts if decoded incorrectly.
- AER status/log fields are diagnostic evidence. Incorrect write handling may clear useful data or fail to clear real faults.
- ACS/PASID/ARI/SR-IOV fields are isolation-sensitive. Wrong masks can affect DMA isolation, function routing, VF enumeration, and translation-tag behavior.
- The EPF1 block includes many PCIe optional capabilities. Runtime code must still check capability presence and platform policy before assuming a feature should be enabled.

## Test Signals

- Build AMDGPU with NBIO 4.3 and SMU13 support enabled. Missing, renamed, or malformed macros should surface through compile failures in NBIO and PM users.
- Probe a supported AMD GPU and confirm `nbio_v4_3` initialization completes without register access faults or PCIe capability decode warnings.
- PCI enumeration should show stable vendor/device/class IDs, capability chains, BAR sizing, ROM BAR state, and endpoint functions for EPF1/EPF2 where applicable.
- Link-health testing should verify expected negotiated width/speed, successful link retrain paths, no unexpected 16 GT/s or 32 GT/s equalization failures, and stable lane-status reporting.
- Margining and modified-TS diagnostics, where platform-supported, should produce coherent per-lane status without corrupting link state.
- Interrupt smoke tests should verify MSI/MSI-X enable, mask, pending, table, and PBA behavior under load.
- Error-injection or PCIe health tests should verify AER status/mask/severity decoding and preservation of header/TLP-prefix logs.
- SR-IOV validation should cover PF controls, VF counts/stride/offset/device ID, VF BARs, VF resizable BAR controls, FLR, and per-VF resource exposure.
- IOMMU/virtualization tests should exercise PASID, ACS, ARI, and related isolation/routing behavior.
- Suspend/resume and GPU reset tests should confirm PCI config save/restore and NBIO reinitialization preserve or restore expected field values.
