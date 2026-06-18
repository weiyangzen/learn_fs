# subset-b-009566

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/file_cache_test.go -->
# sources/user-network-fs/blobfuse2/component/file_cache/file_cache_test.go

Purpose: integration-style unit suite for the `file_cache` component using a loopback storage backend plus selected gomock backends. It verifies cache configuration, local cache/storage coherency, file and directory operations, eviction timing, refresh behavior, size limits, lazy write, and concurrency safety around uploads.

Important APIs/types/functions: `fileCacheTestSuite` owns `FileCache`, loopback component, cache path, fake storage path, and current config. Helpers `newLoopbackFS`, `newTestFileCache`, `setupTestHelper`, `cleanupTest`, `randomString`, `setupMockFileCacheForFlush`, `createLocalDirectoryStructure`, and `createRemoteDirectoryStructure` establish isolated cache/storage roots and mock-backed cache instances. Tests exercise `CreateDir`, `DeleteDir`, `ReadDir`, `StreamDir`, `IsDirEmpty`, `RenameDir`, `CreateFile`, `OpenFile`, `ReleaseFile`, `ReadFile`, `ReadInBuffer`, `WriteFile`, `FlushFile`, `SyncFile`, `DeleteFile`, `GetAttr`, `RenameFile`, `TruncateFile`, `Chmod`, `Chown`, `StatFs`, and `FileUsed`.

Control flow: `SetupTest` installs a silent logger, creates random home-directory cache and storage paths, removes leftovers, loads YAML config, configures loopback and file-cache components, and starts both. Many tests tear down the default setup and restart with custom config to check timeouts, empty-file creation, cleanup-on-start, hard-limit, refresh, lazy-write, symlinked cache path, and mount-path conflict settings. Operation tests create data through either loopback storage or file cache, then assert file presence, content, attributes, dirty flags, and errors in both local and backing trees. Several eviction-sensitive tests poll `os.Stat` or sleep because policy deletion is asynchronous.

State and persistence behavior: tests validate that cache files are persisted under `cache_path`, backing objects under `fake_storage_path`, and handle dirty state controls when data is uploaded. `create-empty-file=false` leaves new empty files local and dirty until flush/release, supporting immutable storage semantics. `timeout-sec=0` causes invalidated files to be purged quickly; positive timeouts retain closed files until policy cleanup. `refresh-sec` preserves cached data until stale, then redownloads. `hard-limit` rejects downloads/writes/truncates that would exceed configured cache capacity. Permission, owner, and group mutations are checked against both local and fake storage paths where supported.

Dependencies/integration points: depends on Blobfuse internal component interfaces, loopback component, global config reader, logging, handlemap, common locks, gomock `internal.MockComponent`, `testify/suite`, filesystem syscalls, `df` shell command for default cache sizing, and the LRU cache policy. The test suite uses actual local files and directories rather than pure mocks for most behavior, so it integrates path normalization, locking, local file descriptors, and backend copy operations.

Risks: tests rely heavily on sleeps and polling around asynchronous eviction, which can be flaky on slow systems. Temporary directories live under the user's home directory and cleanup mistakes can leave state. Global config is overwritten repeatedly; helper code restores config for mock cache tests, but concurrent test execution would be unsafe. Some assertions permit either `err == nil` or `os.IsExist(err)`, which hides certain filesystem error distinctions. A comment notes `ReadDir` on a missing directory returns no error, which may be a semantic gap. The large 100 MB `GetAttr` case and `df` shell use can be expensive or environment-sensitive.

Test signals: coverage is broad for file-cache behavior: config defaults/validation, negative cache size, default disk-size-derived cache size, directory listing merge rules, cache-only/storage-only/mixed attributes, bad file descriptors, flush/upload serialization, release/flush/sync races, rename cleanup with and without timeout, chmod/chown/truncate in cached and uncached states, symlinked cache paths, lazy write background upload, statfs propagation, refresh invalidation, hard size limits, recursive empty-directory detection, and cleanup after failed downloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/file_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/lru_policy.go -->
# sources/user-network-fs/blobfuse2/component/file_cache/lru_policy.go

Purpose: implements the file-cache LRU eviction policy used by Blobfuse file cache. It tracks cached file names in an in-memory doubly linked list, validates recent use, purges explicit invalidations, and periodically evicts stale or over-threshold cache entries from disk.

Important APIs/types/functions: `lruNode` stores list links, usage count, deleted flag, and cached name. `lruPolicy` embeds `sync.Mutex`, `sync.WaitGroup`, `cachePolicyConfig`, `sync.Map nodeMap`, sentinel marker nodes, deletion/validation/close channels, timer channels, and `duPresent`. Public policy methods are `NewLRUPolicy`, `StartPolicy`, `ShutdownPolicy`, `UpdateConfig`, `CacheValid`, `CacheInvalidate`, `CachePurge`, `IsCached`, and `Name`. Internal workers and helpers are `asyncCacheValid`, `cacheValidate`, `clearCache`, `removeNode`, `updateMarker`, `deleteExpiredNodes`, `deleteItem`, and `printNodes`.

Control flow: `StartPolicy` initializes marker nodes as a linked list, creates buffered delete and validation channels, probes `common.GetUsage` to decide whether disk usage checks can run, starts a minute disk monitor when `du` is available, starts a timeout ticker only when `cacheTimeout != 0`, and launches `clearCache` plus `asyncCacheValid`. `CacheValid` synchronously inserts a missing node or queues an existing node for asynchronous promotion. `cacheValidate` stores or loads a node, clears `deleted`, moves it to the list head, and increments usage. `CacheInvalidate` purges immediately when timeout is zero or when the item is already absent from `nodeMap`; otherwise it lets marker-based timeout eviction remove stale nodes later. `CachePurge` removes the node and queues disk deletion.

State and persistence behavior: policy state is in-memory only: node map, linked list, marker positions, and goroutine channels are rebuilt on start. Actual persistence effect is deletion of local cached files from `tmpPath` via `deleteFile` in `deleteItem`. The marker algorithm distinguishes files used since the last timeout interval from older files: `updateMarker` moves the trailing marker to the head and swaps current/last markers; `deleteExpiredNodes` removes nodes after `lastMarker` up to `maxEviction`. Disk-pressure eviction also uses the same expired-node path and retries up to three cleanup cycles until usage drops below `lowThreshold`.

Dependencies/integration points: depends on `cachePolicyConfig` for tmp path, cache timeout, thresholds, max eviction, tracing, and `fileLocks`; `common.GetUsage` and `getUsagePercentage` for disk monitoring; `deleteFile` for local removal; logging; and `common.LockMap` semantics to avoid deleting files under download or open use. It is called by the file-cache component on open/use, close/invalidate, purge, and component shutdown.

Risks: `time.Tick` tickers cannot be stopped, so policy restart can leak ticker resources. `ShutdownPolicy` sends on unbuffered close channels; if a worker is blocked in a receive on another active channel it should eventually select, but shutdown depends on goroutine scheduling. `CacheValid` writes to buffered channels and can block under extreme validation pressure. `removeNode` assumes `p.head` is non-nil when removing the head. `deleteItem` trims `tmpPath` from `name`, so callers must be consistent about whether policy names are cache paths or object paths. Directory cleanup is explicitly TODO and only file deletion is attempted.

Test signals: `lru_policy_test.go` directly verifies defaults, mutable config fields, cache validation insertion and usage increment, immediate invalidation when timeout is zero, retained node when timeout is positive, purge, `IsCached`, timeout eviction, and max-eviction behavior. Broader file-cache tests validate policy behavior through open/release/rename/cache cleanup scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/lru_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/lru_policy_test.go -->
# sources/user-network-fs/blobfuse2/component/file_cache/lru_policy_test.go

Purpose: focused suite for the `lruPolicy` implementation, isolating policy state transitions from the full file-cache component.

Important APIs/types/functions: `lruPolicyTestSuite` stores a `*lruPolicy` and assertions. `SetupTest` creates a fixed `cache_path` under the home directory and starts a policy with timeout zero, default eviction count, thresholds, and a fresh `common.LockMap`. `setupTestHelper` starts a new policy for supplied `cachePolicyConfig`; `cleanupTest` shuts it down and removes the cache path. Test methods cover default values, `UpdateConfig`, `CacheValid`, `CacheInvalidate`, `CachePurge`, `IsCached`, timeout cleanup, and eviction count scenarios.

Control flow: tests construct a policy, invoke policy methods directly, and inspect `nodeMap` entries or `IsCached` results. Positive-timeout tests stop the default policy, restart with `cacheTimeout=1`, call `CacheValid`/`CacheInvalidate`, sleep five seconds, and expect expired entries to become uncached. The max-eviction tests add many names and rely on repeated timeout processing to remove all entries.

State and persistence behavior: most assertions inspect in-memory state (`nodeMap`, `lruNode.name`, `usage`, and cache timeout fields). `TestCacheInvalidate` creates a local file so the asynchronous delete path has a real target. Cleanup removes the shared cache directory after shutting down policy goroutines. The suite validates that `UpdateConfig` changes size/threshold/eviction/trace fields but intentionally does not change `cacheTimeout`.

Dependencies/integration points: depends on `common.LockMap`, filesystem directory creation/removal, `testify/suite`, the LRU policy implementation, default constants from file-cache configuration, and real time through `time.Sleep`.

Risks: the suite uses a fixed home-directory path (`file_cache`) rather than a randomized temp directory, so parallel runs or stale state can collide. Timeout tests sleep fixed five-second windows and can be flaky or slow. Max-eviction tests only assert eventual absence through `IsCached`; they do not inspect physical file deletion, disk-threshold eviction, lock-protected deletion, or marker list structure.

Test signals: confirms the primary public contract: default LRU identity/config, config update exclusions, valid entries become cached, zero timeout invalidates immediately, positive timeout retains until ticker expiry, purge removes map entries, cache lookup reflects map state, and large batches expire within the configured timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/lru_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/extension_handler.h -->
# sources/user-network-fs/blobfuse2/component/libfuse/extension_handler.h

Purpose: C helper for optional dynamically loaded libfuse extensions. It loads an extension shared library, validates its exported callbacks and signature, initializes it, and exchanges FUSE callback tables between Blobfuse and the extension.

Important APIs/types/functions: global `extHandle`, typedefs `callback_exchanger`, `lib_validator`, and `lib_initializer`, globals `ext_fuse_regsiter_func` and `ext_storage_regsiter_func`, and static functions `load_library`, `unload_library`, `get_extension_callbacks`, and `register_callback_to_extension`. The expected extension symbols are `register_fuse_callbacks`, `register_storage_callbacks`, `validate_signature`, and `init_extension`.

Control flow: `load_library` calls `dlopen(extension_path, RTLD_LAZY)`, resolves the four required symbols with `dlsym`, validates all are present, performs a version-dependent handshake (`__FUSE2__` uses fuse2 call signs, otherwise fuse3 call signs), then calls `init_extension("config.txt")`. Error codes distinguish open failure, missing symbols, invalid signature, and init failure. `get_extension_callbacks` asks the extension to populate the operations table that libfuse will use. `register_callback_to_extension` passes Blobfuse's storage callback table into the extension. `unload_library` closes the handle if present.

State and persistence behavior: state is process-global in static C variables. Loaded library handle and callback function pointers persist until process exit or explicit unload. No files are persisted here, but the extension is always initialized with the literal config filename `config.txt`.

Dependencies/integration points: included by both fuse2 and fuse3 Go cgo handlers. Depends on `dlfcn.h`, libfuse headers, `fuse_operations_t` from `libfuse_defs.h`, and preprocessor build tags to select `fuse.h` vs `fuse3/fuse.h` and handshake strings. Integrated from `Libfuse.initFuse` when `extensionPath` is configured.

Risks: global state is not thread-safe and supports only one extension at a time. `dlerror` details are discarded in favor of numeric codes. On missing symbols or invalid signature, the already-open library is not closed in `load_library` itself. The misspelled `regsiter` names are internal but easy to propagate. Hard-coded `config.txt` limits configurability. Signature strings are simple handshakes, not security boundaries.

Test signals: no direct tests in this subset. Indirect coverage would require `Libfuse.initFuse` with a real extension library; the current libfuse tests do not mount or exercise extension loading.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/extension_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse.go -->
# sources/user-network-fs/blobfuse2/component/libfuse/libfuse.go

Purpose: defines the Blobfuse `libfuse` producer component, its configuration model, lifecycle hooks, defaults, and pipeline registration. It bridges global mount options and component config into fields consumed by version-specific cgo FUSE handlers.

Important APIs/types/functions: `Libfuse` embeds `internal.BaseComponent` and stores mount path, permissions, read-only/allow flags, timeout values, owner UID/GID, tracing, extension path, writeback/open-flag behavior, nonempty mount, `lsFlags`, max FUSE threads, direct I/O, umask, and kernel-cache disable. `dirChildCache` stores paginated `StreamDir` state per directory handle. `LibfuseOptions` declares config tags for libfuse YAML/CLI fields. Public component methods are `Name`, `SetName`, `SetNextComponent`, `Priority`, `Start`, `Stop`, `Validate`, `GenConfig`, and `Configure`; constructor and registration are `NewLibfuseComponent` and `init`.

Control flow: `Configure` unmarshals `libfuse` then legacy `lfuse`, reads global keys such as `mount-path`, `read-only`, `allow-other`, `allow-root`, `nonempty`, and `disable-kernel-cache`, calls `Validate`, suppresses FUSE trace when not running in foreground, and logs the resolved configuration. `Validate` applies direct field mapping, forces direct I/O when kernel cache is disabled, chooses permissions based on `allow-other` or `default-permission`, resolves default entry/attribute/negative timeouts unless explicitly configured, zeroes all timeouts for direct I/O, fills UID/GID from current user unless configured, and applies default max FUSE threads. `Start` creates a stats collector, initializes listing flags, sets global `fuseFS`, and calls version-specific `initFuse`. `Stop` calls version-specific `destroyFuse` and destroys stats.

State and persistence behavior: `fuseFS` is a package-global pointer used by exported cgo callbacks, so only one active libfuse component is represented. `libfuseStatsCollector` is also global and tracks operation events/counters across callbacks. The component does not persist data directly; it configures kernel/libfuse caching behavior and delegates all filesystem operations to `NextComponent`.

Dependencies/integration points: integrates with internal pipeline component registration as a producer, common defaults and user helpers, config package flags, logging, stats manager, and version-specific files selected by build tags (`libfuse_handler.go` for fuse3/default, `libfuse2_handler.go` for fuse2). Downstream filesystem operations are routed through `NextComponent`, commonly file-cache or storage components.

Risks: global `fuseFS` and stats collector make concurrent mounts in one process unsafe. `Validate` returns nil when current-user lookup fails after logging an error, which can hide a configuration problem. Direct I/O and disable-kernel-cache mutate timeout semantics globally. Foreground trace behavior depends on global `common.ForegroundMount`. Config is split across component and global keys, so precedence can be subtle.

Test signals: `libfuse_handler_test.go` covers default config, explicit config, zero timeouts, default permissions, disable-kernel-cache forcing direct I/O, foreground-only fuse trace, disable-writeback-cache toggles, and ignore-open-flags toggles. Handler wrapper tests rely on `newTestLibfuse` and direct `fuseFS` assignment to exercise callbacks without starting a real mount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse2_handler.go -->
# sources/user-network-fs/blobfuse2/component/libfuse/libfuse2_handler.go

Purpose: fuse2-specific cgo implementation of Blobfuse's FUSE callbacks. It converts Go `Libfuse` configuration into C fuse2 arguments, mounts via libfuse, translates FUSE callbacks into `internal.Component` operations, manages handle pointer round-trips, and maps errors to negative errno.

Important APIs/types/functions: build tag `fuse2`; cgo flags set `FUSE_USE_VERSION=29`, `_FILE_OFFSET_BITS=64`, and `__FUSE2__`. Key functions include `trimFusePath`, `(*Libfuse).convertConfig`, `(*Libfuse).initFuse`, `populateFuseArgs`, `destroyFuse`, exported `libfuse2_init`, `libfuse_destroy`, `fillStat`, `libfuse2_getattr`, `libfuse_statfs`, directory callbacks (`libfuse_mkdir`, `libfuse_opendir`, `libfuse2_readdir`, `libfuse_releasedir`, `libfuse_rmdir`), file callbacks (`libfuse_create`, `libfuse_open`, `libfuse_read`, `libfuse_write`, `libfuse_flush`, `libfuse_release`, `libfuse_fsync`, `libfuse2_truncate`, `libfuse_unlink`), rename/link callbacks, chmod/chown/utimens stubs, and `blobfuse_cache_update`.

Control flow: `initFuse` optionally loads an extension, retrieves extension callbacks, passes Blobfuse callbacks to it, or directly populates Blobfuse callbacks, then builds fuse args and calls `start_fuse`. `populateFuseArgs` constructs mount options for timeouts, `allow_other`, `allow_root`, `nonempty`, read-only, umask, fuse2-specific `atomic_o_trunc`, and either `direct_io` or `kernel_cache`, always running libfuse in foreground. `libfuse2_init` notifies the parent process, populates UID/GID in C, enables supported async/big-write/splice capabilities, and sets background/readahead values.

State and persistence behavior: open/create/opendir callbacks allocate `handlemap.Handle` objects and store their pointers in C-visible `fi.fh`, often through native `file_handle_t` wrappers. `release` and `releasedir` clean handlemap entries and native wrappers. Directory reads persist a `dirChildCache` in the handle to page through `StreamDir` results and add `.`/`..` only on initial fuse2 reads. File data persistence is delegated to `NextComponent`; cached handles can read via `syscall.Pread`, while non-cached handles call `ReadInBuffer`.

Dependencies/integration points: depends on libfuse2, `libfuse_wrapper.h`, `extension_handler.h`, Blobfuse common normalization and mount notification, handlemap, stats manager, and downstream `internal.Component` APIs. It is tightly coupled to C wrapper helpers like `populate_callbacks`, `allocate_native_file_object`, `release_native_file_object`, `fill_dir_entry`, `populate_statfs`, and `get_root_properties`.

Risks: unsafe pointer conversion across Go and C is central and must match native wrapper lifetime. Read/write convert C buffers through a fixed `[1 << 30]byte` view; requests larger than that would be invalid. Fuse2 truncate lacks a file handle, so ftruncate behaves like path truncate. `libfuse2_chown` and `libfuse2_utimens` are stubs returning success, which can mislead callers. Rename error mapping is incomplete for permission/invalid cases. `libfuse_readlink` writes `data[len(targetPath)] = 0` without checking `len(targetPath) < size`, so oversized targets can write beyond the intended buffer slice. Stats collector is assumed initialized.

Test signals: wrapper tests cover mkdir/rmdir/create/open/truncate/unlink/symlink/readlink/fsync/fsyncdir/chmod/statfs and many error mappings. Open tests confirm O_SYNC/O_DIRECT masking and fuse2 append/WRONLY behavior. Gaps remain around read/write/flush/release paths, readdir pagination, native wrapper lifetime, extension loading, and real mount negotiation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse2_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse2_handler_test_wrapper.go -->
# sources/user-network-fs/blobfuse2/component/libfuse/libfuse2_handler_test_wrapper.go

Purpose: fuse2-specific test helper file that defines the shared `libfuseTestSuite` scaffolding and callback helper functions used by `libfuse_handler_test.go` when built with the `fuse2` tag.

Important APIs/types/functions: `libfuseTestSuite` owns assertions, a `*Libfuse`, gomock controller, and `internal.MockComponent`. `fileHandle` mirrors the C native file-handle layout enough for tests to recover the Go handle pointer from `fi.fh`. `newTestLibfuse`, `SetupTest`, `setupTestHelper`, and `cleanupTest` configure a libfuse component without starting a real mount and assign global `fuseFS`. Helper functions include `testMkDir`, `testStatFs`, `testRmDir`, `testCreate`, `testOpen`, open-flag variations, `testTruncate`, no-op ftruncate tests, `testUnlink`, `testSymlink`, `testReadLink`, `testFsync`, `testFsyncDir`, `testChmod`, `testChown`, and `testUtimens`.

Control flow: each helper creates C strings and FUSE file-info structs, sets gomock expectations on the mock component, invokes the exported cgo callback directly, and asserts the returned C errno-style value. Open/create helpers let the callback allocate a native file object and then inspect its embedded Go handle pointer for fsync tests. Config-specific helpers tear down and rebuild the suite libfuse with custom YAML to test open-flag settings.

State and persistence behavior: no real filesystem persistence is used. State is held in gomock expectations, `handlemap`, allocated C strings/native file objects, and global `fuseFS`. Helpers call `cleanupTest` with `defer`, causing gomock verification after each helper. Since `Start` is not called, stats collector assumptions can matter if callback code updates stats; tests rely on package/test setup providing enough global state or paths that do not dereference nil stats in this environment.

Dependencies/integration points: depends on fuse2 cgo headers, `libfuse_wrapper.h`, `internal.MockComponent`, `handlemap`, global config reader, logging, `testify`, and the callback implementations in `libfuse2_handler.go`. The common `libfuse_handler_test.go` file calls these helper functions to avoid duplicating tests between fuse2 and fuse3 builds.

Risks: this is a wrapper rather than a full integration test; it bypasses libfuse's real C dispatch, kernel behavior, mount lifecycle, extension flow, and many native file I/O paths. There is a TODO for readdir tests. Helpers often return empty handles, which may not represent realistic cached/noncached handle state. Some tests do not release allocated native handles after open/create.

Test signals: validates callback-to-component option construction and errno mapping for common operations under fuse2. It specifically documents fuse2's lack of writeback-cache append-flag rewriting and fuse2's no-op ftruncate test behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse2_handler_test_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_constants.go -->
# sources/user-network-fs/blobfuse2/component/libfuse/libfuse_constants.go

Purpose: centralizes string constants used by libfuse stats/event reporting.

Important APIs/types/functions: constants name operations (`CreateDir`, `DeleteDir`, `CreateFile`, `TruncateFile`, `DeleteFile`, `RenameDir`, `RenameFile`, `CreateLink`, `ReadLink`, `SyncFile`, `SyncDir`, `Chmod`), gauge/counter key `OpenFileHandles`, and event metadata keys (`Mode`, `Size`, `Src`, `Dest`, `Target`).

Control flow: no executable control flow. Handler callbacks use these constants when calling `libfuseStatsCollector.PushEvents` and `UpdateStats`.

State and persistence behavior: no mutable state. Constants influence the names under which runtime stats/events are recorded and therefore the external observability schema.

Dependencies/integration points: imported within libfuse package handler files; coupled to `stats_manager.StatsCollector` consumers and any dashboards/log processors expecting these exact names.

Risks: changing strings is a compatibility break for metrics consumers. The file does not include constants for every callback (`OpenFile`, `ReadFile`, `WriteFile`, `FlushFile`, `ReleaseFile`, `Chown`, `Utimens` are absent), reflecting current instrumentation gaps.

Test signals: no direct tests. Indirect coverage occurs when callback tests exercise handlers that push events or update stats, but assertions generally focus on return codes and component options rather than emitted metric names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_defs.h -->
# sources/user-network-fs/blobfuse2/component/libfuse/libfuse_defs.h

Purpose: shared C definitions for the cgo libfuse wrapper. It normalizes fuse2/fuse3 type names, defines the C `fuse_options_t` config struct, declares Go-exported callback functions, and lists wrapper/native helper prototypes.

Important APIs/types/functions: typedef aliases for `fuse_operations_t`, `fuse_conn_info_t`, `fuse_config_t`, `fuse_args_t`, `fuse_file_info_t`, `statvfs_t`, `stat_t`, `timespec_t`, and readdir/fill flag enums. Fuse2 placeholder enums provide fuse3-only readdir/fill flags. `fuse_options_t` holds mount path, uid/gid, permissions, timeouts, read-only, allow flags, trace, non-empty, and umask. Extern declarations cover shared callbacks plus version-specific signatures for init/getattr/readdir/truncate/rename/chmod/chown/utimens. Native helper prototypes include `blobfuse_cache_update`, `native_read_file`, `native_write_file`, and `native_flush_file`.

Control flow: the header has no runtime control flow, but preprocessor branches select fuse2 vs fuse3 signatures and constants. The comments document cgo constraints: static C definitions to avoid duplicate symbols, `//export` requirements, no blank line before `import "C"`, and matching C/Go types.

State and persistence behavior: defines `static int fill_dir_plus`, zero for fuse2 and `FUSE_FILL_DIR_PLUS` for fuse3. Other content is type/prototype declarations only. No persistence occurs.

Dependencies/integration points: included by `libfuse_wrapper.h` and cgo handler files. Must match Go exported function names exactly and match libfuse ABI differences between fuse2 and fuse3. It also documents unsupported FUSE operations that Blobfuse does not implement.

Risks: signature mismatches between this header, wrapper code, and Go exports will fail compilation or cause runtime ABI corruption. Static definitions are necessary because cgo may include the header in multiple translation units. The fuse2 placeholder enums must not conflict with real fuse2 headers. Unsupported callback list shows feature gaps such as xattrs, lock, fallocate, copy_file_range, lseek, and ioctl.

Test signals: compile-time cgo builds are the primary test. Runtime callback tests indirectly validate that selected declarations match Go functions for the active fuse version.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler.go -->
# sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler.go

Purpose: default fuse3 cgo implementation of Blobfuse's FUSE callbacks. It is the fuse3 counterpart to `libfuse2_handler.go`, adding fuse3 mount options, capability negotiation, writeback-cache open-flag handling, file-handle-aware truncate, and rename flags.

Important APIs/types/functions: build tag `!fuse2`; cgo uses `FUSE_USE_VERSION=39` and `-lfuse3`. Key functions mirror fuse2: `trimFusePath`, `convertConfig`, `initFuse`, `populateFuseArgs`, `destroyFuse`, exported `libfuse_init`, `libfuse_destroy`, `fillStat`, `libfuse_getattr`, directory callbacks, `libfuse_statfs`, file callbacks, `libfuse_truncate`, `libfuse_rename`, symlink/readlink/fsyncdir/chmod/chown/utimens, and `blobfuse_cache_update`.

Control flow: initialization optionally loads an extension, exchanges callback tables, builds args, and starts fuse3. `populateFuseArgs` emits timeouts, allow/read-only/umask, `max_read=1048576`, and `kernel_cache` unless direct I/O is enabled. `libfuse_init` notifies parent, populates UID/GID, enables supported fuse3 capabilities (`PARALLEL_DIROPS`, `AUTO_INVAL_DATA`, `READDIRPLUS`, `ASYNC_READ`, `SPLICE_WRITE`, and optionally `WRITEBACK_CACHE`), sets max background/readahead/read/write values, gates max_write by detected fuse minor version, and sets `cfg.direct_io` for direct I/O. Callback flow normalizes paths, delegates to `NextComponent`, fills stat structs, updates stats, and returns negative errno.

State and persistence behavior: global `fuseFS` drives all callbacks. Directory handles store `dirChildCache` for paginated `StreamDir`; unlike fuse2, adding `.`/`..` is commented out for fuse3. File handles are allocated as native C objects containing a Go handle pointer and optional file descriptor; release removes handlemap entries and frees native objects. `libfuse_flush` and `libfuse_release` propagate native dirty state to `handlemap.Handle` before delegating flush/release. Persistence is delegated to downstream components.

Dependencies/integration points: depends on libfuse3 ABI, C wrapper helpers, extension loader, common path normalization and fuse minor detection, stats manager, handlemap, and the internal component interface. Fuse3 open behavior interacts with file-cache semantics: when writeback cache is enabled, O_WRONLY and O_APPEND are either rewritten to O_RDWR if `ignoreOpenFlags` is true or rejected with `EINVAL`.

Risks: unsafe pointer lifetimes and fixed-size C buffer casts carry the same risks as fuse2. Writeback-cache flag rewriting changes application-visible open semantics and must align with file-cache behavior. `RENAME_EXCHANGE` is explicitly unsupported and returns `ENOTSUP`; other rename error handling is incomplete. `chown` and `utimens` return success without implementation. `readlink` can overrun intended buffer bounds for oversized targets. Stats collector/global state assumptions apply to every callback.

Test signals: common libfuse tests cover config, mkdir/rmdir/create/open/truncate/unlink/symlink/readlink/fsync/fsyncdir/chmod/statfs and open-flag policy. Fuse3-specific behavior is covered by the non-fuse2 wrapper in sibling files outside this work item; this file itself is validated by default builds and the shared test suite. Gaps include real readdir, read/write/flush/release, extension loading, writeback-cache kernel behavior, and mount negotiation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler_test.go -->
# sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler_test.go

Purpose: shared libfuse test suite that validates component configuration and calls version-specific callback helper functions supplied by the active build's test wrapper.

Important APIs/types/functions: methods on `libfuseTestSuite` include `TestDefault`, `TestConfig`, `TestConfigZero`, `TestConfigDefaultPermission`, `TestConfigDisableKernelCache`, `TestConfigFuseTraceEnable`, `TestDisableWritebackCache`, `TestIgnoreAppendFlag`, and a matrix of callback tests delegating to helpers such as `testMkDir`, `testRmDir`, `testCreate`, `testOpen`, `testTruncate`, `testUnlink`, `testSymlink`, `testReadLink`, `testFsync`, `testFsyncDir`, `testChmod`, `testStatFs`, `testChown`, and `testUtimens`. `TestLibfuseTestSuite` registers the suite with `testify`.

Control flow: config tests tear down the default setup and recreate libfuse with YAML snippets to assert resolved fields. Callback tests are thin wrappers; the actual gomock expectations and C callback invocations live in version-specific `*_handler_test_wrapper.go` files selected by build tags. This keeps behavior expectations common while adapting cgo signatures for fuse2/fuse3.

State and persistence behavior: no real mount or storage persistence. Tests mutate global config and, for foreground trace, `common.ForegroundMount`. They assert `Libfuse` struct state and callback return values rather than persisted filesystem artifacts. The wrapper tests set package-global `fuseFS` to the test component.

Dependencies/integration points: depends on `testify/suite`, common permission defaults/global foreground flag, `io/fs` mode values, and the active build's wrapper helper functions. It indirectly integrates with gomock internal component mocks and cgo callback implementations.

Risks: because tests do not start `Libfuse.Start`, they do not validate real mount startup, extension loading, capability negotiation, or stats collector lifecycle. Callback coverage omits read, write, flush, release, and readdir paths. Global `common.ForegroundMount` is reset manually and could leak if a test panics before reset. The same test file serves both fuse versions, so version-specific expectations must remain in wrappers.

Test signals: strong for configuration defaults and option precedence: allow-other permissions, direct I/O timeout zeroing, default-permission override, disable-kernel-cache forcing direct I/O, foreground-only trace, writeback-cache toggle, and ignore-open-flags toggle. Callback signals cover common errno mapping and option construction for many metadata operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler_test.go -->
