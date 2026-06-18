# File Research: sources/cow-pools/bcachefs-tools/fs/Makefile

- Kernel/DKMS kbuild Makefile for the bcachefs module.
- In DKMS mode, forces `CONFIG_BCACHEFS_FS=m` and translates environment flags into compile-time defines for debug, transaction restart injection, tests, and quota.
- Generates or degrades `bch2_getdents_layout.h` to validate an external-kernel getdents fastpath layout.
- Lists all object files composing `bcachefs.o`, covering allocation, btree, data, erasure coding, filesystem namespace, init/recovery, journal, options, superblocks, snapshots, utilities, vendor helpers, and VFS paths.
- Adds debugfs-only async object code, excludes KUnit tests in DKMS, adds `module-version.o` in DKMS, suppresses psABI notes, and ensures `-I$(src)`.
