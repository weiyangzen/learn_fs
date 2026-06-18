# sources/distributed-fs/ceph-client/security/bpf/hooks.c

Purpose: registers BPF LSM hook trampolines for all LSM hooks and reserves inode security blob storage for BPF local storage.

Important APIs, types, and functions: defines `bpf_lsm_hooks[]`, `bpf_lsmid`, `bpf_lsm_init()`, `bpf_lsm_blob_sizes`, and `DEFINE_LSM(bpf)`. Macro expansion over `linux/lsm_hook_defs.h` maps every hook name to `bpf_lsm_<hook>()`; it also registers `inode_free_security` to `bpf_inode_storage_free()`.

Control flow: at LSM initialization, `bpf_lsm_init()` calls `security_add_hooks()` and logs activation. The LSM descriptor advertises blob sizes so inode security storage includes `struct bpf_storage_blob`.

State and persistence: persistent kernel state is the registered LSM hook list and allocated inode blob space. Per-inode BPF storage is cleaned on inode security free.

Dependencies and integration: depends on BPF LSM generated hook functions, LSM infrastructure, UAPI LSM IDs, and BPF local storage.

Risks and test signals: macro-generated all-hook registration can break if hook signatures or generated BPF hook names drift. Test signals include BPF LSM boot registration, BPF LSM program attachment/execution for representative hooks, and inode storage cleanup.
