# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/config

## Purpose

`liveupdate/config` lists kernel features required by the liveupdate selftests and their kexec handover path.

## Important APIs, Types, and Functions

It declares `CONFIG_BLK_DEV_INITRD`, `CONFIG_KEXEC_FILE`, `CONFIG_KEXEC_HANDOVER`, `CONFIG_KEXEC_HANDOVER_ENABLE_DEFAULT`, `CONFIG_KEXEC_HANDOVER_DEBUGFS`, `CONFIG_KEXEC_HANDOVER_DEBUG`, `CONFIG_LIVEUPDATE`, `CONFIG_LIVEUPDATE_TEST`, `CONFIG_MEMFD_CREATE`, `CONFIG_TMPFS`, and `CONFIG_SHMEM`.

## Control Flow and State

There is no executable flow. The file is consumed by selftest config checking to flag missing prerequisites.

## Dependencies and Integration Points

It integrates with the liveupdate test binaries and `do_kexec.sh`, which need kexec, initramfs, memfd, tmpfs/shmem, and liveupdate debug/test support.

## Risks and Test Signals

Risks are stale symbols causing false capability assumptions. Signals are config-check output and runtime tests finding the required debugfs/kexec/liveupdate facilities.
