# sources/distributed-fs/ceph-client/drivers/net/ethernet/realtek/Makefile

Purpose: Maps Realtek Kconfig symbols to driver objects and r8169 composite object parts.

Important rules: `8139cp.o` and `8139too.o` build from their respective config symbols. `r8169-y` always includes `r8169_main.o`, `r8169_firmware.o`, and `r8169_phy_config.o`; `r8169-$(CONFIG_R8169_LEDS)` conditionally adds LED support. `obj-$(CONFIG_R8169)` builds the composite `r8169.o`. `obj-$(CONFIG_RTASE)` descends into `rtase/`.

Control flow and integration: This file lets Kbuild combine multi-object r8169 pieces while keeping optional LED support controlled by config.

State and persistence: No runtime state. Build output reflects selected Kconfig symbols.

Risks and test signals: Risks are missing object pieces after source refactors or optional object linkage mismatches. Build tests should cover each driver as built-in/module and R8169 with and without LED support.
