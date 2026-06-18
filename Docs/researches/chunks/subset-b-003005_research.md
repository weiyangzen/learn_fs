# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 1-2431

## Scope

This chunk covers the first 2,431 lines of the generated NBIO 6.1 shift/mask header. It starts the header guard and defines C preprocessor constants for two NBIO/PCIe configuration-space address blocks:

- `nbio_pcie_pswuscfg0_cfgdecp`, a `PSWUSCFG0_*` PCIe upstream/switch-port style config-space map from standard PCI header fields through PCIe extended capabilities, AER, secondary/link/lane equalization, ACS, multicast, LTR, ARI, L1 PM substates, and an ESM capability bitmap.
- `nbio_nbif_bif_cfg_dev0_epf0_bifcfgdecp`, a `BIF_CFG_DEV0_EPF0_0_*` endpoint function 0 config-space map from vendor/device/class/BAR fields through MSI/MSI-X, PCIe capability, AER, VC, serial-number, and the beginning of the resizable/extended BAR capability block. The chunk ends at `BIF_CFG_DEV0_EPF0_0_PCIE_BAR5_CAP`; the remaining BAR5 control and later endpoint capability masks are in later chunks.

The file is a generated hardware ABI header. This range contains no C functions, structs, variables, allocation, locking, or executable control flow.

## Purpose

`nbio_6_1_sh_mask.h` supplies the bit-level names for NBIO 6.1 registers and PCI configuration-space fields. The matching offset header provides register addresses; this header provides each field's `__SHIFT` and `__MASK` constants so AMDGPU and power-management code can use `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, and direct mask tests without open-coded bit positions.

In this chunk the contract is mostly PCIe config-space presentation. The `PSWUSCFG0_*` family describes a bridge/upstream-port view, while the `BIF_CFG_DEV0_EPF0_0_*` family describes the GPU endpoint PF function's config-space view. Both maps include standard PCI identity/control/status fields, PCIe capability controls, link state, interrupt capabilities, AER logging, and optional extended capabilities that affect platform enumeration, link training, error reporting, virtualization/isolation, and power management.

## Important Macro Families

### Standard PCI Header and Bridge Fields

The `PSWUSCFG0_*` block begins with PCI identity and bridge header fields:

- `PSWUSCFG0_VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, and `BASE_CLASS` expose the enumerated PCI identity and class code.
- `PSWUSCFG0_COMMAND` and `STATUS` define standard enable/status bits such as I/O access, memory access, bus mastering, SERR, interrupt disable, parity, target/master aborts, and capability-list presence.
- Bridge-specific fields include `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, `IO_BASE_LIMIT_HI`, `SECONDARY_STATUS`, and `IRQ_BRIDGE_CNTL`.
- `EXT_BRIDGE_CNTL__IO_PORT_80_EN` adds a vendor/extended bridge-control bit for port-80 decode.

These masks are used to interpret or program the upstream/switch port's PCI bridge window presentation. Incorrect values can change what the OS sees for downstream bus numbering, MMIO/IO decode, VGA behavior, interrupt routing, and secondary bus reset.

### Power Management, PCIe Capability, MSI, and SSID

The early capability-list block defines standard linked-list capability headers and payloads:

- `PSWUSCFG0_VENDOR_CAP_LIST`, `PMI_CAP_LIST`, `PCIE_CAP_LIST`, `MSI_CAP_LIST`, and `SSID_CAP_LIST` define capability IDs and next pointers.
- `PSWUSCFG0_PMI_CAP` and `PMI_STATUS_CNTL` cover power states, PME enable/status, D1/D2 support, auxiliary current, B2/B3 support, and PM data.
- `PSWUSCFG0_PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` define PCIe type, payload/request sizes, relaxed ordering/no-snoop, error enables/status, FLR-like capability on the bridge-side map, link speed/width, ASPM/clock PM controls, retrain/link-disable controls, and link training/status bits.
- `PSWUSCFG0_DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover completion timeout, ARI, atomic operations, ID-based ordering, LTR, OBFF, TLP prefixes, supported link speeds, compliance/equalization controls, and Gen3 equalization status.
- `PSWUSCFG0_MSI_MSG_CNTL`, message address/data fields, and `MSI_MAP_*` expose interrupt message setup and MSI address remapping.
- `PSWUSCFG0_SSID_CAP` and `ADAPTER_ID_W` provide subsystem vendor/device identity fields.

### Vendor, Virtual Channel, Serial Number, AER, and Lane Equalization

The first extended-capability section of `PSWUSCFG0_*` includes:

- Vendor-specific enhanced capability headers and scratch payloads: `PSWUSCFG0_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `HDR`, `SPECIFIC1`, and `SPECIFIC2`.
- Virtual channel capability/control/status: `PCIE_VC_ENH_CAP_LIST`, `PORT_VC_CAP_REG1/2`, `PORT_VC_CNTL`, `PORT_VC_STATUS`, and `PCIE_VC0/VC1_RESOURCE_*`. These define extended VC counts, arbitration table properties, TC-to-VC maps, VC IDs, enable bits, and negotiation-pending status.
- Device serial number capability: `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `DW1`, and `DW2`.
- AER fields: `PCIE_UNCORR_ERR_STATUS`, `UNCORR_ERR_MASK`, `UNCORR_ERR_SEVERITY`, `CORR_ERR_STATUS`, `CORR_ERR_MASK`, `ADV_ERR_CAP_CNTL`, `HDR_LOG0..3`, and `TLP_PREFIX_LOG0..3`. These masks name DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receive overflow, malformed TLP, ECRC, unsupported request, ACS violation, multicast blocked, atomic egress blocked, and TLP-prefix blocked status/mask/severity bits.
- Secondary/link extended capability fields: `PCIE_SECONDARY_ENH_CAP_LIST`, `LINK_CNTL3`, `LANE_ERROR_STATUS`, and per-lane `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`. The lane controls define downstream/upstream TX preset and RX preset-hint fields for all 16 lanes.

### ACS, Multicast, LTR, ARI, L1 PM, and ESM

Later `PSWUSCFG0_*` extended capabilities define isolation, multicast, latency, and equalization-state metadata:

- `PSWUSCFG0_PCIE_ACS_CAP` and `ACS_CNTL` name source-validation, translation-blocking, peer-to-peer redirect, upstream-forwarding, egress-control, and direct-translated P2P capability/control bits. These are security and IOMMU-isolation relevant.
- `PSWUSCFG0_PCIE_MC_*` fields define multicast group count/enable, multicast base address, receive masks, block-all masks, untranslated-block masks, and `PCIE_MC_OVERLAY_BAR0/1`.
- `PSWUSCFG0_PCIE_LTR_CAP` describes max snoop and no-snoop latency values/scales.
- `PSWUSCFG0_PCIE_ARI_CAP` and `ARI_CNTL` define ARI next-function number, function-group capability, and control bits.
- `PCIE_L1_PM_SUB_CAP`, `CNTL`, and `CNTL2` define L1.1/L1.2 support/enables, common-mode restore time, LTR threshold, and power-on timing.
- `PCIE_ESM_*` fields describe an Equalization/ESM vendor capability: headers, minimum time in EI, enable/control for Gen3/Gen4 data rates, and large `PCIE_ESM_CAP_1..7` bitmaps. The bitmaps enumerate supported data-rate steps from 8.0 GT/s through 28.0 GT/s in 0.1 GT/s increments.

### Endpoint Function 0 Config-Space Map

At line 1617 the chunk switches to `BIF_CFG_DEV0_EPF0_0_*`, the endpoint PF function 0 config-space view:

- The standard endpoint header covers vendor/device IDs, command/status, revision/class, cache line/latency/header/BIST, BAR1 through BAR6, subsystem IDs, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- The endpoint PM and PCIe capability blocks mirror many `PSWUSCFG0_*` fields but are endpoint-specific. Notable differences include `BIF_CFG_DEV0_EPF0_0_DEVICE_CNTL__INITIATE_FLR_MASK` rather than the bridge-side retry bit, and endpoint BAR/MSI/MSI-X resources.
- MSI and MSI-X masks include 32-bit and 64-bit message data, mask and pending arrays, MSI-X table size/function mask/enable, table BIR/offset, and PBA BIR/offset.
- Endpoint vendor-specific, VC, serial-number, and AER masks repeat the same capability pattern with `BIF_CFG_DEV0_EPF0_0_` prefixes.
- The chunk ends inside the endpoint resizable/extended BAR capability: `PCIE_BAR_ENH_CAP_LIST`, BAR1 through BAR4 capability/control, and `PCIE_BAR5_CAP`.

## Integration Points

The direct NBIO 6.1 driver consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h`, `nbio_6_1_offset.h`, this shift/mask header, and `nbio_6_1_smn.h`.

Within `nbio_v6_1.c`, masks from this generated header and adjacent NBIO 6.1 generated headers are used to:

- Extract the revision ID from `RCC_DEV0_EPF0_STRAP0`.
- Enable or disable framebuffer access via `BIF_FB_EN__FB_READ_EN_MASK` and `BIF_FB_EN__FB_WRITE_EN_MASK`.
- Program SDMA and IH doorbell ranges via `BIF_SDMA0_DOORBELL_RANGE` and `BIF_IH_DOORBELL_RANGE` fields.
- Toggle the PF doorbell aperture and self-ring aperture via `RCC_PF_0_0_RCC_DOORBELL_APER_EN` and `BIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_CNTL` fields.
- Configure interrupt handling using `INTERRUPT_CNTL` fields.
- Publish HDP flush masks through `nbio_v6_1_hdp_flush_reg`, using `BIF_BX_PF0_GPU_HDP_FLUSH_DONE__CP0..CP9` and `SDMA0/SDMA1`.
- Program ASPM/LTR policy using PCIe link-control masks and endpoint LTR fields, including a locally defined alias for `BIF_CFG_DEV0_EPF0_DEVICE_CNTL2__LTR_EN_MASK`.

Power-management code also includes NBIO 6.1 headers through Vega include files and BACO helpers. For example, Vega BACO tables use `BIF_DOORBELL_CNTL__DOORBELL_MONITOR_EN_MASK`, while several SMU/powerplay paths test `RCC_BIF_STRAP0__STRAP_PX_CAPABLE_MASK` for BACO/MACO capability. Those specific strap and doorbell fields are outside this chunk, but they share the same generated-header contract.

## Control Flow

There is no local control flow in this header. Runtime flow is external:

1. The AMDGPU ASIC initialization path selects the NBIO 6.1 implementation.
2. Driver code includes the offset/default/shift-mask headers for this hardware generation.
3. Register helpers read NBIO/PCIe registers, combine values with the `__MASK` and `__SHIFT` constants here through `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, or `WREG32_FIELD15`, and write updated values back.
4. Hardware or PCI config-space presentation reflects the selected identity, capability, link, interrupt, error-reporting, power-management, and BAR settings.

For status and error registers such as PCI status, device status, AER status, VC status, and link status, the caller determines whether the field is read-only status, write-one-to-clear status, or read/modify/write control according to PCIe/NBIO hardware semantics. The header only names the bits.

## State and Persistence Behavior

The header stores no software state. It names persistent hardware/configuration state in NBIO registers and PCIe config-space images. That state persists until changed by PCI enumeration/config writes, AMDGPU register writes, firmware/SMU actions, function reset/FLR, link retraining, BACO or other power transitions, ASIC reset, or strap/config reload.

Important state represented in this chunk includes PCI identity/class/subsystem IDs, command enables, bus/window decode, bridge control, PM state and PME status, PCIe payload and read-request sizes, error reporting enables/status, link speed/width/training state, MSI/MSI-X configuration, VC/TC mappings, AER header/TLP logs, per-lane equalization presets, ACS isolation controls, multicast maps, LTR/L1 substate timing, ESM data-rate capability bits, endpoint BAR sizing/control, and resizable BAR capability metadata.

Many fields are shared across ownership boundaries. PCI core enumeration may program command, BAR, MSI/MSI-X, and link fields. Platform firmware and straps influence capability presentation. AMDGPU configures selected NBIO policies for doorbells, HDP flushes, ASPM/LTR, and interrupt behavior. Hypervisor/IOMMU correctness can depend on ACS/ARI/MSI/BAR fields, especially for passthrough and SR-IOV-related paths in adjacent chunks.

## Dependencies

This generated header depends on the NBIO 6.1 hardware register specification and must stay synchronized with:

- `nbio_6_1_offset.h` for register names, address offsets, and base indices.
- `nbio_6_1_default.h` for reset/default values.
- `nbio_6_1_smn.h` and local SMN constants for direct PCIE/SMN accesses used by `nbio_v6_1.c`.
- AMDGPU SOC15 and PCIE register helpers: `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.
- PCI/PCIe semantics for config headers, bridges, PM, MSI/MSI-X, AER, VC, ACS, multicast, LTR, ARI, L1 PM substates, link equalization, and resizable BAR capabilities.

## Risks

- A wrong shift or mask compiles cleanly but targets the wrong hardware bit. In this chunk that can alter PCI enumeration, memory/IO decode, bus mastering, link training, MSI delivery, AER handling, ACS isolation, LTR/ASPM behavior, or BAR sizing.
- Similar field names exist in both `PSWUSCFG0_*` and `BIF_CFG_DEV0_EPF0_0_*` namespaces. Reusing a bridge-port mask on the endpoint function, or the endpoint mask on the bridge map, can silently program the wrong config-space image.
- Some controls are capability-presentation or strap-derived fields rather than ordinary runtime knobs. Treating them as freely mutable can conflict with platform firmware or present inconsistent PCIe capabilities to the OS.
- Status, mask, severity, and control registers often sit next to one another with nearly identical field names. Mixing `*_STATUS`, `*_MASK`, and `*_SEVERITY` macros can lose diagnostics or change interrupt/error behavior instead of observing it.
- AER header/TLP-prefix logs are diagnostic state. Full-register writes without respecting hardware clear semantics may erase evidence needed for PCIe error triage.
- ACS and ARI fields affect peer-to-peer routing and function enumeration. Incorrect settings can break IOMMU isolation, passthrough, multi-function enumeration, or peer DMA behavior.
- LTR/L1 PM/ESM/link equalization fields are link-stability sensitive. Bad timing, threshold, preset, or data-rate capability bits can manifest as training failures, ASPM hangs, or power-management regressions.
- The chunk boundary splits the endpoint BAR capability block after `BIF_CFG_DEV0_EPF0_0_PCIE_BAR5_CAP`; merge/reconciliation must combine later chunks before drawing final conclusions about all endpoint BAR controls.

## Test Signals

Useful validation is mostly build and hardware/integration oriented:

- Kernel build coverage for NBIO 6.1 users verifies that generated names still match `nbio_v6_1.c`, Vega powerplay include paths, and SMU/BACO users.
- Boot on NBIO 6.1 ASICs should show expected PCI vendor/device/revision/class/subsystem IDs, BAR layout, command bits, capability list, link speed/width, MSI/MSI-X capability, and AER capability via `lspci -vv`.
- Doorbell and interrupt smoke tests should exercise SDMA/IH doorbell programming, MSI/MSI-X delivery, and absence of unexpected doorbell interrupt status.
- HDP flush tests should cover CP0 through CP9 and SDMA0/SDMA1 flush request/done masks through the AMDGPU HDP flush framework.
- ASPM/LTR validation should compare link stability, LTR enable state, L1 substate behavior, and suspend/resume across systems with and without an LTR-capable path.
- PCIe AER injection or platform error logs should confirm correct uncorrectable/correctable error status, mask, severity, header-log, and TLP-prefix-log interpretation.
- IOMMU/passthrough and peer-to-peer DMA testing should validate ACS/ARI-related capability presentation and control behavior.
