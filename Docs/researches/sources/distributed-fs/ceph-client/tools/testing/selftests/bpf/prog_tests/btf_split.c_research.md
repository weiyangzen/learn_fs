# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_split.c

## Purpose
This file tests split and multi-split BTF creation, serialization, parsing, and C declaration dumping. It verifies that split BTF inherits base metadata, keeps split-local types out of the base, and can round-trip raw BTF files without corrupting type IDs.

## APIs, Types, and Functions
It uses `btf__new_empty`, `btf__new_empty_split`, BTF builder APIs, `btf__set_pointer_size`, `btf__find_str`, `btf__type_by_id`, `btf__raw_data`, `btf__parse`, `btf__parse_split`, `btf_dump__new`, and `btf_dump__dump_type`. `btf_raw_write` writes raw BTF to temp files; `__test_btf_split` implements both single and multi-split cases.

## Control Flow
The test creates a base BTF with `int`, pointer, and `struct s1`, then a split BTF with `struct s2` referencing base types. In multi mode it creates a third BTF layer with `union u1` referencing split types. It validates type visibility, dumps all types to an in-memory stream, compares expected declarations, writes raw base/split/multisplit BTF to temp files, reparses them with proper bases, and byte-compares parsed type records against originals.

## State, Dependencies, and Integration
State includes in-memory BTF objects, dump buffers, and temp files under `/tmp`. It depends on libbpf split-BTF parser semantics and `btf_dump` output. Pointer size is forced to 8 to avoid host architecture drift.

## Risks and Test Signals
Signals include inherited pointer size, type visibility, exact dump text, raw write byte counts, parse success, type-count equality, and per-type memory equality. Risks are temp-file cleanup, strict text matching, and split-base ID boundary regressions.
