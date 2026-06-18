# Research: subset-b-007632

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/main.cc -->
# sources/distributed-fs/lizardfs/src/mount/fuse/main.cc

## Purpose
This is the `mfsmount` executable entrypoint and libfuse low-level session bootstrap. It wires either the normal LizardFS mount operations or the meta/trash filesystem operations into `fuse_lowlevel_ops`, parses command line and config-file options, initializes client-side master/chunkserver subsystems, daemonizes when requested, and owns orderly teardown after the FUSE loop exits.

## Important APIs, Types, And Functions
`init_fuse_lowlevel_ops()` maps FUSE callbacks to `mfs_*` or `mfs_meta_*` functions, conditionally enabling POSIX and BSD-style locks when `gMountOptions.filelocks` is set. `mfs_fsinit()` applies FUSE connection flags such as `FUSE_CAP_DONT_MASK`, POSIX ACL support on FUSE 3, and disables `FUSE_CAP_ATOMIC_O_TRUNC`. `setup_password()` converts a plaintext mount password to an MD5 digest or parses a supplied digest, then zeroes the original option buffer. `mainloop()` performs runtime setup, client initialization, FUSE session creation/mounting, signal handler registration, loop execution, unmount, session destruction, and subsystem termination. `read_masterhost_if_present()` supports the positional `HOST[:PORT]:[PATH]` syntax, while `make_fsname()` builds a FUSE `fsname`/`subtype` option with comma escaping depending on libfuse version.

## Control Flow
`main()` builds separate default and user `fuse_args`, reads positional master syntax, stage-1 parses only config-file options, optionally loads the default config, stage-2 parses defaults then user arguments, parses FUSE 3 connection options, validates cache and sugid modes, fills defaults for master host/port/subfolder, clamps cache sizes and worker counts, appends standard mount options, creates the FUSE-visible fs name, parses the final command line, prompts for passwords if requested, validates the mountpoint, and then either calls `mainloop()` directly or through `daemonize_and_wait()`. `mainloop()` initializes `LizardClient` for a normal mount; in meta mode it initializes `masterproxy`, symlink cache, master connection, and I/O threads manually before selecting the meta operation table.

## State And Persistence
The file mutates process-global `gMountOptions`, `gDefaultMountpoint`, FUSE argument vectors, syslog/stderr logging sinks, resource limits, process priority/session state, password option buffers, and FUSE session state. It does not persist repository data, but it opens long-lived network state through master connections, I/O threads, read/write caches, symlink cache, and master proxy state that must be terminated on each failure path.

## Dependencies And Integration Points
It integrates `mount_config.*`, `mfs_fuse.*`, `mfs_meta_fuse.*`, `LizardClient`, `mastercomm`, `masterproxy`, `readdata`, `writedata`, `stats`, `symlinkcache`, libfuse 2/3 APIs, daemonization helpers, syslog, MD5 helpers, and default protocol constants. Compile-time `FUSE_VERSION` branches significantly change startup, mount, command-line, and cleanup behavior.

## Risks And Test Signals
Risk centers on option lifetime and manual memory ownership, version-specific FUSE paths, duplicate or partially failed subsystem initialization, and unsupported FUSE 3 rename flags being ignored. The mountpoint non-empty check is local to FUSE 3. Test signals should include option parsing permutations, password zeroing behavior, FUSE 2/3 builds, meta vs normal startup failure cleanup, cache-mode validation, and daemon/foreground flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mfs_fuse.cc -->
# sources/distributed-fs/lizardfs/src/mount/fuse/mfs_fuse.cc

## Purpose
This file is the normal low-level FUSE adapter. It translates each kernel FUSE request into a `LizardClient` call, converts reply structures and errors back to libfuse, tracks per-request user/group context, and handles file descriptor state handoff between `fuse_file_info` and `LizardClient::FileInfo`.

## Important APIs, Types, And Functions
`get_reduced_context()` converts `fuse_req_ctx()` uid/gid/pid/umask into `LizardClient::Context`; `get_context()` additionally discovers secondary groups and calls `LizardClient::updateGroups()`. Linux uses `fuse_req_getgroups()` with a 10-second LRU pid cache, while macOS/FreeBSD use `sysctl` process credentials. `fuse_file_info_wrapper` mirrors `flags`, `direct_io`, `keep_cache`, `fh`, and `lock_owner` into `LizardClient::FileInfo` and writes modified values back on destruction. `make_fuse_entry_param()` converts `LizardClient::EntryParam` into libfuse's entry reply. Every exported `mfs_*` function wraps a `LizardClient` operation and catches `RequestException`.

## Control Flow
Most operations follow a direct pattern: build context, call `LizardClient`, reply with `fuse_reply_*`, or return `e.system_error_code`. Directory open creates a synthetic `fh` session id and registers it with `LizardClient::update_readdir_session()`. `mfs_readdir()` requests a bounded number of client entries, packs them with `fuse_add_direntry()`, updates the session's last inode, and replies with a buffer. `mfs_read()` uses `fuse_reply_iov()` for normal file reads and direct buffers for special inodes. Create/open paths remove client file info if libfuse reports `-ENOENT` while replying.

## State And Persistence
The file owns `gPidToContextCache` and `gLockInterruptData`. It mutates per-FUSE-request `fuse_file_info`, directory session state in `LizardClient`, and interrupt data for blocking locks. It does not persist data itself; durable effects are delegated to `LizardClient` and master/chunkserver communication.

## Dependencies And Integration Points
It depends on libfuse low-level request APIs, platform credential APIs, `GroupCache`, `ThreadSafeMap`, `lock_conversion`, `LizardClient`, protocol constants, and `ReadCache` iovec conversion. It is installed by `main.cc` into the normal `fuse_lowlevel_ops` table.

## Risks And Test Signals
The secondary-group cache invalidation uses `gPidToContextCache.erase(ctx.uid)` despite pid-keyed caching, which deserves review. Other risks include reply-time cleanup when FUSE rejects open/create replies, fixed 50 KB readdir buffers, ignored FUSE 3 rename flags, unsupported `security.capability`, and interrupt data lifetime for blocking locks. Test signals include FUSE operation tests, lock interrupt tests, group membership changes, xattr compatibility, and iovec reply coverage from `iovec_traits_unittest.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mfs_fuse.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mfs_fuse.h -->
# sources/distributed-fs/lizardfs/src/mount/fuse/mfs_fuse.h

## Purpose
This header declares the normal LizardFS low-level FUSE callback surface used by `main.cc`. It exposes the functions installed into `struct fuse_lowlevel_ops` for regular filesystem mounts.

## Important APIs, Types, And Functions
The declarations cover statfs, access, lookup, getattr/setattr, node creation and deletion, directory operations, file create/open/read/write/flush/fsync/release, extended attributes, and optional locking. Signatures are version-gated for `mfs_statfs()` on FUSE 2.6+, `mfs_rename()` on FUSE 3 flags, Apple xattr `position`, POSIX byte-range locks on FUSE 2.6+, and flock on FUSE 2.9+.

## Control Flow
The header has no runtime control flow, but it is the ABI contract between the mount bootstrap and `mfs_fuse.cc`. `init_fuse_lowlevel_ops()` assigns these function pointers, so signature drift breaks mount startup or compilation.

## State And Persistence
No state is stored here. State is passed through `fuse_req_t`, inode ids, `fuse_file_info`, and user buffers into the implementation.

## Dependencies And Integration Points
It depends on `common/platform.h`, libfuse headers, and `protocol/MFSCommunication.h` for protocol-visible constants. It integrates with `main.cc`, `mfs_fuse.cc`, and libfuse's low-level operation structure.

## Risks And Test Signals
Risks are mostly compatibility risks: FUSE version macros must match the libfuse headers used to compile the operation table. Test signals are successful FUSE 2 and FUSE 3 builds, plus compile coverage for Apple and non-Apple xattr signatures and optional file-lock support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mfs_fuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mfs_meta_fuse.cc -->
# sources/distributed-fs/lizardfs/src/mount/fuse/mfs_meta_fuse.cc

## Purpose
This file implements the low-level FUSE adapter for the LizardFS meta mount. The meta filesystem exposes synthetic directories and files for trash, undelete, reserved files, and master location data, allowing administrative actions such as purge and undel through filesystem operations.

## Important APIs, Types, And Functions
`mfs_meta_name_to_inode()` parses detached inode names encoded as eight hex digits followed by `|`. `mfs_meta_stat()` and `mfs_attr_to_stat()` build `stat` values for synthetic and detached entries. `mfs_meta_lookup()`, `getattr()`, `statfs()`, `unlink()`, and `rename()` implement discovery, attributes, purge, and undelete. `dirbuf` stores packed directory listings with a mutex; `pathbuf` stores editable trash paths. `dir_metaentries_*` emits synthetic `.`/`..`/trash/undel/reserved entries, while `dir_dataentries_*` converts master trash/reserved listings into FUSE entry names. `mfs_meta_open/read/write/release()` handle either the read-only `masterinfo` file or editable detached-object path files.

## Control Flow
Root lookup recognizes trash, reserved, and masterinfo. Trash lookup additionally recognizes `undel` and detached inode names; reserved lookup recognizes detached inode names. `unlink()` is accepted only under trash and calls `fs_purge()`. `rename()` is effectively an undelete trigger from trash to undel and calls `fs_undel()`. `opendir()` allocates a `dirbuf`; `readdir()` refreshes packed contents on first read or rewind, walks packed records from `off`, and replies with `fuse_add_direntry()` output. Opening a detached inode fetches its trash path, writes modify the path buffer up to 1024 bytes, and release calls `fs_settrashpath()` if changed.

## State And Persistence
Static state holds debug and cache timeout settings set by `mfs_meta_init()`. Per-open directory and path buffers are heap-allocated and protected with pthread mutexes. Persistent effects occur through master RPCs: purge, undelete, fetching trash/reserved lists, fetching detached attrs/paths, setting trash paths, and retrieving master location.

## Dependencies And Integration Points
The implementation depends on special inode definitions, `mastercomm` RPC functions, `masterproxy_getlocation()`, `exports` policy for non-root meta permissions, datapack helpers, protocol attribute formats, libfuse, and pthread mutexes. It is selected by `main.cc` when `mfsmeta` is enabled.

## Risks And Test Signals
Risks include manual packed-buffer parsing, missing replies on some allocation or mutex-init failures, old C-style pointer ownership, FUSE 3 rename flags ignored, and path writes that can create NUL-filled sparse buffers. Test signals should cover root/trash/reserved lookup, purge/undel behavior, directory rewind refresh, malformed directory data logging, masterinfo read sizes with and without version support, and path edit release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mfs_meta_fuse.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mfs_meta_fuse.h -->
# sources/distributed-fs/lizardfs/src/mount/fuse/mfs_meta_fuse.h

## Purpose
This header declares the meta filesystem's low-level FUSE callback surface. It is the compile-time contract used by `main.cc` to populate the meta `fuse_lowlevel_ops` table.

## Important APIs, Types, And Functions
Declarations cover meta statfs, lookup, getattr/setattr, unlink, rename, opendir/readdir/releasedir, open/release/read/write, and `mfs_meta_init()`. FUSE version gates handle `statfs` and FUSE 3 `rename` flags.

## Control Flow
No runtime flow exists in the header. The declared callbacks are invoked by libfuse only when `mfsmeta` selects the meta operation table.

## State And Persistence
No state is defined here. Runtime state lives in `mfs_meta_fuse.cc` through static cache settings and per-handle buffers.

## Dependencies And Integration Points
It depends on `common/platform.h` and `fuse_lowlevel.h`, and it integrates directly with the FUSE bootstrap in `main.cc` and implementation in `mfs_meta_fuse.cc`.

## Risks And Test Signals
The primary risk is signature mismatch across libfuse versions. Build coverage for FUSE 2 and FUSE 3, plus meta mount callback registration, are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mfs_meta_fuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mount_config.cc -->
# sources/distributed-fs/lizardfs/src/mount/fuse/mount_config.cc

## Purpose
This file defines global mount option storage, the libfuse option tables, help text, config-file parsing, and custom option callbacks used by the mount entrypoint.

## Important APIs, Types, And Functions
`gMountOptions` is the global `mfsopts_` instance consumed by `main.cc`. `gMfsOptsStage1` recognizes only config-file options so config files can be loaded before normal parsing. `gMfsOptsStage2` maps `-o` options and short/long aliases into `mfsopts_` fields or keys. `usage()` prints LizardFS-specific options and libfuse help. `mfs_opt_parse_cfg_file()` reads a config file line by line, ignoring `#`/`;` comments, trimming whitespace, treating absolute paths as default mountpoints, and converting bare options into `-o` pairs. `mfs_opt_proc_stage1()` opens explicit config files. `mfs_opt_proc_stage2()` handles short options, legacy help/version behavior for FUSE 2, and option discarding.

## Control Flow
The parser is intentionally two-stage. Stage 1 loads config-file contents into a default argument vector. Stage 2 first parses that vector into `gMountOptions`, then parses original command-line arguments so explicit CLI options override config defaults. Key callbacks update heap-owned string fields by freeing old values and `strdup()`ing new ones.

## State And Persistence
The file stores global option state, `gCustomCfg`, and `gDefaultMountpoint`. It persists no external data; it only reads config files and allocates option strings that `main.cc` later frees.

## Dependencies And Integration Points
It depends on libfuse option parsing, `mount_config.h`, `LizardClient::FsInitParams` defaults, sugid clear mode string helpers, and compile-time FUSE/platform options. It is the source of truth for CLI/config option names accepted by `mfsmount`.

## Risks And Test Signals
Risks include manual string lifetime, `abort()` on non-optional config open failure, a 1000-byte fixed config line buffer, and compatibility differences in FUSE 2 help/version handling. Test signals include config precedence, default mountpoint parsing, short option parsing, help/version output, `--nonempty` gating, and every `MFS_OPT` field mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mount_config.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mount_config.h -->
# sources/distributed-fs/lizardfs/src/mount/fuse/mount_config.h

## Purpose
This header defines the mount option model used by `mfsmount`, default FUSE mount options, option key ids, global parser symbols, and config/parser function declarations.

## Important APIs, Types, And Functions
`mfsopts_` contains every LizardFS mount option: master host/port/bind/subfolder/passwords, resource limits, debug/meta/delayed init, ACL and cache settings, write-cache settings, chunkserver timeouts, I/O limit config, symlink cache, bandwidth overuse, file locks, and FUSE 3 non-empty mounts. Its constructor seeds defaults from `LizardClient::FsInitParams`. The header also exposes `gMountOptions`, `gCustomCfg`, `gDefaultMountpoint`, `gMfsOptsStage1`, `gMfsOptsStage2`, `usage()`, config parsing, and stage parser callbacks.

## Control Flow
No executable control flow exists here, but construction of the global `gMountOptions` applies all default values before command-line parsing. Compile-time branches determine whether memory locking, file locks, and non-empty mounts exist.

## State And Persistence
The structure owns raw C strings allocated by libfuse parsing or `strdup()`, while numeric and boolean fields carry final mount configuration into `main.cc` and `LizardClient::FsInitParams`. There is no persistence beyond process memory.

## Dependencies And Integration Points
It integrates libfuse, resource-limit headers, platform memory-lock support, protocol defaults, and `LizardClient` defaults. `main.cc` translates this struct into initialization parameters and frees string fields on exit.

## Risks And Test Signals
Raw pointer ownership is the main risk; every added string field needs parsing and cleanup handling. Defaults must stay synchronized with `FsInitParams`. Test signals are compile coverage under different platform/FUSE macros and option parsing tests that assert default values, overrides, and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/fuse/mount_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/g_io_limiters.cc -->
# sources/distributed-fs/lizardfs/src/mount/g_io_limiters.cc

## Purpose
This file provides process-wide singleton accessors for the mount's local and global I/O limiters. It centralizes lazy construction of limiter state used by `LizardClient::read()` and `write()`.

## Important APIs, Types, And Functions
`gMountLimiter()` returns the local `ioLimiting::MountLimiter`. `gLocalIoLimiter()` constructs a static real-time clock and `LimiterProxy` over the local mount limiter. `gGlobalIoLimiter()` constructs a static `MasterLimiter`, real-time clock, and `LimiterProxy` for master-controlled global limits.

## Control Flow
Each accessor uses function-local statics, so initialization occurs on first call. `LizardClient::fs_init()` forces initialization for global and local limiters, and read/write paths later call the proxies to wait for byte grants.

## State And Persistence
The singletons hold in-memory limiter configuration, clocks, groups, and registered master packet handlers. They persist for the lifetime of the mount process.

## Dependencies And Integration Points
It depends on `common/io_limiting.h` and `mount/global_io_limiter.h`. It integrates with `LizardClient::fs_init()`, local I/O limits loaded from a config file, global I/O limits delivered by the master, and read/write enforcement.

## Risks And Test Signals
Risks include static initialization/lifetime order and packet-handler lifetime for `MasterLimiter`. Test signals come from `global_io_limiter_unittest.cc`, plus mount startup tests with and without an I/O limits config file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/g_io_limiters.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/g_io_limiters.h -->
# sources/distributed-fs/lizardfs/src/mount/g_io_limiters.h

## Purpose
This header declares global accessor functions for the mount's local and global I/O limiting infrastructure.

## Important APIs, Types, And Functions
It exposes `gMountLimiter()`, `gLocalIoLimiter()`, and `gGlobalIoLimiter()`, returning `MountLimiter&` or `LimiterProxy&`.

## Control Flow
No control flow is implemented here. Callers use these accessors to lazily obtain the singleton limiters.

## State And Persistence
No state is declared in the header. State is created in `g_io_limiters.cc` by function-local statics.

## Dependencies And Integration Points
It includes common and mount I/O limiting declarations and is consumed by `lizard_client.cc` during initialization and read/write throttling.

## Risks And Test Signals
The main risk is exposing mutable singleton references. Relevant signals are compile coverage and limiter behavior tests in `global_io_limiter_unittest.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/g_io_limiters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_chunkserver_stats.cc -->
# sources/distributed-fs/lizardfs/src/mount/global_chunkserver_stats.cc

## Purpose
This source file defines the mount-instance-global chunkserver statistics object.

## Important APIs, Types, And Functions
It defines `ChunkserverStats globalChunkserverStats;` declared in the matching header.

## Control Flow
There is no runtime control flow beyond global object construction before use.

## State And Persistence
The global object accumulates in-memory chunkserver statistics for one mount process. Persistence, if any, is outside this file.

## Dependencies And Integration Points
It depends on `global_chunkserver_stats.h` and `common/chunkserver_stats.h`. Other read/write/chunkserver code can include the header to update or query the shared stats.

## Risks And Test Signals
Risks are singleton lifetime and concurrent access semantics defined by `ChunkserverStats`. Test signals should come from users of chunkserver stats rather than this definition file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_chunkserver_stats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_chunkserver_stats.h -->
# sources/distributed-fs/lizardfs/src/mount/global_chunkserver_stats.h

## Purpose
This header exposes a single mount-instance-global `ChunkserverStats` object.

## Important APIs, Types, And Functions
`extern ChunkserverStats globalChunkserverStats;` is the only API. It provides shared access to statistics defined in `global_chunkserver_stats.cc`.

## Control Flow
No control flow is present.

## State And Persistence
The header declares in-memory process state only. The concrete object is allocated as a global variable in the `.cc` file.

## Dependencies And Integration Points
It includes `common/chunkserver_stats.h` and is intended for mount-side chunkserver communication modules.

## Risks And Test Signals
Risks are the usual global mutable state concerns: synchronization must be provided by `ChunkserverStats` or callers. Compile/link coverage catches duplicate or missing definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_chunkserver_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_io_limiter.cc -->
# sources/distributed-fs/lizardfs/src/mount/global_io_limiter.cc

## Purpose
This file implements local and master-backed I/O limiter plumbing for mount read/write throttling. It adapts generic `ioLimiting` primitives to LizardFS master protocol messages and Linux cgroup classification.

## Important APIs, Types, And Functions
`MasterLimiter` registers a `LIZ_MATOCL_IOLIMITS_CONFIG` packet handler, sends `cltoma::iolimit` requests with the current config version, validates `matocl::iolimit` replies, and returns granted bytes. `IolimitsConfigHandler::handle()` deserializes master config updates and calls `reconfigure_()`. `MountLimiter::request()` delegates to an `IoLimitsDatabase`; `loadConfiguration()` loads local limits and exposes configured groups. `LimiterProxy::waitForRead()` and `waitForWrite()` classify the pid with `getIoLimitGroupIdNoExcept()`, find the configured group or `unclassified`, and wait on the group's token logic until granted or deadline. `LimiterProxy::reconfigure()` atomically removes stale groups, marks removed groups dead, creates new groups, replaces groups when subsystem changes, updates `delta`, and enables/disables limiting.

## Control Flow
Local configuration is loaded at mount initialization, while global configuration arrives asynchronously from master packets. On each read/write, `LizardClient` calls local proxy first, then global proxy. If a group disappears while waiting, `Group::wait()` returns `ENOENT` and the proxy reclassifies/retries.

## State And Persistence
`MasterLimiter` stores `configVersion_` and packet-handler registration. `MountLimiter` stores an `IoLimitsDatabase`. `LimiterProxy` stores a mutex-protected map of group ids to shared `Group` objects, current subsystem, shared limiter state, clock reference, and enabled flag. State is in memory and driven by config files or master packets.

## Dependencies And Integration Points
It depends on protocol serializers/deserializers, `mastercomm` raw send/receive and packet handler registration, `IoLimitsDatabase`, token-bucket/group primitives, `io_limit_group` cgroup parsing, and syslog logging. Its primary integration point is `LizardClient::read()`/`write()`.

## Risks And Test Signals
Risks include stale config-version rejection, blocking waits under reconfiguration, dead group wakeup semantics, Linux-only `/proc` cgroup classification behavior, and returning `EPERM` when no group is usable. `global_io_limiter_unittest.cc` validates deadlines, no-sleep paths, group death, throughput changes, exact timing across deltas, multi-mount aggregate throughput, and bounded master request counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_io_limiter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_io_limiter.h -->
# sources/distributed-fs/lizardfs/src/mount/global_io_limiter.h

## Purpose
This header declares mount-specific limiter types that connect generic I/O limiting to master communication and local mount configuration.

## Important APIs, Types, And Functions
`MasterLimiter : Limiter` sends requests to the master and owns an inner `IolimitsConfigHandler : PacketHandler`. `MountLimiter : Limiter` serves requests from a local `IoLimitsDatabase` and can `loadConfiguration()`. `LimiterProxy` wraps any `Limiter`, classifies pids into groups, and exposes `waitForRead()`/`waitForWrite()` with deadlines.

## Control Flow
The constructor for `LimiterProxy` registers a reconfiguration callback on the wrapped limiter. Reconfiguration and waits are implemented in the `.cc` file.

## State And Persistence
The header defines the shape of in-memory limiter state: config version, handler, database, shared state, mutex, subsystem, group map, enabled flag, and clock reference.

## Dependencies And Integration Points
It includes `common/io_limiting.h` and `mount/mastercomm.h`, and is used by `g_io_limiters.*`, `lizard_client.cc`, and limiter tests.

## Risks And Test Signals
Because `LimiterProxy` stores references to external `Limiter` and `Clock` objects, lifetime must exceed the proxy. Tests in `global_io_limiter_unittest.cc` exercise timing and reconfiguration contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_io_limiter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_io_limiter_unittest.cc -->
# sources/distributed-fs/lizardfs/src/mount/global_io_limiter_unittest.cc

## Purpose
This file tests the timing and concurrency behavior of mount I/O limiting. Many tests are integration-style because limiter correctness depends on clocks, groups, proxy logic, and token database behavior interacting.

## Important APIs, Types, And Functions
`TestingLimiter` exposes `callReconfigure()`. `UnlimitedLimiter` grants every request. `ManuallyAdjustedClock` blocks sleepers until manually advanced and aborts on timeout to catch hangs. `FastClock` jumps directly to requested sleep times. `IoLimitsDatabaseLimiter` wraps `IoLimitsDatabase` and counts request calls. Tests cover `Group::wait()`, `Group::die()`, `LimiterProxy::waitForRead()`, and shared throughput across multiple proxies.

## Control Flow
Simple tests check immediate deadline timeout and no sleeping when unlimited. Future-based tests launch many async operations, reconfigure limits, advance manual clocks, and assert exactly how many operations complete per tick. The exact-time test computes expected microseconds from bytes, delta, and throughput. Multi-mount tests verify several `LimiterProxy` instances share one underlying limiter. Request-count tests ensure the proxy aggregates waits and does not call the limiter excessively.

## State And Persistence
State is test-local: clocks, databases, groups, proxies, futures, atomics, condition variables, and counters. There is no persistence.

## Dependencies And Integration Points
It depends on GoogleTest, `<future>`, protocol constants, common I/O limiting classes, `IoLimitsDatabase`, and unit-test packet helpers. It validates behavior implemented across `global_io_limiter.*` and common limiter primitives.

## Risks And Test Signals
These tests are sensitive to async scheduling and use abort-based deadlock detection. They strongly signal expected limiter semantics: deadline handling, no unnecessary sleeps, dead-group cancellation, reconfiguration wakeups, aggregate throughput fairness, and bounded master communication. Missing cgroup mocks leave group-removal-through-classification behavior less directly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/global_io_limiter_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/group_cache.h -->
# sources/distributed-fs/lizardfs/src/mount/group_cache.h

## Purpose
`GroupCache` caches sets of primary/secondary Unix groups and maps each set to a compact integer id that can be sent to the master instead of resending the full group vector on every request.

## Important APIs, Types, And Functions
`GroupCache::Groups` aliases the protocol credentials group container. `GroupHash` hashes every group id with `hash_combine()`. `find()` returns `{index, found}` for a group vector. `put()` increments a wrapping id counter below `2^31`, inserts the group vector into a 1024-entry `GenericLruCache`, and returns the id. `findByIndex()` reverse-lookups the group vector by id. `reset()` clears cache and counter. Constants include `kMaxGroupId` and `kDefaultGroupsSize`.

## Control Flow
All public operations take a mutex, making cache operations safe for concurrent FUSE requests. `LizardClient::updateGroups()` uses `find()`/`put()` and sends newly assigned group sets to the master; reconnect handling calls `reset()`.

## State And Persistence
The cache stores group-vector-to-index mappings and a monotonically incremented, wrapping index. It is in-memory only and is reset when the master connection is lost.

## Dependencies And Integration Points
It depends on `GenericLruCache`, `small_vector`, and `cltoma::updateCredentials` protocol definitions. It integrates with request context conversion in `mfs_fuse.cc` and credential registration in `lizard_client.cc`.

## Risks And Test Signals
Risks include id reuse after wraparound, eviction causing master re-registration, reverse lookup misses, and dependence on vector ordering. Test signals should cover repeated group sets, eviction behavior, reset on reconnect, and concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/group_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/io_limit_group.cc -->
# sources/distributed-fs/lizardfs/src/mount/io_limit_group.cc

## Purpose
This file parses Linux `/proc/<pid>/cgroup` data to classify a process into an I/O limit group for a configured cgroup subsystem.

## Important APIs, Types, And Functions
`skipHierarchy()` skips the hierarchy id up to the first colon. `searchSubsystems()` scans comma-separated subsystem names and returns true only on exact subsystem matches followed by comma or colon. `getIoLimitGroupId(std::istream&, subsystem)` parses lines until it finds the subsystem and returns the group path after the second colon, otherwise throws `GetIoLimitGroupIdException`. `getIoLimitGroupId(pid, subsystem)` opens `/proc/<pid>/cgroup`. `getIoLimitGroupIdNoExcept()` catches classification errors and returns `kUnclassified`.

## Control Flow
The parser processes each line with a `stringstream` configured to throw on EOF while parsing structural fields; parse failures become `GetIoLimitGroupIdException` unless the underlying input is truly exhausted. The no-throw wrapper is used by `LimiterProxy` so missing cgroup information falls back to an unclassified group.

## State And Persistence
No persistent state is stored. The only external state read is `/proc/<pid>/cgroup`.

## Dependencies And Integration Points
It depends on C++ streams, `/proc`, `common/io_limit_group.h` for `IoLimitGroupId` and `kUnclassified`, and the exception helper. It integrates with `global_io_limiter.cc` process classification.

## Risks And Test Signals
Risks include blocking or malformed stream parsing loops, Linux-specific `/proc` assumptions, exact subsystem matching, and cgroup v2 format differences. `io_limit_group_unittest.cc` covers empty input, no match, prefix/suffix non-matches, minimal valid lines, comma lists, and second-line matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/io_limit_group.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/io_limit_group.h -->
# sources/distributed-fs/lizardfs/src/mount/io_limit_group.h

## Purpose
This header declares cgroup-to-I/O-limit-group classification helpers and the exception type used when classification fails.

## Important APIs, Types, And Functions
`GetIoLimitGroupIdException` is declared with the project exception macro. `getIoLimitGroupId(std::istream&, subsystem)` parses `/proc/*/cgroup` formatted data. `getIoLimitGroupId(pid, subsystem)` reads the process file. `getIoLimitGroupIdNoExcept(pid, subsystem)` returns `kUnclassified` on error.

## Control Flow
No implementation is present. The API separates strict parsing from fallback classification so callers can choose error behavior.

## State And Persistence
No state is stored. Implementations read either a supplied stream or `/proc`.

## Dependencies And Integration Points
It depends on `common/exception.h` and `common/io_limit_group.h`. It is consumed by `global_io_limiter.cc` and tested by `io_limit_group_unittest.cc`.

## Risks And Test Signals
The contract depends on Linux cgroup text format. Tests should verify exact matching and fallback-to-unclassified behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/io_limit_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/io_limit_group_unittest.cc -->
# sources/distributed-fs/lizardfs/src/mount/io_limit_group_unittest.cc

## Purpose
This unit test file validates parsing of `/proc/<pid>/cgroup`-formatted input into I/O limit group ids.

## Important APIs, Types, And Functions
Each GoogleTest case constructs a `std::stringstream` and calls `getIoLimitGroupId(input, "blkio")`. Tests expect either a returned path or `GetIoLimitGroupIdException`.

## Control Flow
The suite checks empty input, no matching subsystem, subsystem suffix/prefix false positives, a minimal `:blkio:/test` line, comma-separated subsystem lists, and matching on a later line.

## State And Persistence
State is test-local and in memory. It avoids reading real `/proc`.

## Dependencies And Integration Points
It depends on GoogleTest and `mount/io_limit_group.h`. It is the direct signal for parser behavior used by `LimiterProxy`.

## Risks And Test Signals
The tests do not cover malformed lines that partially match, cgroup v2 unified hierarchy, or the `pid` and no-throw overloads. Existing cases signal exact subsystem matching and line scanning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/io_limit_group_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/iovec_traits_unittest.cc -->
# sources/distributed-fs/lizardfs/src/mount/iovec_traits_unittest.cc

## Purpose
This test validates helper functions for copying data into and between POSIX `iovec` arrays, which matters because the FUSE read path replies with `fuse_reply_iov()`.

## Important APIs, Types, And Functions
The test calls `memcpyIoVec()` to scatter bytes from a contiguous buffer into an iovec array, then calls `copyIoVec()` to copy from one iovec array to another. It uses zero-length entries and a `{nullptr, 0}` entry to check skip/termination behavior.

## Control Flow
The test fills `out` with `"abcdefghi"` through discontiguous iovecs, then copies 17 bytes into another region and asserts the copied string equals the original output.

## State And Persistence
Only stack buffers and local vectors are used.

## Dependencies And Integration Points
It depends on GoogleTest and `mount/client/iovec_traits.h`. It indirectly supports confidence in `mfs_fuse.cc` read replies where `ReadCache::Result::toIoVec()` supplies iovecs to libfuse.

## Risks And Test Signals
The test signals handling of zero-length iovecs and byte accounting. It does not cover partial destination exhaustion, invalid nonzero null bases, or very large vector counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/iovec_traits_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/lizard_client.cc -->
# sources/distributed-fs/lizardfs/src/mount/lizard_client.cc

## Purpose
This is the central mount-side filesystem client implementation. It translates higher-level FUSE-facing `LizardClient` calls into master RPCs, chunkserver read/write cache operations, special inode handling, ACL/xattr conversion, directory-entry caching, credential registration, I/O limiting, advisory locking, statistics, and subsystem initialization/termination.

## Important APIs, Types, And Functions
Global state includes `gGroupCache`, `gDirEntryCache`, readdir sessions, cache timeouts, `keep_cache`, `use_rwlock`, `gDirectIo`, lock request counters, stats counters, and `acl_cache`. `updateGroups()` compresses secondary group vectors into master-registered group ids; `masterDisconnectedCallback()` resets group and dir caches and marks readdir sessions restarted. Attribute helpers convert protocol `Attributes` into `stat`, build mode/attribute strings, and map `RequestException` to system errors. Core filesystem APIs include `statfs`, `access`, `lookup`, `getattr`, `setattr`, `mknod`, `unlink`, `undel`, `mkdir`, `rmdir`, `symlink`, `readlink`, `rename`, `link`, `opendir`, `readdir`, `readreserved`, `readtrash`, `create`, `open`, `release`, `read`, `write`, `flush`, `fsync`, xattrs, locks, snapshot/goal/chunk queries, `fs_init`, and `fs_term`.

## Control Flow
Metadata operations validate special names/inodes, name lengths, permissions, and then call `fs_*` master RPCs using `RETRY_ON_ERROR_WITH_UPDATED_CREDENTIALS` so missing group registrations trigger credential upload and one retry. Directory reads first consult `DirEntryCache`, then fetch batches from the master, insert sequences and end markers, and repair offsets when the master restarts by searching for the last-read inode. Open/create allocate `finfo` objects with read or write pipeline state. Reads enforce local and global I/O limits, switch write descriptors to read mode by flushing pending data, align to block boundaries, and call `read_data()`. Writes enforce the same limiters, switch read descriptors to write mode, call `write_data()`, and invalidate inode cache entries. Flush/fsync drain pending writes; release closes lock state and file info.

## State And Persistence
This file owns most mount-process state: credential group cache, directory cache, ACL cache, special tweak variables, file-handle `finfo` objects, read/write cache handles, readdir sessions, lock usage flags, and stats counters. Durable filesystem effects occur through master RPCs and chunkserver write pipelines; local state is cache/control state and is reset or invalidated on mutations and reconnects.

## Dependencies And Integration Points
It integrates with `mastercomm`, `masterproxy`, `readdata`, `writedata`, `special_inode`, `direntry_cache`, `acl_cache`, ACL converters, rich ACL and optional OS X ACL converters, symlink cache, oplog/stats, I/O limiters, tweaks, protocol serializers, and chunkserver metadata. It is called by `mfs_fuse.cc` for normal FUSE requests and by administrative code for snapshot/goal/chunk queries.

## Risks And Test Signals
Risks include wide global mutable state, manual `finfo` allocation/destruction, multi-lock ordering around file reads/writes/flushes, cache invalidation gaps after mutations, master restart handling in readdir, xattr/ACL conversion failures, lock send/recv threading constraints, and mixed LizardFS-status vs errno inputs in a few admin error paths. Test signals include FUSE operation tests, ACL/xattr tests, read/write cache tests, limiter tests, direntry-cache restart scenarios, file-lock interrupt tests, and integration tests against a master/chunkserver cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/lizard_client.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/lizard_client.h -->
# sources/distributed-fs/lizardfs/src/mount/lizard_client.h

## Purpose
This header defines the public mount-side `LizardClient` API consumed by the FUSE adapters and other mount utilities. It centralizes default mount parameters, request/response value types, and the operation surface implemented in `lizard_client.cc`.

## Important APIs, Types, And Functions
`FsInitParams` captures all runtime initialization settings with defaults for master connection, retries, chunkserver timeouts, read cache, write cache, symlink cache, FUSE cache behavior, mkdir sgid handling, sugid clearing, rw-lock use, ACL cache, verbosity, and I/O limits config. `FileInfo` mirrors per-open FUSE file state. `EntryParam`, `AttrReply`, `DirEntry`, and `XattrReply` carry operation replies. `RequestException` stores both LizardFS and system error codes. Function declarations cover normal filesystem operations, special reads, read/write/flush/fsync, directory sessions, trash/reserved reads, xattrs, access, locks and interrupts, snapshots, goals, statfs, chunk queries, chunkserver listing, and init/term.

## Control Flow
No implementation flow exists, but this header defines which operations FUSE callbacks can call and which data they must pass. `FsInitParams` is filled by `main.cc` from parsed mount options and then passed to `fs_init()`.

## State And Persistence
Types in this header represent transient mount state: contexts, open file handles, replies, and initialization parameters. Persistent filesystem changes are performed by implementation functions.

## Dependencies And Integration Points
It depends on protocol types for chunkservers, locks, named inode entries, group cache/context, read cache, and stat definitions. It is the bridge between `mfs_fuse.cc`, `main.cc`, special inode/admin callers, and the client implementation.

## Risks And Test Signals
Changing this header has broad blast radius across FUSE, admin utilities, and tests. Risks include default mismatch with `mount_config.h`, bitfield assumptions in `FileInfo`, FUSE generation type differences, and status/errno mapping through `RequestException`. Compile coverage and integration tests across normal operations are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/lizard_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/lizard_client_context.h -->
# sources/distributed-fs/lizardfs/src/mount/lizard_client_context.h

## Purpose
This header defines `LizardClient::Context`, the per-request identity and permission context passed from FUSE into all client operations.

## Important APIs, Types, And Functions
`Context` stores `uid`, primary `gid`, local `pid`, `umask`, and a protocol-compatible `gids` container for primary and secondary groups. It defines `IdType`, `MaskType`, `GroupsContainer`, and `kIncorrectId`. Constructors support an invalid empty context, uid/gid/pid/umask with one group, or uid plus a full group container. `isValid()` returns true when the group container is non-empty.

## Control Flow
There is no complex control flow. FUSE adapters construct the context from `fuse_req_ctx()`, optionally expand secondary groups, and `LizardClient::updateGroups()` may replace `gid` with an encoded group-cache id before RPCs.

## State And Persistence
The context is transient request state. `pid` is intentionally local and never sent to the master; uid/gid/groups/umask feed permission checks and create/setattr behavior.

## Dependencies And Integration Points
It depends on `cltoma::updateCredentials::GroupsContainer`. It integrates with `mfs_fuse.cc` context creation, `GroupCache`, credential registration, and every `LizardClient` operation that talks to the master.

## Risks And Test Signals
Risks include invalid contexts with empty groups, gid rewriting after group-cache encoding, and platform differences in secondary group discovery. Test signals include permission-sensitive FUSE operations, secondary group registration/retry behavior, and reconnect handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/mount/lizard_client_context.h -->
