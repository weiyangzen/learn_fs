# sources/distributed-fs/ceph-client/kernel/bpf/token.c

## Purpose

`token.c` implements BPF token objects, which delegate a bounded subset of BPF capabilities from a bpffs mount's user namespace to token holders. Tokens let user namespaces expose selected BPF commands, map types, program types, and attach types without granting broad global privileges.

## Important APIs, Types, And Functions

- Capability checks: `bpf_token_capable()` applies namespace capability checks and LSM token capability policy; `bpf_ns_capable()` allows `CAP_SYS_ADMIN` to satisfy non-admin capability checks in the token namespace.
- Lifetime: `bpf_token_inc()`, `bpf_token_put()`, deferred `bpf_token_put_deferred()`, `bpf_token_free()`, and `bpf_token_release()`.
- FD interface: `bpf_token_fops` supports release and fdinfo display through `bpf_token_show_fdinfo()`.
- Creation: `bpf_token_create()` validates a bpffs root FD, namespace ownership, `CAP_BPF`, non-init user namespace, delegation mount options, LSM policy, pseudo inode/file creation, and token initialization.
- Introspection and lookup: `bpf_token_get_info_by_fd()` and `bpf_token_get_from_fd()`.
- Delegation filters: `bpf_token_allow_cmd()`, `bpf_token_allow_map_type()`, and `bpf_token_allow_prog_type()`.

## Control Flow

Token creation receives a bpffs FD from `BPF_TOKEN_CREATE`. It verifies the FD refers to the bpffs mount root, checks access permissions, requires the current user namespace to match the bpffs superblock namespace, requires `CAP_BPF` in that namespace, rejects init-user-namespace creation, and requires at least one delegation mask in bpffs mount options. It then creates an unlinked pseudo inode/file, allocates a token, copies delegation masks from mount options, calls `security_bpf_token_create()`, takes a user namespace ref, stores the token in file private data, and publishes the FD.

Consumers get a token via `bpf_token_get_from_fd()`, verify the file ops, increment the token refcount, and then use `bpf_token_allow_*()` plus `bpf_token_capable()` in syscall paths. If a token does not grant a command/type, callers generally drop it and fall back to ambient task capabilities.

## State And Persistence Behavior

A token stores an atomic refcount, deferred free work item, owning user namespace, and four 64-bit allow masks: commands, map types, program types, and attach types. The token persists while its FD or any temporarily acquired references exist. Final release is deferred to a workqueue, where LSM cleanup, user namespace put, and memory free occur.

## Dependencies And Integration Points

The file integrates with bpffs superblock/mount options, user namespaces, capability checks, LSM hooks (`security_bpf_token_*`), pseudo inode/file allocation, fd helpers, and `syscall.c` command paths for map create, program load, BTF load/get, and token info. bpffs mount options are the persistent policy source; token FDs are the transport.

## Risks And Edge Cases

The security boundary depends on strict bpffs-root and namespace checks. Allowing token creation from nested paths, mismatched namespaces, or init user namespace would weaken delegation semantics. Mask sizes are capped by build-time checks in fdinfo; new BPF enum values beyond 63 require rethinking mask representation. Deferred freeing must avoid use-after-free while syscall paths hold temporary references. LSM denial must consistently override namespace capability success.

## Test Signals

Tests should cover token creation success from a delegated bpffs mount in a non-init user namespace, failure from non-root bpffs dentries, non-bpffs FDs, no delegation masks, init user namespace, missing `CAP_BPF`, and mismatched user namespaces. Operation tests should verify allowed and denied command/map/prog/attach masks, fdinfo and `BPF_OBJ_GET_INFO_BY_FD` output, refcounting across close and concurrent use, and LSM hook denial paths.
