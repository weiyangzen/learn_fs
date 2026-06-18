# sources/distributed-fs/ceph-client/net/batman-adv/Kconfig

## Purpose
`Kconfig` defines the build-time feature surface for the B.A.T.M.A.N. Advanced mesh networking module and optional subfeatures.

## Important Configuration Symbols
- `BATMAN_ADV`: tristate module/core option; selects `CRC32`.
- `BATMAN_ADV_BATMAN_V`: enables BATMAN V, gated to avoid unsupported `CFG80211=m` with built-in batman-adv; default yes.
- `BATMAN_ADV_BLA`: bridge loop avoidance; depends on `INET`, selects `CRC16` and `NET_CRC32C`.
- `BATMAN_ADV_DAT`: distributed ARP table; depends on `INET`.
- `BATMAN_ADV_MCAST`: multicast optimization; depends on `INET` and avoids built-in/module bridge mismatch.
- `BATMAN_ADV_DEBUG` and `BATMAN_ADV_TRACING`: developer logging and trace integration.

## Control Flow and Integration
These options control which objects the Makefile includes and which inline stubs are active in headers like `bat_v.h`. The BATMAN V option directly controls inclusion of `bat_v.c`, `bat_v_elp.c`, and `bat_v_ogm.c`.

## State and Persistence
Kconfig stores compile-time decisions only. Runtime persistence is affected indirectly by whether optional protocol state exists in compiled code.

## Dependencies
Uses kernel networking and tracing dependency symbols. The CFG80211 and BRIDGE constraints prevent invalid built-in/module link combinations.

## Risks and Test Signals
Risks are bad dependency expressions causing link failures or unavailable runtime features despite selected config. Test signals include allmodconfig/allyesconfig, `BATMAN_ADV=y` with `CFG80211=m`, `BATMAN_ADV=y` with `BRIDGE=m`, minimal `BATMAN_ADV` without optional features, and trace/debug builds.
