# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_tx.c

Purpose: Implements Octeon EP VF transmit input queue resource setup, teardown, pending cleanup, and completion processing. It does not build/send Tx descriptors itself in this file; it manages queue memory and reclaims SKBs once hardware consumes posted instructions.

Important APIs/types/functions: Public functions are `octep_vf_iq_process_completions()`, `octep_vf_clean_iqs()`, `octep_vf_setup_iqs()`, and `octep_vf_free_iqs()`. Internal helpers are `octep_vf_iq_reset_indices()`, `octep_vf_iq_free_pending()`, `octep_vf_setup_iq()`, and `octep_vf_free_iq()`.

Control flow: Setup allocates `struct octep_vf_iq`, coherent descriptor ring memory, coherent scatter/gather list memory, and per-descriptor `buff_info`; each Tx buffer receives its slice of the SGLIST area. It initializes indices and asks `hw_ops.setup_iq_regs()` to bind hardware registers. Completion processing refreshes the hardware read index via `hw_ops.update_iq_read_idx()`, walks `flush_index` to that read index within budget, unmaps either a single DMA buffer or all gather segments, frees each SKB, updates stats, and wakes the netdev subqueue through `netif_subqueue_completed_wake()`. Shutdown cleanup unmaps and frees all entries still pending between `flush_index` and `host_write_index`.

State and persistence: Queue state persists in `oct->iq[]`, `oct->num_iqs`, coherent ring and sglist DMA memory, per-entry `octep_vf_tx_buffer`, ring indices, fill counters, completion counters, and stats. Hardware progress is represented by the input queue read index and completion count registers accessed through hardware callbacks.

Dependencies and integration: Uses PCI DMA APIs, Linux SKB fragment metadata, netdev queue helpers, Octeon configuration macros, and chip-specific `hw_ops`. It integrates with the main transmit path, which must populate `buff_info`, descriptor ring entries, and doorbells consistently with the cleanup/completion format.

Risks: Scatter/gather unmap length indexing differs between completion and pending-cleanup paths (`len[3 - (i & 3)]` versus `len[i & 3]`), so descriptor packing must be validated carefully. Freeing queues assumes entries have valid SKB pointers between `flush_index` and `host_write_index`. Resource setup errors must unwind coherent memory in the right order. Queue wake thresholds must align with `IQ_INSTR_SPACE()`.

Test signals: Open/close cycles should allocate/free all IQs without DMA leaks, Tx traffic should complete and wake stopped queues, SG and non-SG packets must unmap correctly, forced shutdown with pending packets should free all SKBs, and stats should reflect posted/completed bytes and gather entries.
