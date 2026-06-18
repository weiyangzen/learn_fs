# File Research: sources/block-storage/linux-dm/drivers/md/dm-log-userspace-transfer.c

## Purpose
Implements the connector/netlink transport used by DM userspace dirty logs. It serializes requests to a userspace log server, waits for matching replies, retries on timeout or `-EAGAIN`, and copies response payloads back to callers.

## Main Interfaces
- Request API: `dm_consult_userspace()`.
- Transport lifecycle: `dm_ulog_tfr_init()`, `dm_ulog_tfr_exit()`.
- Internal send/receive: `dm_ulog_sendto_server()`, `cn_ulog_callback()`, `fill_pkg()`.

## Control Flow
`dm_consult_userspace()` validates payload size against a 512-byte preallocated buffer, serializes request construction with `dm_ulog_lock`, fills a `dm_ulog_request`, assigns a sequence number, adds a stack-allocated receiving package to a global list, sends the connector message, and waits up to `DM_ULOG_RETRY_TIMEOUT`.

The connector callback receives ACKs or full replies, requires `CAP_SYS_ADMIN`, finds the waiting package by sequence number, records error/data, and completes the waiter. Timeouts and `-EAGAIN` responses resend the request with a new sequence.

## State And Synchronization
A global preallocated connector message/request buffer is protected by `dm_ulog_lock`. `receiving_list` stores currently waiting stack packages and is protected by `receiving_list_lock`. `dm_ulog_seq` monotonically assigns request sequence numbers.

## Integration Points
Uses Linux connector IDs `CN_IDX_DM` and `CN_VAL_DM_USERSPACE_LOG`, `cn_netlink_send()`, connector callback registration, and the public `dm_ulog_request` protocol definitions from `linux/dm-log-userspace.h`.

## Notable Behaviors
- Netlink/connector is treated as unreliable; timed-out requests are resent indefinitely.
- Late responses are discarded because their receiving package has already been removed.
- Response buffers are size-checked and fail with `-ENOSPC` if too small.
- The request structure is zeroed before filling to avoid leaking kernel memory to userspace.
- Only one request is sent at a time because the send buffer is global and preallocated.

## Risks And Review Focus
- The receiving list contains stack objects from sleeping callers; correctness depends on removing them before returning.
- Infinite retry behavior can hang callers if the userspace server stops responding without returning `-ESRCH`.
- Sequence number wrap is not specially handled.
- Capability checks in the callback guard message acceptance but depend on connector context semantics.
