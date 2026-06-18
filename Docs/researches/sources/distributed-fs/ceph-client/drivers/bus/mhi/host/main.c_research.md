# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/main.c

## Purpose

`main.c` implements the MHI host runtime hot path: register access wrappers, doorbell writes, DMA buffer mapping, ring pointer management, virtual device creation/destruction for channels, IRQ handlers, event-ring parsers, transfer queueing, command ring submission, channel start/stop/reset sequencing, and public buffer queue APIs for MHI client drivers.

## Important APIs, Types, And Functions

- Register helpers: `mhi_read_reg()`, `mhi_read_reg_field()`, `mhi_poll_reg_field()`, `mhi_write_reg()`, `mhi_write_reg_field()`, `mhi_write_db()`.
- Doorbell helpers: `mhi_db_brstmode()`, `mhi_db_brstmode_disable()`, `mhi_ring_er_db()`, `mhi_ring_cmd_db()`, and `mhi_ring_chan_db()`.
- Queue APIs: `mhi_queue_skb()`, `mhi_queue_buf()`, `mhi_queue_is_full()`, `mhi_get_free_desc_count()`, and `mhi_gen_tre()`.
- Event/IRQ paths: `mhi_irq_handler()`, `mhi_intvec_handler()`, `mhi_intvec_threaded_handler()`, `mhi_process_ctrl_ev_ring()`, `mhi_process_data_event_ring()`, `mhi_ev_task()`, and `mhi_ctrl_ev_task()`.
- Channel lifecycle: `mhi_send_cmd()`, `mhi_prepare_for_transfer()`, `mhi_unprepare_from_transfer()`, `mhi_reset_chan()`, and private helpers for channel command state.

## Control Flow

Client queueing enters through `mhi_queue_buf()` or `mhi_queue_skb()`, builds a `mhi_buf_info`, checks PM error state and ring fullness, generates a TRE under the channel write lock, maps or bounce-buffers the payload, takes runtime PM and wake references, rings the channel doorbell if PM permits, and balances the runtime PM reference immediately for device-to-host buffers or at completion for host-to-device buffers.

Event IRQs schedule tasklets unless the event ring is client-managed, in which case the owning MHI device receives `MHI_CB_PENDING_DATA`. Event parsers validate device read pointers, translate DMA pointers into host ring pointers, dispatch control events, state changes, command completions, EE changes, TX completions, and RSC completions, then recycle event-ring entries and ring the event doorbell. Command completions update `mhi_chan->ccs` and complete the waiting channel command.

Channel preparation checks EE masks, allocates non-offload channel contexts, sends a START command, and waits for completion. Unprepare sends RESET when appropriate, marks events for the channel as stale, completes pending buffers with `-ENOTCONN`, unmaps DMA, and deinitializes context memory.

## State And Persistence Behavior

The file maintains ring `rp`/`wp` in host memory and mirrors write pointers into device contexts before ringing doorbells. `mhi_buf_info` entries persist in the channel buffer ring until completion or reset. `pending_pkts` tracks outstanding host-to-device transfers and participates in low-power decisions. Channel state changes are protected by per-channel mutexes and rwlocks, while event rings use spinlocks/tasklets and controller PM uses `pm_lock`.

## Dependencies And Integration Points

`main.c` depends on `internal.h` and `trace.h`, DMA mapping APIs, tasklets, IRQ APIs, runtime PM callbacks supplied by the controller, and client callbacks installed during bus probe in `init.c`. It calls PM functions in `pm.c` for M0/M1/M3/SYS_ERR transitions and EE transition scheduling.

## Risks

Ring pointer validation is a major safety boundary; invalid device-provided pointers are logged and processing stops. The code unlocks channel read locks around client callbacks, so callback reentrancy and channel teardown must remain synchronized. Runtime PM reference balance differs by transfer direction and must stay paired with completion/reset paths. RSC event handling intentionally advances local descriptors based on ordered device caching, which relies on device protocol correctness. Command submission returns success even for an unsupported command after logging because the default case does not set an error before queuing; callers currently pass known command types.

## Test Signals

Tracepoints for generated TREs, data/control events, and channel command start/end should line up with successful transfers. Tests should cover ring-full behavior, DMA mapping failure, chained TRE completion, overflow completion, stale events during channel reset, client-managed event notification, invalid event pointer handling, SYS_ERR detection through both intvec and control events, and runtime PM reference balance under heavy UL and DL traffic.
