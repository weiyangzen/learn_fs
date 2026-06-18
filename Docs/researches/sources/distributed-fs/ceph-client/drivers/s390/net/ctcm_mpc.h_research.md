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
