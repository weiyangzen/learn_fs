# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_dump.c

## Purpose
This file exercises `btf_dump` C type emission and typed data formatting. It compares generated C declarations from BTF-bearing object files against embedded expected output, then validates value dumping for kernel BTF types, synthetic floats, strings, DATASEC variables, and edge cases such as overflow, zero elision, type tags, and anonymous naming conflicts.

## APIs, Types, and Functions
Core APIs include `btf__parse_elf`, `btf__parse`, `libbpf_find_kernel_btf`, `btf_dump__new`, `btf_dump__dump_type`, `btf_dump__dump_type_data`, `btf__find_by_name`, `btf__resolve_size`, and BTF builder APIs for incremental cases. `struct btf_dump_test_case` enumerates fixture objects; `struct test_ctx` owns an in-memory BTF plus `open_memstream` dump buffer. Helper callbacks are `btf_dump_printf` and `btf_dump_snprintf`.

## Control Flow
`test_btf_dump_case` parses each `.bpf.o`, forces pointer size where necessary, writes all dumped declarations to a temp file, and compares with an `awk | diff` extraction from the corresponding source fixture. `test_btf_dump_incremental` checks that already-emitted names influence later conflict resolution. `test_btf_dump_type_tags` checks C attributes for type tags and attrs. The value dump path constructs a dump object over kernel BTF, then subtests integers, floats, chars, typedefs, enums, structs/unions, variables, strings, and DATASEC output using macros that compare exact string output and return sizes.

## State, Dependencies, and Integration
Persistent state is limited to temporary files under `/tmp`, deleted after diffing. The test depends on fixture BPF objects and sources, kernel BTF, libc `open_memstream`, host compiler support for optional `__int128`, and libbpf's BTF dump implementation. It integrates with selftest subtest dispatch through `test__start_subtest`.

## Risks and Test Signals
Exact string comparisons make this a high-sensitivity formatting regression test. Risks include fragile dependency on kernel BTF type names and layouts, architecture pointer-size assumptions, shell `awk`/`diff` behavior, and generated output changes that are semantically valid but textually different.
