# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_core.c

## Purpose
Implements the core pSeries RPA PCI hotplug driver. It discovers hotpluggable DRC entries in the device tree, allocates/enables/registers slots, exposes hotplug callbacks for enable/disable/status/attention, and cleans up registered slots at module exit.

## Important APIs, Types, and Functions
Exports `rpaphp_slot_head`, `rpaphp_check_drc_props()`, and `rpaphp_add_slot()`. Important helpers include `get_children_props()`, `rpaphp_check_drc_props_v1()`, `rpaphp_check_drc_props_v2()`, `is_php_type()`, `is_php_dn()`, `rpaphp_drc_info_add_slot()`, `rpaphp_drc_add_slot()`, `enable_slot()`, `disable_slot()`, and status callbacks. `rpaphp_hotplug_slot_ops` is the hotplug-core operation table.

## Control Flow
Module init walks all `pci` OF nodes and calls `rpaphp_add_slot()`. Discovery supports both legacy `ibm,drc-*` arrays and newer `ibm,drc-info` cells. For each hotpluggable PCI DRC entry, it allocates a slot, records type/power domain/name/index, calls `rpaphp_enable_slot()` to initialize state and add present devices, then registers it with the PCI hotplug core. The enable callback checks the RTAS sensor; present devices trigger EEH init and `pci_hp_add_devices()`, while empty slots become `EMPTY`. Disable removes devices below the slot bus and marks the slot not configured.

## State and Persistence Behavior
Global state is the `rpaphp_slot_head` list and `rpaphp_debug` module parameter. Per-slot state tracks attention LED, power domain, DRC metadata, bus pointer, and configured/empty/not-valid status. Hardware/firmware state is RTAS power, sensor, and indicator state; PCI devices are added/removed from kernel memory only.

## Dependencies and Integration Points
Depends on Open Firmware DRC properties, RTAS indicator/power/sensor services, EEH initialization, pSeries PCI bridge data, PCI hotplug core, PCI rescan/remove locking, and `rpaphp_pci.c` sensor/enable helper. DLPAR add/remove calls `rpaphp_add_slot()` and `rpaphp_deregister_slot()`.

## Risks
Legacy DRC parsing walks packed string arrays and must stay aligned with index counts. The `ibm,drc-info` path currently handles a single first cell for slot creation, so assumptions about multiple cells need audit. The loop in `rpaphp_drc_add_slot()` returns the last slot's result only. Enable/disable state updates depend on RTAS sensor values, and a powered-off slot may need power-on just to read presence.

## Test Signals
Test legacy and `ibm,drc-info` device trees, boot-time slot discovery, attention LED set/get, power get, adapter get, enable/disable of empty and populated slots, EEH initialization, duplicate slot names, DLPAR-added slots, and module exit cleanup.
