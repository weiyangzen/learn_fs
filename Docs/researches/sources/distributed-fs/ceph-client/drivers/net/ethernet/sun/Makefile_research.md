# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/Makefile

Purpose: kbuild object mapping for Sun Ethernet drivers.

Important mappings: `CONFIG_HAPPYMEAL` to `sunhme.o`, `CONFIG_SUNQE` to `sunqe.o`, `CONFIG_SUNBMAC` to `sunbmac.o`, `CONFIG_SUNGEM` to `sungem.o`, `CONFIG_CASSINI` to `cassini.o`, `CONFIG_SUNVNET_COMMON` to `sunvnet_common.o`, `CONFIG_SUNVNET` to `sunvnet.o`, `CONFIG_LDMVSW` to `ldmvsw.o`, and `CONFIG_NIU` to `niu.o`.

Control flow: during kbuild, each `obj-$(CONFIG_...)` entry is built in or as a module according to `.config`. Symbol definitions live in the sibling Kconfig.

State and persistence: no runtime state; build output is determined by configuration.

Dependencies and integration: integrates the Sun Ethernet directory into the kernel build. Kconfig handles dependencies; this file only maps selected symbols to objects.

Risks and test signals: mismatched symbol or object names cause missing modules or build failures. Validate with allmodconfig and targeted builds for each Sun Ethernet symbol.
