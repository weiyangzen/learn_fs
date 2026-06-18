# subset-b-007061 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/call-stub.c -->
## sources/distributed-fs/glusterfs/libglusterfs/src/call-stub.c

### Purpose
`call-stub.c` implements the allocation, storage, replay, unwind, and destruction path for GlusterFS `call_stub_t` objects. A stub captures either a forward FOP invocation (`wind == 1`) or a callback/unwind payload (`wind == 0`) so translators can queue work, resume it later, or synthesize error unwinds without keeping the original stack active.

### Important APIs, Types, And Functions
The file centers on `call_stub_t`, defined in `glusterfs/call-stub.h`, whose fields include a list hook, `call_frame_t *frame`, FOP callback unions, `glusterfs_fop_t fop`, `wind`, `default_args_t args`, and `default_args_cbk_t args_cbk`.

`stub_new(frame, wind, fop)` allocates and initializes a stub, including the list heads and callback directory-entry list. Every public `fop_*_stub` and `fop_*_cbk_stub` constructor delegates to it, stores the function pointer in `fn` or `fn_cbk`, and deep/ref-count stores arguments through the `args_*_store` helpers from `default-args`.

The constructor family covers the normal filesystem surface: lookup/stat/fstat, create/open/read/write/put, namespace ops, xattr ops, locks, readdir/readdirp, rchecksum, setattr, fallocate/discard/zerofill, ipc, lease, seek, get/set active locks, icreate, namelink, and copy-file-range. A few internal helpers fill callbacks manually where no generic store helper is used, such as `args_icreate_store_cbk` and `args_namelink_store_cbk`.

`call_resume_wind()` switches on `stub->fop` and calls the captured forward FOP. `call_resume_unwind()` does the same for callback paths using `STUB_UNWIND`, which either invokes the stored callback function or falls back to `STACK_UNWIND_STRICT`. `call_resume()` and `call_resume_keep_stub()` remove the stub from its list, set `THIS` to `stub->frame->this` for the duration, and resume the proper path. `call_unwind_error()` and `call_unwind_error_keep_stub()` overwrite `op_ret`/`op_errno` and unwind an error. `call_stub_destroy()` wipes either `args` or `args_cbk` and frees the stub.

### Control Flow
A caller constructs a stub with a FOP-specific constructor. The constructor validates selected mandatory arguments, allocates the stub, writes the function pointer, and stores arguments with ownership-preserving copies or refs. Later, `call_resume()` removes it from any queue, binds `THIS`, invokes the wind or unwind switch, restores `THIS`, and destroys the stub. The keep-stub variants perform the same replay but intentionally leave ownership of argument cleanup to the caller.

### State And Persistence Behavior
State is in-memory only. The file persists no data to disk. It manipulates reference-counted GlusterFS runtime objects such as `dict_t`, `fd_t`, `inode_t`, `loc_t`, `iobref`, and directory-entry lists through `args_*_store` and `args_*_wipe`. The `list` hook makes stubs suitable for translator queues. The `THIS` global is temporarily rebound around replay, which is part of runtime execution context state rather than durable state.

### Dependencies And Integration Points
This code depends on `glusterfs/call-stub.h`, `glusterfs/default-args.h`, stack macros, `GF_CALLOC/GF_FREE`, `GF_VALIDATE_OR_GOTO`, `gf_msg_callingfn`, `STACK_UNWIND_STRICT`, and the translator FOP type system. It integrates with translators that defer or serialize operations, with sync/async stack unwinding, and with the generic `default_args` ownership model.

### Risks And Edge Cases
The switch statements must remain synchronized with `call_stub_t` unions, constructor coverage, and `glusterfs_fop_t` values. Missing a new FOP in either resume switch causes an invalid-FOP log instead of replay. Constructor validation is uneven: some constructors validate primary pointers while others rely on lower layers or store helpers. `fop_fgetxattr_cbk_stub()` creates a stub with `GF_FOP_GETXATTR` rather than `GF_FOP_FGETXATTR`, which is worth reviewing because the unwind switch has distinct cases. `fop_setactivelk_cbk_stub()` stores callback xdata into `stub->args.xdata` instead of `stub->args_cbk.xdata`, which looks suspicious for cleanup and unwind behavior. Keep-stub APIs can leak retained refs if callers do not later destroy or wipe the stub.

### Test Signals
Useful tests should cover deferred replay for representative wind and unwind FOPs, error unwind synthesis, argument ref/wipe balance under ASAN or leak checking, missing-callback fallback to `STACK_UNWIND_STRICT`, directory-entry cleanup, active-lock callback xdata ownership, and parity between every new `GF_FOP_*` enum value and the constructor/resume/unwind switch coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/call-stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/changelog.h -->
## sources/distributed-fs/glusterfs/libglusterfs/src/changelog.h

### Purpose
`changelog.h` defines the public changelog consumer interface and event ABI used by GlusterFS components that register for brick changelog events. It is a header-only contract: it declares event types, event payload structures, callback signatures, brick subscription metadata, and the legacy and generic registration APIs.

### Important APIs, Types, And Functions
`CHANGELOG_EV_SELECTION_RANGE` defines the bit range used for event filtering. The event bit masks are `CHANGELOG_OP_TYPE_JOURNAL`, `OPEN`, `CREATE`, `RELEASE`, `BR_RELEASE`, and `CHANGELOG_OP_TYPE_MAX`.

Payload structures include `ev_open`, `ev_creat`, `ev_release`, `ev_release_br`, and `ev_changelog`. `changelog_event_t` carries `ev_type` plus a union of those payloads. `CHANGELOG_EV_SIZE` exposes the ABI size of a changelog event.

Callback typedefs define plugin hooks: `CALLBACK`, `INIT`, `FINI`, `CONNECT`, and `DISCONNECT`. `struct gf_brick_spec` describes one watched brick with `brick_path`, event `filter`, hook pointers, and an opaque `ptr`.

The legacy API is `gf_changelog_register`, `gf_changelog_scan`, `gf_changelog_start_fresh`, `gf_changelog_next_change`, and `gf_changelog_done`. The newer generic API is `gf_changelog_init` and `gf_changelog_register_generic`.

### Control Flow
Consumers initialize the changelog subsystem, register one or more bricks, scan for available changes, iterate paths with `gf_changelog_next_change`, and acknowledge processed changelog files with `gf_changelog_done`. Under the generic API, each brick spec can receive lifecycle callbacks for init/fini/connect/disconnect and per-event callbacks.

### State And Persistence Behavior
The header itself holds no state, but the API represents persistent changelog state: brick paths, scratch directories, changelog files, reconnect policy, event filters, and done/acknowledged changelog files. `ev_changelog.path` is a fixed `PATH_MAX` buffer, and event structures embed GFIDs and flags directly for stable handoff.

### Dependencies And Integration Points
The file forward-declares `struct gf_brick_spec` and relies on external definitions for `PATH_MAX`, `ssize_t`, and integer types through including translation units. It integrates with changelog libraries, bitrot stub release events, geo-replication or indexing consumers, and brick-level event delivery.

### Risks And Edge Cases
This is ABI-sensitive because `changelog_event_t` and `CHANGELOG_EV_SIZE` may be consumed across library boundaries. The comment says "Max bit shiter", indicating stale or typo-prone documentation. Event selection assumes no more than five bit positions unless the range is updated. Fixed-size path storage can truncate if producers are not careful. Callback typedefs use raw `void *` and `char *`, so ownership and lifetime must be documented by implementers.

### Test Signals
Tests should validate event filter bit masks, `CHANGELOG_EV_SIZE` stability where ABI matters, legacy scan/next/done flows, generic multi-brick registration, callback ordering on connect/disconnect/fini, path length handling, and logical release events from bitrot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/changelog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/checksum.c -->
## sources/distributed-fs/glusterfs/libglusterfs/src/checksum.c

### Purpose
`checksum.c` supplies the checksum primitives used by GlusterFS rsync-style workflows and checksum FOPs. It provides a weak rolling-style checksum and strong cryptographic digests over caller-provided memory buffers.

### Important APIs, Types, And Functions
`gf_rsync_weak_checksum(unsigned char *buf, size_t len)` returns a `uint32_t` Adler-32 value from zlib. `gf_rsync_strong_checksum(unsigned char *data, size_t len, unsigned char *sha256_md)` writes a SHA-256 digest using OpenSSL `SHA256`. `gf_rsync_md5_checksum(unsigned char *data, size_t len, unsigned char *md5)` writes an MD5 digest using OpenSSL `MD5`.

### Control Flow
Each function is a direct wrapper. The weak checksum calls `adler32(0, buf, len)`. The strong checksum calls OpenSSL SHA-256 over the full buffer. The MD5 helper calls OpenSSL MD5 over the full buffer. There is no allocation, no locking, and no retry logic.

### State And Persistence Behavior
The file has no persistent state. All outputs are written into caller-owned buffers. The caller must provide digest buffers of the correct OpenSSL sizes.

### Dependencies And Integration Points
It depends on `<zlib.h>`, `<openssl/sha.h>`, `<openssl/md5.h>`, and basic C headers. It integrates with rsync checksum logic and with FOPs such as rchecksum that need weak and strong checksum pairs for data comparison or synchronization.

### Risks And Edge Cases
There is no NULL-pointer validation or output-size validation. The comment says these functions are only called for pathnames and therefore do not need arbitrary long data handling, but the signatures accept any `size_t`; callers must enforce intended use. MD5 is cryptographically weak and should be treated only as a compatibility checksum. OpenSSL 3 builds may warn about low-level MD5 APIs.

### Test Signals
Tests should compare known Adler-32, SHA-256, and MD5 vectors, verify zero-length buffers, exercise non-ASCII byte input, and run with sanitizer coverage for NULL or undersized output buffer misuse at callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/checksum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/circ-buff.c -->
## sources/distributed-fs/glusterfs/libglusterfs/src/circ-buff.c

### Purpose
`circ-buff.c` implements a small thread-safe circular buffer abstraction for storing timestamped opaque pointers. It supports either overwrite-on-full ring behavior or `use_once` behavior where additions fail after capacity is reached.

### Important APIs, Types, And Functions
The public type `buffer_t` owns `w_index`, `used_len`, `size_buffer`, an array of `circular_buffer_t *`, a data destructor callback, a mutex, and the `use_once` policy. Each `circular_buffer_t` stores a `struct timeval tv` and `void *data`.

`cb_buffer_new()` allocates and initializes a buffer and mutex. `cb_add_entry_buffer()` locks and delegates to `__cb_add_entry_buffer()`. `__cb_add_entry_buffer()` inserts a new item, optionally destroys an overwritten entry, timestamps it with `gettimeofday`, advances `w_index`, and returns the next write index. `cb_buffer_dump()` iterates entries in chronological ring order for reusable buffers and index order for use-once buffers. `cb_buffer_show()` logs basic state. `cb_buffer_destroy()` frees entries, their data, the pointer array, the mutex, and the buffer.

### Control Flow
Creation allocates the owner and the entry pointer array. Adding an item acquires the mutex, checks capacity policy, destroys the current write slot if overwriting, allocates a new entry, stores the item and timestamp, advances modulo capacity, and updates `used_len`. Dumping acquires the mutex and invokes a caller-provided dumper for each entry. Destruction iterates the used entries and invokes the optional data destructor before freeing memory.

### State And Persistence Behavior
State is entirely in memory. The buffer owns the `circular_buffer_t` wrappers and, by convention, owns entry data enough to pass it to `destroy_buffer_data` and then `GF_FREE(cb->data)`. Each entry records insertion wall-clock time. No contents are persisted.

### Dependencies And Integration Points
It depends on `glusterfs/circ-buff.h`, GlusterFS allocation/logging macros, `pthread_mutex_t`, `gettimeofday`, and the caller-supplied destroy/dump callbacks. Integration points are diagnostic buffers, recent-event tracking, and translator-local telemetry that needs bounded memory.

### Risks And Edge Cases
`cb_buffer_new()` accepts `buffer_size == 0`; later modulo operations in add/dump would divide by zero. `cb_buffer_destroy()` iterates only `i < used_len`, which is not the same as all occupied slots after ring wrap; entries above `used_len - 1` can be missed when `w_index` has wrapped. `cb_buffer_dump()` copies `used_len`, `w_index`, and `size_buffer` before acquiring the lock, so it can observe inconsistent state under concurrent mutation. `cb_destroy_data()` calls a caller destructor and then always `GF_FREE(cb->data)`, which is only correct if all stored data is GlusterFS-allocated and the destructor does not already free it. Add paths do not validate `buffer`.

### Test Signals
Tests should cover normal insertion order, overwrite behavior, use-once full behavior, destroy callback ownership, wrap-around destroy correctness, dump under concurrent add, zero-capacity rejection, and timestamp population when `gettimeofday` succeeds or fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/circ-buff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/client_t.c -->
## sources/distributed-fs/glusterfs/libglusterfs/src/client_t.c

### Purpose
`client_t.c` manages GlusterFS client identity objects and the process-wide client table attached to an xlator context. It handles allocation, lookup by client UID and auth data, bind/reference lifetimes, disconnect/destroy notifications through translator graphs, scratch client context slots, and statedump helpers for client fd tables and inode tables.

### Important APIs, Types, And Functions
`gf_clienttable_alloc()` allocates a `clienttable_t`, initializes its lock, and expands it to `GF_CLIENTTABLE_INITIAL_SIZE`. `gf_client_get()` either finds an existing matching `client_t` and increments its bind ref or allocates a new client, stores auth/subdir metadata, initializes atomics and scratch context lock, and installs it into the free-list table. `gf_client_put()` decrements the bind ref and unrefs when the last bind detaches. `gf_client_ref()` and `gf_client_unref()` manage the object refcount. `client_destroy()` removes the table entry, re-chains it onto the free list, invokes graph-wide destroy callbacks, releases subdir/auth/name state, destroys locks, and frees the variable-sized client allocation.

`gf_client_disconnect()` walks all graphs and invokes translator `client_disconnect` callbacks. `client_ctx_set/get/del()` provide a fixed-size per-client scratch context keyed by pointer identity. `gf_client_dump_fdtables_to_dict()`, `gf_client_dump_fdtables()`, `gf_client_dump_inodes_to_dict()`, and `gf_client_dump_inodes()` expose state for diagnostics and process dumps.

### Control Flow
The client table uses an array plus integer free list. Expansion allocates a larger array, copies old entries, chains new entries, and moves `first_free` to the previous maximum index. `gf_client_get()` scans allocated entries for a matching UID and auth tuple; on miss it allocates a flexible-array `client_t`, may copy auth bytes and subdir mount, then consumes `first_free`. If consuming the last free entry, it expands before final installation. Destruction reverses that installation by nulling the slot and pushing it back onto the free list.

### State And Persistence Behavior
State is in-memory and shared under `clienttable->lock` plus per-client atomic counters. `bind` represents active logical bindings; `count` represents object references. `auth.data`, `subdir_mount`, `client_name`, `subdir_inode`, `fd_cnt`, `scratch_ctx`, and graph callback side effects are runtime state only. No durable client state is written.

### Dependencies And Integration Points
The file depends on `glusterfs/client_t.h`, `dict`, `statedump`, lists, atomics, lock macros, inode/fd table dump helpers, translator graph structures, and xlator callback vectors. It integrates with RPC authentication, protocol/server connection management, detach-brick fd counting, subdir mounts, graph lifecycle callbacks, and diagnostics.

### Risks And Edge Cases
The matching expression in `gf_client_get()` requires `cred->flavour` to be nonzero, so unauthenticated clients with the same UID are not matched by the visible condition and may be duplicated. If `subdir_mount` duplication fails, the partially created client continues with NULL rather than failing. On some expansion failure paths, auth data or subdir strings allocated before table insertion may not all be freed. `gf_client_clienttable_expand()` returns `0` when allocation of the new table fails, restoring `oldclients` but making the caller think expansion succeeded. Scratch context has only eight pointer-keyed slots and silently refuses new keys when full by returning NULL. Dump paths use try-locks and may skip data under contention.

### Test Signals
Tests should cover allocation, free-list chaining and expansion, duplicate client detection with and without auth, bind/ref transitions, destroy callback traversal over multiple graphs, subdir inode release, auth data ownership on failures, scratch context full behavior, statedump output under lock contention, and sanitizer checks for expansion failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/client_t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/cluster-syncop.c -->
## sources/distributed-fs/glusterfs/libglusterfs/src/cluster-syncop.c

### Purpose
`cluster-syncop.c` provides synchronous cluster-wide FOP helpers for translators that need to issue the same operation to selected subvolumes and wait for callbacks from all of them. It bridges asynchronous GlusterFS stack winds with `syncbarrier_t` so callers receive arrays of `default_args_cbk_t` replies and success masks.

### Important APIs, Types, And Functions
The main macros are `FOP_ONLIST`, `FOP_SEQ`, and `FOP_CBK`. `FOP_ONLIST` initializes a `cluster_local_t`, wipes replies, counts enabled subvolumes, winds the FOP to each selected child using `STACK_WIND_COOKIE`, waits on the barrier, restores frame local state, and resets the stack. `FOP_SEQ` performs the same pattern one selected subvolume at a time. `FOP_CBK` stores callback arguments into the indexed reply slot and wakes the barrier.

`cluster_replies_wipe()` cleans previous reply ownership with `args_cbk_wipe`. `cluster_fop_success_fill()` builds a success bitmap and returns the count of valid nonnegative replies. The file defines callback shims for all supported FOPs, then wrapper functions such as `cluster_lookup`, `cluster_stat`, `cluster_create`, `cluster_writev`, `cluster_xattrop`, and many others. Lock-specific helpers include `cluster_tryinodelk`, `cluster_inodelk`, `cluster_uninodelk`, `cluster_tryentrylk`, `cluster_entrylk`, tiebreaker variants, and unlock helpers.

### Control Flow
A caller provides `subvols`, an `on` bitmap, `numsubvols`, reply storage, an output bitmap, and a call frame. The wrapper macro wipes previous replies, initializes per-reply entry lists, installs a stack-local `cluster_local_t` into `frame->local`, winds selected operations with the subvolume index encoded as the callback cookie, waits for callbacks, restores `frame->local`, and computes the success bitmap. Callback shims copy all callback values into the proper reply slot through `args_*_cbk_store`.

Lock helpers first try nonblocking locks across selected subvolumes. If any selected reply returns `EAGAIN`, they fill the locked bitmap, unlock already acquired subvolumes, then retry sequential blocking locks to avoid deadlocks. Tiebreaker variants return zero immediately if the first contention occurs before any successful lock.

### State And Persistence Behavior
State is transient and stack-scoped. Replies are caller-owned arrays of `default_args_cbk_t`; the code wipes and reinitializes them before use. `frame->local` is temporarily overwritten and restored. Lock helpers create temporary `loc_t` values with inode refs and GFIDs and wipe them before returning. No persistent storage is modified directly, though the FOPs sent to subvolumes may perform persistent filesystem changes.

### Dependencies And Integration Points
This file depends on `glusterfs/cluster-syncop.h`, stack wind macros, `syncbarrier_t`, `default-args` callback storage, `loc_t`, inode refs, locks, and xlator FOP vectors. It is used by cluster translators that coordinate replicate/disperse/distribute behavior and need synchronous fan-out without manually writing callback aggregation each time.

### Risks And Edge Cases
The file explicitly warns that these helpers block the executing thread when not running inside a synctask, so they should not run on epoll worker threads. If `syncbarrier_init()` fails inside the macros, the wrappers break out and then report success based on wiped replies, generally zero, with little detail. `memset(output, 0, numsubvols)` assumes the output mask has at least `numsubvols` bytes. `frame->local` is reused for aggregation, so nested or concurrent use on the same frame would be unsafe. The callback and wrapper families must stay in lockstep with FOP signatures. Lock retry paths rely on correct reply validity and cleanup to avoid leaving partial locks behind.

### Test Signals
Tests should cover fan-out to selected subvolumes, zero selected subvolumes, partial failures, reply ownership wipe between calls, barrier wake count correctness, sequential lock retry after `EAGAIN`, unlock of partially acquired locks, tiebreaker semantics, and detection of accidental use from event-loop threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/cluster-syncop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/common-utils.c -->
## sources/distributed-fs/glusterfs/libglusterfs/src/common-utils.c

### Purpose
`common-utils.c` is a broad libglusterfs utility module. It collects process/runtime helpers, hashing and GFID generation, path and directory utilities, graph dumping, crash backtraces, string and numeric parsers, network/address validation, host identity checks, volfile server parsing, logging-path selection, thread helpers, pid/service checks, recursive removal, FOP metadata helpers, fd closing, group lookup, SHA-256, safe string copy, and miscellaneous conversion utilities.

### Important APIs, Types, And Functions
Hashing and identity helpers include `gf_xxh64_wrapper`, `gf_xxh64_hash_wrapper`, `gf_gfid_generate_from_xxh64`, `uuid_utoa`, `uuid_utoa_r`, `lkowner_utoa`, `leaseid_utoa`, `gf_leaseid_get`, `gf_existing_leaseid`, `gfid_to_ino`, and `glusterfs_compute_sha256`.

Filesystem/path helpers include `mkdir_p`, `gf_lstat_dir`, `gf_path_strip_trailing_slashes`, `gf_canonicalize_path`, `recursive_rmdir`, `gf_set_timestamp`, `gf_unlink`, `gf_nread`, `gf_nwrite`, `gf_pipe`, `close_fds_except_custom`, and `close_fds_except`.

Parsing helpers include `gf_trim`, `gf_strstr`, `gf_string2time`, `gf_string2percent`, the `gf_string2*` signed/unsigned/integer/double family, base-10 variants, `gf_string2bytesize_range`, `gf_string2percent_or_bytesize`, `gf_str_to_long_long`, `gf_string2boolean`, `gf_strn2boolean`, token iteration helpers, `gf_uint64_2human_readable`, and `gf_rebalance_thread_count`.

Networking helpers include `valid_host_name`, `valid_ipv4_address`, `valid_ipv6_address`, `valid_internet_address`, `gf_is_ip_in_net`, `mask_match`, `gf_get_hostname_from_ip`, `gf_interface_search`, `gf_is_loopback_localhost`, `gf_is_local_addr`, `gf_is_same_address`, `get_host_name`, `gf_process_getspec_servers_list`, `gf_set_volfile_server_common`, and reserved-port parsing through `gf_process_reserved_ports`.

Runtime and diagnostics helpers include `gf_assert`, `gf_log_dump_graph`, `gf_print_trace`, `generate_glusterfs_ctx_id`, `get_mem_size`, thread naming/creation helpers, `gf_is_service_running`, `gf_backtrace_save`, `fop_log_level`, `fop_enum_to_pri_string`, `gf_fop_string`, `gf_fop_int`, `gf_inode_type_to_str`, `gf_is_zero_filled_stat`, `gf_is_valid_xattr_namespace`, `gf_bits_count`, `gf_bits_index`, `gf_getgrouplist`, `find_xlator_option_in_cmd_args_t`, `gf_d_type_from_ia_type`, `gf_nanosleep`, `get_xattrs_to_heal`, `gf_gethostname`, and `gf_set_nofile`.

### Control Flow
Most helpers are direct wrappers with validation, conversion, and GlusterFS logging. Numeric parsing clears `errno`, calls `strto*`, validates tails and ranges, then restores old errno on success. Path creation walks slash boundaries and checks symlink policy. Graph dumping walks translators depth-first and prints volume blocks. Crash tracing flushes logs, disables suppression/syslog as needed, emits pending frames, revision/config data, backtrace, and re-raises the signal. Network locality resolves names with `getaddrinfo`, converts addresses, checks loopback and local interfaces, and frees resolver data.

### State And Persistence Behavior
The module touches several forms of runtime state: `gf_signal_on_assert`, thread names, signal masks, `THIS`, `global_ctx->hostname`, command-line server lists, log file paths, pid files, and process file descriptors. It can create directories, recursively delete directories, set file timestamps, unlink files, read `/proc/sys/net/ipv4/ip_local_reserved_ports`, inspect `/proc/self/fd`, and create temporary backtrace files under `/tmp` that are immediately unlinked. It does not own a single persistent data store but many helpers affect process or filesystem state.

### Dependencies And Integration Points
Dependencies include POSIX libc, pthreads, networking APIs, OpenSSL, xxhash, GlusterFS syscall wrappers, logging, stack/graph structures, ACL/xattr constants, command-line argument structures, and platform conditionals for Linux, BSD, Darwin, Solaris, and NetBSD. Because this file is in libglusterfs, it is integrated across most translators and daemon entry points.

### Risks And Edge Cases
`gf_strstr()` calls `strdup(str)` before validating `str`, so NULL input can crash before the intended validation. Some numeric wrappers assign narrowed values even when the parse helper failed or before range validation, so callers should honor return codes strictly. `gf_string2bytesize_range()` multiplies integer values before checking overflow, which can wrap before the max comparison. `valid_ipv4_address()` and `valid_ipv6_address()` use `tmp[length - 1]` after allocation without first checking allocation success. `recursive_rmdir()` treats failure to open a directory as success, which may hide permission or race failures. `gf_getgrouplist()` can return `GF_MAX_AUX_GROUPS` after a failed call without guaranteeing a complete successful population. Many helpers rely on `THIS` or `global_ctx`, which makes standalone use fragile. Address validation is custom and should be kept aligned with tests and platform resolver behavior.

### Test Signals
There is an explicit source comment requiring changes to `gf_is_ip_in_net()` to be mirrored in `tests/utils/ip-in-cidr.c`. Additional tests should cover numeric parser tails/ranges/overflow, byte-size fractional and overflow inputs, NULL validation for string/address helpers, mkdir symlink policy, canonical path normalization, reserved-port range parsing, local-address detection with IPv4 and IPv6 including scoped IPv6, volfile server duplicate handling, log path generation, thread naming truncation, pidfile handling, recursive delete error propagation, fd closing preserve lists, SHA-256 vectors, and FOP log-level mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/common-utils.c -->
