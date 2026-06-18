# sources/distributed-fs/ceph-client/drivers/scsi/scsi_debug.c lines 8969-9701

## Scope

This chunk covers the lower-level SCSI host-template entry points and command-dispatch path for the `scsi_debug` pseudo low-level driver. It includes queue-depth adjustment, synthetic timeout/not-ready behavior, blk-mq queue mapping and polling, debugfs-driven error injection checks, reserved internal abort-command handling, the main `.queuecommand` dispatcher, per-command private initialization, host template registration, and pseudo-bus probe/remove.

## Purpose and integration role

The code in this range is where the driver binds its emulated device state to the SCSI mid-layer:

- `sdebug_driver_template` exports callbacks to the SCSI core, including `.queuecommand`, `.queue_reserved_command`, `.change_queue_depth`, `.map_queues`, `.mq_poll`, error handlers, target lifecycle, and command-private setup.
- `sdebug_driver_probe()` allocates a `Scsi_Host`, configures queue topology and protection capabilities from module/runtime knobs, registers it with `scsi_add_host()`, and starts discovery via `scsi_scan_host()`.
- `sdebug_driver_remove()` tears down the SCSI host and frees per-device emulation state hanging from `sdebug_host_info::dev_info_list`.
- `pseudo_lld_bus` connects those probe/remove hooks to the driver's pseudo bus and exposes driver attribute groups through `sdebug_drv_groups`.

The central runtime path is `scsi_debug_queuecommand()`, which validates the request, locates/creates the emulated LUN state, applies configured failure/timeout injection, resolves the command's opcode metadata, handles unit attention and stopped/not-ready device state, then calls `schedule_resp()` to execute a `resp_*()` handler and complete the command immediately, through workqueue/hrtimer, or through blk-mq polling.

## Important APIs, types, and functions

- `sdebug_change_qdepth(struct scsi_device *sdev, int qdepth)` clamps requested depth to `[1, SDEBUG_CANQUEUE]`, blocks all queues under `sdebug_host_list_mutex`, calls `scsi_change_queue_depth()`, then unblocks queues. It returns the effective `sdev->queue_depth`.
- `fake_timeout(struct scsi_cmnd *scp)` implements the `sdebug_every_nth` synthetic timeout cadence. Depending on `SDEBUG_OPT_TIMEOUT` or `SDEBUG_OPT_MAC_TIMEOUT`, selected commands are intentionally left incomplete.
- `resp_not_ready(struct scsi_cmnd *scp, struct sdebug_dev_info *devip)` returns SCSI NOT READY sense for TEST UNIT READY and medium-access commands while `devip->stopped` is set. For `stopped == 2`, it uses `devip->create_ts` and `sdeb_tur_ms_to_ready` to model a device becoming ready and reports remaining milliseconds in the sense information field for TEST UNIT READY.
- `sdebug_map_queues(struct Scsi_Host *shost)` programs blk-mq maps for default and poll hardware contexts. It assigns `submit_queues - poll_queues` queues to `HCTX_TYPE_DEFAULT`, `poll_queues` to `HCTX_TYPE_POLL`, and calls `blk_mq_map_queues()`.
- `struct sdebug_blk_mq_poll_data` carries the target poll queue and completion count into `blk_mq_tagset_busy_iter()`.
- `sdebug_blk_mq_poll_iter()` scans busy requests, filters by hardware queue and inflight state, checks `struct sdebug_defer` for `SDEB_DEFER_POLL` and an expired `cmpl_ts`, then calls `scsi_done()` and increments completion statistics.
- `sdebug_blk_mq_poll()` is the `.mq_poll` callback. It iterates the tag set, returns the number of commands completed, and accumulates `sdeb_mq_poll_count`.
- `sdebug_timeout_cmd()`, `sdebug_fail_queue_cmd()`, and `sdebug_fail_cmd()` consult `sdebug_dev_info::inject_err_list` under RCU for per-opcode error injection entries. They implement, respectively, silent timeout, nonzero `.queuecommand` return, and successful queueing with synthetic sense/result status.
- `scsi_debug_abort_cmd()` handles a reserved internal command by finding the command with `scsi_host_find_tag()`, locking its `sdebug_scsi_cmd`, calling `scsi_debug_stop_cmnd()`, and setting the reserved command's host byte to `DID_OK` or `DID_ERROR`.
- `scsi_debug_process_reserved_command()` is the `.queue_reserved_command` hook and currently dispatches only `SCSI_DEBUG_ABORT_CMD`.
- `scsi_debug_queuecommand()` is the SCSI command ingress hook. It ties together CDB logging, LUN validation, opcode lookup through `opcode_ind_arr`/`opcode_info_arr`, unit-attention handling, stopped-device handling, fake read/write bypass, failure injection, command response selection, and delayed completion scheduling.
- `sdebug_init_cmd_priv()` initializes `struct sdebug_scsi_cmd` private data for normal requests: spinlock, hrtimer callback, and workqueue completion object. Reserved requests are skipped because their private area is interpreted as `struct sdebug_internal_cmd`.
- `sdebug_driver_probe()` and `sdebug_driver_remove()` are pseudo-bus lifecycle functions.

Key cross-chunk types used here include `struct sdebug_dev_info` for per-emulated-LUN state, `struct sdebug_err_inject` for debugfs-configured injected behavior, `struct sdebug_defer`/`struct sdebug_scsi_cmd` for deferred completion state, `union sdebug_priv` for command-private memory, and `struct opcode_info_t` for opcode metadata and response function selection.

## Control flow

### Queue-depth changes

`sdebug_change_qdepth()` first requires `sdev->hostdata` to exist. It serializes with `sdebug_host_list_mutex`, calls `block_unblock_all_queues(true)`, clamps the requested depth, updates the SCSI device if needed, then unblocks queues. The explicit block/unblock step makes the depth change global with respect to active debug-host queues rather than just a local field update.

### Command dispatch

`scsi_debug_queuecommand()` performs these steps:

1. Reset residual count with `scsi_set_resid(scp, 0)`.
2. If statistics are enabled, increment `sdebug_cmnd_count` and compute `inject_now`; optionally return `SCSI_MLQUEUE_HOST_BUSY` for host-busy injection.
3. Reject out-of-range normal LUNs, while allowing the REPORT LUNS well-known LUN (`SCSI_W_LUN_REPORT_LUNS`).
4. Resolve opcode metadata from `opcode_ind_arr[opcode]` into `opcode_info_arr`.
5. Load `sdp->hostdata`; lazily call `find_build_dev_info()` if the emulated device state does not exist.
6. Apply debugfs error-injection hooks in priority order: silent timeout, failed queuecommand return, then queued command with injected sense/status.
7. Mark `sdeb_inject_pending` for option-driven one-shot failures.
8. If the opcode has attached variants, resolve by service action or opcode plus device selector. On no match, build invalid-field or invalid-opcode sense.
9. Reject invalid-opcode metadata, unsupported well-known-LUN commands, or strict CDB mask violations.
10. If applicable, synthesize unit-attention sense through `make_ua()`.
11. For medium access or TEST UNIT READY while the device is stopped, call `resp_not_ready()`.
12. If `sdebug_fake_rw` and the opcode is flagged `F_FAKE_RW`, skip the command handler and complete success through `schedule_resp()`.
13. Apply periodic fake timeout through `fake_timeout()`.
14. Select the leaf response handler `oip->pfp` or fall back to the root opcode handler.
15. Schedule completion. `F_DELAY_OVERR` forces immediate response; `F_LONG_DELAY` computes a longer SSU/synchronize-cache style delay; other commands use global `sdebug_jdelay`/`sdebug_ndelay`.

The `check_cond` path schedules `check_condition_result` without invoking a response handler. The `err_out` path schedules `DID_NO_CONNECT`.

### Polling and deferred completions

This chunk's polling path complements `schedule_resp()` from an earlier chunk. `schedule_resp()` stores `SDEB_DEFER_POLL` and a boot-time completion timestamp for polled requests; `sdebug_blk_mq_poll()` later walks busy tags and completes only matching hardware queue entries whose timestamp has expired. Non-polled delayed requests use the hrtimer/workqueue setup initialized by `sdebug_init_cmd_priv()`.

The poll iterator intentionally checks `SCMD_STATE_INFLIGHT`, `defer_t`, and `cmpl_ts` under the per-command spinlock before calling `scsi_done()`. The local comment notes that aborted polled commands are not handled in the iterator because the surrounding scheduling path is expected not to create that state.

### Reserved abort command flow

Abort handling is split across chunks. Earlier code allocates an internal reserved SCSI command containing `SCSI_DEBUG_ABORT_CMD` and the target request's unique tag. In this chunk, `scsi_debug_process_reserved_command()` receives that reserved command, calls `scsi_debug_abort_cmd()`, and completes the reserved command with `scsi_done()`. `scsi_debug_abort_cmd()` uses `scsi_host_find_tag()` to locate the original command and attempts to stop its deferred completion through `scsi_debug_stop_cmnd()`.

## State and persistence behavior

This code is stateful but not persistent across module unload or host removal. Important state touched here:

- `sdev->hostdata` points at `struct sdebug_dev_info`. Missing hostdata is lazily built in `scsi_debug_queuecommand()` and required by `sdebug_change_qdepth()`.
- `devip->stopped` models START STOP UNIT/device-start readiness. `resp_not_ready()` may transition it from `2` to `0` once the configured ready delay has elapsed.
- `devip->create_ts` anchors the TEST UNIT READY "becoming ready" countdown.
- `devip->uas_bm` holds pending unit attentions consumed by `make_ua()`.
- `devip->inject_err_list` is walked under RCU for command-specific error injection. Negative `cnt` values are incremented toward zero when matched, while zero disables the injection.
- `sdebug_cmnd_count`, `sdebug_completions`, `sdebug_miss_cpus`, `sdeb_inject_pending`, and `sdeb_mq_poll_count` are global atomic counters/flags used for statistics and fault injection.
- `sdebug_defer` fields (`defer_t`, `cmpl_ts`, `issuing_cpu`, `aborted`) track per-command completion mode and timing.
- `submit_queues` and `poll_queues` are mutable global configuration values; `sdebug_driver_probe()` may trim them to match CPU count and queue topology.
- `sdbg_host->shost` stores the allocated `Scsi_Host`; `sdebug_driver_remove()` removes it and frees all `sdebug_dev_info` objects and their zone state.

No on-disk persistence is introduced in this chunk. Emulated media, provisioning, zone, tape, and injection state exist in kernel memory and are freed during removal.

## Dependencies and integration points

This chunk depends heavily on Linux SCSI and block-mq infrastructure:

- SCSI mid-layer: `struct scsi_host_template`, `scsi_host_alloc()`, `scsi_add_host()`, `scsi_scan_host()`, `scsi_remove_host()`, `scsi_host_put()`, `scsi_change_queue_depth()`, `scsi_done()`, `scsi_set_resid()`, `scsi_set_sense_information()`, `scsi_host_find_tag()`, and SCSI result/status host bytes.
- blk-mq: `blk_mq_map_queues()`, `blk_mq_tagset_busy_iter()`, `blk_mq_unique_tag()`, `blk_mq_unique_tag_to_hwq()`, `blk_mq_is_reserved_rq()`, `blk_mq_rq_to_pdu()`, and `REQ_POLLED`.
- Kernel concurrency primitives: mutexes, spinlocks with IRQ save/restore, atomics, RCU list traversal, hrtimers, workqueues, and scoped lock guards.
- SCSI command metadata from earlier arrays: `opcode_ind_arr`, `opcode_info_arr`, opcode flags such as `F_M_ACCESS`, `F_FAKE_RW`, `F_DELAY_OVERR`, `F_LONG_DELAY`, `F_SYNC_DELAY`, `F_SKIP_UA`, `F_RL_WLUN_OK`, and service-action flags.
- Response handlers declared/defined elsewhere: `resp_inquiry()`, `resp_report_luns()`, read/write/tape/zone handlers, and other `resp_*()` functions selected through `opcode_info_t::pfp`.
- Sense helpers from earlier chunks: `mk_sense_buffer()`, `mk_sense_invalid_fld()`, `mk_sense_invalid_opcode()`, and `make_ua()`.
- Module and driver configuration globals: `sdebug_opts`, `sdebug_verbose`, `sdebug_statistics`, `sdebug_every_nth`, `sdebug_strict`, `sdebug_fake_rw`, `sdebug_max_luns`, `sdebug_max_queue`, `sdebug_host_max_queue`, `sdebug_clustering`, `sdebug_dif`, `sdebug_dix`, `sdebug_guard`, `sdeb_tur_ms_to_ready`, `sdebug_jdelay`, `sdebug_ndelay`, `submit_queues`, and `poll_queues`.

## Risks and correctness considerations

- `scsi_debug_abort_cmd()` assigns `to_be_aborted_sdsc = scsi_cmd_priv(to_be_aborted_scmd)` before checking whether `to_be_aborted_scmd` is NULL. If `scsi_host_find_tag()` can return NULL, this ordering is unsafe even though the subsequent NULL check logs and returns.
- Error injection list entries are located under `rcu_read_lock()`, but `sdebug_fail_cmd()` drops RCU before using `err` in `out_handle`. Correctness depends on the lifetime guarantees of the injection objects beyond the visible RCU read-side section.
- `fake_timeout()` uses `abs(sdebug_every_nth)` only when the caller has checked `sdebug_every_nth`, avoiding divide-by-zero in the normal path. Changes to that call contract would be risky.
- `sdebug_map_queues()` BUGs if the default queue map has zero queues. Probe-time trimming of `poll_queues` is therefore required to preserve at least one default queue.
- `sdebug_driver_probe()` mutates global `submit_queues` and `poll_queues`. With multiple pseudo hosts, the first probe can change settings that affect later hosts.
- Queue-depth changes block/unblock all queues while holding `sdebug_host_list_mutex`; missed unblock paths would be serious, but the current function has a single straight-line exit after blocking.
- Poll completion calls `scsi_done()` after dropping the command lock. That is normal, but relies on `defer_t`/`cmpl_ts` being enough to prevent duplicate completion from another path.
- The stopped/not-ready path returns success from `resp_not_ready()` when a startup delay expires and then falls through to normal handling. This makes TEST UNIT READY behavior time-dependent and sensitive to boot-time timestamp comparisons.
- Strict CDB checking uses `oip->len_mask[0]` capped at 16 bytes. Metadata table mistakes can cause commands to be rejected or accepted incorrectly.

## Test signals

Useful validation signals for this chunk include:

- Loading `scsi_debug` with varied `max_queue`, `submit_queues`, `poll_queues`, `host_max_queue`, `delay`, `ndelay`, and `every_nth` values and checking that host registration succeeds, queue maps are sane, and warnings appear when trimming is expected.
- Running standard SCSI discovery and I/O through the debug device to exercise `.queuecommand`, opcode lookup, response handler dispatch, and `schedule_resp()` completion.
- Enabling polled I/O (`REQ_POLLED` capable workloads) and checking that `sdeb_mq_poll_count` and command completions advance without duplicate completions.
- Using debugfs injection controls to cover `ERR_TMOUT_CMD`, `ERR_FAIL_QUEUE_CMD`, and `ERR_FAIL_CMD`, including wildcard opcode `0xff` and negative/zero/positive `cnt` behavior.
- Issuing TEST UNIT READY and medium-access commands while the device is stopped or becoming ready, verifying NOT READY sense ASC/ASCQ and TEST UNIT READY sense information countdown.
- Exercising abort/error-handler paths to ensure reserved internal commands complete and aborted delayed commands do not call `scsi_done()` twice.
- Running with `sdebug_strict=1` and malformed CDB reserved bits to verify `INVALID_FIELD_IN_CDB` sense locations.
- Removing the pseudo device/module after I/O and checking that `scsi_remove_host()`, `sdebug_dev_info` freeing, zone-state freeing, and `scsi_host_put()` leave no leaks or use-after-free reports under KASAN/KCSAN/lockdep.
