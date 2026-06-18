# sources/distributed-fs/ceph-client/fs/gfs2/Kconfig

## Purpose
Defines build-time configuration for GFS2 filesystem support and optional DLM cluster locking support.

## Important APIs, Types, And Functions
`config GFS2_FS` is a tristate enabling the GFS2 filesystem and selecting buffer heads, POSIX ACLs, CRC32, quota control, and iomap support. `config GFS2_FS_LOCKING_DLM` enables the DLM locking module when GFS2, networking, configfs, sysfs, and compatible DLM availability are present.

## Control Flow
Kconfig dependency resolution decides whether GFS2 can be built in, modularized, or disabled. The DLM option is only offered when its dependency expression is satisfied.

## State And Persistence
No runtime state. It controls compiled features and therefore persistent kernel/module capabilities.

## Dependencies And Integration Points
Feeds the kernel build system and `fs/gfs2/Makefile`. Selected symbols ensure required VFS, ACL, CRC, quota, and iomap support is present.

## Risks
Incorrect dependency constraints can allow invalid builds or hide cluster support. DLM depends on networking/configfs/sysfs because clustered locking requires those subsystems.

## Test Signals
Run Kconfig build combinations for built-in/module GFS2, DLM enabled/disabled, missing DLM/network prerequisites, and verify selected symbols propagate.
