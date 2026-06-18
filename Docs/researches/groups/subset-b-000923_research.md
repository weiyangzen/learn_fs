# Research: subset-b-000923

This grouped report covers the source files assigned to `subset-b-000923`. Each section is source-tree aligned and uses the required split markers for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bfq-iosched.h -->
# sources/distributed-fs/ceph-client/block/bfq-iosched.h

## Purpose

`bfq-iosched.h` is the private interface and state model for the BFQ block I/O scheduler. It defines BFQ's hierarchical B-WF2Q+ entities, per-process queues, per-device scheduler state, cgroup group state, accounting structures, state flags, and cross-file function prototypes used by the BFQ dispatch, merge, cgroup, and fair-queueing implementation files. It is not a passive declaration file: the comments encode important scheduling invariants around virtual time, weight raising, idle trees, cgroup hierarchy traversal, and queue lifetime.

## Important APIs, Types, And Functions

Core constants include `BFQ_IOPRIO_CLASSES`, `BFQ_MIN_WEIGHT`, `BFQ_MAX_WEIGHT`, `BFQ_WEIGHT_CONVERSION_COEFF`, `BFQ_SOFTRT_WEIGHT_FACTOR`, and `BFQ_MAX_ACTUATORS`. These constants shape priority-class scheduling, user-visible weight conversion, soft-real-time boosting, and multi-actuator queue arrays.

The main scheduler types are:

- `struct bfq_service_tree`: active and idle rbtrees for one I/O priority class, plus `first_idle`, `last_idle`, virtual time `vtime`, and aggregate weight `wsum`.
- `struct bfq_sched_data`: one scheduler level containing `in_service_entity`, cached `next_in_service`, three service trees, and idle-class service timestamp.
- `struct bfq_entity`: the schedulable unit used for both leaf `bfq_queue` objects and non-leaf `bfq_group` objects. It stores rb-node membership, B-WF2Q+ `start` and `finish`, active-tree `min_start`, budget, service consumed, effective and pending weights, parent pointers, and optional group pending-request membership.
- `struct bfq_queue`: the per-process/per-actuator leaf queue. It combines scheduler entity state with request trees/lists, FIFO expiration state, service budgets, dispatch counts, idle/think-time heuristics, weight-raising state, cooperative merge state, waker tracking, and actuator index.
- `struct bfq_io_cq`: the per `(request_queue, io_context)` mapping from a task to async/sync queues per actuator, plus persistent queue data used across merges and splits.
- `struct bfq_data`: the per-device scheduler state, including the root group, dispatch list, queue weight tree, busy counts, in-service queue, dispatch and completion timing, peak-rate estimation, idling parameters, low-latency and weight-raising tunables, queue allocation fallback, cgroup integration, and multi-actuator ranges.
- `struct bfq_group` and `struct bfq_group_data`: per blkcg/device and per blkcg BFQ group state when `CONFIG_BFQ_GROUP_IOSCHED` is enabled.
- `struct bfqg_stats`, `struct bfq_stat`: blkcg-facing BFQ statistics, including optional debug counters.

The header declares the internal B-WF2Q+ API implemented by `bfq-wf2q.c`, including `bfq_entity_to_bfqq()`, `bfq_entity_service_tree()`, `bfq_ioprio_to_weight()`, `__bfq_entity_update_weight_prio()`, `bfq_bfqq_served()`, `bfq_bfqq_charge_time()`, `bfq_get_next_queue()`, `bfq_activate_bfqq()`, `bfq_deactivate_bfqq()`, `bfq_requeue_bfqq()`, `bfq_add_bfqq_busy()`, and `bfq_del_bfqq_busy()`. It also declares main BFQ scheduler integration points such as `bfq_bfqq_expire()`, `bfq_schedule_dispatch()`, `bfq_weights_tree_add/remove()`, and cgroup helpers such as `bfq_bic_update_cgroup()`, `bfq_bio_bfqg()`, and `bfqg_to_blkg()`.

## Control Flow And State Behavior

The header models BFQ as a hierarchy of `bfq_entity` objects. Leaf queues represent process I/O; group entities represent blkcg groups. Each entity is attached to its parent's `bfq_sched_data`, and non-leaf entities own their own child `sched_data`. Scheduling walks are abstracted by `for_each_entity()` and `for_each_entity_safe()`, which either traverse the cgroup hierarchy or collapse to a single level when group scheduling is disabled.

Per-class service trees maintain active and idle entities separately. Active trees are ordered by virtual finish time and carry `min_start` for efficient eligibility lookup. Idle trees retain entities whose finish timestamps are still beyond virtual time so that short-idle queues can preserve service guarantees. `bfq_sched_data->next_in_service` is a cached scheduling decision whose definition is deliberately restrictive so upper levels can be updated cheaply when a child changes.

`bfq_queue` state persists across request arrivals and completions. It tracks request rbtrees/FIFO lists, budget use, dispatched requests, request position, think-time, burst membership, soft-real-time classification, weight raising, cooperative merging, waker relationships, and actuator placement. `bfq_iocq_bfqq_data` captures queue state before cooperative merges so split/recycle paths can restore classification, weights, weight raising, injection limits, and timing data.

## Dependencies And Integration Points

This header depends on Linux block, blktrace, hrtimer, cgroup, blkcg rwstat, rbtrees, lists, hlist, and request/bio types. It is consumed by BFQ implementation files and integrates with blk-cgroup through `struct blkg_policy_data`, `struct blkcg_policy`, cgroup stats helpers, and cgroup trace messages. It also integrates with blk-mq request dispatch, IO priority classes, direct block tracing, and multi-actuator disk descriptions.

The logging macros use either `blk_add_cgroup_trace_msg()` or `blk_add_trace_msg()` depending on group-scheduler support. That means queue naming and cgroup association are part of the observability contract, not just debug code.

## Risks And Edge Cases

The highest-risk areas are lifetime and cached state consistency. Queue objects can be active, idle, in service, merged, split, or shared, and fields like `on_st_or_in_serv`, `ref`, `stable_ref`, and saved merge state must remain coherent. Weight changes are lazy through `new_weight`, `new_ioprio_class`, and `prio_changed`; applying them while an entity is already on a tree can corrupt fairness unless callers use the correct update path. Multi-actuator arrays are bounded by `BFQ_MAX_ACTUATORS`; any detected hardware range count above that limit must be handled elsewhere before indexing these arrays.

Cgroup-enabled and cgroup-disabled builds have different structure layouts and traversal semantics, so changes must compile under both configurations. The comments around `num_groups_with_pending_reqs` explicitly describe an accuracy/simplicity tradeoff; code consuming it must not treat it as an exact count.

## Test Signals

Useful validation includes BFQ builds with and without `CONFIG_BFQ_GROUP_IOSCHED` and `CONFIG_BFQ_CGROUP_DEBUG`, lockdep under request arrival/completion and cgroup migration, blktrace output for per-queue names, stress tests with many blkcg groups, soft-real-time and interactive workloads, cooperative merge/split workloads, and multi-actuator tests checking per-actuator queue lists and request injection. Fairness tests should verify weight ratios, idle-class service timeout behavior, and no stale `next_in_service` after activation, requeue, deactivation, and expiration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bfq-iosched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bfq-wf2q.c -->
# sources/distributed-fs/ceph-client/block/bfq-wf2q.c

## Purpose

`bfq-wf2q.c` implements BFQ's hierarchical Budget Worst-case Fair Weighted Fair Queueing scheduler. It manages virtual timestamps, active and idle service trees, entity activation/requeue/deactivation, group hierarchy propagation, queue selection, service accounting, and busy queue insertion/removal. The file is the core scheduling engine behind BFQ's fairness and latency behavior.

## Important APIs, Types, And Functions

Important exported/internal functions include `bfq_entity_to_bfqq()`, `bfq_tot_busy_queues()`, `bfq_entity_of()`, `bfq_entity_service_tree()`, `bfq_ioprio_to_weight()`, `__bfq_entity_update_weight_prio()`, `bfq_bfqq_served()`, `bfq_bfqq_charge_time()`, `__bfq_deactivate_entity()`, `next_queue_may_preempt()`, `bfq_get_next_queue()`, `__bfq_bfqd_reset_in_service()`, `bfq_activate_bfqq()`, `bfq_deactivate_bfqq()`, `bfq_requeue_bfqq()`, `bfq_add_bfqq_busy()`, and `bfq_del_bfqq_busy()`.

Key static helpers include `bfq_gt()` for wrap-safe timestamp comparison, `bfq_class_idx()` for selecting the service tree, `bfq_update_next_in_service()` and `bfq_lookup_next_entity()` for cached next-service decisions, `bfq_delta()` and `bfq_calc_finish()` for virtual-time arithmetic, `bfq_insert()`, `bfq_active_insert()`, `bfq_active_extract()`, `bfq_idle_insert()`, and `bfq_idle_extract()` for rbtrees, and `bfq_first_active_entity()` for eligible-min-finish lookup using `min_start`.

Group-specific helpers behind `CONFIG_BFQ_GROUP_IOSCHED` update parent budgets and active entity counts, while no-op or simplified versions are compiled for non-hierarchical BFQ.

## Control Flow And State Behavior

Activation begins with `bfq_activate_bfqq()`, which calls `bfq_activate_requeue_entity()` on the queue's entity and, when needed, propagates the operation up the parent chain. True activation either extracts an entity from the idle tree or initializes its start time from service-tree virtual time, increments `wsum`, takes a service reference with `bfq_get_entity()`, computes a finish timestamp, and inserts it into the active tree. Requeueing updates start/finish based on already received service and repositions an entity in the active tree.

Selection starts at `bfq_get_next_queue()`. It walks from the root group's `sched_data` down to a leaf, setting `in_service_entity` at every level from cached `next_in_service`. Entities that are no longer next-service candidates are extracted from active trees. After a leaf queue is selected, the function walks back up and refreshes `next_in_service` values.

Deactivation starts with `bfq_deactivate_bfqq()` and `bfq_deactivate_entity()`. It calculates final finish time, clears `in_service_entity` if needed, extracts the entity from active or idle trees, optionally retains it in the idle tree, or forgets it and drops service references. Deactivation propagates upward until a parent remains active, then requeues/repositions the remaining ancestors if their child scheduling state changed.

Service accounting happens through `bfq_bfqq_served()` and `bfq_bfqq_charge_time()`. Actual sectors advance queue and ancestor `service`, service-tree `vtime`, weight-raising counters, and idle-tree expiration. Slow queues may be charged inflated service based on elapsed time and estimated budget to enforce time fairness when service-domain fairness would hurt throughput.

## Dependencies And Integration Points

This file depends on `bfq-iosched.h` structures and external BFQ helpers for queue lifetime, weights-tree maintenance, cgroup stats, expiration, tracing, and group lookup. It uses Linux rbtrees for active/idle entity queues, lists for active and idle BFQ queues, hlist waker lists, jiffies for idle-class service throttling, and block trace logging through macros from the header.

The scheduler integrates with the rest of BFQ through busy queue transitions. `bfq_add_bfqq_busy()` marks a queue busy, activates it, updates per-priority busy counters, adds pending-request group accounting, adds non-weight-raised queues to the weight tree, and moves woken queues in their waker list. `bfq_del_bfqq_busy()` reverses those effects and may remove weights-tree and pending-group state when no requests are dispatched.

## Risks And Edge Cases

The rbtrees carry derived `min_start`, `first_idle`, `last_idle`, and `wsum` state. Any missed update can break eligibility lookup or fairness. Timestamp comparison uses signed subtraction through `bfq_gt()` to tolerate wraparound; replacing it with direct comparison would be wrong. The `next_in_service` cache is intentionally restrictive and can be stale in rare idle-class timing cases; the code relies on expiration and state changes to refresh it.

Reference handling is subtle. `bfq_get_entity()` increments leaf queue references when an entity enters service trees; `bfq_forget_entity()` and `__bfq_bfqd_reset_in_service()` decide when the service reference is dropped. `bfq_del_bfqq_busy()` explicitly warns that `bfq_weights_tree_remove()` may free the queue and must be last. Hierarchical builds add further risk because parent budgets, active entity counts, and pending-request group counters are approximations used by latency heuristics.

## Test Signals

Strong test signals include lockdep and KASAN under queue activation/deactivation storms, request expiration, cgroup creation/removal, and cooperative queue merging. Fairness tests should compare weights across ioprio classes and cgroup levels, exercise idle-class timeout service, and validate no starvation when idle trees retain backshifted entities. Stress tests should cover slow random queues, sequential queues, weight-raised soft-real-time queues, and multi-actuator active lists. Trace output from `bfq_log_bfqq()` should show coherent activation, finish timestamp, and busy removal transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bfq-wf2q.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bio-integrity-auto.c -->
# sources/distributed-fs/ceph-client/block/bio-integrity-auto.c

## Purpose

`bio-integrity-auto.c` provides automatic block-layer generation and verification of protection information for bios whose submitter did not attach integrity metadata. It lets PI-capable devices still get guard/reference/application tag handling for ordinary block users and defers expensive read verification out of interrupt context.

## Important APIs, Types, And Functions

The private `struct bio_integrity_data` embeds a `bio_integrity_payload`, one metadata `bio_vec`, the target `bio`, a saved data iterator, and a work item. `bid_slab` and `bid_pool` provide bounded allocation, while `kintegrityd_wq` runs deferred verification.

The main functions are `bio_integrity_prep()`, `__bio_integrity_endio()`, `blk_flush_integrity()`, and the init routine `blk_integrity_auto_init()`. Internal helpers include `bio_integrity_finish()`, `bio_integrity_verify_fn()`, and `bip_should_check()`.

## Control Flow And State Behavior

`bio_integrity_prep()` allocates `bio_integrity_data` from a mempool, attaches its embedded payload to the bio through `bio_integrity_init()`, marks the payload as `BIP_BLOCK_INTEGRITY`, allocates the metadata buffer with optional zeroing, and configures default guard/reference tag checks when requested. For writes with enabled checks, it immediately calls `bio_integrity_generate()` so metadata travels with the bio. For reads, it stores the original `bio->bi_iter` so completion-time verification can interpret data sectors correctly after the driver has advanced iterators.

`__bio_integrity_endio()` is called from the bio completion path. For successful reads with check flags, it queues `bio_integrity_verify_fn()` on `kintegrityd_wq` and returns false, telling `bio_endio()` that completion is postponed. The work item verifies metadata, stores the resulting blk status in `bio->bi_status`, frees the integrity payload/buffer/container, and then calls `bio_endio()` again. Non-read, failed, or no-check completions free the integrity state synchronously and allow normal completion to continue.

## Dependencies And Integration Points

The file depends on block integrity helpers from `linux/blk-integrity.h`, T10 PI helpers, workqueues, and common block internals in `blk.h`. It is integrated by the generic `bio_integrity_endio()` path and the submit-time integrity preparation path. The workqueue is `WQ_MEM_RECLAIM`, high priority, CPU intensive, per-CPU, and concurrency-limited, reflecting the need to make progress during reclaim while avoiding unbounded verification parallelism.

## Risks And Edge Cases

Read verification must not run in interrupt context because checksum/tag verification can be CPU-heavy. The saved iterator is therefore critical; if it is missing or stale, verification can check the wrong sectors. The code temporarily owns `bio->bi_integrity` and clears `REQ_INTEGRITY` in `bio_integrity_finish()`, so double-free or mixed ownership with filesystem/user integrity paths would be dangerous. Since allocation uses a mempool, initialization failures are handled as boot-time panics rather than runtime fallback.

## Test Signals

Test with PI-capable devices or emulation, reads and writes without user-provided integrity, forced read verification failures, and I/O completion from interrupt context. Verify that successful read completion is delayed until workqueue verification finishes, write metadata is generated before submit, `blk_flush_integrity()` drains pending work, and failure statuses propagate through `bio->bi_status`. Memory-pressure tests should confirm mempool-backed forward progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bio-integrity-auto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bio-integrity-fs.c -->
# sources/distributed-fs/ceph-client/block/bio-integrity-fs.c

## Purpose

`bio-integrity-fs.c` provides filesystem-facing helpers for block integrity metadata. Unlike the automatic block-layer path, these helpers are intended for submitters that explicitly allocate/generate/verify metadata around bios and manage completion context themselves.

## Important APIs, Types, And Functions

The file defines `struct fs_bio_integrity_buf`, which embeds a `bio_integrity_payload` and a single `bio_vec`. Allocation is backed by `fs_bio_integrity_cache` and `fs_bio_integrity_pool`.

Public helpers are `fs_bio_integrity_alloc()`, `fs_bio_integrity_free()`, `fs_bio_integrity_generate()`, and `fs_bio_integrity_verify()`. Initialization is handled by `fs_bio_integrity_init()`.

## Control Flow And State Behavior

`fs_bio_integrity_alloc()` calls `bio_integrity_action()` to determine whether a bio needs metadata buffering, checking, and/or zeroing. If no action is required, it returns zero. Otherwise it allocates a small container from the mempool, attaches its embedded payload to the bio with one vector, allocates the metadata buffer via `bio_integrity_alloc_buf()`, and sets default integrity flags if checks are required. It returns the action mask to the caller.

`fs_bio_integrity_generate()` is a convenience wrapper: allocate integrity state if needed, then generate metadata for the current bio. `fs_bio_integrity_free()` releases the metadata buffer, returns the container to the mempool, clears `bio->bi_integrity`, and removes `REQ_INTEGRITY`.

`fs_bio_integrity_verify()` is used by the submitter after driver completion. It reinitializes `bip->bip_iter` from caller-supplied sector and size, computes the integrity byte count, calls `bio_integrity_verify()`, and converts the block status to errno.

## Dependencies And Integration Points

The file depends on `linux/blk-integrity.h`, `linux/bio-integrity.h`, and `blk.h`. It uses the common integrity allocation, default setup, generation, and verification helpers from `bio-integrity.c` and the underlying device's `blk_integrity` profile. It exports `fs_bio_integrity_generate()` for filesystem modules.

## Risks And Edge Cases

The API assumes the filesystem remembers the original sector and size for verification, because the driver may mutate the bio iterator. Using wrong values causes verification over the wrong metadata range. The helper allocates only one integrity vector and uses a mempool container; callers must not mix it with user-mapped or automatic integrity ownership. Freeing must happen exactly once after the submitter is done with verification/generation.

## Test Signals

Validation should include filesystem direct use on devices with and without integrity profiles, reads/writes that require metadata, no-action paths, verification after driver iterator advancement, and error injection for checksum/tag failures. KASAN or kmemleak should show the mempool container and metadata buffer are released by `fs_bio_integrity_free()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bio-integrity-fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bio-integrity.c -->
# sources/distributed-fs/ceph-client/block/bio-integrity.c

## Purpose

`bio-integrity.c` implements the generic bio integrity payload infrastructure. It decides what integrity action a bio needs, allocates/frees metadata payloads and buffers, maps user integrity iterators, clones and trims integrity metadata for bio transformations, advances integrity iterators with data progress, and initializes a fallback metadata buffer mempool.

## Important APIs, Types, And Functions

The file defines `struct bio_integrity_alloc`, a flexible allocation containing `struct bio_integrity_payload` and inline metadata vectors, plus a global `integrity_buf_pool`.

Important functions include `__bio_integrity_action()`, `bio_integrity_alloc_buf()`, `bio_integrity_free_buf()`, `bio_integrity_setup_default()`, `bio_integrity_free()`, `bio_integrity_init()`, `bio_integrity_alloc()`, `bio_integrity_map_user()`, `bio_integrity_map_iter()`, `bio_integrity_advance()`, `bio_integrity_trim()`, and `bio_integrity_clone()`. User mapping helpers include `bio_integrity_copy_user()`, `bio_integrity_init_user()`, `bvec_from_pages()`, `bio_integrity_unmap_user()`, and `bio_integrity_uncopy_user()`.

## Control Flow And State Behavior

`__bio_integrity_action()` inspects the device integrity profile and bio operation. Reads generally need buffering and checking unless verification is disabled and the device can offload metadata. Writes skip zero-sector flush-like writes, otherwise generate/check metadata unless generation is disabled; metadata larger than PI tuples can require zeroing to avoid leaking uninitialized kernel memory.

`bio_integrity_alloc()` allocates and attaches a payload unless the bio has an inline encryption context, which is rejected. `bio_integrity_init()` sets vector capacity, attaches the payload, and marks `REQ_INTEGRITY`. `bio_integrity_free()` clears the pointer and flag, while `bio_integrity_alloc_buf()` provides a single contiguous metadata buffer from `kmalloc` or the mempool fallback and records `BIP_MEMPOOL` ownership.

User integrity mapping starts in `bio_integrity_map_iter()`, which validates device integrity support, computes the metadata byte count corresponding to the current data bio, validates `uio_meta` flags, maps only the relevant prefix of the iterator, and advances both iterator and seed on success. `bio_integrity_map_user()` pins/extracts pages, converts adjacent pages into bvecs, detects PCI P2PDMA, checks segment limits and DMA alignment, then either attaches the user bvecs directly or copies through a bounce buffer. Read-copy mode preserves original bvecs after the bounce vector so completion can copy verified metadata back to userspace.

Iterator maintenance mirrors data bio changes. `bio_integrity_advance()` advances sector seed and bvec iterator by the metadata bytes corresponding to completed data bytes. `bio_integrity_trim()` recomputes integrity size for cloned/split bios. `bio_integrity_clone()` creates a payload that borrows the source payload's vector and clones only safe flags.

## Dependencies And Integration Points

This file depends on block integrity profiles, T10 PI definitions, bvec helpers, iov_iter page extraction, PCI P2PDMA checks, queue integrity segment limits, and bio crypto state. It is used by automatic integrity, filesystem integrity, user metadata paths, bio split/clone/advance logic in `bio.c`, and lower-level integrity generation/verification helpers.

## Risks And Edge Cases

Ownership is the primary risk. Direct user mapping pins pages that must be unpinned by `bio_integrity_unmap_user()`. Copy mode unpins original write pages immediately after copying, but read mode stores original bvecs and copies back on unmap. Bounce buffers allocated by `kmalloc` are freed with `kfree(bvec_virt())`, while mempool pages use `BIP_MEMPOOL`. Cloned integrity payloads borrow source vectors and must not outlive the source vector storage.

The code rejects crypto + integrity combinations in this path. Segment merging respects queue limits, SG gap restrictions, zone-device page compatibility, and P2PDMA no-merge marking. Partial page extraction must unpin already pinned pages before failing. Metadata length is tied to data sectors; any mismatch between data bio size and metadata iterator count returns `-EINVAL`.

## Test Signals

Test reads/writes with T10 PI profiles, `NOVERIFY`, `NOGENERATE`, metadata larger than tuple size, offload-capable profiles, and zero-sector writes. Exercise user metadata mapping with aligned/direct vectors, misaligned bounce-copy paths, too many vectors, too-large metadata, partial pin failures, P2PDMA pages, queue segment limits, clone/split/trim/advance flows, and read copy-back. KASAN, kmemleak, and page refcount checks are useful for mapping and unmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bio-integrity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bio.c -->
# sources/distributed-fs/ceph-client/block/bio.c

## Purpose

`bio.c` implements core Linux bio allocation, initialization, lifetime, vector management, cloning, splitting, iterator/page mapping, bounce-buffer support, synchronous wait helpers, dirty-page completion handling, and bio end I/O completion. It is the central utility layer for block I/O descriptors.

## Important APIs, Types, And Functions

Important allocation structures include `struct bio_alloc_cache`, global `bvec_slabs`, `struct bio_set fs_bio_set`, and the shared `bio_slabs` xarray protected by `bio_slab_lock`.

Major exported APIs include `bio_init()`, `bio_reset()`, `bio_reuse()`, `bio_chain()`, `bio_chain_and_submit()`, `blk_next_bio()`, `bio_alloc_bioset()`, `bio_kmalloc()`, `bio_put()`, `bio_alloc_clone()`, `bio_init_clone()`, `bio_add_page()`, `__bio_add_page()`, `bio_add_folio()`, `bio_add_vmalloc()`, `bio_iov_iter_get_pages()`, `bio_iov_iter_bounce()`, `bio_iov_iter_unbounce()`, `bio_await()`, `submit_bio_wait()`, `bio_submit_or_kill()`, `bdev_rw_virt()`, `__bio_advance()`, `bio_copy_data()`, `bio_free_pages()`, `bio_set_pages_dirty()`, `bio_check_pages_dirty()`, `bio_endio()`, `bio_split()`, `bio_trim()`, `biovec_init_pool()`, `bioset_init()`, and `bioset_exit()`.

## Control Flow And State Behavior

Bio allocation is bioset-backed. `bio_alloc_bioset()` first tries restricted slab allocation and optional per-CPU cache for small inline-vector bios, then falls back to mempool allocation if blocking allocation is allowed. To avoid deadlock under recursive `submit_bio_noacct()` paths, `punt_bios_to_rescuer()` moves already queued bios from the current task's bio lists to the bioset rescuer workqueue before blocking on the mempool. `bio_put()` returns eligible bios to per-CPU caches or fully frees them through `bio_free()`.

Initialization resets visible bio fields, cgroup association, integrity pointer, crypto context, counters, and vector ownership. `bio_uninit()` releases blkcg references, integrity payloads, and crypto contexts. `bio_reset()` preserves the vector table while clearing state; `bio_reuse()` preserves payload/endio/private fields but forbids cloned, integrity, and crypto bios.

Vector management supports pages, folios, vmalloc memory, direct kernel mappings, and iov_iter extraction. Add paths merge adjacent physical pages when legal, set `REQ_NOMERGE` for P2PDMA pages, enforce `BIO_MAX_SIZE`, and reject cloned bio mutation. Direct-I/O mapping pins user pages or borrows bvec iterators. Bounce helpers allocate folios, copy write data into bounce buffers, or store original read buffers behind the bounce vector for later copy-back.

Completion flows through `bio_endio()`. It waits for chained children, lets integrity completion postpone final completion, runs zone and rq-qos completion hooks, emits trace events, resolves chained bios without unbounded recursion, drops blkcg references for callers that forgot `bio_uninit()`, and finally invokes `bi_end_io`. Dirty-page direct-I/O reads either release pages immediately or queue a work item to redirty pages in process context before unpinning and putting the bio.

Split and trim operations create cloned bios sharing vector storage, adjust iterators, advance the original bio, propagate trace-completion flags, and trim integrity metadata when present. They reject invalid sector counts, zone append splits, and atomic write splits.

## Dependencies And Integration Points

This file integrates with memory management, folios, page pinning, vmalloc cache maintenance, mempools, workqueues, cgroups, blk-crypto, bio integrity, rq-qos, block tracing, zone handling, blk-mq submit paths, and cgroup accounting via `bio_associate_blkg()`. It creates `fs_bio_set` at subsystem init and initializes biovec slabs and CPU hotplug cleanup.

## Risks And Edge Cases

Deadlock avoidance is a major theme. Mempool guarantees only hold if callers avoid allocating multiple unsubmitted bios from the same pool; the rescuer workqueue mitigates recursive submit paths but not arbitrary external mempools. Per-CPU allocation caches must be pruned on CPU teardown and cannot grow beyond `ALLOC_CACHE_MAX`.

Vector ownership is also subtle. Clones borrow the source vector table. Bvec iterators borrowed from iov_iter require caller lifetime guarantees. Pinned user pages must be released and sometimes marked dirty outside interrupt context. Bounce read bios store the bounce buffer at index zero and original user bvecs after it, so users must pair with `bio_iov_iter_unbounce()`.

Completion can be re-entered through integrity work and chained bios. Callers that override `bi_private` or `bi_end_io` must respect helpers such as `bio_await()` and `bio_chain()`. Splitting cannot be used for zone append or atomic writes. End-of-device truncation zeroes only read buffers beyond the valid range and leaves true out-of-range I/O to fail normally.

## Test Signals

Validation should include allocation under memory pressure, recursive stacking-driver submissions, bioset rescuer activity, CPU hotplug cache pruning, clone/split/trim lifetimes, direct I/O page pin/unpin and dirty-page deferral, vmalloc read/write cache maintenance, P2PDMA no-merge behavior, integrity and crypto cleanup, chained completion ordering, synchronous wait helpers, and lockdep around endio and workqueue paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/bio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup-fc-appid.c -->
# sources/distributed-fs/ceph-client/block/blk-cgroup-fc-appid.c

## Purpose

`blk-cgroup-fc-appid.c` stores and retrieves Fibre Channel application identifiers on block cgroups. It lets external FC/app-ID plumbing associate a string with an I/O cgroup and lets bio submission paths retrieve the identifier through the bio's `blkcg_gq`.

## Important APIs, Types, And Functions

The file exports `blkcg_set_fc_appid()` and `blkcg_get_fc_appid()`. `blkcg_set_fc_appid()` takes an application ID string, a cgroup ID, and a length. `blkcg_get_fc_appid()` takes a bio and returns the associated blkcg string or `NULL`.

## Control Flow And State Behavior

`blkcg_set_fc_appid()` validates the length against `FC_APPID_LEN`, looks up the cgroup by ID with `cgroup_get_from_id()`, gets the I/O controller CSS with `cgroup_get_e_css()`, converts it to `struct blkcg`, and copies the app ID into `blkcg->fc_app_id` with `strscpy()`. It drops both CSS and cgroup references before returning. The comment explicitly accepts a small race: I/O may miss the just-updated ID, but avoiding a lock is considered preferable.

`blkcg_get_fc_appid()` checks that the bio is associated with a `bi_blkg` and that the first byte of the blkcg app ID is nonzero. It returns a direct pointer to the stored blkcg buffer, not a copy.

## Dependencies And Integration Points

The file depends on `blk-cgroup.h`, the I/O cgroup subsystem `io_cgrp_subsys`, and the optional `CONFIG_BLK_CGROUP_FC_APPID` field in `struct blkcg`. It is intended for FC transport/app-identification consumers that inspect bios after blkcg association has happened.

## Risks And Edge Cases

The setter is intentionally lockless with respect to readers, so readers can see an old, new, or transient value during updates. The direct pointer returned by `blkcg_get_fc_appid()` is valid only while the underlying blkcg remains alive through the bio's blkg association. Length validation uses the caller-provided length; callers must pass a sensible length for `strscpy()` semantics and ensure the source buffer is valid.

## Test Signals

Test valid and too-long app IDs, missing cgroup IDs, cgroups without I/O CSS, bios with no `bi_blkg`, bios whose blkcg has an empty app ID, and concurrent setter/getter activity. Module users should verify FC-side consumers tolerate `NULL` when I/O races with app-ID installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup-fc-appid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup-rwstat.c -->
# sources/distributed-fs/ceph-client/block/blk-cgroup-rwstat.c

## Purpose

`blk-cgroup-rwstat.c` implements legacy blkcg read/write stat helpers enabled by `CONFIG_BLK_CGROUP_RWSTAT`. The file backs older policy statistics with per-CPU counters plus auxiliary dead-child counters and provides printing and recursive summing helpers.

## Important APIs, Types, And Functions

The exported functions are `blkg_rwstat_init()`, `blkg_rwstat_exit()`, `__blkg_prfill_rwstat()`, `blkg_prfill_rwstat()`, and `blkg_rwstat_recursive_sum()`. These operate on the `struct blkg_rwstat` and `struct blkg_rwstat_sample` types declared in the header.

## Control Flow And State Behavior

Initialization creates `BLKG_RWSTAT_NR` per-CPU counters with `percpu_counter_init_many()` and zeros all auxiliary counters. Exit destroys the per-CPU counters. Printing reads a sample and emits per-device lines for `Read`, `Write`, `Sync`, `Async`, `Discard`, and `Total`, using `blkg_dev_name()` to resolve the device name from policy data.

Recursive summing requires the queue lock. It zeroes the output sample, takes an RCU read lock, walks the target blkg and descendants with `blkg_for_each_descendant_pre()`, skips offline blkgs, locates the rwstat either in policy data or directly in the blkg depending on whether `pol` is supplied, and sums counters including aux counts.

## Dependencies And Integration Points

The file depends on `blk-cgroup-rwstat.h` and through it on blkcg descendant traversal, policy data lookup, `percpu_counter`, `atomic64_t`, and `seq_file`. It is explicitly marked legacy and "Do not use in new code"; newer blkcg I/O stats are handled by the rstat path in `blk-cgroup.c`.

## Risks And Edge Cases

Recursive sums rely on queue-lock protection for online tests and RCU for cgroup traversal. Calling without the lock can race with blkg destruction or online/offline changes. Aux counters exist to carry stats from dead children into recursive views; local-only reads intentionally exclude aux counts. Printing silently skips devices without names.

## Test Signals

Test counter init/exit under allocation failure, add/read/reset behavior from the header helpers, printing format for all stat types, recursive sums with online descendants, offline descendants, dead-child aux propagation, and lockdep assertions for callers missing the queue lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup-rwstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup-rwstat.h -->
# sources/distributed-fs/ceph-client/block/blk-cgroup-rwstat.h

## Purpose

`blk-cgroup-rwstat.h` declares and partially implements legacy blkcg read/write statistics. It provides stat categories, storage types, and inline add/read/reset/total/aux helpers used by older blkcg policies such as BFQ debug/accounting paths.

## Important APIs, Types, And Functions

`enum blkg_rwstat_type` defines `READ`, `WRITE`, `SYNC`, `ASYNC`, `DISCARD`, `NR`, and `TOTAL`. `struct blkg_rwstat` contains per-CPU counters and auxiliary atomic counters per category. `struct blkg_rwstat_sample` is a plain snapshot array.

Inline helpers include `blkg_rwstat_read_counter()`, `blkg_rwstat_add()`, `blkg_rwstat_read()`, `blkg_rwstat_total()`, `blkg_rwstat_reset()`, and `blkg_rwstat_add_aux()`. Out-of-line declarations cover init/exit, printing, and recursive sum.

## Control Flow And State Behavior

`blkg_rwstat_add()` maps a block operation to direction counters: discard, write, or read, and separately sync or async. It uses `percpu_counter_add_batch()` with the large `BLKG_STAT_CPU_BATCH`, reflecting that per-CPU drift is acceptable for these legacy stats. `blkg_rwstat_read()` samples only local per-CPU counters. `blkg_rwstat_read_counter()` and recursive users include aux counts for dead child propagation.

`blkg_rwstat_reset()` zeroes both per-CPU and aux counters. `blkg_rwstat_add_aux()` snapshots another rwstat's per-CPU counters, adds its aux counters, and accumulates the result into the destination aux counters, preserving recursive accounting after child removal.

## Dependencies And Integration Points

The header depends on `blk-cgroup.h` for `BLKG_STAT_CPU_BATCH`, policy data, request operation helpers, and blkcg traversal declarations. It is included by BFQ scheduler headers and legacy rwstat implementation code.

## Risks And Edge Cases

The helpers are legacy and explicitly discouraged for new code. `blkg_rwstat_total()` returns read plus write but not discard, while printing total in the `.c` file includes discard; consumers must understand which total they need. Add operations require caller synchronization according to comments. Per-CPU counter drift is accepted, so these counters are not suitable for exact instantaneous accounting.

## Test Signals

Test operation classification for read/write/discard and sync/async combinations, total semantics, reset clearing both local and aux counters, aux propagation from dead children, and consistency of printed totals versus inline totals. Build coverage should include configurations that enable BFQ cgroup debug or other legacy rwstat users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup-rwstat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup.c -->
# sources/distributed-fs/ceph-client/block/blk-cgroup.c

## Purpose

`blk-cgroup.c` implements the common block I/O cgroup controller. It owns blkcg CSS allocation/free, per-queue/per-cgroup `blkcg_gq` association lifetime, policy registration and activation, cgroup I/O statistics, bio-to-cgroup association, optional punted bio submission for shared kthreads, cgroup writeback lifetime coordination, and delay-based throttling before return to userspace.

## Important APIs, Types, And Functions

Global state includes `blkcg_root`, `blkcg_root_css`, `blkcg_policy[]`, `all_blkcgs`, `blkcg_debug_stats`, and `blkg_stat_lock`. Important lifecycle functions are `blkg_alloc()`, `blkg_create()`, `blkg_lookup_create()`, `blkg_destroy()`, `blkg_destroy_all()`, `blkg_release()`, `__blkg_release()`, and `blkg_free_workfn()`.

Public APIs include `bio_blkcg_css()`, `blkcg_print_blkgs()`, `__blkg_prfill_u64()`, `blkg_conf_init()`, `blkg_conf_open_bdev()`, `blkg_conf_open_bdev_frozen()`, `blkg_conf_prep()`, `blkg_conf_exit()`, `blkg_conf_exit_frozen()`, `blkcg_pin_online()`, `blkcg_unpin_online()`, `blkg_init_queue()`, `blkcg_init_disk()`, `blkcg_exit_disk()`, `blkcg_activate_policy()`, `blkcg_deactivate_policy()`, `blkcg_policy_register()`, `blkcg_policy_unregister()`, `blkcg_maybe_throttle_current()`, `blkcg_schedule_throttle()`, `blkcg_add_delay()`, `bio_associate_blkg_from_css()`, `bio_associate_blkg()`, `bio_clone_blkg_association()`, `blk_cgroup_bio_start()`, and `blk_cgroup_congested()`.

The cgroup subsystem is registered as `io_cgrp_subsys` with CSS alloc/online/offline/free, rstat flush, cgroup files, legacy name `blkio`, task exit cleanup, and optional memcg dependency.

## Control Flow And State Behavior

Each `blkcg_gq` associates one blkcg with one request queue. Creation allocates the base object, percpu reference, percpu iostat sets, request-queue reference, optional async bio state, and per-policy data for policies already active on the queue. `blkg_create()` links parent blkgs, runs policy init/online callbacks, inserts into the blkcg radix tree and hlist, links into the queue blkg list, and marks it online. Lookups use `blkg_hint` and the radix tree; creation walks from root toward the target cgroup so parents exist before children.

Destruction offlines policy data, removes radix/hlist entries, clears lookup hints, and kills the percpu ref. RCU release flushes pending percpu stat lists, drops the held CSS reference, and schedules sleepable free work. The free worker frees policy data under `q->blkcg_mutex`, removes the queue list node, drops parent and queue refs, destroys percpu storage, exits the ref, and frees the object.

Stats are updated in `blk_cgroup_bio_start()`. Non-root default-hierarchy bios add bytes once per split chain through `BIO_CGROUP_ACCT`, increment I/O counts, queue the per-CPU iostat set on the blkcg percpu lockless list, and notify cgroup rstat. Flush drains only queued iostat sets, propagates deltas into global blkg stats and then upward to parent blkgs. Root stats are synthesized from disk-wide stats to avoid duplicate accounting overhead.

Policy registration assigns a `plid`, installs cgroup policy data across all blkgs if needed, and adds cgroup files. Per-disk activation freezes blk-mq queues, allocates missing per-blkg policy data in parent-first order, runs policy online callbacks, and sets the policy bit in `q->blkcg_pols`. Deactivation clears the bit and frees per-blkg policy data under queue and blkcg locks.

Bio association chooses the current task or kthread blkcg CSS, creates or finds the closest live blkg for the bio's disk, takes a blkg reference, and stores it in `bio->bi_blkg`. Existing associations are released before reassociation; clone association preserves source CSS. Passthrough bios skip association.

Delay throttling accumulates nanosecond delay in blkgs and schedules current tasks to check on resume. `blkcg_maybe_throttle_current()` looks up the current task's saved disk and blkcg, walks ancestors for the largest delay, clamps normal delays to 250 ms, optionally marks PSI memstall, and sleeps killably until the absolute timeout.

## Dependencies And Integration Points

The file depends on cgroup core, block devices, request queues, blk-mq queue freezing, backing-dev names, writeback, blk-throttle, blk-ioprio, PSI, task resume notifications, radix trees, RCU, percpu refs, lockless lists, seq_file, and disk stats. It is used by `bio.c` for initial bio association and completion cleanup, by policy modules for registration/activation/config parsing, by BFQ and throttling policies for per-blkg state, and by cgroupfs for `io.stat` and legacy `blkio.reset_stats`.

## Risks And Edge Cases

Lock ordering is critical: queue lock nests outside blkcg lock in most paths, but `blkcg_destroy_blkgs()` performs careful reverse lock dancing with trylock and reschedule points. Policy register/unregister uses two mutexes with documented nesting. Queue rebinds wait for old asynchronous root blkg cleanup before installing a new root blkg; otherwise radix-tree key collisions can occur.

Stat flushing races with blkg release and concurrent update, so `blkg_stat_lock`, `lqueued`, memory barriers, u64 stats seqcounts, RCU, and cgroup rstat ordering all matter. Bio association can fall back to the closest live ancestor if the target cgroup is dying. Delay accounting has two modes: positive `use_delay` is scaled/decayed and clamped, while negative `use_delay` from `blkcg_set_delay()` disables scaling; mixing modes is forbidden by header comments.

## Test Signals

Test cgroup create/destroy while I/O is running, queue add/remove/rebind, policy register/activate/deactivate/unregister under memory pressure, io.stat correctness for root and non-root cgroups, split bio accounting, cgroup writeback delayed destruction, bio clone/reassociation, passthrough bios, delay throttling and PSI memstall accounting, and lockdep for queue/blkcg/policy mutex ordering. Fault injection should cover allocation failures in blkg and policy data creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup.h -->
# sources/distributed-fs/ceph-client/block/blk-cgroup.h

## Purpose

`blk-cgroup.h` is the private block cgroup header for the block layer. It defines the core blkcg and blkg data structures, policy interfaces, lookup/reference helpers, descendant traversal macros, delay helpers, mergeability checks, configuration parser context, and no-op stubs for builds without `CONFIG_BLK_CGROUP`.

## Important APIs, Types, And Functions

Important types include `struct blkg_iostat`, `struct blkg_iostat_set`, `struct blkcg_gq`, `struct blkcg`, `struct blkg_policy_data`, `struct blkcg_policy_data`, `struct blkcg_policy`, and `struct blkg_conf_ctx`. `enum blkg_iostat_type` defines read/write/discard categories used by the rstat path.

The header declares queue/disk lifecycle APIs, policy registration and activation APIs, cgroup printing/config helpers, and `blk_cgroup_bio_start()` plus `blkcg_add_delay()`. Inline helpers include `css_to_blkcg()`, `bio_issue_as_root_blkg()`, `blkg_lookup()`, `blkg_to_pd()`, `blkcg_to_cpd()`, `pd_to_blkg()`, `cpd_to_blkcg()`, `blkg_get()`, `blkg_tryget()`, `blkg_put()`, `blkcg_use_delay()`, `blkcg_unuse_delay()`, `blkcg_set_delay()`, `blkcg_clear_delay()`, `blk_cgroup_mergeable()`, and `blkcg_policy_enabled()`.

## Control Flow And State Behavior

`struct blkcg_gq` is the per `(blkcg, request_queue)` object. It stores queue and blkcg links, parent blkg, percpu refcount, online state, percpu/global iostat sets, per-policy data slots, optional async bio punt state, delay accounting fields, and RCU release state. `struct blkcg` owns the CSS, blkcg lock, online pin, congestion count, radix tree and hint for queue lookup, hlist of blkgs, per-policy cgroup data, all-blkcgs list node, percpu stat-update lockless list heads, optional FC app ID, and optional cgroup writeback list.

Policy data is split between per-blkg `blkg_policy_data` and per-blkcg `blkcg_policy_data`. `struct blkcg_policy` supplies callback pointers for allocation, init, online/offline, free, stats reset, and stat printing. This callback model lets policies such as BFQ, throttling, and ioprio attach their own state while sharing blkg lifetime and cgroupfs plumbing.

`blkg_lookup()` prefers `q->root_blkg` for root, then the `blkg_hint`, then the blkcg radix tree keyed by queue ID. Reference helpers wrap the percpu ref and distinguish ordinary get from RCU-safe tryget. Descendant macros walk CSS descendants and map each CSS to its blkg for the same queue.

Delay helpers manage the cgroup congestion count and per-blkg delay fields. `blkcg_use_delay()` increments a positive user count and increments blkcg congestion on the first user. `blkcg_unuse_delay()` uses compare/exchange to avoid racing below zero. `blkcg_set_delay()` uses negative `use_delay` as an exclusive fixed-delay mode, and `blkcg_clear_delay()` clears it.

## Dependencies And Integration Points

The header depends on Linux blk-cgroup, cgroup, kthread, blk-mq, llist, and internal `blk.h`. It is included by core blkcg code, BFQ, legacy rwstat helpers, FC app ID support, and bio code. `blk_cgroup_mergeable()` integrates blkcg ownership with request merge decisions and keeps metadata/swap root-issued bios from merging with regular cgroup-issued I/O.

## Risks And Edge Cases

Most helpers require specific synchronization. `blkg_lookup()` must be under RCU or queue lock. Descendant traversal requires RCU and stronger locks for exact online sets. `blkg_tryget()` can fail during teardown and callers must fall back safely. `bio_issue_as_root_blkg()` is a policy decision that affects throttling and mergeability; incorrect flags can cause priority inversion or inappropriate throttling.

The `CONFIG_BLK_CGROUP` stubs must keep non-cgroup builds compiling and semantically permissive. Changes to structure layout or helper semantics must be audited with both cgroup-enabled and disabled builds.

## Test Signals

Build with `CONFIG_BLK_CGROUP` enabled and disabled. Exercise blkg lookup under RCU, dying cgroups, queue teardown, policy data access, mergeability across same/different blkgs and metadata/swap flags, delay enable/disable races, and descendant traversal with online/offline children. Static analysis and lockdep should verify lookup and traversal lock assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-cgroup.h -->
