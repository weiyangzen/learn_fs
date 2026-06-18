<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.cpp

Purpose: Maintains in-memory sets of user/group IDs that exceed size or inode quotas.

Important APIs/functions: `updateExceededQuota` replaces one of four sets based on `QuotaDataType` and `QuotaLimitType`. `isQuotaExceeded(uid,gid)` checks size and inode sets together. The overload with `QuotaLimitType` checks only one limit family. `getExceededQuota` copies sets to a list, and `someQuotaExceeded` reports whether any set is non-empty.

Control flow/state/persistence: Public methods take `SafeRWLock` read/write guards around `rwLockExceededLists`. Updating clears and repopulates a `UIntSet` from a caller-provided `UIntList`. Checking prioritizes user matches before group matches and returns specific `QuotaExceededErrorType` values.

Dependencies/integration: Depends on quota enums from `QuotaData.h`, BeeGFS list/set aliases, and `SafeRWLock`. It feeds quota enforcement decisions in storage/session paths.

Risks/test signals: Return precedence matters when both user and group exceed limits. Tests should cover all four sets, empty inputs, duplicated IDs, concurrent readers during updates, and `someQuotaExceeded` after clear/update cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.cpp -->
