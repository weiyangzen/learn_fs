# sources/distributed-fs/ceph-client/drivers/cdx/controller/mcdi.c

## Purpose
This file implements the CDX Management-Controller-to-Driver Interface RPC engine. It serializes firmware commands, builds MCDI v2 request headers, tracks sequence numbers and command lifetimes, processes asynchronous responses, handles timeouts/cancellation, and provides synchronous and asynchronous RPC APIs.

## Important APIs, Types, and Functions
Exported APIs are `cdx_mcdi_init()`, `cdx_mcdi_finish()`, `cdx_mcdi_wait_for_quiescence()`, `cdx_mcdi_process_cmd()`, `cdx_mcdi_rpc()`, and `cdx_mcdi_rpc_async()`. Important internals include `cdx_mcdi_send_request()`, `cdx_mcdi_rpc_sync()`, `cdx_mcdi_cmd_work()`, `cdx_mcdi_complete_cmd()`, `cdx_mcdi_timeout_cmd()`, `cdx_mcdi_mode_fail()`, and `cdx_mcdi_process_cleanup_list()`.

## Control Flow
Initialization allocates `struct cdx_mcdi_iface`, creates an ordered workqueue, initializes locking and wait queues, and starts in event mode with a new epoch. Sync RPC allocates wait/completer data plus a command object, queues the command asynchronously, waits for completion with a command-specific timeout, and cancels on timeout. Command work grabs the iface mutex, assigns a handle, appends to the command list, and either starts immediately or queues behind a held doorbell/sequence. Sending builds an 8-byte v2 extended header, computes checksum into `XFLAGS`, and invokes the transport callback.

Responses enter `cdx_mcdi_process_cmd()`, lookup by response sequence, parse header/data/error, map firmware errors to Linux errno, release doorbell and sequence slots, remove or retry commands, start queued commands, and run completers outside the lock. Timeout moves the interface to fail mode and cancels outstanding commands.

## State and Persistence Behavior
Persistent runtime state includes the ordered workqueue, `iface_lock`, `cmd_list`, wait queue, command sequence ownership array, previous sequence/handle, doorbell owner, mode, outstanding cleanup count, and new-epoch flag. Command and wait data are reference-counted with `kref`. No state survives driver removal; `finish()` waits for cleanup before destroying the workqueue.

## Dependencies and Integration Points
It depends on MCDI protocol constants, CDX bitfield helpers, wait queues, krefs, workqueues, mutexes, and a transport-specific `cdx_mcdi_ops` implementation supplied by `cdx_controller.c` and `cdx_rpmsg.c`.

## Risks
The code assumes at most one active doorbell command while still allowing queued commands and sequence reuse. Timeout is severe: one timed-out command puts the whole iface into fail mode and cancels all outstanding work. `cdx_mcdi_rpc_async_internal()` ignores its `handle` argument and queues work without returning a handle, limiting cancellation by external users. Error handling for `MC_CMD_ERR_QUEUE_FULL` compares `rc` after conversion paths and must preserve raw queue-full semantics. Response buffers passed to completers point into RPMsg callback memory until copied by the sync completer; async completers must not retain them beyond callback semantics. Locking around completion and cleanup reference counts is delicate.

## Test Signals
Unit or integration tests should cover init/finish quiescence, multiple queued commands, sequence wrap, firmware error translation, queue-full retry, timeout fail mode, unexpected response sequence, short response lengths, sync response truncation, async completer exactly-once behavior, and remove while commands are outstanding.
