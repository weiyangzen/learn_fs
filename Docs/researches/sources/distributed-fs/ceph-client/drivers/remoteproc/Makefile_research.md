<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/Makefile

Purpose: Maps remoteproc Kconfig symbols to built objects and composes the common `remoteproc.o` aggregate.

Important APIs and types: `obj-$(CONFIG_REMOTEPROC)` builds `remoteproc.o`, whose `remoteproc-y` members include core, coredump, debugfs, sysfs, virtio, and ELF loader components. Individual `obj-$(CONFIG_...)` lines map platform drivers to their object files. Some modules are multi-object, such as `qcom_wcnss_pil-y` and TI K3 drivers sharing `ti_k3_common.o`.

Control flow: Kbuild evaluates the selected Kconfig symbols and includes matching objects in vmlinux or modules. Common remoteproc objects are built only when `CONFIG_REMOTEPROC` is enabled; platform objects follow their own tristate selections.

State and persistence: Build artifacts and module composition persist in the kernel build output. The Makefile itself carries no runtime state.

Dependencies and integration points: Integrates with `drivers/remoteproc/Kconfig`, remoteproc core object layout, platform driver source files, and Kbuild module naming.

Risks: Missing object entries would make enabled Kconfig options produce no driver. Multi-object modules require exact naming or link failures. Common helpers must be selected in Kconfig before object references become valid.

Test signals: Build each config as builtin and module, verify `remoteproc.o` includes all core members, ensure `CONFIG_DA8XX_REMOTEPROC` builds `da8xx_remoteproc.o`, and run clean builds after adding or renaming platform drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/Makefile -->
