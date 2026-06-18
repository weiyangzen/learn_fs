# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_core.c

## Purpose
Implements Compaq PCI hotplug module and PCI-driver lifecycle: controller discovery, SMBIOS and routing-table setup, MMIO/IRQ initialization, hotplug slot registration, initial slot power policy, debugfs registration, and module teardown.

## Important APIs, Types, and Functions
Exports global driver state `cpqhp_debug`, `cpqhp_legacy_mode`, `cpqhp_ctrl_list`, `cpqhp_slot_list`, and `cpqhp_routing_table`. Important helpers include `detect_SMBIOS_pointer()`, `init_SERR()`, `init_cpqhp_routing_table()`, `get_SMBIOS_entry()`, `ctrl_slot_cleanup()`, `get_slot_mapping()`, `cpqhp_set_attention_status()`, hotplug callbacks `process_SI()` and `process_SS()`, `ctrl_slot_setup()`, `one_time_init()`, `cpqhpc_probe()`, `unload_cpqphpd()`, `cpqhpc_init()`, and `cpqhpc_cleanup()`.

## Control Flow
Module init sets `cpqhp_debug`, creates the `cpqhp` debugfs root, and registers a PCI driver matching PCI hotplug-controller class devices. Probe enables a controller bridge, validates vendor/revision/subsystem capability bits, allocates a controller, duplicates the parent bus object for config-space probing, starts one-time global services, reserves and maps BAR 0, discovers bus speed, maps the first physical slot through the IRQ routing table, saves existing PCI config, discovers add resources from ROM/HRT/NVRAM, registers every physical slot with the PCI hotplug core, masks/clears interrupts, requests the shared controller IRQ, enables SOGO and SERR behavior, saves initial presence/switch snapshots, optionally powers off empty slots, initializes SERR, and creates a debugfs file. Teardown stores NVRAM, disables interrupts/SERR, deregisters slots, frees IRQ/MMIO/resources/function lists, stops the event thread, unmaps ROM/SMBIOS, unregisters the PCI driver, and removes debugfs.

## State and Persistence Behavior
Global one-time state includes ROM and SMBIOS mappings, routing table, event thread, and initialized flag. Per-controller state includes capability flags, resource pools, slot linked list, event queue, current interrupt comparison word, copied bus, MMIO base, IRQ, and debugfs dentry. Per-function state saved by `cpqhp_save_config()` persists original config space and resource ownership for replace/remove flows. If NVRAM support is built, resource-list state can be loaded and stored across module lifetimes.

## Dependencies and Integration Points
Depends on PCI core driver binding, x86 routing table APIs, ioremap of legacy ROM and SMBIOS table addresses, PCI hotplug core registration, controller IRQ handling from `cpqphp_ctrl.c`, resource discovery/configuration from `cpqphp_pci.c`, NVRAM hooks, and debugfs helpers.

## Risks
Probe is tightly coupled to old Compaq/Intel subsystem IDs and x86 firmware tables. Error paths after slot registration can leak already registered slots because `ctrl_slot_setup()` only returns the failing allocation path. The PCI driver has no `.remove` callback; cleanup is module-wide. It copies and mutates a `struct pci_bus`, which is fragile against PCI-core changes. One-time global initialization is shared across all controllers and only partially rolled back on later probe failures.

## Test Signals
Probe supported and unsupported subsystem IDs, failure injection through each probe stage, SMBIOS pointer/table mapping, slot name/number registration, IRQ request and interrupt completion wakeups, initial empty-slot power-off with `power_mode=0`, `power_mode=1` behavior, debugfs file creation, NVRAM store on unload, and module unload after multiple controllers.
