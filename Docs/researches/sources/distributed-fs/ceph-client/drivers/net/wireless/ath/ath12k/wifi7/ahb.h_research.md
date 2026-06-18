## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/ahb.h

Purpose: exposes Wi-Fi 7 AHB init/exit hooks with stubs for non-AHB builds.

Important APIs: `ath12k_wifi7_ahb_init()` and `ath12k_wifi7_ahb_exit()`.

Control flow: enabled builds call into `ahb.c`; disabled builds make init return success and exit do nothing so `core.c` can be shared across transport configurations.

State and persistence: none in the header.

Dependencies/integration: used by Wi-Fi 7 `core.c` module init/exit and depends on `CONFIG_ATH12K_AHB`.

Risks: stubbed success means module init can proceed with only PCI support; logs from `core.c` are needed to distinguish absent AHB support from successful AHB registration.

Test signals: compile and load Wi-Fi 7 module with `CONFIG_ATH12K_AHB` enabled and disabled.
