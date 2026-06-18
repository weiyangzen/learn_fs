# sources/distributed-fs/ceph-client/net/batman-adv/multicast.h

## Purpose
Declares the multicast optimization interface and config-gated fallback behavior for builds without `CONFIG_BATMAN_ADV_MCAST`.

## APIs, Types, and Functions
Defines `enum batadv_forw_mode` with `BATADV_FORW_BCAST`, `BATADV_FORW_UCASTS`, `BATADV_FORW_MCAST`, and `BATADV_FORW_NONE`. When multicast is enabled it declares forwarding decision/send functions, lifecycle functions, netlink dump helpers, purge hooks, multicast tracker TVLV handling, packet header length calculation, header push, and multicast send. When disabled it provides inline stubs that force broadcast decisions, drop multicast send attempts, return no mesh info, and report unsupported dumps.

## Control Flow
Enabled builds route mesh TX through `batadv_mcast_forw_mode()` and then either `batadv_mcast_forw_send()` or `batadv_mcast_forw_mcsend()`. Disabled builds compile the same callers but make multicast optimization a no-op: mode selection returns broadcast, explicit send helpers free the skb and return drop, and lifecycle hooks do nothing.

## State and Persistence
The header owns no storage. It controls whether per-mesh multicast state and per-originator multicast list membership from the C files are reachable in a given build.

## Dependencies and Integration
Depends on `main.h`, netlink callback types, skb types, and integer types. It is included by `mesh-interface.c`, multicast implementation files, originator purge/free paths, and netlink mesh-info reporting.

## Risks
Stub semantics must match caller ownership expectations. In particular, disabled-build send stubs consume/free skbs, while `batadv_mcast_forw_mode()` forces broadcast so normal paths should rarely call them. Adding new multicast APIs requires matching stubs or non-mcast builds will fail.

## Test Signals
Build both `CONFIG_BATMAN_ADV_MCAST=y` and disabled configurations. Runtime disabled-build checks should show mesh operation still broadcasts multicast traffic, netlink multicast flag dumps return `-EOPNOTSUPP`, and no multicast worker or TVLV state is required.
