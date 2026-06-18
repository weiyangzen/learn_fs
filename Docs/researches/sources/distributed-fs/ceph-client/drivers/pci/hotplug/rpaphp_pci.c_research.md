# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_pci.c

## Purpose
Provides rpaphp PCI-slot sensor and initial enable/configuration logic around RTAS and pSeries EEH/PCI bus integration.

## Important APIs, Types, and Functions
Public functions are `rpaphp_get_sensor_state()` and `rpaphp_enable_slot()`. Internal helpers are `rtas_get_sensor_errno()` and `__rpaphp_get_sensor_state()`. The file defines PAPR-specific RTAS sensor error constants for unisolated/not-unisolated/unusable slots.

## Control Flow
`rpaphp_get_sensor_state()` tries to read `DR_ENTITY_SENSE`; if firmware reports that the slot must be powered/unisolated, it powers the slot on with `rtas_set_power_level()` and retries. During EEH recovery, `__rpaphp_get_sensor_state()` bypasses `rtas_get_sensor()` and calls `rtas_call()` directly so extended-delay return codes become `-EBUSY` instead of blocking recovery. `rpaphp_enable_slot()` reads slot power, reads presence, locates the PCI bus by OF node, records bus/device-list pointers, and if an adapter is present, initializes EEH and adds devices on an empty bus.

## State and Persistence Behavior
The code initializes `slot->state`, `slot->bus`, and `slot->pci_devs`. It may change RTAS slot power just to make sensor reads work. PCI devices added to the bus persist until hotplug disable or DLPAR removal.

## Dependencies and Integration Points
Depends on RTAS `get-sensor-state`, RTAS power-level calls, pSeries PCI DN/PHB structures, EEH PE state, PCI bus lookup by OF node, and `pci_hp_add_devices()`. Called by rpaphp discovery and hotplug enable paths.

## Risks
The EEH fast path only inspects the first child PDN under the PHB, so unusual topologies may not reflect the target slot's recovery state. Powering on a slot for sensor reads has side effects. `rpaphp_enable_slot()` requires present slots to have child OF nodes and fails otherwise. It only adds devices if the bus list is empty, assuming firmware/kernel topology consistency.

## Test Signals
Validate sensor reads for powered-on/off slots, RTAS busy/extended-delay behavior during EEH recovery, unusable slots, present slots without children, empty slots, PCI bus lookup failures, EEH init plus device add, and debug listing of configured devices.
