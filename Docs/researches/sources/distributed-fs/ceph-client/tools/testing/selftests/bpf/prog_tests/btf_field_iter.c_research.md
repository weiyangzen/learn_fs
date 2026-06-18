# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_field_iter.c

## Purpose
This file validates libbpf internal BTF field iteration over all supported BTF kind layouts. It fabricates representative BTF types and checks that each raw type exposes the expected type-id and string fields through `btf_field_iter`.

## APIs, Types, and Functions
The `fields` table holds expected `ids` and `strs` for each type. The test builds BTF with `btf__add_int`, pointer, array, struct, union, enum, fwd, typedef, qualifiers, function prototype/function, vars, float, decl/type tags, enum64, and datasec APIs. It uses `btf_field_iter` and `btf_field_iter_next` from `bpf/libbpf_internal.h`.

## Control Flow
`test_btf_field_iter` creates a synthetic BTF, validates its raw dump, then iterates type IDs from 1 to `btf__type_cnt() - 1`. For each type it initializes the field iterator and walks every exposed field, comparing discovered type IDs and strings against the corresponding expected row in `fields`.

## State, Dependencies, and Integration
State is a single in-memory `struct btf`. This is an internal libbpf behavior test rather than a kernel verifier test; it depends on exact struct layout knowledge embedded in libbpf's BTF field iterator.

## Risks and Test Signals
The test detects omissions or ordering changes in internal BTF metadata traversal. Because expectations are aligned to fabricated type IDs, any builder behavior change that changes ID assignment, vlen, or field traversal ordering can fail the test.
