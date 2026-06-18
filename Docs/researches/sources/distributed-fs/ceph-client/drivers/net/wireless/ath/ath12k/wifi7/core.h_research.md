## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/core.h

Purpose: declares Wi-Fi 7 architecture init/deinit hooks used by transport drivers.

Important APIs: `ath12k_wifi7_arch_init()` and `ath12k_wifi7_arch_deinit()`.

Control flow: no implementation; transports call these hooks during probe/remove through family ops.

State and persistence: none in the header. The implementation owns `ab->dp` lifecycle.

Dependencies/integration: included by Wi-Fi 7 AHB/PCI paths and the module core.

Risks: callers must ensure `struct ath12k_base` is fully initialized enough for datapath allocation before calling init, and must not double-free with deinit.

Test signals: compile transport code and probe/remove sequencing tests.
