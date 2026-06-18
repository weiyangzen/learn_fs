<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.c

## Purpose

`syscalltbl.c` maps architecture-specific syscall names and numbers for perf trace and related tools. It wraps generated syscall tables with lookup, reverse lookup, index iteration, and glob matching helpers.

## Important APIs, Types, and Functions

The public functions are `syscalltbl__name()`, `syscalltbl__id()`, `syscalltbl__num_idx()`, `syscalltbl__id_at_idx()`, `syscalltbl__strglobmatch_first()`, and `syscalltbl__strglobmatch_next()`. Internal `find_table()` selects a `struct syscalltbl` from `trace/beauty/generated/syscalltbl.c` and caches the last architecture. `syscallcmpname()` is the `bsearch()` comparator over sorted syscall-name indexes.

## Control Flow and Data Flow

Lookups start by finding the table for an ELF `e_machine` value. `EM_SPARCV9` aliases to `EM_SPARC`, and generated tables may include an `EM_NONE` fallback. Number-to-name lookup checks bounds in `num_to_name`; MIPS syscall numbers above 1000 are reduced modulo 1000 to mask ABI base values. Name-to-number lookup binary-searches `sorted_names` using the actual `num_to_name` strings. Glob iteration walks sorted names from a mutable index and returns matching syscall IDs.

## State and Persistence Behavior

The only mutable state is the static last-table cache in `find_table()`. The generated syscall table data is static read-only process data. Callers own the glob iteration index.

## Dependencies and Integration Points

The file depends on generated syscall table data, ELF machine constants, Linux kernel helper macros, `strglobmatch()`, and standard `bsearch()`. It integrates with perf trace syscall formatting, syscall filters, and beauty decoders that need stable syscall IDs and names.

## Risks and Edge Cases

Unknown architectures return null names, zero index count, or `-1` IDs. `syscalltbl__id_at_idx()` asserts index validity rather than returning an error for out-of-range input. The last-table cache is not synchronized, though races only affect redundant cache updates. MIPS modulo handling is specific to encoded ABI bases and should not be generalized to other architectures.

## Test Signals

Tests should verify known syscall name/id round trips for representative architectures, SPARCV9 aliasing, MIPS high-number masking, unknown architecture behavior, sorted index bounds, glob first/next iteration, and generated table ordering expected by `bsearch()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/syscalltbl.c -->
