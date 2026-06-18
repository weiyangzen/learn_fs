## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaNodeCore.cc

Purpose: Implements the in-memory quota accumulator for one quota node. It tracks logical bytes, physical bytes, and file counts per UID and GID, independent of QuarkDB persistence.

Important APIs and control flow: getter methods acquire shared locks and return zero for missing IDs. `addFile()` and `removeFile()` update both user and group counters under an exclusive lock. `meld()` adds every counter from another core. Assignment replaces both maps; `operator<<` partially replaces entries present in the update core; equality compares both maps. `setByUid()`, `setByGid()`, `filterByUid()`, and `filterByGid()` support targeted repair/update workflows.

State behavior: `mUserInfo` and `mGroupInfo` are `std::map`s guarded by a `std::shared_timed_mutex`. Missing entries are created on add/remove/set. Filtering builds a copy of keys before erasing, avoiding iterator invalidation.

Dependencies and integration: used by `IQuotaNode`/`QuarkQuotaNode` as the cached in-memory copy of persisted quota hash data. It has no direct backend dependency, so it is suitable for isolated unit tests.

Risks and test signals: `removeFile()` subtracts from unsigned counters without bounds checks, so duplicate removes or inconsistent repair input can underflow to huge values. `meld()`, assignment, and equality call `std::lock(mtx, other.mtx)` and then manually unlock both mutexes instead of using RAII lock guards; exceptions during map copy/add would leave locks held. Self-assignment/self-meld may also be risky with `std::lock` on the same mutex. Tests should cover missing-ID getters, add/remove balance, underflow behavior, partial update semantics, filtering, equality, and concurrent reader/writer access.
