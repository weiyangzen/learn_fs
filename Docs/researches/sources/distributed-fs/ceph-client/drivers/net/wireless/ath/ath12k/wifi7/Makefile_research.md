## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/Makefile

Purpose: defines the Wi-Fi 7 ath12k kernel object composition.

Important APIs/targets: builds `ath12k_wifi7.o` when `CONFIG_ATH12K` is enabled, combining `core.o`, PCI/MHI/WMI/CE/HW/HAL/datapath objects, and conditionally `ahb.o` when `CONFIG_ATH12K_AHB` is enabled.

Control flow: Kbuild object lists determine which architecture-specific code is linked into the Wi-Fi 7 module. The AHB object is optional; PCI is part of the base Wi-Fi 7 list.

State and persistence: no runtime state; it controls build-time linkage.

Dependencies/integration: integrates Wi-Fi 7 subdirectory code with the broader ath12k driver and Kconfig symbols.

Risks: object list omissions produce unresolved symbols or missing hardware support. Because `pci.o` is unconditional in this object list, PCI dependencies must be satisfied by surrounding Kconfig/module structure.

Test signals: run build coverage for `CONFIG_ATH12K` with and without `CONFIG_ATH12K_AHB`, and modpost checks for unresolved Wi-Fi 7 symbols.
