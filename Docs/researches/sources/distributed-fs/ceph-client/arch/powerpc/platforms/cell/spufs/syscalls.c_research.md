# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/syscalls.c

Purpose: registers the architecture-facing spufs syscall callbacks for creating contexts and running SPU contexts.

Important functions: `do_spu_run`, `do_spu_create`, and the global `spufs_calls` structure. `spufs_calls` also exposes `do_notify_spus_active` and, under `CONFIG_COREDUMP`, the coredump extra note callbacks.

Control flow: `do_spu_run()` obtains the file for the supplied fd, copies in the user NPC, verifies the file is a spufs context directory (`spufs_context_fops`), calls `spufs_run_spu()`, then writes back NPC and optional status. `do_spu_create()` uses `start_creating_user_path()` with `LOOKUP_DIRECTORY`, delegates to `spufs_create()`, and finishes with `end_creating_path()`.

State and dependencies: this file is glue between generic syscall registration and `inode.c`/`run.c`; module ownership is recorded in `spufs_calls.owner`. Risks include userspace pointer failures overriding prior return status, fd type validation, and create path race/rollback behavior delegated to VFS helpers. Test signals are syscall-level create/run with bad fds, bad user pointers, flags/mode combinations, coredump-enabled registration, and unregister on module exit.
