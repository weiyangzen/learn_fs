# sources/distributed-fs/ceph-client/fs/ecryptfs/messaging.c

## Purpose

`messaging.c` implements the kernel side of request/response messaging between eCryptfs and the per-user `ecryptfsd` userspace daemon. It manages message context allocation, daemon lookup by effective uid, daemon lifetime, response delivery, wait timeouts, and messaging subsystem initialization/release. It is used primarily for public-key operations in `keystore.c`.

## Important APIs, types, and functions

Exported functions are `ecryptfs_msg_ctx_alloc_to_free()`, `ecryptfs_find_daemon_by_euid()`, `ecryptfs_spawn_daemon()`, `ecryptfs_exorcise_daemon()`, `ecryptfs_process_response()`, `ecryptfs_send_message()`, `ecryptfs_wait_for_response()`, `ecryptfs_init_messaging()`, and `ecryptfs_release_messaging()`. Internal state includes `ecryptfs_msg_ctx_free_list`, `ecryptfs_msg_ctx_alloc_list`, `ecryptfs_msg_ctx_lists_mux`, `ecryptfs_daemon_hash`, `ecryptfs_daemon_hash_mux`, `ecryptfs_hash_bits`, `ecryptfs_msg_counter`, and `ecryptfs_msg_ctx_arr`.

## Control flow

Initialization sizes a daemon hash table from `ecryptfs_number_of_users`, initializes every hash head, allocates `ecryptfs_message_buf_len` message contexts, puts them all on the free list, then registers the misc device through `ecryptfs_init_ecryptfs_miscdev()`.

Sending a message locks the daemon hash, finds a daemon for the caller's current euid, acquires a free message context, moves it to the allocated list, assigns a monotonically increasing counter, and queues the request to the daemon with `ecryptfs_send_miscdev()`. Waiting sleeps interruptibly until the context state becomes `DONE` or timeout expires. On success it detaches the response message for the caller; in all cases it returns the context to the free list.

Responses enter through miscdev write handling and call `ecryptfs_process_response()`. The function validates the response index, verifies the context is pending, checks the sequence counter, duplicates the response into the context, marks the context done, and wakes the blocked task.

Daemon lifecycle starts with `ecryptfs_spawn_daemon()`, which allocates a daemon for the miscdev file and inserts it in the euid hash. `ecryptfs_exorcise_daemon()` refuses to destroy daemons in read/poll, drops queued outgoing messages, removes the hash node, and frees sensitive daemon memory.

## State and persistence behavior

There is no disk persistence. Runtime state is bounded by module parameters: daemon hash entries by euid, fixed-size message context array, free/allocated lists, per-daemon outgoing queues, wait queues, task pointers, and response buffers. Message counters are sequence numbers used to reject stale or mismatched daemon responses.

## Dependencies and integration points

The file depends on scheduler sleeps, mutexes, hash lists, uid helpers, slab allocation, and miscdev functions declared in `ecryptfs_kernel.h` and implemented in `miscdev.c`. `keystore.c` uses `ecryptfs_send_message()` and `ecryptfs_wait_for_response()` for public-key FEK encrypt/decrypt. `main.c` initializes and releases messaging during module lifecycle.

## Risks

The fixed message context pool can exhaust and fail public-key operations. Wait semantics use `schedule_timeout_interruptible()` without an explicit condition waitqueue, relying on `wake_up_process()` from response delivery; signal and timeout behavior need careful testing. Sequence checking protects against response misdelivery, but context reuse after timeout must remain safe. Daemon teardown drops queued messages and returns contexts to free state, so races with miscdev reads/writes are a key risk.

## Test signals

Tests should cover daemon registration per euid, duplicate daemon open rejection, message send without daemon returning `-ENOTCONN`, context pool exhaustion, valid response delivery, wrong index and wrong sequence rejection, timeout returning `-ENOMSG`, daemon release with queued requests, module unload cleanup, and public-key keystore operations through a real or mocked `ecryptfsd`.
