# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-arasan.c

Purpose: this file provides `sdhci_pci_fixes` for Arasan PCI SDHCI controllers with an integrated PHY. It initializes and retunes the PHY across legacy, high-speed, HS200, DDR50, HS400, and enhanced-strobe modes.

Important APIs, types, and functions: `struct arasan_host` stores the last programmed clock. PHY access is via indirect registers `PHY_ADDR_REG` and `PHY_DAT_REG`. `arasan_phy_write`, `arasan_phy_read`, `arasan_phy_addr_poll`, and `arasan_phy_sts_poll` implement short timeout polling. `arasan_phy_init` powers/calibrates IO pads, enables command/data/strobe/clock paths, and sets legacy mode. `arasan_phy_set` programs mode, tap delays, drive type, trim, DLL enable, and waits for DLL ready.

Control flow: PCI core calls `arasan_pci_probe_slot()` from the fixup table. That marks the card non-removable and 8-bit capable, then initializes the PHY. The local `set_clock` callback first delegates to `sdhci_set_clock()` and then calls `arasan_select_phy_clock()`, which skips redundant programming when `ios.clock` has not changed, maps clock to DLL frequency select, and programs PHY mode according to MMC timing or enhanced-strobe callback presence.

State and persistence: the only software state is `chg_clk`, used to avoid repeated PHY programming. Hardware state is in the PHY registers and DLL. No persistent data is written.

Dependencies and integration points: this file is not a standalone module; it exports `const struct sdhci_pci_fixes sdhci_arasan` consumed by `sdhci-pci-core.c`. It depends on `sdhci-pci.h`, SDHCI core callbacks, PCI device ID matching, and MMC timing state.

Risks: PHY polling timeouts are only 100 us, and most callers collapse errors to `-EBUSY` or `-ENODEV`; marginal hardware may fail probe or high-speed switching. `arasan_select_phy_clock()` ignores return values from `arasan_phy_set()`, so runtime PHY programming failures after probe are not propagated. Enhanced-strobe selection is inferred from presence of the MMC callback, not directly from timing alone.

Test signals: probe on Arasan PCI eMMC, PHY calibration completion, each timing mode transition, 50/100/200 MHz clock changes, HS400 and enhanced-strobe operation, DLL-ready timeout behavior, and suspend/resume through PCI core are the useful signals.
