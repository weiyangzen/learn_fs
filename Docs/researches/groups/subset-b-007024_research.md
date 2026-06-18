<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/CtaUtils.hh -->
# sources/distributed-fs/eos/mgm/CtaUtils.hh

Purpose: Declares `eos::mgm::CtaUtils`, a small utility surface used by CTA-aware MGM code, especially tape garbage-collection and WFE paths that parse CTA metadata, convert stored binary timestamps, and read bounded command output.

Important APIs/types/functions: The header defines exception types for parsing (`EmptyString`, `NonNumericChar`, `ParseError`, `ParsedValueOutOfRange`) and buffer conversion (`BufSizeMismatch`). `toUint64(std::string)` trims whitespace and parses unsigned decimal values in `CtaUtils.cc`. `divideAndRoundToNearest()` and `divideAndRoundUp()` are inline arithmetic helpers used by tape-GC rate/bin calculations. `bufToTimespec()` converts an exact-size byte buffer into a `timespec`, and `readFdIntoStr()` reads at most a caller-provided byte count from a file descriptor into a null-terminated `std::string`.

Control flow: This header is declaration-heavy; control flow is supplied by `CtaUtils.cc`. The inline division helpers are single-expression functions and assume valid nonzero divisors. The parser family signals input problems through typed exceptions rather than error codes, making callers responsible for catch/report behavior.

State and persistence behavior: `CtaUtils` is stateless and has no persistence. Its ABI-sensitive behavior is `bufToTimespec()`, because it interprets persisted or xattr-style bytes as the platform `timespec` layout.

Dependencies and integration points: It sits in the MGM namespace and includes logging, namespace, tape-GC cache/LRU headers, namespace metadata interfaces, and console protobuf headers, although the declarations themselves mostly require standard C++ and `timespec`. Call sites include `mgm/tgc/RealTapeGcMgm.cc`, `FreedBytesHistogram.cc`, `SmartSpaceStats.cc`, `AsyncUint64ShellCmd.cc`, and WFE archive-id parsing.

Risks: The inline division helpers do not guard `y == 0`. `readFdIntoStr()` uses signed `ssize_t maxStrLen`; negative values would be dangerous after unsigned conversion in the implementation, so callers must pass validated positive limits. `bufToTimespec()` is not portable across differing `timespec` layouts or endianness. Tests should cover whitespace-only parse failures, non-decimal input, max `uint64_t`, overflow, exact/mismatched timestamp buffers, file-descriptor read errors, and zero-divisor caller guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/CtaUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/EosCtaReporter.cc -->
# sources/distributed-fs/eos/mgm/EosCtaReporter.cc

Purpose: Implements RAII-style EOS-to-CTA report generation. Reporter objects collect ordered key/value fields during an operation and emit one ampersand-separated record when the reporter is destroyed.

Important APIs/types/functions: `EosCtaParamMap` maps every `EosCtaReportParam` enum to the external log key string. Static `DEFAULT_PARAMS` vectors define the base fields and per-report extensions for prepare requests, WFE events, evict commands, file deletion, and file creation. `ioStatsWrite()` sends the generated record to `gOFS->mIoStats->WriteRecord()` when I/O statistics are available. `EosCtaReporter::generateEosReportEntry()` serializes `mParams` in `std::map` order using the enum ordering, and the constructors prepopulate default fields with empty strings.

Control flow: Construction sets the writer callback, inserts base defaults, then derived constructors insert report-specific defaults. Callers add values through header-defined `addParam()` overloads. Destruction in the base class triggers `generateEosReportEntry()` if the object is still active; the move constructor transfers parameters/callback and disables the moved-from instance. The generated string is built as `key=value&key=value...` and sent through the callback.

State and persistence behavior: State is per-object only: `mParams`, `mWriterCallback`, and `mActive`. There is no durable storage in this file; persistence is delegated to `Iostat::WriteRecord()` or to a caller-supplied callback such as PrepareManager's log bridge.

Dependencies and integration points: The implementation depends on `mgm/ofs/XrdMgmOfs.hh` for global `gOFS`, `mgm/iostat/Iostat.hh`, and `mgm/EosCtaReporter.hh`. WFE code creates WFE/file creation/deletion reporters, admin evict creates evict reporters, and bulk prepare manager uses `EosCtaReporterPrepareReq` with an explicit writer callback.

Risks: Values are not URL-escaped, so `&`, `=`, or newlines in paths/errors can corrupt downstream parsing unless producers sanitize them. `EosCtaParamMap.at()` throws if a new enum is added without a map entry. Destructor-triggered logging can throw through a destructor if the callback or map lookup fails, which is risky during stack unwinding. The static vectors are mutable globals rather than `const`. Test signals should include deterministic field ordering, moved reporter single-emission behavior, null `mIoStats`, callback capture behavior, and fields containing delimiter characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/EosCtaReporter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/EosCtaReporter.hh -->
# sources/distributed-fs/eos/mgm/EosCtaReporter.hh

Purpose: Defines the public reporting API used by MGM CTA workflows to emit structured audit/report records for prepare, WFE, evict, file deletion, and file creation events.

Important APIs/types/functions: `EosCtaReportParam` is the authoritative enum of supported report fields; comments state that parameter order follows enum order and that `SEC_APP` should remain last by convention. `EosCtaReporter` is the protected base class with chainable `addParam()` overloads for numeric/string/bool/C-string values. Derived reporter types are `EosCtaReporterPrepareReq`, `EosCtaReporterPrepareWfe`, `EosCtaReporterEvict`, `EosCtaReporterFileDeletion`, and `EosCtaReporterFileCreation`.

Control flow: Users instantiate a concrete reporter, call `addParam()` as the operation progresses, and rely on the virtual destructor to emit the record. Copying and assignment are disabled; moving is allowed only through the protected move constructor so containers can transfer reporters without double-emitting. Derived constructors are responsible for adding their default parameter sets.

State and persistence behavior: The report is accumulated in `std::map<EosCtaReportParam, std::string> mParams`, which gives stable enum-ordered serialization. The writer callback abstracts persistence, defaulting to the implementation's I/O-stat writer. The object lifecycle itself is the transaction boundary: destruction means "finalize and write".

Dependencies and integration points: This header depends only on standard containers/callbacks and `mgm/Namespace.hh`, so CTA-aware managers can include it cheaply. It is integrated by `bulk-request/prepare/manager`, WFE archive workflows, and admin evict command code.

Risks: Destructor side effects make reporting easy to forget in tests and hard to suppress on exceptional paths. `std::to_string()` in the templated overload excludes types that need custom formatting and can surprise for char-like values. No API validates that required fields were filled before emission. Since ordering and external key names are split between this header and the `.cc` map, enum additions require coordinated updates. Good tests should assert per-derived default coverage, bool formatting, move semantics in STL containers, and behavior when a caller omits fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/EosCtaReporter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Caps.cc -->
# sources/distributed-fs/eos/mgm/FuseServer/Caps.cc

Purpose: Implements the MGM FUSE capability registry and the broadcast fan-out logic that keeps eosxd clients' metadata/dentry state coherent after namespace mutations.

Important APIs/types/functions: `Store()` records an incoming `eos::fusex::cap` and indexes it by auth id, inode, client id, and client UUID. `Imply()` derives a new cap from an existing auth id for another inode/auth id and assigns a lease time from the owning client heartbeat. `Get()`, `GetBroadcastCapsTS()`, and `Delete()` provide lookup, filtered broadcast audience selection, and inode-wide cap removal. Broadcast methods call `Clients` methods: `BroadcastRefresh*()` sends refreshes, `BroadcastDeletion*()` sends dentry deletion notices, `BroadcastMD()` sends metadata updates, and `BroadcastCap()` sends a cap update.

Control flow: Storage is mutex-protected and updates all secondary indexes together. Broadcasts first snapshot relevant auth ids under lock, release the cap lock, then fetch/send per target to avoid holding the cap mutex during ZeroMQ replies. Suppression logic uses `Clients::BroadCastMaxAudience()` and a configured regex to skip matching client IDs when the audience is too large. `Print()` provides time, inode, or path-oriented diagnostic dumps, resolving paths through EOS namespace services for `option == "p"`.

State and persistence behavior: State is in-memory only: `mCaps`, `mTimeOrderedCap`, `mClientCaps`, `mClientInoCaps`, `mInodeCaps`, and `mClientIds`. Expiry removes stale lease caps based on `vtime`; `dropCaps()` removes all caps for a client UUID after eviction/unmount. No state survives MGM restart, which is why new clients are told to drop all caps on first heartbeat.

Dependencies and integration points: Depends on `gOFS`, `gOFS->zMQ->gFuseServer.Client()`, MGM stats/timing/logging, EOS namespace view services, and `eos::fusex` protobuf messages. `FuseServer/Server.cc` calls broadcasts after create/link/rename/unlink/metadata updates, and `XrdMgmOfs.cc` calls external refresh/MD broadcasts for non-FUSE mutations.

Risks: `Imply()` indexes the implied cap in `mClientInoCaps` under the source cap inode instead of `md_ino`, which may make per-client inode queries/removal inconsistent. `Store()` adds a new time-order entry for replaced caps without removing old time entries, relying on later cleanup. Several diagnostic paths read `mInodeCaps` without taking `mtx` for the whole iteration in non-`t` print modes. Regex compilation/fan-out happens on hot paths. Tests should exercise cap replacement, implied cap removal, audience suppression, self/same-client suppression, client eviction cleanup, and concurrent broadcast/delete races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Caps.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Caps.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Caps.hh

Purpose: Declares `FuseServer::Caps`, the in-memory authority for FUSE client capabilities, lease expiry, and recipient selection for metadata/dentry broadcasts.

Important APIs/types/functions: Nested `capx` wraps an `eos::fusex::cap` protobuf plus the issuing `VirtualIdentity`. Type aliases define auth IDs, client IDs, UUID maps, inode-to-auth sets, and client-to-inode views. Public methods include `Store()`, `Imply()`, `Remove()/RemoveTS()`, `Delete()`, `Get()/GetTS()/GetRaw()`, broadcast methods, `Print()`, `Dump()`, and query helpers such as `HasInodeId()` and `GetInodeCapAuthIds()`.

Control flow: The class uses a single `std::mutex mtx` to protect all maps. Thread-safe wrappers (`GetTS`, `RemoveTS`) acquire the mutex; lower-level methods assume the caller already holds the lock. `expire()` checks the oldest time-ordered entry and removes it when its cap lease has expired; otherwise it signals whether stale time entries should be popped. `dropCaps()` gathers matching caps for a UUID, removes them, then clears client-id views for that UUID.

State and persistence behavior: All capability state is volatile. The primary map is `authid -> shared_cap`; secondary views are maintained for client and inode operations. `mTimeOrderedCap` is a multimap of lease time to auth id used by periodic expiry. Client UUID to client-id tracking supports multi-mount cleanup.

Dependencies and integration points: Includes `mgm/fusex.pb.h`, `common/Mapping.hh`, `common/Timing.hh`, logging, and `common/RWMutex.hh`. It is owned by `FuseServer`, called by the FUSE server command processor, heartbeat client monitor, and external MGM operations that need to invalidate eosxd caches.

Risks: Correctness depends on every mutation keeping all secondary indexes synchronized. Some accessors expose non-const references to internal maps, which can bypass locking and invariants. `Remove()` assumes the cap is present in all secondary maps and uses `operator[]`, potentially creating empty entries during cleanup. `Get()` returns a default empty cap by default, so callers must check `id()` to distinguish misses. Test signals should validate invariant preservation across store, imply, remove, delete, drop-by-UUID, and expiry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Caps.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Clients.cc -->
# sources/distributed-fs/eos/mgm/FuseServer/Clients.cc

Purpose: Implements eosxd client tracking, heartbeat processing, client eviction, runtime statistics reporting, and ZeroMQ response messages sent from MGM back to FUSE clients.

Important APIs/types/functions: `ClientStats()` summarizes active/locked clients. `MonitorHeartBeat()` is the background lifecycle loop. `Dispatch()` stores heartbeats, processes client log/trace payloads, registers UUID mappings, handles first-mount configuration, and revokes requested auth caps. `Print()` and `Info()` render operator diagnostics. Message methods include `Evict()`, `DeleteEntry()`, `RefreshEntry()`, `SendMD()`, `SendCAP()`, `BroadcastConfig()`, and `BroadcastDropAllCaps()`. `HandleStatistics()` updates per-client performance counters, and `DeferClient()` implements dotted-version comparison.

Control flow: Heartbeats are accepted under a write lock unless they are older than the offline window. First-seen clients get a drop-all-caps response and a config response advertising heartbeat rate and feature flags. The monitor loop runs once per second, classifies clients as online, volatile, offline, or evicted based on heartbeat age/shutdown/protocol version, drops locks on offline transition, drops caps and removes map entries on eviction, expires flush records, and records MGM stats. Message-sending functions serialize `eos::fusex::response` protobufs and reply through `gOFS->zMQ->mTask`.

State and persistence behavior: State is volatile in `mMap` (`identity -> Client`) and `mUUIDView` (`uuid -> identity`). Heartbeat windows, heartbeat interval, quota interval, broadcast audience limit, and suppress regex are in-memory settings. Client logs/traces are forwarded to `mFusexLogTraces` and `mFusexStackTraces`; statistics are retained only in the client object.

Dependencies and integration points: Depends on `gOFS`, MGM stats, ZeroMQ task replies, `Locks`, `Caps`, and `Flush`. `Caps.cc` calls the message methods to fan out cache invalidations; admin fusex/evict commands call print/evict paths; `Server.cc` heartbeat handling calls `Dispatch()` and statistics handling.

Risks: `mMaxBroadCastAudience`, suppress-match string, and `terminate_` are not visibly initialized in the constructor. `Print()` uses a five-second `blockedms` threshold while the comment says five minutes. `SetHeartbeatInterval()` holds the write lock while calling `BroadcastConfig()`, which performs network replies. Version comparison collapses dotted components into base-1000 numbers and returns false if component counts differ. Tests should cover delayed heartbeat rejection, first mount setup, auth revocation, shutdown/offline/eviction transitions, protocol mismatch eviction, refresh suppression for protocol/version, and static/autofs eviction filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Clients.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Clients.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Clients.hh

Purpose: Declares `FuseServer::Clients`, the thread-safe registry of connected eosxd clients and the outbound control-message API used by MGM FUSE services.

Important APIs/types/functions: `Clients` inherits `eos::common::RWMutex` and embeds a nested `Client` class containing `heartbeat`, `statistics`, operation timestamp, and atomic status (`PENDING`, `EVICTED`, `OFFLINE`, `VOLATILE`, `ONLINE`). Main APIs include heartbeat `Dispatch()`, `MonitorHeartBeat()`, `ClientStats()`, diagnostics `Print()/Info()`, statistics ingestion, eviction, FUSE cache-message senders, interval setters, broadcast audience settings, and `client2app()`.

Control flow: Callers take read/write locks through the object itself. Inline helpers such as `nclients()` and `client2app()` lock internally. Message APIs are implemented in `Clients.cc` and generally look up UUID-to-identity, serialize a protobuf response, and send it over the ZeroMQ task channel.

State and persistence behavior: `mMap` stores live client identities and their heartbeat/statistics snapshots; `mUUIDView` maps stable client UUIDs to current ZeroMQ identities. Timing windows govern state transitions and eviction. No persistent registry exists; clients repopulate the map via heartbeats after reconnect/restart.

Dependencies and integration points: Includes `Caps.hh`, `mgm/fusex.pb.h`, timing and logging. It is accessed globally through `gOFS->zMQ->gFuseServer.Client()` by capability broadcasting, lock reporting, flush expiry, FUSE server request handlers, and admin commands.

Risks: The header exposes mutable `map()` and `uuidview()` references, so callers can mutate state outside documented lock discipline. The constructor initializes heartbeat/quota windows but not all private scalar fields. `Client` has an unused `mLockPidMap` member while real locking is handled by `FuseServer::Lock`. Tests should verify lock discipline around public helpers, client status transitions, UUID remapping, and default configuration values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Clients.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Flush.cc -->
# sources/distributed-fs/eos/mgm/FuseServer/Flush.cc

Purpose: Implements a short-lived in-memory tracker for FUSE file flush operations so conflicting server-side operations can detect and briefly wait for active client flushes.

Important APIs/types/functions: `beginFlush(id, client)` registers a flush by inode/client. `endFlush(id, client)` decrements the reference count and removes the entry when the final matching flush ends. `hasFlush(id)` polls `validateFlush()` with exponential backoff for up to about 255 ms. `validateFlush(id)` removes expired client entries for one inode and reports whether any unexpired flush remains. `expireFlush()` globally removes expired entries, and `Print()` renders diagnostics.

Control flow: Every mutating or map-inspecting operation uses `XrdSysMutexHelper` on the `Flush` object. `beginFlush()` constructs a `flush_info_t` with expiry `now + cFlushWindow` and calls `Add()`. `hasFlush()` checks under lock, sleeps 1/2/4/.../128 ms while a flush remains, and returns true only if the flush persists through all attempts. `MonitorHeartBeat()` calls `expireFlush()` once per heartbeat loop tick.

State and persistence behavior: `flushmap` is volatile: `inode -> client UUID/string -> flush_info_t`. Each entry carries a client, expiry time, and reference count. Expiry is time-based and independent of client eviction, although heartbeat expiry keeps the map bounded.

Dependencies and integration points: Depends on `common/Timing`, logging, XRootD mutex helpers, and global MGM headers. FUSE server request handling calls begin/end around flush processing, and `XrdMgmOfsFile.cc` checks `hasFlush()` before close-path operations that might race a client flush.

Risks: `endFlush()` uses `flushmap[id][client]`, so an unmatched end creates a default entry and decrements `nref` below zero before erasing. `flush_info_t::Add()` ignores the passed client's name and increments from the default reference count, making first registration `nref == 1` but requiring strict begin/end pairing. `Print()` reports `GetAgeInNs()` directly, which may be negative for still-valid future expiries depending on timing semantics. Tests should cover nested begin/end, unmatched end, expiry, concurrent has/end behavior, and the 255 ms wait contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Flush.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Flush.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Flush.hh

Purpose: Declares `FuseServer::Flush`, a mutex-protected map of currently flushing FUSE clients keyed by inode and client, with a fixed 60-second validity window.

Important APIs/types/functions: `cFlushWindow` is 60 seconds. Public methods are `beginFlush()`, `endFlush()`, `hasFlush()`, `validateFlush()`, `expireFlush()`, and `Print()`. Private `flush_info_t` stores the client string, expiry `timespec`, and reference count and provides `Add()`/`Remove()` helpers.

Control flow: The implementation uses `XrdSysMutex` inheritance and locks the whole map per operation. Entries are created with an expiry in the future, incremented on repeated begins, decremented on ends, and removed either when references reach zero or when the expiry passes.

State and persistence behavior: `flushmap` is process-local and nonpersistent. It is a coordination hint rather than a durable write journal; after MGM restart, flush awareness is lost and clients must recover through normal protocol behavior.

Dependencies and integration points: Includes `mgm/Namespace.hh`, timing/logging, `map`, and XRootD pthread mutex wrappers. It is exposed through `gFuseServer.Flushs()` and used by FUSE server flush handling, heartbeat maintenance, and file close/open conflict paths.

Risks: The API accepts raw `std::string client` by value and does not encode ownership semantics beyond string equality. `validateFlush()` is public but assumes callers understand it mutates state by expiring entries. Tests should verify fixed-window behavior with controlled time, reference counts, cleanup after last client, and that diagnostics do not require external locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Flush.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/FusexCastBatch.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/FusexCastBatch.hh

Purpose: Provides a tiny RAII batch for deferred FUSE broadcast callbacks, allowing code to register invalidation/update work and execute it at scope exit if not executed manually.

Important APIs/types/functions: `FusexCastBatch` stores `std::function<void()>` callbacks in `std::list`. `Register()` appends a callback, `Execute()` runs all callbacks in insertion order and clears the list, `GetSize()` returns pending callback count, and the destructor calls `Execute()` when callbacks remain. Copy and move operations are deleted.

Control flow: Callers create a batch, register lambdas while performing namespace or ACL/commit work, then either call `Execute()` explicitly or let the destructor execute the remaining callbacks. `Execute()` performs synchronous callback invocation on the caller's thread.

State and persistence behavior: State is only the pending callback list. There is no durable storage and no retry; once callbacks run or the process exits, state is gone.

Dependencies and integration points: Includes `mgm/Namespace.hh`, `<functional>`, and `<list>`. It is included by `XrdMgmOfs.hh/.cc`, `ofs/fsctl/CommitHelper.cc`, and user ACL command code. Commit helper registers broadcasts after successful filesystem changes so FUSE clients see the resulting metadata state.

Risks: Callbacks running from a destructor can throw during stack unwinding unless callers ensure lambdas are nonthrowing. The class is not thread-safe. Deleted move operations prevent returning or storing batches in many abstractions. Capturing references in delayed lambdas is risky if scope/lifetime assumptions change. Tests should cover manual execute clearing, destructor execution exactly once, callback order, and exception behavior policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/FusexCastBatch.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Locks.cc -->
# sources/distributed-fs/eos/mgm/FuseServer/Locks.cc

Purpose: Implements the FUSE lock registry wrapper that maps inodes to `LockTracker` instances and provides cleanup/listing operations by PID or client owner.

Important APIs/types/functions: `getLocks(id)` lazily creates and returns the shared `LockTracker` for an inode. `purgeLocks()` removes trackers whose `inuse()` is false. `dropLocks(id, pid)` removes locks for a process on one inode. `dropLocks(owner)` removes all locks owned by a client UUID/string across all inodes. `lsLocks(owner, rlocks, wlocks)` gathers read/write PID sets for diagnostics.

Control flow: Each method uses `XrdSysMutexHelper` to protect `lockmap`. Drop methods mutate trackers under lock, release the lock, then call `purgeLocks()` to clean empty trackers. Listing iterates every inode tracker and merges owner-specific read/write locks into caller-provided maps.

State and persistence behavior: `lockmap` is volatile and process-local: `inode -> shared LockTracker`. Lock state is not persisted; it is tied to live eosxd client sessions and is dropped during offline/eviction paths in `Clients.cc`.

Dependencies and integration points: Depends on `mgm/fuse-locks/LockTracker.hh`, XRootD mutex helpers, and MGM logging. `Clients::MonitorHeartBeat()` drops all locks for offline/evicted UUIDs, admin `Fusex` commands can drop inode/PID locks, and `Clients::Print("k")` lists locks per client.

Risks: `getLocks()` returns a shared tracker after releasing the wrapper lock, so correctness depends on `LockTracker`'s own synchronization and lifetime behavior. `lsLocks()` creates empty entries in output maps even when no locks exist for an inode. `dropLocks(owner)` always returns 0 even if no locks matched. Tests should cover lazy creation, purge after last lock removal, owner-wide eviction cleanup, concurrent get/drop, and diagnostics for clients with no locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Locks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Locks.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Locks.hh

Purpose: Declares `FuseServer::Lock`, the mutex-protected inode-to-lock-tracker map used by FUSE server code to coordinate POSIX-style locks held by eosxd clients.

Important APIs/types/functions: `shared_locktracker` aliases `std::shared_ptr<LockTracker>`, and `lockmap_t` maps inode IDs to trackers. Public APIs are `getLocks()`, `purgeLocks()`, two overloads of `dropLocks()`, and `lsLocks()`.

Control flow: The implementation lazily materializes trackers and performs coarse locking around map operations. Actual read/write lock ownership details are delegated to `LockTracker`, while this wrapper handles object lookup and lifecycle.

State and persistence behavior: `lockmap` is in-memory only and should reflect live client/session state. Empty trackers are purged after removals to keep memory bounded.

Dependencies and integration points: Includes `mgm/Namespace.hh`, `mgm/fuse-locks/LockTracker.hh`, `<map>`, `<memory>`, and XRootD mutex wrappers. It is exposed through the FUSE server singleton and used by heartbeat eviction, admin lock drop commands, and client diagnostics.

Risks: The class privately inherits `XrdSysMutex`, which makes lock ownership implicit. Returning shared trackers allows work outside the map mutex; tests must depend on `LockTracker` behavior as well as this wrapper. Test signals include tracker reuse for the same inode, independent trackers for different inodes, purge behavior, owner-wide drop, and list output separation between read/write lock maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Locks.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Namespace.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Namespace.hh

Purpose: Defines the namespace macros used by the MGM FUSE server headers/implementations so classes such as `FuseServer::Caps`, `Clients`, `Flush`, and `Lock` live under `eos::mgm`.

Important APIs/types/functions: `USE_EOSMGMNAMESPACE` expands to `using namespace eos::mgm;`. `EOSMGMNAMESPACE_BEGIN` opens `namespace eos { namespace mgm {`, and `EOSMGMNAMESPACE_END` closes it. Despite the path under `FuseServer`, this header defines the generic MGM namespace macros, not a distinct FUSE subnamespace.

Control flow: There is no runtime control flow. It is a preprocessor include with an include guard.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Included throughout MGM and FUSE server code to avoid spelling namespace blocks manually. The listed FUSE headers use `EOSFUSESERVERNAMESPACE_BEGIN`, which is resolved through namespace macro definitions elsewhere in the MGM include chain; this local header is the base MGM namespace helper.

Risks: Namespace macros hide the actual namespace structure from tools and can be confusing when combined with similarly named FUSE-server macros. `USE_EOSMGMNAMESPACE` introduces a broad using directive and should be avoided in headers that may leak it to consumers. Tests are compile-time only: include-order checks and namespace qualification builds are the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Namespace.hh -->
