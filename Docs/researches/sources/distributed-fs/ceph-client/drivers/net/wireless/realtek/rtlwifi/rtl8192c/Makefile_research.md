# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/Makefile

The `rtl8192c/Makefile` defines the shared `rtl8192c-common` kernel object. `rtl8192c-common-objs` links `main.o`, `dm_common.o`, `fw_common.o`, and `phy_common.o`; `obj-$(CONFIG_RTL8192C_COMMON)` gates the object on the Kconfig symbol.

There is no runtime state or control flow. Build-time state is the object list and the selected Kconfig value. It integrates with Linux Kbuild and chip-specific rtlwifi drivers that depend on shared RTL8192C-family common code.

Risks are build omissions when common files gain dependencies or when chip-specific modules expect symbols not linked into `rtl8192c-common.o`. Test signals include kernel/module builds with `CONFIG_RTL8192C_COMMON=m/y` and successful symbol resolution for consuming drivers.
