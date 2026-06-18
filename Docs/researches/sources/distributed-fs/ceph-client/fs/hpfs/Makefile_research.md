# sources/distributed-fs/ceph-client/fs/hpfs/Makefile

Purpose: this Makefile defines the HPFS object composition for Kbuild.

Important build variables: `obj-$(CONFIG_HPFS_FS) += hpfs.o` builds the filesystem object when configured. `hpfs-objs` aggregates implementation files: allocation, anode allocation tree, buffer mapping, dentry operations, directory VFS operations, dnode tree handling, extended attributes, file I/O, inode operations, metadata mapping, name handling, namei mutations, and superblock support.

Control flow: when `CONFIG_HPFS_FS` is enabled, Kbuild compiles each listed object and links them into `hpfs.o`, which is then built-in or modular based on the tristate value.

State and persistence: no runtime state exists in the Makefile, but object inclusion controls which persistent metadata paths are present in the driver. Omitting any listed object would leave unresolved cross-file calls declared in `hpfs_fn.h`.

Dependencies and integration: it pairs with `Kconfig` and the central HPFS private header. The object order is conventional and does not encode runtime ordering, but it documents subsystem boundaries.

Risks: adding a new exported helper to `hpfs_fn.h` requires updating this list if implemented in a new source file. Accidentally removing `super.o` would break mount registration even though it is not part of this work item.

Test signals: build HPFS as built-in and module; verify all objects link; run `nm` or modpost checks after file additions/removals; and ensure no object relies on being linked only in one configuration.
