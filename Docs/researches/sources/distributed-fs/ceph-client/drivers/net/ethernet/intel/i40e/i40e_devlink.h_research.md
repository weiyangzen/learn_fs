# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_devlink.h

## Purpose

`i40e_devlink.h` declares the i40e devlink lifecycle interface used by probe, remove, and PF setup code.

## Important APIs, Types, And Functions

- Forward declaration: `struct i40e_pf`.
- `i40e_alloc_pf()` allocates a devlink instance and PF private data.
- `i40e_free_pf()` frees PF/devlink storage.
- `i40e_devlink_register()` and `i40e_devlink_unregister()` manage devlink registration.
- `i40e_devlink_create_port()` and `i40e_devlink_destroy_port()` manage the PF devlink port.

## Control Flow

The header defines ordering expectations rather than implementing them: allocate PF, initialize hardware/PF fields, register devlink, create the port, then destroy/unregister/free on teardown.

## State And Persistence

No state is owned by the header. It exposes functions that manage devlink-backed PF memory and runtime devlink objects.

## Dependencies And Integration Points

The header includes `<linux/device.h>` for allocation context and is paired with `i40e_devlink.c`. Probe/remove code includes it to avoid direct devlink implementation coupling.

## Risks

- Call-order mistakes can leak devlink resources or unregister ports after parent devlink teardown.
- Because `struct i40e_pf` is opaque here, callers must use the implementation contract rather than stack allocation.

## Test Signals

Build coverage catches prototype drift. Probe/remove and fault-injection tests around each lifecycle step are the main runtime signals.
