# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_pci.c

## Purpose
Implements Compaq PCI configuration and firmware-resource helpers. It scans devices, creates/removes Linux `pci_dev` objects, programs legacy IRQ routing, saves existing config space, validates replacement boards, discovers add resources from the Hot Plug Resource Table, and frees/returns resource nodes.

## Important APIs, Types, and Functions
Globals are `cpqhp_nic_irq`, `cpqhp_disk_irq`, and `unused_IRQ`. Public functions include `cpqhp_configure_device()`, `cpqhp_unconfigure_device()`, `cpqhp_set_irq()`, `cpqhp_get_bus_dev()`, `cpqhp_save_config()`, `cpqhp_save_slot_config()`, `cpqhp_save_base_addr_length()`, `cpqhp_save_used_resources()`, `cpqhp_configure_board()`, `cpqhp_valid_replace()`, `cpqhp_find_available_resources()`, `cpqhp_return_board_resources()`, `cpqhp_destroy_resource_list()`, and `cpqhp_destroy_board_resources()`. Internal helpers are `detect_HRT_floating_pointer()`, `PCI_ScanBusForNonBridge()`, and `PCI_GetBusDevHelper()`.

## Control Flow
`cpqhp_configure_device()` gets or scans a `pci_dev` under `pci_lock_rescan_remove()`, adds devices, and handles bridge children. `cpqhp_unconfigure_device()` stops/removes all functions for a device. During probe, `cpqhp_save_config()` recursively snapshots config space and creates `pci_func` entries. `cpqhp_find_available_resources()` locates `$HRT`, loads optional NVRAM, parses slot resource entries, assigns resource nodes either to controller free pools or occupied functions, and sorts pools. Add/remove paths use BAR probing in `cpqhp_save_used_resources()` and `cpqphp_ctrl.c` allocation to track ownership. Replace paths use `cpqhp_valid_replace()` and `cpqhp_configure_board()` to confirm and restore the same device tree.

## State and Persistence Behavior
This file builds the in-memory representation that NVRAM may persist: controller free resource lists and function-owned resource lists. It also stores `config_space[0x20]`, `base_length[]`, `base_type[]`, `pci_dev`, and legacy IRQ defaults. Resource return destroys ownership on function removal and merges nodes back into controller pools. Durable storage is delegated to `compaq_nvram_load/store()`.

## Dependencies and Integration Points
Depends on PCI core scan/remove APIs, PCI config-space accessors, x86 `pcibios_set_irq_routing()`, ELCR I/O ports, IRQ routing table from the core file, HRT/slot structures from `cpqphp.h`, and resource allocation logic in `cpqphp_ctrl.c`.

## Risks
Many routines directly write all-ones to BARs and restore values, which is disruptive if used on active devices without proper quiescing. The code assumes domain 0, 32-bit resource windows, specific HRT scaling, and incomplete bridge recursion in `PCI_ScanBusForNonBridge()`. `cpqhp_set_irq()` hand-allocates fake PCI objects and touches x86 ELCR ports. Several paths return generic `1` or ignore read/write failures, making diagnostics weak.

## Test Signals
HRT detection and parsing, NVRAM overlay, empty versus populated slot resource assignment, save config for bridges and multifunction devices, add/remove Linux `pci_dev` objects, legacy IRQ programming, replacement mismatch cases, BAR length probing, resource return/merge, bridge subordinate resource handling, and module unload leak checks are the main validation points.
