<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_package.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_package.c

Purpose: Provides shared state and package-relative register access for multi-PHY packages, such as quad PHY transceivers that expose shared global registers and package-level private data.

Important APIs and functions: `phy_package_get_node()` and `phy_package_get_priv()` return package DT node and shared private storage. `__phy_package_read()`, `__phy_package_write()`, `__phy_package_read_mmd()`, and `__phy_package_write_mmd()` access C22/C45 registers at `base_addr + addr_offset`. `phy_package_init_once()` and `phy_package_probe_once()` provide per-package one-shot flags. `phy_package_join()`, `of_phy_package_join()`, `phy_package_leave()`, `devm_phy_package_join()`, and `devm_of_phy_package_join()` manage shared package membership and lifetime.

Control flow: `phy_package_join()` validates base address, takes `bus->shared_lock`, allocates a `phy_package_shared` entry in `bus->shared[base_addr]` on first use, optionally allocates shared private memory, sets refcount to one, or increments an existing entry when `priv_size` matches. `of_phy_package_join()` derives the package node from the PHY DT parent named `ethernet-phy-package`, reads its `reg` as base address, joins, and stores the node pointer. `phy_package_leave()` drops a DT node reference if present, decrements the shared refcount under the bus lock on last user, clears the bus slot, frees private memory, and nulls `phydev->shared`. Devm variants allocate a devres pointer and call leave automatically.

State and persistence: Maintains `struct phy_package_shared` instances referenced from each member `phydev->shared` and from `mii_bus->shared[base_addr]`, with `base_addr`, `np`, `refcnt`, `flags`, `priv_size`, and `priv`. Shared private data is runtime-only and driver-managed for locking. One-shot flags persist for the package lifetime.

Dependencies and integration points: Depends on OF, `linux/phy.h`, internal MDIO/MMD helpers from `phylib.h`, and bus-level `shared_lock`/`shared[]`. PHY drivers call these helpers during probe/config init to coordinate package-global initialization and register access.

Risks: All members of a package must use the same base address and private size; mismatches fail. Package-relative address bounds reject offsets that exceed `PHY_MAX_ADDR`, but callers must know the package map. Shared `priv` has no built-in locking beyond allocation/refcounting. `of_phy_package_join()` stores the package node and `phy_package_leave()` drops references for each member, so reference handling depends on balanced joins/leaves. MMD helpers assume the whole package is either C22 or C45.

Test signals: Join first and subsequent package members; mismatched `priv_size` and invalid base address failures; devm cleanup on probe failure; DT package node success and bad parent/name/reg failures; one-shot init/probe flags across multiple members; package-relative C22 and C45 register reads/writes at valid and invalid offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_package.c -->
