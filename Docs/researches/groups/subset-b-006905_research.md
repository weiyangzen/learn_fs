# Research: subset-b-006905

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/SyntheticClient.cc -->
# sources/distributed-fs/ceph/src/client/SyntheticClient.cc

## Purpose
`SyntheticClient.cc` implements a CephFS synthetic workload driver for `StandaloneClient`. It parses `--syn` command sequences into global mode/argument queues, mounts a client, executes metadata, data, trace-replay, object, snapshot, and stress workloads, then unmounts and shuts down.

## Important APIs, Types, and Functions
The file defines `parse_syn_options()`, global workload queues (`syn_modes`, `syn_iargs`, `syn_sargs`), `synthetic_client_thread_entry()`, and the full `SyntheticClient` method set declared in the header. `run()` is the central dispatcher from `SYNCLIENT_MODE_*` values to helpers. Trace replay uses `play_trace(Trace&, string&, bool)`. File tests use `write_file()`, `read_file()`, `read_random()`, `read_random_ex()`, and `chunk_file()`. Metadata tests use `make_dirs()`, `stat_dirs()`, `read_dirs()`, `make_files()`, `full_walk()`, `random_walk()`, `thrash_links()`, `import_find()`, lookup helpers, and snapshot helpers. Objecter-level tests use `create_objects()` and `object_rw()`.

## Control Flow
`parse_syn_options()` removes recognized synthetic options from argv and appends modes plus typed arguments. `run()` picks user permissions, initializes and mounts the client, iterates modes, consumes the matching arguments, applies `run_only`/`exclude`/duration gates, and invokes the workload helper. `play_trace()` reads tokenized operations from `Trace`, maps trace-local ids to open file handles, low-level inode handles, directories, and object ids, then dispatches high-level POSIX calls, `ll_*` calls, and Objecter read/write/zero/stat calls.

## State and Persistence Behavior
The code mutates the mounted CephFS namespace and RADOS objects used by file layouts. It also maintains in-memory workload state: current working `filepath`, cached directory contents/subdirs, open file sets, trace handle maps, and async counters guarded by Ceph mutex/condition variables. Data-writing helpers stamp each 16-byte record with offset and client id; read helpers validate those fingerprints. Snapshot helpers create `.snap` entries and rewrite data after a snapshot.

## Dependencies and Integration Points
It depends on `Client`, `StandaloneClient`, `Trace`, `UserPerm`, `Objecter`, `Filer`, Ceph layout/object types, `C_SafeCond`, perf/debug infrastructure, and POSIX headers. It integrates with both path-based libcephfs APIs and low-level inode/Fh APIs, plus direct Objecter and Filer operations.

## Risks
This is test/stress code with intentional rough edges: many operations ignore return values, `foo()` contains infinite/debug scenarios behind constant branches, `random_walk()` aborts in its readdir population block, `overload_osd_0()` has a `while (left < 0)` condition that prevents normal positive workloads, and trace replay aborts on unknown symbols. Several helpers reseed randomness repeatedly, allocate variable-size buffers from user arguments, and use fixed path buffers.

## Test Signals
Useful test signals are successful mode parsing, clean mount/unmount, expected throughput logs, fingerprint mismatch warnings in reads, `full_walk()` nlink/frag count discrepancies, trace replay line progress, and completion of async object counters without leaked in-flight references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/SyntheticClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/SyntheticClient.h -->
# sources/distributed-fs/ceph/src/client/SyntheticClient.h

## Purpose
`SyntheticClient.h` declares the synthetic workload driver used by CephFS client test tools. It exposes mode constants, global option parsing, and the `SyntheticClient` class interface.

## Important APIs, Types, and Functions
The header defines many `SYNCLIENT_MODE_*` integer constants for random walks, trace replay, directory/file creation, read/write tests, object tests, lookup tests, snapshots, and timing/client-selection controls. `parse_syn_options(std::vector<const char*>&)` fills shared mode queues. `SyntheticClient` stores a `StandaloneClient*`, thread id, operation distribution, current path state, directory caches, open file set, run filters, and mode argument queues. Public methods include thread lifecycle, `run()`, argument accessors, stop checks, path composition, all workload helpers, trace replay, object operations, lookup helpers, chunking, and snapshot helpers.

## Control Flow
Instances copy global parse results into per-client queues. `start_thread()` launches `run()` through a pthread entrypoint; `join_thread()` waits. `run_me()`, `did_run_me()`, and `time_to_stop()` gate mode execution by client id and time.

## State and Persistence Behavior
Header state is entirely in-memory, but it drives persistent CephFS/RADOS mutations through the implementation. Directory-selection helpers use cached `contents` and `subdirs`; `clear_dir()` resets that cache after navigation or error recovery.

## Dependencies and Integration Points
It depends on `Client.h`, `Distribution`, `Trace`, `filepath`, `UserPerm`, and Ceph time/client id types. It is tightly coupled to `StandaloneClient` and CephFS low-level handles declared elsewhere.

## Risks
The mode interface is macro-based and positional: parser and dispatcher must consume exactly matching argument counts. Helper methods expose raw sizes, paths, and counts, so invalid command input can produce oversized allocations or unexpected namespace mutations.

## Test Signals
Compile coverage should confirm every declared helper has a matching implementation. Runtime tests should verify mode argument consumption order and multi-client `only`/`onlyrange` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/SyntheticClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Trace.cc -->
# sources/distributed-fs/ceph/src/client/Trace.cc

## Purpose
`Trace.cc` implements a simple line-oriented trace reader consumed by `SyntheticClient::play_trace()`.

## Important APIs, Types, and Functions
`Trace::start()` reopens the configured trace file and primes the first line. `Trace::peek_string()` returns the current line, optionally replacing a leading `/prefix` marker with the caller-provided prefix. `Trace::get_string()` returns the current token and advances to the next line. Integer reads are implemented inline in the header through `get_int()`.

## Control Flow
The reader keeps one current line buffered. `start()` deletes any previous stream, opens a new `ifstream`, aborts on failure, reads the first line, and sets `_line` to 1. Each `get_string()` calls `peek_string()`, increments `_line`, and performs `getline()` for the next token.

## State and Persistence Behavior
State is in-memory only: filename, stream pointer, current line, and line counter. It does not persist offsets between starts; every `start()` rewinds by reopening the file.

## Dependencies and Integration Points
It depends on `Trace.h`, Ceph debug/config headers, and C string helpers. Its `/prefix` expansion is coupled to synthetic trace path conventions.

## Risks
Failure to open aborts the process. The reader has no token validation, no explicit EOF error for missing arguments, and copy/assignment are declared but not implemented here, so accidental use would need definitions elsewhere or cause link errors.

## Test Signals
Tests should cover open failure, line number increments, EOF behavior, and `/prefix` substitution with empty and non-empty prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Trace.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Trace.h -->
# sources/distributed-fs/ceph/src/client/Trace.h

## Purpose
`Trace.h` declares the trace iterator used to replay synthetic operation traces.

## Important APIs, Types, and Functions
`Trace` owns `_line`, `filename`, an `ifstream*`, and current `line`. Public APIs are `start()`, `peek_string()`, `get_string()`, `get_int()`, `get_line()`, and `end()`. The destructor deletes the stream. Copy constructor and assignment are declared, indicating copy semantics are intentionally controlled.

## Control Flow
Callers construct with a filename, call `start()`, then repeatedly call `get_string()` or `get_int()` until `end()`. `peek_string()` allows inspecting the current token without advancing.

## State and Persistence Behavior
The object is a non-persistent cursor over a file. `end()` returns true when no stream exists or the stream is at EOF.

## Dependencies and Integration Points
It uses C++ streams, strings, lists, and `atoll()`. `SyntheticClient.cc` relies on one trace token per line and uses `get_int()` for numeric arguments.

## Risks
The raw `ifstream*` requires careful copy behavior. EOF and malformed integer handling are lenient; `atoll()` returns 0 for invalid strings.

## Test Signals
Trace replay tests should include token ordering, numeric conversion, EOF after final line, and prefix-expansion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/UserPerm.h -->
# sources/distributed-fs/ceph/src/client/UserPerm.h

## Purpose
`UserPerm.h` packages the effective uid, gid, and supplementary groups used by client permission checks and FUSE request forwarding.

## Important APIs, Types, and Functions
`UserPerm` stores `m_uid`, `m_gid`, `gid_count`, `gids`, and `alloced_gids`. It offers default/effective identity construction, explicit identity construction, deep-copy copy constructor/assignment, move construction, destructor, `uid()`, `gid()`, `gid_in_groups()`, `get_gids()`, `init_gids()`, `shallow_copy()`, and `print()`.

## Control Flow
Default uid/gid values of `(uid_t)-1` and `(gid_t)-1` defer to `geteuid()` and `getegid()`. `init_gids()` takes ownership of an allocated group array. Copy assignment deep-copies owned or borrowed group lists; `shallow_copy()` intentionally borrows without ownership.

## State and Persistence Behavior
All state is process-local and request-scoped. The destructor releases only arrays marked as allocated by this object.

## Dependencies and Integration Points
FUSE code builds `UserPerm` from `fuse_req_ctx()` and optionally fills groups with `fuse_req_getgroups()`. ACL code calls `gid_in_groups()` to evaluate group entries.

## Risks
Ownership is subtle: constructing with a non-owned `gidlist`, then calling `init_gids()` without first releasing an owned list could leak if misused. Move assignment is absent. `print()` omits supplementary groups.

## Test Signals
Unit coverage should exercise default identity fallback, deep copy isolation, move destruction, borrowed vs owned group arrays, and group matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/UserPerm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/barrier.cc -->
# sources/distributed-fs/ceph/src/client/barrier.cc

## Purpose
`barrier.cc` implements write/commit barrier bookkeeping for client block synchronization, tracking outstanding write callback intervals and waiting for overlapping commits to finish.

## Important APIs, Types, and Functions
The local `C_Block_Sync` context records `Client*`, inode, interval, state, owning `Barrier*`, result pointer, and intrusive hook. `BarrierContext::write_nobarrier()`, `write_barrier()`, `commit_barrier()`, and `complete()` maintain unclaimed writes and active commit barriers.

## Control Flow
Constructing `C_Block_Sync` lazily creates a per-inode `BarrierContext` in `cl->barriers` and registers the write as unclaimed. `write_barrier()` waits while any active commit span intersects the write interval, then enqueues the write. `commit_barrier()` selects outstanding writes whose intervals intersect the commit interval, moves them to a new `Barrier`, pushes it to `active_commits`, and waits on its condition. `complete()` removes the callback from either the outstanding list or the barrier write list, notifies waiters, deletes empty barriers, and marks completion.

## State and Persistence Behavior
State is in-memory per inode. It persists only for outstanding async callbacks and active commits. No on-disk state is created.

## Dependencies and Integration Points
It depends on `Client`, `Context`, Ceph mutex/condition variables, Boost intrusive lists, and Boost ICL interval sets. It is intended to support CephFS low-level block commit semantics.

## Risks
The implementation comments say current semantics are not commit-ordered. Correct intrusive-list membership is critical; calling `complete()` on an unexpected state aborts. `BarrierContext` destructor does not drain or validate outstanding entries.

## Test Signals
Tests should verify overlapping intervals block, disjoint intervals proceed, unclaimed writes are removed on completion, commit waiters wake after the last matching write, and empty barriers are deleted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/barrier.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/barrier.h -->
# sources/distributed-fs/ceph/src/client/barrier.h

## Purpose
`barrier.h` declares the write barrier data structures used by CephFS client block synchronization.

## Important APIs, Types, and Functions
It defines `barrier_interval`, `CBlockSync_State`, forward declarations for `BarrierContext` and `C_Block_Sync`, `BlockSyncList`, `Barrier`, `BarrierList`, and `BarrierContext`. `Barrier` stores a condition variable, interval set span, write list, and intrusive hook. `BarrierContext` stores the owning `Client`, inode, mutex, `outstanding_writes`, and `active_commits`.

## Control Flow
Public `BarrierContext` methods register writes, enforce barriers, commit intervals, and complete callbacks. `Barrier` exposes internals to `BarrierContext` via friendship.

## State and Persistence Behavior
The declared state is volatile synchronization state for an inode. Interval sets summarize writes claimed by active commits.

## Dependencies and Integration Points
It integrates with `Client` and Ceph type aliases, and uses Boost ICL/intrusive containers to avoid separate allocation for list nodes.

## Risks
Intrusive containers require member hooks to remain valid for the entire list membership. The header exposes only coarse operations, so implementation correctness controls all lifecycle safety.

## Test Signals
Compile-time signals include correct hook member types; runtime signals are absence of aborts or use-after-free under concurrent write/commit completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/fscrypt_uapi.h -->
# sources/distributed-fs/ceph/src/client/fscrypt_uapi.h

## Purpose
`fscrypt_uapi.h` provides Ceph FUSE-facing wrappers and restricted ioctl definitions around Linux fscrypt user API structures.

## Important APIs, Types, and Functions
On Linux it includes `<linux/fscrypt.h>`, defines `fscrypt_policy_arg` as a union of policy v1/v2, defines `fscrypt_add_key64_arg` with a 64-byte raw key buffer, and declares restricted ioctl constants for set/get policy and add-key operations.

## Control Flow
There is no executable flow. The header is consumed by FUSE ioctl handling to parse and reply to fscrypt requests.

## State and Persistence Behavior
The structs describe user/kernel ABI payloads. Persistent encryption state is stored by CephFS/FSCrypt code outside this header.

## Dependencies and Integration Points
`fuse_ll.cc` includes this header and accepts both standard and restricted fscrypt ioctl numbers. It integrates with `FSCrypt.h` and `Client` fscrypt methods.

## Risks
ABI layout must stay aligned with Linux fscrypt definitions. The definitions are Linux-only, so non-Linux builds must avoid references behind the same preprocessor guards.

## Test Signals
Builds should verify ioctl constants compile on Linux, and FUSE ioctl tests should cover v2 policy, key add/remove/status, and short-buffer errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/fscrypt_uapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/fuse_ll.cc -->
# sources/distributed-fs/ceph/src/client/fuse_ll.cc

## Purpose
`fuse_ll.cc` is CephFS's low-level FUSE adapter. It translates FUSE callbacks into `Client::ll_*` operations, manages FUSE session lifecycle, maps Ceph inode/snapshot identities to FUSE inode numbers, forwards request credentials, exposes Ceph and fscrypt ioctls, and wires invalidation/remount/interrupt callbacks back to libcephfs.

## Important APIs, Types, and Functions
The file defines `CephFuse::Handle`, the `fuse_ll_oper` operation table, helpers for errno mapping, device encoding, mountpoint detection, supplementary groups, request TLS, fake inode/snapshot tags, and many `fuse_ll_*` handlers. Key handlers include lookup/getattr/setattr, xattrs, mknod/mkdir/unlink/rmdir/symlink/rename/link, open/read/write/flush/release/fsync, opendir/readdir/releasedir/fsyncdir, statfs, locks/flock, fallocate, access, create, and ioctl. Lifecycle methods are `Handle::init()`, `start()`, `loop()`, `finalize()`, and wrapper methods on `CephFuse`.

## Control Flow
Every FUSE request begins with `fuse_ll_req_prepare()`, storing the request in thread-local state for callbacks such as umask and interrupt switching. Handlers build `UserPerm` from `fuse_req_ctx()`, optionally load supplementary groups, resolve FUSE inode numbers to `Inode*` with `iget()`, call the corresponding `Client::ll_*` method, translate negative Ceph errors to system errno, reply through FUSE, and release inode references when required. `init()` constructs FUSE arguments from Ceph config, parses mount options, registers client callbacks, and `start()` creates/mounts a FUSE session after checking whether the mountpoint already has a Ceph FUSE mount.

## State and Persistence Behavior
Persistent state lives in CephFS. Adapter state includes FUSE session/channel objects, parsed mountpoint/options, request TLS, and `g_fino_maps`, which maps Ceph inode+snapid to fake 64-bit FUSE inode tags when libcephfs is not already faking inode numbers. File and directory handles are stored in `fuse_file_info::fh`.

## Dependencies and Integration Points
It depends on libfuse low-level APIs, `Client`, `Fh`, `Inode`, `Dir`, Ceph config/debug/safe_io, ioctl ABI headers, and `FSCrypt`. It also integrates with parent daemon signaling via `fd_on_success`, kernel cache invalidation notifications, Linux `syncfs()` before snapshot mkdir when configured, and remount commands for dcache trimming.

## Risks
Reference accounting is delicate: created/lookuped inode refs are intentionally left for FUSE forget, while parents are put immediately. `fuse_ll_rename()` can leak one inode reference on early error if only one of `in`/`nin` resolves. Variable-length stack buffers for xattrs can be risky for large sizes. ioctl handling has many ABI-size branches. Fake inode stag exhaustion aborts, though comments expect snapshot counts to stay below the tag range.

## Test Signals
Integration tests should cover mount detection, FUSE2/FUSE3 builds, permission/group propagation, cache invalidation, snapshot fake inode mapping, fscrypt ioctls, Ceph layout ioctls, lock blocking behavior with single-threaded FUSE, and balanced ll ref/forget behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/fuse_ll.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/fuse_ll.h -->
# sources/distributed-fs/ceph/src/client/fuse_ll.h

## Purpose
`fuse_ll.h` declares the public `CephFuse` wrapper around the low-level FUSE adapter implementation.

## Important APIs, Types, and Functions
`CephFuse` exposes constructor/destructor, `init()`, `start()`, `mount()`, `loop()`, `finalize()`, nested `Handle`, and `get_mount_point()`. It stores an owning raw pointer to `CephFuse::Handle`.

## Control Flow
Callers construct with a `Client*` and success-signal fd, initialize using process arguments, start the FUSE session, enter the loop, then finalize.

## State and Persistence Behavior
The header exposes no persistent state. The private handle owns FUSE session objects and callback state in the implementation.

## Dependencies and Integration Points
It requires `Client` and standard string declarations from includers. `CephFuse` marks the client as a FUSE client in its implementation constructor.

## Risks
The declared `mount()` method has no implementation in the researched file, so callers should use `start()` unless another translation unit provides it. The raw pointer requires destructor/finalize discipline.

## Test Signals
Build/link tests should catch the `mount()` declaration if referenced. Lifecycle tests should call init/start/loop/finalize in expected daemon paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/fuse_ll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/ioctl.h -->
# sources/distributed-fs/ceph/src/client/ioctl.h

## Purpose
`ioctl.h` defines CephFS-specific ioctl ABI structures and command numbers shared by FUSE/client code and test utilities.

## Important APIs, Types, and Functions
It defines `CEPH_IOCTL_MAGIC`, `ceph_ioctl_layout`, layout commands `CEPH_IOC_GET_LAYOUT`, `CEPH_IOC_SET_LAYOUT`, `CEPH_IOC_SET_LAYOUT_POLICY`, `ceph_ioctl_dataloc`, `CEPH_IOC_GET_DATALOC`, and `CEPH_IOC_LAZYIO`.

## Control Flow
There is no executable control flow. FUSE ioctl handling decodes these command numbers and fills or consumes these structures.

## State and Persistence Behavior
`SET_LAYOUT` and `SET_LAYOUT_POLICY` can persist file or directory layout policy in CephFS metadata. `GET_DATALOC` reports mapping information for a file offset.

## Dependencies and Integration Points
It depends on platform ioctl headers and Ceph integer types. `fuse_ll.cc` supports `CEPH_IOC_GET_LAYOUT`; `test_ioctls.c` exercises layout and dataloc commands.

## Risks
This is a stable ABI surface: struct size, alignment, and command numbering must not drift. `sockaddr_storage` in `ceph_ioctl_dataloc` requires compatible includes and caller buffer sizing.

## Test Signals
Tests should compile on Linux and BSD/macOS guarded paths, and runtime ioctl tests should verify layout round-trips and dataloc fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/posix_acl.cc -->
# sources/distributed-fs/ceph/src/client/posix_acl.cc

## Purpose
`posix_acl.cc` implements validation, mode conversion, chmod inheritance/update, and permission checks for POSIX ACL extended-attribute blobs.

## Important APIs, Types, and Functions
`posix_acl_check()` validates ACL EA header version, entry alignment, tag ordering, and mask requirements. `posix_acl_equiv_mode()` derives Unix mode bits and reports whether the ACL has named entries or a mask. `posix_acl_inherit_mode()` applies create mode to an inherited ACL buffer. `posix_acl_access_chmod()` updates ACL owner/group/other or mask entries for chmod. `posix_acl_permits()` evaluates requested permission bits against owner, named user, group, mask, and other ACL entries.

## Control Flow
Validation walks entries in required order: user_obj, named users, group_obj, named groups, optional mask, other. Permission evaluation checks owner first, then named user, then matching groups, then other. Named users/groups and group_obj permissions are constrained by a later mask entry when present.

## State and Persistence Behavior
Functions operate directly on xattr buffers. Inheritance and chmod mutate the passed `bufferptr`; checks are read-only. Persistent ACL storage is the caller-managed xattr.

## Dependencies and Integration Points
It depends on Ceph endian integer wrappers, `bufferptr`, mode constants, and `UserPerm`. It is used by client-side permission and mode handling around `system.posix_acl_access` and `system.posix_acl_default`.

## Risks
Invalid ACLs return `-EIO` in mutating/checking paths after structural validation failure. Correct endian wrapper conversion is assumed by assigning to native `__u16`/`__u32`. Mask lookup scans forward from the matched named entry and assumes valid ordering.

## Test Signals
Tests should cover minimal three-entry ACLs, named user/group requiring mask, chmod with and without mask, inherited default ACL masking, owner/group/other permit and deny cases, malformed order, wrong version, and unaligned sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/posix_acl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/posix_acl.h -->
# sources/distributed-fs/ceph/src/client/posix_acl.h

## Purpose
`posix_acl.h` declares Ceph's POSIX ACL EA wire format and helper functions.

## Important APIs, Types, and Functions
It defines ACL version, tag constants, xattr names (`system.posix_acl_access`, `system.posix_acl_default`), `acl_ea_entry`, `acl_ea_header`, and declarations for validation, mode equivalence, inheritance, chmod update, and permission evaluation.

## Control Flow
The header provides no executable flow; callers pass raw xattr buffers or mutable `bufferptr` instances to the implementation helpers.

## State and Persistence Behavior
The structs describe persisted xattr data in little-endian Ceph types. Helper declarations indicate which functions may mutate ACL buffers.

## Dependencies and Integration Points
It forward-declares `UserPerm` and expects Ceph type and `bufferptr` definitions from includers. Client permission code can use the constants and helpers to match Linux POSIX ACL behavior.

## Risks
The flexible-array member `a_entries[0]` is a C-style ABI pattern requiring careful allocation and size validation. Consumers must not assume native endianness.

## Test Signals
Compile tests should include the header with necessary Ceph type definitions. Runtime tests are the same ACL matrix as the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/posix_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/test_ioctls.c -->
# sources/distributed-fs/ceph/src/client/test_ioctls.c

## Purpose
`test_ioctls.c` is a small manual test utility for CephFS ioctl behavior.

## Important APIs, Types, and Functions
`main()` opens a target file, issues `CEPH_IOC_GET_LAYOUT`, changes stripe unit/count through `CEPH_IOC_SET_LAYOUT`, fetches layout again, issues `CEPH_IOC_GET_DATALOC` for a caller-provided offset, and optionally sets a directory layout policy with `CEPH_IOC_SET_LAYOUT_POLICY` before creating and inspecting a child file.

## Control Flow
The program requires `<filename> <offset>` and optionally a directory path. It exits on the first open/ioctl failure with `perror()`. For dataloc output it formats object metadata and resolves the OSD address with `getnameinfo()`.

## State and Persistence Behavior
It creates or opens the target file, modifies layout metadata, and optionally creates `<dir>/testfile`. These changes persist in the mounted filesystem.

## Dependencies and Integration Points
It includes POSIX file/ioctl/socket headers and `ioctl.h`. It must run on a CephFS mount that supports the ioctl commands.

## Risks
The utility does not close all file descriptors on error, overwrites `new_file_name` globally, and uses fixed test layout values. It is unsuitable as an automated assertion test without output parsing and cleanup.

## Test Signals
Expected output includes initial/final layout fields, dataloc object/offset/block/osd data, and inherited directory policy on the created test file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/test_ioctls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/AioCompletionImpl.h -->
# sources/distributed-fs/ceph/src/librados/AioCompletionImpl.h

## Purpose
`AioCompletionImpl.h` defines the internal librados asynchronous completion object and callback functors used by `IoCtxImpl`.

## Important APIs, Types, and Functions
`librados::AioCompletionImpl` stores a mutex, condition variable, refcount, result, release/complete flags, object version, operation tid, complete/safe callbacks and args, read buffers, owning `IoCtxImpl*`, aio write sequence, and xlist item. It provides callback setters, wait/is-complete APIs, return/version accessors, `get()`, `_get()`, `release()`, `put()`, and `put_unlock()`. `CB_AioComplete` invokes user callbacks after operation completion. `CB_AioCompleteAndSafe` marks a completion complete and invokes both callbacks, used by flush/synthetic completion paths.

## Control Flow
Operations create or receive a completion with refcount 1. Submit paths take extra refs when contexts or waiters need ownership. Completion contexts set `rval`/`complete`, notify waiters, defer callback functors on the finish strand, then `put()`. User release marks `released` and drops a ref.

## State and Persistence Behavior
State is in-memory and synchronization-only. It mirrors completion status for RADOS operations but does not persist to cluster storage.

## Dependencies and Integration Points
It depends on Ceph mutexes, bufferlists, xlist, OSD types, C librados callback typedefs, and `IoCtxImpl`. `IoCtxImpl.cc` uses `aio_write_list_item` to implement write flush ordering.

## Risks
Callback invocation reads callback pointers outside the lock in the functors, so lifecycle relies on the retained completion reference and ordered clearing. `_get()` asserts the lock is already held. `release()` asserts single release.

## Test Signals
Tests should exercise wait before/after completion, callbacks, release/refcount deletion, read buffer return lengths, write flush waiters, and cancellation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/AioCompletionImpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/librados/CMakeLists.txt

## Purpose
`CMakeLists.txt` builds the internal and public librados targets.

## Important APIs, Types, and Functions
It creates static `librados_impl` from `IoCtxImpl.cc`, `RadosXattrIter.cc`, `RadosClient.cc`, `librados_util.cc`, and `librados_tp.cc`, linked with `legacy-option-headers`. It creates shared/static `librados` from C and C++ API translation units plus common buffer objects.

## Control Flow
When shared libraries are enabled, it sets output name `rados`, version `2.0.0`, soversion `2`, hidden inline visibility, optional exclude-libs and version-script linker flags, optional static libstdc++/gcc flags, and `LIBRADOS_SHARED=1`. It links `librados` with implementation, osdc, ceph-common, cls lock client, and platform crypto/block/GSS/external libraries. It installs the target and adds tracing dependencies when LTTng/eventtrace are enabled.

## State and Persistence Behavior
No runtime state. Build output artifacts and install targets are produced by CMake.

## Dependencies and Integration Points
This file integrates librados with Ceph's build options and tracepoint generation. Public API files depend on private `librados_impl`.

## Risks
Link flags are platform-guarded; version scripts and exclude-libs must remain compatible with non-Windows shared builds. Missing trace dependencies can break eventtrace-enabled builds.

## Test Signals
Build matrix signals include shared/static builds, eventtrace/LTTng builds, versioned symbol exports, and installation path correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/IoCtxImpl.cc -->
# sources/distributed-fs/ceph/src/librados/IoCtxImpl.cc

## Purpose
`IoCtxImpl.cc` implements the core librados pool I/O context: synchronous and asynchronous object operations, snapshots, listing, xattrs, class calls, watch/notify, write flushing, object version tracking, pool application metadata, and low-level Objecter integration.

## Important APIs, Types, and Functions
Key helpers include notification and linger completion contexts (`CB_notify_Finish`, `C_aio_linger_Complete`, `C_aio_notify_Complete`), snap completion contexts, `queue_aio_write()`, `complete_aio_write()`, `flush_aio_writes*()`, `prepare_assert_ops()`, `operate()`, `operate_read()`, `aio_operate()`, `aio_operate_read()`, many typed sync/async wrappers, watch/notify methods, `object_list_slice()`, and application metadata methods. `C_aio_Complete`, `C_aio_stat_Ack`, and `C_aio_stat2_Ack` bridge Objecter completions to `AioCompletionImpl`.

## Control Flow
Synchronous operations build an `ObjectOperation`, optionally consume and clear `assert_ver`, submit an Objecter op with `C_SafeCond`, block on a condition, set `last_objver`, and return the result or read length. Async operations configure `AioCompletionImpl`, submit Objecter ops with completion contexts, and rely on finish-strand callback dispatch. Writes call `queue_aio_write()` before submit; `C_aio_Complete::finish()` calls `complete_aio_write()` so flushes can wake in write-sequence order. Watch/notify creates Objecter linger ops, attaches user contexts, submits watch/unwatch/notify operations, and cancels linger state on failure or completion.

## State and Persistence Behavior
The object holds pool id/name context, namespace (`oloc.nspace`), read snap (`snap_seq`), write snap context (`snapc`), extra flags, notification timeout, assert version, `last_objver`, write sequence/list/waiters, Objecter pointer, and RadosClient pointer. Persistent effects are RADOS object mutations, xattrs, snapshots, watches, notifications, cache hints, scrub queries, and pool application metadata via monitor commands.

## Dependencies and Integration Points
It depends on `IoCtxImpl.h`, `AioCompletionImpl`, `PoolAsyncCompletionImpl`, `RadosClient`, Objecter APIs, Ceph buffer/object/snap types, Boost.Asio finish strands, tracing (`EventTrace`, ZTracer, optional blkin/OpenTelemetry), monitor commands, and OSD map access.

## Risks
Async lifecycle is refcount-sensitive. `C_aio_stat_Ack` constructors assert `!c->io`, but their finish methods use `c->io->client`, relying on the submitter setting `c->io` after construction. Read completions into user buffers must be contiguous or return `-ERANGE`. `prepare_assert_ops()` consumes `assert_ver`, so retries must account for one-shot assertion state. Watch/notify linger cancellation ordering is critical to avoid leaks or dropped callbacks.

## Test Signals
Coverage should include sync and async read/write/remove/stat/xattr paths, object version updates, write flush ordering, snapshot read/write rejection, self-managed snap async completion, class calls with replica-read flag masking, watch/unwatch invalid cookies, notify ack/finish sequencing, cancellation, application metadata monitor commands, and object-list slicing boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/IoCtxImpl.cc -->
