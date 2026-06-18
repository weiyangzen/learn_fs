# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_reloc_raw.c

## Purpose
Tests raw BPF syscall handling for a CO-RE relocation that references a non-existent local BTF type ID, which cannot be expressed through normal libbpf loading.

## Important APIs, types, and functions
Uses handcrafted raw BTF (`struct test_btf`), `bpf_btf_load()`, `sys_bpf_prog_load()`, raw `union bpf_attr`, `bpf_func_info`, and `bpf_core_relo`. `test_bad_local_id()` sets relocation `type_id = 100500` and asserts verifier log contains the bad type ID message.

## Control flow and state
The test loads raw BTF, then attempts direct program load with one relocation. Program load is expected to fail. State is limited to BTF FD, optional program FD, and static log buffer.

## Dependencies and integration points
Depends on BPF syscall ABI, verifier log behavior, and test BTF encoding helpers. Integrated via `test_core_reloc_raw()` subtest `bad_local_id`.

## Risks and test signals
Verifier log wording is part of the assertion and can drift. Passing signal is rejected program load plus log substring `relo #0: bad type id 100500`.
