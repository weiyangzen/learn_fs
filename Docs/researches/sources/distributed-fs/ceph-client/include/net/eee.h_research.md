# sources/distributed-fs/ceph-client/include/net/eee.h

Read `sources/distributed-fs/ceph-client/include/net/eee.h` completely for this pass (35 lines, 832 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/eee.h_research.md`.

Purpose: defines a small kernel-internal Energy Efficient Ethernet configuration structure and conversion helpers to/from ethtool EEE configuration.

Important APIs/types/functions: `struct eee_config` stores `tx_lpi_timer`, `tx_lpi_enabled`, and `eee_enabled`. `eeecfg_mac_can_tx_lpi()` returns true only when EEE is globally enabled and TX LPI is enabled. `eeecfg_to_eee()` copies internal config to `struct ethtool_keee`; `eee_to_eeecfg()` copies ethtool config back.

Control flow: drivers keep `eee_config` internally, expose it through ethtool get/set paths using the conversion helpers, and use `eeecfg_mac_can_tx_lpi()` to decide whether MAC low-power idle transmission may be enabled.

State and persistence: the structure is runtime driver configuration; hardware or firmware may persist equivalent settings separately. This header has no storage.

Dependencies and integration points: depends on Linux types and ethtool EEE structures. It is used by Ethernet drivers, phylink/PHY EEE paths, and DSA switch EEE support.

Risks: `eee_enabled` is the master switch; enabling TX LPI alone is insufficient. Helpers copy only three fields, so drivers must manage advertised/supported/link-partner EEE state elsewhere. Missing include context for `struct ethtool_keee` relies on users including ethtool headers.

Test signals: ethtool EEE get/set round trips, MAC TX LPI gating, disabled master with TX LPI enabled, DSA/PHY EEE propagation, and driver suspend/resume preserving EEE config.
