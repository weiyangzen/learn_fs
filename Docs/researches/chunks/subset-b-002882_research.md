# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_sh_mask.h lines 12255-14840

## Purpose

This chunk is generated AMDGPU NBIF 6.3.1 register bitfield metadata. It contains no executable C code, structs, enums, or callable APIs. Its exported interface is a dense set of C preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU register helpers to pack and decode 32-bit PCIe/NBIO configuration and MMIO register values.

The range starts in the middle of `BIF_CFG_DEV0_EPF2_PCIE_UNCORR_ERR_MASK`, so the first complete content is the rest of EPF2 Advanced Error Reporting policy and capability fields. It then defines the tail of EPF2 PCIe extended capabilities, a full `BIF_CFG_DEV0_EPF3_*` PCI configuration-space function view, several RCC endpoint/downstream/PFC NBIF control blocks, and the beginning of the `nbif_pciemsix_0_usb_MSIXTDEC` MSI-X table through `PCIEMSIX_VECT54_ADDR_LO`.

Although the repository path is under `distributed-fs/ceph-client`, this is Linux AMD GPU driver hardware metadata, not Ceph filesystem logic. The constants are paired with `nbif_6_3_1_offset.h` register addresses and consumed by AMDGPU NBIO/NBIF code through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and PCI config-space accessors.

## Important APIs, Types, And Macro Families

There are no functions or runtime types in this chunk. The important API is the generated naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the register mask for that field.

The `BIF_CFG_DEV0_EPF2_PCIE_*` tail covers PCIe AER and optional endpoint capabilities for endpoint function 2. It includes uncorrectable error mask and severity bits for malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, AtomicOp egress blocking, TLP-prefix blocking, and poisoned-TLP egress blocking. It also defines correctable error status/mask bits, AER capability/control fields, four TLP header-log dwords, four TLP-prefix-log dwords, enhanced BAR capability/control registers for BAR1 through BAR6, power-budget capability data selection/value fields, Dynamic Power Allocation capability/status/control/substate power allocation fields, ACS capability/control bits, PASID capability/control bits, and ARI capability/control bits.

The `BIF_CFG_DEV0_EPF3_*` block is a full PCI configuration-space map for endpoint function 3. It starts with standard PCI identity/header fields: vendor/device IDs, command/status, revision/interface/subclass/base class, cache line, latency, header type, BIST, six BARs, CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and min/max latency. It then exposes legacy and PCIe capability structures: vendor capability, power-management capability and status/control, USB-related SBRN/FLADJ/DBESL fields, PCIe capability/device/link registers, MSI and MSI-X capability fields, vendor-specific enhanced capability fields, AER status/mask/severity/header-log/prefix-log fields, enhanced BAR controls, power-budgeting fields, DPA fields, ACS fields, PASID fields, and ARI fields.

The `RCC_DEV0_1_*` block describes root-complex/common control fields for device 0 instance 1: VDM support, bus control, feature-control miscellaneous flags, device and common link controls, endpoint requester-ID restore, LTR light-switch control, multi-host arbitration control, and margining parameter controls. These fields are NBIF-specific rather than generic PCI config-space header fields.

The `RCC_EP_DEV0_1_*` block describes endpoint-side PCIe controls and status: scratch, endpoint control, interrupt control/status, RX control, bus/config control, TX LTR control, strap registers, function-0 DPA capability/control/substate allocation mirrors, PME control, reserved register, TX control, requester-ID, error control, RX control, and link speed control.

The `RCC_DWN_DEV0_1_*` and `RCC_DWNP_DEV0_1_*` blocks describe downstream-port controls: reserved/scratch/control/config/RX/bus/strap registers, downstream error/RX/link controls, PCIeP strap misc, and LTR message information received from the endpoint. These are used to tune or observe the internal PCIe path between NBIF root-complex/downstream pieces and endpoint-facing logic.

The `RCC_PFC_AMDGFX_*` and `RCC_PFC_AMDGFXAZ_*` blocks provide per-function controller state for graphics and audio/azalia-related functions. They include LTR control, PME restore fields, sticky restore registers 0 through 5, and auxiliary power control fields.

The `PCIEMSIX_VECT*` block begins the USB MSI-X table metadata. For each vector, the same four register families appear: `ADDR_LO` with message address low bits shifted by two and masked by `0xFFFFFFFC`, `ADDR_HI` with full 32-bit high address, `MSG_DATA` with full 32-bit data, and `CONTROL` with the per-vector mask bit. This chunk covers vector 0 through vector 53 completely and stops at the shift macro for `PCIEMSIX_VECT54_ADDR_LO`, so the next chunk owns the remaining mask and later vectors.

## Control Flow And Runtime Use

This header has no runtime control flow. Its behavior is pure preprocessing: included C files name a register and field, and macro expansion supplies constants used for bit masking and shifting.

The direct NBIF 6.3.1 implementation is `drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, which includes this shift/mask header and the matching offset header. That file primarily uses other NBIF register families from the same generated header set for revision ID, memory-controller access enablement, doorbell range programming, interrupt handling, HDP flush masks, register remapping, LTR/ASPM programming, and RAS ATHUB interrupt setup. The PCIe config-space and MSI-X table macros in this chunk are part of the same generated register contract even if many are not touched by the narrow visible init path.

Typical consumer flow is:

1. Driver code selects a register offset from `nbif_6_3_1_offset.h` or a PCI configuration-space accessor.
2. It reads an existing 32-bit value when preserving unrelated fields is required.
3. It calls `REG_SET_FIELD` or manually uses the `__SHIFT`/`_MASK` pair to update one field.
4. It writes the result with SOC15 MMIO helpers, PCI config helpers, or another NBIO/NBIF access path.
5. For status paths, it reads a register and uses `REG_GET_FIELD` or equivalent masking to decode hardware-owned state.

The header does not encode sequencing rules. It does not say when AER status is write-one-to-clear, when MSI-X table entries are safe to rewrite, when DPA/ASPM/LTR fields are firmware-owned, or when SR-IOV/virtualization-sensitive fields should be restricted to PF-only paths. Those rules live in the PCIe spec, AMD hardware specs, firmware protocols, and driver call sites.

## State And Persistence Behavior

The header itself has no storage, persistence, allocations, I/O, locks, or side effects. It only contributes constants to compiled code.

The hardware state described by the macros is persistent device register state until reset, power transition, firmware reprogramming, PCI core action, or explicit driver writes. Configuration-like state includes PCI command bits, BAR sizing/control, MSI/MSI-X capability programming, AER masks and severity policy, DPA substate power allocation, ACS/PASID/ARI controls, RCC link and bus controls, LTR/PME restore values, and PFC sticky restore values.

Status-like state includes PCI status bits, PCIe device/link status, correctable and uncorrectable AER status, AER header/prefix logs, DPA status, RCC endpoint interrupt status, downstream link/status fields, LTR message information, and MSI-X per-vector mask state. Some fields in these status registers may be sticky or write-one-to-clear, while others are live read-only views.

MSI-X vector table entries are especially stateful. The message address and data fields determine where interrupts are delivered, and the control mask bit gates delivery for that vector. Incorrect updates can reroute interrupts, lose interrupts, or expose interrupt writes to the wrong address in virtualized configurations.

Because this generated file only names bit ranges, it cannot distinguish read-only, write-trigger, write-one-to-clear, reserved, firmware-owned, or PCI-core-owned fields. Callers must preserve reserved bits and use the right access mechanism for the register's address space.

## Dependencies And Integration Points

The core dependency is the matching offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbif/nbif_6_3_1_offset.h`. Offsets such as `cfgBIF_CFG_DEV0_EPF*_...`, RCC block offsets, and MSI-X table offsets identify where the fields live; this header only describes bit positions.

The primary in-tree C integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c`, registered through `nbif_v6_3_1_funcs` and `nbif_v6_3_1_ras`. Discovery code selects those function tables for compatible NBIO/NBIF IP versions, and other AMDGPU components call them for HDP flush offsets, PCIe index/data offsets, memory size, doorbell apertures, interrupt control, ROM offset, ASPM, and RAS interrupt setup.

This header also integrates with the broader Linux PCIe stack. Generic PCI code may own parts of standard PCI, PCIe, MSI, MSI-X, AER, ACS, PASID, ARI, LTR, and power-management capability behavior, while AMDGPU/NBIF code may use device-specific RCC and PFC registers around that PCIe state. Driver code must avoid racing the PCI core or firmware when programming these fields.

The `EPF2` and `EPF3` namespaces indicate per-function endpoint config-space views. The same field names are repeated across functions, but their offsets and ownership differ. SR-IOV, multi-function, graphics/audio/USB-function exposure, and PF/VF separation all depend on pairing the correct function's offset namespace with the correct field namespace.

Adjacent chunks are needed for a complete per-file report. This chunk starts after the earlier `EPF2_PCIE_UNCORR_ERR_MASK` shift and first mask fields, and ends before completing `PCIEMSIX_VECT54_ADDR_LO`. The merge lane should not treat either boundary register family as complete from this chunk alone.

## Risks And Edge Cases

Generated-register drift is the main risk. A wrong shift or mask can compile cleanly but program a different PCIe/NBIF bit than intended, affecting link behavior, interrupt routing, AER policy, endpoint function identity, BAR exposure, or virtualization isolation.

AER fields are policy-sensitive. Masking unsupported requests, ECRC, malformed TLP, ACS violations, poisoned TLP egress blocking, or internal errors can hide real faults; severity bits control fatal/nonfatal reporting behavior. Header-log and prefix-log fields are diagnostic evidence and can be lost if status clearing is mishandled.

Capability-list fields have pointer and version subfields. Wrong `NEXT_PTR`, `CAP_ID`, or capability version interpretation can break PCI capability traversal or confuse software that expects standard PCIe enhanced capability layout.

BAR enhancement and SR-IOV-adjacent fields are address-exposure sensitive. Incorrect BAR size/index/control values can map too much or too little MMIO space, conflict with PCI resource assignment, or expose resources to the wrong function.

DPA, LTR, ASPM, PME, and auxiliary-power controls interact with platform power management and firmware sequencing. Misprogramming can cause power-state entry/exit failures, link instability, lost PME signaling, or performance/latency regressions.

ACS, PASID, ARI, requester-ID restore, active requester-ID, and endpoint/downstream config controls are security- and routing-sensitive in virtualized or IOMMU-backed systems. Incorrect field packing can break isolation, route DMA or completions incorrectly, or make VFs appear with the wrong capabilities.

MSI-X table entries are repetitive and easy to index incorrectly. A loop or table stride bug can write vector N's message address/data/control into a neighboring vector, and the chunk boundary at vector 54 increases the chance of incomplete generated-table reasoning if adjacent chunks are not merged.

## Test Signals

Build coverage should compile AMDGPU paths that include `nbif_6_3_1_offset.h` and `nbif_6_3_1_sh_mask.h`, especially `amdgpu/nbif_v6_3_1.c`, `gfx_v12_0.c`, `gmc_v12_0.c`, RAS registration paths, and display code that includes the NBIF offset header. Missing or renamed field macros generally surface as compile failures in `REG_SET_FIELD`, `REG_GET_FIELD`, or SOC15 register references.

Static validation should compare this generated header against the source register database and the matching offset header. Useful checks include every field having both a `__SHIFT` and `_MASK`, masks aligning with shifts, repeated EPF2/EPF3 capability layouts staying consistent where hardware intends them to be consistent, and MSI-X vector entries using the expected four-register stride.

Runtime PCIe tests should verify enumeration and capability traversal for functions represented by EPF2 and EPF3, including PCI IDs, BAR assignment, PCIe device/link capabilities, MSI/MSI-X capability exposure, AER capability exposure, ACS/PASID/ARI capability reporting, and power-management capability behavior.

Interrupt tests should exercise MSI-X vector programming for the USB/NBIF MSI-X table region: set address/data, mask and unmask vectors, trigger interrupts, and confirm delivery to the expected CPU vector without disturbing neighboring entries.

RAS and AER tests should inject or observe correctable and uncorrectable PCIe errors where supported, validate status decode, verify mask/severity policy, confirm header/prefix logging, and ensure clearing status does not clear unrelated evidence.

Power-management tests should cover ASPM/LTR/DPA/PME transitions, suspend/resume, reset, and runtime power changes on supported hardware. Regression signals include link retraining loops, failed wake, unexpected latency, missing PME, or device disappearance after low-power entry.

Virtualization and multi-function tests should cover PF/VF or multi-function configurations where EPF2/EPF3, ACS, PASID, ARI, requester-ID, BAR, and MSI-X state matter. Key regressions are DMA isolation failures, wrong function capability exposure, lost interrupts in VF/PF paths, or BAR/resource assignment mismatches.
