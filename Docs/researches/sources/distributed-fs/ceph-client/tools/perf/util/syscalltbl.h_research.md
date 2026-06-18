<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.h

## Purpose

`syscalltbl.h` declares the syscall table lookup API used by perf tools to translate syscall IDs and names for a selected ELF machine architecture.

## Important APIs, Types, and Functions

The declarations provide number-to-name lookup (`syscalltbl__name()`), name-to-number lookup (`syscalltbl__id()`), sorted-table size (`syscalltbl__num_idx()`), index-to-id lookup (`syscalltbl__id_at_idx()`), and glob iteration (`syscalltbl__strglobmatch_first()` and `syscalltbl__strglobmatch_next()`).

## Control Flow and Data Flow

Callers supply an `e_machine` architecture value for every query. Glob iteration uses an integer cursor initialized by the `first` function and advanced by the `next` function.

## State and Persistence Behavior

The header exposes no state. The implementation uses static generated tables and an internal last-lookup cache.

## Dependencies and Integration Points

It integrates with perf trace filtering and syscall beautification code. Consumers must include ELF machine constants from elsewhere; this header deliberately stays small and only declares the lookup contract.

## Risks and Edge Cases

Callers must handle null names and `-1` IDs for unsupported architectures or missing syscalls. The index cursor for glob matching is mutable caller state and should not be shared across independent iterations.

## Test Signals

Compile tests should ensure users can include this header without pulling generated table internals. API tests should exercise all declared functions through `syscalltbl.c` for at least one supported and one unsupported architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.h -->
