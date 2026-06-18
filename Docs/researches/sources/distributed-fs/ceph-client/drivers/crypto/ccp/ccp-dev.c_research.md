# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev.c

## Purpose

`ccp-dev.c` is the generic CCP device core. It maintains the global list of CCP devices, exports presence/version/enqueue APIs, schedules commands onto hardware queue kthreads, handles backlog and suspend/resume, allocates base device state, registers hwrng reads, and dispatches to version-specific vdata init/destroy operations.

## Important APIs, Types, And Functions

- Module parameters `nqueues` and `max_devs` limit queues per device and number of CCP devices initialized.
- `ccp_log_error()` maps hardware error codes to readable messages.
- `ccp_add_device()`/`ccp_del_device()` maintain the global device list and round-robin pointer.
- `ccp_present()` and `ccp_version()` are exported for crypto module feature gating.
- `ccp_enqueue_cmd()` chooses a device, applies queue/backlog limits, adds commands to active/backlog lists, and wakes idle queue threads.
- `ccp_do_cmd_backlog()` moves a backlogged command into the active queue and notifies it with `-EINPROGRESS`.
- `ccp_dequeue_cmd()` is used by queue threads to fetch work or enter suspended state.
- `ccp_cmd_queue_thread()` sleeps until woken, runs `ccp_run_cmd()`, and schedules callback completion via a tasklet.
- `ccp_alloc_struct()` allocates and initializes `struct ccp_device`.
- `ccp_trng_read()` implements hwrng reads from `TRNG_OUT_REG`.
- `ccp_queues_suspended()`, `ccp_dev_suspend()`, and `ccp_dev_resume()` coordinate queue thread suspension.
- `ccp_dev_init()` and `ccp_dev_destroy()` are SP-device lifecycle hooks.

## Control Flow

Generic init enforces `max_devs`, allocates a `ccp_device`, decides max queue count from module parameter, obtains vdata from the SP device, applies vdata setup, and calls the version-specific `perform->init()`. That version-specific init starts queue threads and adds the device to the global list. Commands submitted through `ccp_enqueue_cmd()` use a specific `cmd->ccp` if provided or a round-robin device otherwise. The command is either rejected, placed on backlog, or appended to the active command list. If a queue is idle and the device is not suspending, its kthread is woken.

Queue threads dequeue commands, call `ccp_run_cmd()` to translate and execute the command via vdata operations, then invoke the command callback from a tasklet and wait for that callback to finish before processing more work. Backlogged commands are moved to active via scheduled work so the caller first receives an `-EINPROGRESS` transition.

## State And Persistence Behavior

Global state includes `ccp_units`, `ccp_unit_lock`, `ccp_rr`, `ccp_rr_lock`, and `dev_count`. Per-device state includes active/backlog command lists, command count, queue threads, hwrng state, storage block state, suspend flags, and vdata. This is all runtime kernel state. `ccp_trng_read()` keeps a retry counter to distinguish temporary zero reads from persistent entropy failure.

## Dependencies And Integration Points

This file depends on SP-device bus glue, version-specific action tables, `linux/ccp.h` exported command structures, hwrng, kthreads, tasklets, and the lower `ccp_run_cmd()` operation converter from `ccp-ops.c`. It is consumed by `ccp_crypto` and DMAengine clients through exported command enqueue APIs.

## Risks And Edge Cases

- `max_devs=0` causes `ccp_dev_init()` to return success without initializing devices; consumers then see no present CCP.
- Queue callbacks are invoked from tasklet context; callbacks must respect atomic-context constraints unless the lower stack changes this behavior.
- Round-robin device selection uses locks correctly, but commands pinned to removed devices require external lifetime guarantees.
- Suspend waits for all queue threads to mark suspended; active long-running commands can delay suspend.
- Backlog movement uses work_struct embedded in `struct ccp_cmd`, so command memory must remain valid while backlogged.

## Test Signals

Signals include exported `ccp_present()`/`ccp_version()` behavior, round-robin distribution across devices, queue cap and backlog semantics, command callbacks on success/error/removal, suspend/resume under active load, hwrng zero retry handling, and module parameters `nqueues`/`max_devs`.
