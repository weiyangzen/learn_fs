# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/Makefile

## Purpose
Kbuild recipe for the monolithic RTL8723BS SDIO Wi-Fi module.

## Important APIs, Types, And Functions
Defines `r8723bs-y` as a long object list across `core`, `hal`, and `os_dep`, maps `obj-$(CONFIG_RTL8723BS) := r8723bs.o`, and adds include paths for `include` and `hal`.

## Control Flow
Kbuild compiles all listed Realtek core/PHY/SDIO/OS abstraction objects into one module when `RTL8723BS` is selected.

## State And Persistence
No runtime state. Object composition and include search paths are build metadata.

## Dependencies And Integration Points
Coordinates AP/BT coexistence objects researched here with command, MLME, security, receive/transmit, HAL, SDIO, cfg80211, and regulatory code.

## Risks
The module is tightly coupled; missing one object often breaks many internal symbols. Legacy indentation and broad include paths can hide include-order assumptions.

## Test Signals
Full module build, link all internal Realtek symbols, and verify `ccflags-y` resolves `<drv_types.h>` and HAL headers.
