# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/response_manager.c

Purpose: Manages LiquidIO soft-command response lists and ordered response completion polling.

Important APIs, types, and functions: `octeon_setup_response_list()` initializes all response list heads, locks, pending counters, command response lock, and the `dma-comp` workqueue. `lio_process_ordered_list()` first frees caller-finished done-list entries, then inspects the head of `OCTEON_ORDERED_SC_LIST`, reads the DMA status word, validates that the full 64-bit firmware status has been written, translates firmware status, handles timeouts/force quit, moves commands to done or zombie lists, completes waiters, or invokes callbacks. `oct_poll_req_completion()` is delayed-work polling that reschedules while ordered responses remain.

Control flow: Request reclaim code adds response-bearing soft commands to the ordered list once Octeon has fetched the instruction. This file preserves ordered semantics by processing only from the head until it finds a pending entry or reaches `MAX_ORD_REQS_TO_PROCESS`.

State and persistence: Response state is in list heads, locks, pending counters, soft-command status fields, completion objects, and the workqueue. No state persists after delete.

Dependencies and integration: Depends on `octeon_iq.h` soft-command layout and `octeon_main.h` byte swapping. It cooperates with request-manager done/zombie/free functions and control senders waiting on completions.

Risks: Status-word validation is intentionally conservative; wrong endian handling or premature status use can report false completion. Callbacks free their own commands, while non-callback commands are freed via done-list cleanup, so lifetime rules differ. A pending head blocks later ordered responses.

Test signals: Successful firmware completion, nonzero firmware status translation, timeout path, callback vs completion path, zombie movement, done-list cleanup, reschedule behavior, and processing cap enforcement.
