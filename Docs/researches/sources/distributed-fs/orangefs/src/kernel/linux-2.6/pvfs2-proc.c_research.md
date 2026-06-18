# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-proc.c

## Purpose
`pvfs2-proc.c` implements the `/proc/sys/pvfs2` sysctl control plane. It exposes kernel debug strings, client debug strings, operation and slot timeouts, client cache tunables, performance counter settings, performance counter reads, and kernel-maintained cache statistics.

## Important APIs, tables, and handlers
`pvfs2_proc_initialize` registers the sysctl table and `pvfs2_proc_finalize` unregisters it. `pvfs2_proc_debug_mask_handler` handles `kernel-debug`, `client-debug`, and read-only `debug-help`. `pvfs2_param_proc_handler` handles integer get/set operations by sending `PVFS2_VFS_OP_PARAM` upcalls to the client. `pvfs2_pc_proc_handler` reads client performance counter strings through `PVFS2_VFS_OP_PERF_COUNT`. Static `pvfs2_param_extra` records bind sysctl files to client parameter operations and min/max ranges. `g_pvfs2_stats` backs read-only kernel stats.

## Control flow
Generic proc helpers first parse or format user data. Kernel debug writes are converted locally into `gossip_debug_mask` and canonicalized back into `kernel_debug_string`. Client debug and client parameter reads/writes allocate an operation, fill a parameter request, call `service_operation` interruptibly, consume the downcall, and release the operation. Performance-counter reads honor file offsets by copying a slice of the returned text buffer to userspace.

## State and persistence behavior
`client_debug_string`, `kernel_debug_string`, `debug_help_string`, timeout globals, and `g_pvfs2_stats` live in module memory. Client-side tunables are not stored locally; this file sends requests to the daemon and reports daemon responses. Sysctl registration state is tracked by `fs_table_header`.

## Dependencies and integration points
The file depends on Linux sysctl/proc APIs, debug mask maps and conversion functions from `pvfs2-utils.c`, operation allocation from `pvfs2-cache.c`, and `service_operation` from waitqueue code. It is initialized by `pvfs2-mod.c` after caches, qhash, and device state are ready.

## Risks and edge cases
The client-debug write path calls `op_release(new_op)` and then prints `new_op->downcall.resp.param.u.value64`, which is a use-after-free pattern. Many handlers require a live client daemon; without one, sysctl reads/writes may block until timeout or return service errors. The table contains repeated `CTL_NAME(15)` values under optional readahead entries, which may matter on older numbered sysctl kernels. `pvfs2_pc_proc_handler` trusts the daemon-provided string to be NUL-terminated within the response buffer before `strlen`.

## Test signals
Tests should exercise read/write of kernel-debug, client-debug, op/slot timeout minmax enforcement, each cache tunable, perf-counter partial reads with offsets, daemon-down behavior, module unload after sysctl registration, and the use-after-free site with slab debugging or KASAN-style instrumentation.
