# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 88073-90484

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It covers 2,412 source lines and 2,172 `#define` field-layout macros. There are no functions, structs, enums, local variables, locks, allocations, or executable statements in this range.

The range starts in the middle of `IOMMU_L2_2_IOMMU_COMMAND`, after the first command shifts and before the command masks. It then covers the rest of the `nbio_iohub_iommu_l2_iommul2cfg` block, all of the small `nbio_iohub_nb_pciedummy0_pciedummy_cfgdec` block, all of the `nbio_pcie0_bifplr0_cfgdecp` bridge/port block, and the start of `nbio_pcie0_bifplr1_cfgdecp` through `BIFPLR1_2_SECONDARY_STATUS`. The merge lane should reconcile the boundary registers with adjacent chunks before treating the IOMMU command or BIFPLR1 block as complete.

Although the path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield-geometry half of AMD's generated NBIO 7.0 register interface. For each register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to place or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the encoded bit mask used to isolate, preserve, clear, or update that field.

This chunk describes field layouts for an NBIO IO hub IOMMU L2 PCI/SMMU configuration aperture, a dummy PCI configuration function, and a large PCIe bridge/root-port style `BIFPLR0_2` configuration surface. The fields are intended to be combined with generated register address/default metadata and AMDGPU register helpers; the macros alone do not perform reads, writes, polling, error handling, or persistence.

## Important Macro Families

The `IOMMU_L2_2` section exposes the IOMMU L2 configuration-space and SMMU identity surface:

- PCI-like identity and command/status fields: vendor/device ID, command enables for IO, memory, bus mastering, parity, SERR, and interrupt disable, plus status bits for interrupt status, capability-list presence, master data error, target/master aborts, system error, and parity error.
- Class/header fields: revision ID, programming interface, subclass, base class, cache line size, latency, header type, BIST, subsystem/vendor adapter ID, capability pointer, interrupt line, and interrupt pin.
- IOMMU capability fields: capability header, base-address low/high, range/unit/bus/device fields, MSI vector numbers, GVA/PA/VA sizing, architecture mode, DVM mode, and SMMU MMIO enable/lock.
- MSI and MSI mapping fields: MSI capability header, enable and multiple-message fields, 64-bit address support, MSI address/data words, and MSI mapping capability/address controls.
- Write-side or firmware-visible IOMMU controls: adapter ID write register, control register fields for command buffer enable, event log enable, MMIO enable, interrupt enable, completion wait behavior, guest translation/cache controls, PPR enable, GA log enable, SMI filter controls, MSI controls, GA tag and invalidation tag controls, and address/data controls for MMIO windows.
- Range and dummy/control registers: range valid/unit/bus/device fields, `DSFX_CONTROL`, dummy data registers, poison/DVM controls, IOHC/L2 DMA request and host response stall controls.
- SMMU MMIO identification registers: `IDR0`, `IDR1`, `IDR2`, `IDR3`, `IDR5`, `IIDR`, and `AIDR` fields describing SMMU architecture capabilities such as stage support, context banks, stream matching, translation levels, page granules, ASID/VMID bits, coherency, endianness, secure-state support, PTW behavior, and architecture revision.

The `NB_PCIEDUMMY0_2` section is a compact dummy PCI configuration block. It defines combined device/vendor ID, status/command, class-code/revision, header type, and a write-oriented header-type byte. These fields model a minimal PCI config surface rather than an active algorithm.

The `BIFPLR0_2` section is a full PCIe bridge/root-port style configuration layout:

- Standard PCI bridge header fields: vendor/device ID, command/status, revision/programming interface/subclass/base class, cache line, latency, header/BIST, primary/secondary/subordinate bus numbers, IO base/limit, secondary status, memory and prefetchable memory windows, upper prefetchable base/limit, high IO base/limit, capability pointer, interrupt line/pin, IRQ bridge control, and extended bridge control.
- Power-management capability fields: PM capability list linkage, version, PME and D-state support, PME enable/status, data select/scale, power state, B2/B3 support, bus power/clock control, and PM data.
- PCI Express capability fields: PCIe capability list/header, device capabilities/control/status, link capabilities/control/status, slot/root capability/control/status, and PCIe 2.0 device/link/slot capability/control/status registers.
- MSI and subsystem ID fields: MSI capability header/control, MSI message address/data, 64-bit data, subsystem ID capability fields, and MSI mapping capability/address fields.
- Vendor-specific and virtual-channel fields: PCIe vendor-specific enhanced capability headers and payload words, VC port capabilities/control/status, and VC0/VC1 resource capability/control/status fields.
- Device serial number and AER fields: device serial number dwords; AER enhanced capability, uncorrectable/correctable status, masks and severities, AER capability/control, header logs, root error command/status, source ID, and TLP prefix logs.
- Secondary PCIe/link training fields: secondary enhanced capability, link control 3, lane error status, and lane 0 through lane 15 equalization controls.
- ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM fields: ACS capability/control, multicast address/receive/block/overlay registers, L1 PM substate capability/control, Downstream Port Containment control/status/source, RP PIO status/mask/severity/sys-error/exception/header/prefix logs, and ESM capability/status/control/capability bitmaps.

The `BIFPLR1_2` section begins the next PCIe bridge/root-port style block. This chunk includes only its standard identity/header region through secondary status: vendor/device ID, command/status, revision/class bytes, cache/latency/header/BIST, bus-number/latency, IO base/limit, and secondary-status fields. Memory windows and later capabilities continue in the next chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public surface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only bit positions and masks for 8-, 16-, and 32-bit PCI/NBIO/SMMU register words.

The macros do not encode register addresses, access permissions, write-one-to-clear behavior, reset domains, polling requirements, ordering barriers, firmware ownership, or side effects. Consumers must combine these field definitions with sibling generated metadata:

- `nbio_7_0_default.h` provides reset/default values for the `IOMMU_L2_2`, `NB_PCIEDUMMY0_2`, `BIFPLR0_2`, and `BIFPLR1_2` register families.
- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` provide the address/SMN side for the broader NBIO 7.0 register database, although these exact `*_2` names are more visible in default and shift/mask metadata than in local C call sites.
- AMDGPU code applies the macros through helper patterns such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET` where the target register has a matching address symbol.

## Control Flow

This header has no local runtime control flow. Runtime flow is external and typically looks like:

1. AMDGPU/NBIO/platform code selects a hardware register from generated offset or SMN metadata.
2. The code reads a 32-bit register value from the correct aperture.
3. It extracts a field with the `__SHIFT` and `_MASK` constants, or composes a new value by clearing the mask and inserting a shifted field value.
4. The decoded or written value affects IOMMU configuration, PCIe bridge enumeration, interrupt routing, error reporting, link training, power management, SMMU capability reporting, DPC/RP PIO diagnostics, or capability exposure.

The names imply several hardware-managed flows outside this header: IOMMU command/event/PPR/GA-log enablement, MSI delivery and MSI remapping, SMMU identification reporting, PCI bridge resource-window programming, PME and D-state transitions, PCIe link retraining and equalization, VC resource negotiation, AER/DPC/RP PIO error capture, ACS isolation controls, multicast overlay/blocking controls, and L1 PM substate negotiation.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO IOMMU, SMMU, dummy PCI, and PCIe bridge/root-port configuration registers. Persistence depends on GPU reset domain, PCIe reset, function-level reset, firmware/BIOS programming, host PCI core configuration, suspend/resume restore, and explicit driver writes.

Represented state includes PCI identity/class/header fields, command/status bits, bridge bus numbers and resource windows, interrupt line/pin and MSI routing state, IOMMU base/range/control fields, SMMU capability ID registers, power-management and PME state, PCIe link/device/slot/root controls and statuses, VC/ACS/multicast controls, AER/DPC/RP PIO status/mask/log registers, lane equalization state, and ESM capability bitmaps.

Several fields are likely status or latched hardware state, such as PCI error status, link training/equalization status, AER/DPC/RP PIO logs, lane errors, and MSI pending data. Others are configuration controls that software or firmware may write, including command enables, bridge windows, power-management controls, MSI enables, IOMMU logging/translation controls, ACS controls, multicast controls, DPC enables, and ESM controls. The mask header does not distinguish read-only, read/write, write-one-to-clear, or reserved semantics; callers must preserve reserved bits and follow hardware documentation.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database. It must remain synchronized with sibling generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h`

Direct include users in this tree are `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` shows the intended integration style: include default/offset/shift-mask/SMN headers together and use AMDGPU register helpers around generated symbols. The exact `IOMMU_L2_2`, `NB_PCIEDUMMY0_2`, and `BIFPLR*_2` symbols in this chunk are not directly exercised by local `.c` files in the visible tree, so they are best treated as generated hardware metadata for platform, firmware, diagnostic, or future NBIO access paths rather than active high-level driver logic here.

The PCIe portions also depend on PCI/PCIe architectural semantics for standard config space, bridge windows, PM capabilities, MSI, PCIe capabilities, AER, VC, ACS, multicast, L1 PM substates, DPC, and RP PIO. The SMMU portions depend on ARM SMMU-style ID register semantics as exposed through AMD NBIO's IOMMU L2 MMIO surface.

## Risks And Edge Cases

- Generated shift/mask drift can compile successfully while causing software to decode or write the wrong hardware bit. For this chunk that can affect IOMMU enablement, interrupt delivery, PCI bridge windows, PCIe link state, AER/DPC error handling, or SMMU capability reporting.
- The chunk starts and ends mid-block. Adjacent chunks are required for complete `IOMMU_L2_2_IOMMU_COMMAND` and `BIFPLR1_2` coverage.
- Many registers contain reserved fields represented as explicit macros. Writers must preserve reserved bits unless the hardware specification requires a defined value.
- Status and error fields may be write-one-to-clear or latch-on-error at the hardware level. The masks make those bits easy to target but do not communicate clearing rules.
- IOMMU command/event/PPR/GA-log controls, MMIO enable/lock fields, MSI mapping, and SMMU identification fields can interact with firmware, IOMMU groups, interrupt remapping, and host memory isolation. Incorrect writes can break DMA translation or interrupt delivery.
- PCI bridge bus/resource-window fields are system-visible. Bad masks or writes can misroute IO/MMIO windows, hide downstream devices, or corrupt host PCI resource accounting.
- PCIe link, slot, root, VC, ACS, multicast, L1 PM, DPC, RP PIO, and ESM controls affect topology behavior, isolation, power, recovery, and error reporting. Code that writes them needs topology checks and hardware-specific sequencing.
- The `BIFPLR0_2` block is large and mechanically repetitive; generation errors can be localized to one capability family and missed if tests only cover enumeration or only inspect standard PCI header fields.
- Exact symbol availability differs across NBIO generations. For example, some `BIFPLR*_2` offset symbols are visible in neighboring NBIO 7.7.0 headers, while this NBIO 7.0 chunk mainly exposes shift/mask and default metadata for these names.

## Test Signals

- Build AMDGPU with NBIO 7.0 and SMU10 include paths enabled. Compile-time coverage catches missing generated symbols used by `nbio_v7_0.c`, `soc15.c`, and power-management include stacks.
- Run generated-header consistency checks: every field with a `__SHIFT` should have a compatible `_MASK`, masks should align with their shift, and fields within a register should not overlap except where the hardware register intentionally aliases bytes or words.
- Cross-check this chunk against `nbio_7_0_default.h` so every `IOMMU_L2_2`, `NB_PCIEDUMMY0_2`, `BIFPLR0_2`, and visible `BIFPLR1_2` register has a corresponding generated default where expected.
- Cross-check address coverage against `nbio_7_0_offset.h` and `nbio_7_0_smn.h`; missing address symbols should be treated as metadata coverage gaps or as registers accessed through a different aperture/generation-specific path.
- On supported NBIO 7.0 hardware, validate PCI enumeration, bridge bus/resource windows, MSI delivery, power-management state transitions, AER/DPC reporting, link retraining/equalization status, ACS behavior, L1 PM substate behavior, and reset/suspend/resume restore.
- For IOMMU/SMMU paths, validate command/event/PPR/GA-log enablement, MSI vector programming, MMIO base/range decoding, SMMU ID register values, DMA translation behavior, and interrupt remapping behavior against firmware and host IOMMU expectations.
- For error-path testing, inject or observe AER/DPC/RP PIO conditions and confirm that status, mask, severity, source-ID, header-log, and prefix-log fields decode correctly and that clearing code does not disturb unrelated or reserved bits.
