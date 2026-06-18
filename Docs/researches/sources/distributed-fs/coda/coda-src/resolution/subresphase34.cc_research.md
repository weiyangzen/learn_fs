# sources/distributed-fs/coda/coda-src/resolution/subresphase34.cc

Purpose: subordinate phase 3.5/34 handler that receives the coordinator's consolidated inconsistency list and ensures local replicas contain corresponding inconsistent objects or parent marks before final version-vector installation.

Important functions: `RS_HandleInc` parses an RPC2 bounded byte stream into an `ilink` list, loads required objects with `GetPhase2Objects`, creates missing phase-2 objects with `CreateResPhase2Objects`, calls `ProcessIncList`, then spools a `ResolveNULL_OP` record and returns updated status. `ProcessIncList` marks each listed object inconsistent when it exists under the expected parent, marks both actual and expected parents when parentage diverges, or marks the expected parent when the object cannot be found/created.

Control flow and persistence: this phase only runs when the inconsistency list is nonempty. It may allocate new placeholder objects, set inconsistency bits with `MarkObjInc`, and append a resolution log record to the resolved directory. Objects are returned with `PutObjects`, passing block accounting and commit semantics.

Dependencies, risks, tests: depends on `resutil` inconsistency serialization, vnode lists, `SpoolVMLogRecord`, and normal volume/vnode locking. ENOSPC while spooling the null record is explicitly ignored, which can reduce auditability. Test with object present in expected parent, object moved, missing child requiring parent mark, missing object creation, ENOSPC spooling, and returned `ViceStatus.Length` used by phase 4.
