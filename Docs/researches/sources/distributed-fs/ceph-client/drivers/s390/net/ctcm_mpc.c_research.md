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
