# sources/distributed-fs/ceph-client/tools/perf/util/machine.h

## Purpose

`machine.h` declares perf's machine and machines abstractions: the top-level state used to resolve events, threads, DSOs, maps, callchains, kernel symbols, host/guest machines, and per-CPU current thread information.

## Important APIs, Types, and Functions

`struct machine` contains guest rb linkage, pid, id header size, flags, root and mmap names, thread/DSO containers, perf environment, kernel maps, vmlinux map, cached kernel start, lock/sched/trace section ranges, parallelism, current TID array, private tool storage, parent `machines`, and trampoline status. `struct machines` contains the host machine and cached guest rb-root. The header declares lifecycle, event processing, thread lookup, sample resolution, callchain resolution, kernel map creation/destruction/loading, DSO iteration, kernel-map iteration, lock-function detection, current TID access, and kernel address resolver APIs.

## Control Flow

There is no implementation flow here, but the declarations define the normal caller flow: initialize machines, create kernel maps, process perf events through `machine__process_event()`, resolve samples/callchains, iterate threads or DSOs for reporting, then destroy maps and machines.

## State and Persistence Behavior

The struct layout defines long-lived mutable analysis state. Inline helpers expose the kernel map, kernel maps, host/default guest checks, lazy kernel-start lookup, kernel-IP classification, and kernel symbol lookup wrappers. Current TID state persists per CPU until updated by switch or tracking code.

## Dependencies and Integration Points

The header depends on rbtrees, maps, DSOs, rwsems, and threads. It is included by event readers, report/script/annotate/mem/lock tools, branch and callchain code, kernel symbol resolvers, and guest handling code.

## Risks and Edge Cases

Because many fields are public to perf internals, invariants depend on disciplined callers: maps and threads are refcounted, kernel maps must be created before kernel symbol lookup, and `machine->env` must be populated before architecture or CPU queries. The host kernel id is `-1` and default guest id is `0`, so callers must not treat pid values as ordinary process ids in machine trees.

## Test Signals

Compile coverage should include all major perf tools that include this header. Runtime tests should confirm host/default guest checks, kernel symbol wrappers, current TID helpers, event processor declarations, and callchain prototypes remain compatible with their implementations.
