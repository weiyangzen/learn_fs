# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/Makefile

Purpose: object composition for MT7615/MT7663 kernel modules.

Important targets: builds `mt7615-common.o`, `mt7615e.o`, `mt7663-usb-sdio-common.o`, `mt7663u.o`, and `mt7663s.o` according to Kconfig symbols. `mt7615-common-y` includes `main.o`, `init.o`, `mcu.o`, `eeprom.o`, `mac.o`, `debugfs.o`, and `trace.o`, with optional `testmode.o`. `mt7615e-y` includes PCI/MMIO/DMA pieces and optional `soc.o` for MT7622.

Control flow: kbuild links common code into all relevant transports, then adds transport-specific bus and DMA implementations. Trace compilation gets `CFLAGS_trace.o := -I$(src)` so generated trace headers can include local paths.

State and persistence: no runtime state. Build composition determines which source files share a module namespace and which symbols must be exported for cross-object use.

Dependencies and integration: driven by `Kconfig` symbols and kbuild conventions. Connects common mac80211/MCU/MAC/EEPROM/debug code with PCI, SoC, USB, and SDIO transport files in the same driver family.

Risks: missing an object here can produce unresolved symbols or silently omit transport behavior. Common code exports are necessary because some functions are shared across modules/transports. Optional testmode compilation must stay consistent with declarations guarded by `CONFIG_NL80211_TESTMODE`.

Test signals: successful `M=drivers/net/wireless/mediatek/mt76/mt7615` builds across PCI, SoC, USB, SDIO, and testmode configs; generated module contents match selected Kconfig symbols.
