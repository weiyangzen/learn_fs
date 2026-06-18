## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_tx.h

Purpose: declares Wi-Fi 7 TX datapath entry points.

Important APIs: `ath12k_wifi7_dp_tx()`, `ath12k_wifi7_dp_tx_completion_handler()`, and `ath12k_wifi7_dp_tx_get_vdev_bank_config()`.

Control flow: no implementation here. The declarations connect common mac80211/DP code and the Wi-Fi 7 ops table to TX enqueue/completion logic.

State and persistence: no state is owned; functions operate on runtime pdev DP, link vif, skb, and base objects.

Dependencies/integration: relies on common ath12k structs being visible from includers and is consumed by Wi-Fi 7 `dp.c` and common TX setup.

Risks: signature changes ripple through the ops table and common datapath call sites. `is_mcast`, GSN, and link-vif parameters must stay aligned with MLO multicast behavior.

Test signals: compile all TX callers and run enqueue/completion tests that exercise each parameter combination.
