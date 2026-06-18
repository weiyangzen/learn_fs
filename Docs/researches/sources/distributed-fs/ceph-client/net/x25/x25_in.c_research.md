# sources/distributed-fs/ceph-client/net/x25/x25_in.c

Purpose: implements the X.25 Packet Layer receive state machine for connection establishment, connected data transfer, reset, clear, interrupt handling, and accept-approval pending state.

Important APIs/functions: `x25_process_rx_frame()` is the main receive dispatcher and `x25_backlog_rcv()` is the socket backlog callback. Internal state handlers cover states 1 through 5, and `x25_queue_rx_frame()` handles M-bit fragmentation reassembly.

Control flow: receive decodes frame type/sequence bits with `x25_decode()`, dispatches by `x25->state`, then calls `x25_kick()`. State 1 processes call accepted, call collision, and clear. State 2 waits for clear confirmation. State 3 handles reset, clear, RR/RNR acknowledgements, DATA sequence validation and receive queuing, delayed acknowledgements, and interrupts. State 4 waits for reset confirmation. State 5 waits for explicit call-accepted approval while accepting clear requests.

State and persistence: mutates PLP state, `vs/vr/va/vl`, condition flags, socket state/error, receive and fragment queues, interrupt queues, timers, facilities, call user data, and cause/diagnostic fields. Reassembled records persist on `sk_receive_queue` until userspace receives them.

Dependencies and integration: depends on subroutines for frame decoding, queue clearing, acknowledgement, reset/clear generation, and disconnect; on timers for T2/T22/T23; and on `x25_out.c` for kick/enquiry response.

Risks and test signals: sequence-number validation and fragment reassembly are critical. Tests should cover standard and extended modulus, out-of-order DATA triggering reset, invalid `nr`, full receive buffer setting RNR, fragmented packets over USHRT_MAX, interrupt inline and out-of-band modes, clear/reset races in every state, and malformed short frames.
