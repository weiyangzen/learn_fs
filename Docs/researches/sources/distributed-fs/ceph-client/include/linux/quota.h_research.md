# sources/distributed-fs/ceph-client/include/linux/quota.h

Purpose: defines the VFS quota core data model: quota identifier typing, in-memory quota blocks and quota-file information, dquot lifecycle state, format operations, filesystem quota operations, quotactl operation vectors, and state flags.

Important APIs and types: `enum quota_type` covers user, group, and project quotas with bit masks. `struct kqid` stores a typed kernel quota ID; helpers create, invalidate, and map IDs through user namespaces. `struct mem_dqblk`, `struct mem_dqinfo`, and `struct dquot` hold per-ID usage/limits/grace times, per-quota-file metadata, and active cached quota objects. `struct quota_format_ops`, `struct dquot_operations`, and `struct quotactl_ops` define format, dquot, and userspace control callbacks. `struct qc_dqblk`, `struct qc_info`, `struct qc_state`, and `struct qc_type_state` are filesystem-agnostic query/set payloads. `struct quota_info` is embedded in `super_block` and tracks active files, flags, formats, and locks.

Control flow: quotaon loads a format and `mem_dqinfo`; inode operations acquire or initialize relevant `dquot`s, charge/free blocks and inodes, mark dquots dirty, and write back through format ops. quotactl requests pass through `quotactl_ops` to read/set limits, state, and info. Remount and quotaoff disable, suspend, or release quota state.

State and persistence: persistent state is quota files and filesystem-specific quota metadata. In-memory state includes dquot hash/inuse/free/dirty lists, `dq_count`, flags, locks, `dq_off`, usage/reservation counters, grace times, quota statistics, and superblock quota flags.

Dependencies and integration points: depends on VFS `super_block`/inode concepts, user namespace UID/GID/projid mapping, percpu counters, quota format headers, UAPI quota constants, modules, locks, and optional netlink warnings.

Risks and test signals: risks include namespace mapping bugs, dquot lifetime races, dirty-list corruption, inconsistent reservation vs usage accounting, grace-time/warning misbehavior, project quota ID errors, and format callback mismatch. Test user/group/project quota enable/disable, remount suspend/resume, quota file formats v1/v2/XFS-facing paths, namespace mappings, delayed allocation reservation/claim/reclaim, dirty writeback, quota warnings, and concurrent inode ownership/size changes.
