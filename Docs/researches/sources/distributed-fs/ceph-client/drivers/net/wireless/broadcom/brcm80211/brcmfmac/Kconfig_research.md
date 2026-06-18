# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/Kconfig

## Purpose
Defines brcmfmac FullMAC driver and bus/protocol feature options.

## Important APIs, Types, and Functions
Symbols are `BRCMFMAC`, protocol internals `BRCMFMAC_PROTO_BCDC` and `BRCMFMAC_PROTO_MSGBUF`, and bus options `BRCMFMAC_SDIO`, `BRCMFMAC_USB`, and `BRCMFMAC_PCIE`. SDIO and USB select BCDC; PCIe selects MSGBUF; all bus options select `FW_LOADER`.

## Control Flow, State, and Persistence
No runtime state. The selected bus options decide which transport code and protocol backend are compiled into `brcmfmac`.

## Dependencies and Integration Points
Depends on `CFG80211`, `MMC`, `USB`, `PCI`, and top-level `BRCMUTIL`. The bus selections align with object lists in the brcmfmac Makefile.

## Risks and Test Signals
Incorrect dependencies can build a transport without the needed subsystem or omit the matching protocol. Test modular and built-in combinations for SDIO, USB, PCIe, and multi-bus builds.
