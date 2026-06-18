# sources/distributed-fs/ceph-client/net/6lowpan/6lowpan_i.h

## Purpose
`net/6lowpan/6lowpan_i.h` is the private header shared by the 6LoWPAN core, debugfs, neighbor discovery, and IPHC code. It centralizes link-layer type checks and optional debugfs hooks.

## Important APIs, types, and functions
`lowpan_is_ll()` checks the `struct lowpan_dev` link-layer type after the caller has established `dev->type == ARPHRD_6LOWPAN`. The header declares `lowpan_ndisc_ops`, `addrconf_ifid_802154_6lowpan()`, and debugfs lifecycle functions. When `CONFIG_6LOWPAN_DEBUGFS` is disabled, static inline no-op debugfs stubs keep core code unconditional.

## Control flow
The only runtime logic is the inline link-layer comparison and, depending on configuration, calls either into debugfs implementation functions or no-op stubs.

## State and persistence
This header owns no state. It exposes access to per-device `lowpan_dev(dev)->lltype` and declares functions that manipulate per-device context/debugfs state elsewhere.

## Dependencies and integration points
It depends on `linux/netdevice.h` and `net/6lowpan.h`. It connects `core.c`, `debugfs.c`, `iphc.c`, and `ndisc.c` without exporting these private helpers to unrelated networking code.

## Risks and invariants
Callers must only use `lowpan_is_ll()` on 6LoWPAN netdevices because it dereferences `lowpan_dev(dev)`. The debugfs stubs must match the real function signatures so configuration changes do not alter call sites.

## Test signals
Build both with and without `CONFIG_6LOWPAN_DEBUGFS`, and exercise registration of IEEE802154 and BTLE 6LoWPAN devices to ensure `lowpan_is_ll()` dispatch paths match the link type.
