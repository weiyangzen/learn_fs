# sources/distributed-fs/eos/mgm/proc/user/Quota.cc

Purpose: implements legacy user quota operations in `ProcCommand::UserQuota()`: listing the caller's quotas, admin listing, setting, and removing quota limits.

Important APIs and types: uses `Quota::PrintOut`, `SetQuotaTypeForId`, `RmQuotaForId`, `RmQuotaTypeForId`, `GetResponsibleSpaceQuotaPath`, `Acl::CanSetQuota`, `Mapping` user/group translation, `StringConversion` size parsing, and `gOFS->_stat`.

Control flow: optional quota space is normalized to a directory path when it exists. `lsuser` prints current user's UID and GID quota views. For other subcommands, root/admin users are authorized directly; non-admin users must pass ACL quota-admin checks on the responsible quota node. `ls` prints selected UID/GID quota entries. `set` validates space, exactly one uid/gid, parses byte and inode limits, and updates quota records. `rm` similarly validates identity and removes all or selected quota types, with an extra guard against non-local storage-node `sss` authentication.

State and persistence: `set` and `rm` mutate quota state managed by `Quota`; listing is read-only. Stats are incremented.

Dependencies and integration: quota state is linked to namespace paths, ACLs, identity mapping, and the MGM quota subsystem.

Risks: the `set` branch has an `else` attached to `if (mSubCmd == "set")`, which assigns an EPERM storage-node message for non-set subcommands before `rm` handling can run; this can leave confusing transient state. Parsing uses global `errno` after conversion helpers, so tests should reset and assert error paths. Test signals include ACL quota admin, admin override, UID/GID translation failure, volume/inode parsing, `sss` local versus remote behavior, unknown quota type, monitor format, numeric ID printing, and responsible-space resolution.
