# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_fsms.c

## Purpose
`ctcm_fsms.c` defines the finite state machine behavior for the s390 CTCM network driver. It contains the classic CTC channel FSM, the MPC-specific extended channel FSM, and the device-level FSM that coordinates read and write channels. Its main job is to translate ccw interrupt events, timers, start/stop requests, and MPC XID/sweep events into channel program operations, queue cleanup, retries, and netdev link state transitions.

## Important APIs, Types, And Functions
- Exports state/event name arrays for diagnostics: `dev_state_names`, `dev_event_names`, `ctc_ch_event_names`, and `ctc_ch_state_names`.
- Exports FSM tables and lengths: `ch_fsm`, `ch_fsm_len`, `ctcmpc_ch_fsm`, `mpc_ch_fsm_len`, `dev_fsm`, and `dev_fsm_len`.
- `ctcm_ccw_check_rc()` maps `ccw_device_*()` failures to channel FSM events such as `CTC_EVENT_IO_EBUSY`, `CTC_EVENT_IO_ENODEV`, and `CTC_EVENT_IO_UNKNOWN`.
- `ctcm_purge_skb_queue()` drains skb queues while balancing the driver-held skb user reference.
- Classic CTC actions include `ctcm_chx_start()`, `ctcm_chx_setmode()`, `chx_firstio()`, `chx_rxidle()`, `chx_rx()`, `ctcm_chx_txidle()`, `chx_txdone()`, retry/error actions, and halt/cleanup actions.
- MPC actions include `ctcmpc_chx_firstio()`, `ctcmpc_chx_rxidle()`, `ctcmpc_chx_rx()`, `ctcmpc_chx_txdone()`, `ctcmpc_chx_attn()`, `ctcmpc_chx_attnbusy()`, `ctcmpc_chx_resend()`, and `ctcmpc_chx_send_sweep()`.
- Device FSM actions `dev_action_start()`, `dev_action_stop()`, `dev_action_restart()`, `dev_action_chup()`, and `dev_action_chdown()` coordinate the two channels and call MPC group membership hooks.

## Control Flow
The classic CTC bring-up flow starts with `DEV_EVENT_START` on the device FSM. `dev_action_start()` moves the netdev FSM to `DEV_STATE_STARTWAIT_RXTX` and sends `CTC_EVENT_START` to both channel FSMs. Each channel action initializes ccws, allocates or refreshes DMA-safe skb buffers, halts any outstanding I/O, then waits for final status. `CTC_EVENT_FINSTAT` moves the channel through set-extended-mode and initial 2-byte block handshake. Read channels start an ongoing READ ccw and report `DEV_EVENT_RXUP`; write channels enter `CTC_STATE_TXIDLE` and report `DEV_EVENT_TXUP`. Once both directions have reported up, `dev_action_chup()` moves the device to `DEV_STATE_RUNNING` and wakes the netdev queue.

Normal receive flow is `CTC_STATE_RXIDLE` plus final status into `chx_rx()`. The action computes received length from `max_bufsize - irb->scsw.cmd.count`, validates the block length, calls `ctcm_unpack_skb()`, resets the reusable receive skb, and posts the next read ccw. Normal transmit flow starts in `ctcm_main.c`, moves the channel to `CTC_STATE_TX`, and completes in `chx_txdone()`, which updates stats, frees queued skb references, optionally builds a chained multi-packet `trans_skb` from `collect_queue`, starts another ccw, or returns to `CTC_STATE_TXIDLE`.

MPC control flow reuses start/setup/stop actions but adds XID channel states and events. `ctcmpc_chx_attn()` and `ctcmpc_chx_attnbusy()` coordinate group negotiation through `MPCG_EVENT_XID0DO` and `MPCG_EVENT_XID7DONE`. `ctcmpc_chx_rx()` queues received MPC traffic to the channel tasklet, and `ctcmpc_chx_txdone()` drains collected PDUs into a TH-framed aggregate. Sweep handling uses `sweep_queue` plus `sweep_timer` to send TH sweep requests/responses when sequence numbers need reset.

## State And Persistence Behavior
The file is almost entirely volatile runtime state. Channel FSM state is held in each `struct channel` via `fsm_instance`; device state is held in `struct ctcm_priv`; MPC group state is held in `struct mpc_group`. Timers (`channel.timer`, `channel.sweep_timer`, and `priv.restart_timer`) persist only in memory and convert timeouts into FSM events. The code also maintains in-memory skb queues (`io_queue`, `collect_queue`, `sweep_queue`), retry counters, link sequence numbers, and profiling counters in `struct ctcm_profile`. There is no disk persistence.

## Dependencies And Integration Points
This file depends on the generic FSM helper in `fsm.c`/`fsm.h`, channel/netdev definitions in `ctcm_main.h`, MPC framing and group structures in `ctcm_mpc.h`, and debug macros from `ctcm_dbug.h`. Its actions call s390 ccw APIs (`ccw_device_start()`, `ccw_device_halt()`, `get_ccwdev_lock()`), Linux network APIs (`netif_wake_queue()`, skb queue helpers, `dev_kfree_skb_*()`), and MPC functions implemented in `ctcm_mpc.c` (`mpc_channel_action()`, `mpc_group_ready()`, `mpc_action_send_discontact()`, `ctcmpc_bh()`).

## Risks
- State transitions are interrupt- and timer-driven; many actions use conditional locking depending on caller context, which is explicitly noted as hard for static analysis and easy to break during refactoring.
- The FSM tables are sparse. Missing state/event pairs return nonzero from `fsm_event()` but often have no caller recovery path, so adding states/events requires table coverage checks.
- `ctcm_purge_skb_queue()` decrements skb user refs before freeing; incorrect enqueue/reference conventions elsewhere could cause leaks or double frees.
- MPC queue aggregation code assumes `skb_peek()` returns a valid skb before checking `peekskb->len` in one loop; queue edge cases need careful review.
- Retry logic and group recovery are tuned for peer behavior and VTAM sensitivity; shortening timers or changing stop/restart ordering can make remote peers unreachable.

## Test Signals
- Bring-up/down tests should exercise `ifconfig`/`ip link` up/down and verify device FSM transitions through start-wait to running and back to stopped.
- Fault injection or hardware simulation should cover ccw return codes, unit checks, timer expiry, remote disconnect, busy/attention, and machine check paths.
- Packet tests should verify classic chained transmit, receive block validation, MPC PDU batching, out-of-sequence MPC handling, and sweep sequence reset.
- Memory-pressure tests should force skb allocation and IDAL setup failures and confirm stats, queue cleanup, and MPC INOP recovery.
