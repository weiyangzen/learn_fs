# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/ethtool.c

## Purpose
`falcon/ethtool.c` implements the legacy Falcon `ef4_ethtool_ops` table. It provides ethtool support for driver info, register dumps, message level, link settings, self-tests, stats, identify LED, IRQ coalescing, ring sizing, pause settings, Wake-on-LAN, reset, RX classification filters, RSS indirection, RSS hash fields, and module EEPROM/module info.

## Important APIs, Types, and Functions
The file defines `struct ef4_sw_stat_desc`, software stat descriptor macros, helpers for integer/atomic stat reads, and the exported `const struct ethtool_ops ef4_ethtool_ops`. Key handlers include `ef4_ethtool_get_link_ksettings()`, `ef4_ethtool_set_link_ksettings()`, `ef4_ethtool_self_test()`, `ef4_ethtool_get_sset_count()`, `ef4_ethtool_get_strings()`, `ef4_ethtool_get_stats()`, `ef4_ethtool_get/set_coalesce()`, `ef4_ethtool_get/set_ringparam()`, `ef4_ethtool_get/set_pauseparam()`, RX NFC get/set helpers, RSS get/set helpers, module EEPROM/info helpers, and reset/WOL/LED handlers.

## Control Flow
Self-test flow mirrors the newer shared implementation but uses Falcon `ef4_*` types and optional PHY-specific external tests. Stats flow appends NIC hardware stats, aggregate software counters, and per-channel TX/RX packet counts. Coalescing get/set maps the hardware's shared event-queue moderation model into ethtool's RX/TX and IRQ fields, then pushes moderation to every channel. Ring set validates RX/TX limits, enforces driver minimums, and calls `ef4_realloc_channels()`.

RX classifier get translates an `ef4_filter_spec` back to ethtool flow specs for TCP/UDP IPv4/IPv6, user IPv4/IPv6, and Ethernet flows, including VLAN extension masks. RX classifier set validates user-provided masks, queue/drop cookies, and location semantics, builds a manual filter spec, inserts it, and returns the allocated location. RSS support is Falcon-revision aware: pre-B0 or single-channel devices report no indirection table, and B0 supports Toeplitz RSS without key changes through this interface.

## State and Persistence
The file reads and mutates live `struct ef4_nic` state: `msg_enable`, `wanted_fc`, `link_advertising`, queue sizes, IRQ moderation fields, RX indirection table, manual filter table, WOL settings, and PHY module data. `mac_lock` serializes PHY/MAC, pause, link, and module EEPROM operations. `stats_lock` protects stat snapshots.

## Dependencies and Integration Points
It depends on Falcon driver headers (`net_driver.h`, `workarounds.h`, `selftest.h`, `efx.h`, `filter.h`, `nic.h`), Linux ethtool/netdevice/rtnetlink APIs, MDIO restart helpers, NIC-type callbacks, PHY operations, filter APIs, and reset code in `efx.c`. The ops table is installed in `ef4_register_netdev()`.

## Risks
The file duplicates much of the newer `ethtool_common.c` logic with legacy names, so fixes can diverge between Falcon and non-Falcon paths. String/count/data ordering must remain synchronized. Flow classification only accepts exact masks for supported fields and can reject valid-looking ethtool requests unsupported by hardware. Coalescing compatibility with legacy `*_irq` fields is subtle. RSS key changes are unsupported here, and pre-B0 hash behavior is intentionally limited due to hardware issues.

## Test Signals
Use `ethtool -i`, `-d`, `-S`, `-t`, `-c/-C`, `-g/-G`, `-a/-A`, `-s`, `-p`, `-n/-N`, `-x/-X`, `--show-module`, and WOL commands on Falcon hardware or a targeted test harness. High-value regressions include string/count alignment, ring resize rollback, invalid RX classifier masks, queue-drop filters, RSS disabled on pre-B0/single-channel devices, pause autoneg rejection, and module EEPROM unsupported PHY paths.
