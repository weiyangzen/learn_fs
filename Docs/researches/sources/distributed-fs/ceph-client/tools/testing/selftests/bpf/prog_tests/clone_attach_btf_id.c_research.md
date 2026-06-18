# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/clone_attach_btf_id.c

## Purpose
Verifies that cloning a tracing program preserves or reports the expected attach BTF ID metadata.

## Important APIs, types, and functions
Uses `clone_attach_btf_id.skel.h`, `bpf_prog_get_info_by_fd()`, and `bpf_program__fd()`. `get_prog_attach_btf_id()` reads `struct bpf_prog_info.attach_btf_id`. `test_clone_attach_btf_id()` loads the skeleton and compares attach BTF IDs for relevant programs.

## Control flow and state
The test has minimal runtime state: skeleton object and program FDs. It opens/loads the generated object, queries metadata through kernel BPF info API, asserts equality or expected values, then destroys the skeleton.

## Dependencies and integration points
Depends on generated tracing BPF object and kernel support for `attach_btf_id` in program info. Integrated as a small selftest entry.

## Risks and test signals
Risk is kernel metadata behavior drift. The signal is `bpf_prog_get_info_by_fd()` succeeding and reported attach BTF IDs matching expectations for cloned attach targets.
