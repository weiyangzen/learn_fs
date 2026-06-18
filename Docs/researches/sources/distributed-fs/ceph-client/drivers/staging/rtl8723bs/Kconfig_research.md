# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/Kconfig

## Purpose
Kconfig entry for the Realtek RTL8723BS SDIO wireless LAN staging driver.

## Important APIs, Types, And Functions
Defines `RTL8723BS` as a tristate option depending on `WLAN`, `MMC`, `CFG80211`, and `m`, and selecting AES, ARC4, and crypto utility libraries.

## Control Flow
When enabled as a module, Kbuild builds the large `r8723bs` composite driver for SDIO Wi-Fi devices such as Intel Compute Stick and CHIP-era boards.

## State And Persistence
No runtime state. The symbol is build configuration state.

## Dependencies And Integration Points
Integrates with cfg80211, MMC/SDIO, crypto libraries, and the driver Makefile.

## Risks
The explicit `depends on m` prevents built-in selection. Being staging code, it carries legacy Realtek architecture and broad internal APIs.

## Test Signals
Kconfig should only allow module builds with required dependencies; `CONFIG_RTL8723BS=m` should build `r8723bs.ko` and select crypto helpers.
