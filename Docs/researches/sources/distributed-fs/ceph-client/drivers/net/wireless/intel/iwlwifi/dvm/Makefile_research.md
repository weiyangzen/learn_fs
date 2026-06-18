# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/Makefile

## Purpose
`dvm/Makefile` defines the object composition of the DVM firmware opmode module `iwldvm`, which supports older iwlwifi devices using DVM firmware.

## Important APIs, Types, and Build Targets
- Main target: `obj-$(CONFIG_IWLDVM) += iwldvm.o`.
- Core DVM objects: `main.o`, `rs.o`, `mac80211.o`, `ucode.o`, `tx.o`, `lib.o`, `calib.o`, `tt.o`, `sta.o`, `rx.o`, `eeprom.o`, `power.o`, `scan.o`, `rxon.o`, and `devices.o`.
- Optional objects: `led.o` under `CONFIG_IWLWIFI_LEDS`, `debugfs.o` under `CONFIG_IWLWIFI_DEBUGFS`.
- Include path: `ccflags-y += -I $(src)/../`.

## Control Flow and Integration
Kbuild links the listed objects into `iwldvm.o` when DVM support is enabled. The module integrates with the shared `iwlwifi` core and config files compiled by the parent Makefile. Optional LED/debugfs objects add runtime surfaces only when the corresponding Kconfig features are enabled.

## State and Persistence Behavior
No runtime state is stored in the Makefile. It determines which code contributes to the DVM module, affecting available runtime features and callbacks.

## Dependencies and Integration Points
It consumes `CONFIG_IWLDVM`, `CONFIG_IWLWIFI_LEDS`, and `CONFIG_IWLWIFI_DEBUGFS` from Kconfig and includes headers from the parent `iwlwifi` directory.

## Risks and Edge Cases
Missing objects can cause unresolved symbols or missing opmode functionality. Optional debugfs/LED objects must remain guarded by the same Kconfig symbols as their declarations and call sites. Include path spacing is accepted by kbuild but should remain consistent with local style if edited.

## Test Signals
Build `IWLDVM` built-in and modular, with LED/debugfs enabled and disabled; check modpost for unresolved symbols; boot/probe an older DVM-supported device; verify mac80211 registration, firmware load, scan, RXON, station, TX/RX, power, thermal, LED, and debugfs paths.
