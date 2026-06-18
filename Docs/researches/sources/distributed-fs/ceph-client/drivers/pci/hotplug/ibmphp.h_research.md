# sources/distributed-fs/ceph-client/drivers/pci/hotplug/ibmphp.h

## Purpose
Defines the shared contract for the IBM PCI hotplug driver: EBDA/RIO firmware table layouts, resource manager structures, HPC command/status constants, slot/controller runtime objects, and cross-file prototypes.

## Important APIs, Types, and Functions
Firmware structures include `rio_table_hdr`, `scal_detail`, `rio_detail`, `opt_rio`, `ebda_hpc_list`, `ebda_hpc_slot`, `ebda_hpc_bus`, controller access unions, `ebda_rsrc_list`, `ebda_pci_rsrc`, and `bus_info`. Resource structures are `range_node`, `bus_node`, `resource_node`, and `res_needed`. Runtime objects are IBM-specific `struct pci_func`, `struct slot`, and `struct controller`. It defines HPC write commands (`HPC_SLOT_ON`, `HPC_SLOT_OFF`, bus mode commands, attention LED commands), read commands, status bits, decode macros such as `SLOT_PRESENT()`, `SLOT_PWRGD()`, `CURRENT_BUS_SPEED()`, `CTLR_RESULT()`, and operation prototypes for EBDA, resources, HPC access, polling, PCI configure/unconfigure, and hotplug operations.

## Control Flow
The header has no standalone execution, but all IBM driver files use its state machine. EBDA parsing populates controller, slot, bus, and resource lists. Core validation reads slot status through `ibmphp_hpc_readslot()`, powers slots through `ibmphp_hpc_writeslot()`, allocates resources through `ibmphp_*rsrc*`, and registers `ibmphp_hotplug_slot_ops` with the hotplug core.

## State and Persistence Behavior
Runtime state is list-based: global `ibmphp_slot_head` and EBDA resource/controller lists, per-slot status/ext_status/busstatus, per-slot resource-owned `pci_func` chains, per-controller command/status/options, and per-bus speed/slot-limit data. The header models firmware-derived EBDA data but does not itself persist changes back to firmware.

## Dependencies and Integration Points
Depends on Linux PCI hotplug, PCI register constants, list heads, and x86-era firmware/IRQ concepts. It integrates `ibmphp_core.c` with other IBM hotplug implementation files for EBDA access, HPC I/O, resource management, and PCI card configuration.

## Risks
The header mixes firmware table ABI, controller command protocol, resource allocator internals, and hotplug-core state. Macro decoding must exactly match HPC status bit semantics; wrong interpretation can power unsafe slots or reject valid operations. Several structures assume domain 0, 32-bit resources, and old PCI/PCI-X speed models. The `HPC_CTLR_RESULE2` typo is part of the existing bit definitions and should be changed only with care.

## Test Signals
Compile the whole IBM hotplug driver, EBDA table parsing, slot/controller list population, resource manager initialization, status macro decoding, bus speed/mode detection, HPC command completion result decoding, hotplug slot registration, and PCI/PCI-X capability reporting are key validation signals.
