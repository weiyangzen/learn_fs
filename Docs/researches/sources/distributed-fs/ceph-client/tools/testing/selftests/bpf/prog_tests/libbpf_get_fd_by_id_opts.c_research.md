
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/libbpf_get_fd_by_id_opts.c

## Purpose

`libbpf_get_fd_by_id_opts.c` tests `*_get_fd_by_id_opts()` open flags, especially read-only map FD behavior, and verifies unsupported opts for prog/link/BTF get-by-id calls.

## Important APIs, Types, and Functions

The harness uses `test_libbpf_get_fd_by_id_opts.skel.h`, `bpf_map_get_info_by_fd()`, `bpf_map_get_fd_by_id()`, `bpf_map_get_fd_by_id_opts()`, `bpf_prog_get_fd_by_id_opts()`, `bpf_link_get_fd_by_id_opts()`, `bpf_btf_get_fd_by_id_opts()`, and `BPF_F_RDONLY`.

## Control Flow and Data Flow

After skeleton load/attach, it gets the `data_input` map ID. Legacy get-by-id and opts-NULL get-by-id are expected to fail in this test context, while opts with read-only flag should return an FD. Lookup through the read-only FD must work; update through it must fail; update through the original FD must work. Prog/link/BTF opts calls with ID 0 and read-only opts must return `-EINVAL`.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is map ID/FD and one map value. Dependencies include kernel support for map get-by-id open flags. Integration is libbpf syscall wrappers and map FD access mode. Risks are permission-sensitive behavior around get-by-id without opts and exact `-EINVAL` for unsupported object types. Test signals are read-only lookup success, read-only update failure, normal update success, and expected `-EINVAL` for prog/link/BTF opts.
