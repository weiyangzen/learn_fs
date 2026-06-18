# sources/distributed-fs/ceph-client/net/x25/x25_out.c

Purpose: handles outbound X.25 data fragmentation, transmit window scheduling, interrupt transmission, and acknowledgement/enquiry responses.

Important APIs/functions: `x25_output()` queues user data frames and fragments by negotiated packet size; `x25_kick()` transmits queued data subject to peer busy and window limits; `x25_enquiry_response()` sends RR/RNR based on receive-buffer state.

Control flow: `x25_output()` compares user data length to negotiated packet size, preserves the header, splits data into packet-size chunks, sets the M bit on all but the final fragment, and queues frames on `sk_write_queue`. `x25_kick()` sends one pending interrupt if allowed, skips data when peer RNR is set, computes the send window from `va`, `vs`, and `winsize_out`, clones each queued skb for transmission, updates `vs`, and moves originals to `ack_queue` for retransmission until acknowledged.

State and persistence: mutates write queue, ack queue, interrupt queue, sequence variables, `X25_INTERRUPT_FLAG`, and ACK pending condition. Unacknowledged frames persist in `ack_queue` until `x25_frames_acked()` frees them.

Dependencies and integration: used by `af_x25.c` sendmsg and `x25_in.c` receive processing. Relies on link transmit, socket memory ownership, negotiated facilities, timers, and subroutine acknowledgement helpers.

Risks and test signals: fragmentation and window accounting are high-risk, especially nonblocking allocation returning partial bytes sent. Tests should cover standard/extended headers, M-bit fragmentation, pacsize defaults, peer busy suppression, interrupt confirmation gating, clone failure requeue, ACK queue retransmission after reset, and delayed ACK clearing.
