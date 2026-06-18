# sources/distributed-fs/ceph-client/mm/kmemleak.c

## Purpose
`kmemleak.c` implements the kernel memory leak detector runtime. It records allocator events as `struct kmemleak_object` metadata, scans kernel roots and tracked objects for pointer reachability, and reports old allocated objects that remain below their required reference count through `/sys/kernel/debug/kmemleak` and kernel logs.

## Important APIs, Types, And Functions
The central type is `struct kmemleak_object`, which stores object address, size, allocation stack handle, state flags, reference-count color state, checksum, scan areas, task attribution, RB-tree node, RCU list node, and object-local lock. `struct kmemleak_scan_area` restricts scanning to selected subranges. Public allocator-facing entry points include `kmemleak_alloc()`, `kmemleak_alloc_percpu()`, `kmemleak_vmalloc()`, `kmemleak_free()`, `kmemleak_free_part()`, `kmemleak_free_percpu()`, `kmemleak_alloc_phys()`, `kmemleak_free_part_phys()`, and `kmemleak_ignore_phys()`. False-positive and scan-control APIs include `kmemleak_not_leak()`, `kmemleak_transient_leak()`, `kmemleak_ignore()`, `kmemleak_ignore_percpu()`, `kmemleak_scan_area()`, `kmemleak_no_scan()`, and `kmemleak_update_trace()`.

Internal object management is split between `__alloc_object()`, `__link_object()`, `__create_object()`, `find_and_remove_object()`, `delete_object_full()`, `delete_object_part()`, `__delete_object()`, `get_object()`, and `put_object()`. Lookup uses three RB roots selected by `object_tree()`: normal virtual addresses, physical-address objects, and percpu objects. Reporting uses `print_unreferenced()`, `hex_dump_object()`, and seq-file callbacks exposed by `kmemleak_fops`.

## Control Flow
Allocation hooks call `create_object*()`, which allocate metadata from a slab cache or early emergency pool, capture task and stack-depot information, and insert the object into the proper RB tree and global `object_list`. Free hooks remove the object from the tree/list, clear `OBJECT_ALLOCATED`, and release the metadata through RCU once its use count reaches zero.

The scanner (`kmemleak_scan()`) first resets object reference counts, queues already gray roots, and paints unsuitable physical objects black. It then scans root regions: percpu sections, online `struct page` memory, and optionally task stacks. `scan_block()` reads pointer-sized words, filters by known address ranges, and uses `pointer_update_refs()` to locate tracked objects and turn them gray once they reach `min_count`. `scan_gray_list()` recursively scans newly reachable objects until the gray list drains. A checksum pass temporarily grays modified white objects to reduce false positives, then a final pass marks old still-white allocated objects as reported leaks.

Runtime control flows through the debugfs file. Reads iterate reported unreferenced objects under `scan_mutex`; writes accept commands such as `scan`, `clear`, `off`, `stack=on/off`, `scan=on/off`, `scan=<seconds>`, and `dump=<address>`. Auto-scanning is performed by `kmemleak_scan_thread()`, started at late init when configured or by debugfs command.

## State And Persistence
Persistent runtime state is in global lists, RB trees, address bounds, object caches, the early metadata pool, `scan_thread`, scan timing variables, and enable/error flags. Object state persists until corresponding free hooks remove it or kmemleak is disabled and cleanup runs. Allocation stacks are persisted as stack-depot handles. Report state is sticky through `OBJECT_REPORTED` until `clear` paints reported leaks gray. The debugfs file is created in `kmemleak_late_init()`, while static data and BSS objects are registered in `kmemleak_init()` as initial gray roots.

## Dependencies And Integration Points
The file integrates with kernel allocators, vmalloc, percpu allocation, bootmem/memblock partial frees, physical memory tracking, debugfs, kthreads, workqueues, stack depot, RCU, RB trees, KASAN tag stripping, KFENCE size discovery, KCSAN disable/enable around checksums, memory hotplug zone iteration, and task-stack access. It is controlled by `CONFIG_DEBUG_KMEMLEAK*`, `kmemleak=on/off`, and the `verbose` module parameter.

## Risks
Correctness depends on strict lock ordering among `scan_mutex`, `kmemleak_lock`, and object locks. Missed allocator hooks, stale address bounds, overbroad `OBJECT_NO_SCAN`, or incorrect `min_count` choices can hide leaks. RB-tree overlap handling disables kmemleak because corrupt object ranges invalidate lookup safety. Scanning arbitrary memory requires careful KASAN/KCSAN suppression and chunking to avoid faulting, recursion, and latency. Debugfs `off` is irreversible, and cleanup preserves metadata if leaks were found until users explicitly clear it.

## Test Signals
Operational signals are kernel boot/init logs, warnings from overlap or pool exhaustion paths, `/sys/kernel/debug/kmemleak` scan output, `echo scan`, `echo clear`, and `echo dump=<addr>` behavior. Build coverage is gated by `CONFIG_DEBUG_KMEMLEAK`. Runtime validation should exercise kmalloc/vmalloc/percpu/physical allocation hooks, partial frees, false-positive annotations, auto-scan thread start/stop, and verbose leak reporting.
