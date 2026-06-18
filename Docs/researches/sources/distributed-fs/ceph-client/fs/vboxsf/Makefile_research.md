<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/Makefile -->
# sources/distributed-fs/ceph-client/fs/vboxsf/Makefile

Purpose: Provides Kbuild rules for compiling the vboxsf filesystem.

Important APIs, types, and functions: Uses `obj-$(CONFIG_VBOXSF_FS) += vboxsf.o` and composes `vboxsf-y` from `dir.o`, `file.o`, `utils.o`, `vboxsf_wrappers.o`, and `super.o`.

Control flow: When `CONFIG_VBOXSF_FS` is enabled, Kbuild links the listed objects into the single vboxsf module or built-in object. Directory operations, regular file operations, shared utilities, host-call wrappers, and superblock/module registration are all required pieces.

State and persistence: No runtime state. The object list determines which exported internal symbols are available at link time.

Dependencies and integration points: Integrates with Kbuild and the Kconfig option in this directory. The object grouping matches declarations in `vfsmod.h`.

Risks and test signals: Risks are missing an object after symbol changes or accidentally linking unused host ABI code. Test module and built-in builds and verify `modinfo vboxsf` exposes the filesystem alias from `super.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/Makefile -->
