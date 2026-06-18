# sources/distributed-fs/ceph-client/arch/um/os-Linux/main.c

## Purpose
Provides the host process `main()` for UML, including ASLR disabling/reexec, stack limit setup, environment PATH adjustment, fatal signal handling, boot entry, shutdown, reboot exec, and malloc/free interposition.

## Important APIs, Types, and Functions
`main()` prepares host process state, calls `scan_elf_aux()` and `linux_main()`, then disables timers/SIGIO before optional reboot exec. `set_stklim()`, `setup_env_path()`, and `install_fatal_handler()` are boot helpers. `__wrap_malloc()`, `__wrap_calloc()`, and `__wrap_free()` route libc allocations to kmalloc/vmalloc after `kmalloc_ok`.

## Control Flow, State, and Persistence
Persistent process effects include disabled ASLR personality, session creation, adjusted PATH, fatal handlers, duplicated argv for reboot, and malloc routing based on UML memory ranges. Shutdown unblocks pending signals after deactivating timers/fds.

## Dependencies and Integration Points
Entry point to `linux_main()` in `um_arch.c`. Depends on host personality, signals, `uml_cleanup()`, timer/fd deactivation, physical/vmalloc layout globals, and memory allocators.

## Risks and Test Signals
Risks are failed reexec, PATH memory lifetime, malloc wrapper misclassification, pending signal delivery during shutdown, and reboot argv handling. Test boot with ASLR enabled, reboot, SIGINT/SIGTERM, profiling builds, and allocations before/after `kmalloc_ok`.
