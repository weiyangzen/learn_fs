# Research: subset-b-000925

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-iolatency.c -->
# sources/distributed-fs/ceph-client/block/blk-iolatency.c

## Purpose
`blk-iolatency.c` implements the cgroup block I/O latency controller as an `rq_qos` policy. It protects configured cgroups by tracking bio latency over rolling windows and throttling peer cgroups when a protected group misses its configured `io.latency` target. The implementation is hierarchy-aware: submit and completion paths walk from the bio's `blkcg_gq` toward the root and apply accounting or throttling at configured ancestors.

## Important APIs, Types, And Functions
Core state lives in `struct blk_iolatency`, `struct iolatency_grp`, `struct child_latency_info`, and `struct latency_stat`. `blk_iolatency_init()` attaches `RQ_QOS_LATENCY` to a disk and activates `blkcg_policy_iolatency`. `blkcg_iolatency_throttle()` is the submit hook, `blkcg_iolatency_done_bio()` is the completion hook, and `blkcg_iolatency_exit()` tears the policy down. Cgroup user interface is provided by `iolatency_files`, especially `iolatency_set_limit()` and `iolatency_print_limit()` for the `latency` file. Policy lifecycle hooks are `iolatency_pd_alloc()`, `iolatency_pd_init()`, `iolatency_pd_offline()`, and `iolatency_pd_free()`.

## Control Flow
On configuration, `iolatency_set_limit()` opens the target block device, initializes the rq-qos policy if needed under `rq_qos_mutex`, prepares the cgroup/device binding, parses `target=<usec>|max`, and updates `min_lat_nsec`. Enabling the first target schedules `enable_work`, which freezes the queue before flipping `enabled` and `QUEUE_FLAG_BIO_ISSUE_TIME` so inflight accounting remains balanced. On bio submission, `blkcg_iolatency_throttle()` checks inherited scale cookies and waits on each group's `rq_wait` unless the bio is issued as root or the task is dying. On completion, `blkcg_iolatency_done_bio()` decrements inflight counters, records latency unless status is `BLK_STS_AGAIN`, rolls the accounting window, and calls `iolatency_check_latencies()` to update parent scale cookies. `blkiolatency_timer_fn()` periodically clears stale scale groups and allows recovery.

## State And Persistence
The controller stores runtime-only kernel state in per-cgroup policy data: per-CPU latency stats, current window stats, `max_depth`, delay accounting, scale cookies, and latency targets. Persistent user-visible state is the configured cgroup file value; there is no on-disk persistence in this file. Atomic counters and spinlocks protect shared fields; queue freezing protects the global enabled toggle from racing with in-flight bio accounting.

## Dependencies And Integration Points
This code integrates with blk-cgroup, rq-qos, blk-stat, blk-mq queue freezing, timer/workqueue infrastructure, memcg delay accounting, bio issue time tracking, and block trace/debug stats. It relies on `bio_issue_as_root_blkg()`, `blkcg_schedule_throttle()`, `blkcg_use_delay()`, and `blkcg_add_delay()` for cgroup semantics and priority-inversion handling.

## Risks And Test Signals
High-risk areas are unbalanced inflight counts when enabling/disabling, scale-cookie races between parent and child groups, incorrect treatment of `issue_as_root`, missed wakeups on depth increases, and latency window math for SSD percentile-style versus rotating mean-latency modes. Useful tests include cgroup hierarchy workloads with competing latency targets, toggling targets while I/O is active, root-issued metadata/swap I/O delay behavior, `BLK_STS_AGAIN` retries, queue freeze/unfreeze stress, and debug-stat output for depth/window/average latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-iolatency.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-ioprio.c -->
# sources/distributed-fs/ceph-client/block/blk-ioprio.c

## Purpose
`blk-ioprio.c` implements a blk-cgroup policy that rewrites bio I/O priority class according to a cgroup setting. It is an rq-qos-adjacent cgroup mechanism intended to affect I/O that task-local `ioprio_set()` may miss, including writeback I/O when the filesystem associates writeback with a cgroup.

## Important APIs, Types, And Functions
The central type is `struct ioprio_blkcg`, which embeds `struct blkcg_policy_data` and stores an `enum prio_policy`. Supported policies are `no-change`, `promote-to-rt`, `restrict-to-be`, `idle`, and `none-to-rt`. The public entry point is `blkcg_set_ioprio(struct bio *bio)`. Cgroup file handling is via `ioprio_show_prio_policy()` and `ioprio_set_prio_policy()` for `prio.class`. Policy allocation/free hooks are `ioprio_alloc_cpd()` and `ioprio_free_cpd()`.

## Control Flow
At module init, `ioprio_init()` registers `ioprio_policy` with blk-cgroup. Each cgroup gets a zeroed `ioprio_blkcg` defaulting to `POLICY_NO_CHANGE`. Writes to `prio.class` must start at offset zero and are parsed with `sysfs_match_string()` against `policy_name`. During bio preparation, `blkcg_set_ioprio()` fetches the bio's cgroup policy data through `bio->bi_blkg->blkcg`. If the policy is promotion to RT, non-RT priorities become RT class with level 4. For restrictive policies, the code computes a class value with `IOPRIO_PRIO_VALUE()` and uses `max_t()` because larger non-NONE priority values represent lower priority.

## State And Persistence
State is per-cgroup kernel memory containing only the selected policy enum. It is exposed through cgroupfs but not persisted by this file. The policy is read locklessly in the bio path, so correctness depends on the enum-sized store/load being safe for concurrent readers.

## Dependencies And Integration Points
The file depends on blk-cgroup policy registration, cgroup seq/kernfs helpers, `linux/ioprio.h` class encoding, and bio `bi_ioprio`. It is declared to other block code through `blk-ioprio.h`.

## Risks And Test Signals
Risk centers on policy semantics and class encoding: RT promotion must not downgrade existing RT I/O, `restrict-to-be` must turn NONE/RT into best-effort without changing lower-priority classes incorrectly, and `idle` must force the idle class. Tests should cover cgroup file parsing, offset write rejection, default no-op behavior, writeback bio priority assignment, and interaction with task-set I/O priorities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-ioprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-ioprio.h -->
# sources/distributed-fs/ceph-client/block/blk-ioprio.h

## Purpose
`blk-ioprio.h` is the internal block-layer declaration point for the cgroup I/O priority policy. It lets submit-side code call `blkcg_set_ioprio()` without carrying conditional compilation into every caller.

## Important APIs, Types, And Functions
The only API is `blkcg_set_ioprio(struct bio *bio)`. When `CONFIG_BLK_CGROUP_IOPRIO` is enabled, the function is provided by `blk-ioprio.c`; otherwise this header provides a static inline no-op. The header forward-declares `struct request_queue` and `struct bio`, although only `struct bio` is required by the visible function.

## Control Flow
There is no runtime control flow when the feature is disabled; calls compile away. When enabled, callers link to the policy implementation and bio priority may be rewritten according to the bio's cgroup.

## State And Persistence
The header owns no state. It controls build-time behavior only through the Kconfig guard.

## Dependencies And Integration Points
It depends on `linux/kconfig.h` for configuration predicates and integrates with the block submission path by providing a stable function name regardless of feature availability.

## Risks And Test Signals
The main risk is accidental divergence between enabled and disabled builds. Build tests should cover both `CONFIG_BLK_CGROUP_IOPRIO=y` and `n`, and submit-path tests should verify that disabled builds have no priority side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-ioprio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-lib.c -->
# sources/distributed-fs/ceph-client/block/blk-lib.c

## Purpose
`blk-lib.c` provides exported helper operations for block-device range management: discard, write zeroes, zeroout fallback, and secure erase. It translates large logical ranges into bio chains that obey device limits and block-size alignment.

## Important APIs, Types, And Functions
Exported APIs include `__blkdev_issue_discard()`, `blkdev_issue_discard()`, `__blkdev_issue_zeroout()`, `blkdev_issue_zeroout()`, and `blkdev_issue_secure_erase()`. `blk_alloc_discard_bio()` allocates one discard bio at a granularity-aligned size. Internal helpers include `bio_discard_limit()`, `bio_write_zeroes_limit()`, `__blkdev_issue_write_zeroes()`, `blkdev_issue_write_zeroes()`, `__blkdev_issue_zero_pages()`, and `blkdev_issue_zero_pages()`.

## Control Flow
Discard starts by computing an aligned per-bio sector limit, allocating zero-vector discard bios, chaining them with `bio_chain_and_submit()`, and then waiting on the anchor bio in the synchronous wrapper. Zeroout first validates alignment and read-only state, tries hardware `REQ_OP_WRITE_ZEROES` if the queue advertises support, and falls back to explicit writes of the kernel zero folio unless `BLKDEV_ZERO_NOFALLBACK` is set. `BLKDEV_ZERO_KILLABLE` lets long loops stop on fatal signals. Secure erase caps each bio by the device maximum and `BIO_MAX_SECTORS`, checks logical-block alignment, and submits a chain of `REQ_OP_SECURE_ERASE` bios.

## State And Persistence
The file creates transient bio chains and plugs; it does not persist state. Device queue limits may change at runtime, especially write-zeroes capability after transport errors, so wrappers re-check limits and map post-error zeroes failure to `-EOPNOTSUPP` when support is withdrawn.

## Dependencies And Integration Points
It integrates with `struct block_device`, queue limits exposed through `bdev_*` helpers, bio allocation/submission, plugging, zero folios, and exported block APIs used by filesystems, dm/md, and utilities that need discard or zeroing.

## Risks And Test Signals
Important risks are sector-count overflow when shifting to bytes, discard granularity misalignment for partitions, fallback behavior on devices that drop write-zeroes support, killable loops leaving partial progress, and read-only/alignment error paths. Tests should cover partition-offset discard alignment, zeroout with and without `REQ_NOUNMAP`, devices that fail write-zeroes then require fallback, secure erase limit splitting, and full-device operations that exercise `cond_resched()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-map.c -->
# sources/distributed-fs/ceph-client/block/blk-map.c

## Purpose
`blk-map.c` maps user or kernel buffers into passthrough block requests. It chooses between direct page mapping, iterator-backed bvec reuse, and copied bounce buffers depending on alignment, address type, queue limits, and caller-provided `rq_map_data`.

## Important APIs, Types, And Functions
External APIs are `blk_rq_append_bio()`, `blk_rq_map_user_iov()`, `blk_rq_map_user()`, `blk_rq_map_user_io()`, `blk_rq_unmap_user()`, and `blk_rq_map_kern()`. `struct bio_map_data` preserves a copied `iov_iter` and ownership flags so completion can copy read data back and free pages. Internal mapping paths include `bio_copy_user_iov()`, `bio_map_user_iov()`, `blk_rq_map_user_bvec()`, `bio_map_kern()`, and `bio_copy_kern()`.

## Control Flow
User mapping first classifies whether copying is required: caller-supplied map data, DMA alignment mismatch, non-user iterators, stack objects, or virtual-boundary gaps force a bounce path. ITER_BVEC can be reused directly but falls back to copying if queue limits would require splitting. Each produced bio is appended through `blk_rq_append_bio()`, which calls `bio_split_io_at()` and rejects mappings that would need splitting. Unmap walks the original bio list, copies read data back for copied user buffers, releases pinned pages for direct mappings, unmaps integrity metadata, and drops bio references. Kernel mapping directly maps vmalloc/linear buffers when aligned and copies otherwise, with read completion copying data back from bounce pages.

## State And Persistence
State is attached to bios via `bi_private` and `bi_end_io`, plus request fields `bio`, `biotail`, `__data_len`, `nr_phys_segments`, and `phys_gap_bit`. Lifetimes are sensitive: copied user iterators are deep-copied because caller iovecs can be stack-backed, and unmap must run in process context if data must be copied to user memory.

## Dependencies And Integration Points
This file depends on iov_iter import/copy helpers, bio page pinning, queue DMA alignment and virtual-boundary limits, merge/split helpers from `blk-merge.c`, integrity unmapping, and passthrough request users such as SG_IO and driver-specific command paths.

## Risks And Test Signals
Risk areas include user copy faults, short iterators, stack-buffer kernel mapping, vmalloc cache invalidation, request append failures after partial mapping, and cleanup consistency across mixed copied/direct bios. Tests should include unaligned user buffers, ITER_BVEC passthrough over hardware limits, read copy-back from workqueue/orphan context, `rq_map_data` null-mapped paths, vmalloc reads, and integrity metadata unmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-merge.c -->
# sources/distributed-fs/ceph-client/block/blk-merge.c

## Purpose
`blk-merge.c` enforces queue limits while splitting bios and merging bios or requests. It is the central policy for segment counts, DMA/virtual boundary gaps, discard limits, atomic-write restrictions, integrity and crypto merge compatibility, and scheduler-assisted merging.

## Important APIs, Types, And Functions
Key exported APIs include `bio_submit_split_bioset()`, `bio_split_io_at()`, `bio_split_to_limits()`, `blk_recalc_rq_segments()`, `ll_back_merge_fn()`, `bio_seg_gap()`, `blk_attempt_req_merge()`, `blk_rq_merge_ok()`, `blk_try_merge()`, `bio_attempt_back_merge()`, `blk_attempt_plug_merge()`, `blk_bio_list_merge()`, and `blk_mq_sched_try_merge()`. Internal helpers include `bio_will_gap()`, `get_max_io_size()`, `bvec_split_segs()`, `bio_split_discard()`, `bio_split_zone_append()`, `bio_split_write_zeroes()`, and request-to-request merge routines.

## Control Flow
Bio splitting scans bvecs against queue limits, alignment masks, crypto data-unit size, max segments, max bytes, virtual boundary gaps, zone write granularity, and atomic-write constraints. If splitting is necessary, atomic bios fail with `-EINVAL`, `REQ_NOWAIT` bios fail with `-EAGAIN`, and normal bios are split on a block-aligned boundary with polled I/O cleared. Merge control flow first checks operation, cgroup, integrity, crypto, write hint/stream, I/O priority, and atomic compatibility. Back/front/discard merge paths then enforce gap, sector, and segment limits, update request sector/data/segment accounting, propagate failfast mixed-merge state, call rq-qos merge hooks, and notify trace/elevator code.

## State And Persistence
No persistent state is owned here, but many request and bio fields are mutated: `bi_next`, `biotail`, `__data_len`, `__sector`, `nr_phys_segments`, `nr_integrity_segments`, `phys_gap_bit`, `rq_flags`, and `cmd_flags`. Split bios are chained to preserve completion ordering and resubmit the remainder.

## Dependencies And Integration Points
The file integrates with block queue limits, blk-cgroup merge rules, blk-integrity, blk-crypto, rq-qos, elevator callbacks, blk-throttle, zone write plugging, partition stats, and tracepoints. It is directly consumed by passthrough mapping, bio submission, plug merging, and mq scheduler merging.

## Risks And Test Signals
High-risk cases are off-by-one split boundaries, zero-byte split results, atomic writes being split or cross-boundary merged, NOWAIT semantics, discard segment accounting, mixed failfast propagation, front merges on zoned writes, crypto/integrity incompatibility, and stale physical gap bits. Tests should cover max segment/virt-boundary limits, physical/logical block alignment, write-zeroes limit changes, zone append no-split checks, request-to-request merge accounting, plug-list merge scan limits, and trace/stat increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-merge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-cpumap.c -->
# sources/distributed-fs/ceph-client/block/blk-mq-cpumap.c

## Purpose
`blk-mq-cpumap.c` builds CPU-to-hardware-queue mappings for multiqueue block devices. It provides generic possible/online CPU queue counts, even CPU grouping, NUMA lookup by queue, and IRQ-affinity-based mapping when a bus supplies affinity information.

## Important APIs, Types, And Functions
Exported APIs are `blk_mq_num_possible_queues()`, `blk_mq_num_online_queues()`, `blk_mq_map_queues()`, and `blk_mq_map_hw_queues()`. `blk_mq_hw_queue_to_node()` performs reverse lookup from queue index to NUMA node. The main data structure is `struct blk_mq_queue_map`, especially `nr_queues`, `queue_offset`, and per-CPU `mq_map`.

## Control Flow
Queue count helpers weight either `cpu_possible_mask` or `cpu_online_mask` and cap the result by `max_queues` when nonzero. `blk_mq_map_queues()` asks `group_cpus_evenly()` for queue-sized CPU masks; if allocation fails, all possible CPUs map to `queue_offset`. Otherwise each queue is assigned CPUs from its group and the temporary mask array is freed. `blk_mq_map_hw_queues()` first tries `dev->bus->irq_get_affinity(dev, queue + offset)` for each hardware queue; if any mask is unavailable or the bus has no callback, it falls back to even mapping.

## State And Persistence
The file only writes the caller-provided `qmap->mq_map` array. No persistent or global state is owned.

## Dependencies And Integration Points
It depends on CPU masks, NUMA `cpu_to_node()`, `group_cpus_evenly()`, bus IRQ affinity callbacks, and blk-mq queue-map initialization used by drivers.

## Risks And Test Signals
Risks include fallback mapping hiding affinity failures, possible CPUs with no online counterpart, queue offsets for multiple map types, and NUMA reverse lookup returning `NUMA_NO_NODE` when a queue is unmapped. Tests should cover max queue caps, zero max queue behavior, failed `group_cpus_evenly()`, partial IRQ affinity failure fallback, and hotplug-era possible versus online CPU counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-cpumap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-debugfs.c -->
# sources/distributed-fs/ceph-client/block/blk-mq-debugfs.c

## Purpose
`blk-mq-debugfs.c` creates debugfs files for blk-mq queues, hardware contexts, software contexts, schedulers, and rq-qos policies. It exposes live request state, queue flags, tag bitmaps, dispatch lists, busy requests, and limited control operations for debugging.

## Important APIs, Types, And Functions
The exported request renderers are `__blk_mq_debugfs_rq_show()` and `blk_mq_debugfs_rq_show()`. Registration APIs include `blk_mq_debugfs_register()`, `blk_mq_debugfs_register_hctx()`, `blk_mq_debugfs_unregister_hctx()`, `blk_mq_debugfs_register_hctxs()`, `blk_mq_debugfs_unregister_hctxs()`, `blk_mq_debugfs_register_sched()`, `blk_mq_debugfs_unregister_sched()`, `blk_mq_debugfs_register_rq_qos()`, `blk_mq_debugfs_register_sched_hctx()`, and `blk_mq_debugfs_unregister_sched_hctx()`. `struct blk_mq_debugfs_attr` describes simple show/write or seq-ops files.

## Control Flow
Queue-level files expose `poll_stat`, `requeue_list`, `pm_only`, `state`, and zoned write plugs. Writing `state` accepts `run`, `start`, or `kick`, while rejecting writes on dying queues. Hctx files expose state/flags, dispatch and busy request lists, context maps, tags, sched tags, active count, dispatch busy score, and hctx type. Per-CPU context directories expose request lists by hctx type. Registration walks all hctxs, creates `hctxN` and `cpuN` directories, and later creates `sched` and `rqos` subtrees when schedulers or rq-qos policies are installed. File open/release selects either seq ops or `single_open()` based on the attr definition.

## State And Persistence
The debugfs tree is transient kernel diagnostic state. It stores dentries in `q->debugfs_dir`, `hctx->debugfs_dir`, `hctx->sched_debugfs_dir`, `q->sched_debugfs_dir`, and rq-qos `debugfs_dir`. Data reads are live snapshots protected by relevant locks such as `requeue_lock`, `hctx->lock`, `elevator_lock`, and `debugfs_mutex`.

## Dependencies And Integration Points
The file integrates with debugfs, seq_file, blk-mq request/tag internals, scheduler debug attributes, rq-qos debug attributes, queue debugfs locking, zone write plugging, and driver `mq_ops->show_rq`.

## Risks And Test Signals
Risks are use-after-free during queue removal, lock ordering against frozen queues, exposing stale request state while completions race, and writable debugfs operations changing queue execution. Tests should verify registration/unregistration during elevator switches and queue teardown, readable tag and request lists under load, rejection of invalid `state` writes, and correct absence of files when scheduler/rq-qos attrs are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-debugfs.h -->
# sources/distributed-fs/ceph-client/block/blk-mq-debugfs.h

## Purpose
`blk-mq-debugfs.h` declares the internal blk-mq debugfs interface and compiles it out cleanly when `CONFIG_BLK_DEBUG_FS` is disabled. It also provides the zoned write-plug debugfs hook with a fallback no-op.

## Important APIs, Types, And Functions
When debugfs is enabled, it defines `struct blk_mq_debugfs_attr` with name, mode, show/write callbacks, and optional seq operations. It declares request renderers and registration/unregistration functions for queues, hctxs, schedulers, scheduler hctxs, and rq-qos. When disabled, all registration functions are static inline no-ops. `queue_zone_wplugs_show()` is declared only when both zoned block devices and block debugfs are enabled.

## Control Flow
The header has no runtime logic beyond disabled-build no-ops. Its compile-time branches keep callers simple and ensure debugfs-dependent code is eliminated from non-debug builds.

## State And Persistence
No state is owned in the header. It defines the shape of transient debugfs state managed by `blk-mq-debugfs.c`.

## Dependencies And Integration Points
It depends on `seq_file`, `request_queue`, `request`, and `blk_mq_hw_ctx` declarations in enabled builds. It is included by blk-mq scheduling, debugfs, and registration code.

## Risks And Test Signals
Risks are prototype drift and build failures in disabled configurations. Build coverage should include `CONFIG_BLK_DEBUG_FS=n`, zoned without debugfs, debugfs without zoned, and full debugfs/zoned enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-dma.c -->
# sources/distributed-fs/ceph-client/block/blk-mq-dma.c

## Purpose
`blk-mq-dma.c` maps blk-mq requests into DMA segments and scatterlists. It supports normal request payloads, special payloads, PCI peer-to-peer DMA, IOVA-coalesced mappings, direct physical mappings, and integrity metadata mappings.

## Important APIs, Types, And Functions
Exported APIs are `blk_rq_dma_map_iter_start()`, `blk_rq_dma_map_iter_next()`, `__blk_rq_map_sg()`, and, under integrity support, `blk_rq_integrity_dma_map_iter_start()`, `blk_rq_integrity_dma_map_iter_next()`, and `blk_rq_map_integrity_sg()`. Internal iterators include `struct blk_map_iter`, `blk_map_iter_next()`, `blk_dma_map_iter_start()`, `blk_dma_map_bus()`, `blk_dma_map_direct()`, and `blk_rq_dma_map_iova()`.

## Control Flow
Mapping starts by initializing an iterator from request bios, special payload, or an empty flush request. `blk_map_iter_next()` emits physically mergeable vectors while respecting queue segment size limits and bio boundaries. The first vector determines PCI P2PDMA behavior: bus-address mapping returns a bus address directly; host-bridge P2P is treated like normal DMA with `DMA_ATTR_MMIO`; unsupported P2P fails with `BLK_STS_INVAL`. If request gap constraints allow and IOVA allocation succeeds, the code links all physical vectors into one IOVA mapping and synchronizes it; otherwise it maps one segment at a time with `dma_map_phys()`. Scatterlist mapping mirrors the iterator and marks the final entry.

## State And Persistence
State is caller-provided and transient: `struct dma_iova_state` must survive until unmap, while `struct blk_dma_iter` tracks current mapping status, P2P state, DMA address, and length during iteration. No persistent kernel policy state is owned.

## Dependencies And Integration Points
The file integrates with DMA mapping APIs, PCI P2PDMA, block queue segment limits, request integrity metadata, scatterlist helpers, and drivers that consume DMA iterators or legacy scatterlists.

## Risks And Test Signals
Risks include incorrect physical segment coalescing, IOVA cleanup on partial link/sync failure, P2PDMA map-mode misclassification, scatterlist termination reuse, and integrity segment overrun. Tests should cover empty flush requests, special payloads, mixed-bio request chains, P2P bus and host-bridge cases, IOMMU merge-boundary restrictions, DMA mapping errors, and integrity metadata segment counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-sched.c -->
# sources/distributed-fs/ceph-client/block/blk-mq-sched.c

## Purpose
`blk-mq-sched.c` implements blk-mq scheduler dispatch, merge delegation, scheduler tag allocation, scheduler resource batching, debugfs registration, and scheduler lifecycle attach/detach. It bridges elevator callbacks with blk-mq hardware queues and software queues.

## Important APIs, Types, And Functions
Dispatch APIs include `blk_mq_sched_mark_restart_hctx()`, `__blk_mq_sched_restart()`, and `blk_mq_sched_dispatch_requests()`. Merge APIs are `blk_mq_sched_bio_merge()` and `blk_mq_sched_try_insert_merge()`. Lifecycle/resource APIs include `blk_mq_alloc_sched_tags()`, `blk_mq_alloc_sched_res()`, `blk_mq_alloc_sched_ctx_batch()`, `blk_mq_alloc_sched_res_batch()`, `blk_mq_init_sched()`, `blk_mq_sched_free_rqs()`, and `blk_mq_exit_sched()`.

## Control Flow
Dispatch first drains `hctx->dispatch` for fairness, marks restart when residual requests exist, and only pulls from the scheduler when the dispatch list is empty or made progress. With an elevator, `__blk_mq_do_dispatch_sched()` repeatedly obtains driver budget, asks the scheduler for a request, assigns the budget token, groups cross-hctx requests by hctx if needed, and stops when tags or dispatch capacity are exhausted. Without an elevator, `blk_mq_do_dispatch_ctx()` round-robins software contexts and updates `dispatch_from`. Bio merge first delegates to the scheduler `bio_merge` callback when present, otherwise checks the per-context request list. Scheduler init installs sched tags, calls queue and hctx elevator init callbacks, and unwinds tags on failure.

## State And Persistence
State is runtime queue state: hctx restart bits, `dispatch_from`, scheduler tags, `q->nr_requests`, `q->sched_shared_tags`, `hctx->sched_tags`, `sched_data`, and `q->elevator`. Batch resource changes use an xarray of `elv_change_ctx` entries under `update_nr_hwq_lock`.

## Dependencies And Integration Points
The file integrates with elevator operations, blk-mq dispatch/tag APIs, driver budget callbacks, debugfs registration, writeback throttling defaults, xarray batch updates, and request merge helpers from `blk-merge.c`.

## Risks And Test Signals
Risks include dispatch starvation when residual lists remain, budget leaks on scheduler no-dispatch, cross-hctx scheduler ordering, tag allocation unwind leaks, shared scheduler tag resizing, and elevator switch races. Tests should cover scheduler and no-scheduler queues, busy dispatch lists, SCSI-style budget failures, hctx count changes, shared tags, elevator init_hctx failure unwind, and debugfs register/unregister during scheduler switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-sched.h -->
# sources/distributed-fs/ceph-client/block/blk-mq-sched.h

## Purpose
`blk-mq-sched.h` declares the internal interface between blk-mq core code, elevators, and scheduler resources. It also provides small inline helpers for optional scheduler callbacks and merge predicates.

## Important APIs, Types, And Functions
It declares scheduler dispatch, merge, lifecycle, resource allocation, and free functions implemented in `blk-mq-sched.c`. `MAX_SCHED_RQ` defines the scheduler request pool size. Inline helpers include `blk_mq_alloc_sched_data()`, `blk_mq_free_sched_data()`, `blk_mq_sched_restart()`, `bio_mergeable()`, `blk_mq_sched_allow_merge()`, `blk_mq_sched_completed_request()`, `blk_mq_sched_requeue_request()`, `blk_mq_sched_has_work()`, `blk_mq_sched_needs_restart()`, `blk_mq_set_min_shallow_depth()`, and `blk_mq_is_sync_read()`.

## Control Flow
The inline helpers guard optional elevator callbacks, so callers can notify schedulers without open-coding NULL checks. `blk_mq_sched_restart()` checks the restart bit before invoking the heavier restart path. `blk_mq_sched_allow_merge()` only calls `allow_merge` for requests using scheduler private state. `blk_mq_set_min_shallow_depth()` walks hctxs and adjusts scheduler tag shallow depth.

## State And Persistence
The header owns no state but defines how queue, hctx, request, and elevator state should be accessed. Inline functions can mutate scheduler tag shallow-depth settings and invoke scheduler callbacks that mutate scheduler-private state.

## Dependencies And Integration Points
It depends on `elevator.h` and `blk-mq.h`, and is included by merge, scheduler, and blk-mq core code that needs scheduler-aware behavior.

## Risks And Test Signals
Risks include calling scheduler callbacks after elevator teardown, dereferencing `sched_tags` when no scheduler tags exist, and inconsistent merge behavior when `RQF_USE_SCHED` is not set. Tests should include elevator-less builds, scheduler callback absence, completion/requeue callback coverage, and shallow-depth updates across every hctx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-sysfs.c -->
# sources/distributed-fs/ceph-client/block/blk-mq-sysfs.c

## Purpose
`blk-mq-sysfs.c` creates and destroys the `/sys/block/<disk>/mq` hierarchy for blk-mq queues. It exposes each hardware context and its CPU children, plus read-only attributes for tag counts and CPU affinity.

## Important APIs, Types, And Functions
Public functions are `blk_mq_hctx_kobj_init()`, `blk_mq_sysfs_init()`, `blk_mq_sysfs_deinit()`, `blk_mq_sysfs_register()`, `blk_mq_sysfs_unregister()`, `blk_mq_sysfs_unregister_hctxs()`, and `blk_mq_sysfs_register_hctxs()`. Release callbacks are `blk_mq_sysfs_release()`, `blk_mq_ctx_sysfs_release()`, and `blk_mq_hw_sysfs_release()`. Hctx attributes are `nr_tags`, `nr_reserved_tags`, and `cpu_list`.

## Control Flow
Initialization creates the queue-level mq kobject and per-CPU context kobjects. Registering a disk adds `mq` under the disk kobject, sends `KOBJ_ADD`, locks `tag_list_lock`, and adds each hctx kobject plus child `cpuN` kobjects. On any registration failure, previously added hctx/context kobjects are removed and a `KOBJ_REMOVE` is sent. Unregistration removes hctx trees under the same tag-list lock and deletes the queue mq kobject. Hctx show operations run under `q->elevator_lock` so tag pointers and hctx state are stable enough for sysfs output.

## State And Persistence
State is kobject lifetime state attached to `blk_mq_ctxs`, `blk_mq_ctx`, and `blk_mq_hw_ctx`. Release callbacks free percpu contexts, hctx cpumasks, context arrays, and hctx objects. The sysfs files expose live runtime values and do not persist configuration.

## Dependencies And Integration Points
The file integrates with sysfs/kobject infrastructure, disk device kobjects, blk-mq hctx/context topology, tag-set locking, CPU masks, and queue registration state.

## Risks And Test Signals
Risks include kobject reference leaks, double deletion during hctx reconfiguration, racing queue registration checks, and PAGE_SIZE formatting truncation in large CPU lists. Tests should cover disk register/unregister, partial hctx registration failure, hctx re-register after hardware queue count changes, CPU-list formatting on large systems, and sysfs reads during elevator switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-tag.c -->
# sources/distributed-fs/ceph-client/block/blk-mq-tag.c

## Purpose
`blk-mq-tag.c` manages blk-mq driver tag allocation using scalable bitmaps. It tracks active shared-tag users, allocates normal and reserved tags, wakes sleepers, iterates busy requests, drains completed requests, allocates/frees tag maps, resizes shared tag maps, and generates queue-wide unique tags.

## Important APIs, Types, And Functions
Allocation APIs include `blk_mq_get_tag()`, `blk_mq_get_tags()`, `blk_mq_put_tag()`, and `blk_mq_put_tags()`. Activity APIs are `__blk_mq_tag_busy()`, `__blk_mq_tag_idle()`, and `blk_mq_tag_wakeup_all()`. Iteration/drain APIs are `blk_mq_all_tag_iter()`, `blk_mq_tagset_busy_iter()`, `blk_mq_tagset_wait_completed_request()`, and `blk_mq_queue_tag_busy_iter()`. Lifecycle APIs are `blk_mq_init_tags()`, `blk_mq_free_tags()`, `blk_mq_tag_resize_shared_tags()`, `blk_mq_tag_update_sched_shared_tags()`, and `blk_mq_unique_tag()`.

## Control Flow
Before allocating driver tags, busy hctxs mark themselves active and update wake batches based on active users. `blk_mq_get_tag()` chooses reserved or normal bitmap, tries a shallow or full bitmap allocation, returns immediately for NOWAIT failure, or sleeps on the appropriate sbitmap wait state. While waiting it runs the hardware queue, retries allocation, remaps ctx/hctx after sleep, and compensates with a wakeup if the destination bitmap changed. Tags are returned to the corresponding normal or reserved bitmap. Busy iteration walks reserved and normal bitmaps, safely resolves `tags->rqs[]` entries with request references, filters by queue/hctx, and releases references after callbacks. Tag freeing releases sbitmap queues immediately and uses SRCU-delayed freeing when request pages exist.

## State And Persistence
Runtime state lives in `struct blk_mq_tags`: normal and reserved sbitmap queues, `active_queues`, `nr_tags`, `nr_reserved_tags`, request pointer arrays, allocated request pages, lock, and SRCU free callback. No persistent state exists.

## Dependencies And Integration Points
The file integrates with blk-mq allocation data, hctx flags/state, queue usage refs, SRCU-protected tag-set arrays, sbitmap queues, scheduler shared tags, request references, kmemleak, and blk-mq queue dispatch.

## Risks And Test Signals
Risks include missed wakeups while sleeping for tags, underflow of `active_queues`, allocating tags on inactive hctxs, request pointer races after bitmap bits are set, shared-tag fairness regressions, reserved tag misuse, and SRCU free lifetime bugs. Tests should cover NOWAIT allocation failure, reserved-tag pools, hctx remap while waiting, shared versus per-hctx tags, busy iteration during completion, queue teardown with in-flight requests, tag resize, and unique-tag uniqueness across hctxs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/blk-mq-tag.c -->
