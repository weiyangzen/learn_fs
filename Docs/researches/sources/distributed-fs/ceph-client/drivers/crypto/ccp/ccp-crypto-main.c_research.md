# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-main.c

## Purpose

`ccp-crypto-main.c` is the module entry point and shared scheduler for CCP Crypto API algorithms. It verifies that a CCP device is present, registers enabled algorithms, maintains lists for cleanup, and wraps lower `ccp_enqueue_cmd()` with a global queue that preserves request ordering per Crypto API transform while allowing commands for different transforms to run concurrently.

## Important APIs, Types, And Functions

- Module parameters `aes_disable`, `sha_disable`, `des3_disable`, and `rsa_disable` selectively skip algorithm families.
- `hash_algs`, `skcipher_algs`, `aead_algs`, and `akcipher_algs` track registered algorithm wrappers.
- `struct ccp_crypto_queue` stores pending commands, backlog pointer, and command count.
- `struct ccp_crypto_cmd` wraps a `ccp_cmd`, original async request, transform pointer, and return state.
- `ccp_crypto_success()` normalizes `0`, `-EINPROGRESS`, and `-EBUSY` as successful enqueue outcomes.
- `ccp_crypto_enqueue_request()` allocates the wrapper, sets lower callback/data, maps Crypto API backlog flags to `CCP_CMD_MAY_BACKLOG`, and calls `ccp_crypto_enqueue_cmd()`.
- `ccp_crypto_complete()` handles lower command progress/completion, advances backlog notifications, runs algorithm-specific completion fixups, completes the original request, and submits held same-tfm commands.
- `ccp_crypto_sg_table_add()` copies SG entries into a preallocated SG table.
- `ccp_register_algs()` and `ccp_unregister_algs()` manage algorithm family registration/unregistration.
- `ccp_crypto_init()`/`ccp_crypto_exit()` are module init/exit.

## Control Flow

Module init calls `ccp_present()` and refuses to load when no CCP exists. It initializes the global queue and registers algorithm families unless disabled. Each algorithm request is wrapped in `ccp_crypto_cmd`. The enqueue path rejects or backlogs at `CCP_CRYPTO_MAX_QLEN`, then scans for an existing command with the same `tfm`. If none exists, it submits immediately to `ccp_enqueue_cmd()`; if one exists, it only queues locally to preserve per-transform ordering.

On lower completion, `ccp_crypto_complete()` removes the completed wrapper, sends `-EINPROGRESS` notifications to backlog entries as they advance, runs the transform-specific `ctx->complete()` callback, completes the Crypto API request, then attempts to submit the next held command for the same transform. If held submission fails, it completes that request with the error and continues scanning.

## State And Persistence Behavior

The module stores registered algorithm lists and a global queue protected by `req_queue_lock`. `req_queue.backlog` is a cursor into the command list. Each queued request stores a stable `tfm` pointer separately from the request because the async request may become invalid after completion callback invocation.

## Dependencies And Integration Points

This file depends on exported CCP core APIs from the base driver (`ccp_present()`, `ccp_enqueue_cmd()`, `ccp_version()` via providers), Linux Crypto API registration, and provider registration functions from the other `ccp-crypto-*` files. It integrates lower completion semantics from the CCP device scheduler with upper Crypto API async/backlog semantics.

## Risks And Edge Cases

- The global queue is capped at 100 commands; high concurrency can return `-ENOSPC` or `-EBUSY` depending on caller backlog flags.
- Ordering is per `tfm`, not per algorithm family; shared transforms serialize while different transforms may run out of order relative to each other.
- Completion invokes callbacks outside the queue lock, but uses stored `tfm` to avoid dereferencing freed request memory after callback.
- Partial registration failure calls unregister for already registered algorithms; providers must add list entries only after successful registration.

## Test Signals

Signals include module load refusal without CCP, algorithm list registration with disable parameters, async ordering tests issuing multiple requests on one tfm, backlog notification behavior, unregister cleanup after injected registration failure, and stress tests across multiple transforms and hardware queues.
