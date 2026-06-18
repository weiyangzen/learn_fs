# `sources/distributed-fs/ceph-client/drivers/s390/scsi/zfcp_erp.c`

## Purpose

`zfcp_erp.c` implements zfcp Error Recovery Procedures. It is the recovery state machine for adapters, FC ports, and LUNs. It blocks targets, chooses the minimal required recovery severity, queues one embedded ERP action per target, drives FSF close/open/exchange commands, handles timeouts and low-memory retries, propagates common status bits, and re-enables SCSI transport objects after successful recovery.

## Important APIs And Functions

- Public recovery entry points:
  - `zfcp_erp_adapter_reopen()`, `zfcp_erp_adapter_shutdown()`, and `zfcp_erp_adapter_reset_sync()`.
  - `zfcp_erp_port_reopen()`, `zfcp_erp_port_forced_reopen()`, `zfcp_erp_port_shutdown()`, and `zfcp_erp_port_forced_reopen_all()`.
  - `zfcp_erp_lun_reopen()`, `zfcp_erp_lun_shutdown()`, and `zfcp_erp_lun_shutdown_wait()`.
  - `zfcp_erp_port_forced_no_port_dbf()` records recovery need when no `zfcp_port` object exists.
- ERP queue/thread APIs:
  - `zfcp_erp_thread_setup()`, `zfcp_erp_thread_kill()`, and `zfcp_erp_wait()`.
  - `zfcp_erp_notify()` moves a running action back to ready after FSF completion or timeout.
  - `zfcp_erp_timeout_handler()` is used by ERP-owned FSF request timers.
- Status APIs:
  - `zfcp_erp_set_adapter_status()` / `clear_adapter_status()` propagate common bits to ports and SCSI devices.
  - `zfcp_erp_set_port_status()` / `clear_port_status()` propagate common bits to child SCSI devices.
  - `zfcp_erp_set_lun_status()` / `clear_lun_status()` mutate per-SCSI-device zfcp status.
- Core selection/setup:
  - `zfcp_erp_required_act()` escalates requested LUN/port actions to a parent action when parent state is blocked.
  - `zfcp_erp_handle_failed()` suppresses new recovery for targets already marked ERP failed.
  - `zfcp_erp_setup_act()` takes object references, marks `ERP_INUSE`, initializes the embedded action, and notes close-only mode when target is not running.
  - `zfcp_erp_action_enqueue()` inserts into `erp_ready_head`, sets adapter pending status, and emits recovery trigger traces.
- Strategy functions:
  - Adapter strategy closes QDIO/requests/WKA ports, opens QDIO, exchanges config and port data, registers SCSI host, resizes status-read pools, posts status reads, and schedules port scans/name updates.
  - Port strategy closes/open ports, triggers GID_PN lookup when D_ID is missing, handles point-to-point peer ports, and can force physical close.
  - LUN strategy closes/open LUNs and clears access-denied status before reopen.

## Control Flow

Recovery starts when another subsystem detects a fault and calls a public reopen/shutdown entry. The target is blocked by clearing `UNBLOCKED` and optional clear masks, SCSI rports are scheduled blocked for adapter/port faults, and a queued ERP action is created under `adapter->erp_lock`. The ERP thread waits on `erp_ready_wq`, picks the first ready action, and calls `zfcp_erp_strategy()`.

`zfcp_erp_strategy()` first reconciles outstanding FSF request state with `zfcp_erp_strategy_check_fsfreq()`. If dismissed or timed out, it exits or fails. Otherwise it moves the action to the running list and calls the type-specific strategy without holding the ERP lock. Type-specific strategies typically issue one asynchronous FSF command and return `ZFCP_ERP_CONTINUES`; the FSF handler later calls `zfcp_erp_notify()`, which moves the action back to the ready queue. When a strategy returns final success/failure/exit, the result is checked against target counters, state-change races, and follow-up rules. Success at adapter level schedules port recovery; success at port level schedules child LUN recovery.

Adapter reopen has the richest flow: close existing queues if open, dismiss all outstanding FSF requests, reset sequence number, force WKA ports offline, open QDIO, exchange config data with retries for host-connection-initializing, optionally exchange port data, register/update the SCSI host, set up point-to-point port, resize status-read pools, refill status reads, and mark adapter open/unblocked.

## State And Persistence

ERP uses persistent in-memory state embedded in adapter/port/SCSI-device objects:

- One `struct zfcp_erp_action` per adapter, port, and SCSI device.
- `erp_ready_head` and `erp_running_head` lists per adapter.
- Wait queues for ready actions and overall ERP completion.
- Status bits for running/open/unblocked/failed/in-use/access states.
- Retry counters per adapter/port/LUN, capped by `ZFCP_MAX_ERPS`.
- `erp_total_count` and `erp_low_mem_count` to detect all-active low-memory stalls.
- FSF request id in the ERP action to reconcile outstanding asynchronous commands.

References are held for adapters (`kref_get`), ports (`get_device`), and SCSI devices (`scsi_device_get`) while actions are active, except the explicit no-reference shutdown-wait path.

## Dependencies And Integration

ERP depends on FSF command APIs for all hardware recovery operations, QDIO close/open, request-list lookup for outstanding FSF requests, diagnostic cache data for delayed SCSI host updates, FC port discovery/link scan/name update logic, SCSI rport block/register scheduling, service-level registration, mempool resizing, kernel threads, timers, wait queues, and debug tracing.

ERP is the integration point for errors reported by QDIO, FSF status/protocol evaluation, FC link events, SCSI error handling, sysfs removal, and adapter teardown.

## Risks And Edge Cases

- Locking is delicate: `erp_lock`, `port_list_lock`, `host_lock`, request-list lock, and FSF timers interact. New code must not sleep while holding spin/rw locks except through the established wait macros that release locks.
- Embedded action objects mean only one ERP action per target can be active; overlapping child actions are dismissed when parent recovery starts.
- FSF request pointers can complete concurrently. ERP stores only request ids and uses request-list locking to avoid use-after-free.
- Low-memory handling can escalate to adapter reopen if all actions are stuck in low-memory state.
- `zfcp_erp_lun_shutdown_wait()` intentionally skips `scsi_device_get()`; correctness depends on waiting for ERP completion before the SCSI device disappears.
- State-change detection can enqueue new actions if running/close-only intent changed while an action was executing.
- Adapter exchange-config incomplete data intentionally avoids full shutdown so link-up events can still be recognized.

## Test Signals

Key signals include:

- Requested recovery escalates correctly: LUN recovery to port/adapter when parents are blocked, forced port close before normal port open, adapter recovery dismissing children.
- ERP action lists transition ready -> running -> ready/final without leaks, and `ZFCP_STATUS_ADAPTER_ERP_PENDING` clears when both lists are empty.
- FSF timeout marks action timed out and leads to request dismissal/recovery retry.
- After more than `ZFCP_MAX_ERPS` failures, adapter/port/LUN is marked `ERP_FAILED` and remains blocked.
- Successful adapter recovery reopens QDIO, posts status reads, registers service level, schedules port scan, and updates symbolic name.
- Successful port/LUN recovery unblocks rport only after non-failed child LUNs are unblocked and no newer ERP is active.
