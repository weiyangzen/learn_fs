# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmutil/Makefile

Purpose: Builds the shared Broadcom 802.11 utility module.

Important APIs/build targets: Adds `../include` to the compiler include path, builds `brcmutil.o` when `CONFIG_BRCMUTIL` is enabled, and composes it from `utils.o` and `d11.o`.

Control flow and state: No runtime flow. The file controls which utility objects are linked and exposes their exported symbols to dependent Broadcom wireless drivers.

Dependencies and integration: Depends on Kbuild variables and `CONFIG_BRCMUTIL`. It integrates `brcmu_utils.h` packet queue/helpers and `brcmu_d11.h` chanspec conversion support into one module. Risks include missing include path breaking shared headers, stale object list causing exported symbol failures, and config changes affecting brcmsmac/brcmfmac consumers. Test signals include `CONFIG_BRCMUTIL=m/y` builds, module symbol export checks, and dependent driver link coverage.
