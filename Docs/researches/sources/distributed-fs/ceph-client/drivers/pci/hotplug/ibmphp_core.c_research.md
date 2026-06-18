# sources/distributed-fs/ceph-client/drivers/pci/hotplug/ibmphp_core.c

## Purpose
Implements the IBM PCI hotplug core lifecycle and hotplug-slot operations. It initializes EBDA/resource/controller data, registers slots, reads and updates HPC status, powers slots on/off, sets bus speed/mode, configures/unconfigures PCI cards, handles attention/status callbacks, and cleans up on module exit.

## Important APIs, Types, and Functions
Exports `ibmphp_debug`, `ibmphp_pci_bus`, `ibmphp_init_devno()`, `ibmphp_update_slot_info()`, `ibmphp_do_disable_slot()`, and `ibmphp_hotplug_slot_ops`. Important internals include `get_cur_bus_info()`, `slot_update()`, `get_max_slots()`, `power_on()`, `power_off()`, status callbacks, `get_max_bus_speed()`, `init_ops()`, `validate()`, `ibm_slot_find()`, `free_slots()`, `ibm_unconfigure_device()`, `bus_structure_fixup()`, `ibm_configure_device()`, `is_bus_empty()`, `set_bus()`, `check_limitations()`, `enable_slot()`, `ibmphp_disable_slot()`, `ibmphp_unload()`, `ibmphp_init()`, and `ibmphp_exit()`.

## Control Flow
Module init copies root bus ops into `ibmphp_pci_bus`, sets debug, parses EBDA, initializes resources, computes `max_slots`, registers PCI hotplug slots, runs `init_ops()` to read controller revisions/options/status, update bus speeds, and power off empty powered slots, then starts the HPC polling thread. Enable validates that a present, latched, unpowered slot can be enabled; blinks attention, sets bus speed/mode if the segment is empty, checks bus electrical limits, powers on, validates power-good and speed/mode status, allocates a `pci_func`, configures card resources, scans Linux PCI devices, turns attention off, and updates PCI bus speed. Disable validates if requested by user, blinks attention, creates a boot-time function record if needed, removes Linux devices, unconfigures resources when allowed, powers off, clears attention, and updates slot/bus info. Exit stops polling and frees slots, resources, EBDA queues, and the copied bus.

## State and Persistence Behavior
State is in global `ibmphp_pci_bus`, `max_slots`, `irqs[16]`, and `init_flag`, plus slot/controller/resource lists populated by other IBM files. Slot status is refreshed from the HPC into `status`, `ext_status`, and `busstatus`. `slot_cur->func` owns configured card resources and PCI device references until disable or unload. No durable persistence is implemented here; EBDA is treated as firmware input.

## Dependencies and Integration Points
Depends on IBM EBDA parsing/resource/HPC/polling functions declared in `ibmphp.h`, PCI core scan/remove APIs, x86 IRQ routing and I/O APIC helpers, PCI hotplug core, and ServerWorks CIOBX detection for a 133 MHz PCI-X workaround. It shares the hotplug-core interface through `struct hotplug_slot_ops`.

## Risks
The driver serializes hotplug operations with `ibmphp_lock_operations()`, but also reacts to polling/latch/power-fault paths where `flag` changes disable behavior. It relies on firmware status to prevent unsafe operations; wrong status decoding can power cards at incompatible speeds. `bus_structure_fixup()` manually allocates temporary bus/device objects and scans buses to compensate for PCI-core limitations. Domain 0 assumptions, old PCI-X speed limits, and x86 routing APIs limit portability.

## Test Signals
Module init with valid and missing EBDA/root bus, slot registration, init-time empty-slot power-off, attention LED set/get/blink, enable on valid slot, enable rejection for latch/open/no card/bus limit/speed mismatch/power fault, bridge and multifunction card scan, disable of boot-time and hot-added cards, unexpected latch/power-fault disable path, polling thread start/stop, resource cleanup on failed init, and unload after active slots are primary signals.
