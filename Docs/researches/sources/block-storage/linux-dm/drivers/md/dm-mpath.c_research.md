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
