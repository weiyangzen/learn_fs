# sources/distributed-fs/ceph-client/drivers/net/wireguard/netlink.h

Purpose: Declares WireGuard Generic Netlink module lifecycle functions.

Important APIs: `wg_genetlink_init()` registers the Generic Netlink family; `wg_genetlink_uninit()` unregisters it.

Control flow: Used by `main.c` after device initialization and before device uninitialization. The header has no executable flow.

State and persistence: No direct state; declared functions manage global Generic Netlink family registration.

Dependencies and integration points: Consumed by `main.c` and implemented in `netlink.c`.

Risks: Minimal, but init/uninit order matters because userspace can configure devices through the family once registered.

Test signals: Module load/unload and Generic Netlink family visibility.
