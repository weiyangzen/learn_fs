## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/dp.h

Purpose: declares Wi-Fi 7 datapath allocation/free helpers.

Important APIs: `ath12k_wifi7_dp_device_alloc()` and `ath12k_wifi7_dp_device_free()`.

Control flow: none in the header; the implementation initializes Wi-Fi 7 DP ops.

State and persistence: no header-owned state. The returned object is heap runtime state attached to `ath12k_base`.

Dependencies/integration: includes common datapath definitions and Wi-Fi 7 hardware params so transport/core code can allocate the architecture-specific DP object.

Risks: callers must pair allocation/free and avoid using common DP ops before `dp->ops` is installed.

Test signals: compile users of the allocation API and probe/remove memory leak tests.
