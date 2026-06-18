# sources/distributed-fs/ceph-client/security/apparmor/lsm.c

Purpose: registers AppArmor as an LSM and implements the kernel hook glue for credentials, paths, files, mmap, mounts, procattrs, exec, task controls, sockets, secctx, io_uring, sysctl, netfilter secmark, buffer caching, and module parameters.

Important APIs/functions: credential hooks manage `cred_label`; file/path hooks call `aa_path_perm()`, `aa_file_perm()`, and mount helpers; procattr hooks dispatch profile/hat transitions; task hooks mediate rlimits, ptrace, signals, and user namespace creation; socket hooks label sockets, mediate AF/Unix/secmark operations, and serve peer secctx; `aa_get_buffer()`/`aa_put_buffer()` provide reusable pathname buffers; `apparmor_init()` initializes DFA engines, root namespace, sysctls, buffers, init label, hooks, and audit LSM config.

Control flow: hooks usually enter a current-label critical section, bypass unconfined labels, call the subsystem-specific mediator, then release refs. Exec commit inherits file permissions, clears death signal, transitions rlimits, and later clears task transition context. Init unpacks `nulldfa.in` and `stacksplitdfa.in`, allocates `nullpdb`, creates apparmorfs, then registers hooks via `DEFINE_LSM`.

State and persistence: global knobs include mode, audit, debug, lock_policy, path_max, rawdata export/compression, initialized/enabled flags, root namespace, DFA globals, per-CPU/global buffer pools, LSM blob sizes, sysctls, and socket/file/task blobs.

Dependencies and integration: this is the integration hub for all AppArmor modules plus Linux LSM, audit, netfilter, sysfs, sysctl, zstd, and apparmorfs. Risks include refcount mistakes in blobs, sleeping/allocation in atomic contexts, parameter permission bypass, policy lock semantics, hook ordering, and secmark drop behavior. Test boot enable/disable, init failure cleanup, all hook classes, module parameter permissions, buffer exhaustion, netfilter secmark, io_uring, and policy replacement during active task/file/socket use.
