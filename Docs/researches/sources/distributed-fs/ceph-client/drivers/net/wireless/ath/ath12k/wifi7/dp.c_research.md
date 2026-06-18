## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp.c

Purpose: provides Wi-Fi 7 datapath architecture operations and the top-level NAPI service dispatcher for SRNG interrupt groups.

Important APIs/functions: `ath12k_wifi7_dp_device_alloc()` creates a `struct ath12k_dp` and installs `ath12k_wifi7_dp_arch_ops`; `ath12k_wifi7_dp_device_free()` frees it. The ops table wires TX completion, RX normal/error handling, monitor handling, REO commands, PN setup, fragment cleanup, and peer TID queue management. `ath12k_wifi7_dp_service_srng()` is the main per-interrupt-group service routine.

Control flow: service dispatch checks `dp->hw_params->ring_mask` for the interrupt group and drains rings in order: TX completions, RX error, WBM RX release errors, normal RX, monitor status/destination rings, REO status, and host-to-RXDMA refill. It decrements the NAPI budget after data-bearing RX/monitor work and exits early when exhausted.

State and persistence: the allocated `ath12k_dp` stores pointers to `ab`, `dev`, `hw_params`, HAL, and the ops table. Ring state and stats are owned by shared datapath structs initialized elsewhere.

Dependencies/integration: depends on common DP, RX/TX, monitor, HAL, and hardware parameter code. It is called by HIF interrupt/NAPI code through `dp->ops->service_srng`.

Risks: ring-mask ordering determines fairness and latency; TX completion is not budgeted, while RX/monitor paths are. The TODO for other interrupts indicates incomplete coverage for future SRNG types. Host-to-RXDMA refill passes zero count and relies on common refill behavior.

Test signals: NAPI budget exhaustion, interrupt groups with multiple ring bits, monitor mode rings for all radios/RXDMA instances, REO status callbacks, and refill under RX starvation.
