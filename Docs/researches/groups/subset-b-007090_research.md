<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-journal-handler.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-journal-handler.c

## Purpose
Implements the legacy libgfchangelog journal API backend. It receives journal-path events from the changelog xlator, decodes raw `CHANGELOG.*` files into consumer-readable scratch files, manages `.current`, `.processing`, `.processed`, and `history` scratch directories, and tracks connection state for the API.

## APIs, Types, and Functions
Core entry points are `gf_changelog_journal_init()`, `gf_changelog_journal_fini()`, `gf_changelog_journal_connect()`, `gf_changelog_journal_disconnect()`, and `gf_changelog_handle_journal()`, matching callback typedefs from the helper API. `gf_changelog_consume()` opens a source changelog, writes decoded output in `.current`, and normally renames it into `.processing`; `gf_changelog_publish()` moves a decoded file from `.current` to `.processing` for history consumers. Decoders include `gf_changelog_decode()`, `gf_changelog_parse_binary()`, and `gf_changelog_parse_ascii()`, with version-specific `nr_gfids` and `nr_extra_recs` tables for v1.1/v1.2 entry records. Processor helpers include `gf_changelog_init_processor()`, `gf_changelog_process()`, `gf_changelog_queue_journal()`, `gf_changelog_open_dirs()`, and `gf_changelog_init_history()`.

## Control Flow, State, and Persistence
Initialization resolves the scratch directory, creates/cleans `.current` and `.processing`, preserves `.processed`, creates a tracker file, initializes RFC3986 encoding tables, creates a nested history journal, then starts a long-lived processor thread. Runtime journal events are converted into `gf_changelog_entry_t` records under a mutex/condition list; the processor thread consumes each path, decodes the source file after its `CHANGELOG_HEADER`, and writes a normalized line format. Empty changelogs are detected when the header length equals file size and are unlinked from `.current` instead of published. Binary parsing uses `mmap()` because binary GFIDs can contain newline bytes; ASCII parsing converts fop numbers to `gf_fop_list` names and URL-encodes space/newline/percent in entry path material.

## Dependencies and Integration
Depends on libglusterfs syscall wrappers, UUID helpers, `gf_changelog_write()`, changelog encoding constants from the xlator, memory types, and callback wiring from `gf-changelog-helpers.h`. It is installed as the journal-mode callback in `gf_changelog_register()` and is invoked from the reverse RPC callback path in `gf-changelog-reborp.c`. History APIs in `gf-history-changelog.c` reuse `hist_jnl` and the same consume/publish routines.

## Risks and Test Signals
Risks include parser fragility on malformed NUL-delimited records, fixed `LINE_BUFSIZE`, unchecked table lookup bounds for fop numbers, thread cancellation cleanup, and scratch-directory destructive cleanup of `.current`/`.processing` at initialization. The source as shown contains duplicated declarations/text fragments in places, which should be compile-checked in this snapshot. Test signals should cover v1.1/v1.2 ASCII and binary changelogs, empty changelog handling, rename/publish failures, disconnect state, queue wakeups, and malformed records that omit separators or contain unknown encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-journal-handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-journal.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-journal.h

## Purpose
Defines the libgfchangelog journal-mode state model shared by live journal processing and historical changelog processing.

## APIs, Types, and Functions
`enum api_conn` models connected, connection-in-progress, and disconnected states. `gf_changelog_entry_t` stores queued changelog paths. `gf_changelog_processor_t` owns the queue mutex/condition, waiting flag, processor thread, and list head. `gf_changelog_journal_t` stores directory streams, tracker fd, brick path, scratch directory paths, RFC3986 table, nested history journal pointer, history scan status, spinlock, connected state, and owning xlator. `gf_changelog_history_data_t` and `gf_changelog_consume_data_t` carry history search and parallel consume work. The header declares journal callbacks via `CALLBACK`, `INIT`, `FINI`, `CONNECT`, and `DISCONNECT`.

## Control Flow, State, and Persistence
The structures separate live scratch state from historical scratch state by nesting `hist_jnl`. Directory path fields point to persistent on-disk queues: `.current` for freshly decoded files, `.processing` for files exposed to consumers, `.processed` for files marked done, and a tracker fd for iterating results. Connection state is guarded by a spinlock and accessed through `JNL_SET_API_STATE()` and `JNL_IS_API_DISCONNECTED()`.

## Dependencies and Integration
Requires pthreads, `DIR`, `PATH_MAX`, Gluster list heads, booleans, callback typedefs, and xlator types supplied through included Gluster headers. It is consumed by `gf-changelog-journal-handler.c` and `gf-history-changelog.c`, and its callback names are supplied to `gf_changelog_register()` for legacy journal consumers.

## Risks and Test Signals
Risks include shared ownership between `jnl` and `hist_jnl`, lock discipline around `connected`, and fd/dir cleanup ordering. Test signals are successful initialization/fini cycles, connection/disconnection transitions, tracker fd truncation/iteration, and nested history journal cleanup without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-journal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-reborp.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-reborp.c

## Purpose
Implements the library-side reverse RPC server, named “reborp” as the reverse of probe. It accepts event batches pushed back by the brick-side changelog xlator and invokes registered consumer callbacks.

## APIs, Types, and Functions
`gf_changelog_reborp_init_rpc_listner()` creates a temporary Unix socket listener. `gf_changelog_reborp_rpcsvc_notify()` handles accept/disconnect, unlinks the temporary socket after accept, and calls connected/disconnected callbacks. `gf_changelog_event_handler()` decodes `changelog_event_req`, deep-copies payload iovecs into `struct gf_event`, queues them, and replies with `changelog_event_rsp`. Callback flow is handled by `gf_changelog_callback_invoker()`, `gf_changelog_invoke_callback()`, `queue_ordered_event()`, `queue_unordered_event()`, `pick_event_ordered()`, and `pick_event_unordered()`. `gf_changelog_connection_janitor()` drains cleanup entries.

## Control Flow, State, and Persistence
After the normal probe client asks the brick to connect back, this listener receives reverse RPC event calls. Event payloads are copied out of request memory, optionally sorted by sequence number, then consumed by a per-connection callback-invoker thread. Ordered mode initializes `next_seq` from the first event and only wakes the invoker when the expected sequence is present; unordered mode dispatches FIFO. No persistent files are written here, but journal-mode callbacks enqueue paths that are later persisted by the journal handler.

## Dependencies and Integration
Depends on `changelog-rpc-common` for server creation and reply serialization, XDR types from `changelog-xdr`, libgfchangelog helper types such as `gf_changelog_t`, and changelog event filters. It is started from `gf_changelog_setup_rpc()` before the probe request and shares RPC program numbers with the xlator reverse-dispatch path in `changelog-ev-handle.c`.

## Risks and Test Signals
Risks include unbounded event queue growth, ordered mode blocking forever on a missing sequence, callback execution from a single invoker thread, cleanup TODOs, and all server-side filtering currently being repeated library-side. Test signals include accept/disconnect callbacks, XDR decode failure replies, ordered out-of-order delivery, payload deep-copy correctness across multiple iovecs, and cleanup path behavior when callbacks or RPC clients disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-reborp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-rpc.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-rpc.c

## Purpose
Provides the libgfchangelog client-side probe RPC used to contact a brick’s changelog xlator and request reverse event delivery.

## APIs, Types, and Functions
`gf_changelog_rpc_init()` hashes the brick path into the well-known changelog Unix socket path and calls `changelog_rpc_client_init()`. `gf_probe_changelog_filter()` builds a `changelog_probe_req` containing the reverse socket path and notification filter, then submits `CHANGELOG_RPC_PROBE_FILTER`. `gf_changelog_invoke_rpc()` wraps `changelog_invoke_rpc()`. `gf_changelog_procs` and `gf_changelog_clnt` define the client RPC program table for `CHANGELOG_RPC_PROGNUM`/version 1.

## Control Flow, State, and Persistence
There is no on-disk persistence. A connection is opened to `/var/run`-style changelog socket derived by `CHANGELOG_MAKE_SOCKET_PATH()`, a frame is created by common RPC code, and the probe request tells the server where to connect back. Notification handling is currently a no-op across connect, disconnect, message, destroy, and ping events.

## Dependencies and Integration
Depends on `gf-changelog-rpc.h`, `changelog-rpc-common.h`, `changelog-misc.h`, XDR serialization for `changelog_probe_req`, and the `gf_changelog_t` connection structure. It is orchestrated by `gf_changelog_setup_rpc()` after the reverse listener is created.

## Risks and Test Signals
Risks include copying `strlen(sock)` bytes without explicit NUL assignment into the XDR string field, lack of connection-state handling, and reliance on sleep-based timing in the caller before probe. Test signals include successful probe filter submission, malformed or long reverse socket paths, brick socket path hashing, and behavior when RPC connect/start succeeds but probe fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-rpc.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-rpc.h

## Purpose
Declares the libgfchangelog RPC surface for probe-client setup, probe invocation, and reverse listener setup.

## APIs, Types, and Functions
Exports `gf_changelog_rpc_init(xlator_t *, gf_changelog_t *)`, `gf_changelog_invoke_rpc(xlator_t *, gf_changelog_t *, int)`, and `gf_changelog_reborp_init_rpc_listner(xlator_t *, char *, char *, void *)`. It includes libgfchangelog helper definitions and shared changelog RPC constants/functions.

## Control Flow, State, and Persistence
The header has no runtime state. It describes the two-channel registration flow: create a reverse RPC listener, initialize a forward RPC client to the brick changelog socket, then invoke a probe procedure that asks the brick to connect back.

## Dependencies and Integration
Included by `gf-changelog.c`, `gf-changelog-rpc.c`, and other library files needing RPC setup. It bridges library-side helper types with xlator-side `changelog-rpc-common.h`.

## Risks and Test Signals
Risks are API typo compatibility (`listner` spelling), incomplete ownership documentation for socket buffers and callback data, and tight coupling to common RPC program constants. Test signals are compile coverage of all declarations and registration flows using both legacy journal callbacks and generic callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog.c

## Purpose
Bootstraps libgfchangelog as a small GlusterFS runtime, manages global library state, registers consumers against one or more bricks, and wires callbacks to RPC and journal processing.

## APIs, Types, and Functions
Public registration entry points are `gf_changelog_init()`, `gf_changelog_register_generic()`, and legacy `gf_changelog_register()`. Setup helpers include `gf_changelog_alloc_priv()`, `gf_changelog_ctx_defaults_init()`, `gf_changelog_init_context()`, `gf_changelog_set_primary()`, `gf_setup_brick_connection()`, `gf_changelog_setup_rpc()`, `gf_init_event()`, and cleanup placeholders `gf_cleanup_connections()`/`gf_cleanup_brick_connection()`. `gf_changelog_cleanup_this()` tears down the synthetic context.

## Control Flow, State, and Persistence
A process-wide `primary` xlator singleton owns a generated Gluster context, iobuf/event pools, call frame pools, dict pools, syncenv, logging, and `gf_private_t` connection lists. `gf_changelog_register_generic()` sets logging, iterates `gf_brick_spec` entries, allocates `gf_changelog_t`, initializes its ordered/unordered event invoker, calls the consumer-specific `init`, links it into `priv->connections`, starts reverse and forward RPC channels, sleeps briefly, then sends the probe filter request. The legacy API constructs a one-brick journal spec using `gf_changelog_journal_*` callbacks and stores the scratch-dir API pointer in `priv->api`.

## Dependencies and Integration
Depends on libglusterfs globals, event pools, mem pools, syncop, logging, RPC helpers, changelog memory IDs, and callback structures from `gf-changelog-helpers.h`. It integrates with `gf-changelog-rpc.c` for probe RPC, `gf-changelog-reborp.c` for reverse callbacks, and `gf-changelog-journal-handler.c` for legacy journal persistence.

## Risks and Test Signals
Risks include global singleton constraints, incomplete cleanup functions, sleeps as connection synchronization, partial failure leaks in RPC setup, and legacy API limitation to a single journal owner. Test signals include repeated init idempotence, registration of multiple bricks with ordered and unordered modes, cleanup on failed callback init/RPC setup, logging setup failures, and legacy journal registration against a scratch directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-history-changelog.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-history-changelog.c

## Purpose
Implements historical changelog consumption APIs for libgfchangelog. It locates HTIME metadata files for a requested timestamp range, decodes historical `CHANGELOG.*` files into the history scratch area, and exposes an iterator over processed history entries.

## APIs, Types, and Functions
Public APIs include `gf_history_changelog()`, `gf_history_changelog_scan()`, `gf_history_changelog_next_change()`, `gf_history_changelog_done()`, and `gf_history_changelog_start_fresh()`. Search and consume helpers include `gf_changelog_extract_min_max()`, `gf_history_b_search()`, `gf_history_check()`, `gf_history_get_timestamp()`, `gf_history_consume()`, `gf_changelog_consume_wrap()`, and `gf_is_changelog_usable()`.

## Control Flow, State, and Persistence
`gf_history_changelog()` opens `<changelog_dir>/htime`, scans HTIME files, extracts min/max timestamp and total count from filename plus `trusted.glusterfs.htime`, binary-searches fixed-length NUL-terminated path records for start/end indexes, and spawns detached `gf_history_consume()`. The consume thread reads records in bounded parallel batches, ignores lower-case `changelog.*` placeholders for empty files, decodes usable changelogs with `gf_changelog_consume(..., no_publish=true)`, then publishes decoded files after joins succeed. `hist_done` moves from 1 while parsing, to 0 when done, or -1 on parse/publish failure. `gf_history_changelog_scan()` rewrites the history tracker file from `.processing`, and `next_change()` reads one tracker line for consumers; `done()` validates the path with `realpath()` and moves it to `.processed`.

## Dependencies and Integration
Depends on `gf_changelog_journal_t` from the journal handler, HTIME constants and xattrs from `changelog-misc.h`, Gluster syscall wrappers, pthreads, and decode/publish routines from `gf-changelog-journal-handler.c`. It is used by legacy consumers that need historical replay before or alongside live journal callbacks.

## Risks and Test Signals
Risks include fixed-length record assumptions, directory scan ordering, static `is_last_scan`, detached background parsing with shared `hist_done`, partial-history heuristics using a 20-second window, path-name based empty-changelog detection, and possible resource handling issues on mid-loop failures. Test signals include timestamp range boundary searches, missing/invalid HTIME xattrs, partial history return code 1, no-history return -2, parallel consume errors, scan/next/done iterator behavior, and protection against marking files outside the history scratch tree done.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-history-changelog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/Makefile.am

## Purpose
Builds the changelog feature xlator module and declares its source, private headers, dependencies, and compiler flags.

## APIs, Types, and Functions
Declares `changelog.la` under `xlator_LTLIBRARIES`, installs it in the GlusterFS feature xlator directory, and lists sources: `changelog.c`, `changelog-rt.c`, `changelog-helpers.c`, `changelog-encoders.c`, `changelog-rpc.c`, `changelog-barrier.c`, `changelog-rpc-common.c`, and `changelog-ev-handle.c`. `noinst_HEADERS` lists internal headers such as helpers, memory types, RPC, event handling, encoders, misc constants, and messages.

## Control Flow, State, and Persistence
There is no runtime control flow. Build-time state is the automake recipe: module LDFLAGS, libglusterfs/gfxdr/gfrpc link dependencies, include paths to libglusterfs, RPC XDR, RPC transport socket, and the changelog library source directory. It forces `-fPIC`, 64-bit file offsets, `_GNU_SOURCE`, and `DATADIR`.

## Dependencies and Integration
Integrates the xlator with libglusterfs, RPC XDR, and RPC library artifacts. The include path to `xlators/features/changelog/lib/src` allows the xlator and libgfchangelog to share constants and RPC common headers.

## Risks and Test Signals
Risks include duplicated `changelog-rpc-common.h` in `noinst_HEADERS`, missing source entries when new helpers are added, and include-path coupling to the library implementation tree. Test signals are successful automake/configure builds, module load tests, and link failures catching missing RPC/XDR dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-barrier.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-barrier.c

## Purpose
Implements the changelog barrier queue used during snapshot-related explicit rollover. It temporarily queues FOP call stubs, disables the barrier on timeout or cleanup, and resumes queued calls.

## APIs, Types, and Functions
Exports `__chlog_barrier_enqueue()`, `__chlog_barrier_dequeue()`, `chlog_barrier_dequeue_all()`, `chlog_barrier_timeout()`, `__chlog_barrier_disable()`, and `__chlog_barrier_enable()`. It operates on `changelog_priv_t::queue`, `queue_size`, `barrier_enabled`, and `timer`.

## Control Flow, State, and Persistence
When barriering is enabled, FOP stubs are appended to `priv->queue`. Disabling cancels the timer, splices the queue into a caller-provided list, resets queue size, clears the enabled flag, and resumes every stub outside the lock. Enabling installs a Gluster timer with `priv->timeout`; timeout callback logs an error, disables the barrier under `priv->lock`, and drains the queue. No on-disk state is written.

## Dependencies and Integration
Depends on `call-stub.h`, Gluster timers, `changelog-helpers.h`, and message IDs. It is called from barrier/reconfigure paths in the main changelog translator and from `changelog_barrier_cleanup()` in `changelog-helpers.c`.

## Risks and Test Signals
Risks include timer cancellation races, queue resume ordering under failure, queue-size consistency, and ensuring stubs are never resumed while still protected by `priv->lock`. Test signals should cover enable failure, timeout disable, explicit cleanup, empty queue disable, and all queued FOPs resuming once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-barrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-encoders.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-encoders.c

## Purpose
Serializes changelog records into ASCII or binary on-disk formats, including optional records for fop number, entry path material, UID/GID/mode, and delete path capture.

## APIs, Types, and Functions
Conversion helpers are `entry_fn()`, `del_entry_fn()`, `fop_fn()`, `number_fn()`, `entry_free_fn()`, and `del_entry_free_fn()`. `changelog_encode_ascii()` and `changelog_encode_binary()` construct complete records and call `changelog_write_change()`. `changelog_encode_write_xtra()` serializes `changelog_opt_t` arrays. `changelog_encode_change()` selects `cb_encoder[priv->encode_mode]`.

## Control Flow, State, and Persistence
Encoding writes a one-byte type map from `priv->maps`, the target GFID as UUID text or raw `uuid_t`, optional NUL-separated extra records, and a final NUL. ASCII mode uses `uuid_utoa()` and converter callbacks; binary mode stores fixed binary fields where possible. The resulting buffer is written to the active `CHANGELOG` fd and later rolled over by helper code.

## Dependencies and Integration
Depends on `changelog-helpers.h` for `changelog_log_data_t`, optional record layouts, buffer macros, and write helpers. It is selected during rollover/open through `changelog_encode_change()` and invoked by `changelog_handle_change()`.

## Risks and Test Signals
Risks include `alloca()` sizing based on caller-maintained `cld_ptr_len`, converter/free callback mismatches, binary/ASCII decoder compatibility, and path strings containing separators. Test signals include byte-for-byte expected records for data/metadata/entry records, create/mkdir extra records, delete-path capture records, binary round-trip through the journal decoder, and write failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-encoders.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-encoders.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-encoders.h

## Purpose
Declares changelog record encoder APIs and low-level macros for storing the type marker plus GFID in ASCII or binary form.

## APIs, Types, and Functions
`CHANGELOG_STORE_ASCII()` writes mapped record type and textual GFID. `CHANGELOG_STORE_BINARY()` writes mapped type and raw `uuid_t`. The header declares optional-record converter/free helpers and the main `changelog_encode_binary()`, `changelog_encode_ascii()`, and `changelog_encode_change()` routines.

## Control Flow, State, and Persistence
The macros increment caller-owned offsets using `CHANGELOG_FILL_BUFFER()`. Persistent format decisions are delegated to the selected encoder mode in `changelog_priv_t`.

## Dependencies and Integration
Includes `changelog-helpers.h` for record structures, type maps, and buffer operations. Used by encoder implementation and snapshot logging helper code.

## Risks and Test Signals
Risks include macro argument naming inconsistency (`buf` parameter but `buffer` use), unchecked destination capacity, and ABI compatibility with libgfchangelog decoders. Test signals are compile coverage of macro expansions and decoder compatibility tests for both encoding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-encoders.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-ev-handle.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-ev-handle.c

## Purpose
Implements brick-side reverse event dispatch to libgfchangelog consumers. It manages reverse RPC clients, event selection reference counts, rotating buffer consumption, sequence numbering, and batched event sends.

## APIs, Types, and Functions
Dispatch helpers include `changelog_dispatch_vec()`, `changelog_event_dispatch_rpc()`, `changelog_ev_dispatch()`, `_dispatcher()`, and `sequencer()`. Connection lifecycle is handled by `changelog_rpc_notify()`, `changelog_ev_connector()`, `changelog_ev_queue_connection()`, `changelog_ev_cleanup_connections()`, `get_client()`, and `put_client()`. It defines `changelog_ev_program` for `CHANGELOG_REV_PROC_EVENT`.

## Control Flow, State, and Persistence
Probe handling in `changelog-rpc.c` enqueues `changelog_rpc_clnt_t` objects in `pending`. The connector thread creates RPC clients to the consumer’s reverse socket, and connect notifications move them to `active` while selecting their event filter. Dispatcher threads poll the rotating buffer once per second, claim consumable buffers, stamp sequence ranges, and send up to `NR_IOVEC` payload vectors per reverse RPC. Disconnect/destroy events disable clients, deselect filters, drop refs, and may trigger cleanup when xlator shutdown is pending.

## Dependencies and Integration
Depends on `rot-buffs`, shared RPC helpers, XDR event request types, event selection helpers in `changelog-helpers.c`, and RPC client lifecycle from libglusterfs. It is initialized by `changelog_init_rpc_threads()` in `changelog-rpc.c` and consumes events written by `changelog_dispatch_event()`.

## Risks and Test Signals
Risks include polling latency, coarse active-list locking while iterating clients, missing retransmit logic despite sequence acknowledgments, refcount/list races on disconnect, and buffer starvation under high event rates. Test signals include multi-client filtering, disconnect during dispatch, sequence continuity across split batches, NR_IOVEC boundary cases, and rotating-buffer empty/consumable/starvation return paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-ev-handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-ev-handle.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-ev-handle.h

## Purpose
Defines brick-side reverse RPC client and connection-list structures for changelog event delivery.

## APIs, Types, and Functions
`changelog_rpc_clnt_t` stores owning xlator, lock, atomic refcount, disconnect flag, filter mask, reverse socket path, owning `changelog_clnt_t`, RPC client pointer, list node, and cleanup callback. Inline helpers manage refs and disconnected state. `changelog_clnt_t` owns pending, active, and wait queues, their locks/conditions, the rotating buffer, and sequence counter. The header declares connector, dispatcher, queue, cleanup, and cleanup-notification functions.

## Control Flow, State, and Persistence
Pending clients are inserted under `pending_lock`, moved to active after connect under active locking, and destroyed after disconnect plus final ref release. Sequence state is held in memory and is reset when RPC threads initialize. No persistent state is represented here.

## Dependencies and Integration
Uses Gluster lists, locks, atomics, `rpc-clnt.h`, and `rot-buffs.h`. Included by `changelog-helpers.h`, `changelog-rpc.c`, and `changelog-ev-handle.c`.

## Risks and Test Signals
Risks include refcount underflow, `list_del()` on already removed nodes, lock-order mistakes between pending/active/wait locks, and stale socket/filter ownership. Test signals are thread-sanitized connect/disconnect tests, final unref cleanup, and queue transitions under simultaneous dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-ev-handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-helpers.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-helpers.c

## Purpose
Provides the main utility implementation for changelog persistence, event dispatch, HTIME metadata, rollover/fsync threads, inode-version suppression, snapshot drain/barrier support, local state cleanup, and path reconstruction.

## APIs, Types, and Functions
Thread and local helpers include `changelog_thread_cleanup()`, `changelog_local_init()`, `changelog_local_cleanup()`, and `changelog_get_usable_buffer()`. Event selection/dispatch uses `changelog_init_event_selection()`, `changelog_select_event()`, `changelog_deselect_event()`, `changelog_ev_selected()`, `changelog_dispatch_event()`, and `changelog_perform_dispatch()`. Persistence helpers include `changelog_write()`, `changelog_open_journal()`, `changelog_start_next_change()`, `changelog_rollover_changelog()`, `htime_create()`, `htime_open()`, `htime_update()`, `cl_is_empty()`, and `update_path()`. Runtime threads are `changelog_rollover()` and `changelog_fsync_thread()`. Update suppression uses `__changelog_inode_ctx_get()`, `changelog_inode_ctx_get()`, `changelog_update()`, and `changelog_forget()`. Snapshot/barrier helpers include `changelog_drain_black_fops()`, `changelog_drain_white_fops()`, `changelog_color_fop_and_inc_cnt()`, `changelog_dec_fop_cnt()`, `changelog_barrier_notify()`, `changelog_barrier_cleanup()`, `changelog_snap_*()`, `changelog_fill_entry_buf()`, and `resolve_pargfid_to_path()`.

## Control Flow, State, and Persistence
The active `CHANGELOG` file is opened with a version/encoding header, written via the selected encoder, periodically fsynced, then rolled over to `<changelog_dir>/YYYY/MM/DD/CHANGELOG.<timestamp>`. Rollover fsyncs/closes the current fd, detects empty files, renames or unlinks, updates HTIME records and xattrs, dispatches a journal event, and reopens a fresh journal unless final. HTIME files store fixed-length NUL-terminated changelog paths and xattrs with max timestamp plus rollover count; `HTIME_CURRENT` on the htime directory points at the active metadata file. Inode contexts cache per-type slice versions so repeated changes in one time slice are coalesced. Rollover switches black/white FOP colors, drains the previous color, sleeps one second for explicit rollovers, injects a rollover event through the dispatcher, then increments slice versions. Snapshot call-path logging writes `CHANGELOG.SNAP` under `csnap`.

## Dependencies and Integration
Depends on Gluster syscall wrappers, timers, iobufs, mem pools, inode ctx, rot-buffs, changelog encoders, RPC event dispatch, message IDs, and backend `.glusterfs` handle symlinks. It is central to the xlator FOP paths in `changelog.c`, runtime mode in `changelog-rt.c`, barrier code, and RPC event delivery.

## Risks and Test Signals
Risks include fixed path length assumptions, `alloca()` use in encoders/snapshot paths, HTIME record-length assumptions, explicit rollover races, cancellation cleanup around pthread locks, inode-version races if lock ordering changes, and delete-path reconstruction via backend symlinks. The source snapshot includes duplicated text around a rename log site, so a full build is an important signal. Tests should cover rollover with empty/nonempty files, HTIME create/open/update/xattrs, fsync interval zero/nonzero, repeated inode updates within a slice, black/white drain signaling, explicit rollover during normal timeout, CSNAP logging, and path reconstruction failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-helpers.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-helpers.h

## Purpose
Defines the changelog xlator’s private state, per-FOP local state, record structures, dispatcher contracts, barrier/drain state, and macros used by FOP implementations.

## APIs, Types, and Functions
Important types are `changelog_log_data_t`, `changelog_dispatcher_t`, `changelog_time_slice_t`, `changelog_rollover_t`, `changelog_fsync_t`, `drain_mgmt_t`, `barrier_notify_t`, `barrier_flags_t`, `changelog_ev_selector_t`, `changelog_priv_t`, `changelog_local_t`, `changelog_inode_ctx_t`, `changelog_entry_fields`, and `changelog_opt_t`. The header declares persistence, update, dispatch, barrier, snapshot, and path-resolution helpers. Macros initialize locals, fill optional records, manage iobuf refs, unwind FOPs with cleanup, skip inactive/internal operations, enforce FOP boundaries, update slice versions, and handle pthread errors.

## Control Flow, State, and Persistence
`changelog_priv_t` is the xlator’s state container: active/rpc flags, brick and changelog directories, file descriptors for changelog/HTIME/CSNAP, rollover counters, locks, type maps, dispatcher and encoder selections, drain colors/counters, barrier queue/timer, RPC server, rotating buffer, reverse clients, and cleanup counters. `changelog_local_t` carries one FOP’s pending record and optional previous entry for multi-record operations such as rename. Optional records are stored in an iobuf as `changelog_opt_t` arrays and later serialized by encoders.

## Dependencies and Integration
Includes Gluster locking, timers, iobufs, rot-buffs, call stubs, rpcsvc, changelog xlator declarations, event-handle types, misc constants, and message IDs. It is included by most changelog source files and by FOP code in `changelog.c`.

## Risks and Test Signals
Risks include macro-heavy control flow, lock-order coupling, manual optional-record memory ownership, fd lifetime complexity, and many state fields that must be initialized consistently in the main xlator. Test signals include compile coverage of all FOP macros, memory leak checks for optional records, lock-order stress around rollover, and state initialization/reconfigure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-mem-types.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-mem-types.h

## Purpose
Allocates changelog-specific memory accounting IDs above `gf_common_mt_end`.

## APIs, Types, and Functions
`enum gf_changelog_mem_types` defines IDs for xlator private state, strings, batches, runtime dispatcher data, inode ctx, RPC clients, libgfchangelog connection and entry state, rate-limit/listener state, changelog buffers, history data, lib call pools, events, event dispatchers, and an end marker.

## Control Flow, State, and Persistence
No control flow or persistent state. The IDs are used with `GF_CALLOC`, mem pools, and `xlator_mem_acct_init()` to attribute allocations.

## Dependencies and Integration
Includes `glusterfs/mem-types.h`. Used by both the xlator and libgfchangelog code, so IDs must remain stable enough for diagnostics across the shared component.

## Risks and Test Signals
Risks include collisions if `gf_common_mt_end` moves unexpectedly or new IDs are inserted without updating init bounds. Test signals are successful `xlator_mem_acct_init(..., gf_changelog_mt_end)` and allocation accounting reports showing expected buckets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-messages.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-messages.h

## Purpose
Defines structured log message IDs and canonical message strings for the changelog xlator.

## APIs, Types, and Functions
Uses `GLFS_MSGID(CHANGELOG, ...)` to reserve IDs for open/rename/read/write/fsync errors, barrier state, pthread failures, HTIME operations, RPC lifecycle, cleanup, event dispatch, and snapshot logging. String macros provide reusable human-readable messages such as `CHANGELOG_MSG_HTIME_ERROR_STR`, `CHANGELOG_MSG_RPC_CONNECT_ERROR_STR`, and `CHANGELOG_MSG_BARRIER_TIMEOUT_STR`.

## Control Flow, State, and Persistence
No runtime state. The comment documents the stability rule: append new message IDs and never remove existing IDs to avoid reuse.

## Dependencies and Integration
Includes `glusterfs/glfs-message-id.h` and is included throughout the changelog xlator implementation. Library-side files use a separate `changelog-lib-messages.h`.

## Risks and Test Signals
Risks include accidental ID deletion/reordering, missing string macros for new IDs, and inconsistent structured key usage in `gf_smsg()` calls. Test signals are build-time ID generation, log-format checks, and review of appended-only message changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-misc.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-misc.h

## Purpose
Collects shared changelog format constants, socket path builders, header parsing macro, HTIME/CSNAP path macros, event type enums, mode enum, and encoder enum.

## APIs, Types, and Functions
Defines file and xattr names (`CHANGELOG`, `HTIME`, `CHANGELOG.SNAP`, `trusted.glusterfs.htime`, `trusted.glusterfs.current_htime`), format version 1.2, Unix socket templates, `CHANGELOG_HEADER`, `CHANGELOG_MAKE_SOCKET_PATH()`, `CHANGELOG_MAKE_TMP_SOCKET_PATH()`, `CHANGELOG_GET_HEADER_INFO()`, `CHANGELOG_FILL_HTIME_DIR()`, `CHANGELOG_FILL_CSNAP_DIR()`, `changelog_log_type`, `changelog_mode_t`, `changelog_encoder_t`, and predicates for valid encoding and internal record types.

## Control Flow, State, and Persistence
The header establishes persistent on-disk format details: header text, major/minor version, encoding values, changelog type values, and HTIME xattr names. Socket macros hash brick paths with xxh64 to create stable per-brick Unix socket paths and process-specific temporary reverse socket paths.

## Dependencies and Integration
Requires Gluster defaults and xxhash wrapper visibility through including translation units. Used by both xlator and library decoders, so it is the compatibility hinge between writer and reader.

## Risks and Test Signals
Risks include format-string coupling in `CHANGELOG_GET_HEADER_INFO()`, path truncation from hashed socket templates, and ABI impact if enum values change. Test signals include header parse round-trips, socket path stability for brick paths, and decoder rejection of invalid encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc-common.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc-common.c

## Purpose
Provides shared RPC client/server utilities used by both the brick-side changelog xlator and libgfchangelog.

## APIs, Types, and Functions
Client helpers are `changelog_rpc_poller()`, `changelog_rpc_client_init()`, `changelog_rpc_sumbit_req()`, and `changelog_invoke_rpc()`. Server helpers are `__changelog_rpc_serialize_reply()`, `changelog_rpc_sumbit_reply()`, `changelog_rpc_server_init()`, and `changelog_rpc_server_destroy()`.

## Control Flow, State, and Persistence
Client initialization builds Unix transport options, creates an RPC client, registers notify callbacks, and starts it. Request submission optionally XDR-serializes a request into an iobuf/iobref and submits it with extra payload vectors. `changelog_invoke_rpc()` creates a call frame, invokes the procedure-table function, and destroys the stack. Server initialization builds Unix listener options, initializes `rpcsvc`, registers notify, creates listeners, and registers each supplied program. Reply submission serializes an XDR reply and sends optional payloads. No persistent files are written except Unix socket files created by RPC transport setup and removed by callers/destroy paths.

## Dependencies and Integration
Depends on Gluster RPC client/server APIs, Unix transport option builders, iobuf/iobref pools, XDR helpers, and message IDs. It is included by `changelog-rpc.c`, `changelog-ev-handle.c`, `gf-changelog-rpc.c`, and `gf-changelog-reborp.c`.

## Risks and Test Signals
Risks include typo-preserved API name `sumbit`, iobuf/iobref ownership mistakes, freeing `rpcsvc_t` differently during brick multiplex cleanup, missing socket unlink in common destroy, and call-frame lifecycle assumptions. Test signals include request/reply serialization failures, client notify registration failure, listener/program registration failure, payload plus XDR requests, and cleanup under active transport disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc-common.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc-common.h

## Purpose
Defines shared RPC program numbers, procedure numbers, common RPC state, and function prototypes for changelog forward and reverse RPC paths.

## APIs, Types, and Functions
Forward procedures are `CHANGELOG_RPC_PROC_NULL` and `CHANGELOG_RPC_PROBE_FILTER` under `CHANGELOG_RPC_PROGNUM` version 1. Reverse procedures are `CHANGELOG_REV_PROC_NULL` and `CHANGELOG_REV_PROC_EVENT` under `CHANGELOG_REV_RPC_PROCNUM` version 1. `NR_ROTT_BUFFS` and `NR_DISPATCHERS` size the event rotating-buffer/dispatcher setup. `changelog_rpc_t` groups an RPC service, client, and socket path. Prototypes cover poller, client init, request submission, invocation, reply submission, server init, and server destroy.

## Control Flow, State, and Persistence
No direct control flow. The constants define the network/RPC ABI between the xlator and libgfchangelog and the default dispatcher topology.

## Dependencies and Integration
Includes `rpcsvc.h`, `rpc-clnt.h`, `gf-event.h`, and generated `changelog-xdr.h`. Used from both source trees, making it a shared contract.

## Risks and Test Signals
Risks include program-number/procedure-number incompatibility, hard-coded dispatcher counts, and ABI drift with generated XDR structures. Test signals are interop between xlator and library built from the same headers plus negative tests for mismatched procedure numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc.c

## Purpose
Implements the brick-side changelog RPC server that accepts probe filter requests from libgfchangelog clients, creates reverse client records, and manages event-dispatch worker threads and cleanup.

## APIs, Types, and Functions
Public functions are `changelog_init_rpc_listener()`, `changelog_destroy_rpc_listner()`, and `changelog_cleanup_rpc_threads()`. Internal helpers include `changelog_init_rpc_threads()`, `changelog_cleanup_dispatchers()`, `changelog_rpcsvc_notify()`, `changelog_process_cleanup_event()`, `changelog_rpc_clnt_init()`, `changelog_rpc_clnt_cleanup()`, and `changelog_handle_probe()`. It defines `changelog_svc_prog` with actor `CHANGELOG_RPC_PROBE_FILTER`.

## Control Flow, State, and Persistence
Initialization sets up `priv->connections`, pending/active/wait queues, connector thread, dispatcher threads, and a Unix socket listener derived from the brick path. On probe, the server XDR-decodes `changelog_probe_req`, allocates `changelog_rpc_clnt_t` with the requested reverse socket and filter, and queues it for `changelog_ev_connector()`. RPC service notify tracks accepted listeners/transports and disconnects; when listener and client counts reach zero during cleanup, it notifies parent down, unlinks the socket, unregisters notify, destroys rxpool, and frees the rpc object.

## Dependencies and Integration
Depends on common RPC helpers, event-handle types, socket transport private data, Gluster atomics/list locks, and changelog xlator private state. Called from the main xlator initialization/reconfigure paths and feeds reverse dispatch in `changelog-ev-handle.c`.

## Risks and Test Signals
Risks include cleanup races among listener count, transport count, and client count; socket unlink timing; partial thread initialization cleanup; and XDR request strings copied by length without explicit NUL in lower layers. Test signals include probe success/failure, multiple clients with different filters, transport disconnect cleanup, brick cleanup with active reverse clients, dispatcher thread cancellation, and listener recreation on reconfigure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc.h

## Purpose
Declares brick-side changelog RPC listener lifecycle APIs and the public RPC program name.

## APIs, Types, and Functions
Defines `CHANGELOG_RPC_PROGNAME` as `GlusterFS Changelog`. Declares `changelog_init_rpc_listener()`, `changelog_destroy_rpc_listner()`, and `changelog_cleanup_rpc_threads()`.

## Control Flow, State, and Persistence
The header has no state. The declared APIs start the probe listener plus event dispatcher threads, destroy the listener, and clean worker thread/lock resources.

## Dependencies and Integration
Includes `changelog-helpers.h` and `changelog-rpc-common.h`. It is used by main xlator code that manages startup, cleanup, and reconfigure.

## Risks and Test Signals
Risks include spelling compatibility of `listner`, no ownership detail for `rbuf_t`, and cleanup ordering hidden from callers. Test signals are compile coverage and lifecycle tests around init/destroy/reinit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rt.c -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rt.c

## Purpose
Implements the real-time changelog dispatch mode, serializing change handling behind a simple lock.

## APIs, Types, and Functions
`changelog_rt_init()` allocates `changelog_rt_t`, initializes its lock, stores it in `changelog_dispatcher_t::cd_data`, and sets `dispatchfn` to `changelog_rt_enqueue()`. `changelog_rt_fini()` destroys and frees that state. `changelog_rt_enqueue()` locks, calls `changelog_handle_change()` for the primary record and optional second record, then unlocks.

## Control Flow, State, and Persistence
The runtime state is a single lock protecting writes and rollover/fync handling in the selected dispatch mode. Persistence is delegated to `changelog_handle_change()`, so this file enforces ordering rather than writing files directly.

## Dependencies and Integration
Depends on Gluster locks, logging, memory accounting, and changelog helper APIs. Selected by the changelog bootstrap table in the main xlator for `CHANGELOG_MODE_RT`.

## Risks and Test Signals
Risks include serialization bottlenecks, missing error handling if lock initialization fails, and no batching beyond the optional second record. Test signals include ordered two-record rename handling, concurrent FOP updates producing non-interleaved records, and clean init/fini under reconfigure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rt.h -->
# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rt.h

## Purpose
Declares the real-time changelog dispatcher state and lifecycle/enqueue functions.

## APIs, Types, and Functions
Defines `changelog_rt_t` with a `gf_lock_t`. Declares `changelog_rt_init()`, `changelog_rt_fini()`, and `changelog_rt_enqueue()`.

## Control Flow, State, and Persistence
No direct control flow in the header. It describes a dispatcher mode whose only private state is a lock, with persistence handled by the shared change handler.

## Dependencies and Integration
Includes Gluster locking/timer headers and `changelog-helpers.h`. Used by bootstrap code and `changelog-rt.c`.

## Risks and Test Signals
Risks include the “unused as of now” comment drifting from actual use and the minimal state limiting future mode extension. Test signals are compile coverage and mode initialization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rt.h -->
