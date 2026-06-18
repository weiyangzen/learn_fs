# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rswitch_l2.h

## Purpose
This header declares the R-Switch L2 offload interface used by the main R-Switch driver. It exposes bridge offload recalculation and notifier lifecycle functions while hiding switchdev implementation details in `rswitch_l2.c`.

## Important APIs, Types, And Functions
- `rswitch_update_l2_offload(struct rswitch_private *priv)` recalculates and applies hardware learning/forwarding state for all ports.
- `rswitch_register_notifiers()` registers netdevice and switchdev notifier blocks.
- `rswitch_unregister_notifiers()` unregisters those notifier blocks.

## Control Flow
`rswitch_main.c` includes this header, registers notifiers during probe after hardware/ports initialize, calls `rswitch_update_l2_offload()` from port open/stop when a bridge master is present, and unregisters notifiers during remove before deinitializing driver state.

## State And Persistence
The header defines no storage. It operates on `struct rswitch_private` state declared in `rswitch.h` and maintained by `rswitch_main.c`/`rswitch_l2.c`. There is no persistent state.

## Dependencies And Integration Points
It depends on `struct rswitch_private` being declared before use by including `rswitch.h` in source files. It forms the internal build boundary between `rswitch_main.o` and `rswitch_l2.o`, both linked into `rswitch.o`.

## Risks And Edge Cases
- The header itself does not forward-declare `struct rswitch_private`; include order must provide it.
- Notifier registration is global, so probe/remove ordering must avoid double registration or unregistering while callbacks can still reference freed driver state.
- Main driver callers must call `rswitch_update_l2_offload()` when port open state changes, otherwise hardware offload can remain stale.

## Test Signals
Compile `rswitch_main.c` and `rswitch_l2.c` together, verify probe registers notifiers exactly once, remove unregisters them before state teardown, and bridge membership/open/stop events cause visible forwarding-engine register updates.
