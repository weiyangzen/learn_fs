# sources/distributed-fs/ceph-client/tools/perf/util/thread.h

## Purpose

`thread.h` defines the refcounted `struct thread` and its accessor API. It is the central type for associating perf events with a task, maps, comm history, namespace state, filters, source-code state, unwind data, and branch-stack stitching.

## Important APIs, Types, and Functions

`DECLARE_RC_STRUCT(thread)` contains `maps`, `pid_`, `tid`, `ppid`, current CPU/guest CPU, `refcnt`, exit/filter flags, comm and namespace lists with rwsems, database ID, private data, `thread_stack`, namespace info, source-code state, ELF flags/machine, and `struct lbr_stitch`. The header exports lifecycle, comm, namespace, fork, map/symbol lookup, memory copy, architecture, filtering, stitch cleanup, and resolve functions. Inline accessors wrap fields through `RC_CHK_ACCESS`.

## Control Flow and State

The header's inline helpers provide controlled field mutation and filtering checks against global `symbol_conf` comm/PID/TID lists. Reference helpers ensure callers explicitly own thread references.

## Dependencies and Integration Points

It depends on refcount/rwsem/list infrastructure, callchain, source-code state, symbol configuration, and rc-check instrumentation. It is included across machine, event processing, unwinding, hist, and scripting code.

## Risks and Test Signals

Risks include direct field access bypassing rc-check wrappers, lock ordering issues around comm/namespace lists, and stale filter criteria. Tests should verify accessor behavior, filtering by comm/pid/tid lists, and proper cleanup of LBR stitch resources.
