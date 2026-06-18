# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/gmac.h

## Purpose
`gmac.h` defines the generic MAC abstraction for cxgb. It gives the core adapter code a uniform `struct cmac` and `struct cmac_ops` interface for different MAC chips, plus a shared statistics layout used by netdevice stats and ethtool.

## Important APIs, Types, and Functions
`struct cmac_statistics` contains transmit and receive RMON-style counters for octets, unicast/multicast/broadcast frames, pause frames, collisions, underruns, length/FCS/symbol/data/sequence/runt/jabber/internal errors, and jumbo frames/octets. `struct cmac_ops` is the MAC vtable: destroy/reset, interrupt enable/disable/clear/handler, RX/TX enable/disable, loopback, MTU, RX mode, speed/duplex/flow-control setters/getters, statistics update, and MAC address get/set.

`struct cmac` stores the statistics block, adapter pointer, ops pointer, and implementation-private instance pointer. `struct gmac` is a factory with a statistics-update period, `create()` callback, and board-level `reset()` callback. The header declares `t1_pm3393_ops` and `t1_vsc7326_ops`.

## Control Flow
The core driver obtains a `struct gmac` from board information, calls its factory/reset functions during module initialization, and then invokes `cmac->ops` from netdevice operations. Open calls MAC reset, address programming, RX mode programming, link start, and enable. Close disables RX/TX. Ettool and netdevice stats call `statistics_update()`. Link/pause/MTU/RX-mode changes call the appropriate vtable methods.

## State and Persistence
MAC state is runtime hardware state plus a software statistics accumulator in `struct cmac`. Implementation-specific state lives behind `cmac_instance`; for PM3393 it includes enabled direction bits, flow-control mode, and MAC address. Nothing is persisted across unload or hardware reset.

## Dependencies and Integration Points
The header includes `common.h` for `adapter_t` and `struct t1_rx_mode`. It is consumed by `cxgb2.c` and MAC implementations such as `pm3393.c` and `vsc7326.c`. It integrates with PHY link management through speed/duplex/flow-control callbacks and with ethtool through the common statistics layout.

## Risks
The vtable contract is broad and only partially implemented by some MACs, so callers must check optional callbacks such as `set_mtu` and `macaddress_set`. Statistics field ordering must stay synchronized with ethtool string/data emission in `cxgb2.c`. Implementations must preserve MAC enable state while reprogramming MTU, filters, and addresses; otherwise link traffic can be disrupted.

## Test Signals
Signals include MAC factory creation for each board type, open/close RX/TX enable sequencing, MAC address changes, multicast/promiscuous/all-multicast programming, MTU changes up to board limits, pause setting negotiation, link speed/duplex reporting, interrupt enable/clear/handler paths, and ethtool stats matching the `cmac_statistics` layout.
