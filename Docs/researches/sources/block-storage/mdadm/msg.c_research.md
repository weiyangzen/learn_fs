# File Research: sources/block-storage/mdadm/msg.c

## Role

`msg.c` implements mdmon Unix-domain socket message framing and client helpers for pinging, blocking/unblocking subarrays, freezing containers, and flushing mdmon state.

## Message Protocol

Messages are framed as:

1. 32-bit start magic `0x5a5aa5a5`
2. signed 32-bit payload length
3. optional payload bytes
4. 32-bit end magic `0xa5a55a5a`

`MSG_MAX_LEN` limits payloads to 4 MiB.

## Transport Helpers

- `send_buf()` and `recv_buf()` use `select()` with optional timeout to complete partial writes/reads.
- `send_message()` and `receive_message()` implement framing.
- `ack()` sends a zero-length message.
- `wait_reply()` receives and discards any payload.
- `connect_monitor()` connects to `${MDMON_DIR}/${container}.sock`, including parsing subarray names to find the parent container socket, and switches the socket to nonblocking mode.
- `fping_monitor()`, `ping_monitor()`, and `ping_monitor_version()` implement request/reply checks.

## Blocking and Freezing

- `block_subarray()` changes sysfs `metadata_version` from `external:/...` to `external:-...`.
- `unblock_subarray()` reverses the marker and optionally sets `sync_action` to `idle`.
- `check_mdmon_version()` ensures a running mdmon is new enough to understand blocking semantics.
- `block_monitor()` walks all subarrays in a container, optionally freezes sync action, marks them blocked, pings mdmon, verifies frozen state, and rolls back on failure.
- `unblock_monitor()` clears blocked metadata markers and pings mdmon when needed.

## Manager Coordination

- `ping_manager()` sends a metadata update message with `len = -1`, prompting the mdmon manager to observe updated container state.
- `flush_mdmon()` pings both manager and monitor, used around takeover/grow paths to drain updates.

## Invariants and Risks

- Blocking uses a single-character semantic marker in `metadata_version`; old mdmon versions can mishandle it, so version checks are mandatory.
- `block_monitor()` is rollback-oriented: any failure while freezing subarrays triggers unblocking of those already modified.
- Message framing rejects bad magic and oversized payloads but otherwise treats payloads as opaque metadata updates.
