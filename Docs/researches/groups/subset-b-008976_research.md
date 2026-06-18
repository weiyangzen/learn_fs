# subset-b-008976 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_conn.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_conn.c

Purpose: connection-level setup, configuration, teardown, and statistics initialization for WiredTiger eviction. This file owns the `WT_CONNECTION_IMPL::evict` allocation, validates eviction threshold configuration, creates the condition variable/spinlocks/internal walk session/three eviction queues, and exports threshold and runtime state into connection statistics.

Important APIs and functions: `__wt_evict_config` parses `eviction.*`, `cache_max_wait_ms`, `cache_stuck_timeout_ms`, and application-eviction control settings, then resizes the eviction thread group during reconfiguration. `__evict_validate_config` converts absolute byte settings to percentages, rejects absolute sizes under shared cache, clamps dirty/checkpoint/update thresholds into consistent relationships, and stores `eviction_updates_trigger` atomically. `__wt_evict_create` allocates `WT_EVICT`, seeds read-generation counters, opens the `"evict pass"` internal session, allocates `WTI_EVICT_QUEUE_MAX` queues, and initializes stats. `__wt_evict_destroy` tears down locks, condition variables, queue arrays, and the internal session. `__wt_evict_stats_update` and `__wt_evict_stats_init` publish thresholds, max eviction latencies, queue attempts, active worker counts, and pass-state fields.

Control flow: startup calls `__wt_evict_create`, which immediately delegates to `__wt_evict_config` before any worker threads are created. Runtime reconfigure calls `__wt_evict_config(..., true)` and may resize `conn->evict_config.threads`. Shutdown must stop eviction threads before `__wt_evict_destroy`, because queues and `walk_session` are freed here.

State and persistence behavior: all state is in-memory connection state: threshold doubles, atomic trigger fields, read generations, per-queue arrays, locks, statistics, and the eviction walk session. No pages are persisted here, but the thresholds strongly affect when dirty pages are reconciled and therefore when durable images are written. Shared-cache mode is important because absolute thresholds would become stale as the assigned cache size changes.

Dependencies and integration points: depends on WiredTiger config parsing, atomics, condition variables, spinlocks, internal sessions, thread-group APIs, and statistics macros. It integrates with `evict_thread.c` for worker lifecycle, `evict_queue.c` for queue storage, `evict_inline.h` for threshold checks, and public connection open/reconfigure/close paths.

Risks and test signals: threshold validation is high risk because invalid target/trigger relationships can make eviction impossible; tests should cover percentages, absolute byte conversion, shared-cache rejection, precise-checkpoint defaults, dirty/checkpoint/update clamping, and min/max worker validation. Reconfigure tests should verify thread-group resizing and atomic update-trigger visibility. Startup/shutdown tests should exercise partial initialization failures, stats initialization, and destruction after thread teardown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_dispatch.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_dispatch.c

Purpose: dispatches already-queued eviction candidates to the page eviction path and provides the application-thread assist loop. It is the bridge between queue selection (`WTI_EVICT_QUEUE` entries) and `__wt_evict` in `evict_page.c`, with special handling for urgent pages and application threads blocked by cache pressure.

Important APIs and functions: `__evict_get_ref` chooses a candidate from the urgent queue or rotating ordinary queues, locks the candidate `WT_REF` with a CAS to `WT_REF_LOCKED`, increments `btree->evict_busy`, clears the queue entry, and returns the locked ref plus its previous state. `__wti_evict_page` calls `__evict_get_ref`, records server/worker/application statistics, bumps page read generation, invokes `__wt_evict` under the candidate btree, and drops `evict_busy`. `__wti_evict_app_assist_worker` is the loop used by foreground sessions when cache thresholds require application eviction; it checks stuck-cache rollback conditions, operation/cache wait timeouts, transaction pinning, user interruption, and queue-empty waits. `__wt_evict_page_urgent` inserts a specific page into the urgent queue, clearing ordinary queue membership when safe. `__wt_evict_priority_set` and `__wt_evict_priority_clear` adjust per-btree eviction priority used by walking logic.

Control flow: server and worker threads repeatedly enter `__wti_evict_page`; application sessions reach `__wti_evict_app_assist_worker` through inline threshold checks. Candidate selection first avoids locks when queues are empty, then uses the connection queue lock to pick a queue, then uses the individual queue lock to scan candidates. Dirty pages are skipped by server/application callers unless urgent or hard dirty/update pressure permits them.

State and persistence behavior: updates are in-memory state transitions: queue pointers, `WT_PAGE_EVICT_LRU(_URGENT)` flags, `WT_REF` states, `btree->evict_busy`, wait/attempt/failure counters, and session cache wait accounting. Persistence occurs only indirectly through `__wt_evict`, which may reconcile dirty pages.

Dependencies and integration points: depends on queue helpers from `evict_inline.h`, queue storage from `evict_private.h`, page eviction from `evict_page.c`, server wakeup from `evict_thread.c`, history-store cursor caching, transaction oldest/blocking checks, condition variables, and event-handler interruption.

Risks and test signals: race safety around queue locks and `WT_REF_CAS_STATE` is critical; tests should stress duplicate queue entries, urgent queue races, ordinary-to-urgent promotion, closing btrees with `evict_busy`, and worker/server queue switching. Application-assist tests should cover `cache_max_wait_ms` rollback, operation timeout, cache-stuck blocker rollback, read-only sessions, dirty hard pressure, interruptible event handlers, and `WT_NOTFOUND` wait/retry behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_dispatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_exclusive.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_exclusive.c

Purpose: controls exclusive eviction access for a single btree/file. It prevents the normal eviction server and urgent-queue paths from walking or queuing pages in a tree while schema, close, verify, or whole-file eviction operations need stable ownership.

Important APIs and functions: `__wti_evict_lock_handle_list` acquires the connection dhandle read lock using a custom yield/sleep loop that aborts quickly when `evict->pass_intr` is set. `__wti_evict_set_saved_walk_tree` maintains the eviction server's saved walk dhandle and adjusts `session_inuse` counts so the handle cannot disappear while saved. `__wt_evict_file_exclusive_on` increments `S2BT(session)->evict_disabled`, interrupts an active eviction pass, clears saved walks for the current tree, removes all queued entries for the btree from ordinary and urgent queues, and waits for `btree->evict_busy` to drain. `__wt_evict_file_exclusive_off` atomically decrements `evict_disabled` without taking the walk lock to avoid a documented lock-order deadlock.

Control flow: callers acquire exclusive mode before whole-file eviction or sensitive tree operations. The first entrant takes `evict_walk_lock`; nested entrants just increment `evict_disabled` and return. Exclusive-on clears prefetch references, increments `pass_intr`, runs the saved-walk clear under the pass lock, scans all queue arrays under queue locks, then waits until in-flight dispatch operations release the btree. Exclusive-off releases the counter and logs.

State and persistence behavior: all direct state is in-memory synchronization state: `evict_disabled`, `pass_intr`, `walk_tree`, dhandle `session_inuse`, queue entries, page LRU flags, and btree `evict_busy`. It protects persistence-sensitive operations by ensuring normal eviction cannot reconcile or discard pages from the tree concurrently.

Dependencies and integration points: integrates with the connection dhandle lock, eviction pass lock, queue helpers, prefetch clearing, verbose logging, schema/open/close paths, and `__wt_evict_file`. It is tightly coupled to `evict_queue.c` queue clearing and to the eviction server's saved-walk behavior in `evict_thread.c`.

Risks and test signals: this file is lock-order sensitive. Tests should stress concurrent open/close/schema operations with active eviction, nested exclusive acquisition, urgent queue entries for the same tree, prefetch references, interrupted eviction walks, and diagnostic assertions on `evict_ref`. Deadlock tests should specifically cover the pass-lock versus walk-lock ordering described in `__wt_evict_file_exclusive_off`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_exclusive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_file.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_file.c

Purpose: performs whole-file/tree eviction for close and discard operations. It walks every cached page in a btree under exclusive eviction access and either reconciles dirty content for close or discards pages directly for discard.

Important API: `__wt_evict_file(WT_SESSION_IMPL *session, WT_CACHE_OP syncop)` supports `WT_SYNC_CLOSE` and `WT_SYNC_DISCARD`. For close, dirty pages are reconciled with `WT_REC_EVICT`, `WT_REC_EVICT_CALL_CLOSING`, `WT_REC_CLEAN_AFTER_REC`, `WT_REC_VISIBLE_NO_SNAPSHOT`, and usually `WT_REC_HS` unless the file is history store, metadata, or disaggregated metadata. For discard, it validates that pages are safe to lose and calls `__wt_ref_out` without reconciliation.

Control flow: the function asserts `evict_disabled > 0` or the handle is no longer open, exits early when the root has no page, updates the oldest transaction ID, and handles a disaggregated discard guard via `__wt_btree_can_discard`. It walks with `WT_READ_CACHE | WT_READ_NO_EVICT` and uses `WT_READ_VISIBLE_ALL` when the session has no snapshot. Each returned page is reconciled before advancing the walk because reconciliation can reshape the tree; then the previous ref is evicted or discarded.

State and persistence behavior: for `WT_SYNC_CLOSE`, dirty pages are written/reconciled before `__wt_evict` updates refs and frees in-memory pages, preserving durability and history-store requirements. For `WT_SYNC_DISCARD`, both clean and dirty in-memory images can be discarded, so disaggregated checks prevent losing pages that cannot be retrieved later. The function clears any outstanding tree-walk reference on error.

Dependencies and integration points: depends on exclusive eviction from `evict_exclusive.c`, tree walking, transaction oldest updates, reconciliation, page eviction, disaggregated materialization checks, and close/discard callers in btree/schema lifecycle code.

Risks and test signals: the ordering of reconcile-before-next-walk prevents missing pages after tree shape changes. Tests should cover close of dirty trees, empty trees, instantiated/deleted pages, disaggregated discard when pages cannot be discarded, checkpoint snapshot/no-snapshot sessions, `WT_SYNC_DISCARD` during connection closing, and error cleanup when reconciliation or eviction returns `EBUSY`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_inline.h -->
## sources/storage-engines/wiredtiger/src/evict/evict_inline.h

Purpose: shared inline eviction policy and accounting helpers. This header defines read-generation manipulation, pressure/threshold checks, application-assist gating, queue predicates, page-cache byte decrements, and small helpers used across eviction, cache, reconciliation, cursor, and page-access paths.

Important APIs and helpers: `__wt_evict_aggressive` and `__wt_evict_cache_stuck` expose escalating stuck-cache state from `evict_aggressive_score`. `__wti_evict_read_gen_bump`, `__wti_evict_read_gen_new`, `__wt_evict_page_soon`, `__wt_evict_touch_page`, and related predicates manage LRU read-generation state including forced eviction markers `WT_READGEN_EVICT_SOON` and `WT_READGEN_WONT_NEED`. `__wt_evict_page_cache_bytes_decr` subtracts evicted page memory, dirty bytes, update bytes, internal bytes, disaggregated stable/ingest bytes, and page counters from btree and cache accounting. `__wt_evict_clean_needed`, `__wt_evict_dirty_needed`, `__wti_evict_updates_needed`, and `__wt_evict_needed` compute clean/dirty/update pressure against configured thresholds. `__wt_evict_app_assist_worker_check` decides whether a foreground session may or must run eviction. `__evict_list_clear`, `__evict_queue_empty`, `__evict_queue_full`, and `__evict_page_updates_candidate` support queue management.

Control flow: page access paths initialize/touch read generations; eviction walks and dispatch consult the queue helpers; the server and application threads consult threshold helpers; successful page eviction calls cache-byte decrement when the page is released. Application-assist gating exits early for sessions that cannot safely reconcile, are checkpoint workers, hold locks, ignore cache size, operate on in-memory/cache-resident trees, or are still below configured tolerance.

State and persistence behavior: the header mutates atomic page `read_gen`, page flags, btree/cache byte counters, eviction progress, session cache wait decisions, and cache-control flags. It does not write persistent data, but it controls when reconciliation is requested and whether dirty/update pressure is allowed to force application threads into eviction.

Dependencies and integration points: used by every file in this eviction group plus page read/modify paths. It depends on cache accounting APIs, connection/disaggregated flags, transaction state, session lock flags, event handlers, btree metadata, and stats macros.

Risks and test signals: cache accounting mistakes here can produce negative counters or false cache-full decisions. Tests should stress eviction of internal/leaf pages, dirty/update byte accounting, shared disk references, disaggregated ingest/stable trees, `WT_READGEN_WONT_NEED` pages dirtied later, application eviction tolerance buckets, incremental app eviction, in-memory connections, checkpoint-worker exclusions, and queue empty/full boundary cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_page.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_page.c

Purpose: core page eviction implementation. It takes exclusive access to a candidate page, verifies that eviction is legal, reconciles dirty content when needed, updates the parent/ref state, handles splits and deleted refs, records detailed stats, and optionally stores clean disaggregated leaf pages in the victim cache.

Important functions: `__wt_evict` is the public page eviction entry point used by workers, application assists, urgent eviction, and file close. `__evict_exclusive` rejects pages with hazard pointers. `__evict_review` checks active children, obsolete time-window cleanup, in-memory clean-page restrictions, `__wt_page_can_evict`, checkpoint/history-store blockers, precise-checkpoint repeated reconciliation, garbage-collection prune timestamp, and `WT_SESSION_NO_RECONCILE`. `__evict_reconcile` constructs reconciliation flags for urgent, closing, history-store, metadata, in-memory, scrub, disaggregated, checkpoint-running, and snapshot cases, then calls `__wt_reconcile`. `__evict_page_clean_update` and `__evict_page_dirty_update` transform reconciled pages into `WT_REF_DISK`, `WT_REF_DELETED`, split pages, or rewritten in-memory pages. `__evict_child_check` verifies internal-page children are all disk/deleted and that deleted children are visible. `__evict_page_victim_cache` writes eligible clean disaggregated leaf disk images into the page-log victim cache.

Control flow: `__wt_evict` enters eviction/split generations, handles urgent stats, obtains hazard exclusivity when not closing, clears queue membership, reviews the page, optionally performs an in-memory split, reconciles dirty pages, then updates the ref according to clean/dirty/reconciliation result. After a successful ref update, failure is no longer allowed. Errors before that restore the previous ref state unless closing.

State and persistence behavior: persistent writes happen through reconciliation, with history-store and scrub behavior controlled by flags. Dirty update results include empty-page deletion, multiblock split/rewrite, and one-for-one replace. Clean eviction may cache disaggregated page images after writing a disaggregated block header/checksum and byte-swapping the page header. In-memory state includes ref state, page modify state, split metadata, eviction progress/stat maxima, generation membership, and victim-cache side effects.

Dependencies and integration points: depends on hazard pointers, reconciliation, split/reverse-split code, transaction snapshots, history store, checkpoint state, disaggregated block/page-log APIs, cache accounting, tree walking visibility rules, and queue clearing. It is called by `evict_dispatch.c` and `evict_file.c`.

Risks and test signals: this is the highest-risk eviction file. Tests should cover hazard blocking, internal pages with active/deleted children, reverse split busy paths, dirty leaf reconciliation with and without snapshots, application snapshot refresh/restore, precise checkpoint blockers, history-store dirty-cache blockers, disaggregated dirty scrub assertions, victim-cache compression/checksum/header behavior, multiblock split/rewrite, empty-page deletion, root eviction, and panic if a post-reconciliation non-`EBUSY` error occurs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_private.h -->
## sources/storage-engines/wiredtiger/src/evict/evict_private.h

Purpose: private eviction subsystem declarations and data structures shared by the eviction implementation files. It defines queue sizing constants, candidate/queue structs, a pass-lock helper macro, and prototypes generated for internal eviction APIs.

Important types and constants: `WTI_EVICT_MAX_TREES`, `WTI_EVICT_WALK_BASE`, and `WTI_EVICT_WALK_INCR` shape how many tree walk points and candidate entries eviction tracks. `WT_EVICT_HAS_WORKERS(session)` tests whether the configured thread group has more than the server thread. `WTI_EVICT_ENTRY` stores a candidate btree, ref, and score. `WTI_EVICT_QUEUE` stores the spinlock, queue array, current pointer, candidate count, entry count, and maximum slot used. `WTI_EVICT_QUEUE_MAX` reserves two ordinary queues plus one urgent queue at `WTI_EVICT_URGENT_QUEUE`. `WTI_WITH_PASS_LOCK` wraps the pass lock with session lock-flag tracking.

Declared APIs: the header exposes queue/candidate functions (`__wti_evict_push_candidate`, `__wti_evict_lru_walk`, `__wti_evict_walk`, queue clearing), dispatch/application functions (`__wti_evict_page`, `__wti_evict_app_assist_worker`), saved-walk/exclusive helpers, handle-list locking, and inline policy functions implemented in `evict_inline.h`.

Control flow and integration: included by `wt_internal.h` consumers inside the eviction subsystem. It is the shared contract between queue production (`evict_lru.c`/walk code outside this item), queue consumption (`evict_dispatch.c`), queue maintenance (`evict_queue.c`), exclusive locking (`evict_exclusive.c`), and server orchestration (`evict_thread.c`).

State and persistence behavior: the structs represent in-memory candidate state only. They indirectly protect persistent page state by ensuring a queued ref is associated with its owning btree and can be locked before reconciliation/discard.

Risks and test signals: struct fields are lock-protected by convention, so misuse can cause races or stale refs. Tests should exercise queue capacity boundaries, urgent queue indexing, worker-count behavior with one versus multiple threads, pass-lock interruption, and generated prototype drift. ABI risk is internal but high because all eviction files agree on these layouts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_queue.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_queue.c

Purpose: manages eviction candidate queues after the tree walk has discovered pages. It sorts candidates by score, trims and counts usable entries, rotates two ordinary queues, maintains the urgent queue indirectly through shared helpers, and lets workers drain queued pages.

Important functions: `__evict_lru_cmp` sorts non-null candidates by eviction score and null entries last; `__evict_lru_cmp_debug` ignores score so debug aggressive mode can test alternate behavior. `__wti_evict_queue_clear_page` and `__wti_evict_queue_clear_page_locked` remove a ref from all queues and clear page LRU flags. `__wti_evict_lru_pages` repeatedly calls `__wti_evict_page`, treating `EBUSY` as a nonfatal candidate failure and waiting when worker queues are empty. `__wti_evict_lru_walk` rotates/fills queues, calls `__wti_evict_walk` to populate entries, sorts and trims them, chooses `evict_candidates`, updates read-generation oldest, records queued clean/dirty/update stats, sets `evict_current`, and signals waiting workers.

Control flow: the eviction server calls `__wti_evict_lru_walk` during a pass when cache pressure exists. The current fill queue alternates with the other ordinary queue; full queues may be skipped unless empty-score pressure is high. After population, candidates are sorted so lower scores and forced-eviction read generations are tried first. Workers call `__wti_evict_lru_pages` to consume candidates through dispatch.

State and persistence behavior: queue state is entirely in memory: candidate arrays, current pointers, candidate/entry counts, page `WT_PAGE_EVICT_LRU` flags, `evict_empty_score`, and `read_gen_oldest`. It does not persist pages itself; it decides which pages will reach `evict_page.c`.

Dependencies and integration points: depends on the eviction walk implementation (`__wti_evict_walk`), dispatch (`__wti_evict_page`), queue helpers from `evict_inline.h`, stats, condition variables, and debug flags. Queue locks must coordinate with urgent insertion in `evict_dispatch.c` and exclusive clearing in `evict_exclusive.c`.

Risks and test signals: queue races can leave page flags set or refs stale. Tests should stress clearing pages while workers drain, both ordinary queues full, empty-score escalation, aggressive mode candidate selection, trimming entries over `WTI_EVICT_WALK_BASE`, null entries from failed walks, worker `WT_NOTFOUND` waits, and stats for queued dirty/update candidates.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_stat.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_stat.c

Purpose: gathers detailed per-data-source cache/eviction statistics by walking the in-memory tree. It backs the `cache_walk` diagnostic configuration rather than normal connection-level eviction operation.

Important functions: `__wt_evict_cache_stat_walk` records root and current eviction generation stats, then calls the private `__evict_stat_walk`. `__evict_stat_walk` walks cached refs with `__wt_tree_walk_count` and records page counts, clean/dirty split, internal/leaf split, queued/not-queueable refs, disk-image sizes, memory-only pages, allocation-size anomalies, visited/unvisited age, and read-generation gaps.

Control flow: a stats-enabled session calls `__wt_evict_cache_stat_walk` while positioned on a btree. The walker uses `WT_READ_CACHE | WT_READ_NO_EVICT | WT_READ_INTERNAL_OP | WT_READ_NO_WAIT | WT_READ_VISIBLE_ALL` so it observes cache state without triggering eviction or waiting on unavailable pages. Root stats are read directly from the root page index and root memory footprint.

State and persistence behavior: this file only reads cache/tree/page state and writes data-source statistics. It does not mutate pages or persistent storage. It reads `page->evict_pass_gen`, `page->cache_create_gen`, disk image sizes, queue flags, and page dirty state to infer eviction-walk effectiveness.

Dependencies and integration points: depends on tree walking, page evictability checks, data-source stats macros, btree allocation size, root page index access, and connection eviction generation. It complements `evict_verbose.c`, which prints similar diagnostics to the message stream.

Risks and test signals: diagnostics must avoid blocking or changing cache state. Tests should cover trees with root-only pages, queued pages, dirty/internal/leaf pages, pages without disk images, disk images smaller than allocation size, skipped refs from no-wait walks, and disabled `cache_walk` versus enabled data-source stats. Race tolerance matters because it reads live page and generation values without freezing eviction.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_thread.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_thread.c

Purpose: owns eviction thread lifecycle, the server loop, cache-pressure state computation, stuck-cache diagnostics, and dynamic worker tuning. It decides when to walk for candidates, when to drain pages, when to sleep, and how many worker threads should be active.

Important functions: `__wt_evict_threads_create` starts the thread group and marks `server_running`; `__wt_evict_threads_destroy` clears the server flag, wakes the server, and destroys the group under the group write lock. `__evict_thread_run` marks sessions as eviction sessions, caches a history-store cursor, runs the server when it can take `evict_pass_lock`, or otherwise helps drain queues. `__evict_server` runs one server iteration, clears saved walks when not stuck, detects stuck progress, and optionally dumps transaction/cache state or times out in diagnostic builds. `__evict_update_work` computes `WT_EVICT_CACHE_*` flags from clean/dirty/update usage, urgent queue state, history-store cache usage, scrub policy, in-memory mode, and debug flags. `__evict_pass` increments generations, updates oldest transaction ID, walks queues, drains pages when needed, and raises/lowers aggressive score. `__evict_tune_workers` adjusts worker count based on evicted pages per second.

Control flow: the thread group repeatedly invokes `__evict_thread_run`. One thread acts as server while holding the pass lock; other threads or failed pass-lock attempts drain queues. A pass updates cache pressure, walks candidates when `WT_EVICT_CACHE_ALL` is set, lets the server evict if no workers exist, and escalates aggressive/stuck state when `eviction_progress` does not advance.

State and persistence behavior: direct state is in-memory: server flags, `server_running`, eviction flags, generations, aggressive score, stuck timer, worker tuning measurements, history-store byte snapshots, scrub/nokeep decisions, and condition-variable wakeups. Persistence happens indirectly when selected dirty pages are reconciled by worker/application paths.

Dependencies and integration points: integrates with thread groups, condition variables, transaction oldest/snapshot state, history-store cursor cache, queue walk/drain functions, exclusive saved-walk clearing, verbose diagnostics, and connection close/recovery flags.

Risks and test signals: timing and concurrency dominate. Tests should cover startup after recovery, shutdown with live workers, pass interruption, stuck-cache timeout and verbose dumps, history-store cursor-cache miss stats, clean/dirty/update threshold flag combinations, in-memory mode flag remapping, scrub/nokeep selection, no-worker server eviction, worker auto-tuning up/down/stable/retune behavior, and progress-based aggressive score escalation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_verbose.c -->
## sources/storage-engines/wiredtiger/src/evict/evict_verbose.c

Purpose: emits human-readable cache diagnostics for eviction troubleshooting. It prints per-btree internal/leaf page counts and byte totals, then compares walked totals with tracked connection cache counters.

Important functions: `__wt_verbose_dump_cache` is the exported entry point. It prints cache-full, clean/dirty/update threshold checks, walks all eligible open btree handles under the handle-list read lock, applies cache overhead to walked bytes, and prints totals versus tracked `bytes_inmem`, dirty bytes, and update bytes. `__verbose_dump_cache_apply` iterates open handles, skipping non-btree, closed, discarded, or outdated handles. `__verbose_dump_cache_single` prints one dhandle's live/checkpoint name, eviction-disabled state, and per-page statistics gathered by a no-wait cache tree walk.

Control flow: invoked when eviction appears stuck or by diagnostic tooling. For each handle, it temporarily switches the session dhandle with `WT_WITH_DHANDLE` and walks cached pages using `WT_READ_CACHE | WT_READ_NO_EVICT | WT_READ_NO_WAIT | WT_READ_VISIBLE_ALL`. Handles opened exclusively are reported and skipped to avoid unsafe tree walking.

State and persistence behavior: this file is read-only except for message output. It observes page memory footprints, dirty state, update bytes via `__evict_page_updates_candidate`, dhandle flags, and tracked cache counters. It does not persist data or alter eviction queues.

Dependencies and integration points: depends on eviction threshold helpers from `evict_inline.h`, handle-list locking, tree walking, page dirty/update accounting, dhandle iteration macros, and WiredTiger message/verbose infrastructure. It is called from stuck-cache handling in `evict_thread.c`.

Risks and test signals: diagnostic code must not crash while the system is already unhealthy. Tests should cover exclusive handles, checkpoint handles, discarded/outdated handles, trees with no internal or no leaf pages, dirty/update byte accounting, tracked-versus-walked totals, no-wait skipped pages, and invocation while eviction threads and schema operations are active.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/evict/evict_verbose.c -->
