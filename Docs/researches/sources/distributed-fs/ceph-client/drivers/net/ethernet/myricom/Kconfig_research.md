# sources/distributed-fs/ceph-client/drivers/net/ethernet/myricom/Kconfig

Purpose: Kconfig menu for Myricom Ethernet devices, especially the Myri-10G PCI driver and optional Direct Cache Access support.

Important symbols: `NET_VENDOR_MYRI` depends on `PCI && INET` and gates the menu. `MYRI10GE` is a tristate selecting `FW_LOADER` and `CRC32`. `MYRI10GE_DCA` is a boolean depending on `MYRI10GE`, `DCA`, and a built-in/module compatibility expression.

Control flow: configuration-only. Enabling `MYRI10GE` builds the driver and exposes module firmware dependencies; enabling DCA compiles additional DCA notifier and tag-writing paths.

State and persistence: generated `.config` controls built-in/module inclusion and optional DCA behavior.

Dependencies and integration: ties to the Myricom Makefile and kernel firmware loader. Help text documents external firmware requirements for older EEPROMs.

Risks: DCA dependency must avoid built-in driver depending on module-only DCA. Firmware loader and CRC32 selects are required by `myri10ge.c` hotplug firmware validation.

Test signals: Kconfig resolution for `MYRI10GE=y/m/n`, DCA enabled/disabled, and module build containing `MODULE_FIRMWARE` entries.
