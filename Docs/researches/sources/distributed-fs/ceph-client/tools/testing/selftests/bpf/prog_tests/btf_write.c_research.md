# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_write.c

## Purpose
This file validates libbpf's writable BTF builder APIs, raw dump output, BTF appending, split-BTF appending, and deduplication after combining split BTFs. It is a broad unit test for constructing every important BTF kind programmatically.

## APIs, Types, and Functions
`gen_btf` exercises `btf__add_str`, `btf__add_int`, pointer and qualifiers, arrays, struct/union fields, enum/enum64 values, typedef, fwd, float, func/proto/params, var, datasec, decl tag, and type tag APIs, then inspects `struct btf_type`, members, params, vars, and raw dumps. `test_btf_add`, `test_btf_add_btf`, and `test_btf_add_btf_split` cover creation, copying one BTF into another via `btf__add_btf`, split-BTF copying, and `btf__dedup`.

## Control Flow
The base add subtest creates empty BTF and calls `gen_btf`, which validates both successful additions and invalid inputs. The add-BTF subtest builds two independent BTFs, copies one into another, and validates ID offsets and raw layout. The split test creates a base, two split BTFs referencing the base and their own local types, appends both into a combined split BTF, validates type counts before and after dedup, and confirms duplicate typedefs collapse while references remain coherent.

## State, Dependencies, and Integration
All state is in-memory BTF. It depends on `btf_helpers.h` formatting and current libbpf semantics for ID allocation, raw type layout, and deduplication.

## Risks and Test Signals
Exact ID and raw dump assertions provide strong regression signals for builder behavior. Risks include brittleness to intentional BTF formatting changes and subtle split-ID remapping bugs when copying or deduplicating split BTFs.
