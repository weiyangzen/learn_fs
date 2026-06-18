# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/Kconfig

## Purpose
This Kconfig file declares the build-time configuration surface for the `rtw88` Realtek 802.11ac mac80211 driver family. It separates the common core, transport modules, chip-family helper symbols, concrete adapter symbols, debug options, and LED support.

## Important symbols
`menuconfig RTW88` is the user-visible umbrella tristate and depends on `MAC80211`. Internal symbols include `RTW88_CORE`, `RTW88_PCI`, `RTW88_SDIO`, `RTW88_USB`, chip-family symbols such as `RTW88_8822B`, `RTW88_8822C`, `RTW88_8723X`, `RTW88_8703B`, `RTW88_8723D`, `RTW88_8821C`, `RTW88_88XXA`, `RTW88_8821A`, `RTW88_8812A`, and `RTW88_8814A`. Adapter symbols bind chip and bus support, for example `RTW88_8822BE` selects `RTW88_CORE`, `RTW88_PCI`, and `RTW88_8822B`, while `RTW88_8822BU` selects core, USB, and 8822B.

The adapter coverage includes PCI, SDIO, and USB variants for 8822B/8822C/8723D/8821C, plus 8723CS/8703B, 8821AU/8812AU, and 8814AE/8814AU. `RTW88_DEBUG` and `RTW88_DEBUGFS` add optional debugging. `RTW88_LEDS` defaults to `y` only when the LED class is built-in or compatible with mac80211.

## Control flow and build integration
Kconfig does not run code, but it controls which object lists in the sibling Makefile are reachable. Concrete device symbols use `depends on PCI`, `depends on MMC`, or `depends on USB`, then select the core, transport, and chip-family implementation needed by that adapter. This creates a composable matrix: one core module, one bus module, and one chip module combine into a concrete device module.

## State and persistence behavior
The only persistent behavior is kernel configuration state. Selections become part of `.config` and determine built-in versus module linkage. Because many intermediate symbols are non-prompt tristates, users generally choose adapter symbols rather than low-level core/transport symbols directly.

## Dependencies and integration points
The file integrates with Linux Kconfig, mac80211, bus subsystems (`PCI`, `MMC`, `USB`), `WANT_DEV_COREDUMP`, and LED class support. Its choices must match Makefile object names and source file availability. Device IDs in transport-specific files rely on the corresponding Kconfig symbols being enabled.

## Risks and test signals
The main risk is an incorrect `select` or dependency that lets a device symbol build without its transport or chip support, or prevents valid module combinations. Another risk is LED configuration mismatch when `LEDS_CLASS` and `MAC80211` are configured differently. Test signals include `allyesconfig`/`allmodconfig` builds, targeted builds for each adapter symbol, module names matching help text where promised, and dependency pruning when PCI, MMC, or USB support is disabled.
