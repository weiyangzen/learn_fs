# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kdebugfs.c

## Purpose
Creates and exports the architecture debugfs root directory for PowerPC.

## Important APIs, Types, And Functions
Exports `arch_debugfs_dir` and defines init function `arch_kdebugfs_init`, registered with `arch_initcall`.

## Control Flow
During architecture initcall processing, `debugfs_create_dir("powerpc", NULL)` creates the top-level `/sys/kernel/debug/powerpc` directory and stores the returned dentry for other PowerPC code.

## State And Persistence
State is the global debugfs dentry pointer. The debugfs directory exists until debugfs teardown or reboot and has no durable persistence.

## Dependencies And Integration Points
Depends on debugfs and initcall ordering. Other architecture code can create files under `arch_debugfs_dir`.

## Risks And Edge Cases
If debugfs is disabled or creation fails, consumers must tolerate a NULL/error dentry. There is no explicit cleanup path because debugfs and kernel lifetime manage it.

## Test Signals
Signals include boot with debugfs enabled, presence of `/sys/kernel/debug/powerpc`, and downstream architecture debugfs files appearing under the directory.
