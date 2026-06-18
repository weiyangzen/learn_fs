# sources/distributed-fs/ceph-client/drivers/pci/of.c

## Purpose
Provides PCI/Open Firmware integration: mapping PCI devices and buses to device tree nodes, parsing host bridge resources and interrupts, creating dynamic OF nodes for PCI devices/host bridges, and reading PCI-related DT properties.

## APIs, Types, And Functions
Exports `of_pci_find_child_device()`, `of_pci_get_devfn()`, `of_get_pci_domain_nr()`, `of_pci_check_probe_only()`, `of_irq_parse_and_map_pci()`, `of_pci_supply_present()`, `of_pci_get_max_link_speed()`, `of_pci_get_slot_power_limit()`, and `of_pci_get_equalization_presets()`. Other integration functions include `pci_set_of_node()`, `pci_set_bus_of_node()`, `pci_host_bridge_of_msi_domain()`, `devm_of_pci_bridge_init()`, and dynamic node make/remove helpers under `CONFIG_PCI_DYNAMIC_OF_NODES`.

## Control Flow
Device enumeration finds child OF nodes by PCI devfn, including `multifunc-device` containers, and attaches fwnodes to PCI devices/buses. Host bridge init parses `bus-range`, `ranges`, and `dma-ranges`, requests bus resources, remaps I/O windows, and configures IRQ swizzling/mapping. IRQ parsing uses a device node when available, otherwise builds a PCI interrupt spec, swizzles up the bridge chain until an OF node is found, and calls `of_irq_parse_raw()`. Dynamic node creation builds an OF changeset, adds PCI properties through `of_property.c`, applies it, stores the changeset in `np->data`, and attaches the node to the device or bridge.

## State And Persistence
State is in device/bus `of_node` pointers, `of_node_reused`, dynamic OF node flags, applied `of_changeset` objects, parsed resource lists, and host bridge windows. Dynamic nodes persist only in the live kernel device tree and are reverted on remove.

## Dependencies And Integration
Depends on OF core, OF IRQ/address helpers, PCI resource management, platform bus lookup, irqdomain MSI helpers, and `of_property.c` property synthesis. It integrates with host bridge probing, PCI enumeration, IRQ assignment, dynamic OF overlays, and PCI link/slot tuning code.

## Risks And Test Signals
Risks include refcount leaks on OF nodes, mismatched firmware versus Linux bus numbering in interrupt maps, invalid `linux,pci-probe-only` handling, malformed ranges/dma-ranges, dynamic changeset cleanup ordering, and slot power limit rounding. Test signals include DT host bridge enumeration, missing child nodes, interrupt-map swizzling across bridges, dynamic node add/remove, malformed ranges, power-supply property detection, max-link-speed parsing, slot-power-limit boundary values, and equalization preset array errors.
