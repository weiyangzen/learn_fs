# sources/distributed-fs/ceph-client/net/lapb/lapb_in.c

## Purpose
`lapb_in.c` implements the LAPB receive-side state machine. It decodes an incoming frame and dispatches it to one of five state handlers: disconnected, awaiting connection, awaiting release, connected, or frame-reject.

## Important APIs, Types, and Functions
The externally called entry point is `lapb_data_input()`. Internal handlers are `lapb_state0_machine()`, `lapb_state1_machine()`, `lapb_state2_machine()`, `lapb_state3_machine()`, and `lapb_state4_machine()`. They operate on `struct lapb_cb`, `struct sk_buff`, and decoded `struct lapb_frame` produced by `lapb_decode()`.

## Control Flow
State 0 responds to SABM/SABME only when the configured normal/extended mode matches, otherwise DM is sent; successful establishment resets sequence variables and raises connect indication. State 1 processes UA/DM responses to an outgoing SABM(E), confirming connection or refusal. State 2 processes release completion through UA/DM and rejects unexpected traffic. State 3 is data transfer: it handles reset SABM(E), DISC/DM disconnects, supervisory RR/RNR/REJ acknowledgments, I-frame receive/ack/reject behavior, FRMR reset, and illegal-frame transition to state 4. State 4 handles reset SABM(E) from frame-reject state. Each path frees or transfers skb ownership and calls `lapb_kick()` afterward to continue output.

## State and Persistence
The handler mutates LAPB state number, condition flags, retry count, sequence variables `vs`, `vr`, `va`, frame-reject metadata, and timers. The only durable effect is in-memory control block state and queued skb ownership.

## Dependencies and Integration Points
It relies on helpers from `lapb_subr.c` for decode, validation, queue management, control transmission, and FRMR generation; `lapb_out.c` for establishment, response, and retransmission; and `lapb_timer.c` for timer control. Upper-layer callbacks are reached through `lapb_data_indication()` and connection/disconnection indication helpers.

## Risks and Edge Cases
Frame ownership is subtle: I-frames successfully delivered to the upper layer are marked queued and not freed locally, while dropped indications intentionally skip protocol advancement so the peer retransmits. Sequence-number validation failure drives FRMR/state 4 behavior. Mode mismatch between SABM and SABME must not establish the wrong modulus. Missing `pskb_may_pull()` coverage is delegated to decode.

## Test Signals
Protocol tests should replay valid and invalid SABM/SABME, DISC, UA, DM, RR/RNR/REJ, I, FRMR, and illegal frames across all states. Include congestion/drop return from `data_indication`, normal vs extended modulus wrapping, reject-condition behavior, and timer interaction after state transitions.
