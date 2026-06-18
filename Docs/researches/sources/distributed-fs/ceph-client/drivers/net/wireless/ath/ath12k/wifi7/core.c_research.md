## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/core.c

Purpose: is the Wi-Fi 7 module entry point and architecture glue for allocating the Wi-Fi 7 datapath object.

Important APIs/functions: `ath12k_wifi7_arch_init()` allocates and attaches `ab->dp`; `ath12k_wifi7_arch_deinit()` frees it. Module init/exit functions register/unregister AHB and PCI Wi-Fi 7 transports.

Control flow: module init attempts AHB first and PCI second, logging warnings for either failure. It returns failure only if both transports fail. Per-device architecture init allocates a `struct ath12k_dp` through `ath12k_wifi7_dp_device_alloc()` and stores it on `ath12k_base`.

State and persistence: static `ahb_err` and `pci_err` remember which transport registration succeeded so exit only unregisters successful transports. `ab->dp` is runtime heap state.

Dependencies/integration: integrates with common AHB/PCI registration, Wi-Fi 7 transport headers, datapath allocation, and Linux module init/exit.

Risks: if one transport fails due to a transient error, its exit hook is skipped based on static error state. `ath12k_wifi7_arch_init()` returns `-EINVAL` for allocation failure rather than `-ENOMEM`, which may obscure diagnostics.

Test signals: module load/unload across PCI-only, AHB-only, both-enabled, and both-failing builds; per-device probe/remove leak checks for `ab->dp`.
