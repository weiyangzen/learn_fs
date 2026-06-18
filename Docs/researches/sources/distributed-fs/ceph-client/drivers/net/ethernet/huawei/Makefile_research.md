# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/Makefile

Connects Huawei Ethernet subdirectories to Kbuild. `obj-$(CONFIG_HINIC) += hinic/` and `obj-$(CONFIG_HINIC3) += hinic3/` descend into child directories only when their config symbols are enabled.

No runtime state is created. Dependencies are the matching Kconfig symbols and child Makefiles. Risks are incorrect directory names or missing child object lists. Test by building with `CONFIG_HINIC` and `CONFIG_HINIC3` enabled/disabled as built-in or modules.
