# Group Research: group_923_linux_dm_sources_block_storage_linux_dm_drivers_md_dm_log_writes_c_s_66e978f4d748

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/linux-dm`.

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log-writes.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-log-writes.c

## Purpose

`dm-log-writes.c` implements the Device Mapper `log-writes` target. It passes I/O through to a backing device while sequentially recording completed writes, flushes, FUA writes, discards, metadata writes, and userspace marks to a separate log device. The target is intended for filesystem crash-consistency testing: replay the log up to a mark and inspect the reconstructed block-device state.

## Log Format And State

The log device starts with a `log_write_super` at sector 0 containing magic, version, entry count, and sector size. Each logged operation then consumes one sector of `log_write_entry` metadata followed by operation data when applicable. Mark entries store their string payload inline in the metadata sector; normal write data is copied into private pages and written after the entry. Discards log only metadata.

`struct log_writes_c` owns the pass-through device, log device, logical sector conversion state, next log sector, entry count, enabled flag, pending/log I/O counters, `unflushed_blocks`, `logging_blocks`, a waitqueue, a completion for superblock writes, and the logging kthread. `pending_block` snapshots a completed operation’s target sector, size, flags, optional mark/inline data, and copied bio vectors.

## Ordering Model

Normal completed writes go to `unflushed_blocks`. A completed flush splices previously unflushed writes ahead of the flush block into `logging_blocks`. FUA writes go straight to `logging_blocks`, and FUA or mark entries trigger a superblock update after the entry is logged. This models “what should have reached stable media” rather than raw submission order.

`log_writes_kthread()` serializes logging. It removes blocks from `logging_blocks`, reserves log sectors under `blocks_lock`, disables logging if the log device fills, increments `logged_entries`, submits metadata/data bios, and updates the log super for FUA/mark entries. `io_blocks` and `pending_blocks` allow destructor shutdown to wait until all submitted log bios and pending records drain.

## Mapping And End I/O

`log_writes_map()` ignores reads, zero-length non-flushes, and all I/O when logging has been disabled. For writes, it allocates a pending block before remapping the bio to the backing device. Non-discard write payloads are copied into fresh pages to avoid retaining caller-owned pages, including O_DIRECT pages. Discards allocate metadata-only records; if the backing queue lacks discard support, target limits advertise discard and the target completes the discard while still allowing logging behavior.

`normal_end_io()` attaches completed write records to the correct list: flushes splice their predecessor list into `logging_blocks`, FUA writes are logged immediately, and ordinary writes remain unflushed until a later flush or teardown.

## Control And Integration

The constructor syntax is `log-writes <dev_path> <log_dev_path>`. The target advertises one flush and one discard bio, per-bio private data, pass-through ioctls only when sizes match, and queue limits derived from the data device. The `mark <data>` message queues a `LOG_MARK_FLAG` entry with data truncated to fit one log sector. Teardown splices remaining unflushed blocks, appends `dm-log-writes-end`, waits for all logging, stops the kthread, and releases both devices.

When `CONFIG_FS_DAX` is enabled, DAX direct access and zero-page operations pass through to the backing device with page-offset adjustment.

## Invariants And Risks

- Log record order is based on completion and flush/FUA semantics, not submission order.
- Normal writes are durable in the log only after a later flush, FUA, mark, or teardown-driven drain.
- `logging_enabled` is turned off on log allocation/write errors or log-device exhaustion; status reports `logging_disabled`.
- Log-sector accounting uses target logical sector size and 512-byte bio sectors, so sector-size conversion is central.
- Error paths must balance `io_blocks` and `pending_blocks`; destructor waits on both.
- Superblock writes are serialized by waiting for `super_done`, preventing older super writes from racing newer entry counts.

## Test Focus

Test write/flush/FUA ordering, flush-with-data handling, discard with and without backing discard support, mark truncation and super update, log-device-full behavior, log write errors disabling logging, teardown drain with outstanding unflushed writes, DAX pass-through offsets, sector sizes larger than 512 bytes, and status output before/after logging disables.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log-writes.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-log.c

## Purpose

`dm-log.c` implements Device Mapper dirty-region log registration plus the built-in `core` and `disk` dirty log types used by mirror-like targets to track clean, dirty, synchronized, and recovering regions.

## Type Registry

The file maintains `_log_types` under `_lock`. `dm_dirty_log_type_register()` and `dm_dirty_log_type_unregister()` add and remove `dm_dirty_log_type` implementations. `dm_dirty_log_create()` resolves a type by name, loads modules named `dm-log-<type>` with fallback truncation at hyphens, takes the module reference, allocates `struct dm_dirty_log`, and calls the selected constructor. Destroy calls the type destructor, drops the module reference, and frees the log.

## Core Data Model

`struct log_c` stores the target, region size/count, sync count, flags for dirty/clean bitmap updates, optional persistent log state, and three bitmaps:

- `clean_bits`: whether each region is clean.
- `sync_bits`: whether each region is synchronized.
- `recovering_bits`: regions currently assigned for resync work.

`log_set_bit()` marks cleaned state touched; `log_clear_bit()` marks dirtied state touched. Region size must be a power of two, at least two sectors, and no larger than the target.

## Core Log

The `core` type is memory-only. Constructor arguments are `<region_size> [sync|nosync]`. `nosync` initializes all regions synchronized; default and `sync` initialize them needing resync unless later state says otherwise. The core log implements region clean/dirty marking, sync queries, resync work selection, sync completion accounting, and table/info status. `core_flush()` is a no-op because state is not persistent.

## Disk Log

The `disk` type uses arguments `<log_device> <region_size> [sync|nosync]`. It embeds the on-disk header at sector 0 and the clean bitmap after `LOG_OFFSET` sectors in one vmalloc buffer, accessed through `dm_io`. The disk header stores `MIRROR_MAGIC`, disk version 2, and `nr_regions`.

`disk_resume()` reads the header, initializes a new log if forced or magic is absent, rejects incompatible versions, adjusts bitmap state for grown/shrunk target sizes, copies `clean_bits` into `sync_bits`, recalculates `sync_count`, writes the updated header/bits, and flushes the log device. Read or write failures mark the log device failed and trigger a table event.

## Flush And Failure Semantics

`disk_flush()` writes persistent changes only when clean or dirty state was touched. If regions were marked clean and the caller supplied `flush_callback_fn`, that callback must succeed first; if it fails, all regions are marked dirty because the target cannot trust which clean transitions reached storage. Dirtying changes are followed by a preflush to the log device. Status reports log-device state as active, device failed, or flush failed.

## Invariants And Risks

- Persistent dirty log correctness depends on writing the clean bitmap and issuing required flushes after dirty transitions.
- On log-device read failure, all regions must be treated as out-of-sync; the code resets header region count and continues conservatively.
- `recovering_bits` prevents duplicate resync assignment for the same region.
- `sync_count` must track `sync_bits` transitions exactly.
- `flush_failed` suppresses later clean marking to avoid false-clean regions after an ordering failure.
- Disk log buffer size is rounded to the log device logical block size and rejected if larger than the log device.

## Test Focus

Test type registration duplicates/unregister misses, module autoload name fallback, invalid region sizes, `sync`/`nosync` initialization, disk header version rejection, target grow/shrink behavior, read/write/flush log-device failures, flush callback failure marking all dirty, resync work allocation with recovering bits, sync count updates, and status/table output for core and disk logs.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-log.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-mpath.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-mpath.c

## Purpose

`dm-mpath.c` implements the Device Mapper `multipath` target. It routes I/O over one of several underlying paths grouped into priority groups, supports pluggable path selectors, handles path failure and reinstatement, integrates with SCSI device handlers for path-group activation, and supports both request-based and bio-based queue modes.

## Object Model

A `multipath` instance owns priority groups, current and next selected groups, current path, valid path count, queue mode, SCSI hardware-handler settings, path-group initialization state, no-path queueing flags, queued bio list, timeout timer, and work items. A `priority_group` owns a path selector and `pgpath` entries. A `pgpath` wraps `struct dm_path`, failure count, active flag, and optional delayed activation work.

Important flags include `MPATHF_QUEUE_IO`, `MPATHF_QUEUE_IF_NO_PATH`, saved queue-if-no-path state during suspend, retained attached hardware handler, PG init disabled/required, and delayed PG init retry.

## Path Selection And Mapping

`choose_pgpath()` first tries the requested `next_pg`, then the current group, then non-bypassed groups, then bypassed groups with delayed retry. It calls the group’s selector `select_path()` and switches the current group through `__switch_pg()`. When a hardware handler is configured, switching groups sets `PG_INIT_REQUIRED` and `QUEUE_IO` so I/O waits for activation.

Request-based mapping clones requests to the selected path queue with `blk_mq_alloc_request()`, sets failfast transport, records per-I/O path/size, and calls selector `start_io()`. Bio-based mapping stores original bio details, remaps `bi_bdev`, sets failfast transport, queues bios internally while no path or PG init is pending, and resubmits queued bios from `kmultipathd`.

## Queueing And No-Path Handling

If no usable path exists, `queue_if_no_path` decides whether I/O is queued/requeued or failed. A module parameter, `queue_if_no_path_timeout_secs`, can turn queue-if-no-path off after a timeout and fail queued I/O. During noflush suspend, request-based paths can push I/O back to DM core; bio-based handling keeps an internal queued bio list.

`process_queued_io_list()` kicks the DM request requeue list or schedules queued bio processing depending on queue mode.

## Constructor And Table Syntax

Constructor parsing follows:

`<#feature args> [features...] <#hw_handler args> [handler...] <#priority groups> <initial pg> [<selector> <#selector args> ... <#paths> <#per-path selector args> [<path> args...]...]`

Feature arguments include `queue_if_no_path`, `retain_attached_hw_handler`, `pg_init_retries`, `pg_init_delay_msecs`, and `queue_mode bio|rq|mq`. Bio-based mode rejects explicit hardware-handler arguments and retains any attached handler. Paths are opened with `dm_get_device()`, SCSI device handlers are attached or retained, and each path is passed to the priority group’s selector.

## Path Failure, Reinstatement, And PG Init

`fail_path()` moves a path out of selector use, marks it inactive, decrements valid path count, clears it if current, emits a path-failed uevent, triggers a table event, and enables no-path timeout when appropriate. `reinstate_path()` calls the selector, marks the path active, increments valid path count, wakes queues when the first path returns, may activate a current-group path through the handler workqueue, emits a path-reinstated uevent, and disables the no-path timer when active.

SCSI handler activation runs on `kmpath_handlerd`. `pg_init_done()` handles handler outcomes: success clears queueing, `NOSYS` may fail the path, temporary busy bypasses the group, retry errors respect retry/delay limits, and offline/default errors fail the path. It drains queued I/O and wakes suspend waiters once all PG init work completes.

## Runtime Messages And Status

Supported messages include `queue_if_no_path`, `fail_if_no_path`, `disable_group <n>`, `enable_group <n>`, `switch_group <n>`, `reinstate_path <dev>`, and `fail_path <dev>`. Messages are rejected while the target is suspended.

Status output reports feature state, handler state, priority groups, active/failed paths, fail counts, and selector-specific status. IMA status emits key-value fields for target version, group states, path names, active flags, fail counts, and selector status.

## Suspend, Ioctl, Busy, And Module Lifecycle

Presuspend disables queue-if-no-path for flush suspend, saving old state. Postsuspend flushes activation, queued bio, and event work. Resume restores saved queue-if-no-path. Ioctl passthrough selects a usable path and returns `-ENOTCONN` while path init or no-path queueing prevents a stable backing device.

`multipath_busy()` reports busy only when I/O can be mapped but the expected underlying active paths are busy; it avoids calling path selection from busy checks. Module init creates `kmpathd` and ordered `kmpath_handlerd` workqueues before registering the target.

## Invariants And Risks

- Path selector callbacks and multipath valid-path counts must remain consistent on fail/reinstate.
- `QUEUE_IO` gates mapping while hardware-handler PG activation is required.
- Queue-if-no-path state is altered during suspend/resume and by messages; saved state can be intentionally cleared by `fail_if_no_path`.
- Workqueue flushing and PG init disabling prevent teardown racing handler callbacks.
- Bio-based mode must restore original bio details before remapping queued bios.
- Status and message paths depend on stable priority-group numbering from constructor order.

## Test Focus

Test constructor grammar, feature combinations, bio versus request queue mode, no-path queue and timeout behavior, path fail/reinstate messages, group switch/disable/enable, SCSI handler retain/attach/parameter errors, PG init retry and delayed retry cases, suspend/resume queue-if-no-path restoration, ioctl behavior during no path and PG init, queued bio replay, request clone allocation failures, and selector callback accounting on error completions.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-mpath.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-mpath.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-mpath.h

## Purpose

`dm-mpath.h` defines the small public interface shared by the multipath target and path selectors.

## API

`struct dm_path` contains a read-only `struct dm_dev *dev` for the underlying path and an opaque `void *pscontext` reserved for the active path selector. Selectors use `pscontext` to attach per-path state such as list nodes, counters, throughput data, CPU masks, or historical latency statistics.

The header also declares `dm_pg_init_complete(struct dm_path *path, unsigned err_flags)`, a completion callback interface for hardware path-group initialization users.

## Invariants And Risks

- `dev` ownership remains with the multipath target; selectors must not release it.
- `pscontext` has exactly one owner: the selector instance that accepted the path.
- Selectors must clear/free any `pscontext` allocations in their destroy path.

## Test Focus

Check selector add/fail/reinstate/destroy paths for correct `pscontext` lifetime and ensure no selector assumes more than the two fields exported in `dm_path`.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-mpath.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-path-selector.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-path-selector.c

## Purpose

`dm-path-selector.c` implements registration, lookup, module reference management, and unregister for multipath path selector types.

## Registry

The registry stores private `ps_internal` wrappers containing a copied `path_selector_type` and a list node. `_path_selectors` is protected by `_ps_lock`, an rwsem. Lookup compares selector names. `dm_register_path_selector()` copies the provided type, rejects duplicates with `-EEXIST`, and inserts it under the write lock. `dm_unregister_path_selector()` removes the registered copy and frees it.

## Lookup And Module Loading

`dm_get_path_selector()` first looks up the selector and attempts `try_module_get()` under the read lock. If not found, it requests module `dm-<name>` and retries. `dm_put_path_selector()` finds the registered selector by name and drops the module reference if it is still registered.

## Invariants And Risks

- Registered selector structs are copied, so later mutation of the caller’s static `path_selector_type` is not reflected.
- Module references are taken only for found registered selectors.
- Unregister frees the internal copy; callers must not retain stale selector pointers beyond the get/put contract.
- The name string itself is copied only as a pointer inside the struct copy, so selector modules must keep names static or otherwise stable.

## Test Focus

Test duplicate registration, unregister of missing selectors, autoload success/failure, get/put around concurrent unregister, module reference balancing, and selectors with stable static name storage.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-path-selector.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-path-selector.h -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-path-selector.h

## Purpose

`dm-path-selector.h` defines the path selector interface consumed by `dm-mpath.c` and implemented by selector modules.

## Interface

`struct path_selector` stores a selector type pointer and selector-private context. `struct path_selector_type` supplies the selector name, module, table/info argument counts, constructor/destructor, path registration, path selection, failure/reinstate hooks, status hook, and optional `start_io`/`end_io` accounting callbacks.

The multipath target calls `create()` per priority group, `add_path()` for each path, `select_path()` for mapping, `fail_path()` and `reinstate_path()` on path state changes, `status()` during table/info/IMA reporting, and `start_io()`/`end_io()` around completed mapped I/O when provided.

## Contract

`add_path()` receives selector-specific path arguments and must set `path->pscontext` if it needs per-path state. `select_path()` returns a usable `dm_path` or `NULL` if none are available. `status()` must support being called with `path == NULL` to report selector-level arguments/status.

## Invariants And Risks

- `table_args` and `info_args` must match status output expected by `dm-mpath.c`.
- Selectors must tolerate fail/reinstate and status calls for paths they accepted.
- `start_io()` and `end_io()` must remain balanced across normal and error completions for selectors that maintain load counters.
- Selector callbacks may run in I/O paths, so locking and allocation behavior must be conservative.

## Test Focus

Validate each selector’s table/info argument counts, `path == NULL` status behavior, callback balance under requeue/error completion, and per-path context lifetime.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-path-selector.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-historical-service-time.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-historical-service-time.c

## Purpose

`dm-ps-historical-service-time.c` implements the `historical-service-time` multipath selector. It estimates future service time from a time-weighted exponential moving average of completed I/O service times plus outstanding request counts, with stale-path probing logic.

## State And Parameters

The selector tracks valid and failed path lists, valid path count, precomputed EMA weights, and a `threshold_multiplier`. Each path stores a spinlock, historical service time in fixed-point units, `stale_after`, `last_finish`, and outstanding request count.

Selector constructor arguments are optional `[<base_weight> [<threshold_multiplier>]]`. `base_weight` is a 10-bit fixed-point EMA base below 1024, defaulting to 0.95. Weights are precomputed for 64 time buckets of roughly 16 ms each. `threshold_multiplier` suppresses latency comparison when paths are considered too close.

## Selection Algorithm

`hst_select_path()` scans valid paths and chooses the best according to `hst_compare()`, then moves the chosen path to the list tail for tie spreading. The comparison first checks whether historical service times exceed the threshold. If not, it compares outstanding counts. It preferentially probes unloaded stale paths, compares estimated service time using `(1 + outstanding) * historical_service_time`, and limits stale winners to equal usage.

## I/O Accounting

`hst_start_io()` increments the path’s outstanding count. `hst_end_io()` computes service time, decrements outstanding, updates the fixed-point EMA with the precomputed weight for the observed duration, and sets `stale_after` to `last_finish + valid_count * historical_service_time`. `path_service_time()` serializes overlapping completions by using `last_finish` when the previous completion was later than this I/O’s start time.

## Failure And Status

Path failure moves the path to `failed_paths` and decrements `valid_count`; reinstatement moves it back and increments `valid_count`. Selector-level status reports the first weight and threshold multiplier. Per-path info reports historical service time, outstanding count, and stale deadline; table output emits a placeholder `0` per path.

## Invariants And Risks

- Per-path stats are protected by the path’s lock; path-list membership and valid count are protected by the selector lock.
- `valid_count` directly affects stale deadlines, so fail/reinstate balance matters.
- Fixed-point math clamps service-time input to avoid overflow, and high outstanding counts shift values before multiplication.
- Clock-domain assumptions matter because selection compares current time with stale deadlines set during completion.
- `repeat_count` is parsed and stored but table status emits `0`, unlike older selectors that preserve the argument.

## Test Focus

Test base weight validation, threshold behavior, stale unloaded path probing, degraded stale path limiting, outstanding count balance on errors/requeues, fail/reinstate valid count, overflow boundaries for huge service times/outstanding counts, status/table output, and clock behavior for stale detection.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-historical-service-time.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-io-affinity.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-io-affinity.c

## Purpose

`dm-ps-io-affinity.c` implements the `io-affinity` multipath selector. It chooses paths according to the CPU currently issuing I/O, with NUMA-local and any-valid fallback.

## State And Path Mapping

The selector owns a `path_map` array indexed by CPU, a `path_mask` of CPUs with mappings, and a `map_misses` counter. Each path has a `dm_path`, cpumask, refcount, and failed flag.

Each path requires exactly one cpumask argument. `ioa_add_path()` parses it, assigns unmapped CPUs to the path, warns about duplicate CPU mappings, ignores CPU IDs beyond `nr_cpu_ids`, and uses a refcount to free a path only after all CPU mappings referencing it are released.

## Selection Algorithm

`ioa_select_path()` pins the current CPU with `get_cpu()`, tries that CPU’s mapped path if present and not failed, increments `map_misses` on absent direct mapping, then searches paths mapped to the local NUMA node, then any mapped path in `path_mask`. It returns `NULL` if all mapped paths are failed or absent.

## Failure And Status

Failure and reinstatement toggle the path’s `failed` flag. Per-path table status prints the path cpumask. Per-path info status reports the global `map_misses` counter. Selector-level status reports no selector arguments.

## Invariants And Risks

- CPU-to-path mappings are static after construction; duplicate mappings keep the first path.
- Failed paths remain in `path_map` but are skipped at selection time.
- `path_mask` and `path_map` are freed by walking mapped CPUs and refcounting shared path objects.
- The failed flag is a simple boolean and selection is lockless, so tests should consider concurrent fail/reinstate visibility.
- A path with a cpumask that adds no valid new CPU mappings is rejected.

## Test Focus

Test cpumask parsing, duplicate CPU mappings, out-of-range CPUs, no valid CPU mappings, selection on mapped CPU, local-node fallback, global fallback, all paths failed returning `NULL`, map miss accounting, and destroy refcount cleanup for multi-CPU paths.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-io-affinity.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-queue-length.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-queue-length.c

## Purpose

`dm-ps-queue-length.c` implements the `queue-length` multipath selector. It chooses the currently valid path with the fewest in-flight I/Os.

## State And Arguments

The selector maintains `valid_paths` and `failed_paths` under a spinlock. Each path stores a `dm_path`, repeat count, and atomic `qlen` in-flight I/O count. Path arguments are optional `[<repeat_count>]`; values greater than 1 are deprecated and coerced to 1.

## Selection And Accounting

`ql_select_path()` scans valid paths for the smallest `qlen`, stops early when it finds a zero-load path, moves the selected path to the tail for even balancing, and returns its `dm_path`. `ql_start_io()` increments the selected path’s `qlen`; `ql_end_io()` decrements it.

## Failure And Status

Failure moves a path to `failed_paths`; reinstatement moves it back to the valid list tail. Selector-level status emits `0`. Per-path info status reports current queue length, and table status reports repeat count. The selector registers as `queue-length` with one table arg and one info arg.

## Invariants And Risks

- `start_io()` and `end_io()` must remain balanced or `qlen` will bias future selection.
- List membership changes are locked; per-path load uses atomics for low-cost I/O updates.
- Reinstated paths retain their queue-length counter.
- Repeat count is kept only for compatibility and coerced to one.

## Test Focus

Test path argument parsing, repeat-count deprecation, least-queue selection, tie balancing via list rotation, start/end balance on success and error completions, fail/reinstate list movement, empty valid list returning `NULL`, and status output.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-queue-length.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-round-robin.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-round-robin.c

## Purpose

`dm-ps-round-robin.c` implements the `round-robin` multipath selector. It distributes I/O by rotating through valid paths.

## State And Arguments

The selector owns `valid_paths` and `invalid_paths` lists protected by a spinlock. Each path has a `path_info` containing its `dm_path` and repeat count. Path arguments are optional `[<repeat_count>]`; repeat counts greater than 1 are deprecated and forced to 1.

## Selection And Failure Handling

`rr_select_path()` returns the first valid path and moves it to the tail, producing round-robin rotation. If no valid path exists, it returns `NULL`. `rr_fail_path()` moves the path to `invalid_paths`; `rr_reinstate_path()` moves it back to `valid_paths`.

## Status And Registration

Selector-level status emits `0`. Per-path table status emits repeat count; info status emits no per-path data. The module registers `round-robin` with one table arg and zero info args.

## Invariants And Risks

- The valid list order is the scheduling state.
- Fail/reinstate must move the selector’s existing `path_info`, not allocate a replacement.
- Repeat count is compatibility-only in this implementation.
- Empty valid lists are expected and signal no selector-available path to `dm-mpath`.

## Test Focus

Test optional repeat-count parsing, deprecated repeat coercion, rotation order, fail/reinstate ordering, empty valid list behavior, destroy freeing both lists, and table/info status formatting.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-round-robin.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-service-time.c -->
# File Research: sources/block-storage/linux-dm/drivers/md/dm-ps-service-time.c

## Purpose

`dm-ps-service-time.c` implements the `service-time` multipath selector. It estimates the best path by comparing current in-flight byte load adjusted by each path’s relative throughput.

## State And Arguments

The selector keeps valid and failed path lists under a spinlock. Each path stores `dm_path`, repeat count, relative throughput, and atomic in-flight byte count. Path arguments are `[<repeat_count> [<relative_throughput>]]`; repeat counts greater than 1 are deprecated and forced to 1. Relative throughput defaults to 1 and must be between 0 and 100. A throughput of 0 means the path is avoided while any positive-throughput path is available.

## Selection And Accounting

`st_select_path()` scans valid paths and chooses the path with the lowest estimated service time. `st_compare_load()` compares `(in_flight_size + incoming) / relative_throughput` without division by cross-multiplying, with overflow avoidance for very large in-flight sizes. Equal estimates prefer higher throughput. The selected path is moved to the tail for balancing.

`st_start_io()` atomically adds request size to the path’s in-flight byte count; `st_end_io()` subtracts it.

## Failure And Status

Failure moves a path to `failed_paths`; reinstatement moves it back to the valid tail. Selector-level status emits `0`. Per-path info reports in-flight byte count and relative throughput; table status reports repeat count and relative throughput. The selector registers as `service-time` with two table args and two info args.

## Invariants And Risks

- Byte-count accounting depends on balanced `start_io()`/`end_io()` calls.
- Cross-multiplication depends on overflow guard shifting when in-flight size is large.
- Relative throughput zero is valid but deprioritized.
- Reinstated paths retain their in-flight byte counter and throughput.
- `atomic_t` stores byte counts, so very large or long-lived accounting should be checked against platform integer width.

## Test Focus

Test argument bounds, throughput-zero behavior, equal-throughput least-load behavior, higher-throughput tie breaking, overflow guard paths, list rotation, start/end byte accounting, fail/reinstate movement, empty valid list behavior, and table/info status.
<!-- END FILE RESEARCH: sources/block-storage/linux-dm/drivers/md/dm-ps-service-time.c -->