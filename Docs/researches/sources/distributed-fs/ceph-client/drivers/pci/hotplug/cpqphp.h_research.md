# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp.h

## Purpose
Provides the shared ABI, state structures, constants, prototypes, and MMIO helper routines for the Compaq/HP PCI hotplug controller driver. It binds `cpqphp_core.c`, `cpqphp_ctrl.c`, `cpqphp_pci.c`, `cpqphp_nvram.c`, and `cpqphp_sysfs.c` into one driver stack.

## Important APIs, Types, and Functions
Important packed hardware/firmware layouts include `struct smbios_system_slot`, `struct smbios_entry_point`, `struct ctrl_reg`, `struct hrt`, and `struct slot_rt`, with matching offset enums for direct byte/word access through `readb/readw/readl`. Runtime structures are `struct pci_func` for one PCI function and saved resources/config, `struct slot` for hotplug-core slot state, `struct pci_resource` for simple resource lists, `struct event_info`, `struct controller`, `struct irq_mapping`, and `struct resource_lists`. It declares cross-file entry points for debugfs, event handling, resource sorting, PCI configuration, board add/remove, NVRAM-assisted resource discovery, and device configure/unconfigure. Inline helpers control LEDs, slot enable/power bits, SOGO commits, speed detection, latch/presence/power status, and wait for controller completion.

## Control Flow
The header defines the shared control vocabulary. Core probe fills `struct controller`, registers `struct slot` instances with `cpqphp_hotplug_slot_ops`, and uses MMIO helpers to initialize slots. Interrupts in `cpqphp_ctrl.c` enqueue `event_info` records, and the kthread calls exported SI/SS functions. PCI helpers allocate and return `pci_resource` nodes through `resource_lists`. Hotplug-core callbacks use `to_slot()` and then route through `cpqhp_get_bus_dev()`, `cpqhp_slot_find()`, and controller operations.

## State and Persistence Behavior
The central persistent runtime state is the controller list `cpqhp_ctrl_list`, per-bus function lists `cpqhp_slot_list[256]`, IRQ routing table `cpqhp_routing_table`, per-controller resource pools, per-function saved config space and BAR length/type arrays, event queues, LED/slot state, and presence/switch snapshots. The header also exposes optional NVRAM persistence hooks through `cpqphp_nvram.h`, but durable storage is implemented elsewhere.

## Dependencies and Integration Points
Depends on Linux interrupt, MMIO, delay, mutex, signal, PCI, PCI hotplug, and x86 IRQ routing table definitions. It integrates with the PCI hotplug core through `struct hotplug_slot`, with debugfs through controller dentries, with Compaq ROM/HRT parsing through packed table definitions, and with x86 routing helpers for legacy IRQ programming.

## Risks
Packed layout and offset enums are hardware ABI. Inline MMIO helpers assume slot indexes and bit placements that match Compaq/Intel HPC registers. Global lists are manually managed and shared across interrupt, kthread, timer, hotplug-core, and teardown paths. `wait_for_ctrl_irq()` sleeps a fixed interval and only reports signals, so hardware completion semantics are weak. Resource nodes are raw singly linked lists, making ownership bugs easy.

## Test Signals
Build all `cpqphp` translation units together, probe supported Compaq/Intel controllers, verify slot registration/status callbacks, LED and power bit changes, event queue processing, resource list sorting/combining, IRQ routing table discovery, NVRAM enabled/disabled builds, debugfs creation/removal, and teardown of all global lists.
