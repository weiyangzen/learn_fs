# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/Makefile

This Makefile connects Broadcom wireless Kconfig symbols to kbuild subdirectories. It descends into `b43/` for `CONFIG_B43`, `b43legacy/` for `CONFIG_B43LEGACY`, and `brcm80211/` for either `CONFIG_BRCMFMAC` or `CONFIG_BRCMSMAC`.

There is no runtime state. Build behavior is entirely derived from `.config`, and kbuild uses the `obj-$(CONFIG_...) += dir/` lines to decide which directories to visit for built-in or module builds.

The file integrates with the parent wireless kbuild tree and must stay consistent with Broadcom Kconfig symbols. The main risks are stale symbol names or wrong directory mappings; brcm80211 intentionally serves two symbols from the same directory. Test signals are build traversal and module output for B43, B43LEGACY, BRCMFMAC, and BRCMSMAC configurations.
