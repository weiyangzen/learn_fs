# sources/distributed-fs/ceph-client/include/linux/security.h

Purpose: `security.h` is the central Linux Security Module facade. It declares LSM event types, lockdown reasons, security contexts/properties, capability fallback functions, and hundreds of `security_*()` hooks spanning process, filesystem, IPC, networking, keys, audit, BPF, perf, io_uring, block devices, and securityfs.

Important APIs/types/functions: Key types include `enum lsm_event`, `struct dm_verity_digest`, `enum lsm_integrity_type`, `enum lockdown_reason`, `struct lsm_prop`, and `struct lsm_context`. Important helpers include `kernel_load_data_id_str()`, `lsmprop_init()`, `lsmprop_is_set()`, notifier registration, `security_init()`, `early_security_init()`, `security_locked_down()`, `lsm_fill_user_ctx()`, and the large hook families `security_bprm_*`, `security_inode_*`, `security_file_*`, `security_task_*`, `security_socket_*`, `security_xfrm_*`, `security_key_*`, `security_bpf_*`, `security_perf_event_*`, and `security_uring_*`.

Control flow: Callers in core kernel paths invoke `security_*()` hooks at decision or labeling points. With `CONFIG_SECURITY`, implementation files dispatch to registered LSM hooks and aggregate decisions. Without `CONFIG_SECURITY` or per-feature configs, this header provides inline fallbacks, mostly allow/no-op, with selected capability enforcement delegated to `cap_*()` functions. Conditional sections separately gate network, path, keys, audit, securityfs, BPF, perf, and io_uring hooks.

State and persistence behavior: The header itself stores no security state but describes how state is attached to credentials, inodes, superblocks, files, IPC objects, sockets, keys, BPF objects, perf events, block devices, and LSM property structures. Context buffers returned through `struct lsm_context` must be released with `security_release_secctx()`. Mount options and xattrs carry persistent labels for LSMs.

Dependencies and integration points: It depends on core VFS, task credentials, namespaces, IPC, sockets, XFRM, keys, audit, BPF, perf, io_uring, block layer, kernel file loading, and individual LSM property headers for SELinux, Smack, AppArmor, and BPF LSM. The lockdown enum must stay synchronized with `security/lockdown/lockdown.c`.

Risks: Hook placement is security-critical: missing a call site can bypass policy, while incorrect fallback semantics can change behavior when security configs are disabled. Context length and user-copy helpers must avoid truncation and UAF. Lockdown reasons are not stable fine-grained ABI, so policy should not expose brittle reason-level guarantees.

Test signals: Build matrices for `CONFIG_SECURITY` and each feature flag, LSM stacking property propagation, inode xattr labeling, mount option parsing, exec credential transitions, capability fallbacks, network socket and SCTP hooks, key/audit rules, BPF token checks, perf/io_uring policy, securityfs disabled stubs, and lockdown reason coverage.
