# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/Kconfig

## Purpose
Kconfig entry for the MT7603E PCIe and MT76x8 SoC WLAN driver.

## Important APIs, Types, And Functions
- `config MT7603E` defines a tristate driver option named "MediaTek MT7603E (PCIe) and MT76x8 WLAN support".
- It selects `MT76_CORE` and depends on `MAC80211` and `PCI`.
- Help text documents support for MT7603E PCIe devices and MT7628/MT7688 WLAN core devices, with 802.11n 2x2 up to 300 Mbps.

## Control Flow
Build-time only. Enabling this option causes the Makefile to build `mt7603e.o` and include the mt7603 driver in-kernel or as a module.

## State And Persistence
No runtime state. The chosen Kconfig value persists in the kernel build configuration.

## Dependencies And Integration Points
Integrates with the kernel wireless stack through `MAC80211`, with PCI support, and with the mt76 core selected by `MT76_CORE`.

## Risks
The hard `depends on PCI` means pure SoC users still need PCI enabled in this tree even though the help mentions MT7628/MT7688 SoC WLAN. Misconfigured builds will omit the driver entirely.

## Test Signals
Validate `allyesconfig`, module build, and target platform configs. Confirm `CONFIG_MT7603E=m` builds `mt7603e.ko` and pulls in mt76 core dependencies.
