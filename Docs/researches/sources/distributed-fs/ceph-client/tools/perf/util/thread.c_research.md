# sources/distributed-fs/ceph-client/tools/perf/util/thread.c

## Purpose

`thread.c` implements perf's per-thread runtime object. A thread owns process/thread IDs, maps, comm history, namespace history, source-code state, unwind state hooks, optional synthesized stack state, architecture identity, filters, and LBR stitch state.

## Important APIs, Types, and Functions

Creation and lifetime functions are `thread__new()`, `thread__delete()`, `thread__get()`, `thread__put()`, and `thread__set_priv_destructor()`. Mapping functions include `thread__init_maps()`, `thread__insert_map()`, `thread__fork()`, `thread__find_map()`, `thread__find_symbol()`, `thread__find_cpumode_addr_location()`, and `thread__memcpy()`. Metadata functions include `thread__set_namespaces()`, `thread__set_comm()`, `thread__set_comm_from_proc()`, `thread__comm()`, `thread__exec_comm()`, `thread__comm_str()`, `thread__comm_len()`, `thread__e_machine()`, `thread__main_thread()`, and `thread__free_stitch_list()`.

## Control Flow and State

`thread__new()` initializes defaults, creates a placeholder `":tid"` comm, initializes locks and lists, sets refcount to one, and allocates namespace info. `thread__delete()` flushes stack state, drops maps, frees namespace/comm histories under write locks, clears source-code state, frees stitch lists, runs the private destructor, and frees the refcounted object. Comm and namespace updates append new history entries and timestamp old entries when appropriate. Fork handling copies or shares maps according to process/thread relationship and optionally clones maps for new processes. Architecture detection first consults cached thread fields, then leader thread, then mapped DSOs, and finally `/proc/<pid>/exe` for live sessions before falling back to host identity.

## Dependencies and Integration Points

It depends on machine/thread registries, maps, DSOs, symbols, namespaces, comm records, unwind access preparation, DWARF registers, callchain, and procfs helpers. It is a core integration point for perf record/report/top/script because most events are resolved through a `thread`.

## State and Persistence Behavior

State is in-memory and refcounted. Map groups may be shared with the process leader. Comm and namespace lists retain historical names/namespaces with timestamps for event-time resolution. Cached `e_machine` and `e_flags` avoid repeated ELF inspection. LBR stitch state and thread stacks are released on deletion.

## Risks and Test Signals

Risks include refcount leaks, stale map sharing after fork/exec, missing comm locks, incorrect architecture detection for mixed 32/64-bit workloads, and failed unwind preparation on new maps. Tests should cover thread creation/deletion, forked thread vs new process behavior, comm updates with exec flushing unwind state, namespace history, symbol/map lookup across CPU modes, `/proc` comm reads, and `thread__memcpy()` against mapped DSOs.
