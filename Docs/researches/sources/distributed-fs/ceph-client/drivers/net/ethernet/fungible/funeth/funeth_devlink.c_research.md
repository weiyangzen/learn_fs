# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_devlink.c

## Purpose
Provides thin devlink allocation and registration wrappers for the Fungible Ethernet driver.

## Important APIs, Types, And Functions
Defines an empty `devlink_ops` table and wrapper functions `fun_devlink_alloc()`, `fun_devlink_free()`, `fun_devlink_register()`, and `fun_devlink_unregister()`. Allocation reserves private space sized as `struct fun_ethdev`.

## Control Flow
The main Ethernet probe path calls allocation to get a devlink object with embedded driver-private storage, registers it with devlink after initialization, unregisters during teardown, and frees the object when no longer needed.

## State And Persistence
The devlink object owns runtime kernel state and private storage for `struct fun_ethdev`. No persistent state or devlink parameters are defined in this file.

## Dependencies And Integration Points
Includes `funeth.h` and `funeth_devlink.h`; depends on `NET_DEVLINK` selected by Kconfig. `struct funeth_priv` also contains a `devlink_port` for per-port integration handled elsewhere.

## Risks
Because `devlink_ops` is empty, user-visible devlink functionality is limited to registration/port plumbing. The private allocation size couples devlink object lifetime to the Ethernet device wrapper.

## Test Signals
Probe/remove should show balanced devlink alloc/register/unregister/free. Devlink core should list the device/ports without custom ops, and teardown should be clean under failure paths before and after registration.
