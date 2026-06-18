## sources/distributed-fs/eos/namespace/interface/INamespaceStats.hh

Purpose: Defines a minimal stats sink used by namespace operations to report counters and execution timings to MGM statistics infrastructure.

Important APIs and types: `Add(tag, uid, gid, val)` increments a tagged user/group value, and `AddExec(tag, exectime)` records execution time.

Control flow: namespace code calls stats methods around operations; concrete MGM stats implementation handles aggregation.

State and persistence: interface has no state; concrete implementations may maintain runtime counters or export metrics.

Dependencies and integration: depends on namespace macros and sys uid/gid types. Comment states it mirrors MGM `Stat` API.

Risks: no ownership, thread-safety, or failure semantics are expressed; implementers must be safe for namespace call patterns.

Test signals: mock stats capture for namespace operations and concurrency tests for real stats implementation.
