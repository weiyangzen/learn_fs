# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_slot.c

## Purpose
Owns allocation, deallocation, registration, and deregistration of rpaphp `struct slot` objects with the PCI hotplug core.

## Important APIs, Types, and Functions
Public functions are `alloc_slot_struct()`, `dealloc_slot_struct()`, `rpaphp_register_slot()`, and `rpaphp_deregister_slot()`. The private `is_registered()` helper detects duplicate slot names in `rpaphp_slot_head`.

## Control Flow
Allocation zeroes a slot, duplicates the DRC name, takes an OF node reference, stores DRC index/power-domain metadata, and attaches `rpaphp_hotplug_slot_ops`. Registration rejects duplicate names, searches child OF nodes for matching `ibm,my-drc-index` to derive a PCI slot number, registers with `pci_hp_register()`, then links the slot into the global rpaphp list. Deregistration removes the slot from the list, deregisters the hotplug slot, drops the OF node, and frees memory.

## State and Persistence Behavior
This file manages heap lifetime and OF node references for slot objects. The global list is updated without a local lock, relying on rpaphp/DLPAR call serialization and module init/exit context.

## Dependencies and Integration Points
Depends on OF node reference counting, PCI DN metadata for child devfn lookup, PCI hotplug registration, and `rpaphp_hotplug_slot_ops` from `rpaphp_core.c`.

## Risks
The `retval` variable in child-node lookup is not initialized before the loop but is assigned before use if matching logic behaves normally; malformed children can make slot number fallback subtle. Lack of explicit locking around `rpaphp_slot_head` is safe only if callers serialize. Duplicate detection is name-based, not DRC-index-based.

## Test Signals
Exercise allocation failures, duplicate slot registration, missing child DRC index, successful register/deregister, OF node refcount balance, and DLPAR add/remove cycles.
