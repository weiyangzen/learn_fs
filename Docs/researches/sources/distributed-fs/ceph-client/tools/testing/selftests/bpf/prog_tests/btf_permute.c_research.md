# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_permute.c

## Purpose
This file tests `btf__permute`, which reorders BTF type IDs and rewrites all internal type references. It covers both standalone base BTF and split BTF that references a base BTF.

## APIs, Types, and Functions
The test uses BTF builders, `btf__permute`, `VALIDATE_RAW_BTF`, `btf__new_empty_split`, and arrays of target IDs. `permute_base_check` and `permute_split_check` validate canonical postconditions. `test_permute_base` and `test_permute_split` exercise success and failure cases.

## Control Flow
The base test constructs a small graph of `int`, pointer, typedef, struct, const, and volatile types, validates it, applies a permutation, and checks that IDs and type references changed consistently. It then attempts invalid permutations such as duplicate targets, invalid IDs, wrong array length, and inclusion of ID zero, confirming the BTF remains unchanged after errors. The split test repeats the pattern where split-local IDs are permuted while base IDs remain stable.

## State, Dependencies, and Integration
State is entirely in-memory `struct btf` objects. The file integrates with libbpf's BTF mutation logic and with `btf_helpers.h` raw dump assertions.

## Risks and Test Signals
The core signal is exact raw BTF after permutation and unchanged BTF after invalid calls. Regressions are likely in reference rewriting, split/base ID boundary handling, and validation of permutation arrays.
