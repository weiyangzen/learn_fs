# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_controlq.c

## Purpose
`ice_controlq.c` implements the Intel ice driver control queue runtime: AdminQ, PF-VF mailbox queue, and the optional sideband queue. These queues are DMA descriptor rings used to exchange synchronous commands and asynchronous receive events with device firmware. The file owns queue register selection, DMA allocation, initialization/shutdown, locking, command submission, receive event cleanup, descriptor debug logging, sideband fallback, and firmware AdminQ API compatibility checks.

## Important APIs, Types, And Functions
The exported entry points are `ice_create_all_ctrlq()`, `ice_init_all_ctrlq()`, `ice_shutdown_all_ctrlq()`, `ice_destroy_all_ctrlq()`, `ice_sq_send_cmd()`, `ice_clean_rq_elem()`, `ice_fill_dflt_direct_cmd_desc()`, `ice_check_sq_alive()`, `ice_is_sbq_supported()`, and `ice_get_sbq()`. They operate on `struct ice_hw` queue members declared through `struct ice_ctl_q_info` and `struct ice_ctl_q_ring` in `ice_controlq.h`.

Internal helpers map queue types to register blocks with `ICE_CQ_INIT_REGS()`, allocate descriptor rings via `dmam_alloc_coherent()`, allocate per-entry DMA buffers for indirect commands/events, program head/tail/length/base registers, and free queue memory through `ICE_FREE_CQ_BUFS()` plus `ice_free_cq_ring()`. `ice_aq_ver_check()` compares firmware AdminQ API versions against `EXP_FW_API_VER_*_BY_MAC()` and blocks newer incompatible major versions. `ice_debug_cq()` provides descriptor and optional payload dumps under dynamic debug or `hw->debug_mask`.

## Control Flow
Driver load calls `ice_create_all_ctrlq()`, which initializes mutexes and then calls `ice_init_all_ctrlq()`. AdminQ is initialized first and validated by `ice_init_check_adminq()`, which sends `ice_aq_get_fw_ver()` and performs the API version check. A critical firmware error causes AdminQ init to be retried up to `ICE_CTL_Q_ADMIN_INIT_TIMEOUT` with `ICE_CTL_Q_ADMIN_INIT_MSEC` sleeps. The sideband queue is initialized only on generic MAC devices; otherwise sideband users fall back to AdminQ via `ice_get_sbq()`. Mailbox queue initialization follows.

Send command flow is centralized in `ice_sq_send_cmd()`: it rejects reset-in-progress, locks `sq_lock`, validates direct/indirect buffer arguments, checks the hardware head, cleans completed descriptors, copies the command onto the next ring descriptor, copies indirect payload into the per-entry DMA buffer, advances `next_to_use`, rings the tail, flushes MMIO writes, polls queue head with `ice_sq_done()`, copies writeback descriptor and optional data back to caller, updates `sq_last_status`, saves an optional writeback descriptor, and returns Linux errno-style status. Receive event flow in `ice_clean_rq_elem()` locks `rq_lock`, compares hardware head against `next_to_clean`, copies descriptor and bounded payload to caller, restores the receive buffer descriptor for reuse, updates tail and ring cursors, and optionally reports pending event count.

## State And Persistence
State is in `hw->adminq`, `hw->mailboxq`, and `hw->sbq`: ring register offsets, DMA addresses, queue depths, buffer sizes, cursors, counts, mutexes, and the last send status. No disk persistence exists. Hardware-visible persistence is limited to queue register programming and firmware-side command effects. Shutdown zeros control queue registers, frees coherent DMA buffers, and marks queue counts as zero. `hw->reset_ongoing` is treated as a soft blocker for new commands.

## Dependencies And Integration Points
The file depends on `ice_common.h`, `ice_adminq_cmd.h`, MMIO helpers (`rd32`, `wr32`, `ice_flush`, `rd32_poll_timeout`), kernel DMA APIs, mutexes, endian helpers, firmware AdminQ opcodes, and libie AQ descriptor definitions. Higher-level modules call `ice_aq_send_cmd()` wrappers, which route through `ice_sq_send_cmd()`; event processing paths consume `ice_clean_rq_elem()` for AdminQ/mailbox events. DCB, DDP, scheduler, resource-lock, mailbox, and reset code all depend on a working AdminQ.

## Risks
The main risks are DMA allocation unwind correctness, command timeouts during firmware critical errors, stale ring cursors after resets, incorrect indirect buffer lengths, and missed receive event recycling. `ice_sq_send_cmd()` returns `-EIO` for many firmware descriptor errors after recording `sq_last_status`, so callers must inspect queue status when they need detailed firmware reason codes. Sideband fallback to AdminQ is intentional but means callers must tolerate different queue routing by MAC type.

## Test Signals
Useful signals include successful probe and AdminQ firmware version reads, no leaked DMA buffers across probe/remove and reset cycles, AQ dynamic debug traces for descriptors and payloads, forced reset paths that shut down and reinitialize queues cleanly, mailbox traffic with VFs, sideband-capable and non-sideband hardware coverage, and negative tests for oversized buffers, invalid direct/indirect argument pairs, full send queues, receive queues with no pending events, and firmware/NVM API mismatch warnings.
