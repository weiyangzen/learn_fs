# sources/distributed-fs/ceph-client/fs/exportfs/Makefile

Purpose: Builds the generic Linux exportfs support object when `CONFIG_EXPORTFS` is enabled.

Important APIs/types/functions: `obj-$(CONFIG_EXPORTFS) += exportfs.o` selects the composite object, and `exportfs-objs := expfs.o` maps that object to `expfs.c`.

Control flow: Kbuild includes `exportfs.o` only for enabled exportfs configurations. There is no runtime control flow in the file; it only controls object inclusion.

State and persistence behavior: No persistent state. The Makefile determines whether the exported helper symbols in `expfs.c` are present in the kernel/module build.

Dependencies and integration points: Integrated with Kconfig symbol `CONFIG_EXPORTFS` and the kernel's composite object convention. NFS export-capable filesystems and fanotify file-handle code depend on the resulting symbols.

Risks: Accidentally changing object names breaks symbol availability for all filesystems relying on exportfs helpers. The SPDX is GPL-2.0-only, matching `expfs.c`.

Test signals: Kernel build with `CONFIG_EXPORTFS=y/m`; confirm `expfs.o` is linked into `exportfs.o` and exported symbols such as `exportfs_encode_fh` and `exportfs_decode_fh` resolve.
