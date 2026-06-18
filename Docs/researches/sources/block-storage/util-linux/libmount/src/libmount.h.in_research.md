# File Research: sources/block-storage/util-linux/libmount/src/libmount.h.in

This header template defines the public libmount API, version macros, opaque types, option maps, error codes, exit codes, flags, and exported functions. Build substitution fills `@LIBMOUNT_VERSION@` and version components.

Major declarations:

- Opaque types: cache, lock, iterator, filesystem, table, update, context, monitor, tabdiff, namespace, and statmount settings.
- `struct libmnt_optmap` and option-map masks (`MNT_INVERT`, `MNT_NOMTAB`, `MNT_PREFIX`, `MNT_NOHLPS`, `MNT_NOFSTAB`, `MNT_SUPERBLOCK`).
- Action constants `MNT_ACT_MOUNT` and `MNT_ACT_UMOUNT`.
- Private libmount error codes `MNT_ERR_*`, including loop, mount option, apply flags, lock, namespace, chown/chmod, idmap, and exec failures.
- Public command-style exit codes `MNT_EX_*`.
- API declarations for initialization, version/features, utilities, cache, optstring parsing, iterators, option maps, locks, filesystem entries, statmount, table parsing/manipulation, listmount, updates, diffs, monitor, context configuration/status, mount/umount flows, and namespace switching.
- Userspace mount option bits such as `MNT_MS_LOOP`, `MNT_MS_OFFSET`, dm-verity bits, helper/uhelper bits, and ownership/user bits.
- Linux `MS_*` fallback constants and derived masks such as `MS_PROPAGATION`, `MS_SECURE`, and `MS_OWNERSECURE`.

Important relationships:

- Declares the implementation surface provided by files in this group: `init.c`, `iter.c`, `lock.c`, `fs.c`, `fs_statmount.c`, and `context_umount.c`.
- The hook files are internal and not directly exposed here, but their errors and option bits are part of the public surface through `MNT_ERR_*` and `MNT_MS_*`.
- The header exposes staged mount/umount APIs: prepare, do, finalize, full operation, and next-entry iteration.

Risk notes:

- Because this is an installed public API template, changes here affect ABI/API consumers.
- Some error and flag values are fixed numeric contracts; renumbering would break callers.
- Fallback `MS_*` definitions are guarded to avoid collisions with libc/kernel headers.
