# sources/distributed-fs/ceph-client/include/uapi/linux/lsm.h

Purpose: defines common userspace structures and identifiers for Linux Security Module context APIs.

Important APIs and types: `struct lsm_ctx` carries an LSM ID, LSM-specific flags, total record length, context length, and flexible context bytes. `LSM_ID_*` constants identify capability, SELinux, Smack, Tomoyo, AppArmor, Yama, LoadPin, SafeSetID, Lockdown, BPF, Landlock, IMA, EVM, and IPE. `LSM_ATTR_*` constants identify current, exec, fscreate, keycreate, previous, and socket-create security attributes. `LSM_FLAG_SINGLE` requests special single-record behavior.

Control flow: userspace LSM APIs return or accept one or more `lsm_ctx` records; callers iterate by `len`, interpret `ctx` according to `id`, and select requested attributes with `LSM_ATTR_*`.

State and persistence: no state in the header. Runtime context data comes from active LSMs and task/object security blobs. String contexts should be NUL-terminated when applicable; binary contexts are allowed.

Dependencies and integration points: depends on `linux/stddef.h`, `linux/types.h`, and `linux/unistd.h`; integrates LSM syscalls, security context queries, multi-LSM stacking, and userspace policy tools.

Risks and test signals: risks include incorrect flexible-array sizing, nonzero unused flags, string-vs-binary context assumptions, ID collisions, and multi-record parsing bugs. Test stacked LSM context retrieval, malformed `len`/`ctx_len`, `LSM_FLAG_SINGLE`, each supported attribute, and unknown IDs.
