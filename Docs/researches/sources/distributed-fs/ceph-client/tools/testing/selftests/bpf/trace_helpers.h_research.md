<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.h

## Purpose
`trace_helpers.h` declares tracing helper data structures and APIs for kernel symbol lookup, trace-pipe reading, uprobe offset resolution, build-ID extraction, and ftrace symbol/address enumeration.

## Important APIs, Types, And Functions
- `SYS_PREFIX` maps architectures to syscall symbol prefixes.
- `ALIGN()` and `__ALIGN_MASK()` support ELF note parsing and other aligned metadata handling.
- `struct ksym` and `struct ksyms` model symbol address/name arrays plus filtered symbol lists.
- Function pointer typedefs allow custom sorting/searching comparators.
- Declarations cover kallsyms load/search, `kallsyms_find()`, trace-pipe readers, `get_uprobe_offset()`, `get_rel_offset()`, `read_build_id()`, `bpf_get_ksyms()`, and `bpf_get_addrs()`.

## Control Flow
No standalone flow exists; consumers call the declared helpers when preparing trace targets or decoding kernel/user addresses.

## State And Persistence
The header owns no state but defines ownership-bearing structures that implementations allocate and free.

## Dependencies And Integration Points
It includes libbpf for build ID sizing and integrates with `trace_helpers.c` and many BPF tracing tests.

## Risks And Edge Cases
`SYS_PREFIX` must track kernel symbol naming by architecture. Structure layout changes affect all consumers. Consumers must free `struct ksyms` correctly to avoid leaks.

## Test Signals
Regressions show as compile errors, inability to resolve syscall/kallsyms names, bad uprobe offsets, or trace attach failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/trace_helpers.h -->
