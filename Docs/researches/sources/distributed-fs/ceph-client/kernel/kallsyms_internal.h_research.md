# sources/distributed-fs/ceph-client/kernel/kallsyms_internal.h

## Purpose
Declares the generated kallsyms data arrays consumed by `kallsyms.c` and selftests. It is a private contract between the build-time kallsyms generator and kernel lookup code.

## Important APIs, Types, and Functions
The header exports no functions. It declares `kallsyms_offsets`, `kallsyms_names`, `kallsyms_num_syms`, `kallsyms_token_table`, `kallsyms_token_index`, `kallsyms_markers`, and `kallsyms_seqs_of_names`.

## Control Flow
No runtime control flow exists in the header. Consumers use `kallsyms_markers` to jump into compressed names, `kallsyms_token_*` to expand names, `kallsyms_offsets` to compute addresses, and `kallsyms_seqs_of_names` for name-sorted binary search.

## State and Persistence
State is generated at build time and linked into the kernel image as constant data. It persists only for the lifetime of the running kernel.

## Dependencies and Integration Points
Depends on `linux/types.h` and on generated symbols emitted by the build system. `kallsyms.c` and `kallsyms_selftest.c` must agree on array encoding.

## Risks
Any generator/layout mismatch corrupts symbol lookup globally. The arrays have implicit size and encoding relationships not captured by C types, so changes must be coordinated with kallsyms generation scripts.

## Test Signals
The kallsyms selftest indirectly validates this header by traversing all symbols, calculating compression ratios, and matching lookups against expected addresses.
