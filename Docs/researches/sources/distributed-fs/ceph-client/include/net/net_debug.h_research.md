<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_debug.h -->
# sources/distributed-fs/ceph-client/include/net/net_debug.h

## Purpose
`net_debug.h` provides netdevice-aware logging helpers, `netif_msg_*` gated driver logging macros, dynamic-debug integration, verbose-debug stubs, and optional debug-network warning macros.

## Important APIs, types, and functions
It declares `netdev_printk` and severity wrappers, defines `netdev_*_once`, `netdev_dbg`, `netdev_vdbg`, `netif_printk`, `netif_*`, `netif_dbg`, `netif_cond_dbg`, `netif_vdbg`, and `DEBUG_NET_WARN_ON*`.

## Control flow
Callers log with a netdevice context and severity. Dynamic debug builds route debug output through `dynamic_netdev_dbg`; DEBUG builds emit directly; normal builds type-check arguments through dead code. `netif_*` macros first check the driver's message bitmap via `netif_msg_type` helpers.

## State and persistence
Only `*_once` macros create static per-callsite booleans in `.data..once`. Otherwise the header has no runtime state.

## Dependencies and integration points
It depends on bug/warn infrastructure, kernel log levels, dynamic debug, and netdevice message-level helpers. It integrates all network drivers with consistent device-prefixed logging.

## Risks and test signals
Risks include side effects in arguments compiled out, incorrect message-type names, once-state not reset across module lifetime expectations, and debug warnings disappearing without CONFIG_DEBUG_NET. Tests should build with dynamic debug, DEBUG, VERBOSE_DEBUG, CONFIG_DEBUG_NET on/off, and verify message gating.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_debug.h` completely for this pass (159 lines, 5352 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_debug.h -->
