# sources/distributed-fs/ceph/src/osd/ECTransaction.h

Purpose: `ECTransaction.h` declares the optimized EC transaction-generation interface and helper classes that turn a planned PG transaction into shard-level ObjectStore transactions.

Important APIs and types: `WritePlanObj` captures the per-object plan: optional reads, writes, original/projected size, cache invalidation, and PDW flag. `WritePlan` contains ordered plans and whether reads are needed. `Generate` is the per-object executor with private phases for delete/init/truncate/write/attrs/OMAP. `OmapCloneVisitor` extracts EC OMAP modifications from PG log mod_desc entries and applies them to clone transactions. Free functions cover OMAP accumulation/application and top-level `generate_transactions`.

Control flow: callers first build `WritePlanObj` instances, perform any required reads, then call `generate_transactions` with partial read extents, log entries, output maps, transactions, and journal/log context.

State and persistence: the header defines the data that bridges planning and durable write generation. It references persistent PG log entries, per-shard transactions, ObjectContext cache state, and the in-memory `ECOmapJournal`.

Dependencies and integration: includes `ECUtil.h`, `PGTransaction.h`, `ECOmapJournal.h`, `PGLog`, `OSDMap`, erasure-code interfaces, and ObjectStore transactions. It is optimized EC only, not the legacy hinfo path.

Risks: `Generate` stores many references, so lifetimes must outlive construction. The ordered plan contract is enforced by assertions in the implementation. OMAP helpers require encoded `OmapUpdateType` payloads to match decode expectations.

Test signals: header API is indirectly tested through optimized ECBackend transaction tests. Focus should be on plan ordering, no-read write plans, PDW flags, OMAP clone visitor accumulation, and `generate_transactions` output maps.
