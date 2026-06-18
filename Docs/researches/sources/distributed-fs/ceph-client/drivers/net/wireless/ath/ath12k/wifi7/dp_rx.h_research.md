## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp_rx.h

Purpose: declares Wi-Fi 7 RX datapath architecture hooks.

Important APIs: declarations cover normal/error/WBM RX processing, REO status handling, RXDMA ring selector configuration, PN check command setup, REO queue assignment/update/cache flush, link descriptor return, fragment cleanup, queue-reference setup/reset, peer TID deletion, MPDU validity checks, and RX TID delete handling.

Control flow: the header groups functions consumed by the Wi-Fi 7 DP ops table and common peer/key/RX setup code.

State and persistence: no state is owned. Callers pass `ath12k_dp`, `ath12k_base`, peer, TID, and queue structs whose state is mutated by `dp_rx.c`.

Dependencies/integration: includes common core/RX headers and Wi-Fi 7 HAL RX descriptor definitions. It is the contract between common ath12k datapath code and the Wi-Fi 7-specific RX implementation.

Risks: broad API surface increases the chance of inconsistent locking assumptions; for example fragment cleanup requires `dp_lock` in implementation. New chip support must add matching ring selector declarations and hw-param wiring.

Test signals: compile all callers, lockdep around fragment/REO paths, and chip-specific RXDMA setup coverage.
