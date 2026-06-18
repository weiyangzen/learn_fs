# subset-b-009807 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/adouble.c -->
# sources/user-network-fs/samba/source3/lib/adouble.c

Purpose: implements Samba AppleDouble helpers for Netatalk metadata xattrs, `._` resource sidecar files, AFP info packing, and conversion between macOS AppleDouble blobs and Samba alternate-stream storage.

Important APIs/types/functions: private `struct adouble`, `struct ad_xattr_header`, `struct ad_xattr_entry`, `ad_get_entry()`, `ad_getdate()`, `ad_setdate()`, `ad_init()`, `ad_get()`, `ad_fget()`, `ad_fset()`, `ad_convert()`, `ad_unconvert()`, `adouble_open_from_base_fsp()`, `adouble_path()`, `adouble_name()`, `afpinfo_pack()`, `afpinfo_unpack()`, and `adouble_buf_parse()`.

Control flow: allocation chooses fixed Netatalk metadata size or a 64 KiB resource header buffer, `ad_read()` opens/reads metadata or resource state, `ad_unpack()` validates magic/version/entry count/offsets, and `ad_pack()` writes headers plus optional packed xattr blocks before persistence. Conversion pulls xattrs out of oversized FinderInfo into streams, moves resource data back to the canonical offset, optionally wipes blank resource forks, writes FinderInfo to `AFPINFO_STREAM`, and may delete now-empty sidecar files. Unconversion enumerates streams, collects AFP info/resource/general streams, maps stream names through CATIA mappings, deletes converted streams, and writes a rebuilt AppleDouble sidecar.

State and persistence: stores metadata through `SMB_VFS_FGETXATTR/FSETXATTR` on `AFPINFO_EA_NETATALK` or through `pread/pwrite/ftruncate/unlinkat` on `._` files. `struct adouble` owns temporary xattr entry/data buffers and may own an opened `files_struct`, closed by its talloc destructor.

Dependencies/integration: depends on Samba VFS file APIs, `files_struct`, `smb_filename`, stream helpers, AFP constants from `MacExtensions.h`, CATIA/string replacement, byte-order macros, talloc, and root elevation when deleting corrupt metadata xattrs.

Risks: many paths perform multi-step conversion with side effects before final cleanup, so interruption can leave duplicated streams or partially rewritten sidecars. Resource fork relocation allocates the full fork in memory. Bounds checks are extensive, but `adouble_buf_parse()` validates `entries[id]` for duplicates while storing into `entries[i]`, which can misplace parsed entries. Test signals should include corrupt entry offsets/lengths, duplicate IDs, oversized xattr headers, blank resource fork cleanup, readonly fallback, conversion failure cleanup, stream-name mapping, and round-trip AFP info/resource fork preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/adouble.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/adouble.h -->
# sources/user-network-fs/samba/source3/lib/adouble.h

Purpose: declares the AppleDouble public contract used by vfs_fruit and related Samba VFS code.

Important APIs/types/functions: defines `adouble_type_t`, AppleDouble magic/version/entry identifiers, Netatalk xattr names, fixed entry lengths, sharemode lock offsets, date conversion macros, conversion flags, opaque `struct adouble`, `struct adouble_buf`, and APIs for reading/writing entries, dates, conversion/unconversion, sidecar naming/opening, AFP info packing/unpacking, and raw buffer parsing.

Control flow: callers choose `ADOUBLE_META` for Netatalk metadata xattrs or `ADOUBLE_RSRC` for resource sidecar files, then use `ad_get()/ad_fget()`, mutate entry pointers/lengths or date fields, and persist with `ad_fset()`. Higher-level conversion flows call `ad_convert()` or `ad_unconvert()` with CATIA mappings and flags.

State and persistence: the header exposes persistent wire/layout constants rather than storage itself. Date macros translate between AppleDouble network-order time and Unix time using `AD_DATE_DELTA`.

Dependencies/integration: includes `MacExtensions.h`, relies on Samba `DATA_BLOB`, `TALLOC_CTX`, `vfs_handle_struct`, `files_struct`, and `smb_filename` declarations from surrounding includes.

Risks/test signals: constants are ABI/file-format sensitive; changing lengths, IDs, lock offsets, or xattr names breaks stored metadata and locking semantics. Test callers should verify compile-time consumers see consistent entry IDs, date conversions, `HAVE_ATTROPEN` xattr naming, and sidecar name behavior for root and nested paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/adouble.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/adt_tree.c -->
# sources/user-network-fs/samba/source3/lib/adt_tree.c

Purpose: implements a small sorted path tree keyed by backslash-separated path components with inherited data pointers.

Important APIs/types/functions: private `struct tree_node` and `struct sorted_tree`; public `pathtree_init()`, `pathtree_add()`, `pathtree_find()`, `pathtree_print_keys()`; helper `trim_tree_keypath()`, `pathtree_birth_child()`, `pathtree_find_child()`, and recursive printing.

Control flow: `pathtree_add()` requires paths beginning with `\`, duplicates the path, splits it component by component, binary-search-like early exits are not used but children are kept sorted with insertion shifting, and the final node receives `data_p`. `pathtree_find()` walks components and returns the deepest matching non-null data pointer, so parent policy/data applies to descendants until overridden.

State and persistence: the tree is entirely in-memory and talloc-owned; child arrays are reallocated under each node. It stores external `void *data_p` without owning or freeing that payload.

Dependencies/integration: uses talloc, Samba debug, `strcasecmp_m()` charset-aware comparison, `SMB_STRDUP`, and macros from `smb_macros.h`. Intended for consumers that need Windows-style path prefix matching.

Risks/test signals: no deletion API, linear child scan despite sorted storage, and mutation of duplicated path strings during parsing. Tests should cover root data inheritance, case-insensitive matching, insertion ordering, missing children, bad paths without leading backslash, allocation failure, and multiple descendants overriding parent data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/adt_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/audit.c -->
# sources/user-network-fs/samba/source3/lib/audit.c

Purpose: maps LSA audit categories between numeric constants, symbolic strings, smb.conf parameter tokens, descriptions, and policy result strings.

Important APIs/types/functions: static `audit_category_tab`; public `audit_category_str()`, `audit_param_str()`, `audit_description_str()`, `get_audit_category_from_param()`, and `audit_policy_str()`.

Control flow: lookup functions linearly scan the sentinel-terminated table and return null on unknown category. `get_audit_category_from_param()` uses case-insensitive token comparisons and writes `Undefined` before selecting a category. `audit_policy_str()` formats `None`, `Success`, `Failure`, or `Success, Failure` using talloc.

State and persistence: stateless except for constant table data and caller-owned talloc allocations for policy strings.

Dependencies/integration: consumes generated LSA constants from `../librpc/gen_ndr/lsa.h`, Samba string helpers, DEBUG logging, and talloc.

Risks/test signals: category spelling follows upstream constants including `PROCCESS`; unknown parameters log at level 0 and return false. Tests should cover every table row round-trip, unknown categories returning null, unknown params preserving `Undefined`, and combined success/failure policy formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/avahi.c -->
# sources/user-network-fs/samba/source3/lib/avahi.c

Purpose: adapts Avahi's `AvahiPoll` callback interface onto Samba's tevent loop.

Important APIs/types/functions: `struct avahi_poll_context`, private `AvahiWatch` and `AvahiTimeout` wrappers, `avahi_watch_new/update/get_events/free`, `avahi_timeout_new/update/free`, event handlers, and exported `tevent_avahi_poll()`.

Control flow: Avahi asks for fd watches or timers through the returned `AvahiPoll`. Watch creation appends a talloc-owned wrapper, registers a tevent fd handler, maps tevent read/write flags to Avahi flags, and invokes Avahi callbacks. Timeout creation optionally schedules a tevent timer; update frees the old timer and installs a new one or disables it.

State and persistence: all state is in-memory under the returned `AvahiPoll` talloc tree. Arrays of watches/timeouts are compacted with `memmove()` on free.

Dependencies/integration: uses `<avahi-common/watch.h>`, tevent fd/timer APIs, talloc, and Samba assertions. It is the bridge needed for mDNS/DNS-SD code to share Samba's event loop.

Risks/test signals: `AvahiWatch.fd` is never assigned in `avahi_watch_new()`, so callbacks may receive an uninitialized fd. `avahi_timeout_update()` asserts on timer allocation failure. Tests should register watches/timers, verify callback fd/event values, disable and reschedule timers, and free items from the middle of arrays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/avahi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/background.c -->
# sources/user-network-fs/samba/source3/lib/background.c

Purpose: runs recurring background jobs by forking child helpers from a tevent parent, with optional messaging triggers to wake the schedule early.

Important APIs/types/functions: `struct background_job_state`, `background_job_send()`, `background_job_recv()`, trigger filter `background_job_trigger()`, wait callback `background_job_waited()`, completion callback `background_job_done()`, and destructor.

Control flow: `background_job_send()` registers filtered messaging reads for configured message IDs and schedules the initial wakeup. On wakeup it creates a pipe, forks, reinitializes messaging/event state in the child, runs `fn(private_data)`, writes the returned wait seconds to the pipe, and exits. The parent asynchronously reads the integer; `-1` completes the request, otherwise a new wakeup is scheduled.

State and persistence: state is talloc-owned and keeps trigger IDs, the active wakeup request, child result pipe fd, and pending pipe read. No durable persistence is used.

Dependencies/integration: tevent requests/timers, Samba messaging, `read_packet_send`, fork/pipe, `reinit_after_fork()`, NTSTATUS helpers.

Risks/test signals: child only reports a single integer and exits, so failures before pipe write surface as read/NT errors. Destructor must close pipe/read state during cancellation. Tests should cover initial delay, trigger wakeup, repeating return values, `-1` stop, fork/pipe errors, callback failure after fork reinit, and cancellation cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/background.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/background.h -->
# sources/user-network-fs/samba/source3/lib/background.h

Purpose: declares the asynchronous recurring background-job API.

Important APIs/types/functions: forward declares `struct messaging_context`; exposes `background_job_send()` and `background_job_recv()`.

Control flow: callers create a tevent request with an event context, messaging context, optional trigger message list, initial delay, function pointer, and private data. The function returns seconds until the next run or `-1` to stop. Callers later receive final NTSTATUS through `background_job_recv()`.

State and persistence: no public state; implementation-owned request state is talloc-scoped to the returned `tevent_req`.

Dependencies/integration: includes `replace.h`, `<tevent.h>`, and `libcli/util/ntstatus.h`, making it usable by Samba daemons that already operate on tevent/messaging.

Risks/test signals: API users must ensure `private_data` is valid in forked child context and that `fn` is async-signal/fork aware. Header-level tests are compile/interface checks plus integration tests that schedule, trigger, and stop a background job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/background.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cbuf.c -->
# sources/user-network-fs/samba/source3/lib/cbuf.c

Purpose: implements a talloc-owned growable character/binary buffer with a current write position and convenience formatting/quoting helpers.

Important APIs/types/functions: private `struct cbuf`; public creation/copy/delete/clear/swap/takeover/swapptr/resize/reserve/write/get/set/printf/quoted helpers.

Control flow: buffers start at 32 bytes and grow in `cbuf_reserve()` by doubling or fitting the requested space. String writes keep a debug NUL terminator, `cbuf_putdw()` writes little-endian binary data, and `cbuf_printf()` first tries available space then reserves and retries. Quoting escapes `"` and `\`, and `cbuf_print_quoted()` hex-escapes non-printable or whitespace bytes except plain space.

State and persistence: all state is in-memory under talloc; `cbuf_swap()` and `cbuf_swapptr()` adjust talloc parents to preserve ownership.

Dependencies/integration: talloc, locale `isprint/isspace`, byte-order `SIVAL`, assert, Samba `MIN/MAX/FALL_THROUGH`.

Risks/test signals: many APIs use `(size_t)-1` as sentinel despite `size_t`; `cbuf_resize()` frees the saved buffer on realloc failure, making failure destructive; several quote helpers ignore intermediate write failures. Tests should cover growth, zero/large writes, binary `putdw`, pointer swapping ownership, formatting retry, non-printable quoting, and realloc failure semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cbuf.h -->
# sources/user-network-fs/samba/source3/lib/cbuf.h

Purpose: declares the cbuf growable talloc character buffer interface.

Important APIs/types/functions: opaque `struct cbuf` typedef and functions for lifecycle, buffer swapping/takeover, resizing/reserving, writing characters/strings/dwords/printf output, position management, and quoted string emission.

Control flow: callers allocate a `cbuf`, append bytes or formatted text, bookmark positions with `cbuf_getpos()`, rewind with `cbuf_setpos()`, and retrieve NUL-terminated content from any previous position with `cbuf_gets()`.

State and persistence: public API exposes no fields; all state is heap memory attached to the provided talloc context. No durable persistence.

Dependencies/integration: requires Samba's `PRINTF_ATTRIBUTE`, integer types, and talloc conventions supplied by surrounding includes.

Risks/test signals: `cbuf_delete()` is documented as preferred over direct `talloc_free()` despite parent-free working; callers must treat returned pointers as invalid after resize/swap. Tests should compile all prototypes, verify sentinel length behavior, and assert that position invariants hold after clear, setpos, reserve, and takeover.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/charcnv.c -->
# sources/user-network-fs/samba/source3/lib/charcnv.c

Purpose: provides SMB character set conversion helpers between Samba Unix strings, DOS codepage strings, and UTF-16LE/UCS2 wire strings.

Important APIs/types/functions: `gfree_charcnv()`, `push_ascii()`, `pull_ascii()`, internal talloc pull helpers for ASCII and UCS2, `push_ucs2()`, `push_string_check_fn()`, `push_string_base()`, `pull_string_talloc()`, and `rpcstr_push_talloc()`.

Control flow: push functions choose ASCII or UTF-16LE based on flags and SMB `FLAGS2_UNICODE_STRINGS`, optionally uppercase, align UCS2 buffers unless `STR_NOALIGN`, and use `convert_string()` or `convert_string_talloc()`. Pull functions bound client-provided terminated lengths with `strnlen/strnlen_w`, reject `-1` lengths in newer paths, append NUL when conversion did not include it, and panic on invalid API use.

State and persistence: no durable state; `gfree_charcnv()` releases global iconv handles. Talloc pull variants allocate destination strings for callers.

Dependencies/integration: iconv conversion layer, Samba charset helpers, SMB flags, Unicode case conversion, talloc, and panic/debug infrastructure.

Risks/test signals: invalid lengths intentionally panic, and failed conversion may clear destination output. Tests should cover ASCII/Unicode selection, alignment, termination with bounded source lengths, uppercase conversion, conversion failure, empty strings, large client lengths near the 1 MiB guard, and RPC string allocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/charcnv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cleanupdb.c -->
# sources/user-network-fs/samba/source3/lib/cleanupdb.c

Purpose: tracks smbd child cleanup obligations in a shared TDB so cleanupd can discover children that exited cleanly or uncleanly.

Important APIs/types/functions: private `struct cleanup_key`, `struct cleanup_rec`, singleton `cleanup_db()`, public `cleanupdb_store_child()`, `cleanupdb_delete_child()`, and `cleanupdb_traverse_read()`.

Control flow: `cleanup_db()` lazily opens `lock_path("smbd_cleanupd.tdb")` with incompatible hash, clear-if-first, and mutex locking. Store/delete wrap pid keys in fixed-size TDB records. Traversal validates key/value sizes, copies them into local structs, and invokes the caller callback.

State and persistence: persistent TDB at Samba lock path; static `struct tdb_wrap *db` caches the handle for process lifetime. `TDB_CLEAR_IF_FIRST` resets the DB when the first process opens it after all handles are gone.

Dependencies/integration: tdb_wrap, TDB mutex locking, Samba lock path utility, talloc stack, DEBUG.

Risks/test signals: fixed binary pid/bool layouts are host ABI dependent and intended only for local runtime state. Traversal aborts on malformed records. Tests should store/delete pids, traverse multiple records, reject malformed TDB entries, verify lock path/open flags, and simulate missing DB/open failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cleanupdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cleanupdb.h -->
# sources/user-network-fs/samba/source3/lib/cleanupdb.h

Purpose: declares cleanup database operations for reliable child cleanup tracking.

Important APIs/types/functions: `cleanupdb_store_child(pid, unclean)`, `cleanupdb_delete_child(pid)`, and `cleanupdb_traverse_read(callback, private_data)`.

Control flow: callers record child pids with a cleanup/unclean flag, remove them after normal cleanup, and traverse remaining records to perform recovery.

State and persistence: the header hides the TDB implementation and exposes only pid/bool records through callbacks.

Dependencies/integration: includes `replace.h` for portability and pid/bool types.

Risks/test signals: callback return nonzero stops traversal as an error; callers should not assume ordering. Tests should compile callback signatures and verify boolean semantics match `cleanupdb.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cleanupdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cluster_support.c -->
# sources/user-network-fs/samba/source3/lib/cluster_support.c

Purpose: reports whether Samba was built with CTDB cluster support and resolves CTDB feature/default socket information.

Important APIs/types/functions: `cluster_support_available()`, `cluster_support_features()`, and `lp_ctdbd_socket()`.

Control flow: compile-time `CLUSTER_SUPPORT`, `CTDB_SOCKET`, and `CTDB_PROTOCOL` conditionals determine feature strings and availability. `lp_ctdbd_socket()` prefers configured `lp__ctdbd_socket()` when non-empty, then compile-time `CTDB_SOCKET`, else empty string.

State and persistence: stateless; returns static string data or configuration-derived pointers.

Dependencies/integration: loadparm/private `lp__ctdbd_socket()`, CTDB protocol headers when clustering is compiled, and `tdb.h`.

Risks/test signals: missing cluster support must return false and feature text `NONE`; empty socket strings will cause CTDB open/probe failures elsewhere. Tests should cover clustered and non-clustered builds, configured socket override, compile-time socket fallback, and feature string content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cluster_support.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cluster_support.h -->
# sources/user-network-fs/samba/source3/lib/cluster_support.h

Purpose: exposes cluster support capability helpers.

Important APIs/types/functions: declarations for `cluster_support_available()`, `cluster_support_features()`, and `lp_ctdbd_socket()`.

Control flow: callers query availability before using CTDB-dependent features and call `lp_ctdbd_socket()` for the runtime socket path.

State and persistence: no public state.

Dependencies/integration: expected to be included by DB, messaging, and command-line helpers that need compile/runtime cluster decisions.

Risks/test signals: header lacks include guards in this snapshot, so repeated inclusion depends on compiler tolerance for repeated identical prototypes. Compile tests should include it from multiple translation units and verify no conflicting declarations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cluster_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cmdline_contexts.c -->
# sources/user-network-fs/samba/source3/lib/cmdline_contexts.c

Purpose: provides command-line tools with a safe way to obtain Samba's global messaging context.

Important APIs/types/functions: `cmdline_messaging_context()` and `cmdline_messaging_context_free()`.

Control flow: the getter ensures loadparm is initially loaded, then enforces that clustering mode only runs as root because CTDB/registry/messaging access requires privileges. It returns `global_messaging_context()`, exiting on root initialization failure while allowing non-root non-cluster callers to handle a null result.

State and persistence: uses global loadparm and global messaging context state; no file persistence.

Dependencies/integration: loadparm, global contexts, messaging, `geteuid()`, stderr, process exit.

Risks/test signals: this helper can terminate the process for clustered non-root or root messaging-init failures. Tests should exercise config-load failure, non-root non-cluster null handling, clustered non-root exit, root init failure exit, and free delegating to `global_messaging_context_free()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cmdline_contexts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cmdline_contexts.h -->
# sources/user-network-fs/samba/source3/lib/cmdline_contexts.h

Purpose: declares command-line messaging context helpers.

Important APIs/types/functions: forward declaration of `cmdline_messaging_context(config_file)` and `cmdline_messaging_context_free()`.

Control flow: callers request a global messaging context after optional config loading and later free global state through the paired function.

State and persistence: no public state; implementation uses global Samba state.

Dependencies/integration: includes no heavy headers, relying on surrounding declarations for `struct messaging_context`.

Risks/test signals: consumers must be aware that implementation may exit in clustered/root error cases. Compile tests should verify the lightweight header can be included without pulling full messaging internals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/cmdline_contexts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ctdb_dummy.c -->
# sources/user-network-fs/samba/source3/lib/ctdb_dummy.c

Purpose: provides non-cluster stub implementations for CTDB/messaging/dbwrap symbols so Samba can link without CTDB support.

Important APIs/types/functions: stubs for `ctdbd_probe()`, CTDB messaging registration/IP functions, `ctdbd_process_exists()`, `db_open_ctdb()`, `messaging_ctdb_send()`, `messaging_ctdb_ref()`, `messaging_ctdb_register_tevent_context()`, `messaging_ctdb_connection()`, and `ctdb_async_ctx_reinit()`.

Control flow: functional calls return `ENOSYS`, `NULL`, or `false`; deregistration/unregister/pass functions are no-ops.

State and persistence: no state or persistence.

Dependencies/integration: includes the same public CTDB, messaging, dbwrap, and torture headers as callers expect, preserving ABI at link time when clustering is disabled.

Risks/test signals: callers must gate CTDB behavior on cluster support or handle `ENOSYS`/null cleanly. Tests should build without cluster support and verify local database paths do not call these stubs unexpectedly, while explicit cluster-only operations fail with clear unsupported errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ctdb_dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ctdbd_conn.c -->
# sources/user-network-fs/samba/source3/lib/ctdbd_conn.c

Purpose: implements Samba's low-level connection to the CTDB daemon for cluster messaging, controls, database attach/traverse/fetch/migrate, IP registration/enumeration, probing, and async request handling.

Important APIs/types/functions: private `struct ctdbd_connection` and callback table; public connection init/reinit/async init, `ctdbd_vnn()`, `ctdbd_conn_get_fd()`, `register_with_ctdbd()`, `deregister_from_ctdbd()`, `ctdbd_messaging_send_iov()`, `ctdbd_control_local()`, `ctdbd_db_attach()`, `ctdbd_dbpath()`, `ctdbd_migrate()`, `ctdbd_parse()`, `ctdbd_traverse()`, IP register/unregister/pass/foreach helpers, watch/unwatch, probe, `ctdbd_req_send/recv()`, and `ctdbd_parse_send/recv()`.

Control flow: initialization opens a Unix socket, gets local PNN/VNN, validates node activity via nodemap, registers a random srvid, and optionally creates nonblocking async queues. Synchronous controls/calls write CTDB packets and loop reading replies while dispatching intervening messages. Async requests enqueue writes, maintain pending requests by reqid, run one packet read at a time, and complete matching tevent requests. Traversal starts a CTDB traverse and consumes message records until an empty key/data marker.

State and persistence: per-connection fd, reqid counter, callback array, random service id, outgoing queue, pending requests, and active read request. Persistent cluster state lives in CTDB daemon databases and node maps, not in this file.

Dependencies/integration: CTDB protocol structs/opcodes, tevent, Samba messaging, dbwrap RBT for IP collation, Unix sockets, poll/read/write helpers, talloc, fault handling. `cluster_fatal()` exits immediately on daemon I/O failure to release process IDs quickly.

Risks/test signals: sync calls are rejected when async requests are pending on the same connection; daemon read/write errors terminate the process; packet validation is minimal in async receive beyond length. IP aggregation must handle inactive/deleted nodes and duplicate public IP views. Tests should cover reqid wrap, mismatched replies, message callback dispatch, timeout/probe, async cancellation/pending cleanup, traverse end markers, malformed public IP payloads, IPv4-mapped IPv6 canonicalization, and fatal-path behavior under socket loss.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/ctdbd_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_ctdb.c -->
# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_ctdb.c

Purpose: implements the dbwrap backend that exposes CTDB-clustered TDB databases through Samba's `db_context` API.

Important APIs/types/functions: `struct db_ctdb_ctx`, `struct db_ctdb_transaction_handle`, `struct db_ctdb_rec`, global `ctdb_async_ctx`, public `db_open_ctdb()` and `ctdb_async_ctx_reinit()`, plus transaction, fetch-lock, parse, async parse, traverse, delete, store, seqnum, and ID callbacks installed into `db_context`.

Control flow: open attaches to CTDB, resolves the local database path/open flags, optionally enables seqnums/read-only optimization, initializes async CTDB for non-persistent DBs, opens the local TDB copy, and configures callback methods. Non-persistent `fetch_locked` chainlocks the local TDB, checks whether the local header is writable dmaster state, migrates through CTDB if needed, then returns a locked record whose destructor unlocks and logs slow locks. Persistent DBs auto-start transactions: a global CTDB lock protects a marshalled write buffer, commit bumps an internal sequence-number record and sends `TRANS3_COMMIT`, retrying or accepting recovery-completed commits based on sequence comparison.

State and persistence: persistent local TDB copies contain CTDB ltdb headers plus payloads. Transactions store pending writes in `ctdb_marshall_buffer`; non-persistent deletes write tombstone-like empty records and schedule CTDB deletion. Async connection is process-global.

Dependencies/integration: CTDB daemon controls, `messaging_ctdb_connection()`, g_lock, dbwrap private API, TDB/tdb_wrap, loadparm thresholds, tevent async NTSTATUS, root elevation for async connection init.

Risks/test signals: transaction lock waits up to a day; nested cancel poisons later commit; empty records are treated as not found for non-persistent reads; commit recovery logic depends on sequence-number correctness. Tests should cover local read-only shortcuts, migration retry/log thresholds, locked-record destructor unlocks, persistent nested transactions, commit failure during recovery, transaction-buffer newest-value parsing, delete scheduling, traverse skipping `CTDB_DB_SEQNUM_KEY`, async parse request states, and open failures for missing CTDB/socket/dbpath.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_ctdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_ctdb.h -->
# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_ctdb.h

Purpose: declares the CTDB dbwrap backend entry points.

Important APIs/types/functions: forward declarations for `struct db_context` and `struct ctdbd_connection`; `db_open_ctdb()` and `ctdb_async_ctx_reinit()`.

Control flow: `db_open()` and cluster-aware callers invoke `db_open_ctdb()` to attach/open a CTDB-backed database. Messaging or reconnect paths can call `ctdb_async_ctx_reinit()` to rebuild the process-global async CTDB connection after fork or connection loss.

State and persistence: no public state; implementation manages local TDB copies, CTDB db IDs, transaction state, and async connection state.

Dependencies/integration: includes talloc and `dbwrap_private.h` for lock order and dbwrap flags.

Risks/test signals: callers must only use this when clustering and messaging CTDB are initialized. Header tests should validate prototypes remain consistent with `dbwrap_open.c`, `ctdb_dummy.c`, and `dbwrap_ctdb.c` in both clustered and non-clustered builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_ctdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_open.c -->
# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_open.c

Purpose: central database opener that chooses local TDB or clustered CTDB dbwrap backend and applies per-database tuning.

Important APIs/types/functions: `db_is_local()` and `db_open()`.

Control flow: `db_is_local()` checks clustering, CTDB socket existence, strips path to basename, and honors `ctdb:<db>` parameter overrides. `db_open()` validates lock order, applies `tdb_hash_size:<base>`, readonly optimization for clear-if-first DBs, TDB mutex options subject to mmap and robust mutex availability, then chooses CTDB if clustering is enabled and allowed. CTDB path initializes global messaging, verifies a CTDB connection, and delegates to `db_open_ctdb()`. Otherwise it initializes loadparm context and calls `dbwrap_local_open()`.

State and persistence: no owned persistent state; returns a `db_context` backed by either CTDB/local TDB. It modifies local `tdb_flags/dbwrap_flags` based on configuration.

Dependencies/integration: loadparm, cluster support socket helper, messages CTDB, global contexts, CTDB connection, local/CTDB dbwrap backends, TDB runtime mutex checks.

Risks/test signals: clustered configuration with missing socket returns null; CTDB open failure sets `errno` to EIO if unset. Mutex requirements can force flags even when runtime support is absent. Tests should cover local fallback, per-DB CTDB disable, missing socket, global messaging failure, robust mutex unavailable, mmap disabled, readonly optimization toggles, and invalid lock order.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_open.h -->
# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_open.h

Purpose: declares cluster-aware dbwrap open helpers.

Important APIs/types/functions: forward `struct db_context`, `db_is_local(name)`, and `db_open(...)`.

Control flow: callers use `db_is_local()` for routing decisions or call `db_open()` directly to receive either local TDB or CTDB-backed `db_context` based on runtime clustering and per-db configuration.

State and persistence: no public state; returned context owns backend-specific state.

Dependencies/integration: requires dbwrap lock-order enum and flags from surrounding dbwrap private/public includes.

Risks/test signals: API returns null and sets errno for many configuration/runtime failures, so callers need robust error reporting. Compile tests should ensure declarations match implementation and all call sites pass valid lock-order values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_open.h -->
