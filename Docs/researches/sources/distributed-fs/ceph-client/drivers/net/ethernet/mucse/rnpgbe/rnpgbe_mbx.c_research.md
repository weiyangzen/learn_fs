# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx.c

Purpose: low-level PF-to-firmware mailbox transport for rnpgbe. It performs MMIO reads/writes to shared memory/control registers, arbitrates ownership with PFU/REQ bits, tracks firmware request/ack counters, and provides blocking read/write helpers.

Important functions: `mucse_write_and_wait_ack_mbx`, `mucse_poll_and_read_mbx`, and `mucse_init_mbx_params_pf` are externally visible. Internal helpers handle data/control MMIO, lock acquisition/release, counter extraction/increment, polling for messages, polling for acks, and reset of local mailbox state.

Control flow: writes acquire the PF mailbox lock through `read_poll_timeout_atomic`, copy u32 words into shared memory, snapshot current FW ack, increment PF request, and release the lock with `MUCSE_MBX_REQ` set. The caller then polls for a changed nonzero FW ack. Reads poll for a changed nonzero FW request, acquire the lock, copy shared memory into the caller buffer, clear the first data word, snapshot FW request, increment PF ack, and release without request.

State and persistence: `hw->mbx.fw_req` and `fw_ack` are local snapshots used to identify new mailbox events. `mbx->lock` serializes higher-level firmware command exchanges; lower-level PFU ownership serializes shared memory with firmware. Hardware counters persist until reset.

Dependencies and integration: uses Linux `read_poll_timeout`, `read_poll_timeout_atomic`, bitfield helpers, and mailbox offsets from `rnpgbe_mbx.h` and board initialization.

Risks: `size` is divided by four, so non-u32-aligned sizes would silently truncate. Polling treats zero counters as reset/error, which may be fragile across firmware behavior. Raw MMIO has no bounds checking against mailbox buffer size. Atomic lock polling allows IRQ-context use, but higher-level wrappers also use a mutex and therefore are process-context only.

Test signals: firmware command round trips, timeout handling when firmware is absent, reset register behavior, concurrent command serialization, ack/request counter wraparound, and malformed size tests under instrumentation.
