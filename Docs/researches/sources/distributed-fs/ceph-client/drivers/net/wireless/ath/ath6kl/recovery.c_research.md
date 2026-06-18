<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/recovery.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/recovery.c

## Purpose
`recovery.c` implements firmware error recovery and optional heartbeat polling. It translates endpoint-full or heartbeat failures into asynchronous hardware restart attempts and coordinates that logic with suspend/resume and driver cleanup.

## Important APIs, Types, And Functions
The core worker is `ath6kl_recovery_work()`, stored in `ar->fw_recovery.recovery_work`. Public entry points are `ath6kl_recovery_err_notify()`, `ath6kl_recovery_hb_event()`, `ath6kl_recovery_init()`, `ath6kl_recovery_cleanup()`, `ath6kl_recovery_suspend()`, and `ath6kl_recovery_resume()`. Heartbeat polling is driven by `ath6kl_recovery_hb_timer()` and WMI challenge/response commands.

## Control Flow
When an error is reported and recovery is enabled, the reason bit is recorded in `err_reason`. If cleanup is not active and the device is not already recovering, work is queued on `ar->ath6kl_wq`. The worker sets state to `ATH6KL_STATE_RECOVERY`, deletes the heartbeat timer, calls `ath6kl_init_hw_restart()`, returns state to ON, clears control endpoint full state, clears `err_reason`, and restarts heartbeat polling if configured.

Heartbeat timer ticks ignore cleanup and recovery states. Each tick checks whether the previous challenge is still pending; too many misses trigger `ATH6KL_FW_HB_RESP_FAILURE`. Otherwise it increments `seq_num`, marks a heartbeat pending, sends `ath6kl_wmi_get_challenge_resp_cmd()`, and rearms the timer. Matching heartbeat events clear `hb_pending`.

## State And Persistence
State lives in `ar->fw_recovery`: enable flag, `err_reason` bitmask, heartbeat poll interval, sequence number, miss count, pending flag, timer, and work item. The global `ar->state` and flags `RECOVERY_CLEANUP` and `WMI_CTRL_EP_FULL` are also touched. There is no persistent storage.

## Dependencies And Integration Points
This file depends on `init.c` restart, WMI challenge/response, cfg80211 stop behavior inside restart, and workqueue/timer APIs. `txrx.c` calls `ath6kl_recovery_err_notify()` when the WMI control endpoint fills.

## Risks
`ath6kl_recovery_work()` sets state back to ON even if `ath6kl_init_hw_restart()` logs failure, so later code may believe recovery succeeded. Error reasons are bit-set but cleared wholesale after the worker, which can obscure concurrent reasons. Suspend cleanup cancels work and timer, then optionally restarts inline if an error was pending; callers must ensure the device is in ON state as asserted.

## Test Signals
Useful signals include recovery debug logs, heartbeat challenge command failures, transition to and from `ATH6KL_STATE_RECOVERY`, control endpoint full clearing, timer rearm behavior, and suspend/resume with a pending `err_reason`. Fault-injection tests should simulate heartbeat misses, endpoint full, restart failure, cleanup during queued work, and resume after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/recovery.c -->
