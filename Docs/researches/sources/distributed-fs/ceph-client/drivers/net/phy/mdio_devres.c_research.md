# sources/distributed-fs/ceph-client/drivers/net/phy/mdio_devres.c

## Purpose
`mdio_devres.c` provides device-managed helpers for allocating and registering MDIO buses. It lets MDIO bus provider drivers bind bus cleanup to the lifetime of their parent `struct device`, reducing manual error-path and detach cleanup.

## Important APIs, Types, And Functions
- `struct mdiobus_devres` stores the managed `struct mii_bus *`.
- `devm_mdiobus_alloc_size()` wraps `mdiobus_alloc_size()` and registers a devres action that calls `mdiobus_free()`.
- `__devm_mdiobus_register()` wraps `__mdiobus_register()` and registers a devres action that calls `mdiobus_unregister()`.
- `__devm_of_mdiobus_register()` conditionally wraps `__of_mdiobus_register()` when `CONFIG_OF_MDIO` is enabled.
- `mdiobus_devres_match()` verifies that a bus being registered was previously allocated by the matching managed allocation helper.

## Control Flow And State Behavior
Managed allocation creates a devres record, allocates the bus, stores it, and attaches the record to the parent device. Managed registration first checks that a matching allocation devres exists, allocates a second devres record for unregister, calls the underlying registration function, then stores the bus in the unregister record. On parent-device detach, devres unwinds in reverse order: unregister runs before free when both records were added normally.

The file persists no global state. Its only state is devres-managed records attached to parent devices. The underlying bus state transitions remain owned by `mdio_bus_provider.c`.

## Dependencies And Integration Points
The file depends on devres, phylib MDIO allocation/register APIs, and optional OF MDIO registration. It integrates with MDIO controller drivers that prefer `devm_mdiobus_alloc_size()`, `devm_mdiobus_register()`, or `devm_of_mdiobus_register()` wrappers exposed through headers/macros.

## Risks And Edge Cases
- Managed registration deliberately fails with `-EINVAL` if the bus was not allocated through the managed helper for that device, preventing mismatched cleanup ownership.
- If registration fails, the unregister devres record is freed and only the allocation/free record remains.
- Devres unwind ordering is important; manually unregistering/freeing a managed bus without removing devres would risk double cleanup.
- The OF helper exists only under `CONFIG_OF_MDIO`.

## Test Signals
Validate allocation failure returns `NULL`, managed registration rejects unmanaged buses, failed registration does not add unregister devres, successful detach unregisters before free, OF registration behaves the same under `CONFIG_OF_MDIO`, and parent-driver probe error unwinds leave no registered bus or leaked `mii_bus`.
