# subset-b-007037 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/iostat/Iostat.cc -->
# sources/distributed-fs/eos/mgm/iostat/Iostat.cc

Purpose: implements EOS MGM IO statistics collection, time-window aggregation, QDB or legacy-file persistence, report ingestion, report file rotation, UDP broadcast, namespace popularity accounting, and text/monitoring output formatting. The file is split between `IostatPeriods`, which owns one 24-hour circular timeline, and `Iostat`, which owns global/user/group/domain/application accounting and the receiver/circulator threads.

Important APIs and functions: `IostatPeriods::Add`, `StampBufferZero`, `GetDataInPeriod`, `UpdateTransferSampleInfo`, and `GetLastSampleUpdateTimestamp` distribute finished transfers over one-second bins and derive 5-minute sample metrics such as time to 90/95/99/100 percent completion, longest transfer, report latency, average transfer size, and transfer count. `Iostat::Init` chooses QDB versus legacy persistence, runs one-off migration, loads persisted counters, and starts the circulation thread. `ApplyConfig`, `StoreIostatConfig`, `Start/StopCollection`, `Start/StopPopularity`, `Start/StopReport`, and `Start/StopReportNamespace` bind instance configuration to runtime toggles. `Receive` consumes `/eos/*/report` QDB messages, parses them through `eos::common::Report`, updates counters, broadcasts UDP reports, records domain/app/popularity data, and optionally appends reports to daily or namespace files. `WriteRecord` writes plain daily `.eosreport` files or zstd-rotated `.eosreport.zst` segments controlled by `EOS_ZSTD_REPORTS`, `EOS_ZSTD_REPORTS_ROTATION`, and `EOS_ZSTD_REPORTS_LEVEL`. `PrintOut`, `PrintNsPopularity`, and `PrintNsReport` render operator/monitoring views. `EncodeKey`, `DecodeKey`, `LoadFromQdb`, `FlushCache`, `LegacyStoreInFile`, and `LegacyRestoreFromFile` implement persistence mechanics.

Control flow: initialization builds `mHashKeyBase` and the metadata flusher path from the MGM instance, uses QDB for QuarkDB namespace deployments, or forces legacy file mode for in-memory namespace deployments. The receiver waits for initialization, listens to QDB report messages, normalizes escaped ampersands, then sequentially calls `Add` for read/write byte counts, call counts, seek counts, disk times, and deletion counters. `Add` first updates the QDB cache when applicable and then updates in-memory sparse maps under `mDataMutex`. Domain and application byte accounting use separate `IostatPeriods` maps; popularity uses a seven-day array of sparse hash maps keyed by every parent subpath. The circulation thread wakes roughly twice per second, periodically stores legacy counters, zeroes stale time bins for all period maps, and clears the popularity day bucket when the modulo day bin changes.

State and persistence: runtime state includes total maps (`IostatTag`, `IostatUid`, `IostatGid`), period maps for tags/uids/gids/domain/app data, a QDB update cache, UDP target sockets, and popularity maps. QDB persistence stores annual hashes keyed as `eos-iostat:<instance>:<year>` with fields like `idt=u&id=1000&tag=bytes_read`; writes are batched through `HINCRBYMULTI` via `MetadataFlusher` when the cache reaches 3000 entries or 30 seconds. Legacy mode writes `tag=...&uid=...&val=...` and `tag=...&gid=...&val=...` lines to a temp file then renames it. A one-time migration imports an old legacy file into QDB and renames the file to `.bkp`. Report persistence is independent from counter persistence and writes under `gOFS->IoReportStorePath`.

Dependencies and integration points: depends on `XrdOucEnv`, EOS common table formatting, report parsing, path utilities, timing, string conversion, QDB client/hash/listener/flusher APIs, `FsView` global config, `gOFS`, master-state checks, namespace services, `Prefetcher`, `FileSystem` hotfile stats, UDP/XRootD networking, and zstd. External writers call `WriteRecord` from MGM OFS paths, CTA reporting, bulk request integration, and drop handling. Operator commands use `proc/admin/IoCmd.cc`, and configuration is surfaced through `IConfigEngine` and `FsView`.

Risks: `IostatPeriods::Add` computes `mbins = tdiff / sBinWidth`; with the current one-second bin width, very short or boundary-invalid reports are mostly guarded, but any future bin-width change needs the commented partial-bin logic and a zero-bin audit. Several persistence helpers use static local state shared across instances (`GetHashKey`, `ShouldFlushCache`, `FlushCache`, and `WriteRecord`), so multi-instance tests need care. `AddUdpTarget` inserts the target before DNS resolution, and on resolution failure can leave a target without socket/address entries, which `UdpBroadCast::at` would not tolerate. `DecodeKey` does not require all fields to be present before returning true. Report JSON and text are built manually, so embedded quotes/newlines from report fields can break consumers. Legacy restore and migration parse with fixed-size token scanning, so malformed long lines are skipped or truncated. The receiver only flushes QDB cache opportunistically during `Add`; low traffic can delay persistence until the time threshold is checked by a later report.

Test signals: existing `unit_tests/mgm/IostatTests.cc` covers config keys, start/stop toggles, store/apply config, UDP target add/remove, period bin accounting, and sequential transfer samples. Useful additional coverage would include QDB key encode/decode malformed cases, cache flush threshold/time behavior, year rollover, zstd rotation fallback, UDP DNS failure cleanup, namespace report path creation, popularity bin rollover, and `Receive` behavior for future stop times, stale reports, replication paths, and readv byte accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/iostat/Iostat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/iostat/Iostat.hh -->
# sources/distributed-fs/eos/mgm/iostat/Iostat.hh

Purpose: declares the MGM IO statistics subsystem and the 24-hour period accumulator used by it. This header is the public contract for starting/stopping collection, report persistence, popularity tracking, UDP targets, output rendering, and direct counter updates.

Important APIs and types: `Period` and `PercentComplete` name reporting periods and transfer-completion percentiles. `IostatPeriods` exposes `Add`, `StampBufferZero`, `GetDataInPeriod`, transfer sample getters, total-sum getter, and sample timestamp formatting. Its private state is a one-second, 86400-bin circular data buffer plus a 5-minute transfer integral buffer and counters for average size, transfer count, longest transfer, and report delay. `Iostat` exposes static config keys, lifecycle methods (`Init`, collection/popularity/report toggles), `ApplyConfig`/`StoreIostatConfig`, report receiver/circulator thread functions, UDP target management, `WriteRecord`, `PrintOut`, `PrintNsPopularity`, `PrintNsReport`, and `Add`. Private helpers cover QDB persistence, UDP broadcast, popularity updates, migration, key encoding/decoding, legacy storage, and cache flushing.

Control flow and state model: callers initialize one `Iostat` through `Init`, apply persisted `FsView` config, then use assisted threads for receiving and circulating. `Add` feeds both durable totals and time-window period objects. The header makes locking expectations explicit for aggregate readers: `GetTotalStatForTag` and `GetPeriodStatForTag` require `mDataMutex` protection by their callers or are used internally while already locked. `mThreadSyncMutex` serializes lifecycle changes; `mDataMutex`, `mBcastMutex`, and `mPopularityMutex` protect the three major mutable domains.

State and persistence behavior: the class can persist counters either in QuarkDB hashes through `qclient::QClient`/`MetadataFlusher` or in a legacy local file. Annual hash keys are based on `mHashKeyBase`; pending increments are stored in `mMapCacheUpdates`. UDP targets are runtime sockets plus persisted config strings. Popularity is in memory only and rotates over seven day buckets. The static `gOpenReportFD` supports the legacy report-file writer.

Dependencies and integration points: includes EOS assisted threads, logging identity, string conversion, `FsView`, namespace globals, QuarkDB client/hash structures, sparse hash maps, POSIX socket types, and forward declarations for `MetadataFlusher` and `eos::common::Report`. Integration is through `XrdMgmOfs::mIoStats`, admin IO commands, report producers, and unit tests that enable `IN_TEST_HARNESS` to inspect internals.

Risks and test signals: the header exposes a broad stateful class with many atomics and mutexes; API misuse risk is mostly around calling output/stat helpers without appropriate locking or changing lifecycle flags while threads are active. `IostatPeriods` assumes `sBinWidth == 1` in comments and implementation. Test signals are the `IostatTests.cc` harness plus compile-time checks for `IN_TEST_HARNESS`; tests should assert that private constants, cache sizes, and enum-to-index assumptions remain aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/iostat/Iostat.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/lru/LRU.cc -->
# sources/distributed-fs/eos/mgm/lru/LRU.cc

Purpose: implements the MGM LRU policy worker. It scans namespace directories carrying `sys.lru.*` extended attributes and applies four policy families: empty-directory age expiry, filename/age/size file expiry, quota-watermark cache expiry, and age/size-triggered file layout conversion.

Important APIs and functions: `Start` and `Stop` manage the assisted background thread. `getOptions` reads `space default` config members `lru` and `lru.interval`, validates the interval, and disables the worker on malformed configuration. `extractTimeSizeCriterias`, `parseExpireMatchPolicy`, and `parseExpireSizeMatchPolicy` parse policy expressions such as `*:1d`, `*.root:1mo`, or `*:1d:<1G`. `performCycleQDB` uses `NamespaceExplorer` to fetch all directories and linked attributes from QuarkDB. `backgroundThread` waits for namespace boot and master role, then cycles with a minimum five-second interval and refresh support. `processDirectory` dispatches per-directory xattrs to `AgeExpireEmpty`, `SizeAgeExpire`, `CacheExpire`, and `ConvertMatch`.

Control flow: QDB scans populate attributes only for directories and ignore files. Each directory is skipped if it is root or under the proc path. Empty-directory expiry stats the directory and removes it when child count is zero and creation time plus policy age is older than now. Size/age expiry prefetches children, locks each file metadata record only long enough to read name, ctime, and size, matches it against parsed `PolicyRule`s, collects deletion paths, then removes outside the metadata scan. Watermark expiry refreshes project quota, validates low/high percentages, finds enough oldest files to drop current logical bytes below the low watermark, and deletes from oldest to newest. Conversion policy validates a matching `sys.conversion.<pattern>` attribute, skips files already in the target layout or outside size criteria, builds conversion tags, and schedules jobs with `ConverterEngine`.

State and persistence behavior: the worker has little durable state of its own. Runtime state is the QDB client, assisted thread, root virtual identity, error object, and refresh flag. Durable policy state lives in namespace xattrs (`sys.lru.expire.empty`, `sys.lru.expire.match`, `sys.lru.lowwatermark`, `sys.lru.highwatermark`, `sys.lru.convert.match`, `sys.conversion.*`, and space-forcing attrs), while actual effects are namespace mutations or converter jobs. Watermark state is derived from namespace quota accounting via `Quota`.

Dependencies and integration points: depends on `gOFS`, master election, `FsView`, QuarkDB namespace exploration, namespace metadata/prefetch APIs, `FileMapIterator`, metadata locks, root MGM OFS operations (`_stat`, `_rem`, `_remdir`, `_find`), quota statistics, conversion tag/engine code, EOS string parsing, regex wrapper, and layout identifiers. Admin space commands validate or refresh `lru.interval`; unit tests in `unit_tests/mgm/LRUTests.cc` cover policy parsing.

Risks: destructive actions run as root identity, so parser mistakes or overly broad patterns can remove or convert many files. `extractTimeSizeCriterias` relies on `errno` after size parsing and should be checked for stale `errno` behavior. `parseExpireSizeMatchPolicy` uses a map for one policy entry, so duplicate pattern keys in a single entry are not meaningful. Size policy semantics are strict greater-than and less-than, despite comments saying equal-or-more. `CacheExpire` uses `ctime` as LRU ordering and `st_blocks * st_blksize` as size, which may differ from logical size. The background thread only checks termination every thousand directories during exploration, so very large scans can be slow to stop between checkpoints. Conversion parses layout IDs from the raw conversion string even when it can contain an env representation, so target-layout comparison can be imprecise in that mode.

Test signals: existing `LRUTests.cc` validates classic match parsing, time/size extraction, valid multi-policy parsing, and malformed policy rejection. Additional integration tests should exercise directory skipping, proc-tree protection, empty directory age boundaries, strict size comparisons, wildcard `*` versus regex `.*`, quota watermark deletion ordering, malformed low/high watermark values, conversion attribute absence, conversion space precedence, master/slave transitions, and refresh behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/lru/LRU.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/lru/LRU.hh -->
# sources/distributed-fs/eos/mgm/lru/LRU.hh

Purpose: declares the MGM LRU engine, policy parser data structures, public controls, and the private background scan interface. It is the contract used by MGM configuration/admin code and by unit tests for parser behavior.

Important APIs and types: `LRU::Options` carries `enabled` and scan `interval`. `PolicyRule` captures a filename regex, required age, optional signed size condition, and fixed `now` timestamp; it provides `nameMatches`, `ageMatches`, `sizeMatches`, `getSizeCriteria`, and `matches`. `PolicyRules` is a vector of rules. Static parser helpers are `extractTimeSizeCriterias`, `parseExpireMatchPolicy`, and `parseExpireSizeMatchPolicy`. Public methods include `getOptions`, `getLRUIntervalConfig`, `Start`, `Stop`, `AgeExpireEmpty`, `SizeAgeExpire`, `CacheExpire`, `ConvertMatch`, and `RefreshOptions`. `lru_entry_t` is a sortable path/ctime/size tuple for watermark expiry.

Control flow and state model: callers construct `LRU`, call `Start`, and can request option reload by setting `mRefresh` through `RefreshOptions`. The private background path is `backgroundThread`, which calls `performCycleQDB`; every discovered directory is passed to `processDirectory`. `PolicyRule` freezes `m_now` at parse time so every file in one policy application uses a consistent age cutoff.

State and persistence behavior: the header stores only runtime scanning state: `mQcl`, `mThread`, root virtual identity, XRootD error info, and an atomic refresh flag. Persistent behavior is indirect through namespace xattrs and file deletion/conversion effects.

Dependencies and integration points: includes assisted threads, mapping, regex wrapper, namespace interfaces, XRootD error info, `qclient::QClient`, and EOS virtual identity. `gLRUPolicyPrefix` names the policy xattr wildcard used by namespace scanning/configuration.

Risks and test signals: `PolicyRule::sizeMatches` treats positive sizes as `fileSize > limit` and negative sizes as `fileSize < limit`; callers expecting inclusive comparisons should test boundary files. `nameMatches("*")` is a special compatibility case outside the regex wrapper. Unit tests already cover parser helpers and equality; additional tests should cover `PolicyRule::matches` against boundary ctime and size values and `RefreshOptions` interaction with the running thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/lru/LRU.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/macros/Macros.cc -->
# sources/distributed-fs/eos/mgm/macros/Macros.cc

Purpose: provides function equivalents for selected MGM OFS macros: namespace path mapping and proc-request access checks. These functions make macro behavior reusable from non-OFS command paths such as HTTP/WebDAV and proc command implementations.

Important APIs and functions: `NamespaceMap(std::string& path, const char* ininfo, const VirtualIdentity& vid)` unescapes or curl-decodes a path, honors token path replacement for `/zteos64:`, applies `gOFS->PathRemap` unless `eos.prefix` is present, rejects CR/LF for non-root users by clearing the path, and applies `eos.prefix=` or `eos.lfn=` opaque overrides outside `/proc/`. `ProcBounceIllegalNames` converts an empty mapped path into `EILSEQ` and an operator-facing error string. `ProcBounceNotAllowed` checks `Access` allow lists under `Access::gAccessMutex` and rejects unauthorized user/group/host/domain identities with `EACCES`.

Control flow: proc and WebDAV callers first map the path, then call bounce helpers. The access helper allows uid 0-3 unless other conditions require checking, then verifies allowed users, groups, hosts, and user-at-domain. A separate domain check rejects when allowed domains are configured, `-` is not present, and the caller domain is not listed.

State and persistence behavior: no local persistent state. Behavior depends on global `gOFS`, path remap configuration, token contents, and static access allow-list sets. It mutates only the input path and output error/errno fields.

Dependencies and integration points: depends on `mgm/macros/Macros.hh`, `mgm/access/Access.hh`, `XrdOucEnv`, `VirtualIdentity`, `StringConversion`, and global `XrdMgmOfs`. Callers include `mgm/http/webdav/PropFindResponse.cc`, `mgm/proc/IProcCommand.cc`, and `mgm/proc/user/RmCmd.cc`.

Risks and test signals: `NamespaceMap` assumes `gOFS` is valid for `PathRemap`; unlike the macro, the function body does not guard every use. CR/LF rejection is represented as an empty path, so an originally empty path and an illegal path are indistinguishable to `ProcBounceIllegalNames`. Opaque parsing trusts `XrdOucEnv` values and should be tested for unusual `eos.prefix` and `eos.lfn` combinations. There is no direct unit-test hit in the observed sweep; tests should cover token remap, encoded paths, prefix/lfn precedence, `/proc/` exclusion, CR/LF rejection for root versus non-root, and allow-list combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/macros/Macros.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/macros/Macros.hh -->
# sources/distributed-fs/eos/mgm/macros/Macros.hh

Purpose: defines the legacy macro layer used by many XRootD MGM OFS entrypoints for access mode tagging, request stalling, redirect handling, namespace path mapping, token scope assignment, illegal-name rejection, and allow-list authorization. It also declares function forms for namespace/proc helpers implemented in `Macros.cc`.

Important APIs and macros: access mode macros define `__AccessMode__` for read, write, and master-read paths. `WAIT_BOOT` blocks until namespace boot. `MAYSTALL`, `FUNCTIONMAYSTALL`, and `RECURSIVE_STALL` consult `gOFS->ShouldStall`, register requests in `mTracker`, and either return a stall/error or continue. `MAYREDIRECT` routes operations to a master or path route with retry detection; `MAYREDIRECT_ENOENT`, `MAYREDIRECT_ENONET`, and `MAYREDIRECT_ENETUNREACH` handle error-specific redirects. `MAYSTALL_ENOENT`, `MAYSTALL_ENONET`, and `MAYSTALL_ENETUNREACH` are error-specific stalls. `NAMESPACEMAP` performs in-place path decoding, token path replacement, path remap, CR/LF validation, and opaque prefix/LFN handling. Token scope macros assign authorization scopes. `BOUNCE_ILLEGAL_NAMES`, `PROC_BOUNCE_ILLEGAL_NAMES`, `REQUIRE_SSS_OR_LOCAL_AUTH`, `BOUNCE_NOT_ALLOWED`, and `PROC_BOUNCE_NOT_ALLOWED` enforce access checks and update `MgmStats` on denial.

Control flow: OFS methods typically declare an access mode, execute namespace mapping, set token scope, optionally bounce illegal names or unauthorized users, then check stall and redirect rules before doing the actual filesystem operation. Most macros return from the enclosing function, so they encode both policy and control transfer.

State and persistence behavior: no standalone persistence, but macros interact with global mutable state: `gOFS`, `gOFS->IsStall`, `gOFS->IsRedirect`, `gOFS->mTracker`, `Access` allow lists, `MgmStats`, routing/stall configuration, token contents, and path remap configuration.

Dependencies and integration points: includes MGM stats and OFS headers and relies on XRootD types (`XrdOucString`, `XrdOucEnv`, `XrdCl::URL`) through included headers. It is deeply integrated across the MGM OFS command surface, while the declared functions are used by proc and WebDAV paths.

Risks and test signals: macro side effects are implicit and depend on variable names such as `vid`, `error`, `inpath`, `ininfo`, `path`, `epname`, and `retc`. Return-from-macro behavior makes cleanup ordering easy to miss. Request tracking in `MAYSTALL` occurs before stall decisions and can itself trigger a client stall. The macro and function forms should stay behaviorally aligned; drift can create different path validation between OFS and proc/WebDAV paths. Tests should compile representative call sites, exercise denial stats, retry detection, token scope assignment, and all redirect/stall branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/macros/Macros.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/misc/AuditHelpers.hh -->
# sources/distributed-fs/eos/mgm/misc/AuditHelpers.hh

Purpose: header-only helpers for converting EOS namespace metadata objects into `eos::audit::Stat` protobuf messages used by MGM audit logging.

Important APIs and functions: `auditutil::buildStatFromFileMD` fills ctime/mtime seconds, optional nanosecond string fields, owner uid/gid, permission mode in numeric and octal string forms, optional size, and optional checksum for an `IFileMD`. `auditutil::buildStatFromContainerMD` does the same for an `IContainerMD` except size and checksum are not applicable. Both functions are null-safe and return immediately when the shared pointer is empty.

Control flow: callers pass metadata already obtained from namespace services. The helpers read ctime/mtime into `IFileMD::ctime_t` structures, format `<sec>.<nsec>` strings with `snprintf` when requested, mask modes with `07777`, and set protobuf fields. File checksum formatting delegates to `eos::appendChecksumOnStringAsHex`.

State and persistence behavior: no state or persistence. The output protobuf becomes part of audit event records elsewhere; these helpers only copy current metadata snapshots.

Dependencies and integration points: depends on `proto/Audit.pb.h`, file/container metadata interfaces, checksum utilities, and C stdio formatting. Callers include `XrdMgmOfsFile.cc`, Fuse server operations, `Commit.cc`, and chmod/chown command handlers.

Risks and test signals: callers must ensure metadata lifetime and locking are appropriate before invoking these helpers; the helpers do not lock metadata internally. `%ld` formatting assumes time values fit long on the build platform. Mode formatting buffer is fixed at eight bytes but adequate for `0%04o`. Checksum inclusion can be more expensive and should be requested only where needed. Tests should verify null handling, namespace timestamp formatting, mode masking, checksum opt-in, and file/container field differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/misc/AuditHelpers.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/misc/Constants.hh -->
# sources/distributed-fs/eos/mgm/misc/Constants.hh

Purpose: centralizes string constants for MGM extended attributes and policy keys so callers avoid repeated allocations and typo-prone string literals.

Important APIs and constants: atomic/injection attributes include `EOS_ATOMIC` and `EOS_INJECTION`. System namespace attributes include hard-link metadata, owner authorization, versioning, alternative checksums, forced atomicity, ENOENT redirect, forced size/stall/space/group/layout/checksum/blocksize/blockchecksum/stripe settings. User attributes mirror versioning and forced layout/checksum/blocksize/blockchecksum/stripe controls plus `user.stall.unavailable` and `user.tag`. Policy keys include bandwidth, IO priority, IO type, and schedule.

Control flow and state behavior: this header has no functions. Consumers perform map lookups or assignments against `static const std::string` objects. The comment explains the current choice: `std::string` helps existing `map.find` call sites avoid temporary construction until transparent lookup or string-view migration is available.

Dependencies and integration points: depends only on `<string>`. Integration points include MGM policy resolution in `mgm/policy/Policy.cc`, attribute helpers in `mgm/utils/AttrHelper.cc`, LRU conversion space selection, and unit tests in `unit_tests/mgm/utils/AttrHelperTests.cc`.

Risks and test signals: `static const std::string` in a header creates one internal-linkage object per translation unit, which is acceptable for read-only constants but can complicate address identity assumptions. Tests should focus on consumer behavior: forced atomic precedence, system versus user forced policy resolution, and exact key spelling for externally visible xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/misc/Constants.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/misc/IdTrackerWithValidity.hh -->
# sources/distributed-fs/eos/mgm/misc/IdTrackerWithValidity.hh

Purpose: template utility for tracking IDs temporarily claimed by MGM subsystems such as balancing, conversion, draining, and fsck. It prevents duplicate work on the same entry across tracker types while automatically expiring claims after a validity period.

Important APIs and types: `TrackerType` enumerates `None`, `All`, `Balance`, `Convert`, `Drain`, and `Fsck`. `IdTrackerWithValidity<EntryT>` is constructed with cleanup interval, default entry validity, and optional fake clock. Public methods are `AddEntry`, `HasEntry`, `RemoveEntry`, `DoCleanup`, `Clear`, `GetClock`, `TrackerTypeToString`, `StringToTrackerType`, and `PrintStats`. Internally it stores `std::map<TrackerType, std::map<EntryT, time_point>>` under a mutex.

Control flow: `AddEntry` rejects invalid aggregate tracker types (`None` and `All`), scans all tracker maps to enforce global uniqueness, then records an expiry timestamp using either caller-supplied validity or the default. `DoCleanup` runs only after `mCleanupTimestamp` passes, advances the next cleanup timestamp, and removes expired entries for all trackers or one selected tracker. `RemoveEntry` erases the first matching entry from any tracker. `PrintStats` emits either human or monitoring-style lines and can include the full tracked ID list.

State and persistence behavior: all state is in memory and intentionally temporary. The optional `SteadyClock` wrapper supports deterministic unit tests. Clearing `TrackerType::All` removes every tracker map; clearing a specific tracker leaves other subsystem claims intact.

Dependencies and integration points: depends on EOS namespace macros, `common/SteadyClock`, mutexes, and maps. The global MGM file-id tracker is stored on `XrdMgmOfs` as `mFidTracker` and used by balancer, converter, drain, stripes, admin space commands, and admin namespace tracker reporting.

Risks and test signals: cleanup is gated by one global cleanup timestamp, so calling `DoCleanup` for one tracker can postpone cleanup for other trackers until the next interval. `PrintStats(full=true)` assumes `EntryT` is streamable. `AddEntry` scans all maps, so very large tracker sets have linear cross-tracker insertion cost. Tests in `unit_tests/mgm/IdTrackerTests.cc` cover basic add, fake-clock cleanup, custom validity, removal, and clear behavior. Additional tests should cover cross-tracker duplicate rejection, tracker string conversion for unknown values, monitor formatting, and cleanup interaction across different tracker types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/misc/IdTrackerWithValidity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/CachedCollectable.cc -->
# sources/distributed-fs/eos/mgm/monitoring/CachedCollectable.cc

Purpose: implements a Prometheus `Collectable` wrapper that caches metric families for a configurable TTL and shields scrapes from expensive collection or collection exceptions.

Important APIs and functions: the constructor stores an inner `std::shared_ptr<prometheus::Collectable>` and TTL. `CacheIsFresh` returns true when cached metrics exist, TTL is positive, and the cache age is less than TTL. `Collect` returns empty for a null inner collectable, bypasses caching for non-positive TTL, returns fresh cached metrics under `mCacheMutex`, serializes refreshes with `mRefreshMutex`, returns stale cached data while another thread refreshes when possible, catches all exceptions from the inner collectable, and updates cache state after successful collection.

Control flow: fast path checks cache freshness under the cache mutex. If stale, a thread tries to acquire the refresh mutex without blocking; losing threads return stale metrics if any exist, otherwise wait for the refresh lock. After acquiring refresh responsibility, the code rechecks freshness to avoid duplicate refreshes. The actual inner `Collect` runs outside `mCacheMutex`, so cached readers are not blocked by the expensive collection except for refresh serialization.

State and persistence behavior: state is in-memory only: cached metric families, cache timestamp, and a flag indicating whether a cache has ever been populated. Exceptions preserve the last successful cache; without a cache, exceptions yield an empty vector.

Dependencies and integration points: depends on `prometheus::Collectable` and `prometheus::MetricFamily`. `PrometheusExporter.cc` wraps its registry/collectable in `CachedCollectable` using `monitoring.prometheus.cache_ttl_seconds`. Logging alias setup maps `CachedCollectable` under the Monitoring fanout.

Risks and test signals: returned vectors are copied, which is safe but can be costly for large metric sets. A TTL of zero intentionally disables caching. Catch-all exception handling prevents scrape failures but can hide repeated collection bugs unless logs are emitted by the inner collectable. Tests should simulate concurrent scrapes, null collectable, zero TTL, stale fallback while another thread refreshes, exception after a successful cache, and exception before any cache exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/CachedCollectable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/CachedCollectable.hh -->
# sources/distributed-fs/eos/mgm/monitoring/CachedCollectable.hh

Purpose: declares the cached Prometheus collectable wrapper used by MGM monitoring to limit scrape-time work.

Important APIs and types: `CachedCollectable` derives from `prometheus::Collectable`, accepts an inner collectable and TTL in its constructor, and overrides `Collect`. Private `CacheIsFresh` centralizes TTL validation. State includes the wrapped collectable, TTL, a cache mutex, a refresh mutex, cache-existence flag, timestamp, and cached metric families.

Control flow and state behavior: the two-lock design separates short cache reads from long refresh ownership. Members are mutable because Prometheus collection is a logically const API but cache refresh mutates internal state. No persistent state is involved.

Dependencies and integration points: includes Prometheus C++ client headers, chrono, memory, mutex, and vector. Used by `PrometheusExporter.cc` when building the MGM metrics endpoint.

Risks and test signals: because `Collect` is const and internally synchronized, tests should treat it as thread-safe under concurrent Prometheus scrapes. The TTL unit is milliseconds in the wrapper even though configuration is seconds elsewhere, so integration tests should verify conversion at the exporter boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/CachedCollectable.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/Monitoring.cc -->
# sources/distributed-fs/eos/mgm/monitoring/Monitoring.cc

Purpose: centralizes logging helpers for the MGM Prometheus endpoint lifecycle and monitoring configuration errors.

Important APIs and functions: `LogPrometheusEndpointStarting`, `LogPrometheusEndpointStarted`, `LogPrometheusEndpointStopped`, `LogPrometheusEndpointStartFailed`, and `LogMonitoringConfigError` emit structured EOS log lines with bind address, cache TTL, and error text as applicable.

Control flow and state behavior: there is no local state. Callers invoke these helpers around endpoint start/stop/configuration paths. Success paths log at notice level; start/config failures log at error level.

Dependencies and integration points: depends on `Monitoring.hh` and `common/Logging.hh`. The functions are intended for `PrometheusExporter` or MGM configuration code to keep log messages consistent.

Risks and test signals: errors are interpolated into structured log strings, so callers should pass already-sanitized single-line messages if log parsers are sensitive. Tests can assert that endpoint lifecycle paths call the right helper by using logging test sinks or integration logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/Monitoring.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/Monitoring.hh -->
# sources/distributed-fs/eos/mgm/monitoring/Monitoring.hh

Purpose: declares monitoring log helper functions for the MGM Prometheus endpoint.

Important APIs: the header exposes start, started, stopped, start-failed, and configuration-error logging functions in `eos::mgm::monitoring`. Start/start-failed functions carry bind address; start/started also include cache TTL seconds.

Control flow and state behavior: this is a pure declaration header with no state. It gives monitoring code a stable logging API while keeping `common/Logging.hh` out of consumers that only need declarations.

Dependencies and integration points: depends on fixed-width integer and string headers. Implemented by `Monitoring.cc` and used by monitoring endpoint setup code.

Risks and test signals: API stability matters because these helper names encode endpoint lifecycle events. Tests should focus on implementation logging format and ensuring configuration/start failures route to the error helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/Monitoring.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/MonitoringConfig.hh -->
# sources/distributed-fs/eos/mgm/monitoring/MonitoringConfig.hh

Purpose: defines configuration keys, defaults, bounds, and parsing helpers for the MGM Prometheus monitoring endpoint.

Important APIs and constants: keys are `monitoring.prometheus.enabled`, `monitoring.prometheus.port`, and `monitoring.prometheus.cache_ttl_seconds`. Defaults are port `9987`, cache TTL `1` second, and maximum cache TTL `60` seconds. `ParseUint32Config` parses a non-empty unsigned 64-bit string and rejects values above `uint32_t` max. `ParsePortConfig` parses a non-zero `uint16_t` port through `ParseUint32Config`. `IsValidCacheTtl` accepts TTL values up to the configured maximum.

Control flow and state behavior: this is header-only parsing logic with no state. Callers read string config values, parse them into numeric types, validate TTL, and apply defaults outside the helper when parsing fails or config is absent.

Dependencies and integration points: depends on `common/ParseUtils.hh`, integer limits, and strings. Used by MGM monitoring configuration and `PrometheusExporter` setup; `CachedCollectable` consumes the resulting TTL after conversion to chrono duration.

Risks and test signals: empty values are invalid rather than defaulted inside the parser, so callers must implement default behavior consistently. The port parser rejects zero and values above 65535. TTL validation only checks the upper bound, so zero is valid and later disables caching when converted to the collectable TTL. Tests should cover empty strings, non-numeric strings, max uint32 boundaries, port 0, port 65535/65536, TTL 0, TTL 60, and TTL 61.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/monitoring/MonitoringConfig.hh -->
