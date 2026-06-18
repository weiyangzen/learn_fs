# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp.h

## Purpose
Defines the shared contract for the pSeries RPA PCI hotplug driver: RTAS constants, LED/power/sensor/state values, debug macros, `struct slot`, and cross-file prototypes.

## Important APIs, Types, and Functions
Key constants include `DR_INDICATOR`, `DR_ENTITY_SENSE`, `POWER_ON`, `POWER_OFF`, `LED_*`, `PRESENT`, `EMPTY`, `CONFIGURED`, `NOT_CONFIGURED`, `NOT_VALID`, and `MAX_DRC_NAME_LEN`. `struct slot` stores DRC index/type/power domain/name, OF node, PCI bus/device list, hotplug slot, attention state, and list linkage. Prototypes cover rpaphp PCI, core, and slot allocation/registration functions.

## Control Flow
The header has no execution, but its `to_slot()` helper maps generic `struct hotplug_slot` callbacks back to rpaphp `struct slot`. The hotplug ops object declared here is supplied by `rpaphp_core.c` and installed by `rpaphp_slot.c`.

## State and Persistence Behavior
The header describes per-physical-slot runtime state and declares the global `rpaphp_slot_head` list plus `rpaphp_debug`. Slot objects hold references to OF nodes and PCI buses but no external persistence.

## Dependencies and Integration Points
Includes Linux PCI and PCI hotplug headers. It is shared by `rpaphp_core.c`, `rpaphp_pci.c`, `rpaphp_slot.c`, and the DLPAR core.

## Risks
Several state names overlap semantically (`EMPTY` is both sensor and slot state), so call sites must distinguish sensor values from hotplug slot states. Changes to `struct slot` affect all rpaphp files and DLPAR lookup. DRC constants are RTAS ABI values and must not drift.

## Test Signals
Compile all rpaphp/rpadlpar objects, register/deregister slots, use attention/power/sensor callbacks, and verify debug macro/module parameter behavior.
