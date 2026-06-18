# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/Kconfig

## Purpose
This Kconfig file defines configuration entries for ARC EMAC-family Ethernet support, including a vendor menu gate, a shared core driver symbol, and Rockchip SoC glue support.

## Important APIs, types, and functions
`NET_VENDOR_ARC` is a bool vendor selector defaulting to yes. `ARC_EMAC_CORE` is a tristate internal/shared core depending on `ARC`, `ARCH_ROCKCHIP`, or `COMPILE_TEST`, and it selects `MII`, `PHYLIB`, and `CRC32`. `EMAC_ROCKCHIP` is the user-visible tristate for RK3036/RK3066/RK3188 EMAC support; it selects `ARC_EMAC_CORE` and depends on OF IRQ and regulator support plus Rockchip or compile-test builds.

## Control flow
Kconfig controls build visibility and dependency resolution. If `NET_VENDOR_ARC` is disabled, ARC Ethernet questions are skipped. Enabling Rockchip EMAC pulls in the core ARC EMAC object and required PHY/MII/CRC dependencies.

## State and persistence
The persistent output is the kernel `.config`, which determines whether the core and platform glue are built in, modular, or omitted.

## Dependencies and integration points
The symbols integrate with the drivers/net/ethernet Kconfig hierarchy and the local Makefile. `ARC_EMAC_CORE` builds `arc_emac.o`, while `EMAC_ROCKCHIP` builds `emac_rockchip.o`.

## Risks
Because `ARC_EMAC_CORE` is not user-described, platform glue must select it correctly. Missing dependency selections would surface as build failures in PHY, MII, CRC, OF, IRQ, or regulator paths. The vendor gate default y follows kernel vendor-menu convention but can hide prompts when disabled.

## Test signals
Run configuration coverage for built-in, module, and disabled cases; compile-test on non-ARC/non-Rockchip; and verify Rockchip selection pulls the core object and dependencies.
