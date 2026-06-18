# sources/distributed-fs/moosefs/mfsmaster/datacachemgr.h

Purpose: declares the master data-cache hint manager API. It gives client-service code a small interface to decide when session-local cached file data can be reused and when inode modifications should invalidate other sessions' cached data.

Important APIs/types/functions: `dcm_open(inode, sessionid)` returns an integer cache-ok decision and ensures the pair is represented in the LRU table. `dcm_access(inode, sessionid)` marks the pair as safe after access. `dcm_modify(inode, sessionid)` invalidates other sessions for the inode and records the modifying session. `dcm_init()` initializes static manager state.

Control flow: call order is normally initialize, open check, access mark after successful read-like use, and modify notification before or during write-like operations. The API is intentionally fire-and-forget for `access` and `modify`; only `open` returns a decision.

State/persistence: the header exposes no state and no persistence hooks. The implementation is purely in-memory, so all cache hints reset on master restart.

Dependencies/integration: only depends on fixed-width integer types. It integrates with `matoclserv.c` and the session subsystem through the `sessionid` values passed by callers.

Risks/test signals: consumers must call `dcm_modify()` on every operation that can make another client's cached file data stale; missing a call is a coherency risk. Tests should verify that all write/truncate/chunk-changing paths in client service code notify this API and that startup calls `dcm_init()` before first use.
