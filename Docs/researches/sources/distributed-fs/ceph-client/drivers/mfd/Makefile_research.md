# sources/distributed-fs/ceph-client/drivers/mfd/Makefile

Purpose: Kbuild object map for `drivers/mfd`. It translates Kconfig symbols into built-in or module objects, including composite object definitions for multi-file MFD drivers.

Important APIs, types, and functions: this file uses Kbuild variables such as `obj-$(CONFIG_...)`, `<module>-objs`, and conditional `ifeq` blocks. Relevant subset mappings include `88pm860x-objs := 88pm860x-core.o 88pm860x-i2c.o`, `obj-$(CONFIG_MFD_88PM860X) += 88pm860x.o`, `obj-$(CONFIG_MFD_88PM800) += 88pm800.o 88pm80x.o`, `obj-$(CONFIG_MFD_88PM805) += 88pm805.o 88pm80x.o`, `obj-$(CONFIG_MFD_88PM886_PMIC) += 88pm886.o`, `obj-$(CONFIG_ABX500_CORE) += abx500-core.o`, `obj-$(CONFIG_AB8500_CORE) += ab8500-core.o ab8500-sysctrl.o`, `obj-$(CONFIG_MFD_AAT2870_CORE) += aat2870-core.o`, and `obj-$(CONFIG_MFD_AC100) += ac100.o`.

Control flow: Kbuild evaluates configuration symbols and adds corresponding objects to the directory build. Composite object lists build several `.o` files into one module/built-in unit. Conditional table additions, such as Arizona/Madera codec tables, include variant-specific data only when their symbols are built in.

State and persistence: no runtime state. The persistent effect is the generated build graph and module composition.

Dependencies and integration: tightly coupled to `Kconfig` symbols and source filenames. It also encodes ordering notes, for example AB8500 must come after DB8500 PRCMU because the channel provider is needed first.

Risks: duplicate inclusion of shared helper objects such as `88pm80x.o` when both PM800 and PM805 are enabled can affect module composition and symbol ownership; Kconfig/Makefile mismatch causes silent missing drivers or build failures; ordering constraints are comments rather than enforceable dependency checks except by object order.

Test signals: build the MFD directory under configurations enabling each relevant symbol singly and together, inspect generated modules for composite contents, verify `modpost` symbol ownership, and test built-in link order for AB8500/DB8500 PRCMU.
