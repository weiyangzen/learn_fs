# sources/distributed-fs/ceph-client/fs/quota/netlink.c

Purpose: Implements the generic netlink notification path for quota warnings so kernel quota enforcement can notify userspace listeners about exceeded or recovered limits.

Important APIs, types, and functions: Defines genl family `VFS_DQUOT`, multicast group `events`, and exports `quota_send_warning()`. The warning payload carries quota type, exceeded id, warning code, device major/minor, and the current uid that caused the warning.

Control flow: `quota_send_warning()` allocates a `sk_buff` with `GFP_NOFS`, builds a generic netlink message with a monotonic atomic sequence, appends attributes with `nla_put_*`, finalizes with `genlmsg_end()`, and multicasts. Attribute build failures free the skb and log errors. `quota_init()` registers the family at `fs_initcall`.

State and persistence: State is limited to the registered genl family and a static sequence counter. Messages are transient and not persisted.

Dependencies and integration points: Called by `flush_warnings()` in `dquot.c` and can be used by filesystems that do not use generic dquot. Depends on generic netlink, quota id mapping, current credentials, and device number helpers.

Risks and test signals: Risks include allocation failure in filesystem write paths, malformed attribute sizes, and userspace ABI regressions. Test by triggering block and inode soft/hard warnings, listening on the `VFS_DQUOT` `events` group, validating id/dev attributes, and injecting allocation or attribute failures.
