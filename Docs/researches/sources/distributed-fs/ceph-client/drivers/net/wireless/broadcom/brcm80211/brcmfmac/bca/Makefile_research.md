# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/bca/Makefile

## Purpose
Builds the brcmfmac BCA firmware-vendor plugin module.

## Important APIs, Types, and Functions
Sets include paths for the plugin, parent brcmfmac directory, and shared include directory. Builds `brcmfmac-bca.o` from `core.o` and `module.o`.

## Control Flow, State, and Persistence
No runtime behavior. It controls module composition for the BCA vendor plugin.

## Dependencies and Integration Points
Used when brcmfmac is built modular and the parent Makefile descends into `bca/`. It must line up with module namespace imports in `module.c` and exported vendor ops from `core.c`.

## Risks and Test Signals
Risks are include path breakage or incomplete module object lists. Test modular brcmfmac builds and loading `brcmfmac-bca.ko`.
