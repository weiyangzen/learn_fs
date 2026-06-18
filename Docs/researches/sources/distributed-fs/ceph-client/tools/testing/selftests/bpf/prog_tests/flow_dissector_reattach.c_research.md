
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_reattach.c

## Purpose

`flow_dissector_reattach.c` exhaustively tests attach, detach, query, link creation, link update, and link-info behavior for `BPF_FLOW_DISSECTOR` in init and non-root network namespaces.

## Important APIs, Types, and Functions

The file uses low-level BPF syscalls via libbpf wrappers: `bpf_prog_attach()`, `bpf_prog_detach2()`, `bpf_prog_query()`, `bpf_link_create()`, `bpf_link_update()`, `bpf_link_get_info_by_fd()`, and `bpf_prog_get_info_by_fd()`. It loads minimal flow-dissector programs with `bpf_test_load_program()`, switches namespaces with `setns()`/`unshare(CLONE_NEWNET)`, and checks `struct bpf_link_info.netns`.

## Control Flow and Data Flow

`serial_test_flow_dissector_reattach()` saves the starting netns, moves to `/proc/1/ns/net`, skips if init_net already has a dissector, runs a table of subtests there, then creates a new netns and repeats. Subtests cover prog/prog replacement, link/link exclusivity, prog-vs-link exclusivity, detach/query, link close, update with/without `BPF_F_REPLACE`, invalid opts, invalid program type, destroyed netns, and link info stability across updates.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the per-netns flow dissector attachment and link FD lifetime. Dependencies include namespace privileges, no preexisting init_net dissector, low-level BPF syscall support, and correct errno reporting. Integration points are kernel netns attachment ownership and libbpf link APIs. Risks are leaked namespace state on early failure, global init_net interference, and exact errno drift (`EEXIST`, `E2BIG`, `EINVAL`, `EPERM`, `EBADF`, `ENOLINK`). Test signals are queried program IDs matching expected FDs, no attachment after detach/close, and link info matching program id, link id, attach type, and netns inode.
