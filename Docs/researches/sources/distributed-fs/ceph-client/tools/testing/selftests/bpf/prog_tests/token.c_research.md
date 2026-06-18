# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/token.c

## Purpose
Comprehensive BPF token selftest. It validates delegated bpffs mount options, token creation in a user namespace, token-gated map/BTF/program/object loading, libbpf explicit and implicit token discovery, LSM veto hooks, freplace behavior, struct_ops BTF delegation, token info reporting, and kallsyms exposure.

## APIs, Types, and Functions
Key helpers wrap mount API syscalls (`fsopen`, `fsconfig`, `fsmount`, `fspick`, `move_mount`), capability drop/restore, delegation mask formatting, Unix fd passing (`sendfd`, `recvfd`), user namespace setup, and parent/child orchestration. `struct bpffs_opts` describes delegated command/map/program/attach masks. Callback tests include `userns_map_create()`, `userns_btf_load()`, `userns_prog_load()`, object privileged map/prog/freplace tests, BTF success/failure checks, implicit token tests, `userns_obj_priv_prog_kallsyms()`, and `userns_bpf_token_info()`.

## Control Flow, State, and Persistence
`serial_test_token()` runs subtests by constructing `bpffs_opts` and calling `subtest_userns()`. The child loads an LSM skeleton, enters a new user and mount namespace, creates a bpffs fs context, proves unprivileged delegation reconfiguration is rejected, sends the fs fd to the parent, receives completion notification, materializes a detached bpffs mount, creates a token fd, sends it back, and runs the callback. The parent receives the fs context, applies privileged delegation options, signals the child, receives the token fd, and waits for child exit. State is in transient fds, namespaces, bpffs mounts, environment variable `LIBBPF_BPF_TOKEN_PATH`, BSS flags in `token_lsm`, and temporary custom mount directory.

## Dependencies and Integration
Depends on Linux new mount API, user namespaces, capability helpers, sysctl helpers, libbpf token APIs, BTF APIs, kallsyms helpers, and skeletons for private map/prog, struct_ops, kallsyms, LSM, and freplace programs. It integrates with bpffs delegation options such as `delegate_cmds`, `delegate_maps`, `delegate_progs`, and `delegate_attachs`.

## Risks and Test Signals
Risks include kernel/config support for user namespaces, bpffs token delegation, LSM hooks, struct_ops, kallsyms visibility, mount namespace permissions, and cleanup of custom directories or env vars. Signals include expected `-EPERM` without both token and namespaced caps, success with correct token delegation, LSM-induced failures, implicit token success from `/sys/fs/bpf` or env path, expected freplace success/failure split, token info masks, and kallsyms containing loaded token BPF functions.
