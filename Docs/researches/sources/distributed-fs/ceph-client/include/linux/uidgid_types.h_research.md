<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uidgid_types.h -->
# sources/distributed-fs/ceph-client/include/linux/uidgid_types.h

Purpose: defines the opaque wrapper structs used for kernel-internal user and group IDs.

Important APIs and types: `kuid_t` wraps a `uid_t val`; `kgid_t` wraps a `gid_t val`. The wrappers intentionally make raw userspace ID values type-incompatible with internal kernel IDs unless code explicitly converts.

Control flow: this is a pure type header. Higher-level conversion, comparison, and validity helpers live in `uidgid.h`.

State and persistence: no state is stored here. The fields are embedded in credentials and ownership-bearing objects elsewhere.

Dependencies and integration points: depends only on `linux/types.h`; it is a low-level include for credential, VFS, namespace, and security code that needs type declarations without the full mapping API.

Risks and test signals: risks are mostly misuse of `.val` directly or ABI-width assumptions about `uid_t`/`gid_t`. Test signals are compile-time type checking and namespace/ownership tests that catch missing conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uidgid_types.h -->
