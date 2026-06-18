<!-- Source: sources/distributed-fs/ceph-client/fs/nfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/nfs/Makefile

## Purpose
Builds the Linux NFS client objects and conditionally includes version-specific, feature-specific, and pNFS layout subdirectories.

## Important APIs, Types, And Functions
Defines `obj-$(CONFIG_NFS_FS) += nfs.o`, `nfs-y` core objects, optional `nfsroot.o`, `sysctl.o`, `fscache.o`, and `localio.o`, version modules `nfsv2.o`, `nfsv3.o`, `nfsv4.o`, and pNFS subdirs `filelayout/`, `blocklayout/`, and `flexfilelayout/`. Adds include-path flags for trace sources.

## Control Flow
Kbuild composes objects according to Kconfig symbols. `nfsv4-y` includes core NFSv4 files and conditionally adds legacy DNS, sysctl, v4.0, and v4.2 files. pNFS layout directories are descended into only when their configs are enabled.

## State And Persistence
No runtime state. Build output composition is determined by `.config`.

## Dependencies And Integration Points
Consumes symbols from `fs/nfs/Kconfig`. Integrates the blocklayout Makefile researched in this group and includes NFS FS-Cache support when `CONFIG_NFS_FSCACHE` is enabled.

## Risks
Object list drift can omit source needed by a config or include incompatible code. Trace CFLAGS must keep generated trace headers resolvable. Optional localio/fscache objects require matching Kconfig definitions elsewhere.

## Test Signals
Compile NFS as built-in and module across v2/v3/v4, FSCACHE, ROOT_NFS, SYSCTL, v4.0/v4.2, and all pNFS layout combinations.
