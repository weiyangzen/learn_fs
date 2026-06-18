# sources/distributed-fs/ceph-client/include/linux/user_namespace.h

## Purpose
This header defines user namespace identity mapping, per-namespace resource accounting, keyring/sysctl state, and APIs for creating, referencing, and querying user namespaces.

## Important APIs, types, and functions
Key types are `uid_gid_extent`, `uid_gid_map`, `user_namespace`, and `ucounts`. Enums define namespace and rlimit count classes. APIs include sysctl setup/retire, `inc_ucount()`/`dec_ucount()`, ucount allocation/refcounting, rlimit count helpers, `get_user_ns()`/`put_user_ns()`, `create_user_ns()`, `unshare_userns()`, `/proc/*_map` write helpers, setgroups checks, and namespace ancestry helpers.

## Control flow, state, and persistence
Namespace creation initializes UID/GID/projid maps, parent/owner/group, flags, counts, keyring/sysctl state, and resource limits. Proc map writes populate translation extents; resource helpers increment/decrement per-user counters and rlimit usage. State is kernel runtime namespace state; mappings and sysctls are observable through procfs but not persisted by this header.

## Dependencies and integration points
It depends on namespace common code, credentials, keyrings, sysctl, workqueues, RCU refs, and procfs sequence operations. It integrates with clone/unshare, capability checks, ID mapping, keyrings, binfmt_misc, and per-user resource enforcement.

## Risks and test signals
Risks include ID-map extent overflow, wrong parent/owner capability checks, ucount leaks, rlimit underflow/overflow, and disabled `CONFIG_USER_NS` behavior returning init namespace. Tests should cover nested namespace creation, uid/gid/projid map writes, setgroups policy, ucount limits, rlimit enforcement, and disabled-config fallbacks.
