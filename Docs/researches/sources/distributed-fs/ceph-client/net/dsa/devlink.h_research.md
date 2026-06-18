# sources/distributed-fs/ceph-client/net/dsa/devlink.h

## Purpose
This private header declares the DSA core devlink lifecycle API used by switch and port setup.

## Important APIs, Types, And Functions
It declares `dsa_port_devlink_setup()`, `dsa_port_devlink_teardown()`, `dsa_switch_devlink_register()`, `dsa_switch_devlink_unregister()`, `dsa_switch_devlink_alloc()`, and `dsa_switch_devlink_free()`.

## Control Flow
No executable logic is present. `dsa.c` calls these functions as part of switch-tree setup and teardown.

## State And Persistence
No state is stored here; it describes functions that manage `ds->devlink` and `dp->devlink_port`.

## Dependencies And Integration Points
It forward-declares `struct dsa_port` and `struct dsa_switch` to keep include dependencies light.

## Risks And Edge Cases
Signature changes must stay synchronized with `devlink.c` and `dsa.c`; otherwise DSA core build breaks.

## Test Signals
Compile coverage and DSA probe/teardown tests exercise the declarations.
