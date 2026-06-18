# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/Kconfig

## Purpose
Adds the kernel configuration option for TI WiLink 8 support.

## Important APIs, types, and functions
- `config WL18XX` is a tristate option labeled "TI wl18xx support".
- It depends on `MAC80211` and selects the common `WLCORE` module.

## Control flow
No runtime control flow. Build-system selection causes the wl18xx lower-driver module to be compiled when enabled and ensures wlcore is present.

## State and persistence behavior
No runtime state. The selected Kconfig value persists in the kernel build configuration.

## Dependencies and integration points
Integrates with Linux Kconfig, mac80211, and the common TI `WLCORE` dependency. The corresponding Makefile builds `wl18xx.o` when `CONFIG_WL18XX` is enabled.

## Risks and test signals
The main risk is missing required dependencies or failing to select wlcore. Build tests should cover builtin and module builds with `CONFIG_WL18XX=m/y`, and disabled builds should omit wl18xx objects cleanly.
