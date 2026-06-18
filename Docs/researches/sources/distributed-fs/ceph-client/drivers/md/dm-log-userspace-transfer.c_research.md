
# sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-transfer.c

## Purpose
Provides the low-level connector/netlink transport for dm userspace dirty logs. It serializes kernel requests into `struct dm_ulog_request`, sends them to the userspace log daemon, waits for matching replies or ACKs, retries on timeout or `-EAGAIN`, and exposes a single `dm_consult_userspace()` API to the userspace dirty-log implementation.

## Important APIs, Types, And Functions
Global state includes `dm_ulog_seq`, preallocated 512-byte connector/request buffer, connector id `CN_IDX_DM/CN_VAL_DM_USERSPACE_LOG`, `dm_ulog_lock`, and `receiving_list` protected by `receiving_list_lock`. `struct receiving_pkg` is a stack-resident waiter containing sequence, completion, error, and return-data buffer. `dm_ulog_sendto_server()` fills `cn_msg` and calls `cn_netlink_send()`. `fill_pkg()` matches replies by sequence and copies ACK or payload results. `cn_ulog_callback()` validates `CAP_SYS_ADMIN`, decodes messages, and completes waiters. `dm_consult_userspace()` builds a request, links a waiter, sends, waits up to `DM_ULOG_RETRY_TIMEOUT`, and retries as needed. `dm_ulog_tfr_init()`/`dm_ulog_tfr_exit()` allocate buffers and register connector callbacks.

## Control Flow
Each request is serialized by `dm_ulog_lock` because the message buffer is shared. A waiter is added before send so a fast reply can complete it. On send failure the waiter is removed and the error is returned. On timeout the waiter is removed, a warning is emitted, and the request is rebuilt with a new sequence. Empty connector messages are treated as ACKs; non-empty messages are expected to contain a complete `dm_ulog_request` payload.

## State And Persistence
All state is volatile kernel memory. There is no persistence. Sequence values are process-lifetime counters. Waiters are stack objects visible through the receiving list only while `dm_consult_userspace()` is active.

## Dependencies And Integration Points
Depends on Linux connector, netlink credentials, completions, spinlocks, mutexes, dm-log-userspace protocol structures, and device-mapper logging macros. It is initialized by `dm-log-userspace-base.c` before the dirty-log type is registered.

## Risks
Connector is unreliable, so retry behavior can wait indefinitely if the daemon never responds. The fixed preallocated size limits payloads; callers must stay below the calculated capacity. Stack-resident waiters are safe only because list removal is synchronized. Capability checks protect callbacks, but daemon/protocol mismatches can return wrong data sizes. ACK `msg->ack` is negated into an errno, so userspace must follow connector ACK conventions.

## Test Signals
Exercise callback registration failure, oversized payload rejection, timeout and retry, `-EAGAIN` retry, ACK-only and payload replies, insufficient receive buffer handling, incomplete message logging, concurrent callers serialized through `dm_ulog_lock`, unauthorized callback messages, and module unload while no waiters remain.
