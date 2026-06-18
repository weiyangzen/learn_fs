# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/Makefile

Kbuild and external build Makefile for the NILFS2 kernel module. It defaults `CONFIG_NILFS2_FS=m` for external builds, lists the `nilfs2.o` composite object members, and includes core files such as `inode.o`, `file.o`, `dir.o`, `btree.o`, `dat.o`, `cpfile.o`, `ifile.o`, `alloc.o`, and `gcinode.o`.

It supports debug builds through `CONFIG_NILFS_DEBUG`, adds local UAPI/include paths, detects RHEL release metadata from `$(KSRC)/Makefile.rhelver`, and injects `RHEL_RELEASE_N` when available. In kbuild context, it disables unsupported xattr and POSIX ACL options for this external module.

External targets call the running kernel build tree at `/lib/modules/$(uname -r)/build`, install `nilfs2.ko` under `/lib/modules/<kver>/kernel/fs/nilfs2/`, run `depmod`, and provide guarded unload logic that refuses to remove the module while NILFS2 mounts exist.

Risk/notes: hardcoded `/lib/modules`, `/sbin/depmod`, `/sbin/rmmod`, and `modprobe` assumptions make this Linux-distribution-specific. The file explicitly states it only supports external builds, not in-kernel tree builds.
