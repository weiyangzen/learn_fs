# sources/distributed-fs/ceph-client/drivers/iio/resolver/Makefile

Purpose: build glue mapping resolver Kconfig symbols to object files.

Important APIs/types/functions: `obj-$(CONFIG_AD2S90) += ad2s90.o`, `obj-$(CONFIG_AD2S1200) += ad2s1200.o`, and `obj-$(CONFIG_AD2S1210) += ad2s1210.o`.

Control flow: Kbuild includes exactly the objects whose symbols are enabled as built-in or module.

State and persistence: no runtime state; output is determined by `.config`.

Dependencies/integration: must stay in sync with Kconfig symbol names and source filenames in this directory.

Risks and test signals: stale object names or missing entries silently omit drivers from builds. Test each symbol as `m` and `y`, and verify module filenames match Kconfig help.
