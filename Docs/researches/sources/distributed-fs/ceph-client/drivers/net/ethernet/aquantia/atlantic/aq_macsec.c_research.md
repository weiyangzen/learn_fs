## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_macsec.c

Purpose: hardware MACsec offload implementation for Atlantic, exposing Linux `macsec_ops` and programming the MACsec Security System records.

Important APIs/types: implements locked `macsec_ops` wrappers for SecY, TX/RX SC, TX/RX SA add/update/delete, device open/stop, and stats. Uses `struct aq_macsec_cfg`, `aq_macsec_txsc`, `aq_macsec_rxsc`, and MSS API record types. Public helpers initialize/free/enable MACsec, run periodic work, count active SAs/SCs, and append ethtool stats.

Control flow: init checks firmware link capabilities for MACsec, allocates config, enables `NETIF_F_HW_MACSEC`, and installs ops. Adding a SecY rejects XPN, selects SA/SC packing based on `MACSEC_NUM_AN`, allocates a TX SC slot, and programs egress class/SC records if carrier/running. TX/RX SA add stores keys in driver memory and writes SA/key records when active. RX SC setup programs two preclass records: SCI-present and SCI-absent matching. Delete/clear paths can clear hardware, software, or both. Enable optionally sends firmware MACsec config, installs PAE ethertype bypass records, then reapplies all saved SC/SA state. Work checks TX SA PN expiration and notifies macsec core. Stats read common, SC, and SA counters and update software next-PN fields.

State and persistence: MACsec state persists in memory in `nic->macsec_cfg` across link/device transitions and is reapplied by `aq_macsec_enable()`/device-open hooks. Keys are stored in per-SA arrays and zeroed in temporary hardware record buffers with `memzero_explicit`, but the persistent key copies remain until config is freed or overwritten. All ops are serialized by `macsec_mutex`.

Dependencies/integration: depends on `CONFIG_MACSEC`, Linux macsec core, `aq_nic`, firmware MACsec request op, and `macsec/macsec_api.c` MSS hardware programming. `aq_ethtool.c` uses its counters and stats writer.

Risks: key lifetime and memory clearing require care because persistent key arrays are not explicitly scrubbed on free. Hardware slot packing depends on `MACSEC_NUM_AN`; changes to MACsec core assumptions can affect SC/SA index math. Many hardware operations are gated on carrier/running, so deferred reapply paths must be correct. Stats functions dereference RCU-protected SA pointers and update PN under SA locks. Some helper return values are ignored in apply paths.

Test signals: builds with `CONFIG_MACSEC`, `ip macsec` add/update/delete for SecY/RXSC/TXSA/RXSA, link down/up reapply, hardware offload packet encryption/decryption, PAE bypass, PN wrap notification, ethtool MACsec stats count/string alignment, and key deletion/free memory review.
