# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/Makefile

## Purpose
Routes brcm80211 subdirectory builds and applies common debug compiler flags.

## Important APIs, Types, and Functions
Adds `-DDEBUG` when `CONFIG_BRCMDBG` is enabled and builds `brcmutil/`, `brcmfmac/`, and `brcmsmac/` according to `CONFIG_BRCMUTIL`, `CONFIG_BRCMFMAC`, and `CONFIG_BRCMSMAC`.

## Control Flow, State, and Persistence
No runtime behavior. It controls object inclusion at build time.

## Dependencies and Integration Points
Depends on Kbuild variable expansion and the Kconfig symbols defined in this directory and child directories.

## Risks and Test Signals
Risks are missing subdir objects or inconsistent debug flag propagation. Build all brcm80211 permutations as built-in and modules.
