# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_kind.c

## Purpose
This test covers BTF kind layout metadata used to decode future or unrecognized BTF kinds. It checks that raw BTF can optionally include a layout table and that a BTF with an otherwise unknown kind can be decoded when the layout section describes its shape.

## APIs, Types, and Functions
It uses `btf__new_empty_opts` with `LIBBPF_OPTS(btf_new_opts, .add_layout = true)`, `btf__raw_data`, `btf__add_int`, `btf__add_typedef`, `btf__parse`, `btf__find_by_name`, `btf__type_by_id`, and low-level mutation of `struct btf_header`, `struct btf_layout`, and `struct btf_type`. `write_raw_btf` persists synthetic raw BTF into temp files for parser tests.

## Control Flow
`test_btf_kind_encoding` creates empty BTF with and without layout metadata and asserts header offsets and lengths. `test_btf_kind_decoding` builds normal BTF, copies its raw bytes, appends or modifies layout metadata, overwrites one typedef's kind to `BTF_KIND_MAX + 1`, and verifies parse failure or success depending on the presence and correctness of kind layout entries. `test_btf_kind` dispatches encoding and decoding subtests.

## State, Dependencies, and Integration
The file uses temporary `/tmp/test_btf_kind.*` files and raw memory buffers. It depends on libbpf's experimental or recent BTF layout support and on the kernel/libbpf UAPI definitions for `struct btf_layout`.

## Risks and Test Signals
Strong signals are header layout assertions, parser success/failure, and ability to find later named types after the unknown kind. Risks are high around UAPI version skew, raw buffer mutation, and layout alignment assumptions.
