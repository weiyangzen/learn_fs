# sources/distributed-fs/ceph-client/include/linux/projid.h

Purpose: defines type-safe project ID handling for filesystems, separating userspace `projid_t` values from kernel-internal `kprojid_t` values and supporting user namespace mappings.

Important APIs and types: `projid_t` is the userspace-style scalar, while `kprojid_t` wraps the kernel value. Helpers include `__kprojid_val()`, `KPROJIDT_INIT()`, `INVALID_PROJID`, `OVERFLOW_PROJID`, `projid_eq()`, `projid_lt()`, and `projid_valid()`. With user namespaces, `make_kprojid()`, `from_kprojid()`, `from_kprojid_munged()`, and `kprojid_has_mapping()` perform namespace translation; without them they are identity mappings with overflow munging.

Control flow: filesystems convert incoming project IDs from a user namespace into `kprojid_t`, store/compare the internal value, and convert back for presentation. The munged form substitutes `OVERFLOW_PROJID` when no mapping exists.

State and persistence: no state is stored here, but project IDs are persistent filesystem metadata in quota/project-inheritance users. Namespace mapping state belongs to `struct user_namespace`.

Dependencies and integration points: depends on kernel UID-sized types and user namespace mapping code. It integrates quota, filesystem inode attributes, idmapped presentation, and user namespace permissions.

Risks and test signals: risks include confusing `projid_t` and `kprojid_t`, failing to check mappings, storing unmapped values, and overflow behavior differences with `CONFIG_USER_NS`. Test project quota operations across user namespaces, invalid project IDs, serialization/deserialization of inode metadata, and user-ns disabled builds.
