<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uidgid.h -->
# sources/distributed-fs/ceph-client/include/linux/uidgid.h

Purpose: provides the kernel's typed UID/GID helpers, separating internal kernel IDs (`kuid_t`, `kgid_t`) from userspace `uid_t`/`gid_t` values so user namespace translation cannot be accidentally skipped.

Important APIs and types: `KUIDT_INIT`, `KGIDT_INIT`, `GLOBAL_ROOT_UID/GID`, and `INVALID_UID/GID` define canonical constants. Inline comparators (`uid_eq`, `uid_gt`, `uid_gte`, `uid_lt`, `uid_lte` and GID variants) compare wrapped IDs through `__kuid_val()`/`__kgid_val()`. `uid_valid()`/`gid_valid()` reject the all-ones sentinel. With `CONFIG_USER_NS`, external translation APIs include `make_kuid()`, `make_kgid()`, `from_kuid()`, `from_kgid()`, munged overflow variants, and low-level `map_id_*()` helpers over `struct uid_gid_map`; without namespaces they collapse to identity mappings.

Control flow: callers construct or receive kernel IDs, compare them only through the typed helpers, and translate at user namespace boundaries. The mapping path is config-dependent: user namespace builds call real mapping code, while non-namespace builds inline identity conversions and overflow fallback.

State and persistence: this header owns no storage. Persistent identity state lives in credentials, inodes, IPC objects, and namespace UID/GID maps; these helpers control how that state is interpreted when crossing namespaces.

Dependencies and integration points: depends on `uidgid_types.h`, `highuid.h`, `struct user_namespace`, and `struct uid_gid_map`. It is used by VFS, credentials, capabilities, procfs/sysfs, IPC, and filesystem protocol code that must not confuse global kernel IDs with namespace-local user-visible IDs.

Risks and test signals: risks include direct `.val` access bypassing namespace conversion, treating invalid IDs as root in non-multiuser builds, missing overflowuid/overflowgid handling, and range mapping bugs. Test with user namespace ID maps, unmapped IDs, filesystem ownership display, chown across namespaces, and build matrices with `CONFIG_MULTIUSER`/`CONFIG_USER_NS` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uidgid.h -->
