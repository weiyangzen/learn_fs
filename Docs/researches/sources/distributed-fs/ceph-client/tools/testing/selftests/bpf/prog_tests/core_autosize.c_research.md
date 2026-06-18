# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_autosize.c

## Purpose
Tests CO-RE autosizing across a custom 32-bit-pointer target BTF and BPF-side 64-bit target, including same-size, downsize, probed reads, and expected signed-load failure.

## Important APIs, types, and functions
Uses libbpf BTF construction (`btf__new_empty()`, `btf__set_pointer_size()`, `btf__add_int()`, `btf__add_struct()`, `btf__raw_data()`), custom `bpf_object_open_opts.btf_custom_path`, skeleton `test_core_autosize`, and BSS map lookup. A real-layout `test_struct___real` mirrors the custom target BTF.

## Control flow and state
The test writes a temporary BTF file, opens the skeleton with that BTF, disables `handle_signed`, loads and attaches three programs, reads `.bss` into local `out`, and checks all expected values. It then reloads with signed handling enabled and expects load failure. State is temporary `/tmp/core_autosize.btf.*`, BTF object, skeleton links, and BSS output.

## Dependencies and integration points
Depends on libbpf BTF APIs, generated CO-RE skeleton, mmap/lookup of BSS data, and tracepoint attachment. Integrated as a CO-RE selftest.

## Risks and test signals
Risks include BTF encoding mistakes, pointer-size assumptions, and temp-file cleanup. Passing signals are exact values for same-sized/down-sized/probed reads and an expected load error for signed autosize handling.
