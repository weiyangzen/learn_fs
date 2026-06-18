# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_iq.h

Purpose: Defines the LiquidIO input queue, which is the host-to-Octeon transmit/instruction ring abstraction. It also defines instruction formats and the soft-command buffer model used for firmware control requests.

Important APIs, types, and functions: `struct octeon_instr_queue` holds DMA ring addresses, host/read/flush indexes, pending instruction accounting, doorbell state, locks, stats, queue metadata, and request tracking. `struct octeon_request_list` links each descriptor slot to a host buffer and `REQTYPE_*` cleanup class. `struct octeon_instr_32B`, `struct octeon_instr2_64B`, `struct octeon_instr3_64B`, and `union octeon_instr_64B` describe chip-generation-specific command layouts. `struct octeon_soft_command` adds response DMA buffers, status words, completion, callbacks, expiry, and caller lifetime state. Exported declarations cover queue setup/delete, command posting, flush, soft-command preparation/sending, and soft-command pool management.

Control flow: Other LiquidIO files allocate a queue with `octeon_setup_iq()`, post descriptors with `octeon_send_command()` or `octeon_send_soft_command()`, then reclaim slots through `octeon_flush_iq()` and `lio_process_iq_request_list()`. Soft commands flow through IQ 0 because only that queue sets `allow_soft_cmds`.

State and persistence: State is in kernel memory, coherent DMA rings, atomics, and hardware doorbell/count registers. It is not persistent across driver unload or reset. Concurrency is managed by `lock`, `post_lock`, and `iq_flush_running_lock`.

Dependencies and integration: Depends on `liquidio_common.h` instruction bitfields, `octeon_device` chip hooks, response-manager status codes, and netdev/BQL cleanup helpers in `octeon_main.h`. The request type enum must stay aligned with registered free callbacks.

Risks: Incorrect descriptor sizing, 32B/64B format mismatch, missing memory barriers, or reqtype/free callback mismatches can corrupt DMA, leak SKBs, or stall TX. Soft-command status lifetime is race-sensitive because callers and response polling both observe `caller_is_done`.

Test signals: Exercise queue full/stop/failed statuses, BQL completion accounting, IQ flush under NAPI budget and shutdown, soft-command timeout/zombie handling, and both CN6XXX and CN23XX command layouts.
