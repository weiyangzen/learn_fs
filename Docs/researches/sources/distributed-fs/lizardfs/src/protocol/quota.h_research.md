# sources/distributed-fs/lizardfs/src/protocol/quota.h

Purpose: Defines serializable quota owner, key, and entry types used in client-master quota APIs.

Important APIs/types/functions: Enums `QuotaRigor` (`kSoft`, `kHard`, `kUsed`), `QuotaResource` (`kInodes`, `kSize`), `QuotaOwnerType` (`kUser`, `kGroup`, `kInode`); classes `QuotaOwner`, `QuotaEntryKey`, `QuotaEntry`.

Control flow: No explicit control flow beyond generated serialization. The nested structure encodes owner, rigor, resource, and limit.

State and persistence: Represents quota state in request/response packets. Master-side quota persistence lives elsewhere.

Dependencies and integration: Used by `matocl::fuseGetQuota`, `cltoma::fuseSetQuota`, and tools `quota_rep.cc`/`quota_set.cc`. Depends on serialization macros.

Risks and test signals: Enum ordering is significant because tools index tables by enum cast. Wire compatibility and quota table interpretation can break if enum values change. No direct serialization tests in this subset.
