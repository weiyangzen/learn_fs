# sources/distributed-fs/ceph-client/fs/autofs/Kconfig

Purpose: Defines the build-time configuration option for Linux kernel automounter filesystem support.

Important APIs and types: `config AUTOFS_FS` is a tristate option labeled "Kernel automounter support (supports v3, v4 and v5)". It selects whether autofs is built in, built as the `autofs` module, or omitted.

Control flow: Kconfig exposes the option to kernel configuration tools. The help text explains that autofs combines kernel fast-path handling for already-mounted paths with a userspace automount daemon for demand mounting.

State and persistence: The selected tristate value persists in the kernel `.config` and controls compilation of objects in the autofs Makefile. There is no runtime state in this file.

Dependencies and integration points: Integrates with kbuild and the autofs source directory. The help text points users toward kernel.org autofs userspace tools and notes NFS support is commonly useful.

Risks: Misconfiguration omits automount support or builds it as a module when early boot expects built-in behavior. The text is user-facing and should remain accurate for supported protocol versions and module name.

Test signals: Kconfig menu visibility, `CONFIG_AUTOFS_FS=y/m/n` builds, module name generation, and successful build of the objects listed in the Makefile for enabled states.
