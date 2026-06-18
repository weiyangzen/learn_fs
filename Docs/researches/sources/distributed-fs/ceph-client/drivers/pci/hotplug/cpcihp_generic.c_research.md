<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_generic.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_generic.c

## Purpose
Implements a generic polling CompactPCI hotplug controller driver for x86 systems where the chassis exposes the `#ENUM` signal as a bit in a port-I/O register.

## Important APIs, Types, and Functions
Module parameters are `debug`, `bridge`, `first_slot`, `last_slot`, `port`, and `enum_bit`. `validate_parameters()` parses and validates them. `query_enum()` reads the port and tests the configured bit. `cpcihp_generic_init()` requests the I/O port, finds the bridge and subordinate bus, registers a CPCI controller and bus range, and starts the CPCI core. `cpcihp_generic_exit()` stops and unregisters everything.

## Control Flow
Init validates configuration, reserves one I/O port, resolves the bridge specified as hexadecimal `<bus>:<slot>` in domain 0, uses its subordinate bus as the hotplug bus, provides only `query_enum()` controller ops so the core uses polling mode, registers slots, and starts the CPCI worker. Exit stops polling, unregisters slots and controller, and releases the I/O region.

## State and Persistence
State is global module parameter/configuration state plus the selected subordinate `pci_bus`, generic controller ops, and controller struct. It persists while the module is loaded.

## Dependencies and Integration Points
Depends on x86 port I/O, PCI device lookup, CompactPCI core APIs, module parameters, and the selected bridge's subordinate bus.

## Risks and Edge Cases
No IRQ mode is supported, so detection latency is tied to the CPCI polling interval. Error paths after `request_region()` and bridge lookup can return without releasing the I/O region in some early failures. The driver assumes PCI domain 0 and a valid bridge with a subordinate bus. Parameters are required and parse with legacy `simple_strtoul()`.

## Test Signals
Load with missing/invalid parameters, invalid bridge, busy I/O port, valid bridge and slot range, simulated ENUM bit transitions, module unload after partial init failure, and insertion/extraction behavior through the CPCI polling thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_generic.c -->
