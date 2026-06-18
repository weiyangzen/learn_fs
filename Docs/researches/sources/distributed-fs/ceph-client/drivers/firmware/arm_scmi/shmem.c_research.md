# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/shmem.c

Purpose: This file implements shared-memory transport helpers for SCMI SMT-style transports. It prepares tx messages in the SCMI shared memory layout, fetches responses/notifications, clears channels, polls completion, maps device-tree shmem regions, and chooses IO copy methods.

Important APIs/types/functions: `struct scmi_shared_mem` models the SCMI shared memory header and payload. `shmem_tx_prepare()` waits for a free channel, writes channel status, flags, length, header, and payload. `shmem_fetch_response()` reads status and response payload. `shmem_fetch_notification()` reads notification payload without status. `shmem_clear_channel()`, `shmem_poll_done()`, `shmem_channel_free()`, and `shmem_channel_intr_enabled()` expose state checks. `shmem_setup_iomap()` validates the DT `shmem` phandle, resource size, compatibility, maps it, and selects 32-bit or default IO copy ops. `scmi_shared_mem_operations_get()` exports the operation table.

Control flow: Transports call `setup_iomap()` at channel setup. On send, transports call `tx_prepare()` before ringing a mailbox/SMC/OP-TEE doorbell. On RX, they read the header then fetch response or notification. After P2A processing, transports clear the channel and may signal completion to firmware.

State and persistence: Shared memory itself is firmware/OS shared runtime state. The helper keeps no global mutable state. IO ops are static. Mappings are devm-managed by callers' device lifetimes.

Dependencies and integration points: It depends on OF address parsing, IO memory accessors, ktime/processor spin waiting, and `common.h` shared-memory operation types. It is used by mailbox, SMC, and OP-TEE static SMT transports.

Risks and edge cases: `shmem_tx_prepare()` gives up after twice the channel timeout but returns void, so transports proceed even after warning that the channel is likely compromised. The 32-bit IO copy path warns on misalignment and count not multiple of 4. Misconfigured shmem size is rejected using `max_msg_size + SCMI_SHMEM_LAYOUT_OVERHEAD`. Poll completion compares tokens to avoid stale completion, but late firmware replies can still stress transport recovery.

Test signals: Device-tree validation should reject missing/non-compatible/undersized shmem. Transport tests should cover interrupt-enabled and polling messages, late response channel-free waiting, 32-bit `reg-io-width`, response status extraction, notification extraction, and channel clear semantics.
