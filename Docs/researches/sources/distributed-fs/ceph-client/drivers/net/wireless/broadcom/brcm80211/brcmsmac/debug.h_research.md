# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/debug.h

Purpose: declares brcmsmac logging/debugfs APIs and convenience macros for categorized debug output.

Important APIs and macros: declares `__brcms_info()`, `__brcms_warn()`, `__brcms_err()`, `__brcms_crit()`, optional `__brcms_dbg()`, debugfs lifecycle/create functions, and macros that bind a `bcma_device` core to device logging. Category helpers cover info, mac80211, rx, tx, interrupt, DMA, and HT debug levels.

Control flow: when neither `CONFIG_BRCMDBG` nor `CONFIG_BRCM_TRACING` is enabled, `__brcms_dbg()` is an inline no-op. Other log wrappers always exist.

State and persistence: no state. Macros route runtime logs and trace events implemented in `debug.c`.

Dependencies and integration: depends on Linux device, BCMA, cfg80211/mac80211, and brcms main/mac80211 interface headers. Included by many brcmsmac implementation files.

Risks and test signals: debug macros assume a fully initialized `wlc`/core and the file explicitly warns against use before `brcms_c_attach()` succeeds. Tests should build all debug/tracing config combinations and exercise log paths before and after attach only where valid.
