# sources/distributed-fs/ceph-client/mm/page-writeback.c

## Purpose

`page-writeback.c` manages dirty page accounting, dirty throttling, background writeback thresholds, backing-device writeback proportions, folio dirty/writeback state transitions, and helper iteration for filesystem `writepages` implementations. It is the core policy layer that prevents dirty file cache from overrunning memory while keeping storage devices busy.

For Ceph-client code, this is a major integration point. Ceph file data dirtied through the page cache uses these helpers for dirty accounting and throttling, while Ceph writeback behavior interacts with `address_space_operations`, `writeback_control`, backing-device limits, cgroup writeback domains, and folio writeback state.

## Important APIs, Types, And Functions

- Sysctl-backed policy variables: `dirty_background_ratio`, `dirty_background_bytes`, `vm_dirty_ratio`, `vm_dirty_bytes`, `dirty_writeback_interval`, `dirty_expire_interval`, `vm_highmem_is_dirtyable`, and deprecated `laptop_mode`.
- Global writeback domain: `struct wb_domain global_wb_domain`.
- Dirty limit calculators: `global_dirty_limits()`, `node_dirty_ok()`, `domain_dirty_limits()`, `node_dirty_limit()`, `global_dirtyable_memory()`, and `node_dirtyable_memory()`.
- Writeback-domain accounting: `wb_domain_init()`, `wb_domain_exit()`, `wb_writeout_inc()`, `wb_domain_writeout_add()`, `writeout_period()`, and `__wb_writeout_add()`.
- BDI limit controls: `bdi_set_min_ratio()`, `bdi_set_max_ratio()`, `bdi_set_min_bytes()`, `bdi_set_max_bytes()`, `bdi_set_strict_limit()`, and byte getters.
- Dirty throttle engine: `balance_dirty_pages_ratelimited_flags()`, `balance_dirty_pages_ratelimited()`, `balance_dirty_pages()`, `wb_position_ratio()`, `wb_update_dirty_ratelimit()`, `wb_update_bandwidth()`, and `wb_over_bg_thresh()`.
- Writeback iteration: `tag_pages_for_writeback()`, `writeback_iter()`, `do_writepages()`, and helper `writeback_get_folio()`.
- Folio dirty/writeback state APIs: `noop_dirty_folio()`, `filemap_dirty_folio()`, `folio_mark_dirty()`, `folio_mark_dirty_lock()`, `folio_redirty_for_writepage()`, `__folio_cancel_dirty()`, `folio_clear_dirty_for_io()`, `__folio_start_writeback()`, `__folio_end_writeback()`, `folio_wait_writeback()`, `folio_wait_writeback_killable()`, and `folio_wait_stable()`.

## Control Flow

Initialization enters `page_writeback_init()`. It initializes `global_wb_domain`, registers CPU hotplug callbacks that recompute `ratelimit_pages`, and registers VM writeback sysctls. `writeback_set_ratelimit()` computes the global dirty threshold and sets a per-CPU/task polling interval intended to limit overshoot when all CPUs dirty concurrently.

Dirty limit calculation starts from dirtyable memory. `global_dirtyable_memory()` sums free pages and active/inactive file pages, subtracts reserves and optionally highmem. `domain_dirty_limits()` converts ratio or byte sysctls into dirty and background thresholds for either the global domain or a memcg domain, including real-time/deadline task boosts and 32-bit cap enforcement. `global_dirty_limits()` exposes global thresholds, and `node_dirty_ok()` checks per-node dirty/writeback pages against node-scaled limits.

Writeback bandwidth accounting uses `wb_domain` completions with fprop. `__wb_writeout_add()` increments per-wb `WB_WRITTEN`, global completions, and memcg-domain completions when enabled. `writeout_period()` ages proportions on a deferrable timer and stops the timer when all fractions decay to zero.

Backing-device threshold sharing is handled by `__wb_calc_thresh()`, which assigns each `bdi_writeback` a fraction of a dirty threshold based on recent completion proportions, BDI min/max ratios, inactive-device grace, and strict-limit behavior. BDI setter functions validate ratio/byte limits under `bdi_lock` and maintain the global `bdi_min_ratio` sum.

Dirty throttling begins when `balance_dirty_pages_ratelimited_flags()` is called after newly dirtying pages. It skips non-writeback BDIs, resolves the current cgroup writeback object if needed, handles per-CPU ratelimit and leaked dirty counts from exiting tasks, and calls `balance_dirty_pages()` once the current task reaches its dirty pause threshold.

`balance_dirty_pages()` repeatedly computes global and optional memcg dirty domains, starts background writeback when above background thresholds, checks freerun ceilings, computes per-wb dirty limits, chooses the stricter global or memcg throttle control, updates bandwidth and dirty ratelimit every `BANDWIDTH_INTERVAL`, and sleeps the task with `io_schedule_timeout()` unless `BDP_ASYNC` asks for `-EAGAIN`. The core control loop uses `wb_position_ratio()` and `wb_update_dirty_ratelimit()` to scale each task's dirtying rate based on dirty position relative to freerun, setpoint, hard limit, write bandwidth, strict BDI limits, and observed dirty rate.

Background writeback decisions use `wb_over_bg_thresh()`, which checks global and memcg domains without counting writeback pages for the background decision, then checks per-wb background thresholds.

Filesystem writeback uses the second half of the file. `tag_pages_for_writeback()` marks currently dirty xarray entries with `PAGECACHE_TAG_TOWRITE` to avoid livelock against new dirtying. `writeback_iter()` is the expected helper loop for filesystem `->writepages`: it initializes range state, tags pages for integrity or tagged writeback, fetches and locks folios by tag, waits for existing writeback in sync mode, clears dirty for I/O, decrements `nr_to_write`, preserves the first error for `WB_SYNC_ALL`, and updates cyclic writeback index without wrapping in a way that would invert folio lock ordering. `do_writepages()` invokes the filesystem's `writepages` op, throttles on repeated `-ENOMEM` in sync mode, and updates bandwidth periodically.

Dirty-state transitions are carefully accounted. `filemap_dirty_folio()` sets the folio dirty bit, calls `__folio_mark_dirty()` to set xarray dirty tags and account `NR_FILE_DIRTY`, `NR_DIRTIED`, `WB_RECLAIMABLE`, `WB_DIRTIED`, task I/O, and cgroup foreign dirty tracking, then marks the inode `I_DIRTY_PAGES`. `folio_clear_dirty_for_io()` serializes against dirty PTEs with the locked folio, performs `folio_mkclean()`, invokes `folio_mark_dirty()` for side effects if needed, clears the dirty bit, and subtracts dirty accounting while leaving xarray tags temporarily coherent for writeback discovery. `__folio_start_writeback()` sets `PG_writeback`, xarray writeback tags, writeback stats, superblock inode-writeback state, clears dirty/TOWRITE tags as appropriate, and updates LRU/zone pending stats. `__folio_end_writeback()` clears writeback state, removes writeback xarray tags, subtracts `WB_WRITEBACK`, increments writeout completions and `NR_WRITTEN`, and wakes waiters through the folio flag transition.

## State And Persistence Behavior

The file maintains runtime-only kernel policy state: dirty thresholds, BDI ratios, writeback-domain fprop completions, timers, per-wb bandwidth/ratelimit stamps, per-CPU dirty ratelimit counters, and per-task `nr_dirtied`, `nr_dirtied_pause`, and `dirty_paused_when`. These states persist across writeback cycles until sysctl changes, CPU hotplug, BDI teardown, or domain exit.

Persistent file data is not written here directly. Instead, this code selects and prepares dirty folios, updates accounting, and calls filesystem `writepages`; the filesystem and lower layers perform actual I/O. Correct xarray tags and folio flags persist in the page cache until writeback or truncation changes them.

## Dependencies And Integration Points

This file depends on the page cache xarray, folios, inode/address-space operations, backing-dev info, cgroup writeback, memcg dirty stats, per-node VM stats, task I/O accounting, CPU hotplug, timers, fprop, sysctl, tracepoints, reclaim throttling, and architecture stable-page hooks.

Ceph integrates through its mapping and inode writeback operations. When Ceph marks folios dirty or implements `writepages`, these helpers control when dirtying tasks throttle, when background writeback starts, how errors propagate in writeback iteration, how cgroup writeback domains apply, and when folios are considered under writeback or clean.

## Risks And Edge Cases

- Dirty throttling is feedback-control code; small changes can destabilize throughput, fairness, or latency.
- Strict-limit BDIs throttle on per-wb counters even when global dirty pages are low; this is important for untrusted or slow filesystems but can surprise callers.
- Memcg writeback adds a second dirty domain; the effective throttle is the lower position ratio of global and memcg domains.
- Per-cpu stat error forces expensive exact stats at low thresholds; missing this can deadlock stacked BDIs by undercounting dirty pages.
- `writeback_iter()` callers must not break out early; they must call until it returns `NULL` so batches, errors, and cyclic index state are finalized.
- Dirty flag and xarray dirty tag are intentionally inconsistent while a folio is locked for writeback preparation; filesystem code must follow the expected folio lifecycle.
- `folio_clear_dirty_for_io()` relies on lock-based exclusion against dirty faults and on filesystem dirty_folio side effects.
- Stable writes can force waits in `folio_wait_stable()`, affecting direct I/O or network filesystem latency.
- `do_writepages()` retries sync writeback on `-ENOMEM` with reclaim throttling, which can stall under severe memory pressure.

## Test Signals

- VM tests should cover sysctl ratio/byte exclusivity, dirty threshold computation, highmem handling, CPU hotplug ratelimit recalculation, and BDI min/max/strict-limit validation.
- Writeback stress should validate `balance_dirty_pages()` under single fast device, slow device, mixed devices, strict-limit BDI, and memcg writeback.
- Filesystem tests should verify `writeback_iter()` usage, `WB_SYNC_ALL` error preservation, cyclic range progression, and no livelock while pages are being dirtied concurrently.
- Folio state tests should exercise dirty, redirty, cancel dirty, clear-for-IO, start/end writeback, wait-writeback, and stable-write behavior with correct VM and wb stats.
- Ceph-client tests should include buffered writes under cgroup limits, dirty throttling during slow OSD/network conditions, writeback error propagation, and page-cache accounting under memory pressure.
