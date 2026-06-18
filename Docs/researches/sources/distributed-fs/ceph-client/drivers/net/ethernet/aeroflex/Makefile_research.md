# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/aeroflex/Makefile

Purpose: this Makefile connects the GRETH Kconfig symbol to the GRETH driver object.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_GRETH) += greth.o`.

Control flow: kbuild links `greth.o` into vmlinux for `CONFIG_GRETH=y`, builds `greth.ko` for `CONFIG_GRETH=m`, and skips it when unset.

State and persistence: there is no runtime state. The persistent output is the build artifact selected by `.config`.

Dependencies and integration points: it integrates with the parent networking driver kbuild tree and with `aeroflex/Kconfig`. The object name directly corresponds to `greth.c` and its local header `greth.h`.

Risks: the file is intentionally minimal. The main maintenance risk is symbol/object drift if the driver or Kconfig symbol is renamed.

Test signals: enabling `CONFIG_GRETH` should compile `drivers/net/ethernet/aeroflex/greth.o`, and modular builds should produce module metadata from `greth.c`.
