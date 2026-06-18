# sources/distributed-fs/ceph-client/kernel/gcov/gcc_base.c

## Purpose
`gcc_base.c` provides the exported symbols that GCC-generated profiling code expects in the kernel. It registers each object file's `gcov_info` and stubs out libgcov merge/flush/exit helpers that are referenced by instrumented code but not used by the kernel runtime.

## Important APIs, types, and functions
The central entry point is `__gcov_init(struct gcov_info *info)`. Exported no-op helpers are `__gcov_flush()`, `__gcov_merge_add()`, `__gcov_merge_single()`, `__gcov_merge_delta()`, `__gcov_merge_ior()`, `__gcov_merge_time_profile()`, `__gcov_merge_icall_topn()`, and `__gcov_exit()`. The file uses shared `gcov_lock`, `gcov_info_link()`, `gcov_info_version()`, `gcov_events_enabled`, and `gcov_event()`.

## Control flow
When GCC constructor code calls `__gcov_init()`, the function takes `gcov_lock`, records and logs the first observed GCC version magic, links the object into the compiler-specific gcov list, and notifies the debugfs event consumer if events are enabled. The merge and flush symbols return immediately because kernel gcov does not rely on libgcov process-exit merge logic.

## State and persistence
The only local state is a static `gcov_version` used for one-time logging. Persistent runtime state is owned by the compiler-specific backend list and debugfs node tree. There is no on-disk persistence and no ownership transfer of the compiler-generated `gcov_info` object.

## Dependencies and integration points
This file is the GCC-specific registration bridge between instrumented object constructors and the generic kernel gcov stack. It depends on `gcov.h`, exported kernel symbols for modules, and the debugfs event path in `fs.c`. Instrumented modules link against these symbols when built with coverage enabled.

## Risks and test signals
Risks include missing newly introduced GCC merge symbols, event ordering before debugfs initialization, version-magic mismatches hidden by one-time logging only, and module unload requiring other code to unlink/remove data correctly. Test signals include module load registering coverage, first-version printk, debugfs event replay after late gcov fs init, and successful linking of coverage-instrumented objects across GCC versions.
