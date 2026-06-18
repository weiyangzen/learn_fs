# sources/distributed-fs/ceph-client/net/lapb/lapb_out.c

## Purpose
`lapb_out.c` builds and transmits outbound LAPB I-frames and selected control responses. It moves queued user data into the transmit window, assigns sequence numbers, and starts retransmission timers.

## Important APIs, Types, and Functions
Key functions are `lapb_kick()`, `lapb_transmit_buffer()`, `lapb_establish_data_link()`, `lapb_enquiry_response()`, `lapb_timeout_response()`, `lapb_check_iframes_acked()`, and `lapb_check_need_response()`. The internal `lapb_send_iframe()` formats normal or extended I-frame control fields.

## Control Flow
`lapb_kick()` checks peer busy state, transmit window availability, and `write_queue` contents. It copies each original skb for transmission, sends the copy as an I-frame, advances `vs`, and queues the original skb on `ack_queue` until acknowledged. `lapb_transmit_buffer()` prepends the LAPB address byte according to DCE/DTE and MLP modes, then calls the registered `data_transmit` callback. Establishment sends SABM or SABME with poll set and starts T1. Enquiry and timeout responses send RR responses and clear pending-ack state.

## State and Persistence
This file mutates `vs`, condition flags, the write and ack queues, and T1 state. It does not persist data beyond skb queues and LAPB control block fields.

## Dependencies and Integration Points
It depends on skbuff queue APIs, callback dispatch through `lapb_data_transmit()`, control generation in `lapb_subr.c`, and timer helpers. The upper network device driver is responsible for actual frame transmission once the callback is invoked.

## Risks and Edge Cases
`skb_copy()` failure requeues the original skb and stalls additional sends. Transmit window arithmetic must match the selected modulus. Address-byte selection changes with DCE and MLP mode. Timer startup happens only when outstanding data exists and T1 is not already running; mistakes here affect retransmission.

## Test Signals
Validate window fill behavior, retransmit queue ordering, normal and extended header bytes, DCE/DTE address selection, MLP address selection, callback failure skb free behavior, and T1 startup when the first unacknowledged I-frame is sent.
