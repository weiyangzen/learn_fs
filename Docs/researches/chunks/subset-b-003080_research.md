# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 29279-31718

## Scope And Purpose

This chunk is a generated AMD NBIO 7.0 register field header segment. It defines `__SHIFT` and `__MASK` constants for fields in several NBIO address blocks: IOMMU L2 MMIO control/status, IOMMU queue and counter state, IOAPIC MMIO/index registers, and the start of the NBIF0 BIF root-complex PCI configuration space for device 0 RC1.

The header contains no executable functions or types. Its purpose is to make register programming in the AMDGPU driver readable and mechanically consistent: call sites include the paired offset header for register addresses and this shift/mask header for field extraction or read/modify/write composition. Consumers use these constants with AMDGPU register helpers, `REG_GET_FIELD`-style macros, and direct bit operations when configuring NBIO, PCIe, IOMMU, interrupt, and power-management behavior.

This chunk starts just after the IOMMU event-base fields and opens with `IOMMU_L2MMIO0_IOMMU_MMIO_CNTRL_0`. It ends at the declaration of `BIF_CFG_DEV0_RC1_SLOT_STATUS`, before that register's field definitions continue in the next chunk.

## Register Areas Covered

The first major area is `nbio_iohub_iommu_l2mmio_l2mmiocfg`. It covers AMD IOMMU MMIO controls such as `IOMMU_EN`, command/event logging enable bits, event/PPR/GA interrupt enables, coherent/isoc behavior, guest translation and address translation support, SMIF/GAM toggles, and queue sizing fields. Capability registers `EFR_0` and `EFR_1` expose feature support for prefetch, PPR, guest translation, x2APIC/NX-like support bits, HATS/GATS/GLX, SMIF, GAM, PASID maximum, DTE segmenting, automatic PPR response, MARC, MSI capability, snoop attributes, HA/EPH/ATTRFW/HD, and IOTLB invalidation type support.

The same IOMMU block defines address and size fields for exclusion ranges, PPR queues, GA log buffers, duplicated B-side PPR/event queues, and alternate device-table bases `DEVTBL_1` through `DEVTBL_7`. Base and limit values are split into low/high halves, with low-address fields commonly shifted by 12 and high halves carrying 20-bit masks, reflecting page-aligned physical address programming.

Queue pointer and status definitions cover command, event, PPR, GA, PPR_B, and EVENT_B buffers. Each queue has head and tail pointer fields, usually aligned on low reserved bits and paired with reserved high bits. `IOMMU_MMIO_STATUS_0` reports queue activity, log interrupts, command-buffer running state, event/PPR/GA overflow, B-side overflow, buffer-active state, and early-overflow conditions.

The performance-counter section describes IOMMU counter topology and two banks with four counters each. Each counter group includes a 48-bit counter split into low/high registers, an event source selector (`CSOURCE`), count units, clear/active control (`CAC`), PASID/domain/device-ID match fields and masks with enable bits, and event-note report fields with a report-enable bit (`CERE`). Bank lock registers separately cover PASID, domain, and device-ID lock masks.

The next address blocks are IOAPIC-related. `nbio_iohub_nb_ioapicmio_ioapic_miodec` defines the IOAPIC index/data windows, an IRQ pin assertion register, and an EOI vector register. `nbio_iohub_nb_ioapicmioindex_ioapic_mioindexdec` defines indexed IOAPIC ID/version/arbitration fields and redirection table entries 0 through 31. Each redirection entry low half has vector, delivery mode, destination mode, delivery status, polarity, remote IRR, trigger mode, and mask fields; each high half has the destination APIC ID.

The final area in this chunk begins `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` and covers PCI/PCIe root-complex config-space fields for `BIF_CFG_DEV0_RC1`. It includes vendor/device ID, command/status, revision/class/header/BIST fields, bridge bus numbering, IO/memory/prefetchable windows, interrupt and bridge control fields, PCI power-management capability fields, and PCIe capability fields. The visible PCIe capability portion covers device capability/control/status, link capability/control/status, and slot capability/control before stopping at `SLOT_STATUS`.

## Important Definitions

The most important API surface is the naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit index used before masking or after extraction.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned field mask, usually suffixed with `L`.
- Comment lines such as `//IOMMU_L2MMIO0_IOMMU_MMIO_CNTRL_0` and `// addressBlock: ...` segment fields by hardware register and address block.

High-impact field groups include:

- IOMMU control: `IOMMU_EN`, `CMD_BUF_EN`, `EVENT_LOG_EN`, `EVENT_INT_EN`, `PPR_LOG_EN`, `PPR_INT_EN`, `PPR_EN`, `GT_EN`, `GA_EN`, `SMIF_EN`, `GAM_EN`, `GA_LOG_EN`, `GA_INT_EN`, and `PPRQ`.
- IOMMU capabilities: `PREF_SUP`, `PPR_SUP`, `GT_SUP`, `GA_SUP`, `HATS`, `GATS`, `GLX_SUP`, `SMIF_SUP`, `GAM_SUP`, `PAS_MAX`, `DTE_seg`, `PPR_AUTORESP_SUP`, `MARCnum`, `MMIO_MSI_CAP_SUP`, and `InvIotlbTypeSup`.
- Queue state: `CMD_HDPTR`, `CMD_TAILPTR`, `EVENT_HDPTR`, `EVENT_TAILPTR`, `PPR_HDPTR`, `PPR_TAILPTR`, `GA_HDPTR`, `GA_TAILPTR`, and B-side equivalents.
- IOMMU status: `EVENT_OVERFLOW`, `EVENT_LOGINT`, `COMWAIT_INT`, `CMD_BUFRUN`, `PPR_OVERFLOW`, `PPR_INT`, `GA_OVERFLOW`, `GA_INT`, `EVENT_B_OVERFLOW`, and early-overflow flags.
- IOMMU counters: `N_COUNTER`, `N_COUNTER_BANKS`, `ICOUNTER_*`, `CSOURCE_*`, `COUNT_UNITS_*`, `CAC_*`, `PASID_MATCH/MASK`, `DOMAIN_MATCH/MASK`, `DEVICEID_MATCH/MASK`, and report `EVENT_NOTE`/`CERE` fields.
- IOAPIC redirection: `Vector_N`, `Delivery_Mode_N`, `Destination_Mode_N`, `Interrupt_Pin_Polarity_N`, `Remote_IRR_N`, `Trigger_Mode_N`, `Mask_N`, and `Destination_id_N`.
- Root-complex config: bridge command/status bits, bus number/window fields, PM capability/status bits, PCIe link speed/width, link retrain/disable/control bits, error enable/status bits, FLR capability, and slot hotplug/power/indicator controls.

## Control Flow And Data Flow

There is no local control flow in this header. Runtime flow is indirect: AMDGPU initialization, interrupt setup, PCIe link handling, power-management code, and low-level NBIO helpers include this file and use the constants to read a register, isolate fields, compose new values, and write them back.

The effective flow at call sites is normally:

1. Select a register address from a matching `nbio_7_0_offset.h` or related offset header.
2. Read the register through MMIO, PCI config, or indexed IOAPIC access helpers.
3. Extract a field with the mask and shift, or clear and insert a new field value.
4. Write the modified value back, preserving reserved bits where the hardware requires it.

Because this file defines only bit positions, correctness depends on consumers pairing these masks with the matching NBIO generation and register address block. A correct mask applied to the wrong register can silently program a different hardware field.

## State And Persistence Behavior

The header itself has no state, allocation, locking, or persistence. The hardware registers it describes are persistent hardware state across driver operations until reset, power transition, firmware action, or later driver writes alter them.

The IOMMU definitions affect durable device state such as command/event/PPR/GA queue base addresses, head/tail pointers, interrupt enables, exclusion ranges, MARC remap windows, and performance-counter configuration. Incorrect values can persist long enough to break DMA translation, event delivery, or queue processing until the device or function is reset.

The IOAPIC redirection fields define interrupt routing state. Vector, delivery mode, polarity, trigger mode, mask, and destination changes directly control how NBIO-originated interrupts are delivered to the host.

The BIF RC1 PCI config fields describe bridge-visible state exposed to the PCI subsystem. Command bits, memory/IO windows, PM state, PCIe link controls, and slot/hotplug controls can affect enumeration, link training, error reporting, power management, and device reset behavior.

## Dependencies And Integration Points

This chunk is included through AMDGPU NBIO and SoC support code, notably files such as `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and SMU10 power-management includes. It must remain synchronized with the matching offset headers and generated register database for NBIO 7.0.

Important integration points include:

- AMDGPU register access helpers that expect these masks to be already shifted into register position.
- PCIe/NBIO code that interprets root-complex config registers and link status fields.
- IOMMU programming and diagnostics paths that manage device tables, queue buffers, PASID/domain/device matching, and event logs.
- Interrupt routing code that accesses IOAPIC indexed registers and redirection entries.
- Firmware and hardware documentation contracts: many fields are reserved, capability-only, or split across low/high registers, so preserving reserved bits and programming paired registers in the right order is part of the external contract.

## Risks And Edge Cases

The main risk is generated-data drift. If a shift or mask is wrong, driver code will still compile, but it may read false capability data, write reserved bits, corrupt queue pointers, disable interrupts, misroute IOAPIC entries, or report incorrect PCIe link state.

Split address fields are especially sensitive. Many base/limit registers expose low fields starting at bit 12 and high fields masked to 20 bits. Call sites must maintain page alignment, combine low/high halves correctly, and avoid truncating physical addresses.

Queue pointer fields reserve low alignment bits and high unused bits. Bugs here can make command/event/PPR/GA queues appear empty, full, or active forever. Overflow and early-overflow masks are also status-like fields, so consumers must know whether hardware uses write-one-to-clear or read-only semantics from the register spec; the header does not encode that behavior.

Reserved masks are present throughout the chunk. They are useful for decoding but risky for writes: code should not use `Reserved*_MASK` as writable fields unless the hardware programming guide explicitly requires it.

IOAPIC redirection entries are repetitive and index-sensitive. A copy/paste or generation error for one entry can affect only a specific interrupt line, making failures intermittent and platform-dependent.

The BIF RC1 config fields mix standard PCI/PCIe semantics with AMD-specific root-complex placement. Link retraining, link disable, clock power management, hotplug interrupt enables, bridge window, and SERR/error bits can have visible system behavior. Misprogramming can affect boot enumeration, suspend/resume, GPU reset, AER-like reporting, or hotplug handling.

## Test Signals

There are no unit tests for this header alone. Useful signals come from build coverage and hardware/integration behavior:

- Compile tests for AMDGPU configurations that include NBIO 7.0 ensure symbol names and include ordering remain valid.
- PCI enumeration and `lspci`/kernel logs can reveal broken vendor/device ID, class, bridge window, command/status, or PCIe capability decoding.
- GPU initialization, reset, suspend/resume, and runtime power-management tests exercise NBIO register programming paths using these masks.
- IOMMU and DMA stress tests can expose bad device-table, queue, PASID/domain/device-ID, event-log, or PPR/GA fields through translation faults, hangs, or missing interrupts.
- Interrupt-routing tests and normal display/compute interrupt traffic can expose IOAPIC redirection mistakes through lost, masked, or misdelivered interrupts.
- PCIe link training and error-injection diagnostics can validate `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, device status, root control, and slot-control fields.

For review, the strongest static check is diffing this generated chunk against the authoritative AMD register database or an adjacent known-good NBIO generation, while verifying that all consumers include the matching offset header for the same ASIC generation.
