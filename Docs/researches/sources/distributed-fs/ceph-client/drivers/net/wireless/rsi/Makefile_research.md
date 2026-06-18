# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/Makefile

Purpose: kernel build recipe for the RSI 91x driver family.

Important entries: `rsi_91x-y` lists common core objects: main, core scheduler, mac80211 glue, management, HAL, and power-save. Conditional additions include coexistence and debugfs objects. `rsi_usb-y` and `rsi_sdio-y` define bus-specific modules. `obj-$(CONFIG_RSI_91X)`, `obj-$(CONFIG_RSI_SDIO)`, and `obj-$(CONFIG_RSI_USB)` hook modules into Kbuild.

Control flow/integration: Kbuild composes `rsi_91x.o` from common objects and separate `rsi_usb.o`/`rsi_sdio.o` bus modules based on Kconfig selections.

State and persistence: build-time only.

Dependencies: names must match C source files and Kconfig symbols.

Risks/test signals: missing conditional object coverage can leave unresolved references, especially for coexistence/debugfs. Build tests across core-only, USB, SDIO, debugfs, and coex combinations validate the recipe.
