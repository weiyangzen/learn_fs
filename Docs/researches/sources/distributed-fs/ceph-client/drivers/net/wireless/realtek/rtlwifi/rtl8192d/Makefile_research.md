
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/Makefile

Purpose: Builds the shared RTL8192D common support object used by 8192D-family rtlwifi drivers.

Important APIs/types/functions: Defines `rtl8192d-common-objs` as `dm_common.o`, `fw_common.o`, `hw_common.o`, `main.o`, `phy_common.o`, `rf_common.o`, and `trx_common.o`. `obj-$(CONFIG_RTL8192D_COMMON) += rtl8192d-common.o` binds the composite object to the common Kconfig symbol.

Control flow: No runtime flow. Kbuild links common DM, firmware, hardware, PHY, RF, and TRX support into a reusable common module/object.

State and persistence: Build metadata only. Runtime state lives in the listed source objects.

Dependencies/integration: Downstream 8192D transport-specific drivers depend on these common symbols. The object list is the authoritative compile boundary for shared 8192D support.

Risks: Adding 8192D common functionality without updating this list causes unresolved symbols. Removing or renaming objects can break transport drivers that expect common exports. The common object is gated separately from transport-specific symbols.

Test signals: Kbuild with `CONFIG_RTL8192D_COMMON`, modpost symbol checks, and transport driver builds that depend on this common object.
