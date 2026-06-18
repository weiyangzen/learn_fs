
# sources/distributed-fs/ceph-client/drivers/hwtracing/ptt/Makefile

Purpose: build rule for the HiSilicon PTT hwtracing driver.

Important APIs/types/functions: `obj-$(CONFIG_HISI_PTT) += hisi_ptt.o`.

Control flow: kbuild compiles and links `hisi_ptt.c` when the Kconfig symbol is enabled.

State and persistence: no runtime state.

Dependencies and integration: relies on `Kconfig` symbol and normal kbuild object naming.

Risks: minimal; object name must match source file.

Test signals: kernel build with `CONFIG_HISI_PTT=m/y` produces `hisi_ptt.o` or module.
