# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/agere/Kconfig

Purpose: this Kconfig fragment introduces the Agere Ethernet vendor menu and the ET-1310 Gigabit Ethernet driver option.

Important APIs, types, and functions: the relevant symbols are `NET_VENDOR_AGERE` and `ET131X`. `NET_VENDOR_AGERE` is a boolean vendor gate, defaults to `y`, and depends on `PCI`. `ET131X` is a tristate prompt for "Agere ET-1310 Gigabit Ethernet support", depends on `PCI`, and selects `PHYLIB` and `CRC32`.

Control flow: enabling the vendor gate makes the ET131X prompt visible. Selecting `ET131X` controls whether the companion Makefile builds `et131x.o` built-in or as a module.

State and persistence: there is no runtime state. The persistent artifact is the kernel build configuration selecting or omitting the Agere driver.

Dependencies and integration points: `PCI` reflects the ET-1310 adapter bus, `PHYLIB` supports PHY management in the driver, and `CRC32` supports Ethernet CRC/hash-style filtering logic. The help text names the module `et131x`.

Risks: the vendor gate hides all Agere options when PCI is disabled, which is appropriate for the present driver but should be revisited if non-PCI Agere devices are added. Configuration drift between the `ET131X` symbol, Makefile object name, and help text would break builds or user expectations.

Test signals: `CONFIG_NET_VENDOR_AGERE=y` should expose the ET131X prompt on PCI-capable builds, `CONFIG_ET131X=m` should produce `et131x.ko`, selected dependencies should be set, and the option should disappear when PCI support is unavailable.
