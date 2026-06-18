# Research: subset-b-005215

Grouped research for s390 networking files under `sources/distributed-fs/ceph-client/drivers/s390/net`. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_fsms.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_fsms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_fsms.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_fsms.h

## Purpose
`ctcm_fsms.h` declares the event and state contracts used by the CTCM channel, MPC channel, device, and MPC group finite state machines. It is the shared vocabulary between the ccw interrupt path, the netdev lifecycle path, the MPC negotiation implementation, and the FSM tables in `ctcm_fsms.c` and `ctcm_mpc.c`.

## Important APIs, Types, And Functions
- `enum ctc_ch_events` defines ccw result events, attention/busy events, unit-check events, machine-check events, normal IRQ/final-status events, start/stop commands, and MPC-only `CTC_EVENT_SEND_XID` and `CTC_EVENT_RSWEEP_TIMER`.
- `enum ctc_ch_states` defines classic states such as `CTC_STATE_STOPPED`, `CTC_STATE_SETUPWAIT`, `CTC_STATE_RXIDLE`, `CTC_STATE_TXIDLE`, error/termination states, and MPC-only XID states `CH_XID0_PENDING` through `CH_XID7_PENDING4`.
- `enum dev_states` and `enum dev_events` define the two-channel netdev FSM states and channel-up/channel-down events.
- `enum mpcg_events` and `enum mpcg_states` define MPC group negotiation and operational states from reset/inop through passive or active XID phases to flow-control and ready.
- Declares exported FSM tables, lengths, and helper actions: `ch_fsm`, `ctcmpc_ch_fsm`, `dev_fsm`, `ctcm_ccw_check_rc()`, `ctcm_purge_skb_queue()`, `ctcm_chx_txidle()`, and `ctcmpc_chx_rxidle()`.

## Control Flow
The header does not implement flow, but it constrains it. Interrupts in `ctcm_main.c` convert ccw status into `CTC_EVENT_*` values declared here. `ctcm_fsms.c` consumes those values in table-driven transitions. `ctcm_mpc.c` consumes the MPC group event/state definitions to coordinate XID2 negotiation, flow control, and discontact handling. The numbering deliberately extends the classic channel state/event ranges for MPC, so classic FSMs use `CTC_NR_STATES` and `CTC_NR_EVENTS` while MPC FSMs use `CTC_MPC_NR_STATES` and `CTC_MPC_NR_EVENTS`.

## State And Persistence Behavior
The header defines symbolic in-memory state only. Persistence is provided by `fsm_instance` objects embedded in runtime structures, not by this file. The order and final-count constants are persistent ABI-like contracts within the driver because FSM table dimensions and state/event name arrays rely on them.

## Dependencies And Integration Points
It includes kernel headers for interrupts, timers, skbs, ccw devices, and IDALs, then includes the local `fsm.h` and `ctcm_main.h`. Because `ctcm_main.h` also includes MPC definitions, this header sits in a tightly coupled local include graph. The declarations are consumed by `ctcm_main.c`, `ctcm_fsms.c`, and `ctcm_mpc.c`.

## Risks
- Enum ordering is semantically important. Moving values, inserting states before sentinel counts, or changing `CTC_NR_*` and `CTC_MPC_NR_*` boundaries can corrupt jump-matrix indexing.
- The header includes many heavyweight kernel headers, which increases coupling and makes circular include changes risky.
- MPC and classic CTC share state names and event names, so diagnostics and FSM dimensions must remain aligned when adding MPC-only states.

## Test Signals
- Compile-time coverage catches many enum/table dimension mismatches, but behavioral tests should assert all expected state/event pairs are represented in `ch_fsm`, `ctcmpc_ch_fsm`, and `dev_fsm`.
- Trace/debug output should display correct names for channel, device, and MPC group states during setup, teardown, and XID negotiation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_fsms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_main.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_main.c

## Purpose
`ctcm_main.c` is the primary Linux network driver implementation for s390 CTC and CTCMPC channel devices. It registers the ccw and ccwgroup drivers, creates two-channel group devices, initializes netdevs, handles ccw interrupts, formats and transmits packets, unpacks classic CTC receive blocks, and tears resources down.

## Important APIs, Types, And Functions
- Module lifecycle: `ctcm_init()` registers debug views, a root device, the ccw driver, and the ccwgroup driver; `ctcm_exit()` unregisters them.
- Device discovery and grouping: `ctcm_ids`, `ctcm_ccw_driver`, `ctcm_group_driver`, `group_store()`, `ctcm_probe_device()`, `ctcm_new_device()`, `ctcm_shutdown_device()`, and `ctcm_remove_device()`.
- Channel management: global `channels`, `add_channel()`, `channel_get()`, `channel_free()`, `channel_remove()`, and `ctcm_ch_alloc_buffer()`.
- Netdev operations: `ctcm_open()`, `ctcm_close()`, `ctcm_tx()`, `ctcmpc_tx()`, `ctcm_change_mtu()`, and `ctcm_stats()` via `ctcm_netdev_ops` and `ctcm_mpc_netdev_ops`.
- Packet paths: `ctcm_transmit_skb()` for classic CTC, `ctcmpc_transmit_skb()` for MPC, `ctcm_unpack_skb()` for classic receive blocks, and `ctcmpc_send_sweep_req()` for MPC sequence maintenance.
- Interrupt path: `ctcm_irq_handler()` maps ccw status into channel FSM events.

## Control Flow
Module initialization starts with `ctcm_init()`, which sets `channels = NULL`, creates the `ctcm` root device, registers a ccw driver for 3088 channel variants, and registers a ccwgroup driver with a writable `group` driver attribute. Writing a group spec calls `ccwgroup_create_dev()`, then `ctcm_probe_device()` allocates `struct ctcm_priv`, assigns both ccw interrupt handlers, and attaches sysfs groups.

When a group is set online, `ctcm_new_device()` adds both channel devices to the global list, sets both ccw devices online, allocates and initializes a netdev, reserves one channel for read and one for write, attaches the netdev to the ccwgroup device, and registers it. Non-MPC netdev open/close directly sends device FSM start/stop events. MPC open/close is mediated by exported MPC APIs in `ctcm_mpc.c`.

`ctcm_irq_handler()` validates the IRB, identifies whether the interrupt belongs to the read or write channel, copies the IRB to `ch->irb`, and emits FSM events based on subchannel checks, unit checks, busy/attention bits, final status, or normal IRQ status. Unit-check sense bytes are decoded by `ccw_unit_check()` into remote reset, remote system reset, hardware failure, parity, timeout, zero, or unknown events.

Classic transmit begins at `ctcm_tx()`. It validates skb headroom, ensures the device FSM is running, marks the netdev busy, and calls `ctcm_transmit_skb()`. That function prepends the link-level header and block length, handles high-address DMA/IDAL limitations by copying when needed, prepares either direct skb ccws or reusable `trans_skb` ccws, starts the write ccw, and relies on FSM completion actions for stats and queue draining. MPC transmit follows the same high-level shape but prepends PDU and TH headers, observes MPC group state and sweep state, and can aggregate PDUs.

Classic receive blocks are unpacked by `ctcm_unpack_skb()`: it parses a leading length and repeated `struct ll_header` entries, validates protocol and lengths, clones each packet into a fresh skb, sets protocol/checksum metadata, updates stats, and delivers via `netif_rx()`.

## State And Persistence Behavior
The file owns the global in-memory channel list and root device pointer. Per-device state is held in `struct ctcm_priv` and attached to ccwgroup and netdev objects. Per-channel state includes ccw arrays, IRB storage, skbs, skb queues, timers, FSMs, flags, retry counters, and profiling counters. Sysfs can persistently influence runtime defaults while the device exists (`protocol`, `buffer_size`), but there is no storage across module unload or reboot.

## Dependencies And Integration Points
This code integrates with the s390 ccw and ccwgroup subsystems, Linux netdev APIs, skbuff APIs, IDAL/CDA helpers, root devices, sysfs driver attributes, and local FSM/MPC/debug modules. It depends on `ctcm_fsms.c` for state tables and actions, `ctcm_sysfs.c` for device attributes, and `ctcm_mpc.c` for MPC group initialization and callbacks.

## Risks
- The global `channels` list is manipulated without an obvious global list lock in the visible code, so lifetime assumptions depend on ccwgroup serialization.
- Error paths in `ctcm_new_device()` call `channel_get()` during rollback; because `channel_get()` marks channels in use and mutates direction flags, rollback ordering is subtle.
- DMA and IDAL fallback handling is complex. Incorrect normalized CDA cleanup or skb refcounting can leak DMA mappings, leak skbs, or free buffers still referenced by ccws.
- `ctcm_tx()` returns `NETDEV_TX_BUSY` after `ctcm_transmit_skb()` failure even after some error paths have already cleared busy state, so queue behavior should be tested under start failures.
- `ctcm_unpack_skb()` returns on the first malformed packet in a block; malformed trailing data can drop remaining packets.

## Test Signals
- Module load/unload and ccwgroup creation should leave no dangling root devices, ccw handlers, netdevs, channels, tasklets, or timers.
- Online/offline tests should cover both success and rollback after each failure point in `ctcm_new_device()`.
- Packet tests should cover classic S390/OS390/Linux protocols, MTU changes, illegal packet type/length, multi-packet receive blocks, direct and fallback transmit, and MPC TH/PDU formatting.
- IRQ tests should inject unit-check, busy, attention, final-status, subchannel-check, and IRB error cases and verify the emitted FSM events.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_main.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_main.h

## Purpose
`ctcm_main.h` defines the central CTCM driver data structures, constants, protocol identifiers, channel flags, CCW command values, and shared helper declarations. It is the common contract for main driver code, FSM actions, sysfs handlers, and MPC support.

## Important APIs, Types, And Functions
- Defines driver and netdev naming constants: `CTC_DRIVER_NAME`, `CTC_DEVICE_NAME`, `MPC_DEVICE_NAME`, `CTC_DEVICE_GENE`, and `MPC_DEVICE_GENE`.
- Defines channel flags and helpers such as `CHANNEL_FLAGS_READ`, `CHANNEL_FLAGS_WRITE`, `CHANNEL_FLAGS_INUSE`, `CHANNEL_FLAGS_BUFSIZE_CHANGED`, `CHANNEL_DIRECTION()`, and log flags.
- Defines supported protocols: `CTCM_PROTO_S390`, `CTCM_PROTO_LINUX`, `CTCM_PROTO_LINUX_TTY`, `CTCM_PROTO_OS390`, and `CTCM_PROTO_MPC`.
- `struct ctcm_profile` stores runtime transmit profiling counters.
- `struct channel` is the per-ccw-channel state holder for ccws, IRBs, skbs, queues, timers, MPC XID/sweep state, FSM, netdev pointer, flags, and statistics.
- `struct ctcm_priv` is the per-netdev private object containing netdev stats, busy bit, MPC group pointer, device FSM, restart timer, buffer size, and read/write channel pointers.
- Inline helpers implement netdev busy handling, channel id ordering, buffer allocation checks, and MPC protocol checks.
- `struct ll_header` defines the classic CTC link-layer header prepended to packets.

## Control Flow
The header does not execute control flow, but its structures define how control moves. `ctcm_main.c` fills `struct channel` during `add_channel()` and associates two channels with one `struct ctcm_priv` during `ctcm_new_device()`. `ctcm_fsms.c` uses channel flags to choose read vs write behavior and mutates channel/device FSM state. `ctcm_mpc.c` uses the MPC-only fields in `struct channel` and `struct ctcm_priv` to negotiate XID, sweep sequence numbers, and flow control.

## State And Persistence Behavior
All state defined here is in-memory driver state. `struct channel` owns transient DMA buffers, queued skbs, tasklets, timers, and link sequence counters. `struct ctcm_priv` owns per-interface FSM state and stats. `buffer_size` and `protocol` can be changed through sysfs before or during operation subject to validation, but they are not persisted outside the live kernel object.

## Dependencies And Integration Points
The header depends on s390 ccw headers, Linux skbuff/netdevice headers, local `fsm.h`, `ctcm_dbug.h`, and `ctcm_mpc.h`. It is included by every CTCM implementation file. Its busy helpers call `netif_stop_queue()` and `netif_wake_queue()` and are therefore part of the netdev integration contract.

## Risks
- `struct channel` mixes classic and MPC fields; changes for one protocol can accidentally affect layout, initialization, or cleanup for the other.
- The busy helper `ctcm_clear_busy()` suppresses queue wake while MPC sweep is active, so sweep state bugs can stall transmission.
- `ctcm_checkalloc_buffer()` frees and reallocates `trans_skb` if the buffer-size-changed flag is set; callers must ensure no ccw still references the old buffer.
- The macros `IS_MPC()` and `IS_MPCDEV()` assume the pointed object has a `protocol` member or is a `ctcm_priv`; misuse is unchecked.

## Test Signals
- Compile tests should catch structure and prototype drift across `ctcm_main.c`, `ctcm_fsms.c`, `ctcm_mpc.c`, and `ctcm_sysfs.c`.
- Runtime tests should validate busy-bit behavior, buffer reallocation after sysfs changes, protocol-specific MTU limits, and correct read/write channel assignment.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_mpc.c

## Purpose
`ctcm_mpc.c` implements Multi Path Channel protocol support for CTCM. It exports a small channel allocation/connectivity interface, manages MPC group negotiation through XID2(0) and XID2(7), handles flow control and discontact, unpacks MPC TH/PDU traffic, and initializes the MPC group FSM and buffers.

## Important APIs, Types, And Functions
- Exported API: `ctc_mpc_alloc_channel()`, `ctc_mpc_establish_connectivity()`, `ctc_mpc_dealloc_ch()`, and `ctc_mpc_flow_control()`.
- Group lookup and initialization: `ctcmpc_get_dev()` and `ctcmpc_init_mpc_group()`.
- Receive bottom half: `ctcmpc_bh()` drains a channel `io_queue` and calls `ctcmpc_unpack_skb()`.
- MPC group FSM table `mpcg_fsm` and actions: `mpc_action_go_ready()`, `mpc_action_go_inop()`, `mpc_action_timeout()`, `mpc_action_discontact()`, `mpc_action_doxid0()`, `mpc_action_doxid7()`, `mpc_action_rcvd_xid0()`, `mpc_action_rcvd_xid7()`, and `mpc_action_side_xid()`.
- Control helpers: `mpc_validate_xid()`, `mpc_send_qllc_discontact()`, `mpc_rcvd_sweep_req()`, `mpc_rcvd_sweep_resp()`, and `ctcmpc_send_sweep_resp()`.
- Debug helpers are compiled only under `DEBUGDATA`: `ctcmpc_dumpit()` and `ctcmpc_dump_skb()`.

## Control Flow
External users address an MPC netdev by port number. `ctcmpc_get_dev()` resolves names like `mpc0`, validates `ml_priv`, and returns the CTCM private structure. `ctc_mpc_alloc_channel()` records a passive-open callback, marks the port persistent, starts the underlying device if needed, and eventually expects channel-up events to move the group to `MPCG_STATE_XID2INITW`. `ctc_mpc_establish_connectivity()` performs active open from `MPCG_STATE_XID2INITW` by moving to `MPCG_STATE_XID0IOWAIT`, arming the XID timer, and issuing XID0 work on read and write channels that are in the MPC group.

Device FSM channel-up notifications call `mpc_channel_action()`. On add, it increments active read/write counters, allocates a per-channel XID skb from the group template, sets the channel-side DLC type, and transitions the channel to `CH_XID0_PENDING`. When at least one read and one write channel are active, the group can enter passive XID start state. On remove, it decrements counts and can force group INOP if one side disappears.

XID negotiation is two phase. `mpc_action_doxid0()` prepares XID2(0), chooses sense vs write-control command based on active/passive side, and calls `mpc_action_side_xid()` to build ccw[8..14]. `mpc_action_rcvd_xid0()` validates received XID, decrements outstanding XID2, and transitions to XID7 once all initial XIDs arrive. `mpc_action_doxid7()` sends XID2(7) in phase 1 and phase 2 depending on chosen role (`XSIDE` or `YSIDE`) and channel state. `mpc_action_rcvd_xid7()` decrements counters, validates, and eventually moves to `MPCG_STATE_XID7INITF`; a final XID7 done event calls `mpc_action_go_ready()`, which schedules `mpc_group_ready()`.

When ready, `mpc_group_ready()` sets the group ready, posts read I/O, marks write idle, clears busy, and invokes either the establish-connectivity or allocate-channel callback with the negotiated max buffer length. Normal receive uses `ctcmpc_bh()` and `ctcmpc_unpack_skb()`: TH/PDU data is sequence-checked, split into skb packets with a prepended PDU sequence, and delivered via `netif_rx()`. Non-PDU control packets are dispatched as sweep, XID, or discontact events. Flow control moves between `MPCG_STATE_READY` and `MPCG_STATE_FLOWC`, and queued receive processing resumes when flow is released.

## State And Persistence Behavior
MPC group state is volatile and held in `struct mpc_group`. Important fields include callbacks, port number and persistence, active channel counts, outstanding XID counters, selected side, saved received XID, group max buffer length, sweep flags, flow-control flags, and the group FSM/timer. Channel-level MPC state includes XID buffers, TH/PDU sequence counters, sweep queues, discontact tasklets, and `in_mpcgroup`. No state is persisted to disk.

## Dependencies And Integration Points
The file depends on local CTCM channel/device structures, local FSM helpers, and the s390 ccw infrastructure. It exports symbols for an external CCS/SNA consumer. It uses netdev lookup in `init_net`, tasklets for group-ready and receive bottom halves, skbuff APIs for protocol framing, `netif_rx()` for delivery, and `ccw_device_start()` for XID and discontact channel programs.

## Risks
- The exported APIs locate devices by generated netdev name; renaming or namespace assumptions can break callers.
- XID negotiation has many interleaved channel and group states. Races between attention, attention-busy, received XID, and timers can move state unexpectedly if table coverage changes.
- `mpc_validate_xid()` sets `grp->saved_xid2->xid2_flag2` on error even though early NULL paths require care; validation changes must preserve saved-XID lifetime assumptions.
- `ctcmpc_unpack_skb()` requeues out-of-sequence packets and relies on a threshold to declare data loss; repeated requeueing or flow-control pauses can starve processing.
- Several paths deliver synthetic QLLC/discontact packets to the network stack during recovery. Callback ordering and stats should be verified when failures occur mid-negotiation.

## Test Signals
- Passive and active open tests should cover successful XID0/XID7 negotiation, side collision via ATTN-BUSY, invalid XID rejection, callback success/failure values, and INOP recovery.
- Receive tests should cover TH_HAS_PDU data, PDU_FIRST/PDU_LAST/PDU_CNTL flags, sweep request/response, XID control packets, discontact packets, and out-of-sequence handling.
- Flow-control tests should verify `MPCG_STATE_FLOWC` pauses bottom-half processing and resumes queued receive work on release.
- Resource tests should force skb allocation failures and ccw start failures in XID, sweep, normal data, and discontact paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_mpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_mpc.h

## Purpose
`ctcm_mpc.h` defines the MPC protocol structures, constants, group state container, and exported entry points used by the CTCM MPC implementation. It encodes the transport header, XID2 negotiation payload, PDU header, sweep control, QLLC commands, and runtime `struct mpc_group` state.

## Important APIs, Types, And Functions
- Exported external interface declarations: `ctc_mpc_alloc_channel()`, `ctc_mpc_establish_connectivity()`, `ctc_mpc_dealloc_ch()`, and `ctc_mpc_flow_control()`.
- MPC protocol constants: `ETH_P_SNA_DIX`, XID constants (`XID_FM2`, `XID2_0`, `XID2_7`, `XID2_WRITE_SIDE`, `XID2_READ_SIDE`), TH flags, PDU flags, QLLC commands, and group limits/timeouts.
- Packed wire structures: `struct xid2`, `struct th_header`, `struct th_addon`, `struct th_sweep`, `struct pdu`, and `struct qllc`.
- Runtime structures: `struct mpcg_info` bundles a received skb/channel/header/XID/sweep for FSM actions; `struct mpc_group` holds group FSM state, callbacks, counters, sequence negotiation buffers, sweep state, and timers.
- Internal function declarations used across files: `mpc_group_ready()`, `mpc_channel_action()`, `mpc_action_send_discontact()`, `mpc_action_discontact()`, and `ctcmpc_bh()`.

## Control Flow
The header provides the structures consumed by `ctcm_mpc.c` and the MPC-specific actions in `ctcm_fsms.c`. `struct mpc_group` fields are mutated as channels are added, XID exchanges progress, data becomes ready, flow control toggles, or recovery begins. Packed protocol structures are pushed onto or parsed from skbs in the transmit and receive paths.

## State And Persistence Behavior
This header defines in-memory runtime state, not persistent storage. `struct mpc_group` is allocated during netdev initialization and freed with the netdev. Its callbacks and counters survive across short recovery cycles while the device exists, but are reset during INOP/deallocation paths.

## Dependencies And Integration Points
The file includes Linux interrupt/skbuff types and local `fsm.h`. It is included by `ctcm_main.h`, so it is transitively visible to the main driver and FSM code. Packed structure layout is an integration point with remote MPC/SNA peers and cannot be changed casually.

## Risks
- Packed wire structure changes affect interoperability and skb parsing directly.
- `struct mpc_group` is large and stateful; partial initialization or cleanup changes can leave callbacks, timers, or skbs stale.
- The external API comment says calls are made with a lock, but the specific lock is not documented in the header, making caller obligations ambiguous.
- Constants such as `MAX_MPCGCHAN`, `MPC_XID_TIMEOUT_VALUE`, and buffer length calculations need consistency with hardware/peer expectations.

## Test Signals
- Compile tests should verify packed struct sizes and offsets if protocol conformance tests exist.
- XID negotiation tests should confirm `struct xid2` fields and TH headers are serialized as expected.
- Group lifecycle tests should verify callbacks, timers, and saved XID buffers are initialized and cleared around ready, INOP, and dealloc flows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_sysfs.c

## Purpose
`ctcm_sysfs.c` defines the ccwgroup device sysfs attributes for CTCM. It exposes buffer size, protocol, channel type, and a stats trigger/reset interface through the `ctcm_attr_groups` attribute group consumed by `ctcm_main.c`.

## Important APIs, Types, And Functions
- `ctcm_buffer_show()` and `ctcm_buffer_write()` expose and update `priv->buffer_size` and both channels' `max_bufsize`.
- `ctcm_print_statistics()` formats current device/channel FSM states and write-channel profiling counters to the kernel log.
- `stats_show()` triggers statistics printing and returns `0`; `stats_write()` clears write-channel profiling counters.
- `ctcm_proto_show()` and `ctcm_proto_store()` expose and set the protocol field.
- `ctcm_type_show()` reports the ccw channel type based on `driver_info`.
- Defines `DEVICE_ATTR(buffer)`, `DEVICE_ATTR(protocol)`, `DEVICE_ATTR(type)`, `DEVICE_ATTR(stats)`, and exports `ctcm_attr_groups`.

## Control Flow
The sysfs group is attached through the `ctcm_devtype` in `ctcm_main.c`. Reads validate that private data and, for stats, online state exist before reporting. Buffer writes parse an unsigned integer, validate maximum and minimum classic CTC buffer sizes, reject running devices if the requested buffer is smaller than the current MTU plus header overhead, update both channel max buffer sizes, and mark both channels with `CHANNEL_FLAGS_BUFSIZE_CHANGED` so the next buffer check reallocates safely. Protocol writes accept S390, Linux, MPC, or OS390 protocol values and update `priv->protocol`.

## State And Persistence Behavior
All sysfs writes update live in-memory driver state. Buffer changes affect `priv->buffer_size`, both channel `max_bufsize` values, current netdev MTU if the interface is down, and the buffer-size-changed flags. Stats writes clear only `priv->channel[WRITE]->prof`. Values are lost when the device is removed or module unloaded.

## Dependencies And Integration Points
The file depends on `ctcm_main.h` for `struct ctcm_priv`, channel constants, buffer limits, protocol values, debug macros, and FSM helpers. It integrates with Linux device attributes and ccwgroup device state. Statistics output depends on FSM instances being valid and channels being present.

## Risks
- `ctcm_proto_store()` does not check whether the device is already online/running, so protocol changes after setup may not reinitialize existing channel state consistently.
- Buffer validation is classic-header based and does not use MPC TH/PDU overhead; MPC buffer changes should be treated cautiously.
- `stats_show()` logs details to the kernel log rather than returning them through sysfs, which can surprise tests and users.
- The code uses `WRITE` in a few `priv->channel[WRITE]` references; correctness depends on local/global constants resolving as intended.

## Test Signals
- Sysfs tests should verify accepted and rejected buffer sizes, including running vs stopped interface behavior.
- Protocol tests should verify valid protocol numbers and invalid values.
- Stats tests should verify show logs FSM/profile information only for online devices and write clears profiling counters.
- Type tests should verify ccw `driver_info` indexes map to expected strings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/fsm.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/fsm.c

## Purpose
`fsm.c` implements a generic table-driven finite state machine helper used by the CTCM driver and exported to other modules. It allocates FSM instances, builds jump matrices from `fsm_node` templates, dispatches events, stores atomic state, and provides timer helpers that translate Linux timer expiry into FSM events.

## Important APIs, Types, And Functions
- `init_fsm()` allocates `fsm_instance`, `fsm`, and a `nr_states * nr_events` jump matrix, validates template entries, and installs action functions.
- `kfree_fsm()` frees the jump matrix, FSM descriptor, and instance.
- `fsm_getstate_str()` returns the current state name or `"Invalid"`.
- `fsm_settimer()` initializes an `fsm_timer` with `timer_setup()`.
- `fsm_deltimer()` deletes a timer.
- `fsm_addtimer()` and `fsm_modtimer()` arm or rearm timers and store the event/argument to dispatch on expiry.
- Under `FSM_DEBUG_HISTORY`, `fsm_print_history()` and `fsm_record_history()` maintain a circular event/state history.
- Exports all public helpers with `EXPORT_SYMBOL`.

## Control Flow
`init_fsm()` is called by CTCM channel, device, and MPC group initialization. It converts a sparse list of `(state,event,function)` entries into a direct-indexed matrix indexed as `nr_states * event + state`. Runtime event dispatch mostly happens through the inline `fsm_event()` in `fsm.h`, but the action functions and table backing are provided here. Timer expiry runs `fsm_expire_timer()`, obtains the enclosing `fsm_timer`, and calls `fsm_event()` with the stored event and argument.

## State And Persistence Behavior
FSM state is stored in `fsm_instance.state` as an `atomic_t`; state names, event names, and jump matrices are allocated per instance. Timers store only the target FSM, event, and argument. All state is in-memory and freed by `kfree_fsm()`. There is no persistent storage.

## Dependencies And Integration Points
The implementation depends on Linux allocation, timers, exports, and module metadata. It relies on `fsm.h` for types and inline dispatch. CTCM integrates by embedding `fsm_instance *` pointers and `fsm_timer` objects in driver structures.

## Risks
- `fsm_addtimer()` does not reject already-active timers despite the header comment claiming `-1` is possible; callers must delete or avoid duplicate adds themselves.
- `timer_delete()` is used rather than a synchronous delete, so callers freeing structures must ensure no timer callback can still race.
- The jump matrix is per-instance rather than shared per template, which is simple but increases allocation pressure.
- Invalid template entries free partial allocations through `kfree_fsm()`; future changes must preserve `this->f` assignment ordering.

## Test Signals
- Unit-style tests should initialize small FSMs, dispatch valid and missing events, validate state names, and verify out-of-range template entries fail.
- Timer tests should verify expiry dispatches the expected event/argument and deletion prevents callback under expected synchronization.
- Driver tests should watch for timer-after-free warnings during device teardown.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/fsm.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/fsm.h

## Purpose
`fsm.h` defines the generic finite state machine types and inline operations used by the s390 networking drivers. It provides the data model for FSM descriptors, FSM instances, transition templates, timers, and event dispatch.

## Important APIs, Types, And Functions
- `fsm_function_t` is the action function signature.
- `fsm` stores the jump matrix dimensions and diagnostic name arrays.
- `fsm_instance` stores the current atomic state, instance name, optional user fields, wait queue, and optional debug history.
- `fsm_node` describes one transition table entry.
- `fsm_timer` binds a Linux timer to an FSM event and argument.
- Declares lifecycle and timer helpers implemented in `fsm.c`: `init_fsm()`, `kfree_fsm()`, `fsm_getstate_str()`, `fsm_settimer()`, `fsm_deltimer()`, `fsm_addtimer()`, and `fsm_modtimer()`.
- Inline `fsm_event()` validates current state and event, looks up the matrix entry, optionally records debug history, and invokes the action.
- Inline `fsm_newstate()` atomically sets state and wakes waiters; `fsm_getstate()` reads current state.

## Control Flow
Callers build a template array of `fsm_node` entries and pass it to `init_fsm()`. After that, `fsm_event()` is the hot path: it reads the current state, validates indexes against the descriptor, computes the jump-matrix slot, and invokes the action if present. Actions usually call `fsm_newstate()` or emit more events. Timers are represented as delayed calls to `fsm_event()`.

## State And Persistence Behavior
The header defines runtime-only state. `fsm_instance.state` is atomic and can be observed by concurrent contexts, but action execution itself is not serialized by the FSM helper. Wait queues are woken on state changes, but this CTCM code mostly uses the FSM for event dispatch rather than blocking waits.

## Dependencies And Integration Points
The header depends on Linux kernel, timer, wait queue, allocation, string, scheduler, and atomic APIs. It is included by both CTCM and MPC headers and therefore forms a foundational local API. Debug switches are compile-time macros.

## Risks
- `fsm_event()` does not lock around state lookup and action invocation. Concurrent events can race unless callers provide external serialization.
- Missing state/event actions are not fatal by default; they return nonzero and optionally log only when debug is enabled.
- `fsm_newstate()` accepts any integer without range validation, so action functions must set valid states.
- Timer callbacks run in timer context and call arbitrary action functions; those actions must be safe for that context.

## Test Signals
- Static checks should confirm every state set by action functions is within the instance's configured range.
- Concurrency tests should focus on callers that can emit events from IRQ, tasklet, timer, and process contexts.
- Debug builds with history enabled can validate unexpected missing transitions during fault injection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/fsm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ism.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ism.h

## Purpose
`ism.h` defines the s390 ISM PCI device command ABI, event queue structures, summary-bit area layout, device state container, and low-level zpci command/move helpers used by `ism_drv.c`. It is the wire/register contract between the Linux ISM driver, DIBS clients, and the s390 PCI instruction interface.

## Important APIs, Types, And Functions
- Command codes: `ISM_REG_SBA`, `ISM_REG_IEQ`, `ISM_READ_GID`, VLAN commands, query commands, DMB register/unregister, signal IEQ, and unregister commands.
- Event constants: `enum ism_event_type` and `enum ism_event_code`.
- Request/response headers: `struct ism_req_hdr` and `struct ism_resp_hdr`.
- Command unions with alignment requirements: `ism_reg_sba`, `ism_reg_ieq`, `ism_read_gid`, `ism_qi`, `ism_query_rgid`, `ism_reg_dmb`, `ism_sig_ieq`, `ism_unreg_dmb`, `ism_cmd_simple`, and `ism_set_vlan_id`.
- Event and shared-memory layouts: `struct ism_eq_header`, `struct ism_event`, `struct ism_eq`, and `struct ism_sba`.
- Runtime device state: `struct ism_dev` holds command lock, DIBS/PPCI pointers, coherent SBA/IEQ DMA mappings, DMB allocation bitmap, and event queue index.
- Inline hardware helpers: `__ism_read_cmd()`, `__ism_write_cmd()`, and `__ism_move()` use zpci load/store instructions.

## Control Flow
`ism_drv.c` fills the command unions, writes payload after the request header, writes the header to trigger a command, then reads the response header and payload. DMB movement uses `ISM_CREATE_REQ()` to compose a device memory buffer request and `__ism_move()` to store data through zpci. IRQ handling reads and clears `struct ism_sba` bits and scans `struct ism_eq` entries defined here.

## State And Persistence Behavior
The header describes hardware-visible memory that persists only while the driver has registered coherent pages with the device. `struct ism_sba` contains summary/event bits, DMB bits, and masks updated by the device and cleared by the interrupt handler. `struct ism_eq` contains an event ring. `struct ism_dev` tracks the live software view.

## Dependencies And Integration Points
This file depends on Linux PCI, spinlock, DIBS, and s390 zpci instruction headers. It is directly consumed by `ism_drv.c` and indirectly defines the DIBS provider behavior exposed to clients. Alignment attributes are integration-critical for the device ABI.

## Risks
- Command unions and alignment must match hardware expectations exactly. Field reordering or type-size changes can break device commands.
- `__ism_read_cmd()` and `__ism_write_cmd()` assume 8-byte granularity and command lengths consistent with the hardware protocol.
- `struct ism_sba` reserves the first DMB word for alignment; bitmap indexing must consistently account for `ISM_DMB_BIT_OFFSET`.
- UUID/GID mapping comments indicate compatibility behavior; changing GID layout can break remote matching.

## Test Signals
- Hardware or emulator tests should verify every command union length/alignment and command code path.
- IRQ tests should validate SBA bit indexing and IEQ ring entry parsing.
- DIBS client tests should validate DMB registration, move requests across page boundaries, VLAN operations, and event signaling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ism.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ism_drv.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ism_drv.c

## Purpose
`ism_drv.c` implements the s390 ISM PCI driver and exposes ISM devices as DIBS devices. It manages PCI probe/remove, command serialization, summary-bit and interrupt-event queue registration, DMB allocation and registration, VLAN/GID commands, data movement, interrupt dispatch, and DIBS client notifications.

## Important APIs, Types, And Functions
- PCI/module integration: `ism_device_table`, `ism_driver`, `ism_init()`, `ism_exit()`, `ism_probe()`, and `ism_remove()`.
- Command path: `ism_cmd()`, `ism_cmd_simple()`, `query_info()`, `register_sba()`, `register_ieq()`, `unregister_sba()`, and `unregister_ieq()`.
- DIBS operations in `ism_ops`: `ism_get_chid()`, `ism_query_rgid()`, `ism_max_dmbs()`, `ism_register_dmb()`, `ism_unregister_dmb()`, `ism_move()`, VLAN add/delete, and `ism_signal_ieq()`.
- DMB memory management: `ism_alloc_dmb()`, `ism_free_dmb()`, and bitmap management with `sba_bitmap`.
- Interrupt/event path: `ism_handle_irq()`, `ism_handle_event()`, `ism_match_event_type()`, and `ism_match_event_subtype()`.
- Device setup/teardown: `ism_dev_init()` and `ism_dev_exit()`.

## Control Flow
On module init, `ism_init()` registers a s390 debug area and the PCI driver. `ism_probe()` allocates `struct ism_dev`, enables PCI memory access, requests regions, sets a 64-bit DMA mask and segment constraints, allocates a DIBS device, wires `dibs->drv_priv` and ops, then calls `ism_dev_init()`. Device init allocates one MSI vector, requests the IRQ, registers a coherent summary-bit area and interrupt-event queue with the device, and queries device info. After local GID is read, probe names and registers the DIBS device so clients can subscribe.

`ism_cmd()` serializes device commands with `cmd_lock`. It writes the request payload, writes the request header to trigger the command, initializes the response return to `ISM_ERROR`, reads the response header, logs failures, and reads the response payload on success. Higher-level helpers fill the specific aligned command union and call `ism_cmd()`.

DMB registration allocates a folio of requested size, maps it for DMA_FROM_DEVICE, chooses or validates an SBA bitmap index above `ISM_DMB_BIT_OFFSET`, sends `ISM_REG_DMB`, stores the returned token, and records the owning DIBS client id under `dibs->lock`. Unregistration clears the client id first, sends `ISM_UNREG_DMB`, tolerates `ISM_ERROR` during teardown, and frees/unmaps the DMB.

The IRQ handler clears the summary bit, scans inverted DMB bits, clears each bit and mask, looks up the DIBS client id, and calls the client's `handle_irq()` with the DMB index and mask. If the event bit is set, it clears it and calls `ism_handle_event()`, which walks the IEQ ring, maps s390 event type/subtype to DIBS event values, fills `struct dibs_event`, and broadcasts to subscribed clients.

## State And Persistence Behavior
The driver keeps live state in `struct ism_dev`: PCI/DIBS pointers, command lock, coherent SBA and IEQ memory, DMA addresses, DMB allocation bitmap, and event queue index. DIBS state stores client subscriptions and DMB owner ids. Hardware-visible registrations persist only until `ism_dev_exit()` unregisters IEQ/SBA and frees IRQ vectors. There is no disk persistence.

## Dependencies And Integration Points
The file integrates with Linux PCI, DMA mapping, MSI IRQs, s390 debug features, zpci helpers from `ism.h`, DIBS device/client APIs, and folio memory allocation. It is a provider for DIBS clients, so its operation table and event mappings are external behavioral contracts.

## Risks
- `ism_cmd()` depends on strict command ordering under `cmd_lock`; any unlocked direct command path would corrupt device command state.
- DMB allocation uses a folio but the DMA mapping failure path calls `kfree(dmb->cpu_addr)` instead of folio-specific release, which is a code path worth auditing against the kernel version's allocation semantics.
- `ism_unregister_dmb()` clears the DIBS client id before the hardware unregister command completes, so failures can leave hardware state with software no longer routing interrupts for that DMB.
- IRQ scanning uses inverted bit operations and offset arithmetic; off-by-one errors would dispatch wrong DMB indexes or miss events.
- Event broadcast holds `dibs->lock` while invoking client callbacks through `ism_handle_event()` from the IRQ handler, so client callback locking and latency constraints matter.

## Test Signals
- Probe/remove tests should verify all rollback labels free IRQs, DMA pages, DIBS devices, PCI regions, and driver data.
- Command tests should cover success and nonzero response codes for all command helpers, including teardown with `ISM_ERROR`.
- DMB tests should cover requested index, auto index allocation, duplicate indexes, too-large buffers, DMA mapping failure, register failure cleanup, and unregister failure.
- IRQ tests should cover DMB bit delivery, event queue wraparound, no-client cases, client callback dispatch, and mixed DMB/event interrupts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ism_drv.c -->
