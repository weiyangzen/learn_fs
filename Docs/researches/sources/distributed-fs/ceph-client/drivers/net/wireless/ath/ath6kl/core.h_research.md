# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/core.h

## Purpose
`core.h` is the central ath6kl driver contract. It collects firmware naming/version constants, firmware capability flags, hardware parameter tables, driver state enums, per-VIF state, station/aggregation/key/cookie structures, the main `struct ath6kl`, and prototypes exported across core, cfg80211, WMI, HTC, HIF, aggregation, recovery, and diagnostic code. It is not an implementation file; its main behavioral importance is defining which state is shared and which locks/queues protect it.

## Important APIs, types, and functions
Key constants include firmware API names (`fw-2.bin` through `fw-5.bin`), AR6003/AR6004 firmware paths and board-data paths, receive buffer sizes, cookie limits, WMI timeout values, scan/listen defaults, and configuration flags such as `ATH6KL_CONF_ENABLE_11N`, `ATH6KL_CONF_ENABLE_TX_BURST`, and `ATH6KL_CONF_UART_DEBUG`. `enum ath6kl_fw_capability` defines the negotiated firmware feature bitmap, including P2P, scheduled scan, WOW multicast filtering, heartbeat polling, 64-bit rates, endpoint mapping, and checksum limitations.

The major state types are `struct ath6kl_vif`, `struct ath6kl`, `struct ath6kl_sta`, `struct ath6kl_cookie`, `struct target_stats`, `struct ath6kl_bmi`, `struct ath6kl_mbox_info`, RX aggregation structures (`aggr_info`, `aggr_info_conn`, `rxtid`), and key material structures. `ath6kl_vif_from_wdev()`, `ath6kl_priv()`, and `ath6kl_get_hi_item_addr()` are small helper APIs. The prototypes at the bottom define the cross-file integration surface for init/cleanup, WMI events, cfg80211 VIF stop, HTC RX/TX callbacks, diagnostics, firmware recovery, cookies, RX refills, and aggregation.

## Control flow and integration
`struct ath6kl` is the root object. Bus-specific code fills `hif_ops`, HTC attachment fills `htc_ops`, core initialization creates `htc_target` and `wmi`, and cfg80211/VIF paths hang interfaces from `vif_list`. WMI events update `ath6kl_vif` connection/scan/stats fields, while HTC invokes `ath6kl_rx()`, `ath6kl_tx_complete()`, `ath6kl_core_rx_complete()`, and `ath6kl_core_tx_complete()` for transport completion. Firmware boot and target diagnostic paths use `ath6kl_bmi`, firmware blobs in `ar->fw*`, mailbox information in `ar->mbox_info`, and target-type address helpers.

## State and persistence behavior
All state is in-memory kernel driver state. Persistence across operations is through `struct ath6kl` lifetime, per-VIF profiles, firmware capability bits, cached firmware image pointers, per-station AP-mode queues, aggregation reorder queues, target stats snapshots, and debug-only fields under `CONFIG_ATH6KL_DEBUG`. Locking contracts are partially documented: `ar->lock` protects AMSDU queues, cookies, and TX counters; `list_lock` protects VIF list membership; per-VIF `if_lock` protects stats/flags; `psq_lock` protects station power-save queues; `mcastpsq_lock` is noted as mostly redundant.

## Dependencies and integration points
The header depends on Linux netdevice, cfg80211, firmware loading, timers, semaphores, workqueues, SKBs, WMI, BMI, HTC, and target register definitions. It is included by most ath6kl implementation files and is therefore sensitive to include cycles; it also includes `htc.h`, while `hif.h` includes `core.h`, creating a tightly coupled local header graph.

## Risks and test signals
The main risks are stale lock documentation, shared mutable fields updated from workqueue/interrupt/cfg80211 contexts, firmware capability mismatches, and size/limit constants that must match target firmware contracts. Useful test signals include successful firmware boot across AR6003/AR6004 variants, VIF add/remove under concurrency, AP-mode station power-save queue behavior, aggregation reorder tests, suspend/WOW/resume transitions, heartbeat recovery, and exercising diagnostic read/write paths.
