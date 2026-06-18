# sources/distributed-fs/ceph-client/net/6lowpan/debugfs.c

## Purpose
`net/6lowpan/debugfs.c` exposes 6LoWPAN runtime inspection and tuning through debugfs, primarily for IPHC context table entries and IEEE802154 short-address visibility.

## Important APIs, types, and functions
Exported-to-core functions are `lowpan_dev_debugfs_init()`, `lowpan_dev_debugfs_exit()`, `lowpan_debugfs_init()`, and `lowpan_debugfs_exit()`. Per-context files use `lowpan_ctx_flag_active_*`, `lowpan_ctx_flag_c_*`, `lowpan_ctx_plen_*`, and `lowpan_ctx_pfx_*` handlers. `lowpan_context_show()` summarizes active contexts, and `lowpan_short_addr_get()` exposes the IEEE802154 short address.

## Control flow
Global init creates `/sys/kernel/debug/6lowpan`. Device init creates a directory named for the netdevice, a `contexts` directory, a summary `show` file, and one directory per context id with `active`, `compression`, `prefix`, and `prefix_len` files. Writes validate boolean flags, prefix length <= 128, or an eight-field IPv6 prefix string, then update context fields under the context-table spinlock where needed. IEEE802154 devices also get an `ieee802154/short_addr` file read under RTNL.

## State and persistence
Debugfs reflects and mutates live per-device IPHC context table state: active flag, compression flag, prefix, and prefix length. It does not persist across device removal or reboot. Dentries are tracked through `lowpan_debugfs` and per-device `iface_debugfs`.

## Dependencies and integration points
The file depends on debugfs, seq_file helpers, user copy/parsing, RTNL for reading IEEE802154 short address, and the 6LoWPAN IPHC context definitions in `net/6lowpan.h`.

## Risks and invariants
Input validation is intentionally minimal but must reject invalid booleans, overlong prefixes, malformed prefix strings, and copy faults. Prefix and prefix length reads/writes must stay synchronized with IPHC compression/decompression readers through `ctx.lock`. Debugfs entries are diagnostic/control-plane only and should not be assumed present in production configs.

## Test signals
With `CONFIG_6LOWPAN_DEBUGFS`, create a 6LoWPAN device and read/write every context file. Verify invalid values return `-EINVAL`, prefix writes round-trip, active contexts appear in `contexts/show`, short address reads work for IEEE802154, and recursive removal happens on device unregister and module exit.
