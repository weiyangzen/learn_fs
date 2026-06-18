# sources/distributed-fs/lizardfs/src/tools/quota_set.cc

Purpose: Implements `lizardfs setquota`, setting soft and hard limits for a user, group, or directory.

Important APIs/types/functions: `quota_set_run`; static `quota_set`; `QuotaOwner`; `QuotaEntry`; `cltoma::fuseSetQuota`; `matocl::fuseSetQuota`; `my_get_number`.

Control flow: Parses exactly one owner mode (`-u`, `-g`, or `-d`), four numeric limits, and a directory path. For directory quotas it replaces owner id with the target inode; for user/group quotas it verifies the path is the mount root. It builds four quota entries for soft/hard inodes and size, sends the request, and expects OK status.

State and persistence: Mutates master quota state. No local persistence.

Dependencies and integration: Uses typed quota protocol, `ServerConnection`, master quota types, and shared master connection logic.

Risks and test signals: Unit parsing and owner selection must be exact because the command changes limits. The command trusts master response status after typed deserialization. No direct tests in this subset.
