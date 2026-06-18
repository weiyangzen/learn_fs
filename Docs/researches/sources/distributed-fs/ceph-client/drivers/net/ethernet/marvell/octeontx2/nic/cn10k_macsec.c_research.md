# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/cn10k_macsec.c

## Purpose

`cn10k_macsec.c` implements CN10K MACsec hardware offload through the Linux `macsec_ops` interface. It allocates MCS hardware resources, programs TX/RX SecY policies, flow-id TCAM entries, SC CAM entries, SA keys and PN tables, tracks software-to-hardware mappings, reports MACsec stats, handles packet-number wrap events, and exposes `NETIF_F_HW_MACSEC`.

## Important APIs, Types, And Functions

- Policy and TCAM macros define MCS register fields for MAC DA/SA, EtherType, RX/TX SecY policy, cipher selectors, and SecTAG TCI bits.
- `cn10k_ecb_aes_encrypt()` derives the MACsec hash subkey from SAK using AES ECB over zeroes.
- Mapping helpers find `cn10k_mcs_txsc` and `cn10k_mcs_rxsc` entries in `pfvf->macsec_cfg` lists.
- Resource helpers allocate/free MCS FLOWID, SC, SECY, and SA ids through mailbox.
- Write helpers program RX/TX SecY policies, flow-id entries, SC CAM, SA policies, SA-to-SC maps, and PN tables.
- Stats helpers query/optionally clear SA/SC/SecY stats and accumulate software counters where hardware counters are shared.
- Create/delete helpers manage TXSC/RXSC resource lifetimes and all child SAs.
- `cn10k_mcs_ops` implements the Linux MACsec callbacks for open/stop, add/update/delete SecY, RXSC, RXSA, TXSA, and stats.
- `cn10k_handle_mcs_event()` reports TX PN wrap through `macsec_pn_wrapped()`.
- `cn10k_mcs_init()` and `cn10k_mcs_free()` install/uninstall MACsec offload support.

## Control Flow

Initialization checks `CN10K_HW_MACSEC`, allocates `cn10k_mcs_cfg`, initializes TX/RX SC lists, sets `NETIF_F_HW_MACSEC`, attaches `macsec_ops`, and asks AF to enable MCS TX PN wrap interrupts. Adding a SecY allocates TX flow id, TX SecY, RX SecY, and TX SC resources, caches software SecY and VLAN state, and immediately programs TX policy if the netdev is running. Opening a MACsec device programs the active TX SA, TX SecY, TX flow id, RX SecY, and active RXSC/RXSA resources.

TX SA add allocates a hardware SA, stores key/salt/SSCI in the driver, writes SA policy, writes PN, and links it to the TX SC if it is the encoding SA. RX SC add allocates RX flow id and SC; RX SA add allocates SA, stores key/salt/SSCI, writes policy/map, and writes PN. Updates change PNs, active bits, encoding SA linkage, flow enablement, and SecY policy. Delete paths disable flow ids, free SA/SC/SecY resources, unlink lists, and free memory.

Stats callbacks query hardware through mailbox. Some RX SecY/SC counters are cleared on read and accumulated in software because hardware counters are shared or policy-dependent. `cn10k_mcs_sync_stats()` snapshots affected counters before changing validation or replay-protect policy.

## State And Persistence

State lives in `pfvf->macsec_cfg`, with `txsc_list` and `rxsc_list` entries storing software pointers, hardware ids, key material, salt, SSCI, SA bitmaps, encoding SA, VLAN mode, last policy values, and accumulated stats. Hardware state persists in MCS resource allocation, TCAM entries, SecY policy tables, SC CAM, SA policy tables, SA maps, PN tables, counters, and interrupt configuration.

## Dependencies And Integration Points

The file depends on Linux MACsec, rtnl/RCU access conventions, AES helper routines, OTX2 mailbox APIs, MCS mailbox message types, and hardware capability discovery from `otx2_set_hw_capabilities()`. It integrates with `otx2_common.c` capability setup and mailbox up handlers for MCS events.

## Risks

- Several add paths allocate hardware resources and then return on later programming errors without fully unwinding the newly allocated/listed resources.
- Key material is stored in driver structures and not explicitly zeroed before `kfree()`.
- List operations do not show a local lock; MACsec core/rtnl serialization must be relied upon.
- Stats callbacks clear hardware counters and accumulate in software, so missed calls around policy changes can skew reported counters.
- `cn10k_mcs_init()` returns 0 even when PN wrap interrupt configuration fails, leaving offload enabled with reduced event reporting.
- Event handling walks TXSC/SA mappings without breaking after a match; duplicate or stale ids could produce wrong reporting.

## Test Signals

MACsec selftests with HW offload for AES-GCM-128/256 and XPN variants, VLAN device SecTAG offset, SecY open/stop/update/delete, TX/RX SC/SA add/update/delete, PN update and wrap events, replay protection, validate-frame modes, stats read/clear behavior, resource exhaustion, and unload cleanup are critical.
