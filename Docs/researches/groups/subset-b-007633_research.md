# Research: subset-b-007633

Grouped research for the LizardFS mount/master communication, special inode, read-cache, polonaise server, and related helper files. Each section preserves the source path in its title and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/mastercomm.cc -->
## sources/distributed-fs/lizardfs/src/mount/mastercomm.cc

Purpose: implements the mount client's primary control-plane connection to the LizardFS master. It owns master address/session state, registration and reconnection, per-thread request records, request/response matching, periodic keepalive and reserved-inode reporting, and the exported `fs_*` wrappers used by the FUSE/client layer for metadata, chunks, xattrs, ACLs, locks, snapshots, goals, and custom master packets.

Important APIs and types: internal `threc` stores a calling thread's packet id, output/input buffers, status flags, and condition variable. `acquired_file` tracks open/reserved inodes reported to the master. Public functions include `fs_init_master_connection`, `fs_init_threads`, `fs_term`, `fs_getmasterlocation`, `fs_access`, `fs_lookup`, `fs_getattr`, `fs_setattr`, `fs_truncate`, namespace operations, `fs_readchunk`/`fs_lizreadchunk`, `fs_lizwritechunk`, xattr and ACL calls, lock send/recv pairs, `fs_custom`, and packet handler registration.

Control flow: initialization records `LizardClient::FsInitParams`, resolves/binds/connects TCP, performs optional password challenge using MD5, sends `CLTOMA_FUSE_REGISTER`, and parses session flags/version. After fork, `fs_receive_thread` continuously reconnects, reads packet headers/payloads, dispatches registered async packet handlers, extracts message ids, and wakes the matching `threc`. `fs_nop_thread` sends NOPs and periodically reports acquired inode ids. Each RPC builds an old MooseFS packet with `fs_createpacket` or a generated LizardFS protocol buffer with `cltoma::*`, flushes it under `fdMutex`, waits on the per-thread condition, validates response type/version/length, and returns a LizardFS status byte.

State and persistence: all state is process memory: TCP fd, session id, master version, init params, per-thread records, acquired inode list, stats counters, reconnect flags, and custom handlers. No disk persistence occurs; master sessions are re-established by reconnect or full registration. Password digests can be zeroed after registration when configured.

Dependencies and integration: depends on `common/sockets`, `datapack`, `md5`, `slogger`, `stats`, `exports`, and generated protocol namespaces `cltoma`/`matocl`. It is called heavily by `lizard_client`, read/write paths, `masterproxy`, and special inode masterinfo. It exports stats under the `master.*` tree and calls `LizardClient::masterDisconnectedCallback()` on disconnect.

Risks: retrying arbitrary requests after send/receive failure is explicitly noted as unsafe for some operations such as snapshots. The module mixes raw pointer/list management, multiple mutexes, and condition-variable ownership; message id corruption or response length/version mistakes force disconnects. `msgIdPtr` casts into vector storage for in-place id rewrites and depends on packet layout. Many wrappers assume returned buffers remain valid until the next request on the same `threc`. Long-lived global state makes test isolation difficult.

Test signals: no direct unit test in this subset. Coverage is mostly integration-level through FUSE/client operations and protocol compatibility. Key test targets are reconnect/session-loss behavior, versioned response parsing, old/new packet interoperability, xattr/ACL capability gates by master version, and custom packet proxying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/mastercomm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/mastercomm.h -->
## sources/distributed-fs/lizardfs/src/mount/mastercomm.h

Purpose: declares the mount client's master communication API. It is the narrow public surface for metadata RPCs, chunk location/write-end RPCs, xattrs, ACLs, trash/reserved meta operations, locks, snapshots, goal management, custom packet forwarding, lifecycle initialization, and async packet handlers.

Important APIs and types: declares dozens of `uint8_t fs_*` status-returning functions plus `fs_statfs`, `fs_getmasterlocation`, `fs_getsrcip`, `fs_notify_sendremoved`, lifecycle functions, and `PacketHandler` with virtual `handle(MessageBuffer)`. It exposes overloads for legacy byte-buffer directory/trash listings and newer vector forms (`DirectoryEntry`, `NamedInodeEntry`, `ChunkTypeWithAddress`, `ChunkserverListEntry`).

Control flow and integration: callers create no object; they call global functions backed by process-wide state in `mastercomm.cc`. FUSE/client code uses these functions synchronously, while lock interruption and packet handlers support asynchronous interactions. `masterproxy` uses `fs_custom` to forward arbitrary master packets.

State and persistence: header owns no state but its API implies per-process master connection state and per-thread request matching. Returned `const uint8_t **` buffers are owned by the communication layer and should be treated as transient.

Dependencies: includes ACL, attributes, chunk address, group cache, `LizardClient`, packet, lock, directory, and named inode protocol types. This makes the header a central coupling point between mount and common/protocol code.

Risks and tests: broad C-style global API increases coupling and makes lifetime rules easy to misuse. Separate send/recv lock APIs require callers to pair calls correctly. There are no direct tests here; interface changes require broad compile and integration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/mastercomm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/masterproxy.cc -->
## sources/distributed-fs/lizardfs/src/mount/masterproxy.cc

Purpose: provides a local TCP proxy endpoint for tools that need to talk to the master through the mounted client. It listens on loopback, exposes its location via the `masterinfo` special file for sufficiently new masters, and forwards most packets through `fs_custom`.

Important APIs: `masterproxy_init` creates a nonblocking loopback listener on an ephemeral port and starts an acceptor thread. `masterproxy_getlocation` overwrites master host/port in a 14-byte masterinfo buffer when proxying is available and master version is at least 1.6.24. `masterproxy_term` stops the acceptor. Worker routines are `masterproxy_acceptor` and `masterproxy_server`.

Control flow: accepted client sockets get detached threads. Each server thread reads a packet header and payload, handles `CLTOMA_FUSE_REGISTER` for tools locally by validating the register blob and returning OK, otherwise calls `fs_custom` to rewrite the message id, send to master, receive a response, restore the original id, and write it back to the local client.

State and dependencies: global listener fd, proxy thread, terminate flag, proxy host/port. Uses `common/sockets`, packet serialization, `MFSCommunication`, and `mastercomm`.

Risks: each connection creates a detached pthread, so resource exhaustion is possible under local abuse. Reads and writes use 1-second timeouts and close on partial IO. Protocol validation is minimal outside the register special case. `terminate` is a plain byte read by another thread.

Test signals: best verified by opening `masterinfo`, connecting to advertised loopback location, performing tool registration, forwarding a known packet, and checking shutdown joins the acceptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/masterproxy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/masterproxy.h -->
## sources/distributed-fs/lizardfs/src/mount/masterproxy.h

Purpose: declares the three-function API for the local master proxy: initialize, terminate, and rewrite masterinfo location.

Important APIs: `masterproxy_getlocation(uint8_t *masterinfo)` mutates the serialized masterinfo buffer in place; `masterproxy_init()` returns positive success or negative failure; `masterproxy_term()` stops the proxy thread.

Integration: used by special inode reads for `MASTERINFO` and initialized/terminated by the mount/client lifecycle when proxy support is enabled.

Risks and tests: the in-place 14-byte buffer contract is implicit and must match `fs_getmasterlocation`. Tests should validate that proxy location is not advertised before successful init or for older master versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/masterproxy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/oplog.cc -->
## sources/distributed-fs/lizardfs/src/mount/oplog.cc

Purpose: implements an in-memory operation log backing special files for live operation log and operation history. It stores formatted log lines in a fixed-size circular buffer and lets readers hold handles with independent read positions.

Important APIs/types: `fhentry` tracks handle id, read position, refcount, and next link. `oplog_printf` overloads prepend timestamps and optional Lizard client uid/gid/pid context, then append to the ring via `oplog_put`. `oplog_newhandle`, `oplog_releasehandle`, `oplog_getdata`, and `oplog_releasedata` manage reader cursors.

Control flow: log writes lock `opbufflock`, wrap-copy into `opbuff`, advance `writepos`, and broadcast waiters. New history handles start either at zero or near `writepos - MAXHISTORYSIZE` aligned to the next newline; live handles start at current `writepos`. Reads find the handle, increment refcount, block up to one second for new data, return either a contiguous ring slice or `"#\n"` heartbeat, and intentionally leave `opbufflock` held until `oplog_releasedata`.

State and persistence: all log data is volatile process memory. The ring is 16 MiB with history capped at about 15 MiB. Time conversion caches localtime for the current hour under a separate mutex.

Dependencies and integration: special inode open/read/release uses handles for `OPLOG` and `OPHISTORY`; many mount operations call `oplog_printf`. Uses pthread primitives and `LizardClient::Context`.

Risks: callers must always call `oplog_releasedata` after `oplog_getdata` because the mutex remains locked. If a handle is invalid in `oplog_getdata`, the function returns without unlocking, which is a latent deadlock path if reachable. Returned buffers point into the ring and are valid only while the lock is held.

Test signals: no direct unit tests here. Important tests are concurrent writers/readers, history truncation alignment, timeout heartbeat, and invalid-handle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/oplog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/oplog.h -->
## sources/distributed-fs/lizardfs/src/mount/oplog.h

Purpose: declares the operation-log formatting and handle API used by special inode files and mount operation tracing.

Important APIs: `oplog_printf` overloads carry GCC printf-format attributes when available; `oplog_newhandle`, `oplog_releasehandle`, `oplog_getdata`, and `oplog_releasedata` implement streaming reads.

Integration and state: header exposes unsigned long file handles that map to internal `fhentry` records. Consumers must respect the get/release pairing and buffer lifetime.

Risks and tests: the API does not express that `oplog_getdata` holds a mutex until release, so misuse can deadlock or expose stale ring memory. Compile-time format checking is a positive test signal for log calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/oplog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/osx_acl_converter.cc -->
## sources/distributed-fs/lizardfs/src/mount/osx_acl_converter.cc

Purpose: Apple-only conversion layer between macOS extended ACL xattr blobs and LizardFS `RichACL` objects.

Important APIs/functions: inside `#ifdef __APPLE__`, `extractAclObject` copies an ACL from xattr data and converts each allow/deny entry. `objectToOsxXattr` converts `RichACL` entries to a macOS ACL and serializes it. Helpers map RichACL permission bits to `acl_perm_t`, translate UUID qualifiers to uid/gid or NFS special identifiers, and map inheritance flags.

Control flow: extraction calls `acl_copy_int`, iterates entries with `acl_get_entry`, rejects unsupported tags/id types, builds `RichACL::Ace` values, inserts valid ACEs, and sets `RichACL::kAutoSetMode`. Serialization initializes an ACL sized to the RichACL, creates entries, fills permset/tag/qualifier/flags, then uses `acl_copy_ext`.

State and dependencies: no persistent state. Depends on macOS `sys/acl.h`, `membership.h`, RichACL, and syslog.

Risks: permission mappings are many-to-one for some RichACL bits, so round trips may lose detail. Errors often log and skip entries; an xattr with positive size but no valid ACE throws. The header includes macOS ACL declarations unconditionally, while implementation bodies are Apple-only, so build guards matter.

Test signals: should be tested on macOS with user/group/special identifier entries, allow/deny ACEs, inheritance flags, invalid UUIDs, and round-trip serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/osx_acl_converter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/osx_acl_converter.h -->
## sources/distributed-fs/lizardfs/src/mount/osx_acl_converter.h

Purpose: declares macOS ACL conversion helpers and `AclConversionException`.

Important APIs: namespace `osxAclConverter` provides `extractAclObject(const void*, size_t)` returning `RichACL` and `objectToOsxXattr(const RichACL&)` returning serialized xattr bytes.

Dependencies and integration: depends on `common/exception`, `common/richacl`, `mount/lizard_client`, and `sys/acl.h`; used by mount xattr/ACL handling on Apple builds.

Risks: declarations are platform-specific because `sys/acl.h` here means Apple's ACL API, not libacl. Non-Apple build inclusion must be guarded by the build system or platform headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/osx_acl_converter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/CMakeLists.txt -->
## sources/distributed-fs/lizardfs/src/mount/polonaise/CMakeLists.txt

Purpose: conditionally builds and installs the `lizardfs-polonaise-server` executable, a Thrift/Polonaise bridge over the LizardFS mount client.

Important behavior: returns early when Boost.Program_options, Polonaise, or Thrift are missing. It collects sources under `MOUNT_POLONAISE`, enables install rpath/link path handling, adds include directories, links `mfscommon`, `mount`, Polonaise, Thrift, Boost.Program_options, and Boost.System, and installs to `${BIN_SUBDIR}`.

Integration: part of the LizardFS CMake source collection pattern. The executable depends on both generated Polonaise/Thrift code and the regular mount client library.

Risks and tests: optional dependencies silently skip the server, so packaging tests should assert expected feature availability. Rpath settings affect deployment behavior and should be covered in install-tree smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/main.cc -->
## sources/distributed-fs/lizardfs/src/mount/polonaise/main.cc

Purpose: implements `lizardfs-polonaise-server`, a Thrift `Polonaise` service that maps remote Polonaise filesystem requests to `LizardClient` operations without using FUSE as the transport.

Important APIs/types: conversion helpers map errno to `StatusCode`, Thrift contexts to `LizardClient::Context`, Polonaise flags/modes/stat structs to Unix/LizardFS equivalents, and LizardFS replies back to Polonaise structs. `PolonaiseHandler` implements lookup/getattr/setattr/mknod/mkdir/opendir/readdir/releasedir/rmdir/access/create/open/read/write/fsync/flush/release/statfs/symlink/readlink/link/unlink/rename/xattr operations. `BigBufferedTransportFactory` supplies 512 KiB read and 4 KiB write buffers.

Control flow: `main` parses options, installs signal handlers, optionally daemonizes, initializes `LizardClient::fs_init` with master, cache, write-buffer, subfolder, password, and mode settings, then starts a threaded Thrift server on a TCP socket or Windows pipe. Each RPC uses `OPERATION_PROLOG/EPILOG` to translate LizardFS request exceptions into Polonaise statuses and conversion failures into Polonaise failures. Open/create allocate descriptors in a guarded map containing `LizardClient::FileInfo`; release/releasedir erase descriptors.

State and persistence: server state is in memory: global server pointer/termination flag, global setup, descriptor map, and the initialized LizardFS client state. It persists no files itself. Descriptor ids are monotonic per handler.

Dependencies and integration: depends on Thrift, generated Polonaise headers, Boost, `LizardClient`, read/write data initialization through `fs_init`, symlink cache, master communication, and platform stat definitions.

Risks: `toInt32` returns `uint32_t` despite documenting int32 conversion, though values are range checked. Descriptor insertion before successful create/open may leak descriptors if a later client call throws before return. `getFileInfo` returns a pointer after releasing the mutex, so concurrent release of the same descriptor can invalidate it in a threaded server. Write trusts the caller's `size` against `data.size()`. Unsupported or unknown errno values become Failure exceptions.

Test signals: needs integration tests with generated Polonaise clients for descriptor lifecycle, concurrent read/write/release, xattr two-step size queries, special inode reads, Windows pipe path, daemon signal shutdown, and error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/options.cc -->
## sources/distributed-fs/lizardfs/src/mount/polonaise/options.cc

Purpose: parses command-line options for the Polonaise server and implements stream conversion for `SugidClearMode`.

Important APIs: `operator>>(std::istream&, SugidClearMode&)` accepts `never`, `always`, `osx`, `bsd`, `ext`, and `xfs`; `operator<<` prints the same tokens. `parse_command_line` fills a `Setup` struct with master host/port, bind port, mountpoint, password, IO retries, write buffer, cache settings, subfolder, daemonization, ACL flag, and Windows pipe name.

Control flow: Boost.Program_options defines options and defaults from `LizardClient::FsInitParams`. Parse errors print to stderr and `exit(1)`; `--help` prints usage and exits 0.

State and dependencies: writes only the passed `Setup`. Depends on Boost.Program_options and default mount client parameters.

Risks and tests: `enable-acl` is deprecated and ignored. `no-mkdir-copy-sgid` uses a bool switch whose default is the positive default value but later inverted in `main`; option semantics should be tested. Invalid sugid mode should throw validation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/options.h -->
## sources/distributed-fs/lizardfs/src/mount/polonaise/options.h

Purpose: declares `parse_command_line` for the Polonaise server.

Important APIs: `parse_command_line(int argc, char **argv, Setup &setup)` mutates the caller-provided setup object and may exit the process on help or parse failure.

Integration: included by `main.cc`; depends on `Setup` from `setup.h`.

Risks and tests: process-exiting behavior complicates unit testing and embedding. Tests should isolate parse paths in a subprocess or refactor toward status-returning parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/setup.cc -->
## sources/distributed-fs/lizardfs/src/mount/polonaise/setup.cc

Purpose: defines the global `Setup gSetup` used by the Polonaise server.

Important behavior: no logic beyond storage definition.

State and integration: `gSetup` is populated by `parse_command_line` and consumed by `main` to initialize `LizardClient` and choose transport settings.

Risks and tests: global mutable configuration makes repeated in-process server startup hard to test. Tests should reset or avoid sharing process state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/setup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/setup.h -->
## sources/distributed-fs/lizardfs/src/mount/polonaise/setup.h

Purpose: declares the Polonaise server configuration struct and global instance.

Important fields: master host/port, bind port or Windows pipe name, mountpoint, password, IO retry count, write buffer size, report-reserved period, forget-password flag, subfolder, debug flag, directory/entry/attribute cache settings, mkdir SGID behavior, `SugidClearMode`, daemonization, and deprecated ACL flag.

Integration: filled by command-line parsing and translated into `LizardClient::FsInitParams`.

Risks and tests: stores password as plaintext string until `main` copies it into params. Field defaults are not intrinsic to the struct; callers must run the parser or initialize every field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/polonaise/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readahead_adviser.h -->
## sources/distributed-fs/lizardfs/src/mount/readahead_adviser.h

Purpose: header-only adaptive read-ahead predictor for the mount read path.

Important APIs/types: `ReadaheadAdviser::feed(offset, size)` observes original FUSE reads; `window()` returns the suggested extra read size. `HistoryEntry` stores timestamp and request size. Constants define initial window, default max, random threshold, history lifespan/capacity, and validity threshold.

Control flow: zero timeout disables read-ahead. Sequential reads matching `current_offset_` reset random-candidate count and expand the window. Nonmatching reads increment random candidates; once enough random candidates accumulate, the window is reduced and the current offset resets. Recent history estimates throughput and caps max window to roughly twice the observed throughput times timeout.

State and dependencies: maintains current offset, current/max window, random counter, ring-buffered recent request sizes, total requested bytes, and a timer. Used per `readrec` in `readdata.cc`.

Risks and tests: history lifespan constant is named `_ns` but uses `Timer::elapsed_us`, so units deserve review. Overlapping or holey sequential-ish reads can reduce read-ahead. Unit tests in `readahead_adviser_unittest.cc` cover monotonic expansion and reduction patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readahead_adviser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readahead_adviser_unittest.cc -->
## sources/distributed-fs/lizardfs/src/mount/readahead_adviser_unittest.cc

Purpose: GoogleTest coverage for `ReadaheadAdviser` behavior under sequential, holey, overlapping, and mixed read streams.

Important tests: `ReadSequential` asserts the window never shrinks for contiguous 64 KiB reads. `ReadHoles` and `ReadOverlapping` verify the window does not grow after enough nonmatching requests. `ReadSequentialThenHolesThenSequential` checks reduction during random-looking reads and renewed expansion when sequentiality resumes.

Dependencies and integration: includes only gtest and the adviser header, so tests are cheap and isolated.

Risks and gaps: tests assert monotonic directions but not exact window sizes, timeout-zero behavior, throughput-based max-window adjustment, random threshold boundary, or history expiry. They also do not address the apparent timestamp unit naming mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readahead_adviser_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readdata.cc -->
## sources/distributed-fs/lizardfs/src/mount/readdata.cc

Purpose: implements high-level file read handling for mounted files, combining chunk-location/reading, connection pooling, retry/backoff, cache lookup/fill, and adaptive read-ahead.

Important APIs/types: internal `readrec` owns `ChunkReader`, `ReadCache`, `ReadaheadAdviser`, inode, refresh counter, and expiry flag. Public functions include timeout getters, `read_data_init`, `read_data_new`, `read_data`, `read_data_end`, `read_inode_ops`, and `read_data_term`.

Control flow: init configures atomics, source IP, tweaks, connector timeouts, and starts `read_data_delayed_ops`, which cleans connection pool state and removes expired read records. `read_data_new` creates per-open read records. `read_data` feeds the adviser, queries cache, computes a request size at least as large as the asked range or read-ahead window, then calls `read_to_buffer`. `read_to_buffer` prepares chunk locations as needed, reads chunk segments with configured timeouts and XOR prefetch setting, handles EOF short reads, retries recoverable exceptions with exponential sleep, and maps ENOENT to EBADF.

State and persistence: global atomics store retry, timeout, cache, read-ahead, and prefetch settings. Active read records live in an unordered multimap protected by `gMutex`; `read_data_end` only marks expiry, and the delayed thread deletes records later. Data cache is per-readrec and memory-only.

Dependencies and integration: uses `ConnectionPool`, `ChunkConnectorUsingPool`, `ChunkReader`, `ReadPlanExecutor`, `mastercomm` for source IP, `Tweaks` for runtime configuration, and `ReadCache` for buffered slices. Called by `LizardClient::read`.

Risks: `read_data_freebuff` is declared in the header but not implemented here. Active record lifetime depends on delayed cleanup; callers must not use a record after `read_data_end`. The retry loop permits `try_counter > maxRetries`, so total attempts deserve precise validation. Cache and record operations are partially synchronized; per-record cache is otherwise used by the owning file handle.

Test signals: no direct unit test in this subset. Exercise cache hits/misses, inode refresh, chunk boundary reads, EOF, recoverable and unrecoverable chunk errors, tweak mutation, and termination cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readdata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readdata.h -->
## sources/distributed-fs/lizardfs/src/mount/readdata.h

Purpose: declares the read-data subsystem API used by the client file operations.

Important APIs: timeout/prefetch getters, `read_inode_ops` for invalidation after inode attribute changes, lifecycle `read_data_init`/`read_data_term`, per-open `read_data_new`/`read_data_end`, and `read_data` returning a `ReadCache::Result` for requested aligned ranges.

Integration: includes `chunk_locator` and `readdata_cache`; parameters expose chunkserver RTT/connect/wave/total timeouts, cache expiration, readahead max window, XOR prefetch, and bandwidth overuse tuning.

Risks and tests: `read_data_freebuff` is declared but not defined in the implementation read for this item, suggesting legacy API drift. Callers must provide block-aligned `offset` and `size` because implementation asserts alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readdata_cache.h -->
## sources/distributed-fs/lizardfs/src/mount/readdata_cache.h

Purpose: header-only per-read-handle cache storing contiguous read buffers by file offset and returning acquired cache entries to callers.

Important APIs/types: `ReadCache::Entry` stores offset, buffer, timer, atomic refcount, and intrusive hooks. `ReadCache::Result` owns acquired entry pointers, releases them on destruction, can expose an input buffer for missing data, serialize data to an iovec, or copy to a flat buffer. `ReadCache::query(offset, size)` returns cached spans and inserts an empty tail entry for missing bytes.

Control flow: `query` garbage-collects a few expired/LRU and reserved entries, seeks to the entry before the requested offset, accumulates nonexpired overlapping entries, erases expired/empty ones, and inserts a new empty entry if bytes remain. Insert clears colliding entries up to the new end offset. Erased entries with outstanding refs move to a reserved list until released.

State and dependencies: uses boost intrusive set/list, `Timer`, `small_vector`, and raw heap allocation. The cache itself has no mutex; it is intended to be owned by a single read record/handle.

Risks: callers must fill `Result::inputBuffer()` only when the last entry is empty and acquired. `Result` is move-only by convention but copy is not explicitly deleted. Expiration and collision rules can discard overlapping cache entries aggressively. Refcount is atomic, but container mutations are not thread-safe.

Test signals: no direct tests in this subset. Important tests are partial hit plus tail fill, collision eviction while a result is alive, expired entry cleanup, EOF empty buffer behavior, and iovec/copy slicing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/readdata_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_getattr.cc -->
## sources/distributed-fs/lizardfs/src/mount/special_getattr.cc

Purpose: implements `getattr` dispatch for LizardFS special inodes.

Important APIs: namespace-local `getattr` functions for `MASTERINFO`, `STATS`, `OPLOG`, `OPHISTORY`, `TWEAKS_FILE`, and `FILE_BY_INODE_FILE` convert static `Attributes` into `struct stat`, increment stats, format attr strings, log to oplog, and return `AttrReply` with 3600-second timeout. `special_getattr` indexes a 16-entry function table by `ino - SPECIAL_INODE_BASE`.

State and dependencies: uses static attrs from `special_inode.cc`, `client_common` conversion helpers, `stats`, and `oplog`.

Risks: no bounds check before indexing the function array; callers must pass a valid special inode. Unimplemented table entries throw EINVAL after logging. All attrs are static and do not reflect dynamic size of stats/oplog/tweaks.

Test signals: verify every defined special inode maps to correct mode/type, invalid reserved slots return EINVAL, and logged attr strings match expected stat conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_getattr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_inode.cc -->
## sources/distributed-fs/lizardfs/src/mount/special_inode.cc

Purpose: defines static attributes and inode constants for mount internal special files.

Important data: `InodeMasterInfo::attr` is a read-only file of length 10 or 14 depending on `MASTERINFO_WITH_VERSION`; `InodeStats` and `InodeTweaks` are 0644 files; `InodeOplog` and `InodeOphistory` are 0400 files; `InodeFileByInode` is a 0755 directory. Each namespace also exposes `inode_` from `SPECIAL_INODE_*`.

State and dependencies: immutable process-global constants. Depends on `special_inode_defs`, `lizard_client` attributes, and stats include only indirectly.

Risks: encoded `Attributes` byte arrays are hard to audit and must stay aligned with `attr_to_stat` expectations. Size of dynamic files is mostly zero/static, so readers rely on direct IO and runtime read logic.

Test signals: compare `attr_to_stat` output for every special inode against intended file type, permissions, nlink, and size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_inode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_inode.h -->
## sources/distributed-fs/lizardfs/src/mount/special_inode.h

Purpose: central declaration point for special inode constants, per-namespace attributes, and operation dispatch functions.

Important APIs/types: declares namespace attrs/inode ids for masterinfo, stats, oplog, ophistory, tweaks, and file-by-inode. `InodeStats::sinfo` stores a stats snapshot buffer, length, reset flag, and mutex. Declares `special_lookup`, `special_getattr`, `special_setattr`, `special_open`, `special_read`, `special_write`, and `special_release`.

Integration: included by all special operation implementation files and pulls in `mastercomm`, `masterproxy`, `oplog`, `tweaks`, and client context types.

Risks: broad includes create coupling; dispatch functions assume `ino` is in the special range. `sinfo` uses C allocation and pthread mutex, so open/release symmetry is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_lookup.cc -->
## sources/distributed-fs/lizardfs/src/mount/special_lookup.cc

Purpose: implements lookup responses for internal special inode directory entries.

Important APIs: one static lookup per special inode fills `EntryParam` with inode id, 3600-second attr/entry timeouts, stat-converted static attrs, increments `OP_LOOKUP_INTERNAL`, builds attrstr, and writes an operation log entry. `special_lookup` dispatches through a 16-entry table.

State and dependencies: no mutable state besides stats/oplog. Depends on `client_common` and `special_inode`.

Risks: indexes `funcs[ino - SPECIAL_INODE_BASE]` without range validation. The table comments contain repeated/misaligned slot labels in some related files; actual initializer position is what matters. Name is only logged, not validated here.

Test signals: lookup each supported internal name through caller path, verify returned inode/attrs/timeouts and stats increment. Invalid reserved slots should throw EINVAL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_lookup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_open.cc -->
## sources/distributed-fs/lizardfs/src/mount/special_open.cc

Purpose: implements open behavior for special inode files.

Important APIs: `MASTERINFO`, `OPLOG`, and `OPHISTORY` require read-only access. Stats open allocates `InodeStats::sinfo`, initializes a mutex, snapshots all stats via `stats_show_all`, and stores it in `fi->fh`. Oplog/history opens allocate oplog handles with or without history. Tweaks open allocates a `MagicFile`. `special_open` dispatches by special inode index.

State and dependencies: stores per-open state in `LizardClient::FileInfo::fh`. Sets FUSE hints: masterinfo is cacheable, stats/oplog/history/tweaks use direct IO and no keep-cache.

Risks: if later operations fail, allocated `sinfo`, oplog handles, or `MagicFile` require release cleanup. No range check before table indexing. Stats snapshot allocation errors are mapped to out-of-memory.

Test signals: verify access modes, per-file `direct_io`/`keep_cache`, handle allocation, stats mutex lifecycle, and invalid inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_open.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_read.cc -->
## sources/distributed-fs/lizardfs/src/mount/special_read.cc

Purpose: implements read behavior for special files.

Important APIs: `InodeMasterInfo::read` returns the 14-byte master location/session/version buffer after optional proxy rewriting. `InodeStats::read` slices the per-open stats snapshot. `InodeOplog` and `InodeOphistory` read from oplog handles. `InodeTweaks::read` lazily snapshots `gTweaks.getAllValues()` into its `MagicFile` and returns requested slices. `special_read` dispatches by inode.

State and dependencies: uses file-handle state from `special_open`, mastercomm/masterproxy, stats snapshot buffers, oplog, tweaks, and operation logging. Reads return `std::vector<uint8_t>`.

Risks: oplog read constructs a vector from `buff` after `oplog_releasedata`; because release may unlock and allow ring mutation, this depends on the source bytes remaining valid long enough and should copy before release. Offset/size arithmetic casts around signed `off_t` and unsigned sizes need boundary tests. No range check before dispatch.

Test signals: partial reads at zero/middle/end for masterinfo/stats/tweaks, blocking oplog read heartbeat, proxy masterinfo rewrite, and concurrent tweak writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_read.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_release.cc -->
## sources/distributed-fs/lizardfs/src/mount/special_release.cc

Purpose: releases per-open resources for special inodes.

Important APIs: stats release frees snapshot buffer, optionally resets all stats if the file was written, destroys mutex, and frees `sinfo`. Oplog/history release their log handles. Tweaks release parses `name=value` from the accumulated `MagicFile` value and calls `gTweaks.setValue`, then deletes the file object. Masterinfo has no resource beyond logging.

State and dependencies: consumes `fi->fh` state allocated by `special_open`; touches global stats, oplog, and tweaks.

Risks: tweaks apply only on release, so write errors may surface late only via logs. Stats reset is triggered by any write, regardless of content. No dispatch range check. Release must be called exactly once for allocated state.

Test signals: write stats then release resets counters, write tweaks with and without `=`, newline trimming, double/invalid release protection through caller layer, and oplog handle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_release.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_setattr.cc -->
## sources/distributed-fs/lizardfs/src/mount/special_setattr.cc

Purpose: handles setattr attempts on special inodes.

Important APIs: masterinfo rejects all setattr with EPERM. Other implemented special inodes ignore requested changes, return their static attrs with 3600-second timeout, and log an OK entry through `printSetattrOplog`. `special_setattr` dispatches through a 16-entry table.

State and dependencies: no persistent mutation occurs; depends on `client_common`, static special attrs, and operation logging.

Risks: callers may interpret successful setattr on stats/oplog/tweaks/file-by-inode as mutation even though it is ignored. No range check before function-table indexing. Static attr return means requested chmod/chown/truncate has no effect.

Test signals: ensure masterinfo returns EPERM, other special inodes return unchanged attrs, invalid slots return EINVAL, and no dynamic state changes happen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_setattr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_write.cc -->
## sources/distributed-fs/lizardfs/src/mount/special_write.cc

Purpose: implements writes to special files.

Important APIs: masterinfo, oplog, and ophistory reject writes with EACCES. Stats writes mark the per-open stats snapshot to reset counters on release and report all bytes written. Tweaks writes splice bytes into the per-open `MagicFile::value`, mark it written, and apply on release. `special_write` dispatches by inode.

State and dependencies: mutates only per-open `sinfo` or `MagicFile` state until release. Uses oplog for tracing.

Risks: stats reset is content-insensitive. Tweaks accepts sparse/offset writes and grows a string; malformed data is logged on release. The write function trusts `off + size` arithmetic and table index validity.

Test signals: writes to read-only internal files return EACCES; stats write triggers reset only after release; tweak offset writes compose expected string and update registered atomics after release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/special_write.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/stat_defs.h -->
## sources/distributed-fs/lizardfs/src/mount/stat_defs.h

Purpose: provides cross-platform Unix stat/statvfs definitions for mount code, especially Windows builds.

Important content: on `_WIN32`, defines a `statvfs` struct and Unix mode bit constants/macros (`S_IF*`, `S_IS*`, permissions, suid/sgid/sticky). On non-Windows, includes system `<sys/stat.h>` and `<sys/statvfs.h>`.

Integration: included last by `polonaise/main.cc` with an explicit warning, because it may redefine mode macros on Windows.

Risks: Windows definitions must match expectations of LizardFS and Polonaise conversions. Redefining standard-like macros can conflict if included in the wrong order.

Test signals: compile on Windows and non-Windows, verify mode conversions for every file type and permission bit, and statfs field mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/stat_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/stats.cc -->
## sources/distributed-fs/lizardfs/src/mount/stats.cc

Purpose: implements a hierarchical in-memory counter tree used by mount subsystems and exposed through the stats special file.

Important APIs: `stats_get_subnode` finds or creates child/root nodes by name. `stats_get_counterptr` marks a node active and returns a pointer to its counter. `stats_lock`/`stats_unlock` provide external locking for pointer users. `stats_reset_all` resets non-absolute counters. `stats_show_all` allocates and fills a newline-delimited `fullname: value` buffer. `stats_term` frees the tree.

Control flow/state: nodes are singly linked by first child/next sibling. Active node counts and path lengths estimate the buffer size for printing. Absolute counters survive reset. All tree mutations and printing are guarded by global pthread mutex `glock`.

Dependencies and integration: used by mastercomm, symlink cache, special inode stats, and operation counters elsewhere.

Risks: callers holding counter pointers must use `stats_lock` around increments; the API cannot enforce this. Allocation failure in subnode creation can return null and downstream callers may not always check. `stats_term` does not reset globals after freeing.

Test signals: create nested counters, active/inactive printing, reset behavior with absolute counters, concurrent increments with external lock, and termination cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/stats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/stats.h -->
## sources/distributed-fs/lizardfs/src/mount/stats.h

Purpose: declares the stats tree node layout and public counter-tree API.

Important APIs/types: `statsnode` stores counter, active/absolute flags, short and full names, name lengths, and child/sibling pointers. Functions create subnodes, fetch counter pointers, reset, show, lock/unlock, and terminate.

Integration: subsystems cache returned `uint64_t *` counter pointers and mutate them under `stats_lock`.

Risks and tests: raw pointers and global lock make lifetime/order important. Tests should ensure no subsystem uses counter pointers after `stats_term`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/sugid_clear_mode_string.h -->
## sources/distributed-fs/lizardfs/src/mount/sugid_clear_mode_string.h

Purpose: small helper converting `SugidClearMode` enum values to uppercase diagnostic strings.

Important API: `sugidClearModeString(SugidClearMode mode)` returns `NEVER`, `ALWAYS`, `OSX`, `BSD`, `EXT`, `XFS`, or `???` for out-of-range values.

Dependencies and integration: includes `protocol/MFSCommunication.h` for the enum. Useful for logs/config displays.

Risks and tests: array order must match enum numeric order. A simple enum-coverage test should pin every expected string and invalid fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/sugid_clear_mode_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/symlinkcache.cc -->
## sources/distributed-fs/lizardfs/src/mount/symlinkcache.cc

Purpose: implements a fixed-size in-memory symlink target cache keyed by inode.

Important APIs/state: `symlink_cache_init` allocates 6257 hash buckets, each with 16 slots; four multiplicative hash functions probe up to 64 candidate slots. `symlink_cache_insert` updates an existing inode or replaces the oldest candidate slot. `symlink_cache_search` checks expiration, returns cached path pointer on hit, and updates stats. `symlink_cache_term` frees paths and bucket storage.

Control flow: insertion and search are protected by `slcachelock`. Entries store inode, timestamp, and `strdup` path. `kCacheTimeInSeconds` controls expiry. Stats counters track inserts, hits, misses, and live links.

Dependencies and integration: used by symlink read path elsewhere in mount code; exports counters under `symlink_cache`.

Risks: returned path pointer is unlocked before return and can be invalidated by later cache mutation, so callers must copy or consume carefully. `symlink_cache_init` does not check malloc failure before `memset`. Expired entry accounting decrements link count on search cleanup only.

Test signals: insert/search hit, replacement policy, expiration, duplicate update, stats counters, and termination after many allocated paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/symlinkcache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/symlinkcache.h -->
## sources/distributed-fs/lizardfs/src/mount/symlinkcache.h

Purpose: declares the symlink cache API.

Important APIs: `symlink_cache_insert(inode, path)`, `symlink_cache_search(inode, &path)` returning int hit/miss, `symlink_cache_init(cache_time = 3600)`, and `symlink_cache_term`.

State and integration: the returned `path` points to cache-owned memory; the cache is global and must be initialized before use.

Risks and tests: lifetime of returned path is not encoded in the API. Tests should copy the result immediately and verify behavior before/after termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/symlinkcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/thread_safe_map.h -->
## sources/distributed-fs/lizardfs/src/mount/thread_safe_map.h

Purpose: generic mutex-protected unordered map with a monotonically increasing generated key.

Important APIs: `put(key, data)` stores/replaces data; `take(key)` removes and returns `{true, data}` or `{false, default}`; `generateKey()` increments and returns `next_key_`.

State and dependencies: owns a `std::unordered_map<K, D>`, `std::mutex`, and key counter initialized to zero.

Risks: `take` default-constructs `D` even on miss, so `D` must be default constructible. Key overflow and zero-as-special semantics are caller concerns. It does not expose lookup without removal.

Test signals: concurrent put/take/generateKey, missing keys, duplicate puts, and generated-key wrap behavior for small integral key types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/thread_safe_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/tweaks.cc -->
## sources/distributed-fs/lizardfs/src/mount/tweaks.cc

Purpose: implements runtime tweak registry for selected atomic variables, exposed through the tweaks special file.

Important APIs/types: abstract `Variable` supports string set/get. `VariableImpl<T>` wraps `std::atomic<T>`, parses values with `std::boolalpha`, and stores only on successful stream extraction. `Tweaks::registerVariable` overloads accept atomic bool, uint32_t, and uint64_t. `setValue` applies to all variables with matching name; `getAllValues` returns tab-separated name/value lines. Defines global `Tweaks gTweaks`.

State and dependencies: registry is a list of name/unique_ptr pairs in `Tweaks::Impl`. No explicit mutex protects registration or set/get; expected use is mostly during initialization plus special-file writes.

Risks: duplicate names are allowed and all are set. Parsing accepts prefixes such as `16 xxx`, as confirmed by tests. There is no feedback for unknown names or invalid values. Concurrent access is not synchronized around the registry.

Test signals: `tweaks_unittest.cc` covers output formatting, invalid numeric input ignored, partial numeric parses accepted, newline handling, and bool parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/tweaks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/tweaks.h -->
## sources/distributed-fs/lizardfs/src/mount/tweaks.h

Purpose: declares the `Tweaks` runtime variable registry and global `gTweaks`.

Important APIs: registration overloads for atomic bool/uint32_t/uint64_t, `setValue(name, value)`, and `getAllValues()`.

Integration: read/write special inode uses it for operator-visible configuration; `readdata.cc` registers read/cache timeout and counter variables.

Risks and tests: registry lifetime is global; variables are stored by pointer, so registered atomics must outlive the registry entry. Tests should cover lifetime and duplicate names if expanded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/tweaks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/tweaks_unittest.cc -->
## sources/distributed-fs/lizardfs/src/mount/tweaks_unittest.cc

Purpose: GoogleTest coverage for `Tweaks`.

Important tests: `GetAllValues` registers uint32, uint64, and bool atomics and verifies tab/newline formatting and boolalpha output. `SetValue` verifies invalid strings leave values unchanged, numeric parsing accepts whitespace/prefix numeric data, uint64 updates independently, and bool values parse `true`, `false`, and `true\n`.

Dependencies and integration: isolated unit test depending only on gtest and `tweaks.h`.

Risks and gaps: does not cover duplicate names, unknown names, concurrent access, registry lifetime after referenced atomics go out of scope, or negative/out-of-range numeric parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/tweaks_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/write_cache_block.cc -->
## sources/distributed-fs/lizardfs/src/mount/write_cache_block.cc

Purpose: implements the movable block buffer used by write-cache/chunk-writer logic.

Important APIs: constructor allocates one `MFSBLOCKSIZE` buffer for a chunk/block/type and asserts `blockIndex < MFSBLOCKSINCHUNK`. Move constructor/assignment transfer or swap ownership. `expand(from, to, buffer)` initializes or extends the valid byte range if the new range overlaps/touches current data. `offsetInFile`, `offsetInChunk`, `size`, and `data` expose location and valid bytes.

State and dependencies: each block stores raw `blockData`, chunk index, block index, valid `[from, to)` range, and type. Depends on `MFSCommunication` constants and `massert`.

Risks: `expand` does not validate `to <= MFSBLOCKSIZE` or `from <= to`; callers must enforce bounds. Move assignment via swaps leaves the moved-from object owning the old destination buffer, which is valid but subtle. Raw buffer is always full block size even for small writes.

Test signals: construct/move/destruct, overlapping and non-overlapping expand, boundary offsets, parity/read-only type propagation, and invalid range assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/write_cache_block.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/write_cache_block.h -->
## sources/distributed-fs/lizardfs/src/mount/write_cache_block.h

Purpose: declares `WriteCacheBlock`, the write cache's owned memory block plus metadata.

Important APIs/types: enum `Type` distinguishes writable, read-only-after-submit, parity, and read-for-parity blocks. Public fields expose `blockData`, chunk/block indexes, valid range, and type. Copy is deleted; move is supported. Methods expand data and compute file/chunk offsets, size, and data pointers.

Integration: used by write data/cache code to merge byte ranges within one filesystem block and pass buffers to chunk writers.

Risks and tests: public mutable fields permit invariant violations outside the class. Tests should assert callers cannot create out-of-bounds ranges and that moved blocks remain destructible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/write_cache_block.h -->
