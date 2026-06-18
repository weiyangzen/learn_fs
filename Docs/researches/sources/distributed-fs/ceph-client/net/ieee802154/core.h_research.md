## sources/distributed-fs/ceph-client/net/ieee802154/core.h

Purpose: private core definitions for cfg802154 registered-device management.

Important APIs/types/functions: `struct cfg802154_registered_device` wraps driver `cfg802154_ops`, global list linkage, internal PHY index, open-count wait queue, running-interface count, WPAN device list, generation counters, per-rdev WPAN device ID allocator, and the embedded `struct wpan_phy`. `wpan_phy_to_rdev()` converts from public `wpan_phy` to the private wrapper. Externs declare the global rdev list and generation, namespace switching, free helper, index lookup, and phy lookup.

Control flow and state: this header defines layout and invariants. The embedded `wpan_phy` must remain last and aligned because private driver data is derived relative to it by public APIs. `opencount`, `dev_wait`, and `wpan_dev_list` are managed in `core.c`; list readers/writers rely on RTNL/RCU as documented in comments.

Dependencies and integration points: includes `net/cfg802154.h`; used by nl802154, legacy netlink, rdev op wrappers, and core lifecycle code.

Risks: changing struct layout, especially moving `wpan_phy`, can break `wpan_phy_priv()` assumptions. The comments specify lock domains; violating them in users of the struct risks use-after-free or stale generation data.

Test signals: build-time layout users, PHY allocation/free with private data, nl802154 lookups by PHY index and WPAN dev ID, lockdep around RTNL-protected access.
