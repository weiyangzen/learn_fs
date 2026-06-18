# sources/distributed-fs/ceph-client/fs/ubifs/Makefile

## Purpose
This Makefile composes the UBIFS filesystem object from its implementation modules.

## Important APIs, Types, and Functions
`obj-$(CONFIG_UBIFS_FS) += ubifs.o` builds UBIFS as built-in or module. `ubifs-y` includes shrinker, journal, file, dir, superblock, IO, TNC, master, scan, replay, log, commit, GC, orphan, budget, find, commit helpers, compression, LPT/LPROPS, recovery, ioctl, debug, misc, and sysfs support. Conditional objects add encryption, xattr, and authentication support.

## Control Flow and State
There is no runtime logic. Object composition reflects UBIFS subsystems and controls whether `crypto.o`, `xattr.o`, and `auth.o` are linked.

## Persistence, Dependencies, and Integration
The Makefile integrates UBIFS with Kconfig-selected VFS, UBI, crypto, xattr, and authentication functionality.

## Risks and Test Signals
Risks are missing objects under conditional configs or unresolved symbols when feature options are toggled. Build tests across `CONFIG_UBIFS_FS=m/y`, xattr, encryption, and authentication combinations provide coverage.
