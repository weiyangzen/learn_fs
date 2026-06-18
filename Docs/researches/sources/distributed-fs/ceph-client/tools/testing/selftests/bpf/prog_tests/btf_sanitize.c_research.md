# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_sanitize.c

## Purpose
This file validates libbpf's BTF sanitization when a kernel feature is missing. It specifically checks that BTF layout metadata is removed when `FEAT_BTF_LAYOUT` is marked unsupported.

## APIs, Types, and Functions
It defines a synthetic `struct layout_btf` containing a `struct btf_header`, one encoded int type, layout entries, and strings. It uses `btf__new`, `btf__raw_data`, `bpf_object_set_feat_cache`, `kernel_supports`, `bpf_object__sanitize_btf`, and the `kfree_skb` skeleton object as a host `bpf_object`.

## Control Flow
`test_btf_sanitize_layout` opens the skeleton, parses the synthetic BTF, confirms nonzero `layout_off` and `layout_len`, allocates a feature cache that marks all features supported except `FEAT_BTF_LAYOUT`, installs it on the object, and asserts the feature gates. Sanitization should return BTF with layout offsets zeroed, strings moved after types, unchanged string length, and a smaller raw size.

## State, Dependencies, and Integration
State includes a manually allocated feature cache transferred to the skeleton object and BTF objects freed at exit. This test integrates with libbpf's internal feature-detection cache and BTF object sanitization path.

## Risks and Test Signals
The signal is header-level structural change, not verifier execution. Risks include UAPI layout changes, ownership of the feature cache, and mismatches between skeleton object feature probing and manual feature cache overrides.
