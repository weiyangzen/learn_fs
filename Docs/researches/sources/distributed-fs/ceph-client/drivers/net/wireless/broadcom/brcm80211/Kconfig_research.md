# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/Kconfig

## Purpose
Defines top-level Kconfig symbols for the brcm80211 family: common utilities, brcmsmac SoftMAC, brcmfmac FullMAC inclusion, tracing, and debug support.

## Important APIs, Types, and Functions
Symbols are `BRCMUTIL`, `BRCMSMAC`, `BRCMSMAC_LEDS`, `BRCM_TRACING`, and `BRCMDBG`, plus a `source` directive for `brcmfmac/Kconfig`. `BRCMSMAC` selects `BCMA`, `BRCMUTIL`, `FW_LOADER`, and `CORDIC`; `BRCMDBG` selects `WANT_DEV_COREDUMP` for brcmfmac.

## Control Flow, State, and Persistence
Kconfig has no runtime state. It controls which objects compile and which debug/tracing code is reachable.

## Dependencies and Integration Points
Integrates with kernel `MAC80211`, `CFG80211` through child config, `BCMA`, tracing, debug, LED, firmware loader, and device coredump infrastructure.

## Risks and Test Signals
Dependency mistakes lead to impossible build combinations or missing helper libraries. Test `allyesconfig`, modular brcmsmac/brcmfmac builds, tracing/debug toggles, and LED dependency combinations.
