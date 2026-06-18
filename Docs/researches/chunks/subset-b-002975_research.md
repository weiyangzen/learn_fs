# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 34357-36823

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header slice. It defines C preprocessor constants for bit positions and bit masks in several NBIO/PCIe configuration decode blocks. The range begins at the tail of the PCIe performance counter definitions for `TXCLK10`, then covers:

- `nbio_pcie0_pswuscfg0_cfgdecp`, with upstream-switch/bridge configuration fields prefixed `PSWUSCFG0_*`.
- `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, with root-complex bridge and slot capability/control/status fields.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, with endpoint PF0 PCI configuration space and PCIe extended capability fields.
- The beginning of `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`, with virtual-function 0 PCI configuration and early PCIe capability fields.

The chunk is declarative only. It contains no functions, structs, enums, executable control flow, allocations, locking, initialization routines, or direct register access. Its interface is the macro namespace consumed by AMDGPU code and generated register helpers.

## Purpose

The macros give symbolic layouts for NBIO 4.3.0 PCIe/NBIF registers so driver code can decode or compose register values without open-coded bit constants. Each register field generally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The companion offset header, `nbio_4_3_0_offset.h`, provides addresses and base indices. This file provides field extraction and update metadata used by register helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, and SOC15/PCIE read-modify-write paths.

This range is concentrated around PCIe configuration exposure: bus numbering, bridge windows, standard PCI command/status, BARs, power management, MSI/MSI-X, PCIe device/link controls, AER, resizable BAR, DPA, ACS, PASID, SR-IOV, link equalization, lane margining, and high-speed link capability status up to 32 GT/s.

## Address Blocks and Register Coverage

The first few lines complete PCIe performance counter macros:

- `PCIE_PERF_CNTL_TXCLK10` selects two performance events and exposes counter-full status bits.
- `PCIE_PERF_COUNT0_TXCLK10` and `PCIE_PERF_COUNT1_TXCLK10` expose full 32-bit counter values.

`nbio_pcie0_pswuscfg0_cfgdecp` covers a PCI-to-PCI bridge style configuration block:

- `PSWUSCFG0_SUB_BUS_NUMBER_LATENCY` fields for primary, secondary, subordinate bus numbers, and secondary latency timer.
- `PSWUSCFG0_IO_BASE_LIMIT`, `PSWUSCFG0_MEM_BASE_LIMIT`, and `PSWUSCFG0_PREF_BASE_LIMIT` fields for bridge I/O, memory, and prefetchable memory windows.
- Upper 32-bit prefetchable base/limit and high I/O base/limit fields.
- `PSWUSCFG0_SECONDARY_STATUS` error and status bits.
- SSID capability list and subsystem vendor/device identity fields.

`nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` mirrors bridge/root-complex configuration:

- `BIF_CFG_DEV0_RC_SUB_BUS_NUMBER_LATENCY`, I/O base/limit, memory base/limit, prefetchable base/limit, upper base/limit, and high I/O base/limit.
- PCIe slot capability, control, and status registers, including hotplug, attention/power indicators, presence detect, MRL sensor, power fault, command-completed interrupt, electromechanical interlock, and physical slot number fields.
- Slot capability/control/status version 2 placeholder or reserved fields.
- Root-complex SSID capability list and subsystem ID fields.

`nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` is the dominant part of the chunk. It covers PF0 config-space and extended capability fields:

- Basic PCI header: vendor/device IDs, command, status, revision, programming interface, class/subclass, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, vendor capability, and writeable adapter ID.
- Power management: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL`, including PME support/status, power state, data select/scale, B2/B3 support, and bus power enable.
- PCIe base capability: `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X: MSI control, 32-bit and 64-bit message address/data layout, extended message data, mask and pending bits, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific extended capability and virtual-channel capability/resource fields.
- Device serial number fields.
- PCIe Advanced Error Reporting: uncorrectable error status, mask, severity, correctable error status/mask, AER capability/control, TLP header logs, and TLP prefix logs.
- Resizable BAR controls for BAR1 through BAR6.
- Power budget and Dynamic Power Allocation capability/control/status/substate allocation registers.
- Secondary PCIe extended capability, link control 3, lane error status, and per-lane 8 GT/s equalization controls for lanes 0 through 15.
- Access Control Services capability/control.
- PASID capability/control.
- Multicast capability/control/address/receive/block registers.
- Latency Tolerance Reporting capability.
- ARI capability/control.
- SR-IOV capability/control/status and VF resource fields.
- Data Link Feature capability/status.
- PHY 16 GT/s capability/control/status, parity mismatch status, and per-lane 16 GT/s equalization control for lanes 0 through 15.
- PCIe lane margining capability plus per-lane margining control/status for lanes 0 through 15.
- VF resizable BAR capability/control for BAR1 through BAR6.
- 32 GT/s link capability/control/status.

`nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp` begins near the end of the range:

- VF0 basic PCI header fields from vendor/device IDs through max latency.
- VF0 PCIe capability list, `PCIE_CAP`, device capability/control/status, link capability/control/status.
- The first line of `BIF_CFG_DEV0_EPF0_VF0_DEVICE_CAP2` starts at the chunk boundary, so the VF0 PCIe capability block is incomplete in this chunk.

## Important APIs, Types, and Functions

There are no C functions, types, or callable APIs in this chunk. The significant interface is the generated macro set. Important macro families include:

- `*_COMMAND__*` and `*_STATUS__*` for PCI enablement and reporting bits: I/O access, memory access, bus master, special cycles, parity response, SERR, fast back-to-back, interrupt disable, capability list presence, abort reporting, parity error, and detected parity.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR`, `*_PCIE_BAR*_CAP`, and `*_PCIE_BAR*_CNTL` for BAR layout, ROM enablement, resizable BAR supported sizes, selected size, BAR index, and total BAR count.
- `*_SUB_BUS_NUMBER_LATENCY`, `*_IO_BASE_LIMIT*`, `*_MEM_BASE_LIMIT`, and `*_PREF_BASE_LIMIT*` for bridge bus numbering and decode windows.
- `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` for hotplug and slot events. These fields are particularly relevant to bridge/root-complex behavior.
- `*_DEVICE_CAP*`, `*_DEVICE_CNTL*`, and `*_DEVICE_STATUS*` for payload size, read request size, relaxed ordering, no-snoop, auxiliary power, FLR, completion timeout, LTR enable, emergency power reduction, atomic operations, ID-based ordering, 10-bit tags, and error reporting.
- `*_LINK_CAP*`, `*_LINK_CNTL*`, and `*_LINK_STATUS*` for supported/current link speed, link width, ASPM, retraining, link disable, common clock, clock power management, autonomous bandwidth, DRS, equalization state, and high-speed link features.
- `*_MSI_*` and `*_MSIX_*` for interrupt delivery programming and masking.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, `*_PCIE_ADV_ERR_CAP_CNTL`, `*_PCIE_HDR_LOG*`, and `*_PCIE_TLP_PREFIX_LOG*` for PCIe AER status, mask, severity, ECRC, first-error pointer, multi-header recording, and diagnostic captured TLP data.
- `*_PCIE_DPA_*`, `*_PCIE_PWR_BUDGET_*`, and `*_PCIE_LTR_*` for PCIe power-management reporting and latency tolerance contracts.
- `*_PCIE_ACS_*`, `*_PCIE_PASID_*`, `*_PCIE_ARI_*`, and `*_PCIE_SRIOV_*` for isolation, address-space IDs, alternate routing-ID interpretation, and virtualization resources.
- `*_PCIE_LANE_*_EQUALIZATION_CNTL`, `*_LANE_*_MARGINING_LANE_CNTL`, and `*_LANE_*_MARGINING_LANE_STATUS` for per-lane signal integrity tuning and diagnostics.
- `*_LINK_CAP_32GT`, `*_LINK_CNTL_32GT`, and `*_LINK_STATUS_32GT` for PCIe 5.0 class 32 GT/s equalization and modified training-sequence behavior.

## Control Flow

This header range has no runtime control flow. Inclusion is controlled by the file-level header guard defined near the start of `nbio_4_3_0_sh_mask.h`.

The expected consumer flow is inferred from AMDGPU generated register conventions:

1. Include `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`.
2. Select a register address from the offset header, for example a `cfgBIF_CFG_DEV0_EPF0_*` or related NBIO address.
3. Read the register through the appropriate AMDGPU access path, such as SOC15/NBIO helpers, PCIE config access, or firmware/SMU code that includes these headers.
4. Extract a field with the `*_MASK` and `*_SHIFT` constants, or compose a new register value with the same constants.
5. Write the new value only when the target field is a writable control bit and surrounding bits have been preserved.

The range is used as a compile-time description of hardware layout. Any behavioral sequencing, delays, reset ordering, PCI enumeration, SR-IOV provisioning, interrupt setup, or error recovery is implemented elsewhere.

## State and Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware state held in NBIO and PCIe configuration registers.

Several fields represent long-lived configuration state until reset, function-level reset, or PCI reconfiguration:

- Bridge bus numbers and decode windows.
- `COMMAND` control bits such as memory access, I/O access, bus mastering, SERR enable, and interrupt disable.
- BAR/ROM mappings and resizable BAR size selections.
- Power management control bits such as power state, PME enable/status, LTR enable, DPA substate control, and power budget selection.
- MSI/MSI-X enablement, MSI address/data fields, mask bits, and MSI-X table/PBA descriptors.
- PCIe device/link controls such as maximum payload/read request, relaxed ordering, no-snoop, completion timeout, FLR initiate, link retrain/disable, autonomous speed/width controls, and equalization controls.
- AER masks/severity and ECRC generation/checking enables.
- ACS/PASID/ARI/SR-IOV controls, including VF enablement, VF migration, memory-space enablement, VF BARs, and system page size.

Other fields are status or diagnostics updated by hardware and sometimes sticky or write-one-to-clear according to PCIe semantics:

- PCI status, secondary status, slot status, device status, and link status.
- AER correctable and uncorrectable status, first-error pointer, header logs, and prefix logs.
- Lane error status, 8 GT/s/16 GT/s/32 GT/s equalization status, parity mismatch status, DRS messages, and margining lane status.
- MSI pending bits and PME status.

Because the macros do not encode access permissions, consumers must know from the PCIe specification and hardware register database whether a field is read-only, read/write, clear-on-write, sticky, reserved, or hardware-updated.

## Dependencies and Integration Points

This chunk depends conceptually on nearby generated register headers:

- `nbio_4_3_0_offset.h` supplies addresses and base indices for the registers whose fields are described here.
- `nbio_4_3_0_default.h`, when present for the same register database, supplies default/reset values used for comparison or initialization.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` naming convention for field extraction and read-modify-write updates.

Direct include integration found in this tree includes SMU 13 code paths, such as `smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c`, which include both `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`. The field names also align with broader AMDGPU NBIO/PCIe handling used by NBIO, power-management, RAS, PCIe, and virtualization code.

Subsystem integration points include:

- Linux PCI and PCIe enumeration/configuration for command/status, bridge windows, capabilities, BARs, link controls, slot state, AER, MSI/MSI-X, ACS, PASID, ARI, and SR-IOV.
- AMDGPU power-management and SMU code that needs NBIO/PCIe capability fields, LTR, DPA, power budget, or BACO-adjacent PCIe state.
- AMDGPU RAS and PCIe recovery code through AER status/mask/severity and TLP log fields.
- IOMMU and process-address-space integration through PASID fields and ATS/PASID-adjacent PCIe capability policy.
- SR-IOV PF/VF orchestration through PF0 SR-IOV controls and the VF0 configuration-space window started at the end of the chunk.
- Hardware validation and debug tooling through per-lane equalization, margining, lane error, and high-speed link status fields.

## Risks and Edge Cases

- The header is generated and highly repetitive. A single incorrect shift or mask can make all downstream field extraction or read-modify-write logic wrong while still compiling.
- This chunk starts and ends at arbitrary boundaries. It begins mid `PCIE_PERF_CNTL_TXCLK10` and ends immediately after the first `BIF_CFG_DEV0_EPF0_VF0_DEVICE_CAP2` shift definition, so final reconciliation must not treat either boundary as a complete register family.
- Many fields have standard PCIe names but hardware-specific decode locations. Mixing macros from NBIO 4.3.0 with offsets from another NBIO generation can produce silent register corruption.
- Address-like fields such as BARs, ROM BARs, MSI-X table offsets, PBA offsets, bridge windows, and resizable BAR controls contain encoded low bits. Treating them as plain addresses can lose type, enable, BIR, or size metadata.
- Status, mask, and severity macros in the AER block have nearly identical names. Confusing these can clear the wrong status, suppress error reporting, or misclassify fatal and non-fatal errors.
- Some status bits may be sticky or clear-on-write while this header only exposes bit layout. Read-modify-write sequences that write back a stale status word can accidentally clear events.
- Link-control, compliance, retraining, autonomous speed/width, and equalization fields can affect PCIe reachability. Incorrect writes may trigger link retrains, force compliance behavior, or degrade width/speed.
- ACS, PASID, ARI, and SR-IOV controls interact with isolation and IOMMU policy. Enabling a field purely because the bit exists can break DMA translation, PCIe routing, VF enumeration, or peer-to-peer isolation.
- Per-lane equalization and margining fields repeat for lanes 0 through 15. Copy/paste or generation drift in one lane is hard to detect by manual review because the only expected textual difference is the lane number.
- Literal widths vary between byte, word, and dword registers, while masks use `L` suffixes. Consumers need correct access width and no implicit truncation.

## Test Signals

Useful validation signals for this chunk:

- Build AMDGPU code that includes `nbio_4_3_0_sh_mask.h`; malformed or missing macros should fail compile-time references.
- Run generated-register consistency checks comparing this range against the authoritative NBIO 4.3.0 register database and the matching `nbio_4_3_0_offset.h`.
- Pattern-check repeated families: BAR1 through BAR6, lane 0 through 15 equalization, lane 0 through 15 margining, VF resizable BAR1 through BAR6, and PF0 versus VF0 common PCIe capability fields.
- Verify bridge and slot fields against PCI config dumps from hardware using `lspci -vv` or driver debug output: bus numbers, bridge windows, slot capabilities, hotplug bits, and secondary status should decode as expected.
- Exercise PCIe capability decoding on supported NBIO 4.3.0 devices: payload/read request sizes, FLR, completion timeout, LTR, link width/speed, ASPM, DRS, 16 GT/s and 32 GT/s status.
- Test MSI and MSI-X enable, masking, pending, table, and PBA behavior during interrupt setup, teardown, suspend/resume, and reset.
- Use AER injection or observed hardware errors to validate uncorrectable/correctable status, mask, severity, first-error pointer, ECRC bits, header logs, and prefix logs.
- Validate SR-IOV lifecycle: enable VFs, enumerate VF0, program VF BARs, perform VF FLR, and confirm PF0 SR-IOV control/status fields return expected values after teardown.
- Validate ACS/PASID/ARI behavior in IOMMU-enabled configurations by checking device isolation, PASID width/enablement, and ARI function discovery.
- For hardware validation environments, use link equalization and margining diagnostics to confirm per-lane fields map to the expected physical lanes and do not drift across lane indices.
