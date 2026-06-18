# sources/distributed-fs/ceph-client/drivers/net/netdevsim/macsec.c

Purpose: exposes a minimal simulated MACsec offload implementation for netdevsim, tracking SecY and RXSC objects and validating callback ordering.

Important APIs/types/functions: `nsim_macsec_init()` installs `macsec_ops` and advertises `NETIF_F_HW_MACSEC`. The callback table covers add/update/delete for SecY, RXSC, RXSA, and TXSA. Helpers `nsim_macsec_find_secy()` and `nsim_macsec_find_rxsc()` locate tracked SCI entries.

Control flow: SecY add checks capacity, finds a free entry, stores SCI, resets RXSC count, and increments global count. SecY update/delete require a matching SCI; delete clears the entry and count. RXSC add/update/delete first locate the parent SecY, then manage the per-SecY RXSC table. RXSA/TXSA operations mostly validate that the related SecY/RXSC exists and log debug messages.

State and persistence: `struct nsim_macsec` holds three SecY slots and one RXSC per SecY. It stores SCI and used/count flags only; SA key material and packet transforms are not simulated. State is reset at init and volatile.

Dependencies and integration: depends on `net/macsec.h`, netdev MACsec offload hooks, and netdev feature flags. Called from `netdev.c` PF device initialization and teardown.

Risks: it is intentionally shallow and validates object relationships rather than performing MACsec. Capacity constants are small, so tests must expect `-ENOSPC`. Teardown is empty, relying on MACsec core to have deleted offloaded objects before device destruction.

Test signals: create more than three SecYs or more than one RXSC, update/delete nonexistent SCI values, exercise RXSA/TXSA callbacks without parent objects, and confirm feature exposure after device creation.
