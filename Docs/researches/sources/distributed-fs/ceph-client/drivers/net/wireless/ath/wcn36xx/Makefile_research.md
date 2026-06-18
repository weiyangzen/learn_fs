<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Makefile

Purpose: Describes the object composition for the `wcn36xx` kernel module.

Important APIs/types/functions: Sets `obj-$(CONFIG_WCN36XX) := wcn36xx.o`, includes `main.o`, `dxe.o`, `txrx.o`, `smd.o`, `pmc.o`, `debug.o`, and `firmware.o`, and conditionally includes `testmode.o` for `CONFIG_NL80211_TESTMODE`.

Control flow: Kbuild uses these object lists to link the module.

State and persistence: Build metadata only.

Dependencies and integration points: Mirrors source-level module boundaries: DXE DMA, TX/RX, SMD firmware control, power management, debugfs, firmware, and optional testmode.

Risks and test signals: Risks are missing objects after source changes or optional testmode link failures. Test signals are module builds under `CONFIG_WCN36XX=m/y` and `CONFIG_NL80211_TESTMODE` toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/Makefile -->
