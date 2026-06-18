# sources/distributed-fs/ceph-client/fs/autofs/Makefile

Purpose: Connects the autofs implementation files to kbuild.

Important APIs and variables: `obj-$(CONFIG_AUTOFS_FS) += autofs4.o` builds the composite autofs object when the Kconfig option is enabled. `autofs4-objs` lists `init.o`, `inode.o`, `root.o`, `symlink.o`, `waitq.o`, `expire.o`, and `dev-ioctl.o`.

Control flow: During kbuild, the tristate expansion emits either built-in or module build rules. The composite object is still named `autofs4.o` internally while the registered filesystem/module identity is `autofs`.

State and persistence: No runtime state. The object list determines which source files form the autofs module or built-in component.

Dependencies and integration points: Integrates with `CONFIG_AUTOFS_FS`, module aliasing in `init.c`, and all autofs implementation files. Any new autofs translation unit must be added here to participate in builds.

Risks: Object list drift can silently omit required features, especially ioctl or expiration code. Renaming the composite object may affect module packaging expectations.

Test signals: Built-in and module builds, `modinfo`/module alias behavior, and link errors when adding or removing autofs functions.
