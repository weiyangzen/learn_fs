## sources/distributed-fs/eos/mgm/bulk-request/BulkRequestFactory.hh

Purpose: declares `BulkRequestFactory`, a static factory for domain request objects. It includes stage, evict, and cancellation request headers, but only declares stage and cancellation creation methods.

Important APIs: overloads for creating stage requests with generated or explicit IDs and explicit creation time, plus `createCancelBulkRequest()`.

Integration: used by prepare-manager hooks and proc DAO reconstruction. State is absent; ownership is via `std::unique_ptr`. Risks include the included-but-not-produced `EvictBulkRequest`, which can confuse callers expecting a complete factory for all enum types. Test signals should compile-check all overloads, verify return dynamic types, and confirm ownership transfer semantics.
