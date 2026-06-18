## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_mon.h

Purpose: declares Wi-Fi 7 monitor datapath entry points.

Important APIs: `ath12k_wifi7_dp_mon_process_ring()` services monitor rings for a MAC/RXDMA instance; `ath12k_wifi7_dp_mon_tx_parse_mon_status()` parses TX monitor status from an skb and can deliver monitor frames.

Control flow: none in the header. The functions are called from datapath SRNG service and common monitor code.

State and persistence: no state is owned; implementations mutate `ath12k_mon_data`, ring IDRs, and PPDU tracking structs.

Dependencies/integration: includes Wi-Fi 7 hardware definitions and relies on common `struct ath12k_dp`, `struct ath12k_pdev_dp`, `struct ath12k_mon_data`, NAPI, skb, and monitor mode enums.

Risks: enum return types expose HAL monitor status directly, so callers must handle both negative error-like values and status constants consistently.

Test signals: compile integration with `dp.c` and TX monitor callers; runtime monitor capture tests.
