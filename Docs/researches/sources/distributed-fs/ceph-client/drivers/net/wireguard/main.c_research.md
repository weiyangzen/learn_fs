# sources/distributed-fs/ceph-client/drivers/net/wireguard/main.c

Purpose: Provides WireGuard module initialization and exit sequencing plus module metadata and aliases.

Important APIs and functions: `wg_mod_init()` initializes allowedips slab state, optional DEBUG selftests, Noise constants, peer kmem cache, device RTNL/pernet/notifier plumbing, and Generic Netlink family. `wg_mod_exit()` unregisters Generic Netlink, device plumbing, peer cache, and allowedips slab state. Module macros expose license, description, author, version, RTNL link alias, and Generic Netlink family alias.

Control flow: Initialization proceeds from low-level data structures to externally visible APIs; each error branch unwinds only resources already initialized. In DEBUG builds, allowedips, packet counter, and ratelimiter selftests run before peer/device/netlink registration. Exit unwinds in reverse external-to-internal order.

State and persistence: Module load creates global slab caches, precomputed Noise initialization constants, notifier registrations, RTNL link kind, and Generic Netlink family. These persist until module unload.

Dependencies and integration points: Integrates with `allowedips`, `noise`, `peer`, `device`, `netlink`, and optional DEBUG selftest sources included elsewhere. Uses `WG_GENL_NAME` and `WIREGUARD_VERSION`.

Risks: Error labels must remain aligned with initialization order. DEBUG selftests can make module load fail. Netlink/device registration order affects userspace visibility of partially initialized functionality.

Test signals: Module load/unload, failure injection for each init step, DEBUG selftest pass/fail behavior, RTNL link autoload alias, and Generic Netlink family autoload alias.
