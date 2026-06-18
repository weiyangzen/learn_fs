# sources/distributed-fs/ceph-client/drivers/power/reset/pwr-mlxbf.c

## Purpose
Mellanox/NVIDIA BlueField ACPI power-handling driver.

## Important APIs, Types, and Functions
`struct pwr_mlxbf`, IRQ handler, deferred reboot work, and ACPI platform probe.

## Control Flow
probe obtains the platform IRQ, initializes work, and requests IRQ; interrupt schedules reboot/power handling work that calls orderly reboot or low-power flow depending on GPIO/firmware event semantics.

## State and Persistence Behavior
state contains device, IRQ, and work item; pending work persists until flushed by driver core removal.

## Dependencies and Integration Points
ACPI IDs, BlueField GPIO dependencies, IRQ/workqueue, reboot helpers.

## Risks and Edge Cases
interrupt context is deliberately deferred; event storms can queue repeated work; behavior depends on platform firmware exposing the correct ACPI device and IRQ.

## Test Signals
ACPI match, IRQ trigger, work scheduling, reboot action, and unload with pending work.
