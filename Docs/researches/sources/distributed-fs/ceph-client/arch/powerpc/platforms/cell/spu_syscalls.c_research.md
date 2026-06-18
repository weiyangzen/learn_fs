# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_syscalls.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_syscalls.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_syscalls.c

### Purpose
Kernel syscall entry points and registration glue for spufs-backed SPU operations. It exposes `spu_create` and `spu_run`, delegates to registered spufs callbacks, and supports SPU coredump notes and active notifications.

### Important APIs, Types, And Functions
Important objects/functions are RCU-protected `spufs_calls`, `spufs_calls_get()`, `spufs_calls_put()`, `SYSCALL_DEFINE4(spu_create)`, `SYSCALL_DEFINE3(spu_run)`, coredump helpers, `notify_spus_active()`, `register_spu_syscalls()`, and `unregister_spu_syscalls()`. Module builds use `try_module_get()` and `module_put()` around the callback owner.

### Control Flow
spufs registers a `struct spufs_calls`. Syscalls acquire the calls pointer through the cleanup-class helper, validate file descriptors or affinity neighbor descriptors, then call `create_thread()` or `spu_run()`. Coredump and notification helpers call optional registered callbacks. Unregister clears the RCU pointer and waits for readers.

### State, Persistence, And Dependencies
State is the global RCU callback pointer and module references. No durable persistence. Dependencies include spufs, file descriptor helpers, RCU, module ownership, coredump APIs, and syscall definitions.

### Integration Points
This is the ABI bridge between userspace SPU syscalls and the spufs implementation, whether built-in or module.

### Risks
RCU/module lifetime and fd handling are critical. Incorrect unregister or owner checks could call unloaded code; syscall behavior is user ABI.

### Test Signals
Test `spu_create`/`spu_run` before registration, after registration, and during module unload; test affinity neighbor fd validation, coredump note paths, and concurrent syscall/unregister races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spu_syscalls.c -->
