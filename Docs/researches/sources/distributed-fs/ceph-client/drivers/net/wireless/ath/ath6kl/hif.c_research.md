# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/hif.c

## Purpose
`hif.c` implements common HIF support for mailbox-style ath6kl transports: asynchronous read/write completion dispatch, virtual scatter buffer copying, firmware crash dump handling, mailbox polling, RX interrupt masking, scatter request submission, interrupt processing, interrupt enable/disable, and initial mailbox block-size setup.

## Important APIs, types, and functions
`ath6kl_hif_rw_comp_handler()` receives bus async completion status, stores it in the `htc_packet`, and invokes the packet completion callback. `ath6kl_hif_submit_scat_req()` prepares read or write scatter requests, assigns mailbox addresses, copies virtual scatter bounce buffers when needed, dispatches through `ath6kl_hif_scat_req_rw()`, and updates synchronous read status. `ath6kl_hif_poll_mboxmsg_rx()` repeatedly reads the interrupt register table until mailbox data and a valid lookahead are present or timeout. `ath6kl_hif_intr_bh_handler()` loops through `proc_pending_irqs()` until no more work or communication timeout. `ath6kl_hif_unmask_intrs()`, `ath6kl_hif_mask_intrs()`, and `ath6kl_hif_setup()` manage chip-level and host-level interrupt state.

## Control flow and integration
The bottom-half interrupt handler reads target interrupt status registers, extracts mailbox lookahead, calls `ath6kl_htc_rxmsg_pending_handler()` to drain HTC messages, and then handles CPU, error, and counter interrupts. Counter debug interrupts trigger `ath6kl_hif_proc_dbg_intr()`, which clears the debug counter, dumps firmware crash registers through diagnostic reads, reads firmware logs, and notifies firmware recovery with `ATH6KL_FW_ASSERT`. RX flow control toggles mailbox data interrupts when HTC runs out of receive buffers.

## State and persistence behavior
Persistent state lives in `struct ath6kl_device`: shadow interrupt process/enable registers, lock, HTC context, and backpointer to `ar`. `ath6kl_hif_setup()` stores mailbox block size, verifies it is a power of two, and derives `target->block_mask` for mailbox padding. Interrupt enable shadows are updated under `dev->lock` and written to target registers. Scatter requests are owned by lower HIF pools and returned by callers.

## Dependencies and integration points
The file depends on target register addresses/macros, HIF ops wrappers, HTC RX pending handler, diagnostic helpers, firmware log reader, and recovery notification. It assumes its HIF implementation allows synchronous I/O in bottom-half processing context.

## Risks and test signals
Risks include timeout handling during target unresponsiveness, stale interrupt shadow state, mailbox lookahead zero/mismatch cases, race-sensitive RX interrupt masking, crash dump diagnostic read failure, and scatter bounce copy length correctness. Test signals include forced firmware assert, mailbox RX under buffer starvation, interrupt mask/unmask around start/stop, scatter read/write with virtual and real scatter, invalid block-size rejection, and stress RX that forces `chk_irq_status_cnt` rechecks.
