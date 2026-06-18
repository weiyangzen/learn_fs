<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Kconfig

Purpose: Kconfig entries for mt76x2 common, PCIe, and USB drivers.

Important APIs/types/functions: symbols `MT76x2_COMMON`, `MT76x2E`, and `MT76x2U`. PCIe depends on `MAC80211` and `PCI`; USB depends on `MAC80211` and `USB` and selects `MT76x02_USB`; both select common code.

Control flow: build-time configuration only. Selecting a bus-specific symbol pulls in the shared mt76x2 and mt76x02 support modules needed by that transport.

State and persistence: no runtime state. It controls kernel configuration/module availability.

Dependencies/integration: Linux Kconfig, mt76 parent Kconfig, mac80211, PCI, USB, and the Makefile object split.

Risks: missing selects cause unresolved symbols; overly broad dependencies expose unsupported builds. Test signals include `allyesconfig`, modular builds for PCI and USB separately, and verifying help text/device coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Kconfig -->
