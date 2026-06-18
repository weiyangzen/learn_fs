
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_probes.c

## Purpose

`libbpf_probes.c` validates libbpf feature-probing helpers for BPF program types, map types, and selected helpers.

## Important APIs, Types, and Functions

It parses `/sys/kernel/btf/vmlinux` with `btf__parse()`, enumerates `enum bpf_prog_type` and `enum bpf_map_type`, and calls `libbpf_probe_bpf_prog_type()`, `libbpf_probe_bpf_map_type()`, and `libbpf_probe_bpf_helper()`.

## Control Flow and Data Flow

Program-type and map-type tests enumerate kernel BTF enum values, skip `UNSPEC` and max sentinels, create one subtest per enum, and assert libbpf probe result is supported. Helper tests use a small fixed table of supported/unsupported helper/program-type pairs and compare boolean results.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is only the parsed BTF object. Dependencies include vmlinux BTF and kernel support for probing all enumerated types. Integration is libbpf feature probe behavior against the running kernel's ABI. Risks are kernels exposing enum values that probing intentionally reports unsupported and helper support changing over time. Test signals are probe result 1 for all real enum types and table-expected helper support values.
