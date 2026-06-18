# subset-b-007951 research

Grouped research for the requested XRootD source files. Each source file section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPagesUnaligned.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPagesUnaligned.cc

## Purpose
Implements the unaligned read/write checksum paths for `XrdOssCsiPages`. It maintains per-page CRC32C tags when writes do not align cleanly to `XrdSys::PageSize`, when writes extend a file through sparse holes, or when reads need verification/checksum results for partial pages.

## Important APIs and control flow
`UpdateRangeHoleUntilPage()` fills missing tag entries between the tracked file size and a later page, extending a partial tracked page with zero CRC state and then writing either zero-filled-page CRCs or literal zero tags depending on `writeHoles_`. `UpdateRangeUnaligned()` is a wrapper around `StoreRangeUnaligned()` for ordinary writes without a caller-provided checksum vector.

`StoreRangeUnaligned()` handles partial first pages via `StoreRangeUnaligned_preblock()`, optional partial final pages via `StoreRangeUnaligned_postblock()`, and delegates full interior tag updates to `apply_sequential_aligned_modify()`. The preblock path covers sparse append, append inside the current last page, and partial overwrite. Non-loose mode requires existing data to match the stored tag before recalculating; `loosewrite_` allows several recovery checks where on-disk content or an already-applied write can explain a mismatch.

`FetchRangeUnaligned()` reads the needed tags into either the caller's `csvec` or an internal tag buffer, verifies full pages in batches, and calls pre/post helpers to handle partial page verification and checksum-vector trimming.

## State, dependencies, and integration
State is the sidecar tagstore `ts_`, file name `fn_`, loose-write fields, and the tracked sizes supplied by the caller. It depends on `XrdOssDF` reads, `XrdOucCRC::Calc32C`, `XrdOssCsiCrcUtils` checksum combine/split helpers, `XrdSys::PageSize`, and CSI trace macros.

## Risks and test signals
Important risks are off-by-one page boundaries, signed/unsigned offset conversions, sparse-hole semantics when `writeHoles_` is false, and concurrent modification between user buffers and rereads. Good tests write and read ranges crossing page boundaries, append after holes, truncate and rewrite short last pages, exercise `Verify` plus `csvec`, and force corrupted tag/data mismatches in both strict and loose-write modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPagesUnaligned.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiRanges.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiRanges.cc

## Purpose
Provides the out-of-line lifetime methods for `XrdOssCsiRangeGuard`, the RAII object used by CSI page code to release page-range reservations and tracked-size locks.

## Important APIs and control flow
`ReleaseAll()` first releases a tracked-size lock if one is held, then removes the range from the owning `XrdOssCsiRanges` object and clears local pointers. `Wait()` asserts that the guard owns a range and delegates to `XrdOssCsiRanges::Wait()`. `unlockTrackinglen()` asserts that the guard has an associated `XrdOssCsiPages` object and calls `TrackedSizeRelease()`. The destructor calls `ReleaseAll()`, so normal scope exit cleans up both locking layers.

## State, dependencies, and integration
The file depends on `XrdOssCsiRanges.hh` for the guard/range definitions and `XrdOssCsiPages.hh` for tracked-size release. It does not persist state; it coordinates in-memory locks already acquired by page operations.

## Risks and test signals
Correctness depends on every successful `SetRange()` or `SetTrackingInfo(..., locked=true)` being paired with guard destruction or explicit `ReleaseAll()`. Assertions catch programmer misuse but disappear in release builds. Stress tests should issue overlapping read/write page operations, throw or early-return through guarded regions, and confirm no waiters remain blocked after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiRanges.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiRanges.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiRanges.hh

## Purpose
Defines the page-range locking primitive used by the CSI checksum layer to serialize overlapping mutations while allowing non-overlapping operations and compatible read-only overlaps.

## Important APIs and types
`XrdOssCsiRange_s` stores an inclusive page range, a read-only flag, the count of earlier overlapping blockers, its own mutex/condition variable, and a free-list link. `XrdOssCsiRangeGuard` owns a registered range and optional tracked-size lock, exposes `Wait()`, `ReleaseAll()`, `unlockTrackinglen()`, and records the tracked-size pair seen by the caller. `XrdOssCsiRanges` maintains `ranges_` plus a recycled allocation list.

`AddRange()` counts overlapping non-compatible existing ranges, allocates a range record, pushes it to the active list, and arms the guard. `Wait()` blocks on the range's condition variable until `nBlockedBy` reaches zero. `RemoveRange()` erases a completed range, decrements blocker counts for later overlapping ranges, notifies newly unblocked ranges, and recycles the node.

## State, dependencies, and integration
State is purely in-memory and protected by `rmtx_` plus per-range mutexes. It depends on C++ mutex/condition-variable primitives and `XrdSysPthread.hh`. CSI page read/write code integrates it with tracked-size locking in `XrdOssCsiPages`.

## Risks and test signals
The active-list algorithm assumes ranges are removed exactly once and that compatibility only exists for read-only/read-only overlaps. Recycled nodes must not retain stale counters or flags after `AddRange()` reinitializes them. Tests should cover multiple waiters, read-only sharing, writer after readers, readers after writer, and destruction while waiters are pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiRanges.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstore.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstore.hh

## Purpose
Declares the abstract sidecar checksum tag storage interface used by CSI page checksum code. Implementations persist per-page CRC32C tags and metadata about the amount of data covered by those tags.

## Important APIs and types
`XrdOssCsiTagstore` exposes lifecycle methods `Open()` and `Close()`, durability methods `Flush()` and `Fsync()`, bulk tag I/O methods `WriteTags()` and `ReadTags()`, size/status accessors `GetTrackedTagSize()`, `GetTrackedDataSize()`, and `IsVerified()`, plus state mutators `SetTrackedSize()`, `SetUnverified()`, `ResetSizes()`, and `Truncate()`. The `csVer` flag marks a tag file whose checksums are considered verified.

## State, dependencies, and integration
The interface depends on `XrdOss.hh` for `XrdOucEnv`, `XrdOssDF`, and OSS error conventions. It stores no state itself; concrete implementations such as `XrdOssCsiTagstoreFile` hold the file descriptor and header.

## Risks and test signals
The contract uses negative errno-style returns and `ssize_t` tag counts, so callers must distinguish bytes from tag entries. Implementations must keep tracked data length, tag file length, and verified/unverified state consistent across open, write, truncate, and close. Tests should use a mock tagstore for page logic and an on-disk implementation test for endian, truncation, and header integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstore.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstoreFile.cc -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstoreFile.cc

## Purpose
Implements the file-backed CSI tagstore. The on-disk format is a 20-byte header followed by one 32-bit CRC tag per data page.

## Important APIs and control flow
`Open()` opens the sidecar through the wrapped `XrdOssDF`, determines machine endianness, attempts to read and validate the header magic and header CRC, initializes a new header if needed, warns on tracked-size disagreement, and calls `ResetSizes()`. A local guard closes the descriptor if initialization fails. `ResetSizes()` compares expected sidecar length with `Fstat()` and either truncates an overlong tag file or reduces the tracked size if the sidecar is short. `Fsync()`, `Flush()`, and `Close()` forward to the underlying descriptor.

`WriteTags()` and `ReadTags()` translate tag offsets to byte offsets at `20 + 4 * off`, using swapped variants when file and machine endian differ. `Truncate()` first adjusts sidecar length, then updates the header tracked size and, when truncating data to zero, marks the tags verified. `WriteTags_swap()` and `ReadTags_swap()` batch 1024 tags through a local conversion buffer.

## State, dependencies, and integration
Persistent state is the header magic, tracked length, flags, header CRC, and tag array. Runtime state includes `trackinglen_`, `actualsize_`, `fileIsBige_`, `machineIsBige_`, `hflags_`, and `isOpen`. It integrates with CSI page code through `XrdOssCsiTagstore`.

## Risks and test signals
Key risks are partial sidecar writes, stale verified flags after data modification, short sidecar recovery reducing coverage, and endian conversion. Tests should open legacy/empty/corrupt headers, round-trip tags on simulated opposite endian data, truncate up/down, and inject short reads/writes from a fake `XrdOssDF`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstoreFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstoreFile.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstoreFile.hh

## Purpose
Declares the concrete file-backed implementation of `XrdOssCsiTagstore`, including the sidecar header marshalling helpers and full-read/full-write utilities.

## Important APIs and types
The constructor takes the logical file name, an owned `XrdOssDF`, and a trace identity. Public overrides implement open/close, flush/fsync, tag I/O, truncation, tracked-size accessors, verification-state mutation, and size resynchronization. `SetTrackedSize()` updates `actualsize_` when needed and writes a new header when the tracked length changes. `SetUnverified()` clears the `csVer` flag and rewrites the header.

`fullread()` repeatedly calls `Read()` until the exact requested byte count is read, returning `-EDOM` on short read. `fullwrite()` loops until all bytes are written. `MarshallAndWriteHeader()` writes magic, tracked length, flags, and a CRC32C over the first 16 header bytes, applying byte swaps when the file byte order differs from the host.

## State, dependencies, and integration
The class owns `fd_`, caches header bytes and endian flags, and stores `trackinglen_`/`actualsize_`. It depends on OSS descriptor APIs, `XrdOucCRC`, `XrdSysPlatform` byte swaps, and the abstract tagstore header.

## Risks and test signals
The destructor closes if still open, so ownership is simple but callers must not retain the moved descriptor. `fullwrite()` assumes zero-byte writes do not occur indefinitely. Tests should cover idempotent close behavior, header CRC calculation, `SetUnverified()` persistence, and exact-byte I/O failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTagstoreFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTrace.hh

## Purpose
Defines trace flags and macros for the OSS CSI checksum module.

## Important APIs and control flow
`TRACE_ALL`, `TRACE_Warn`, `TRACE_Info`, and `TRACE_Debug` define bit masks consumed by a global `XrdOucTrace` instance. In non-`NODEBUG` builds, `QTRACE()` checks whether a trace class is active. `TRACE()` emits a message through `OssCsiTrace.Beg()`/`End()` using the local `epname` and `tident` symbols expected in calling code. `TRACEReturn()` logs and returns an error code. `DEBUG()` emits debug-only messages. `EPNAME()` declares a static function name used by trace output. In `NODEBUG` builds the macros collapse to no-ops or bare returns.

## State, dependencies, and integration
The header depends on `XrdOucTrace.hh` and, for debug builds, `XrdSysHeaders.hh`/`std::cerr`. It does not define the global trace object; CSI implementation files declare it as `extern XrdOucTrace OssCsiTrace`.

## Risks and test signals
The macros assume caller scope contains compatible `tident` where `TRACE()` is used; missing symbols produce compile errors. Since `TRACE()` wraps stream expressions, side effects inside disabled trace expressions are skipped. Build tests should compile CSI with and without `NODEBUG`, and runtime tests should verify trace masks gate warnings/info/debug as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssHandler.hh -->
# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssHandler.hh

## Purpose
Provides chain-of-responsibility base wrappers for OSS plugins. Derived classes can override selected methods while forwarding the rest to a successor OSS or data-file object.

## Important APIs and types
`XrdOssDFHandler` inherits `XrdOssDF` and forwards directory operations, file operations, page read/write operations, AIO methods, vector I/O, raw reads, close, fctl, and transaction ID access to `successor_`. Its constructor mirrors the successor's TID, DF type, and FD into the base class, and its destructor deletes the successor.

`XrdOssHandler` inherits `XrdOss` and forwards filesystem-level methods including chmod, connect/disconnect, create, features, fsctl, mkdir, reloc, remdir, rename, stat variants, truncate, unlink, and LFN/PFN translation. Comments indicate derived classes must provide `newDir()`, `newFile()`, and initialization behavior.

## State, dependencies, and integration
State is just the successor pointer. The header depends on `XrdOss.hh` and integrates with plugins that layer functionality such as CSI checksum validation or stats collection over an existing OSS.

## Risks and test signals
Ownership differs between classes: `XrdOssDFHandler` deletes its successor, while `XrdOssHandler` leaves its successor alive. Plugin tests should confirm ownership expectations, forwarding of all overloaded methods, and correct behavior when derived wrappers override only a subset of calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdOssStats/CMakeLists.txt

## Purpose
Builds and installs the `XrdOssStats` OSS plugin module.

## Important APIs and build flow
The script sets the module target name to `XrdOssStats-${PLUGIN_VERSION}` and creates a `MODULE` library from the stats config, file, and filesystem sources/headers. It links the plugin privately against `XrdServer` and `XrdUtils`. On non-Apple platforms it applies an ELF version script from `export-lib-symbols` to constrain exported symbols. Finally it installs the module to `${CMAKE_INSTALL_LIBDIR}`.

## Dependencies and integration
The target integrates into the broader XRootD plugin build and relies on `PLUGIN_VERSION`, `CMAKE_INSTALL_LIBDIR`, and core XRootD targets being defined by the parent CMake project.

## Risks and test signals
The most important build risk is symbol visibility: the plugin entry point must remain exported by the version script. Tests should build on Linux and macOS, inspect exported symbols for `XrdOssAddStorageSystem2`, and load the plugin in an XRootD configuration with `osslib`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsConfig.cc

## Purpose
Implements stats-plugin configuration helpers and the plugin entry point used by XRootD to wrap an existing OSS.

## Important APIs and control flow
`LogMaskToString()` renders configured log mask bits as a comma-separated string, with `all` as a special case. `ParseDuration()` parses compound duration strings such as `1s500ms`; it repeatedly consumes a floating-point value and a unit among `ns`, `us`, `ms`, `s`, `m`, or `h`, rejects empty, negative, unknown-unit, missing-unit, and out-of-range inputs, and returns a `steady_clock::duration`.

The `extern "C"` function `XrdOssAddStorageSystem2()` constructs `XrdOssStats::FileSystem` around `curr_oss`, asks `InitSuccessful()` whether initialization succeeded, and either returns the new wrapper, bypasses the wrapper for non-fatal initialization failure, or returns null for fatal initialization failure. `XrdVERSIONINFO` publishes plugin version metadata.

## State, dependencies, and integration
This file depends on `XrdVersion.hh`, `XrdSysError`, and `XrdOssStatsFileSystem`. It is the integration boundary between XRootD's plugin loader and the stats filesystem wrapper.

## Risks and test signals
Parsing uses `typeof(dur)`, which is a GNU extension and may affect portability. The entry point must not delete `curr_oss` when bypassing; `InitSuccessful()` handles ownership release. Tests should exercise duration parsing edge cases and plugin startup paths for configured g-stream, missing g-stream, and fatal configuration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsConfig.hh

## Purpose
Declares small configuration utilities shared by the stats plugin.

## Important APIs and types
Inside `XrdOssStats::detail`, `LogMask` defines bit values for `Debug`, `Info`, `Warning`, `Error`, and `All`. `LogMaskToString(int mask)` converts a mask to display text. `ParseDuration()` converts a user-supplied duration string into `std::chrono::steady_clock::duration` and returns an error message on failure.

## State, dependencies, and integration
The header depends only on `<chrono>` and `<string>`. It is consumed by `XrdOssStatsConfig.cc` and `XrdOssStatsFileSystem.cc` while parsing `fsstats.trace` and `fsstats.slowop`.

## Risks and test signals
The enum values intentionally mirror the message mask used by `XrdSysError`; any change should be validated against logging behavior. Unit tests should cover mask rendering and duration parsing without needing a live OSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsDirectory.hh -->
# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsDirectory.hh

## Purpose
Defines the directory wrapper used by the stats OSS plugin to time directory listing operations.

## Important APIs and control flow
`Directory` inherits `XrdOssWrapDF`, owns the wrapped `XrdOssDF` in `m_wrappedDir`, and forwards through `wrapDF`. `Opendir()` wraps the call in `FileSystem::OpTimer` using directory-list operation counters and timing fields. `Readdir()` similarly times individual directory entries using the `m_dirlist_entries` counter and the same directory-list timing bucket.

## State, dependencies, and integration
The object holds a copy of `XrdSysError`, a reference to the parent `FileSystem`, and the owned wrapped directory descriptor. It depends on `XrdOucEnv`, `XrdOssWrapper`, and `XrdOssStatsFileSystem`.

## Risks and test signals
The wrapper only instruments open/list operations, leaving other descriptor methods inherited through `XrdOssWrapDF`. Directory tests should verify descriptor ownership, forwarded return codes, and increments to directory operation and slow-operation counters under configured slow thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsDirectory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFile.cc -->
# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFile.cc

## Purpose
Provides the out-of-line destructor for the stats file wrapper.

## Important APIs and control flow
The file includes `XrdOssStatsFile.hh`, uses the `XrdOssStats` namespace, and defines `File::~File() {}`. Actual forwarding and timing logic is inline in the header.

## State, dependencies, and integration
The destructor relies on members declared in the header, especially the `std::unique_ptr<XrdOssDF>` that owns the wrapped descriptor. Destruction of the wrapper releases the underlying OSS data-file object through normal C++ member destruction.

## Risks and test signals
Although the destructor is empty, it is a useful ABI anchor for the class. Tests should ensure deleting `File` through an `XrdOssDF` pointer releases the wrapped descriptor exactly once and does not require explicit close beyond normal OSS semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFile.hh -->
# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFile.hh

## Purpose
Defines the file descriptor wrapper used by `XrdOssStats::FileSystem` to count and time file-level OSS operations.

## Important APIs and control flow
`File` inherits `XrdOssWrapDF`, owns the wrapped `XrdOssDF`, and forwards calls through `wrapDF`. Most methods construct a `FileSystem::OpTimer` around the operation: `Open`, `Fchmod`, `Fstat`, `Ftruncate`, `pgRead`, `pgWrite`, scalar `Read` variants, scalar `Write`, and `WriteV`. `ReadV()` is manually timed so it can also count vector segments in `m_readv_segs`.

## State, dependencies, and integration
The wrapper holds `m_wrapped`, a logger reference, an unused `m_client` pointer, and a parent `FileSystem` reference. It directly updates the parent's atomic counters/timers through friendship. It depends on `XrdOssWrapper`, `XrdSysError`, and the filesystem header.

## Risks and test signals
`ReadV()` appears to add slow readv duration to `m_times.m_readv` rather than `m_slow_times.m_readv`, unlike `OpTimer`; this is a likely metrics bug. The `m_client` member is not initialized by the constructor. Tests should compare counters for every file operation, check vector segment accounting, and verify slow-readv timing lands in the expected JSON field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFileSystem.cc -->
# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFileSystem.cc

## Purpose
Implements the stats OSS wrapper that instruments filesystem operations and periodically emits aggregate metrics through XRootD's monitoring g-stream.

## Important APIs and control flow
The constructor configures logging and slow-operation threshold, obtains `oss.gStream*` from the environment, reads optional `oss.runmode`, starts a background aggregation thread with `XrdSysThread::Run()`, and marks the wrapper ready. Missing g-stream is treated as non-fatal bypass; missing environment and thread creation failures are fatal. `InitSuccessful()` communicates those outcomes and releases ownership of the underlying OSS on bypass.

`Config()` gathers `fsstats.trace` and `fsstats.slowop` directives from the config file. It maps trace names to `XrdSysError` masks and parses slow durations with `ParseDuration()`. `newDir()` and `newFile()` wrap underlying descriptors in stats `Directory` and `File` objects. Filesystem operations such as `Chmod`, `Rename`, stat variants, `Truncate`, and `Unlink` are timed with `OpTimer`.

`AggregateBootstrap()` loops forever, sleeping one second and calling `AggregateStats()`. `AggregateStats()` formats one JSON record with normal and slow counts plus accumulated seconds and inserts it into g-stream. `OpTimer` increments counts and nanosecond totals on destruction, including separate slow counters when duration exceeds the configured threshold.

## State, dependencies, and integration
State is atomic counter structs, timing structs, `m_slow_duration`, `m_runmode`, owned wrapped OSS, logger, and g-stream pointer. Dependencies include `XrdOucGatherConf`, `XrdOssWrapper`, `XrdXrootdGStream`, atomics, pthread helpers, and `<thread>`.

## Risks and test signals
The aggregation thread has no shutdown path and may call into a destructing object if plugin lifetime changes. JSON formatting uses a fixed 1500-byte buffer. Tests should validate config parsing, startup bypass/fatal cases, metric increments for all wrapper methods, slow thresholds, runmode event naming, and g-stream insert failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFileSystem.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFileSystem.hh -->
# sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFileSystem.hh

## Purpose
Declares `XrdOssStats::FileSystem`, an `XrdOssWrapper` implementation that owns an underlying OSS and records operation counts/timings.

## Important APIs and types
Public APIs include construction, `Config()`, `InitSuccessful()`, `newDir()`, `newFile()`, and overrides for filesystem operations that can be instrumented. Private `AggregateBootstrap()` and `AggregateStats()` drive periodic emission. Nested `OpTimer` records count and elapsed time via RAII. `OpRecord` groups operation counters; `OpTiming` groups accumulated nanosecond timers.

## State, dependencies, and integration
The class is friends with `File` and `Directory`, allowing descriptor wrappers to update counters directly. It stores `m_gstream`, initialization state, `m_runmode`, owned `m_oss`, environment pointer, logger, normal/slow counters, normal/slow timings, and slow-duration threshold. Dependencies are `XrdOssWrapper`, `XrdSysError`, `XrdSysRAtomic`, and `XrdXrootdGStream` forward declaration.

## Risks and test signals
All counters are atomic, but object lifetime around the background thread is the main concurrency risk. The header exposes many counters indirectly through friendship, so changes to counter names must stay synchronized with JSON output. Tests should compile wrappers against the current OSS virtual method set and verify ABI/plugin loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOssStats/XrdOssStatsFileSystem.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdOuc/CMakeLists.txt

## Purpose
Adds the XrdOuc utility sources to the `XrdUtils` target and builds the `XrdN2No2p` name-to-name plugin.

## Important build flow
The file first looks for system `nlohmann_json` 3.10.2. When present, it links `XrdUtils` publicly to `nlohmann_json::nlohmann_json` and defines `USE_SYSTEM_NLOHMANN_JSON`. `target_sources(XrdUtils PRIVATE ...)` then lists a large set of OUC implementation and header files, including argument parsing, backtrace, buffers, cache interfaces, CRC, environment/config helpers, JSON, name mapping, plugin loading, ranges, tokenizers, tracing, URIs, and miscellaneous utility containers.

At the end it creates `XrdN2No2p-${PLUGIN_VERSION}` as a module from `XrdOucN2No2p.cc`, links it against `XrdUtils`, and installs it to `${CMAKE_INSTALL_LIBDIR}`.

## Dependencies and integration
This is a central build manifest for the utility library used throughout XRootD. The optional JSON dependency changes compile definitions consumed by OUC JSON code.

## Risks and test signals
Because many headers are listed as private sources, IDE/export behavior depends on parent CMake conventions. Build tests should cover both bundled-json and system-json configurations, and plugin tests should confirm the `XrdN2No2p` module loads with the expected versioned name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucArgs.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucArgs.cc

## Purpose
Implements `XrdOucArgs`, a getopt-like parser that supports single-character options, optional/required arguments, long option abbreviations, and input from either argv arrays or tokenizer-backed strings.

## Important APIs and control flow
`XrdOucArgsXO` stores one extended option mapping: option word, minimum abbreviation length, one-character mapped value plus option suffix, and linked-list next pointer. Its `%` operator searches for a matching abbreviation and returns the mapped option spec.

The `XrdOucArgs` constructor records error reporting, copies the standard option string, detects leading `:` to change missing-argument return from `?` to `:`, and consumes varargs triples for extended options. `getarg()` returns remaining non-option arguments from the stream or argv. `getopt()` fetches the next token, verifies it begins with `-`, resolves long or single-letter options, handles invalid options, consumes required or optional arguments, rolls back optional arguments that look like options, and reports missing values.

`Set(char*)` attaches a tokenizer to a command string; `Set(int,char**)` switches to argv mode.

## State, dependencies, and integration
State includes tokenizer position, argv index, option specs, current option pointer, `argval`, and error prefix. Dependencies are `XrdOucTokenizer` and `XrdSysError`.

## Risks and test signals
The parser intentionally does not support clustered short options (`-ab`). It uses `strdup/free`, raw varargs, `sprintf` into a fixed buffer for invalid-option messages, and `index()` from strings compatibility headers. Tests should cover required/optional arguments, abbreviation collisions, invalid long options, `:` missing-argument mode, string mode rollback, and reusing one parser via repeated `Set()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucArgs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucArgs.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucArgs.hh

## Purpose
Declares the `XrdOucArgs` command-line parser used by XRootD utilities and interactive command code.

## Important APIs and types
`getopt()` returns option identifiers similarly to C `getopt()`, with `?`, `:`, or `-1` signaling invalid option, missing value, or option-list exhaustion. `getarg()` returns positional arguments after option parsing. `Set(char*)` and `Set(int,char**)` choose string-tokenizer or argv input. The constructor accepts a standard option specification plus varargs triples for extended options: long word, minimum abbreviation length, and mapped one-character option spec.

The public `argval` points to the current option argument when one is consumed.

## State, dependencies, and integration
The class embeds `XrdOucTokenizer`, stores error target/prefix, linked extended options, valid option string, current option cursor, argv position, and missing-argument return policy. It forward-declares `XrdSysError` and `XrdOucArgsXO`.

## Risks and test signals
The varargs constructor is type-unsafe and must be terminated with a null option word. Consumers must not assume POSIX clustered short-option behavior. Tests should include documented examples such as `debug` and `force`, optional argument behavior with following `-` tokens, and parser reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucArgs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBackTrace.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBackTrace.cc

## Purpose
Implements optional debugging backtraces with filters by pointer, XRootD request code, and response/status code.

## Important APIs and control flow
Static request/response tables map protocol names to numeric codes and bit masks. `Init()` populates request and response filters from explicit strings or `XRDBT_REQFILTER`/`XRDBT_RSPFILTER`, using `XrdOucTokenizer`. `Filter()` manages pointer filters for `this` or object pointers under `btMutex`, supporting add, clear, delete, and replace actions while `xeqPtrFilter` provides a fast atomic indication that any pointer filters exist.

`DoBT()` applies pointer filters unless forced, formats a `TBT` header with thread id and pointers, calls `DumpStack()`, and writes to `std::cerr`. `XrdBT()` additionally applies request/response filters. `DumpStack()` uses `backtrace()` and `backtrace_symbols()` except on musl, demangles C++ symbols with `abi::__cxa_demangle`, and limits depth using `XRDBT_DEPTH` capped at 30.

## State, dependencies, and integration
State is process-global filter vectors and bit masks. Dependencies include XRootD protocol constants, tokenizer, atomics, pthread mutex helpers, platform thread IDs, and glibc/macos backtrace APIs.

## Risks and test signals
`Filter(delIt)` emits an unconditional `std::cerr` debug line, which may be unintended in production. `backtrace_symbols()` output is not freed, creating a small allocation leak per dump. Tests should validate filter truth tables, env-var parsing, forced traces, musl fallback, depth capping, and request/response code mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBackTrace.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBackTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBackTrace.hh

## Purpose
Documents and declares the public backtrace debugging interface for XRootD and general code.

## Important APIs and types
`DoBT()` produces a generic backtrace header including `thisP` and `objP`, with optional head/tail strings and a `force` flag. `Init()` configures XRootD-specific request/response filters from strings or environment variables. `Filter()` configures pointer filters. `XrdBT()` emits an XRootD-specific trace including request and response names.

`PtrType` distinguishes `isThis` and `isObject` filters. `Action` selects add, clear, delete, or replace behavior.

## State, dependencies, and integration
The header itself has no includes besides guards; implementation supplies all platform and protocol dependencies. It is designed for selective debugging of rare races or unexpected protocol paths and is safe to call from multiple threads according to the comments.

## Risks and test signals
The filtering rules are non-trivial: pointer filters can force traces, both pointer lists set can suppress nonmatching calls, and `XrdBT()` requires code filters unless forced. Tests should encode the documented filtering matrix and verify `force=true` bypasses all configured filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBackTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBuffer.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBuffer.cc

## Purpose
Implements an aligned buffer pool and movable buffer object used to reduce allocation churn and data copies.

## Important APIs and control flow
`XrdOucBuffPool::XrdOucBuffPool()` normalizes the minimum size to a power-of-two KiB bucket, rounds maximum size to slot increments, and computes per-slot retention limits. `Alloc()` maps a requested size to a slot, reuses a free buffer under `SlotMutex` when available, or allocates a new `XrdOucBuffer` with `posix_memalign()` using page or smaller alignment.

`BuffSlot::~BuffSlot()` deletes all cached free buffers. `BuffSlot::Recycle()` deletes the buffer if the slot already holds enough cached buffers; otherwise it clears data length/offset and pushes it onto the free list.

`XrdOucBuffer(char*,int)` creates a one-time buffer backed by caller-provided `posix_memalign()` memory and a static null pool. `Clone()` allocates from the same pool and copies `doff + dlen` bytes. `Highjack()` allocates a replacement for the current object and swaps state so the returned object owns the original buffer. `Resize()` highjacks and recycles when the size changes.

## State, dependencies, and integration
Pool state is slot metadata, free lists, bucket sizes, and `alignit` from `sysconf(_SC_PAGESIZE)`. Dependencies are `XrdSysMutex`, `XrdSysPlatform`, and POSIX allocation.

## Risks and test signals
`Recycle()` checks `numbuff >= maxbuff` before taking the slot lock, so concurrent recycle can overshoot retention. One-time buffers use a zero-size null pool, making clone/highjack/resize fail as documented. Tests should cover alignment, slot rounding, concurrent allocation/recycle, one-time buffer limitations, clone trimming, and highjack ownership transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBuffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBuffer.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBuffer.hh

## Purpose
Declares `XrdOucBuffPool` and `XrdOucBuffer`, a small buffer-management layer for XRootD utility code.

## Important APIs and types
`XrdOucBuffPool` exposes `Alloc()` and `MaxSize()`. Its constructor parameters control minimum/maximum buffer size, minimum/maximum retained buffers, and reduction rate for larger buckets. Nested `BuffSlot` stores a mutex, free-list head, slot size, current retained count, and maximum retained count.

`XrdOucBuffer` exposes `Buffer()`, `BuffSize()`, `Data()`, `Data(int&)`, `DataLen()`, `SetLen()`, `Clone()`, `Highjack()`, `Resize()`, and `Recycle()`. The public constructor creates a one-time buffer from caller-owned aligned storage that will be freed by the buffer object.

## State, dependencies, and integration
The buffer object tracks raw memory, data length, data offset, total size, slot index, and either free-list next pointer or owning pool pointer via a union. It includes `XrdOucChain.hh` and `XrdSysPthread.hh`, though the chain type is not directly used in this header.

## Risks and test signals
Users must call `Recycle()` rather than `delete`, and must not destroy a pool before outstanding buffers return. Since `SetLen()` does not bounds-check, callers can create invalid data windows. Tests should verify documented allocation size limits, one-time buffer caveats, and misuse behavior under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBuffer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC.cc

## Purpose
Implements historical CRC32 plus CRC32C calculation and verification wrappers used throughout XRootD.

## Important APIs and control flow
`CRC32()` computes reflected table-driven CRC-32 with initial and final XORs. `Calc32C(data,count,prevcs)` delegates to `crc32c()` for incremental CRC32C. `Calc32C(data,count,csval)` splits a buffer into `XrdSys::PageSize` pages and writes one CRC32C per full page plus one for a remainder.

`Ver32C()` overloads verify a single checksum, return the first bad page index and computed checksum, fill a boolean per-page success vector, or fill a computed-checksum vector while returning aggregate success. All page-vector variants use page-size segmentation and handle a final partial page.

## State, dependencies, and integration
The file owns the static CRC32 lookup table and depends on `XrdOucCRC32C.hh` for the accelerated CRC32C implementation. CSI page checksum logic and page-read/write utilities depend on these wrappers.

## Risks and test signals
Callers must allocate checksum vectors for the exact number of pages, including a final partial page. The page count uses `int`, so extremely large buffer lengths could overflow on unusual callers. Tests should verify known CRC32 and CRC32C vectors, incremental `prevcs` behavior, page-vector sizing, and mismatch reporting for first and multiple bad pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC.hh

## Purpose
Declares the `XrdOucCRC` static utility class for CRC32 and CRC32C calculation and verification.

## Important APIs and types
`CRC32()` is the legacy CRC-32 entry point. `Calc32C()` has scalar and page-vector overloads; scalar supports incremental continuation via `prevcs`, while vector mode fills one checksum per page. `Ver32C()` overloads verify scalar checksum, identify first failing page, produce per-page booleans, or return computed page checksums.

## State, dependencies, and integration
The class stores a private static `crctable[256]` for legacy CRC32. It depends on `XrdSys::PageSize` for page splitting and `<cstdint>` for fixed-width checksum types.

## Risks and test signals
The API is static and has no synchronization needs beyond the underlying CRC32C implementation. The main contract risk is vector sizing by callers. Unit tests should compile all overloads, check known vectors, and verify final partial-page behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC32C.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC32C.cc

## Purpose
Provides Mark Adler's CRC32C implementation adapted for XRootD C++ builds, with x86_64 SSE4.2 hardware acceleration and portable software fallback.

## Important APIs and control flow
On x86_64, helper functions build GF(2) zero-shift operators and lookup tables so the hardware path can process three independent streams over large `LONG` and `SHORT` blocks, combine them, and then finish aligned eight-byte and trailing byte segments using inline `crc32` assembly. `crc32c()` checks SSE4.2 via `cpuid` on each call and chooses hardware or software. On non-x86_64, it always calls `crc32c_sw()`.

The software path lazily initializes little-endian or big-endian slicing-by-8 tables with `pthread_once`. `crc32c_sw_little()` and `crc32c_sw_big()` pre/post invert CRC state, align to eight bytes, process table-driven words, and finish trailing bytes. The `TEST` block can compile a standalone stdin benchmark/checksum tool.

## State, dependencies, and integration
State consists of static lookup tables and `pthread_once_t` guards. The public functions are declared in `XrdOucCRC32C.hh` and wrapped by `XrdOucCRC`. Dependencies include pthreads, inline assembly, and endian byte swapping.

## Risks and test signals
The x86 `SSE42` macro uses inline asm clobbering `%ebx`, which can be sensitive under PIC/toolchain differences. CPU feature detection occurs every call rather than cached. Tests should compare hardware and software CRCs for known vectors and random buffers, run under non-SSE emulation if possible, and cover unaligned pointers and big-endian builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC32C.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC32C.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC32C.hh

## Purpose
Declares the low-level CRC32C functions used by `XrdOucCRC`.

## Important APIs
`crc32c(uint32_t crc, void const *buf, size_t len)` computes CRC32C over a byte sequence, allowing chunked continuation with the previous return value and requiring the first call use `crc == 0`. It may use Intel hardware instructions when available. `crc32c_sw()` provides the same calculation but forces the software implementation.

## State, dependencies, and integration
The header depends only on `<cstddef>` and `<cstdint>`. It is the narrow C-style API boundary between generic XRootD checksum code and the optimized implementation.

## Risks and test signals
The comments are part of the contract for incremental use; callers passing a nonzero initial CRC that was not produced by a prior call will get a valid continuation but not a standalone checksum. Tests should compare `crc32c()` and `crc32c_sw()` on the same data and verify chunked results equal one-shot results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCRC32C.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCache.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCache.cc

## Purpose
Implements default synchronous helper methods for the cache I/O abstraction.

## Important APIs and control flow
`XrdOucCacheIO::pgRead()` performs a plain `Read()` into the caller buffer, then, when bytes were read and `forceCS` is set, computes page checksums with `XrdOucPgrwUtils::csCalc()` using the file offset and byte count. `pgWrite()` ignores checksum inputs by default and forwards to plain `Write()`.

`ReadV()` iterates each `XrdOucIOVec` segment, calls scalar `Read()`, and requires every segment to return exactly the requested size; a short positive read is converted to `-ESPIPE`, and errors are returned immediately. `WriteV()` mirrors that behavior for scalar `Write()`.

## State, dependencies, and integration
The implementation is stateless. It depends on `XrdOucCache.hh`, `XrdOucPgrwUtils.hh`, `XrdSys::PageSize` indirectly through checksum utilities, and errno constants. Concrete cache/source implementations inherit these defaults unless they provide optimized page or vector I/O.

## Risks and test signals
The default vector methods do not support partial completion semantics; callers get `-ESPIPE` for short reads/writes after earlier segments may have succeeded. `pgWrite()` does not verify or store caller-provided checksums. Tests should exercise force-checksum reads, vector short-read/short-write behavior, negative error propagation, and concrete overrides that need different semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCache.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCache.hh

## Purpose
Defines the public cache plugin and cache-I/O abstraction used to interpose local or remote caches in front of XRootD data sources.

## Important APIs and types
`XrdOucCacheIOCB` is the async completion callback with `Done(int)`. `XrdOucCacheIOCD` reports deferred detach completion. `XrdOucCacheOp::Code` defines file/global fcntl-like query operations.

`XrdOucCacheIO` is the per-file source/cache interface. Required methods include `Detach()`, `FSize()`, `Path()`, scalar `Read()`, `Write()`, `Sync()`, and `Trunc()`. Default methods provide unsupported `Fcntl()`, optional `Fstat()`/`Location()`, page read/write wrappers with checksum vectors, synchronous-as-asynchronous callback wrappers, preread hooks, vector I/O, and `Update()` for deferred open replacement. The protected destructor enforces use of `Detach()` rather than direct delete.

`XrdOucCache` is the cache plugin interface. Required `Attach()` wraps an `XrdOucCacheIO`. Optional methods support global fcntl, local-file-path lookup, prepare/defer open, rename/rmdir/stat/truncate/unlink, special `Xeq()`, statistics, and a short `CacheType`. The typedef `XrdOucCache_t` describes the plugin factory signature.

## State, dependencies, and integration
The header depends on cache stats, I/O vectors, range lists, errno, strings, and vectors. It is consumed by cache implementations such as proxy/file caches and by code that loads `XrdOucGetCache` plugins.

## Risks and test signals
The API mixes sync and async paths; default async callbacks may run inline, so callers holding non-recursive locks can deadlock. Ownership and deferred detach are critical. Tests should validate plugin factory loading, attach failure fallback, inline callback behavior, local path return modes, and stats aggregation from deleted cache I/O objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCache.hh -->
