# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/Makefile

Purpose: Defines the NetXen NIC module composition for `CONFIG_NETXEN_NIC`.

Important build rules: `obj-$(CONFIG_NETXEN_NIC) := netxen_nic.o` creates the module/built-in object. `netxen_nic-y` links `netxen_nic_hw.o`, `netxen_nic_main.o`, `netxen_nic_init.o`, `netxen_nic_ethtool.o`, and `netxen_nic_ctx.o`.

Control flow: Kbuild compiles and links all listed component objects into one `netxen_nic` driver when the symbol is enabled.

State and persistence behavior: No runtime state. The file defines static composition of the driver.

Dependencies and integration points: Integrates the files researched here with the rest of the NetXen implementation (`hw`, `main`, `init`).

Risks: Missing a component breaks unresolved symbols or removes required feature surfaces such as ethtool or context setup.

Test signals: Module build for `CONFIG_NETXEN_NIC=m`, built-in build for `=y`, and modpost symbol checks.
