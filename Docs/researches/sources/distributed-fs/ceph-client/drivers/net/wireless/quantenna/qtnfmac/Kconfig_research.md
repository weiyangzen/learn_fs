<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Kconfig

## Purpose
This Kconfig file defines the Quantenna FullMAC common symbol and PCIe transport option for QSR1000/QSR2000/QSR10g adapters.

## Important APIs, Types, And Functions
`config QTNFMAC` is a hidden tristate that depends on `QTNFMAC_PCIE` and mirrors the PCIe symbol's built-in/module state. `config QTNFMAC_PCIE` is the user-visible tristate, depends on `PCI` and `CFG80211`, selects `QTNFMAC`, `FW_LOADER`, and `CRC32`, and describes the two module outputs `qtnfmac.ko` and `qtnfmac_pcie.ko`.

## Control Flow
Selecting PCIe support enables the common qtnfmac core and PCIe transport build. The common symbol defaults to module or built-in according to the PCIe symbol.

## State And Persistence
The `.config` persists `CONFIG_QTNFMAC_PCIE` and derived `CONFIG_QTNFMAC`.

## Dependencies And Integration Points
Consumed by `qtnfmac/Makefile`, which splits common objects and PCIe-specific objects. Dependencies match the driver's cfg80211, PCI, firmware loader, and CRC usage.

## Risks
The common symbol depends on the PCIe symbol, so adding another bus requires revisiting dependency/default logic. Incorrect select/depend choices could expose build failures or omit firmware support.

## Test Signals
Kconfig tests should verify `QTNFMAC` follows `QTNFMAC_PCIE` for y/m, and that disabling PCI or CFG80211 hides PCIe support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/Kconfig -->
