## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_macsec.h

Purpose: MACsec offload declarations and state structures for Atlantic.

Important APIs/types: under `CONFIG_MACSEC`, defines maximum SC/SA counts, hardware SC/SA packing enum, common/RX-SA/TX-SA/TX-SC stats structures, `aq_macsec_txsc`, `aq_macsec_rxsc`, and `aq_macsec_cfg`. Declares `aq_macsec_ops` and init/free/enable/work/stat-count functions.

Control flow: header only.

State and persistence: `aq_macsec_cfg` is the in-memory state root: busy bitmaps, TX/RX SC arrays, per-SA key copies, software macsec object pointers, and cached counters.

Dependencies/integration: includes Linux `netdevice.h` and macsec core only when enabled; used by `aq_macsec.c`, `aq_ethtool.c`, and NIC lifecycle code.

Risks: fixed `AQ_MACSEC_MAX_SC` and `AQ_MACSEC_MAX_SA` define hardware/stat limits. Stored software pointers must remain valid under macsec core lifetime rules. Persistent key arrays need explicit lifecycle scrutiny.

Test signals: compile with MACsec on/off, ethtool stats with varying active SC/SA counts, and MACsec lifecycle operations.
