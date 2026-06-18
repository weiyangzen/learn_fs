<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug.h

## Purpose
Defines the internal interface and data structures for CompactPCI hotplug support, including PICMG 2.1 hot-swap CSR bits, slot state, controller callbacks, and core/PCI helper APIs.

## Important APIs, Types, and Functions
Defines HS CSR bit masks (`HS_CSR_INS`, `HS_CSR_EXT`, `HS_CSR_LOO`, and related bits), `struct slot`, `struct cpci_hp_controller_ops`, and `struct cpci_hp_controller`. Declares controller/bus lifecycle functions, internal PCI helper functions, and `cpci_hotplug_init()`.

## Control Flow
Board drivers provide a `cpci_hp_controller` with operations for querying or interrupting on ENUM, then register a bus range. The core uses the declared helpers to register hotplug slots, scan slots, manipulate LEDs, and configure/unconfigure PCI devices.

## State and Persistence
The header defines runtime state only. Slots track bus, devfn, cached `pci_dev`, latch/adapter state, extraction state, and hotplug core registration. Controllers track IRQ and operation callbacks.

## Dependencies and Integration Points
Depends on PCI and `pci_hotplug.h`. Shared by CompactPCI core, PCI helper implementation, generic port I/O driver, and other board-specific CompactPCI drivers.

## Risks and Edge Cases
The generic `struct slot` name is shared with ACPI hotplug but isolated by source inclusion. Controller ops are partially optional depending on interrupt versus polling mode; callers must validate required callbacks. Cached `pci_dev` references must be balanced.

## Test Signals
Compile all CPCI configurations, register/unregister controllers and buses, verify HS CSR bit handling, and run insertion/extraction scenarios through both interrupt and polling controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpci_hotplug.h -->
