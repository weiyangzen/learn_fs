# sources/distributed-fs/ceph-client/drivers/sbus/Makefile

Purpose: gates the SPARC SBUS miscellaneous character-driver subtree.

Important APIs/types/functions: `obj-$(CONFIG_SBUSCHAR) += char/` makes kbuild descend into `drivers/sbus/char` only when `CONFIG_SBUSCHAR` is enabled.

Control flow: build-time only; it has no runtime paths.

State and persistence: no runtime state.

Dependencies and integration: connects the top-level SBUS driver directory to the `char` subdirectory's Kconfig-selected objects.

Risks and test signals: the main signal is build matrix coverage that enabling `CONFIG_SBUSCHAR` reaches the child Makefile and disabling it excludes legacy SBUS char drivers.
