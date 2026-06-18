# sources/distributed-fs/ceph-client/fs/configfs/Kconfig

Purpose: declares the `CONFIG_CONFIGFS_FS` build option for the userspace-driven configuration filesystem.

Important entries: `config CONFIGFS_FS` is a tristate named "Userspace-driven configuration filesystem". The help text positions configfs as the converse of sysfs: sysfs exposes kernel objects, while configfs lets userspace create and manage kernel `config_item` objects through filesystem operations.

Control flow: no runtime control flow. Kconfig selection determines whether the configfs code is built in, built as a module, or omitted.

State and persistence: no state. The option controls availability of the `configfs` filesystem and associated APIs.

Dependencies/integration: consumed by `fs/configfs/Makefile` via `obj-$(CONFIG_CONFIGFS_FS)`. Kernel subsystems that expose configfs trees depend on this option or select it in their own Kconfig entries.

Risks: as a tristate, dependent subsystems must handle built-in versus module availability and symbol export constraints. Misconfigured systems will lack `/sys/kernel/config` and configfs APIs.

Test signals: Kconfig dependency resolution, allnoconfig disabling configfs, module and built-in builds, and dependent subsystem builds against each mode.
