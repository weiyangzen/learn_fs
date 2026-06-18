# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/cmd.c

## Purpose

`cmd.c` implements the mlx5 firmware command interface. It allocates command descriptors and mailbox chains, serializes work through command slots, rings the device command doorbell, handles completions by event or polling, translates delivery and firmware status into Linux errors, exposes debugfs command injection helpers, manages async command contexts, and initializes/disables the command queue.

## Important APIs, Types, And Functions

Command submission and status:

- `mlx5_cmd_do()`: executes a command and returns `-EREMOTEIO` when firmware executed the command but outbox status is non-OK.
- `mlx5_cmd_exec()` and `mlx5_cmd_exec_polling()`: execute and normalize status through `mlx5_cmd_check()`.
- `mlx5_cmd_exec_cb()`: asynchronous command execution with callback and inflight accounting.
- `mlx5_cmd_check()`, `cmd_status_err()`, `cmd_status_to_err()`, `deliv_status_to_err()`: error/status translation.
- `mlx5_cmd_out_err()` and trace helpers log firmware failures.

Command engine:

- `cmd_alloc_ent()`, `cmd_ent_get()`, `cmd_ent_put()`: command work entry lifecycle and slot release.
- `cmd_alloc_index()` / `cmd_free_index()`: command slot bitmap management.
- `cmd_work_handler()`: builds a descriptor, copies mailbox data, schedules timeout work, rings the doorbell, and optionally polls.
- `mlx5_cmd_comp_handler()`: handles real or forced completions, copies output, verifies signatures, runs callbacks, frees messages, and completes waiters.
- `wait_func()` and `wait_func_handle_exec_timeout()`: blocking wait and EQ recovery on timeout.
- `mlx5_cmd_flush()` and `mlx5_cmd_trigger_completions()`: force completion of pending commands during teardown/reset.

Mailbox and caches:

- `mlx5_alloc_cmd_msg()`, `mlx5_free_cmd_msg()`, `alloc_cmd_box()`, `free_cmd_box()`: command message/mailbox chain allocation.
- `mlx5_copy_to_msg()` / `mlx5_copy_from_msg()`: linear buffer to/from command message chains.
- `create_msg_cache()` / `destroy_msg_cache()` and `alloc_msg()`: reusable input-message caches for common sizes.

Initialization and mode:

- `mlx5_cmd_init()` / `mlx5_cmd_cleanup()`: command workqueue and command debugfs scaffolding.
- `mlx5_cmd_enable()` / `mlx5_cmd_disable()`: command interface page, DMA pool, semaphores, caches, debugfs, and firmware queue address.
- `mlx5_cmd_use_events()` / `mlx5_cmd_use_polling()`: switch between EQ completion and polling modes.
- `mlx5_cmd_set_state()`, `mlx5_cmd_is_down()`, and `mlx5_cmd_allowed_opcode()`: state and gating.
- `mlx5_cmd_add_privileged_uid()` / `mlx5_cmd_remove_privileged_uid()`: privileged UID throttling exceptions.

Helper commands:

- `mlx5_cmd_allow_other_vhca_access()`, `mlx5_cmd_alias_obj_create()`, and `mlx5_cmd_alias_obj_destroy()` build specific general-object/access commands on top of the command interface.

## Control Flow

For synchronous commands, `cmd_exec()` checks device state/opcode gating, optionally takes a throttle or unprivileged semaphore, allocates input/output command messages, assigns a token, copies input data, and calls `mlx5_cmd_invoke()`. `mlx5_cmd_invoke()` creates a work entry, queues `cmd_work_handler()` on the command workqueue unless it is the page queue, then waits through `wait_func()`.

`cmd_work_handler()` takes a regular command slot semaphore or the special manage-pages semaphore, allocates an index, fills `struct mlx5_cmd_layout`, sets owner to hardware, calculates signatures if enabled, records timestamps, schedules async timeout work when needed, marks the entry pending completion, and rings `dev->iseg->cmd_dbell`. In polling mode it waits for the owner bit to return to software and directly invokes the completion handler.

Completions arrive through `cmd_comp_notifier()` when event mode is enabled or are forced during timeout/reset. `mlx5_cmd_comp_handler()` walks the completion vector, ignores duplicate/late completions appropriately, cancels async timeout work, copies out the descriptor data, validates signatures, stores delivery status, updates stats, releases command slots, and either calls the async callback or completes the synchronous waiter.

Initialization is split: `mlx5_cmd_init()` creates the workqueue, while `mlx5_cmd_enable()` validates command interface revision, reads queue sizing from the initialization segment, creates semaphores and the DMA pool, allocates an aligned command page, programs its DMA address to the device, initializes caches/debugfs, and starts in polling mode.

## State And Persistence Behavior

Runtime state is held in `dev->cmd`: command mode, command-interface state, slot bitmask, semaphores, workqueue, DMA pool, command descriptor page, entry array, token counter, mailbox caches, debugfs buffers, xarray of privileged UIDs, stats xarray, and notifier. Command state is volatile and rebuilt on device enable. Debugfs `in`, `out`, `out_len`, `status`, and `run` files expose temporary buffers only.

The code tracks stalled entries with `MLX5_CMD_ENT_STATE_PENDING_COMP` and `MLX5_CMD_ENT_STATE_TIMEDOUT`. Timed-out commands can intentionally leak a command resource until a late real completion arrives, avoiding reuse of a slot still owned by firmware.

## Dependencies And Integration Points

The command engine integrates with PCI MMIO (`dev->iseg` doorbell and queue address registers), DMA pools, workqueues, completions, semaphores, xarrays, debugfs, mlx5 EQ notifier infrastructure, timeout policy from `lib/tout`, tracepoints from `diag/cmd_tracepoint.h`, and the wider mlx5 driver through exported command functions. Almost every mlx5 object-management file depends on this interface.

## Risks

- Timeout handling is deliberately complex. Forced completions, late real completions, refcounts, and slot bitmaps must stay balanced to avoid use-after-free, leaked slots, or reusing firmware-owned descriptors.
- Async callbacks cannot sleep and may free their `mlx5_async_work`; the handler correctly avoids touching `work` after user callback, but future edits must preserve that rule.
- `mlx5_cmd_allowed_opcode()` and mode changes drain all semaphores; misuse can block command progress globally.
- Debugfs command injection accepts raw command buffers and should remain restricted to debugfs permissions and trusted users.
- Throttling and privileged UID semaphores protect command queue saturation; bypassing them for high-volume opcodes can stall the device.
- Signature/checksum code is present but `checksum_disabled` is initialized to `1` in this snapshot, so checksum coverage is disabled unless changed elsewhere.

## Test Signals

High-value tests include command success/failure status translation, mailbox sizes crossing cache thresholds, async callback cleanup, forced polling during teardown, event completion mode, timeout/EQ recovery, late completion after timeout, PCI/internal-error state returning synthetic statuses, all-slots-stalled rejection, manage-pages special queue behavior, privileged UID throttling, and debugfs command paths. Lockdep, KASAN/KCSAN, fault injection for DMA/mailbox allocation, and tracepoint/stat checks are useful.
