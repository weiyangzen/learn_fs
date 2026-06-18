# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mailbox.c

Purpose: Implements LiquidIO PF/VF mailbox transfers over paired 64-bit registers. It assembles multiword request/response messages, drives the register ACK/signature protocol, and handles a small set of PF/VF control commands.

Important APIs, types, and functions: `octeon_mbox_read()` consumes one 64-bit mailbox word, advances request or response receive state, and writes `OCTEON_PFVFACK` or `OCTEON_PFVFERR`. `octeon_mbox_write()` serializes `struct octeon_mbox_cmd` after waiting for `OCTEON_PFVFSIG` and per-word ACKs. `octeon_mbox_process_message()` dispatches complete responses to callbacks or complete requests to `octeon_mbox_process_cmd()`. `get_vf_stats()` aggregates IQ and DROQ counters for `OCTEON_GET_VF_STATS`. `octeon_mbox_cancel()` aborts a pending request.

Control flow: Read-side interrupts or pollers call `octeon_mbox_read()` until a full command is received. `octeon_mbox_process_message()` then either invokes a saved response callback, resets error state, or handles commands such as VF active handshake, FLR request, PF-changed MAC propagation, and VF stats response. Writes are synchronous polling loops with 1 ms sleeps and a 1000-iteration cap.

State and persistence: Mailbox state lives in `struct octeon_mbox`: IDLE, REQUEST_RECEIVING, REQUEST_RECEIVED, RESPONSE_PENDING, RESPONSE_RECEIVING, RESPONSE_RECEIVED, and ERROR bits plus saved request/response command buffers. No state persists beyond the driver instance; hardware register contents are used only as a handshake surface.

Dependencies and integration: Includes LiquidIO device, IQ, response, main, and CN23XX PF definitions. It calls `pcie_flr()`, `octeon_pf_changed_vf_macaddr()`, and stats fields from instruction/output queues. It assumes callers hold mailbox objects set up with correct PF/VF read/write register addresses.

Risks: The protocol is sensitive to stale signatures, partial multiword transfers, and concurrent state changes. Long synchronous waits can delay callers. Invalid state transitions write `OCTEON_PFVFERR`; recovery depends on later process/cancel paths. Stats are read without global queue teardown protection.

Test signals: Cover multiword request/response sequences, busy mailbox returns, timeout/failure exits, error-state callback delivery, VF active version handshake, FLR dispatch, stats response length, and cancellation of pending requests.
