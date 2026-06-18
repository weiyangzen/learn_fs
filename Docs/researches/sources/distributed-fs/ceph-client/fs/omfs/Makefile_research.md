# sources/distributed-fs/ceph-client/fs/omfs/Makefile

Purpose: describes the OMFS object composition for Kbuild.

Important APIs and targets: `obj-$(CONFIG_OMFS_FS) += omfs.o` builds the filesystem object when configured, and `omfs-y := bitmap.o dir.o file.o inode.o` links allocation, directory, file-mapping, and super/inode logic into one module or built-in object.

Control flow: no runtime control flow. The file controls link composition and therefore which translation units provide the symbols declared in `omfs.h`.

State and persistence behavior: no persistent state. Build output shape affects module packaging under the name `omfs`.

Dependencies and integration points: integrates with Kbuild and the `OMFS_FS` Kconfig symbol. The object order is straightforward and does not encode initialization ordering; module init/exit live in `inode.c`.

Risks: omitting any listed object would break cross-file references such as `omfs_aops`, `omfs_make_empty`, `omfs_count_free`, or `omfs_iget`.

Test signals: incremental and clean builds for built-in and module configurations, plus `modinfo omfs` when built as a module.
