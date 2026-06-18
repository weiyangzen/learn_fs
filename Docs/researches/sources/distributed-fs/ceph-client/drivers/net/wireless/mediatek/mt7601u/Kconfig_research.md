# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/Kconfig

## Purpose
Adds the kernel configuration option for the MT7601U USB Wi-Fi driver.

## Important APIs, Types, And Functions
Defines `config MT7601U` as a tristate with prompt `MediaTek MT7601U (USB) support`, depending on `MAC80211` and `USB`. Help text states it supports MT7601U-based USB wireless dongles.

## Control Flow
No runtime flow. Kconfig selection controls whether the mt7601u object is built in, as a module, or omitted.

## State And Persistence
The persistent state is the kernel build configuration symbol.

## Dependencies And Integration Points
Integrates with the kernel wireless driver Kconfig tree, mac80211, and USB subsystems. The Makefile consumes `CONFIG_MT7601U`.

## Risks
Missing dependencies would allow invalid builds; extra dependencies would hide the driver. The option does not select firmware or helper libraries, so packaging must handle runtime firmware separately if needed by adjacent code.

## Test Signals
`CONFIG_MT7601U=m/y` builds the driver only when MAC80211 and USB are enabled, and disabling the symbol omits the module.
