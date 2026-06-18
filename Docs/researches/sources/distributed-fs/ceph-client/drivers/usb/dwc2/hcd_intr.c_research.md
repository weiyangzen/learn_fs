# sources/distributed-fs/ceph-client/drivers/usb/dwc2/hcd_intr.c

## Purpose
`hcd_intr.c` implements DWC2 host-mode interrupt handling. It turns core interrupt status bits, port events, FIFO events, and per-host-channel interrupts into URB progress, QTD/QH scheduling changes, channel release, transfer completion, retry, or error completion. It is the interrupt-side partner of the host queueing and transaction programming code.

## Important APIs, Types, And Functions
- Exported entry point: `dwc2_handle_hcd_intr()` is called by the common interrupt handler when host-mode HCD processing is possible.
- Channel dispatch: `dwc2_hc_intr()` reads `HAINT` and services split transactions in `hsotg->split_order` before scanning all channels; `dwc2_hc_n_intr()` reads and clears `HCINT(n)` bits, validates the channel/QTD, and invokes specific handlers.
- Core interrupt handlers: `dwc2_sof_intr()`, `dwc2_rx_fifo_level_intr()`, `dwc2_np_tx_fifo_empty_intr()`, `dwc2_perio_tx_fifo_empty_intr()`, and `dwc2_port_intr()`.
- Transfer state helpers: `dwc2_get_actual_xfer_length()`, `dwc2_update_urb_state()`, `dwc2_update_urb_state_abn()`, `dwc2_update_isoc_urb_state()`, and exported `dwc2_hcd_save_data_toggle()`.
- Channel lifecycle helpers: `dwc2_halt_channel()`, `dwc2_release_channel()`, `dwc2_deactivate_qh()`, `dwc2_complete_non_periodic_xfer()`, and `dwc2_complete_periodic_xfer()`.
- Error/event handlers: `dwc2_hc_xfercomp_intr()`, `dwc2_hc_stall_intr()`, `dwc2_hc_nak_intr()`, `dwc2_hc_ack_intr()`, `dwc2_hc_nyet_intr()`, `dwc2_hc_babble_intr()`, `dwc2_hc_ahberr_intr()`, `dwc2_hc_xacterr_intr()`, `dwc2_hc_frmovrun_intr()`, `dwc2_hc_datatglerr_intr()`, and `dwc2_hc_chhltd_intr_dma()`.

## Control Flow
`dwc2_handle_hcd_intr()` first checks controller liveness, then takes `hsotg->lock` and confirms host mode. It reads masked core interrupts with `dwc2_read_core_intr()` and handles SOF, Rx FIFO, non-periodic FIFO empty, port, host-channel, and periodic FIFO empty interrupts in a fixed order. SOF updates `hsotg->frame_number`, tracks missed SOFs, moves ready periodic QHs from inactive to ready, selects transactions, and queues work.

Host-channel interrupts are two-level. `dwc2_hc_intr()` reads `HAINT`, handles channels in split-completion order first to preserve USB 2.0 TT ordering, then handles remaining channels by index. `dwc2_hc_n_intr()` reads raw and masked channel interrupt bits, writes the masked bits back to clear them, validates `chan`, `chan->qh`, and the active QTD, and then processes bits by priority. It rechecks whether the original QTD is still at the QH head after handlers that may complete and free/unlink it.

Transfer-complete handling is endpoint-specific. Control transfers advance setup, data, and status phases; bulk and interrupt transfers update `urb->actual_length` and data toggle; isochronous transfers update per-frame status and length. Non-periodic completions normally release or halt and release the channel so the scheduler can assign it again. Periodic completions either release immediately or halt first if outstanding IN packets remain.

## State And Persistence Behavior
The file mutates transient in-memory HCD state: URB status and `actual_length`, QTD fields such as `control_phase`, `complete_split`, `isoc_frame_index`, `error_count`, `num_naks`, and `want_wait`, QH fields such as `data_toggle`, `ping_state`, `tt_buffer_dirty`, and channel fields such as `halt_status`, `xfer_count`, `xfer_buf`, and `hcint`. It updates host controller counters and lists through `dwc2_release_channel()` and `dwc2_hcd_qh_deactivate()`, including free-channel lists, non-periodic/periodic schedule lists, `available_host_channels`, and non-periodic channel counters. Hardware state is persisted only in controller registers such as `GINTSTS`, `GINTMSK`, `HPRT0`, `HCFG`, `HFIR`, `HAINTMSK`, `HCINT`, and `HCTSIZ`.

## Dependencies And Integration Points
This code depends on DWC2 register definitions from `hw.h`, host data structures and helpers from `core.h` and `hcd.h`, USB core URB and TT APIs, Linux spinlocks, DMA mapping, and workqueue/timer interactions created elsewhere. It calls scheduler functions from host queue code (`dwc2_hcd_select_transactions()`, `dwc2_hcd_queue_transactions()`, `dwc2_hcd_qh_deactivate()`), transfer completion helpers (`dwc2_host_complete()`), DDMA helpers (`dwc2_hcd_complete_xfer_ddma()`), and core helpers for mode, frame number, FIFO, TT clear, and channel halt/cleanup.

## Risks
- QTD/QH lifetime is fragile in interrupt context. The explicit `dwc2_check_qtd_still_ok()` calls show that handlers may complete and free the active QTD; any new handler ordering must preserve this validation.
- Split transaction handling is latency-sensitive and order-sensitive. Changing `split_order` handling or NYET/NAK retry logic risks TT protocol regressions.
- DMA and slave mode paths differ substantially. A fix for one path can break the other if channel halt/release semantics are assumed to be identical.
- Actual-length calculation depends on correct interpretation of `HCTSIZ` fields after halt; using AHB byte count for abnormal halts would corrupt URB progress.
- Port enable handling can reset the port when FS/LS low-power clock settings change. Bad sequencing here can cause reconnect loops or descriptor DMA mode toggling problems.
- Error retry policy uses a three-strikes `qtd->error_count` rule and NAK delay threshold; changing it can cause interrupt storms or premature URB failure.

## Test Signals
- Exercise control, bulk, interrupt, and isochronous transfers in host mode, both DMA and non-DMA if platform supports them.
- Test high-speed hub with full-/low-speed devices to cover split ordering, TT clear, NAK/NYET, and isochronous split paths.
- Validate port connect, enable change, overcurrent change, reset, and FS/LS low-power clock paths with real devices.
- Stress with devices that NAK repeatedly and confirm retry delay prevents interrupt storms without control-IN stalls.
- Enable debug or tracing around HC interrupts to verify no "Interrupt on disabled channel", "no QTD queued", or unknown halt reason messages appear under normal load.
- Use error injection or flaky devices to cover STALL, babble, AHB error, transaction error, frame overrun, and data toggle error completion status.
