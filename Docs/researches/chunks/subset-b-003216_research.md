# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_sh_mask.h lines 136076-138528

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.2 register field mask header. It defines preprocessor constants for bit shifts and masks used with PCIe configuration and extended-capability registers under NBIF device 0 endpoint functions.

The span starts at the tail of `BIF_CFG_DEV0_EPF1_1` SR-IOV/GPUIOV definitions, covering VF resizable BAR6 and a large vendor-specific GPUIOV area. It then switches at `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` to the full `BIF_CFG_DEV0_EPF2_1` PCI/PCIe function map, including standard config space, power management, MSI/MSI-X, AER, resizable BAR, power budgeting, DPA, ACS, PASID, ARI, TPH requester, and all 64 TPH steering-table entries. The final section begins `addressBlock: nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` and covers `BIF_CFG_DEV0_EPF3_1` from standard config space through the start of AER uncorrectable error mask definitions.

These definitions contain no executable code. They are an ASIC-specific hardware ABI: paired offset headers identify register addresses, while this file identifies field positions inside each register dword or word.

## Covered Register Areas

- `BIF_CFG_DEV0_EPF1_1` VF resizable BAR6: `VF_BAR_SIZE_SUPPORTED`, `VF_BAR_INDEX`, `VF_BAR_TOTAL_NUM`, selected `VF_BAR_SIZE`, and supported upper size bits.
- `BIF_CFG_DEV0_EPF1_1` GPUIOV vendor-specific capability: capability list/header fields, SR-IOV shadow enable/count, interrupt enable/status bits for GFX, UVD, UVD1, VCE, and HVVM mailbox events, soft PF FLR control, mailbox dwords, context sizing, total framebuffer accounting, scheduler offsets, LFB region bounds, and P2P-over-XGMI enables.
- `BIF_CFG_DEV0_EPF1_1` per-VF framebuffer records: `VF0_FB` through `VF30_FB`, each with size and offset halves.
- `BIF_CFG_DEV0_EPF1_1` scheduler descriptors: UVD, VCE, GFX, and UVD1 scheduler dwords `DW0..DW8`, with fields for scheduler mode, world-switch settings, time-slice controls, idle counters, engine reset controls, boot/submission messages, VF grant/control pairs, and related status/control bits.
- `BIF_CFG_DEV0_EPF2_1` standard PCI config fields: vendor/device IDs, command/status, revision/class code bytes, cache/latency/header/BIST, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, legacy interrupt fields, min grant, max latency, vendor capability list, and writable adapter ID mirror.
- `BIF_CFG_DEV0_EPF2_1` PCIe and power-management capability fields: `PMI_CAP`, `PMI_STATUS_CNTL`, `SBRN`, `FLADJ`, `DBESL_DBESLD`, PCIe capability header, device capability/control/status, link capability/control/status, and PCIe capability version-2 device/link registers.
- `BIF_CFG_DEV0_EPF2_1` interrupt configuration: MSI and MSI-X capability list entries, MSI message control, 32-bit and 64-bit MSI address/data/mask/pending registers, MSI-X table descriptor, and MSI-X PBA descriptor.
- `BIF_CFG_DEV0_EPF2_1` PCIe extended capabilities: vendor-specific header/scratch registers, Advanced Error Reporting status/mask/severity/logging, resizable BAR controls for BAR1 through BAR6, power budget, dynamic power allocation and substate power allocation, ACS, PASID, ARI, and TPH requester controls.
- `BIF_CFG_DEV0_EPF2_1` TPH steering table entries: `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63`, each splitting one register into lower and upper 8-bit steering-tag entries.
- `BIF_CFG_DEV0_EPF3_1` standard PCI/PCIe function fields: standard config space, power-management capability, PCIe device/link capability/control/status, version-2 capability/control/status registers, MSI/MSI-X capability state, vendor-specific capability header/scratch registers, AER capability list, and AER uncorrectable error status. The chunk ends immediately after the `PCIE_UNCORR_ERR_MASK` comment, before its field definitions.

## Important APIs, Types, and Functions

This chunk defines no functions, structs, enums, variables, or inline helpers. Its public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register position.

The practical consumers are AMDGPU register and field helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32*`, `WREG32*`, and SOC15/NBIO-specific accessors. Consumers combine these macros with the matching `regBIF_CFG_DEV0_EPF*_1_*` offsets from `nbio_7_2_0_offset.h`; using a correct shift/mask with the wrong endpoint-function offset would decode or program unrelated hardware state.

## Control Flow

There is no runtime control flow in this header. The effective control flow is compile-time substitution:

1. AMDGPU code selects a NBIO 7.2 register offset for an EPF1, EPF2, or EPF3 register.
2. It reads a hardware/configuration-space value or prepares a new dword/word value.
3. It uses the associated `__SHIFT` and `_MASK` constants to extract a field or compose a read-modify-write update.
4. Hardware owns the resulting behavior, such as interrupt delivery, mailbox handshakes, BAR sizing, power-state transitions, link training, AER reporting, or SR-IOV resource partitioning.

Within this chunk, the only sequencing encoded by the source order is register-map order: EPF1 GPUIOV continuation, EPF2 full function map, then EPF3 partial function map.

## State and Persistence Behavior

The file itself has no mutable state and persists nothing. The macros name hardware-backed state with several different lifetimes:

- Capability and identity fields such as vendor/device IDs, class codes, PCIe capability bits, supported link speeds, BAR-size support, AER capability bits, ACS/PASID/ARI/TPH capabilities, power-budget data, and DPA capability are normally read-only or firmware/strap-derived.
- Mutable configuration fields include PCI command bits, power state and PME enable, PCIe device/link controls, completion-timeout control, MSI/MSI-X enable and masking, resizable BAR selected sizes, AER masks/severity, ACS/PASID/ARI/TPH controls, DPA substate control, GPUIOV interrupt enables, mailbox transmit/receive bits, soft PF FLR, scheduler control dwords, P2P-over-XGMI enable masks, and VF framebuffer size/offset records.
- Status and diagnostic fields include PCI status, device/link status, MSI pending bits, GPUIOV interrupt status, mailbox acknowledge/valid bits, framebuffer-consumed accounting, DPA status, AER uncorrectable/correctable status, AER header logs, and TLP prefix logs. Some of these may be latched, clear-on-write, or reset by FLR/GPU reset according to PCIe/NBIO hardware rules.
- Persistence across driver reload, suspend/resume, hot reset, function-level reset, PF reset, or GPU reset is not described by this header. The macros only encode layout, not reset values, access permissions, ordering requirements, or side effects.

## Dependencies

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`: provides the matching register offsets and base-index macros.
- AMDGPU SOC15/NBIO register access code: supplies the read/write and bitfield helper machinery that consumes generated `__SHIFT` and `_MASK` names.
- PCI/PCIe architectural definitions: the field names mirror standard PCI config space, power management, MSI/MSI-X, PCIe capability, Advanced Error Reporting, ACS, PASID, ARI, TPH, DPA, power budgeting, BAR resizing, and link-status concepts.
- AMD NBIO 7.2 hardware specification: the generated numeric masks and shifts must match the ASIC register database for this NBIO generation.

## Integration Points

- The GPUIOV EPF1 definitions are integration points for SR-IOV virtualization support: VF enable/count shadowing, per-VF framebuffer allocation, hypervisor-to-virtual-machine mailbox state, VF/PF transmit acknowledgements and receive-valid bits, scheduler dwords for graphics/video engines, P2P-over-XGMI policy, and FLR recovery.
- The EPF2 and EPF3 definitions mirror PCIe functions exposed by device 0. They support enumeration identity, BAR programming, command/status handling, power management, MSI/MSI-X setup, link capability reporting, link control/status inspection, AER configuration, and optional PCIe services such as ACS, PASID, ARI, DPA, power budgeting, and TPH.
- The TPH steering-table macros are emitted as 64 individually named registers. Callers that treat the table as indexed data must map each index to explicit register symbols or use generated access code; this header does not provide an array abstraction.
- AER fields integrate with kernel PCIe error reporting and GPU reset paths. Mismatched masks can hide, misclassify, or accidentally clear link/protocol errors.
- Resizable BAR and VF BAR fields integrate with memory aperture sizing and SR-IOV resource allocation. Width or prefix mistakes can alter address decoding and framebuffer partitioning.

## Risks and Edge Cases

- The chunk starts mid-family: `BIF_CFG_DEV0_EPF1_1_PCIE_VF_RESIZE_BAR5_CNTL` masks appear before the first visible register comment, while the matching BAR5 shifts were in the previous chunk. Merge logic should preserve this boundary.
- The chunk ends at the `BIF_CFG_DEV0_EPF3_1_PCIE_UNCORR_ERR_MASK` comment before any mask fields for that register. The following chunk must supply those definitions.
- Prefixes are highly similar: `EPF1_1`, `EPF2_1`, and `EPF3_1` share many field names but point at different function maps. Copying a mask across prefixes can compile cleanly while targeting the wrong hardware function.
- GPUIOV mailbox dwords pack per-VF acknowledgement and valid bits densely. Off-by-one VF indexing or confusing transmit acknowledgement with receive-valid status would break PF/VF handshake behavior.
- Scheduler dwords for UVD, VCE, GFX, and UVD1 are structurally similar but not interchangeable. A field helper applied to the wrong engine scheduler register may alter reset, time-slicing, or VF scheduling policy.
- Full-width masks such as BARs, MSI masks, AER logs, TLP prefix logs, scratch registers, and TPH table halves should be treated as values, not boolean flags.
- Status and error fields can have write-one-to-clear or other side effects. Full-register writes using masks from PCI status, AER status, MSI pending, or GPUIOV interrupt status definitions may acknowledge or clear diagnostics unintentionally.
- The header does not encode access width. Many fields are byte or word-sized within PCI config space, but AMDGPU register helpers may still access dwords; callers must preserve unrelated fields during read-modify-write operations.

## Test Signals

- Build signal: AMDGPU NBIO 7.2 users of these macros compile with the matching `nbio_7_2_0_offset.h` and do not report undefined field names at EPF1/EPF2/EPF3 boundaries.
- Static validation signal: generated masks and shifts should match the NBIO 7.2 register database, especially for dense GPUIOV mailbox bits, per-VF framebuffer entries, scheduler dwords, repeated BAR controls, and the 64 TPH steering-table registers.
- Enumeration signal: `lspci -vv`, kernel PCI resource logs, and DRM/amdgpu init logs should show coherent device identity, class, BAR sizing, MSI/MSI-X capability, power-management capability, and PCIe link capability for EPF2/EPF3 functions.
- Virtualization signal: SR-IOV enablement, VF enumeration, mailbox traffic, per-VF framebuffer allocation, GPU reset/FLR paths, and engine scheduling under VF load exercise the GPUIOV fields in the EPF1 portion.
- Runtime error signal: kernel AER messages, link retraining reports, completion-timeout events, MSI/MSI-X interrupt failures, PCIe link-speed/width changes, suspend/resume, hot reset, and GPU reset stress can reveal wrong masks for mutable PCIe, interrupt, power, and AER fields.
