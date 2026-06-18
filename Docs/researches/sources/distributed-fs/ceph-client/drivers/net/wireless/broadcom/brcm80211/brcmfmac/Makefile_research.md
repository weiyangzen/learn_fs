# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/Makefile

## Purpose
Builds the brcmfmac FullMAC driver from core, protocol, bus, debug, firmware-vendor, OF, DMI, and ACPI objects.

## Important APIs, Types, and Functions
The base `brcmfmac-objs` list includes cfg80211, chip, firmware interface, event handling, P2P, protocol, common, core, firmware, fwvid, feature, BT coexistence, vendor, PNO, and XTLV objects. Conditional lists add BCDC/fwsignal, MSGBUF/rings/flowring, SDIO, USB, PCIe, debug, tracing, OF, DMI, and ACPI. When `BRCMFMAC=m`, vendor folders `wcc/`, `cyw/`, and `bca/` build as modules; otherwise their core objects are linked into brcmfmac.

## Control Flow, State, and Persistence
No runtime state. It determines which vendor ops are linked versus separated into plugin modules and which protocol/bus functions are available.

## Dependencies and Integration Points
Uses `ccflags-y` include paths for brcmfmac and shared include headers. Must match Kconfig protocol and bus selections and module namespace expectations from vendor modules.

## Risks and Test Signals
Risks include missing object dependencies, wrong built-in versus module vendor linking, and include path drift. Test SDIO/USB/PCIe builds, debug/tracing builds, ACPI/OF/DMI combinations, and modular vendor plugin loading.
