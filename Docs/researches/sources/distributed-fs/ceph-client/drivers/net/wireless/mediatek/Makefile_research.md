# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/Makefile

Purpose: wires top-level MediaTek wireless Kconfig symbols to subdirectory builds.

Important APIs/types/functions: adds `mt7601u/` when `CONFIG_MT7601U` is enabled and `mt76/` when `CONFIG_MT76_CORE` is enabled.

Control flow: kbuild descends into selected subdirectories based on the final kernel configuration. This file does not build objects directly; it delegates to each family Makefile.

State and persistence: no runtime state. Build state is represented by kbuild object lists and generated modules.

Dependencies and integration: depends on child directories providing their own Makefiles and on Kconfig symbols being defined by sourced Kconfig files.

Risks: mismatched Kconfig symbol names would silently omit a driver family from builds. New MediaTek subtrees need corresponding `obj-*` entries.

Test signals: build a configuration with `CONFIG_MT7601U=m/y` and `CONFIG_MT76_CORE=m/y` and verify kbuild descends into the expected directories.
