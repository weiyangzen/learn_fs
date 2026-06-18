# subset-b-007938 research

Grouped research for `subset-b-007938`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcStrmWriter.hh -->
# sources/distributed-fs/xrootd/src/XrdEc/XrdEcStrmWriter.hh

## Purpose

This header declares `XrdEc::StrmWriter`, the asynchronous erasure-coded stream writer used by the XrdEc client layer. It accepts user writes, fills block-sized `WrtBuff` objects, schedules erasure coding and CRC calculation, and drains completed encoded blocks to data and metadata ZIP archives through XrdCl file/zip operations. It is the orchestration layer between the public write/open/close API and lower-level block encoding.

## Important APIs, Types, and Functions

The public API is `StrmWriter(const ObjCfg&)`, `~StrmWriter()`, `Open(ResponseHandler*, time_t)`, `Write(uint32_t, const void*, ResponseHandler*)`, `Close(ResponseHandler*, time_t)`, and `GetSize()`. `ObjCfg` supplies erasure layout and sizes, while user completion is reported through XrdCl `ResponseHandler` callbacks.

`buff_queue` is a `sync_queue<std::future<WrtBuff*>>`. `EnqueueBuff()` sends a raw `WrtBuff` pointer into `ThreadPool::Instance().Execute()` so `WrtBuff::Encode()` runs away from the caller. `DequeueBuff()` waits for the future and reclaims the pointer into a `unique_ptr`. `writer_routine()` is a dedicated consumer thread, and `WriteBuff()`, `GetMetadataBuffer()`, and `CloseImpl()` are the private write/close implementation hooks defined in the companion source.

`global_status_t` tracks outstanding bytes, committed bytes, the first non-OK status, close intent, and the saved close handler. It is protected by a recursive mutex and is shared by open/write/close callback paths.

## Control Flow

Construction starts the writer thread immediately. User `Write()` calls fill the current `WrtBuff`; full buffers are enqueued for background parity/checksum preparation. The writer thread blocks in `DequeueBuff()`, obtains an encoded buffer, and calls `WriteBuff()` to issue writes for the prepared stripes/archives.

Close is two-phase. `Close()` calls `global_status.issue_close()`, which marks that no more writes should arrive. If no bytes remain in flight, it calls `CloseImpl()` immediately; otherwise it saves the close handler and lets `report_wrt()` trigger `CloseImpl()` when outstanding writes reach zero.

Destruction sets `writer_thread_stop`, interrupts the queue, and joins the writer thread, which exits by catching `sync_queue::wait_interrupted`.

## State and Persistence Behavior

Persistent data is external: encoded chunks, metadata archive records, and central directory buffers are written through XrdCl ZIP/file objects. In-memory state includes the active write buffer, `dataarchs`, `metadataarchs`, `cdbuffs`, queued futures, `next_blknb`, and global byte/status counters.

The object keeps a reference to `ObjCfg`, so the configuration must outlive the writer. `global_status.status` retains failure state across callbacks, while `btswritten` is the size reported by `GetSize()`.

## Dependencies and Integration Points

The class depends on `XrdEcWrtBuff.hh`, `XrdEcThreadPool.hh`, `XrdClFileOperations`, `XrdClParallelOperation`, and `XrdClZipOperations`. It integrates with the XrdEc open/write/close implementation in the companion source and with XrdCl's asynchronous callback model.

## Risks and Edge Cases

The close path depends on every asynchronous write eventually calling `report_wrt()` with the same byte accounting used by `issue_write()`. A missed report can hang close; a double report can underflow `btsleft`. `get_btswritten()` is not mutex-protected even though updates are protected. The destructor interrupts the local queue but cannot cancel already running thread-pool encode jobs.

## Test Signals

Useful tests exercise partial-block writes, full-block writes, close while writes are outstanding, write failures before close, destructor during an idle dequeue, and byte-count accounting. Integration tests should verify generated ZIP metadata and data archives are readable by the matching XrdEc reader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcStrmWriter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcThreadPool.hh -->
# sources/distributed-fs/xrootd/src/XrdEc/XrdEcThreadPool.hh

## Purpose

This header implements a singleton thread-pool adapter for XrdEc. It wraps `XrdCl::JobManager` and exposes a C++ future-based `Execute()` API so erasure-coding work and checksum work can be scheduled without exposing XrdCl job objects to callers.

## Important APIs, Types, and Functions

`ThreadPool::Instance()` returns the process-local singleton. `Execute(FUNC, ARGs...)` packages a callable and moveable arguments into an `AnyJob`, queues it on the `JobManager`, and returns `std::future<std::invoke_result_t<FUNC, ARGs...>>`.

The private `sequence`/`seq_gen` templates and `tuple_call()` helpers unpack argument tuples in pre-C++17 style. `AnyJob<FUNC, RET, ARGs...>` derives from `XrdCl::Job`, owns the callable, argument tuple, and promise, and deletes itself at the end of `Run()`.

## Control Flow

The singleton constructor creates `XrdCl::JobManager threadpool(64)`, initializes it, and starts it. `Execute()` allocates a self-owning job, obtains its future before queueing, and passes the job to `QueueJob()`. When an XrdCl worker invokes `Run()`, the job calls the stored function with moved tuple arguments, sets the promise, and deletes itself.

The destructor stops and finalizes the job manager when the singleton is destroyed during process shutdown.

## State and Persistence Behavior

State is in-memory only: one `JobManager` with 64 worker capacity and a collection of queued jobs managed by XrdCl. There is no durable state. Futures are the only result handles returned to callers.

## Dependencies and Integration Points

This adapter is used by `WrtBuff::Encode()` for per-stripe CRC calculation and by `StrmWriter::EnqueueBuff()` for whole-buffer encoding. It depends on XrdCl job manager semantics, including self-deleting `Job` objects.

## Risks and Edge Cases

If the callable throws, `AnyJob::Run()` never catches the exception and the promise may never be fulfilled. `std::promise<void>` is handled by a void overload, but all jobs still rely on successful `set_value()`. The pool size is hard-coded to 64, which may oversubscribe small deployments or underserve high-throughput erasure-coded streams.

## Test Signals

Tests should cover value-returning and void callables, moved-only arguments, concurrent submissions, exception behavior, and shutdown after outstanding work. Integration signals come from XrdEc write throughput and absence of stuck futures during close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcThreadPool.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcUtilities.cc -->
# sources/distributed-fs/xrootd/src/XrdEc/XrdEcUtilities.cc

## Purpose

This source implements XrdEc callback scheduling helpers. It converts immediate status or read-chunk data into XrdCl `Job` instances queued on the default postmaster job manager, preserving asynchronous callback behavior even when the operation completes locally.

## Important APIs, Types, and Functions

`ResponseJob` derives from `XrdCl::Job` and owns a `ResponseHandler*`, heap-allocated `XRootDStatus*`, and optional `AnyObject*`. Its `Run()` calls `HandleResponse()` and deletes the job object.

`ScheduleHandler(uint64_t offset, uint32_t size, void *buffer, ResponseHandler*)` creates a `ChunkInfo`, wraps it in `AnyObject`, and queues a successful response. `ScheduleHandler(ResponseHandler*, const XRootDStatus&)` queues a status-only response.

## Control Flow

Both helpers return immediately when the handler is null. Otherwise they allocate response payloads and queue a `ResponseJob` through `XrdCl::DefaultEnv::GetPostMaster()->GetJobManager()->QueueJob(job)`. XrdCl later invokes the job and the user handler receives ownership according to normal XrdCl callback conventions.

## State and Persistence Behavior

The file has no persistent state. Its only state is temporary heap allocation for status, response objects, chunk metadata, and scheduled jobs.

## Dependencies and Integration Points

The implementation depends on `XrdClJobManager`, `XrdClPostMaster`, and `XrdClDefaultEnv`. It integrates with XrdEc read/write code paths that need to deliver callbacks through the same asynchronous machinery as network operations.

## Risks and Edge Cases

The code assumes `HandleResponse()` or XrdCl response ownership will dispose of `pStatus` and `pResponse`; `ResponseJob` deletes only itself. If callback ownership differs, this leaks. The raw `buffer` pointer in `ChunkInfo` must remain valid under XrdCl's expected callback lifetime. There is no failure path if the default postmaster or job manager is unavailable.

## Test Signals

Tests should verify null-handler no-ops, status propagation, chunk offset/length/buffer propagation, callback execution on the postmaster queue, and memory ownership under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcUtilities.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcUtilities.hh -->
# sources/distributed-fs/xrootd/src/XrdEc/XrdEcUtilities.hh

## Purpose

This header provides shared utility types for XrdEc: stripe descriptors, byte buffers, an exception wrapper for XrdCl status, asynchronous callback scheduling declarations, a blocking interruptible queue, and a filename-to-block helper.

## Important APIs, Types, and Functions

`stripe_t` pairs a stripe buffer pointer with a validity flag, and `stripes_t` is the vector passed to redundancy-code implementations. `buffer_t` aliases `std::vector<char>`.

`IOError` wraps an `XrdCl::XRootDStatus`, exposes `what()` as `ToString()`, and returns the original status through `Status()`. It defines `ioTooManyErrors` as a local error discriminator.

`sync_queue<Element>` provides `enqueue()`, blocking `dequeue()`, nonblocking `dequeue(Element&)`, `empty()`, and `interrupt()`. Blocking dequeue throws `wait_interrupted` after the queue is awakened with the interrupt flag set.

`fntoblk()` parses a block number from the substring between the last two dots of a filename.

## Control Flow

`sync_queue::dequeue()` waits on a condition variable while the queue is empty. `interrupt()` sets an atomic flag and notifies all waiters. Producers move elements into an STL queue and notify waiters; consumers move the front element out.

## State and Persistence Behavior

All state is in memory. `sync_queue` owns queued elements and an interrupt flag. `IOError` copies the status and string message so the exception remains valid after the original status object goes out of scope.

## Dependencies and Integration Points

The header depends on XrdEc object configuration and several XrdCl headers. `sync_queue` is used directly by `StrmWriter` to coordinate futures between user/write threads and the writer thread. `stripe_t` feeds the redundancy plugins configured by `Config::GetRedundancy()`.

## Risks and Edge Cases

`sync_queue::dequeue()` checks `interrupted` only after a condition-variable wake inside the empty loop; if `interrupt()` happens before a thread enters `wait()`, a later blocking `dequeue()` on an empty queue can still wait until another notify. `fntoblk()` assumes the filename contains at least two dots and a numeric middle suffix; malformed names throw from `std::stoul`.

## Test Signals

Useful tests cover FIFO behavior, moving futures or move-only elements, interruption before and during waits, nonblocking empty dequeue, exception message stability, and block-number parsing for normal and malformed XrdEc chunk names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcUtilities.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcWrtBuff.hh -->
# sources/distributed-fs/xrootd/src/XrdEc/XrdEcWrtBuff.hh

## Purpose

This header defines the write-buffer layer for XrdEc. `BufferPool` limits and recycles large XrdCl buffers, while `WrtBuff` accumulates one erasure-coded data block, splits it into stripes, computes parity, and starts CRC32C futures for each stripe.

## Important APIs, Types, and Functions

`BufferPool::Instance()`, `Create(const ObjCfg&)`, and `Recycle(Buffer&&)` manage up to 1024 reusable `XrdCl::Buffer` objects sized from `objcfg.blksize`.

`WrtBuff` exposes `Write()`, `Pad()`, `GetStrpBuff()`, `GetStrpSize()`, `GetBlkSize()`, `Complete()`, `Empty()`, `Encode()`, and `GetCrc32c()`. It stores `ObjCfg`, an `XrdCl::Buffer`, stripe descriptors, and CRC futures.

## Control Flow

Construction obtains a buffer from the singleton pool, reserves stripe capacity, and zeroes the whole buffer. `Write()` copies user data until `objcfg.datasize` is reached. `Pad()` advances over zero-filled bytes, allocating and clearing if needed. `Complete()` reports whether the data area is full.

`Encode()` creates one stripe descriptor per chunk, marks data stripes valid, invokes the configured redundancy implementation to compute parity, and schedules one digest job per stripe through `ThreadPool`. `GetCrc32c()` blocks on the corresponding future.

Destruction recycles the buffer back into the pool.

## State and Persistence Behavior

State is in-memory and block-local. The write cursor determines block size and stripe sizes. The underlying buffer contains data and parity bytes after `Encode()`. No persistent writes happen here; persistence is handled by `StrmWriter`.

## Dependencies and Integration Points

The file depends on `ObjCfg`, `Config`, `ThreadPool`, XrdCl buffers, and `XrdOucCRC32C`. It integrates with `StrmWriter` for buffering and with XrdEc redundancy plugins for parity calculation.

## Risks and Edge Cases

`BufferPool::Create()` ignores the requested `ObjCfg` when reusing a buffer, so mixed object configurations with different block sizes can be unsafe unless all users share sizing. `Pad()` only clears bytes at construction or allocation time and assumes recycled buffers were reset enough. CRC futures are consumed exactly once; repeated `GetCrc32c()` calls on the same stripe would be invalid.

## Test Signals

Tests should verify boundary writes, partial final blocks, stripe-size calculation, parity invocation for data and parity stripes, CRC scheduling, buffer-pool blocking/recycling, mixed-configuration behavior, and destructor recycling under move construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcWrtBuff.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdFfs/CMakeLists.txt

## Purpose

This CMake file builds the XrdFfs shared library and conditionally builds the `xrootdfs` FUSE executable. XrdFfs is the C/C++ support layer that wraps XrdPosix operations, maintains directory/stat/write caches, and supplies the FUSE callbacks used by the mount tool.

## Important APIs, Types, and Functions

`add_library(XrdFfs SHARED ...)` includes the Dent, Fsinfo, Misc, Posix, Queue, and Wcache implementation/header pairs. The library links privately to `XrdCl`, `XrdPosix`, `XrdUtils`, and pthread libraries. `set_target_properties()` applies XRootD's shared-library versioning.

When `ENABLE_FUSE` is true and the system is Linux or kFreeBSD, the script locates FUSE, sets `BUILD_FUSE`, adds `xrootdfs` from `XrdFfsXrootdfs.cc`, links it to `XrdFfs`, `XrdPosix`, FUSE, and pthreads, and installs both library and executable.

## Control Flow

The library is always declared. The executable branch returns early when FUSE is requested but not found without `FORCE_ENABLED`. With `FORCE_ENABLED`, missing FUSE is a configuration error.

## State and Persistence Behavior

The file does not persist runtime state. Build outputs are shared-library and executable artifacts installed under `${CMAKE_INSTALL_LIBDIR}` and `${CMAKE_INSTALL_BINDIR}`.

## Dependencies and Integration Points

This integrates XrdFfs into the larger XRootD build and gates FUSE support by platform and dependency discovery. Consumers link to `XrdFfs`; end users run `xrootdfs`.

## Risks and Edge Cases

FUSE support is excluded on non-Linux/non-kFreeBSD platforms. A missing FUSE package silently skips the executable when not force-enabled, which can surprise users expecting `xrootdfs`. Header files are listed as sources for IDE visibility rather than compilation.

## Test Signals

Build tests should cover `ENABLE_FUSE=ON/OFF`, missing FUSE with and without `FORCE_ENABLED`, install layout, and successful link resolution against XrdCl, XrdPosix, XrdUtils, and pthreads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsDent.cc -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsDent.cc

## Purpose

This file implements directory-entry list utilities and a small global directory-entry cache for XrdFfs. It supports merging directory listings from many data servers, sorting and de-duplicating names, and remembering recent listings so later stat calls can avoid expensive fan-out.

## Important APIs, Types, and Functions

List helpers are `XrdFfsDent_names_add()`, `XrdFfsDent_names_join()`, `XrdFfsDent_names_extract()`, and `XrdFfsDent_names_del()`. They manipulate `XrdFfsDentnames` linked lists and convert them to sorted `char**` arrays with `qsort()`.

Cache helpers are `XrdFfsDent_cache_init()`, `XrdFfsDent_cache_fill()`, `XrdFfsDent_cache_search()`, and `XrdFfsDent_cache_destroy()`. Internal `XrdFfsDentcache` records hold a directory name, sorted entry array, creation time, lifetime, and entry count. There are 20 global cache slots protected by `XrdFfsDentCaches_mutex`.

## Control Flow

Directory fan-out code collects names in per-server lists, joins those lists, then calls `names_extract()` to sort and destroy the linked-list nodes while transferring name ownership to the returned array. `cache_fill()` updates an existing matching slot if present; otherwise it replaces an expired or invalid slot. `cache_search()` checks each slot for either an exact directory path match or a member name inside a cached directory.

## State and Persistence Behavior

All state is process-local. Cache entries duplicate directory and entry strings and expire after `nents / 10` seconds for replacement purposes, while `dentcache_invalid()` treats entries as unusable after about eight hours because redirector memory may expire.

## Dependencies and Integration Points

The cache is used by `XrdFfsPosix_readdirall()` after merged listings and by `XrdFfsPosix_statall()` as a fast path for files known from a directory listing. It exports a C ABI for the FUSE-oriented code.

## Risks and Edge Cases

The path assembly in `dentcache_search()` uses a fixed 1024-byte buffer with `strcpy()`/`strcat()`, so long paths can overflow. Cache lifetime is proportional to entry count, making tiny directories expire immediately. `names_extract()` transfers name pointers to the caller and destroys nodes, so ownership mistakes can double-free or leak names.

## Test Signals

Tests should cover list add/join/extract ordering, duplicate filtering by callers, cache replacement, exact directory hits, member hits, invalidation after time changes, empty directories, long paths, and concurrent cache search/fill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsDent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsDent.hh -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsDent.hh

## Purpose

This header declares the C ABI for XrdFfs directory-entry list and cache helpers. It is intentionally C-compatible so both C-style FUSE code and C++ XrdPosix wrappers can share directory merge logic.

## Important APIs, Types, and Functions

`struct XrdFfsDentnames` is a singly linked node containing a heap-owned name and next pointer. Public functions add, delete, join, and extract names from these lists. Cache functions initialize, fill, search, and destroy the global directory-entry cache.

## Control Flow

Callers build one or more `XrdFfsDentnames` lists with `names_add()`, optionally join them, then call `names_extract()` to obtain a sorted array. Directory listing code can then call `cache_fill()` with that array, and later stat paths can call `cache_search()` with a directory and child name.

## State and Persistence Behavior

The header declares interfaces for process-global cache state implemented in the source file. There is no durable persistence; callers own arrays returned by `names_extract()` and must free each string and the array.

## Dependencies and Integration Points

The header includes C library string/allocation/time headers and pthreads. It is consumed by `XrdFfsPosix.cc`, `XrdFfsMisc.cc`, and the XrdFfs build target.

## Risks and Edge Cases

There are no include guards in this header, so repeated inclusion depends on build behavior and may cause redeclaration problems in stricter contexts. The ABI uses raw `char*` and double pointers, making ownership conventions critical.

## Test Signals

Compile tests should include the header from C and C++ translation units. Runtime tests should pair it with the implementation's list ownership and cache lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsDent.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsFsinfo.cc -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsFsinfo.cc

## Purpose

This file implements a cache for filesystem space information returned through `statvfs`. XrdFfs uses it to avoid repeatedly querying every XRootD data server for OSS quota/free-space attributes during frequent FUSE `statfs` calls.

## Important APIs, Types, and Functions

The public function is `XrdFfsFsinfo_cache_search(func, rdrurl, path, stbuf, user_uid)`. The supplied `func` has the same signature as `XrdFfsPosix_statvfsall()` and is called on cache misses or refreshes.

Internal `XrdFfsFsInfo` stores timestamp, `f_blocks`, `f_bavail`, and `f_bfree`. `XrdFfsFsinfoHtab` is an `XrdOucHash` keyed by an extracted `oss.cgroup=` token or a single-space default key. Separate reader and writer mutexes gate lookup and periodic updates.

## Control Flow

The function tries to take the writer mutex without blocking, then locks the reader mutex and looks up cached data. A hit copies space fields into `stbuf`; a miss calls the real stat function and creates a candidate record. If this caller acquired the writer lock and the record is older than 120 seconds, it refreshes the value, updates timestamp and counters, and stores nonzero-capacity results back into the hash.

## State and Persistence Behavior

The cache is in-memory and keyed by OSS space token rather than full path. Entries persist until process exit and are refreshed every two minutes by whichever caller obtains the writer mutex. Space tokens with zero blocks are not cached.

## Dependencies and Integration Points

The file depends on `statvfs`, pthreads, and `XrdOucHash`. It is called by the FUSE executable's `xrootdfs_statfs()` and delegates actual collection to `XrdFfsPosix_statvfsall()`.

## Risks and Edge Cases

The key extraction uses `strstr(path, "oss.cgroup=")` and keeps everything after the token, including later query data. Miss handling allocates `s` before knowing whether it will be inserted; only some zero-block miss paths free it. The two-mutex scheme allows stale values during refresh and is not a conventional read/write lock.

## Test Signals

Tests should cover default and `oss.cgroup` keys, hit/miss behavior, refresh after 120 seconds, zero-block non-caching, concurrent callers, and propagation of delegate errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsFsinfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsFsinfo.hh -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsFsinfo.hh

## Purpose

This header exposes the C ABI for XrdFfs filesystem-space cache lookup. It lets FUSE code call a cached wrapper around a supplied `statvfs` fan-out implementation.

## Important APIs, Types, and Functions

`XrdFfsFsinfo_cache_search()` accepts a function pointer, redirector URL, path, output `statvfs`, and user uid. The function pointer contract matches `XrdFfsPosix_statvfsall()`.

## Control Flow

Callers initialize the block size fields in `stbuf`, then call this function. The implementation either fills block/free counters from cache or delegates to the supplied function.

## State and Persistence Behavior

The header itself stores no state; the implementation owns a global in-memory hash.

## Dependencies and Integration Points

It includes `sys/statvfs.h` and is consumed by `XrdFfsXrootdfs.cc`.

## Risks and Edge Cases

The header has no include guard and uses `uid_t` without explicitly including `sys/types.h`, relying on transitive platform headers. The function pointer ABI must stay synchronized with `XrdFfsPosix_statvfsall()`.

## Test Signals

Compile tests should include the header standalone where possible. Runtime tests come from the implementation and FUSE `statfs` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsFsinfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsMisc.cc -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsMisc.cc

## Purpose

This file contains miscellaneous XrdFfs runtime support: data-server discovery and caching, process-wide XRootD initialization, syslog setup, worker startup, directory cache initialization, and optional SSS credential identity registration/editing.

## Important APIs, Types, and Functions

URL helpers include `XrdFfsMisc_get_current_url()`, `XrdFfsMisc_get_all_urls_real()`, `XrdFfsMisc_get_all_urls()`, `XrdFfsMisc_refresh_url_cache()`, `XrdFfsMisc_logging_url_cache()`, `XrdFfsMisc_get_list_of_data_servers()`, and `XrdFfsMisc_get_number_of_data_servers()`.

Initialization is handled by `XrdFfsMisc_xrd_init(rdrurl, urlcachelife, startQueue)`, which sets XrdPosix worker threads, optionally initializes SSS security, opens syslog, refreshes/logs data-server URLs, optionally starts queue workers, initializes `url_mlock`, and initializes the directory cache.

SSS helpers are `XrdFfsMisc_xrd_secsss_init()`, `XrdFfsMisc_xrd_secsss_register()`, and `XrdFfsMisc_xrd_secsss_editurl()`. Base-24 conversion helpers generate short user identifiers used in root URLs.

## Control Flow

The data-server cache stores fan-out URLs for one current redirector URL. `get_all_urls()` refreshes the cache when empty, expired, or asked about a different redirector; otherwise it returns duplicated URL strings for the caller to free. Refresh deliberately invalidates the timestamp first, then calls the normal cache getter.

SSS registration converts uid/gid to passwd/group names, rotates a per-user connection id when requested, registers an `XrdSecEntity`, and injects `user@` into root URLs when per-user identity or SSS mode is active.

## State and Persistence Behavior

State is process-global and in-memory: cached redirector URL, cached data-server URLs, cache timestamp/lifetime, worker count through XrdFfsQueue, syslog identity, SSS ID registry, and URL mutexes. No durable files are written here.

## Dependencies and Integration Points

The file integrates with `XrdPosixAdmin::FanOut`, XrdNet address parsing, XrdPosix configuration, XrdSecSSS, XrdFfsDent, XrdFfsQueue, and the FUSE executable. It also feeds data-server lists to `XrdFfsPosix_*all()` fan-out operations.

## Risks and Edge Cases

The URL cache has fixed limits and manual allocation/freeing; negative `FanOut()` results can interact poorly with loops indexed by cached counts. Several buffers use fixed 1024-byte URL limits. `XrdFfsMisc_xrd_init()` is one-time only, so later callers cannot change cache lifetime or queue behavior. `getpwuid_r()`/`getgrgid_r()` results are not validated before dereference.

## Test Signals

Tests should cover cache refresh/expiry, malformed URL handling, data-server list formatting, one-time initialization, SSS URL rewriting with and without link ids, env-driven queue startup, and memory cleanup under repeated refreshes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsMisc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsMisc.hh -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsMisc.hh

## Purpose

This header declares the C ABI for XrdFfs miscellaneous runtime helpers used by the FUSE executable and POSIX fan-out wrappers.

## Important APIs, Types, and Functions

It defines `XrdFfs_MAX_NUM_NODES` as 4096 and declares URL discovery/cache functions, initialization, logging/refresh helpers, data-server count/list helpers, and SSS init/register/edit-url functions.

## Control Flow

Callers typically invoke `XrdFfsMisc_xrd_init()` during FUSE initialization, then use `get_all_urls()` for fan-out operations and `xrd_secsss_register()`/`editurl()` before user-scoped XRootD calls.

## State and Persistence Behavior

All state is owned by the implementation: URL cache, SSS identity state, and queue/directory-cache initialization.

## Dependencies and Integration Points

The declarations are consumed by `XrdFfsXrootdfs.cc` and `XrdFfsPosix.cc`. The C ABI lets C-style FUSE callbacks call C++ XRootD support code.

## Risks and Edge Cases

The header lacks include guards and relies on external includes for `uid_t` and `gid_t`. Public APIs expose raw `char*` buffers and caller-owned allocations, so buffer sizing and freeing are part of the contract but not enforced by types.

## Test Signals

Compile tests should include the header from multiple translation units. Runtime validation comes from URL-cache and SSS behavior in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsMisc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsPosix.cc -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsPosix.cc

## Purpose

This file provides C ABI wrappers around `XrdPosixXrootd` and higher-level operations that fan out metadata mutations and queries across all known data servers. It is the main bridge between FUSE callbacks and XRootD client/file-system operations.

## Important APIs, Types, and Functions

Simple wrappers include `stat`, `opendir`, `readdir`, `closedir`, `mkdir`, `rmdir`, `open`, `close`, `lseek`, `read`, `pread`, `write`, `pwrite`, `fsync`, `unlink`, `rename`, `ftruncate`, `truncate`, and `getxattr`. `stat()` also converts HPSS block-device-looking modes into regular file or directory modes.

Fan-out functions include `XrdFfsPosix_unlinkall()`, `rmdirall()`, `renameall()`, `truncateall()`, `readdirall()`, `statvfsall()`, and `statall()`. Helper worker functions perform one per-server operation and are optionally scheduled through `XrdFfsQueue`.

`XrdFfsPosix_clear_from_rdr_cache()` creates then removes a path to force redirector cache updates after failed creates or renames.

## Control Flow

Mutating fan-out functions fetch data-server URLs from `XrdFfsMisc_get_all_urls()`, append the path, edit URLs for SSS identity, perform each operation in parallel when queues are enabled, then aggregate return codes and errno. Directory listing fan-out gathers `dirent` names from each server, merges/sorts via XrdFfsDent, filters duplicates plus `.lock`/`.fail` companions, caches the result, and returns an array.

`statall()` first tries a redirector stat when the task queue is deep or the directory cache suggests the file exists. Otherwise it stats each data server and returns the first successful result, with timeout handling for down hosts. `statvfsall()` queries XRootD xattrs for total/free/used space and aggregates block counters across servers.

## State and Persistence Behavior

The simple wrappers mutate remote XRootD namespace state. Fan-out functions can delete, rename, truncate, or query files on every cached data server. Local state is temporary arrays of URLs, job handles, per-server errno/result buffers, and directory-cache updates.

## Dependencies and Integration Points

The implementation depends on `XrdPosixXrootd`, XrdCl filesystem/URL APIs, `XrdFfsMisc`, `XrdFfsDent`, and `XrdFfsQueue`. It is consumed by `XrdFfsWcache` and `XrdFfsXrootdfs`.

## Risks and Edge Cases

Several fixed-size URL buffers use manual `strncat()` arithmetic; one `statall()` append uses `MAXROOTURLLEN - strlen(path) - 1` instead of remaining destination space. Fan-out mutations are not atomic across servers, so partial success can leave inconsistent namespace state. `statall()` initializes `max_mtime` inside the loop, so the intended latest-mtime selection does not actually compare across all results. Error aggregation favors early non-ENOENT failures and timeout behavior.

## Test Signals

Tests should cover wrapper errno propagation, xattr subclass parsing, fan-out success/partial failure/down-host handling, directory merge and cache behavior, `statall()` fast path, `.lock`/`.fail` filtering, and non-atomic mutation recovery scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsPosix.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsPosix.hh -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsPosix.hh

## Purpose

This header declares C ABI wrappers for the XRootD POSIX client and the XrdFfs multi-server operations. It is the interface used by the FUSE executable and write/read cache layer.

## Important APIs, Types, and Functions

The first group mirrors POSIX filesystem calls: stat, directory iteration, mkdir/rmdir, open/lseek/read/pread/write/pwrite/close/fsync, unlink/rename/truncate, and getxattr. The second group exposes redirector-cache clearing and fan-out operations over all data servers: unlinkall, rmdirall, renameall, truncateall, readdirall, statvfsall, and statall.

## Control Flow

FUSE callbacks call these wrappers instead of direct libc calls. For ordinary open file descriptors, calls pass through to `XrdPosixXrootd`. Namespace-wide operations use the `*all` variants when `ofs.fwd` behavior is not requested.

## State and Persistence Behavior

The header itself has no state. The implementation mutates remote XRootD namespace and consults global caches from XrdFfsMisc and XrdFfsDent.

## Dependencies and Integration Points

It includes POSIX/FUSE-related system headers and is included by `XrdFfsXrootdfs.cc`, `XrdFfsWcache.cc`, and other XrdFfs utilities.

## Risks and Edge Cases

The header lacks include guards and exposes raw C pointers for arrays such as `char ***direntarray`; callers must understand allocation ownership. Function signatures use platform types such as `off_t`, `uid_t`, and `struct statvfs`, making ABI compatibility dependent on `_FILE_OFFSET_BITS` and platform headers.

## Test Signals

Compile coverage should validate 64-bit offset mode and repeated inclusion. Runtime signals come from wrapper/fan-out tests in the implementation and FUSE mount operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsPosix.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsQueue.cc -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsQueue.cc

## Purpose

This file implements a simple pthread-based work queue used by XrdFfs fan-out operations. It allows operations against many data servers to run concurrently without binding the code to C++ threading abstractions.

## Important APIs, Types, and Functions

Queue APIs are `XrdFfsQueue_create_task()`, `XrdFfsQueue_wait_task()`, `XrdFfsQueue_free_task()`, and `XrdFfsQueue_count_tasks()`. Worker APIs are `XrdFfsQueue_create_workers()`, `XrdFfsQueue_remove_workers()`, `XrdFfsQueue_count_workers()`, and the internal `XrdFfsQueue_worker()`.

Global state includes head/tail task pointers, monotonic task id, task mutex/condition, worker count/id, and worker mutex.

## Control Flow

`create_task()` allocates a task, initializes synchronization, and enqueues it. `dequeue()` blocks on the queue condition until a task exists. Worker threads repeatedly dequeue tasks, execute `task->func(task->args)` unless the task is a sentinel with `done == -1`, mark the task done, signal waiters, and either continue or exit.

`remove_workers()` enqueues one sentinel task per worker to remove and waits for each sentinel to be processed before freeing it.

## State and Persistence Behavior

All state is process-local. Tasks are heap-allocated by callers and must be freed after completion. Workers are detached pthreads with a configured 2 MiB stack.

## Dependencies and Integration Points

The queue is used by `XrdFfsPosix_*all()` fan-out operations and is started by `XrdFfsMisc_xrd_init()` or the FUSE executable init path. It can be compiled out with `NOUSE_QUEUE`.

## Risks and Edge Cases

`XrdFfsQueueWorker_mutex` is declared but not statically initialized in this file, so correctness depends on zero-initialization being accepted for `pthread_mutex_t` on the platform or external initialization. `wait_task()` uses `if` rather than a loop around `pthread_cond_wait()`, so spurious wakeups can return early. Queue length is approximated from task ids and can be off by one or wrong after wrap.

## Test Signals

Tests should cover task ordering, multiple workers, worker removal, sentinel behavior, spurious-wakeup robustness, queue length under empty/single/multiple states, and fan-out integration under high concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsQueue.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsQueue.hh -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsQueue.hh

## Purpose

This header declares the C ABI and task structure for the XrdFfs pthread work queue.

## Important APIs, Types, and Functions

`struct XrdFfsQueueTasks` stores mutex, condition variable, done state, function pointer, argument pointer, id, and linked-list pointers. Public functions create, wait for, free, and count tasks, plus create/remove/count workers.

## Control Flow

Callers submit tasks with a function pointer and argument pointer, wait for completion when needed, then free the task. The worker pool processes tasks asynchronously.

## State and Persistence Behavior

The header stores no state but exposes the task layout used by the source file's global queue.

## Dependencies and Integration Points

It includes pthreads and is consumed by `XrdFfsMisc.cc`, `XrdFfsPosix.cc`, and `XrdFfsXrootdfs.cc`.

## Risks and Edge Cases

The function pointer signature uses `void **args`, while several callers cast addresses through `void**`; this is type-unsafe and can hide ABI mistakes. No include guard is present.

## Test Signals

Compile tests should catch strict-pointer warnings. Runtime tests should validate create/wait/free ownership and worker lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsQueue.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsWcache.cc -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsWcache.cc

## Purpose

This file implements a per-file-descriptor cache used by XrootdFS. It batches consecutive small writes into larger `pwrite()` calls and, for a restricted direct-I/O read case, caches one read block to improve erasure-coded or remote read performance.

## Important APIs, Types, and Functions

`XrdFfsWcache_init(basefd, maxfd)` initializes the descriptor table and cache sizing. `XrdFfsWcache_create(fd, flags)` allocates a buffer and mutex for a descriptor. `destroy()`, `flush()`, `pread()`, and `pwrite()` manage descriptor-local cache contents.

`XrdFfsWcacheFilebuf` stores cached offset, length, buffer pointer, buffer size, and mutex pointer. Global state includes base virtual fd, maximum fd count, cache buffer array, write buffer size, and read-cache buffer size.

## Control Flow

Initialization sizes read cache to 128 KiB by default, to the EC data-block size when `XRDCL_EC` is set, or to `XROOTDFS_WCACHESZ` when present. `create()` allocates either read-cache or write-cache sized buffers depending on open flags.

`pwrite()` bypasses the cache for large writes or out-of-range descriptors. Small consecutive writes append to the descriptor buffer. Non-consecutive writes or buffer overflow force `flush()`, which calls `XrdFfsPosix_pwrite()` and clears the cache on success. `pread()` loads the block containing the requested offset and serves bytes from cache when possible.

## State and Persistence Behavior

Cached data is process-local and per virtual fd. Remote persistence only happens on `flush()`, direct bypass writes, `fsync()`, `ftruncate()`, or release paths that explicitly flush. Destroy does not call flush, so callers must flush first.

## Dependencies and Integration Points

The implementation depends on XrdFfsPosix for actual I/O and is used by `xrootdfs_open()`, `create()`, `read()`, `write()`, `fsync()`, `ftruncate()`, and `release()`.

## Risks and Edge Cases

`XROOTDFS_WCACHESZ` assigns to `XrdFfsRcacheBufsize`, not the write-cache size, despite the name. `create()` can leak the first allocation if mutex allocation fails. Descriptor bounds are checked after subtracting base fd in some paths but not consistently before table access. Destroying without flush loses buffered writes.

## Test Signals

Tests should cover consecutive small-write coalescing, flush on gaps/overflow, direct large write bypass, release/fsync/ftruncate flush behavior, direct-I/O read cache hits/misses, fd bounds, environment sizing, and failure cleanup under allocation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsWcache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsWcache.hh -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsWcache.hh

## Purpose

This header declares the C ABI for XrdFfs per-file-descriptor read/write caching.

## Important APIs, Types, and Functions

The public API is `XrdFfsWcache_init()`, `create()`, `destroy()`, `flush()`, `pread()`, and `pwrite()`. These calls wrap descriptor-local cache allocation, invalidation, flushing, and cached I/O.

## Control Flow

FUSE open/create calls initialize a descriptor cache. Reads and writes route through cached pread/pwrite when appropriate. Fsync, truncate, and release call flush before remote synchronization or close.

## State and Persistence Behavior

The header has no state; the implementation owns the global descriptor table. Buffered writes are not durable until flushed.

## Dependencies and Integration Points

It is consumed by `XrdFfsXrootdfs.cc` and implemented by `XrdFfsWcache.cc`.

## Risks and Edge Cases

No include guard is present, and the header uses `ssize_t`, `size_t`, and `off_t` without including their defining system headers. Callers must pass XrdPosix virtual descriptors in the same range configured by `init()`.

## Test Signals

Compile tests should include standalone header checks. Runtime signals come from implementation and FUSE open/read/write/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsWcache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsXrootdfs.cc -->
# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsXrootdfs.cc

## Purpose

This file implements the `xrootdfs` FUSE executable, presenting an XRootD storage cluster as a mounted filesystem. It wires FUSE callbacks to XrdFfs POSIX wrappers, data-server fan-out, write/read cache behavior, optional CNS shadow namespace updates, and optional SSS user identity handling.

## Important APIs, Types, and Functions

`struct XROOTDFS` stores command/environment options: redirector URL, CNS URL, fast stat mode, daemon uid, SSS keytab, URL cache lifetime, `ofs.fwd` behavior, worker count, and max virtual fd count. `xrootdfs_oper` maps FUSE operations to local static functions.

Important callbacks include `init`, `getattr`, `readdir`, `mknod`, `create`, `mkdir`, `unlink`, `rmdir`, `rename`, `truncate`, `open`, `read`, `write`, `statfs`, `release`, `fsync`, `setxattr`, and `getxattr`. `main()` parses FUSE and XrootdFS options, applies defaults, converts `xroot://` to `root://`, configures SSS env, installs SIGUSR1 handling, and calls `fuse_main()`.

## Control Flow

Initialization optionally drops privileges, creates `XrdPosixXrootd` with negative maxfd, initializes XrdFfs runtime, initializes Wcache with the virtual fd origin, derives `XRDEXPORTS`, starts worker threads, and restores the original working directory.

Per-operation control flow registers the calling FUSE uid/gid with SSS, constructs root URLs from redirector or CNS plus path, edits URLs for user identity, then calls XrdFfsPosix or Wcache functions. Metadata operations use CNS when configured and may use redirector/data-server fan-out depending on `ofsfwd`. File release flushes and destroys the cache, closes the data fd, and optionally updates CNS shadow file size/token metadata.

Operational controls are exposed through xattrs: refreshing/logging data servers and adjusting worker count. SIGUSR1 refreshes/logs the data-server cache in a detached thread.

## State and Persistence Behavior

Process state includes parsed mount options, worker pool, URL caches, directory/stat caches, SSS registrations, and Wcache descriptors. Persistent effects are remote XRootD file/namespace mutations, optional CNS shadow files, and syslog messages. FUSE cache timeouts differ for EC mode by setting entry timeout to zero.

## Dependencies and Integration Points

The executable depends on FUSE 2.6 API, XrdFfsPosix, XrdFfsMisc, XrdFfsWcache, XrdFfsQueue, XrdFfsFsinfo, and XrdPosixXrootd. It integrates with environment variables such as `XROOTDFS_RDRURL`, `XROOTDFS_CNSURL`, `XROOTDFS_FASTLS`, `XROOTDFS_USER`, `XROOTDFS_OFSFWD`, `XROOTDFS_NWORKERS`, `XROOTDFS_MAXFD`, `XROOTDFS_NO_ALLOW_OTHER`, and `XRDCL_EC`.

## Risks and Edge Cases

Many URL buffers are fixed 1024-byte arrays assembled by `strncat()`. `xrootdfs_init()` builds `exportpath` without initializing it before `strcat()`. `xrootdfs_readdir()` returns `-errno` after a successful fan-out listing, so stale errno can affect success. Several callbacks intentionally no-op permission/time/link operations, which may surprise POSIX applications. Shadow CNS updates are best-effort and can diverge from data files.

## Test Signals

Tests should cover mount option parsing, environment defaults, create/open/write/read/release flows, CNS and non-CNS metadata behavior, EC mode read bounds and FUSE timeouts, xattr controls, SIGUSR1 refresh, SSS URL rewriting, and error propagation through FUSE negative errno returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsXrootdfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdFrc/CMakeLists.txt

## Purpose

This CMake file adds the File Residency Manager client sources to the `XrdServer` target. XrdFrc supplies request-queue, proxy, cluster-id, tracing, utility, xattr, and locking support for file residency/prestage/migration workflows.

## Important APIs, Types, and Functions

`target_sources(XrdServer PRIVATE ...)` lists CID, Proxy, ReqAgent, ReqFile, Trace, Utils, Request, XAttr, and XLock files. There is no independent library or executable in this file.

## Control Flow

During configuration/generation, these files become private sources of `XrdServer`. Build order and linkage are inherited from the server target.

## State and Persistence Behavior

No runtime state is stored by the build file. It controls whether XrdFrc queue/checkpoint code is compiled into `XrdServer`.

## Dependencies and Integration Points

The file integrates XrdFrc with the server build rather than exposing it as a standalone target. Source-level dependencies include XrdOuc, XrdSys, XrdNet, and request queue files.

## Risks and Edge Cases

Because all listed files are private server sources, external consumers cannot link a separate XrdFrc component. Missing a source here can produce unresolved symbols only when related server code is enabled.

## Test Signals

Build tests should verify `XrdServer` compiles and links with all XrdFrc sources and that installation/runtime configurations exercising FRM client features resolve the included symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcCID.cc -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcCID.cc

## Purpose

This file implements `XrdFrcCID`, a checkpointed in-memory map from XRootD instance names to cluster names and associated process metadata. It supports FRM client registration and lets request queues preserve cluster identity across restarts.

## Important APIs, Types, and Functions

The global instance is `XrdFrc::CID`. Public methods are `Add()`, `Get(iName, buff, blen)`, `Get(iName, vName, env)`, `Init(aPath)`, and `Ref(iName)`. Private methods are `Find()`, stream-record `Init()`, and `Update()`.

`cidEnt` stores linked-list pointers, instance name, cluster name, add timestamp, pid, use count, and cached string lengths. `cidMon` wraps a static mutex for all CID operations.

## Control Flow

`Init(aPath)` opens the `CIDS` checkpoint file, reads records of `<iname> <cname> <addt> <pid>`, validates timestamp and pid, clears dead pids, and reconstructs the linked list. `Add()` inserts new entries or updates existing entries only when the incoming timestamp is newer. `Update()` writes live/default/referenced entries to `CIDS.new` under a file lock, removes dead unused non-`anon` entries, then renames the temp file to `CIDS`.

`Get()` returns the matching cluster or default `anon` entry when the instance name is empty. `Ref()` marks an entry as used so request-file recovery can prevent cleanup of known instance names.

## State and Persistence Behavior

State is a process-local linked list plus two checkpoint paths, `CIDS` and `CIDS.new`. Persistence is atomic-by-rename after rewriting the full checkpoint file under `fcntl` write lock. Entries with dead pids and no use count are pruned during updates.

## Dependencies and Integration Points

The implementation depends on XrdFrc tracing, XrdOuc streams/environments, XrdSys errors/file descriptors/platform wrappers, POSIX file locking, `writev()`, and `kill(pid, 0)` for liveness checks. `XrdFrcReqFile::Init()` calls `CID.Ref()` for recovered request instance names.

## Risks and Edge Cases

`Init(aPath)` uses fixed 1024-byte path assembly with `strcpy()`. `Update()` uses static iovec buffers, relying on the outer mutex for thread safety. Persistence failures are logged but `Add()` still mutates memory before `Update()` failures. Dead pid detection treats permission errors as alive.

## Test Signals

Tests should cover checkpoint recovery, newer/older update ordering, default `anon` behavior, environment injection, dead-pid pruning, `Ref()` preservation, corrupt records, and atomic rename failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcCID.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcCID.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcCID.hh

## Purpose

This header declares `XrdFrcCID`, the File Residency Manager cluster-id registry, and the global `XrdFrc::CID` instance.

## Important APIs, Types, and Functions

Public methods add cluster identity records, retrieve cluster names into buffers or `XrdOucEnv`, initialize from a queue path, and mark instance names referenced. Private `cidEnt` nodes hold identity data and `cidMon` serializes access with a static `XrdSysMutex`.

## Control Flow

Callers initialize the registry from a checkpoint directory, then add registrations as FRM clients appear and query cluster names when composing request environment or recovering queue state.

## State and Persistence Behavior

The class stores a linked list, default entry pointer, and checkpoint filenames. The source implementation persists to `CIDS` files under the queue path.

## Dependencies and Integration Points

It depends on XrdSys pthread mutex wrappers and forward-declares `XrdOucEnv`/`XrdOucStream`. It is used by request-file recovery and FRM registration paths.

## Risks and Edge Cases

The destructor does not free linked-list entries or filename strings, so the object is effectively process-lifetime. Copy/move operations are not explicitly disabled. The registry exposes raw C-string buffers for callers to size correctly.

## Test Signals

Header-level tests should cover inclusion and API use with forward declarations. Behavior tests live in the source implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcCID.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcProxy.cc -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcProxy.cc

## Purpose

This file implements `XrdFrcProxy`, the client-facing proxy that maps FRM operations into persistent request queues. It validates request fields, initializes queue agents, supports cancellation, and lists pending work.

## Important APIs, Types, and Functions

The operation-to-queue table maps `getf`, `migr`, `pstg`, and `putf` names to `XrdFrcRequest` queue ids and public operation flags. Public methods are `Add()`, `Del()`, `List(Queues&, char*, int)`, `List(qType, qPrty, Items, Num)`, and `Init()`.

`Init2()` parses the active XRootD configuration for `frm.xfr.qcheck` to discover a queue path, and `qChk()` validates/extracts that path.

## Control Flow

Construction wires logging, enables tracing when requested, derives public and internal instance names, and clears agent pointers. `Init()` determines a queue path from explicit argument, config, or default path, creates queue directories, then starts an `XrdFrcReqAgent` for each requested operation type.

`Add()` maps the request opcode to a queue, checks support, packs `XrdFrcRequest` fields, appends optional opaque data after the LFN with `Opaque` offset, validates URL or absolute path layout, fills user/id/notify/priority/options, and calls the queue agent. `Del()` maps opcode and asks the agent to cancel by request id. `List()` walks queue types and priorities incrementally.

## State and Persistence Behavior

Proxy state is in memory: one agent pointer per queue, instance names, and queue path. Persistent request records are written by `XrdFrcReqAgent`/`XrdFrcReqFile` into queue files. Configuration-derived queue path is copied into `QPath`.

## Dependencies and Integration Points

The implementation depends on `XrdFrcReqAgent`, `XrdFrcUtils`, request types, XrdOuc config streams/utilities, XrdSys logging/platform, and FRM trace facilities. It is a bridge between server/client command handling and on-disk FRM queues.

## Risks and Edge Cases

`Add()` indexes `Agent[qType]` after `MapR2Q()` without an explicit bounds check, relying on utility correctness. Opaque data is packed into `LFN` with embedded NUL separation, so all consumers must honor `Opaque`. `Init2()` only captures the qcheck path if the config directive is present and valid.

## Test Signals

Tests should cover each opcode mapping, unsupported queues, LFN length and URL validation, opaque packing, default user/id/notify values, priority clamping in the agent, config qcheck parsing, and listing across queue types/priorities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcProxy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcProxy.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcProxy.hh

## Purpose

This header declares the FRM request proxy class. It exposes a compact API for adding, deleting, listing, and initializing file-residency queues without exposing request-file implementation details.

## Important APIs, Types, and Functions

`XrdFrcProxy::Add()` creates a request; `Del()` cancels by request id; the two `List()` overloads stream pending LFNs or structured item fields; `Init()` creates queue agents. Operation masks `opGet`, `opPut`, `opMig`, `opStg`, and `opAll` select supported queues.

Nested `Queues` holds incremental list state: offset, priority, queue list mask, current queue, and active flag.

## Control Flow

Users construct a proxy with logger, instance name, and optional debug flag, initialize it for desired operation masks, then call add/delete/list. Listing with `Queues` can resume across calls.

## State and Persistence Behavior

The class stores pointers to `XrdFrcReqAgent` instances and queue path/instance strings. Persistent state is delegated to request agents/files.

## Dependencies and Integration Points

The header includes `XrdFrcRequest.hh` and forward-declares agents, streams, and loggers. It is part of the XrdServer private source set.

## Risks and Edge Cases

The destructor does not delete allocated agents or strings, implying process-lifetime ownership. `Queues` internals are friend-accessed by the proxy and initialized only through its constructor.

## Test Signals

Tests should compile users of the public API and exercise lifecycle through the source implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcProxy.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqAgent.cc -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqAgent.cc

## Purpose

This file implements `XrdFrcReqAgent`, a per-operation manager for priority request files. It completes request metadata, writes requests to the correct priority queue, cancels requests, lists queue contents, and pings the FRM transfer daemon through a UDP path.

## Important APIs, Types, and Functions

Public methods are `Add()`, `Del()`, `List()`, `NextLFN()`, `Ping()`, and `Start()`. `c2sFN` is a static client-to-server UDP filename initialized once per process.

The constructor chooses a default ping message based on queue type: get, migrate, prestage, put, or generic. `Start()` creates one `XrdFrcReqFile` per priority and optionally inserts registration requests when `XRDCMSCLUSTERID` is set.

## Control Flow

`Add()` clamps priority, sets `addTOD`, copies the instance name, writes to the matching priority `XrdFrcReqFile`, and pings the transfer daemon. `Del()` calls `Can()` on all priority queues for the request id. List methods scan request files and either print LFNs or return one next LFN for streaming proxy listing.

`Ping()` lazily validates the UDP path with `stat()` and sends either the queue-specific ping or an override message through `XrdNetMsg`. `Start()` creates the shared UDP path string, resolves instance name, creates queue directory path, initializes all priority files, and pings if registration records were added.

## State and Persistence Behavior

Agent state is process-local, but queue records are persistent files managed by `XrdFrcReqFile`. Registration records are inserted into every priority queue when cluster id is configured. UDP ping state is cached through static `udpOK`.

## Dependencies and Integration Points

The implementation depends on request files, request structs, FRM utilities, XrdNet UDP messaging, XrdOuc instance names, XrdSys platform headers, and the transfer daemon's `xfrd.udp` control path.

## Risks and Edge Cases

`Ping()` uses static `XrdNetMsg` and `udpOK` shared across all agents, so the first `c2sFN` path dominates. `List()` writes LFNs to `std::cout` while also returning counts, which can be surprising for library callers. If initialization fails after some priority queues are created, earlier allocations are not cleaned up.

## Test Signals

Tests should cover priority clamping, metadata completion, queue file creation per priority, cancellation across priorities, list item formatting, registration insertion from `XRDCMSCLUSTERID`, UDP ping path absence/presence, and start failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqAgent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqAgent.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqAgent.hh

## Purpose

This header declares `XrdFrcReqAgent`, the manager for one FRM operation queue family and its priority request files.

## Important APIs, Types, and Functions

The class exposes `Add`, `Del`, two `List` overloads, `NextLFN`, `Ping`, and `Start`. It stores an array of `XrdFrcReqFile*` indexed by priority, queue persona/name, default ping message, instance name, and queue id. Static `c2sFN` stores the transfer daemon UDP path.

## Control Flow

An agent is constructed for an operation type, started with a queue path/mode, then receives add/delete/list calls from `XrdFrcProxy`.

## State and Persistence Behavior

Priority request files persist queued work. The agent's in-memory state owns pointers to those files for process lifetime.

## Dependencies and Integration Points

The header includes `XrdFrcReqFile.hh` and `XrdFrcRequest.hh`. It is consumed by the proxy and compiled into `XrdServer`.

## Risks and Edge Cases

The destructor does not delete request-file pointers. Copy/move are not disabled, so accidental copies would duplicate raw pointers. Callers must call `Start()` before `Add()` to initialize `rQueue`.

## Test Signals

Tests should validate lifecycle assumptions and null/unstarted behavior through implementation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqAgent.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqFile.cc -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqFile.cc

## Purpose

This file implements the persistent request-file queue used by FRM agents and consumers. It stores fixed-size `XrdFrcRequest` records in a file with a small header, supports append, cancellation, pop, listing, recovery/compaction, and cross-process file locking.

## Important APIs, Types, and Functions

Public methods are `Add()`, `Can()`, `Del()`, `Get()`, `Init()`, `List()`, and `ListL()`. Private helpers include `FileLock()`, `reqRead()`, `reqWrite()`, `ReWrite()`, and failure logging helpers.

`FileHdr` stores offsets for first, last, and free-chain records. `recEnt` is an in-memory recovery list node. `rqMonitor` serializes in-process agent access with a static mutex, while `FileLock()` uses a `.lock` file and `fcntl` locks for interprocess serialization.

## Control Flow

`Init()` opens/locks the lock file, opens/creates the request file, initializes a new file when shorter than one request record, or, for consumer mode, reads all valid records, sorts normal requests by `addTOD`, places registration requests at the front, rewrites a compacted queue file, and references recovered instance names in `CID`.

`Add()` locks the file, obtains either a free-chain slot or appends at EOF, links the new record to the tail unless it is a registration request, writes the record and header, and unlocks. `Can()` scans all records and clears matching request ids by setting empty LFN. `Get()` pops the first valid request, skipping empty canceled records and adding them to the free chain. `Del()` places a known record offset onto the free chain. `List()` scans fixed-size records with a shared lock and formats requested items with `ListL()`.

## State and Persistence Behavior

The request file persists a header at offset zero and fixed-size request records after it. Deleted/canceled entries are represented by empty LFNs and/or free-chain links. Writes update the header and fsync by default. `ReWrite()` compacts through a `.new` file and rename. Agent mode opens/closes the request file around locks; consumer mode keeps it open.

## Dependencies and Integration Points

The implementation depends on `XrdFrcRequest`, `XrdFrcCID`, XrdFrc tracing, XrdSys file/error/platform wrappers, POSIX `pread/pwrite/fcntl/fsync/rename`, and `XrdFrcReqAgent`.

## Risks and Edge Cases

`reqRead()` treats short reads as success because it only checks `rc < 0`. `Can()` clears matching records without repairing linked-list pointers, leaving canceled entries for `Get()` to skip later. `FileLock(lkNone)` closes `reqFD` in agent mode, so callers must not use stale descriptors after unlock. Fixed-size binary record layout is ABI-sensitive.

## Test Signals

Tests should cover new-file initialization, append order, registration FIFO/front behavior, free-chain reuse, cancellation by id, pop semantics and return codes, listing item formats, recovery sorting/compaction, lock behavior across processes, short read/write failures, and fsync/rename failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqFile.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqFile.hh

## Purpose

This header declares `XrdFrcReqFile`, the fixed-record persistent queue file abstraction used by FRM request agents and workers.

## Important APIs, Types, and Functions

Public operations add, cancel, delete/free, get/pop, initialize, list, and format request records. Private state includes lock and request filenames/descriptors, header data, agent-mode flag, file mutex, lock type enum, and recovery list node type.

`FileHdr` records first, last, and free-chain offsets. `rqMonitor` wraps a static mutex used when the object is in agent mode.

## Control Flow

Agents create one request file per operation priority, call `Init()`, then `Add()`/`Can()`/`List()`. Consumers can call `Get()` and `Del()` to pop and free records.

## State and Persistence Behavior

Persistent state lives in the request file and companion lock file. In-memory state caches header fields and descriptor/fname ownership.

## Dependencies and Integration Points

It includes `XrdFrcRequest.hh` and XrdSys mutex wrappers. It integrates with `XrdFrcReqAgent` and `XrdFrcCID` recovery logic.

## Risks and Edge Cases

The destructor does not close file descriptors or free filename strings, so objects are expected to live for process duration. The binary record format is tied to `sizeof(XrdFrcRequest)`. Copy/move operations are not disabled despite raw ownership.

## Test Signals

Tests should exercise lifecycle through the implementation, with special focus on persistent format compatibility and lock-file behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcReqFile.hh -->
