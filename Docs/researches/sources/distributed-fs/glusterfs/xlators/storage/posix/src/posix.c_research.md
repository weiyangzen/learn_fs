# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix.c

## Purpose

This file registers the POSIX storage translator with GlusterFS. It binds the translator's fop table, callback table, dumpops, options, lifecycle hooks, memory accounting hook, identifier, and maintenance category.

## Important APIs, Types, and Functions

`dumpops` exposes `posix_priv` and `posix_inode`. `fops` maps Gluster operations to POSIX implementations including lookup, namespace operations, inode/fd operations, xattrs, locking stubs, checksum, allocation, discard, zerofill, ipc, seek, lease, put, and copy_file_range. `cbks` maps release, releasedir, and forget callbacks. `xlator_api` registers `posix_init`, `posix_fini`, `posix_notify`, `posix_reconfigure`, `mem_acct_init`, `posix_options`, identifier `"posix"`, and category `GF_MAINTAINED`.

## Control Flow

At translator load time, Gluster reads `xlator_api`, calls init/mem accounting, and installs the fop/callback tables. Runtime fops are dispatched through the table. Optional runtime code, such as io_uring enablement, can later patch entries like readv/writev/fsync.

## State and Persistence Behavior

This file itself has no persistence. It controls which implementation functions are reachable by the Gluster stack and therefore determines the persistent effects of all POSIX operations.

## Dependencies and Integration Points

It depends on `posix.h` for function declarations and private option declarations. It integrates with every POSIX source file that defines one of the registered functions and with the Gluster translator loader.

## Risks

Missing or incorrect fop mappings can silently disable functionality or route a request to the wrong implementation. New fops added elsewhere must be wired here. Since io_uring can mutate fop pointers after registration, restore paths must match this table. Lock and lease entries intentionally return ENOSYS unless higher translators are loaded, so volume graphs must include the proper feature translators.

## Test Signals

Build/link tests catch missing symbols. Runtime translator smoke tests should verify each registered fop reaches the intended implementation, init/fini/reconfigure hooks run, dumpops work, and io_uring on/off restores readv/writev/fsync mappings.
