<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Flush.cc -->
# sources/distributed-fs/eos/mgm/FuseServer/Flush.cc

Purpose: Implements a short-lived in-memory tracker for FUSE file flush operations so conflicting server-side operations can detect and briefly wait for active client flushes.

Important APIs/types/functions: `beginFlush(id, client)` registers a flush by inode/client. `endFlush(id, client)` decrements the reference count and removes the entry when the final matching flush ends. `hasFlush(id)` polls `validateFlush()` with exponential backoff for up to about 255 ms. `validateFlush(id)` removes expired client entries for one inode and reports whether any unexpired flush remains. `expireFlush()` globally removes expired entries, and `Print()` renders diagnostics.

Control flow: Every mutating or map-inspecting operation uses `XrdSysMutexHelper` on the `Flush` object. `beginFlush()` constructs a `flush_info_t` with expiry `now + cFlushWindow` and calls `Add()`. `hasFlush()` checks under lock, sleeps 1/2/4/.../128 ms while a flush remains, and returns true only if the flush persists through all attempts. `MonitorHeartBeat()` calls `expireFlush()` once per heartbeat loop tick.

State and persistence behavior: `flushmap` is volatile: `inode -> client UUID/string -> flush_info_t`. Each entry carries a client, expiry time, and reference count. Expiry is time-based and independent of client eviction, although heartbeat expiry keeps the map bounded.

Dependencies and integration points: Depends on `common/Timing`, logging, XRootD mutex helpers, and global MGM headers. FUSE server request handling calls begin/end around flush processing, and `XrdMgmOfsFile.cc` checks `hasFlush()` before close-path operations that might race a client flush.

Risks: `endFlush()` uses `flushmap[id][client]`, so an unmatched end creates a default entry and decrements `nref` below zero before erasing. `flush_info_t::Add()` ignores the passed client's name and increments from the default reference count, making first registration `nref == 1` but requiring strict begin/end pairing. `Print()` reports `GetAgeInNs()` directly, which may be negative for still-valid future expiries depending on timing semantics. Tests should cover nested begin/end, unmatched end, expiry, concurrent has/end behavior, and the 255 ms wait contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Flush.cc -->
