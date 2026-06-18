# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_rxtx.h

## Purpose
This header declares the Prestera RX/TX public interface. It lets switch setup code initialize and tear down SDMA packet I/O, lets port setup reserve DSA headroom, and exposes the transmit function used by Prestera netdev operations.

## Important APIs, types, and functions
The header forward-declares `struct prestera_switch` and `struct prestera_port`, includes `<linux/netdevice.h>` for `netdev_tx_t`, and exports `prestera_rxtx_switch_init()`, `prestera_rxtx_switch_fini()`, `prestera_rxtx_port_init()`, and `prestera_rxtx_xmit()`.

## Control flow
Callers are expected to initialize RX/TX once per switch before ports transmit packets, initialize each port to set required headroom, call `prestera_rxtx_xmit()` from the port netdev start-xmit path, and tear down switch RX/TX after ports are stopped.

## State and persistence behavior
The header exposes no state structs; all SDMA state is private to `prestera_rxtx.c` and attached to `sw->rxtx`. There is no persistence.

## Dependencies and integration points
It is the compile-time boundary between Prestera core/port netdev code and the SDMA implementation. The dependency on `netdevice.h` is needed for `struct sk_buff` through declarations and `netdev_tx_t`.

## Risks and edge cases
Because the implementation state is opaque, callers must obey lifecycle ordering. Calling transmit before switch init or after switch fini would dereference missing `sw->rxtx`. Port init currently only sets headroom, so later DSA headroom requirements must keep this API synchronized.

## Test signals
Build tests should catch prototype drift. Runtime tests should verify switch init/fini wraps all port xmit lifetimes and that port netdevs expose enough `needed_headroom` for DSA insertion.
