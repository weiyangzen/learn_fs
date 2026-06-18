# sources/distributed-fs/ceph-client/drivers/pci/of_property.c

## Purpose
Synthesizes standard Open Firmware properties for dynamically created PCI device and host bridge nodes. It encodes PCI address cells, ranges, interrupts, compatible strings, and host bridge windows into an `of_changeset`.

## APIs, Types, And Functions
Exports `of_pci_add_properties()` and `of_pci_add_host_bridge_properties()`. Internal types include `struct of_pci_addr_pair` and `struct of_pci_range_entry`. Helpers generate `bus-range`, `ranges`, `reg`, `interrupts`, `interrupt-controller`, `interrupt-map`, `compatible`, and host bridge `ranges` properties.

## Control Flow
For bridges, property generation adds `device_type = "pci"`, bus range, and interrupt-map information for child devices. For endpoints, it adds interrupt-controller metadata when an interrupt pin exists. Common flow then adds ranges, address/size cell counts, config-space `reg`, compatible strings based on vendor/device and class, and interrupt pin data. Host bridge generation emits device type, address/size cells, and translated memory ranges using bridge windows and parent address-cell width.

## State And Persistence
No independent state is stored. The function allocates temporary range arrays and string arrays, adds properties to a caller-owned `of_changeset`, and frees temporary memory. Applied changeset lifetime is managed by the caller in `of.c`.

## Dependencies And Integration
Depends on OF changeset APIs, PCI resource helpers, OF IRQ parsing, PCI swizzling, and resource-window lists. It is used by dynamic OF node creation for PCI devices and host bridges.

## Risks And Test Signals
Risks include incorrect cell counts, endian/width encoding mistakes, bad interrupt-map sizing, failure to free temporary allocations on error, compatible string allocation failures, and host bridge parent address-cell assumptions. Test signals include dynamic bridge and endpoint node creation, bridges with multiple children and INTx pins, empty or I/O-only ranges, 64-bit memory resources, invalid parent `#address-cells`, and changeset rollback after mid-property failure.
