## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaNodeCore.hh

Purpose: Declares `QuotaNodeCore`, the synchronized data model for per-quota-node user/group usage accounting. It is the common state object that QuarkDB quota nodes cache and expose through the quota interfaces.

Important APIs and types: `UsageInfo` contains `space`, `physicalSpace`, and `files`, with additive and equality operators. Public methods expose per-user/per-group logical space, physical space, and file count; mutators add/remove files; bulk operations meld, assign, partially update, set selected IDs, and filter to selected IDs. `getUids()` and `getGids()` expose keys present in the maps.

State and access: the header defines `mUserInfo` and `mGroupInfo` as private maps protected by mutable `std::shared_timed_mutex`. It grants friendship to quota abstractions and `QuarkQuotaNode`, allowing persistence code to read/write maps directly.

Dependencies and integration: depends on EOS namespace types and POSIX UID/GID identifiers. Its role is intentionally backend-agnostic; `QuotaStats.cc` translates this state to QuarkDB hash fields.

Risks and test signals: the friend access bypasses the public locking API in callers such as backend import/replacement, so tests should include thread-safety assumptions around `QuarkQuotaNode`. The default `UsageInfo` zero initialization is a useful invariant. Validate that `operator<<` means "replace only entries present in update", not a full merge or clear.
