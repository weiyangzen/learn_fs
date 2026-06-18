# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dp_cmn.h

Purpose: Provides common DP definitions shared across ath12k devices and links, especially MLO-aware DP hardware grouping, vif/link-vif TX metadata, per-peer TX stats, peer creation parameters, rate-info export, and common peer/device lifecycle prototypes.

Important APIs and types: `MAX_DP_PEER_LIST_SIZE` sizes DP peer arrays to 16,384 to cover regular and MLO peer IDs. `struct ath12k_dp_hw` stores RCU peer pointers, a peer lock, and peer list. `struct ath12k_dp_hw_group` maps device IDs to DP roots. `struct ath12k_dp_link_vif` stores vdev ID, HAL address search flags, pdev/lmac IDs, AST info, TCL metadata, vdev-ID check state, and bank ID. `struct ath12k_dp_vif` stores TX encapsulation, key cipher, multicast/broadcast global sequence number, and per-link DP vif state. `struct ath12k_per_peer_tx_stats`, `ath12k_dp_peer_create_params`, and `ath12k_dp_link_peer_rate_info` carry peer stats and setup/rate data. Prototypes cover common DP device init/deinit, hardware-group assign/unassign, link-peer assign/unassign, rate-info fetch, and RX-stats reset. `ath12k_dp_vif_to_dp_link_vif()` maps a shared vif DP object plus link ID to link-specific state.

Control flow: No complex flow lives here; it defines storage and function contracts. Callers allocate/init common DP through `ath12k_dp_cmn_device_init()`, attach DP objects to an `ath12k_hw_group`, assign/unassign link peers as firmware peer map/unmap and mac80211 station events occur, and query/reset per-peer stats from debugfs/mac80211 paths.

State and persistence: Defines runtime state for DP peer tables, MLO hardware groups, link-vif TX configuration, multicast global sequence numbers, and per-peer rate/stat summaries. These are reconstructed on device/peer/vif setup and are not durable, but peer IDs and MLO group mappings must stay consistent with firmware while peers exist.

Dependencies and integration points: Includes `cmn_defs.h` and uses `ATH12K_MAX_DEVICES`, `ATH12K_NUM_MAX_LINKS`, mac80211 station/rate types, and ath12k DP peer structures declared elsewhere. It is included by `dp.h`, `dp.c`, `debugfs_sta.c`, and peer/RX/TX code that needs common MLO-aware DP state.

Risks: `MAX_DP_PEER_LIST_SIZE` is a memory and bounds contract; firmware peer IDs beyond it or incorrect MLO assumptions would cause lookup failures. `ath12k_dp_vif_to_dp_link_vif()` does no link ID bounds checking. Peer table updates require the documented locks/RCU discipline in implementation files. The per-peer TX stats TODO notes that stats placement may be temporary, increasing coupling.

Test signals: Assign/unassign single-link and MLO peers; validate peer IDs near regular and ML ranges; exercise per-link vif metadata for STA/AP/IBSS modes; read link peer rate info under traffic; reset RX stats through debugfs; and run lockdep/KCSAN around peer table updates and RCU readers.
