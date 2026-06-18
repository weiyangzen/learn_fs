## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ahb.c

Purpose: supplies Wi-Fi 7 AHB family registration and hardware-revision probing for IPQ5332/IPQ5424 platform devices.

Important APIs/functions: `ath12k_wifi7_ahb_init()` registers a family driver via `ath12k_ahb_register_driver()`, `ath12k_wifi7_ahb_exit()` unregisters it, and `ath12k_wifi7_ahb_probe()` fills AHB-specific runtime fields then calls `ath12k_wifi7_hw_init()`.

Control flow: platform matching uses `qcom,ipq5332-wifi` and `qcom,ipq5424-wifi` compatible strings. Probe retrieves the already allocated `ath12k_base`, maps OF match data to `hw_rev`, sets user PD/scm-auth behavior, memory mode, and hardware revision, then initializes Wi-Fi 7 hardware parameters.

State and persistence: runtime state is stored in `struct ath12k_ahb` (`userpd_id`, `scm_auth_enabled`) and `struct ath12k_base` (`target_mem_mode`, `hw_rev`). It is recreated on probe.

Dependencies/integration: depends on the generic parent AHB framework in `../ahb.h`, platform OF matching, Qualcomm MDT/SCM-related platform support, Wi-Fi 7 `hw.h`, `dp.h`, and `core.h`.

Risks: IPQ5424 reuses `ATH12K_IPQ5332_USERPD_ID`, which may be intentional but should be hardware-validated. Unsupported OF data returns `-EOPNOTSUPP`. AHB registration failure prevents that transport while PCI can still initialize at module level.

Test signals: device-tree match/probe on IPQ5332 and IPQ5424, scm-auth path coverage, hardware init failure unwinding, and module load/unload with `CONFIG_ATH12K_AHB`.
