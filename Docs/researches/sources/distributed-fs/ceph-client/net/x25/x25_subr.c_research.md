# sources/distributed-fs/ceph-client/net/x25/x25_subr.c

Purpose: contains shared X.25 protocol subroutines for queue cleanup, acknowledgement accounting, retransmission requeue, frame generation, frame decoding, disconnect, and receive-buffer recovery.

Important APIs/functions: `x25_clear_queues()`, `x25_frames_acked()`, `x25_requeue_frames()`, `x25_validate_nr()`, `x25_write_internal()`, `x25_decode()`, `x25_disconnect()`, and `x25_check_rbuf()` are used across input, output, timers, and socket teardown.

Control flow: acknowledgement helpers remove or requeue frames based on `va/vs` and modulus. Internal frame writing sizes an skb for the requested control frame, writes GFI/LCI, emits call request/accepted facilities and CUD, clear/reset cause bytes, RR/RNR/REJ sequence fields, or confirmations, then sends through the link. Decode validates skb length and returns frame type plus parsed sequence, Q/D/M bits. Disconnect clears queues/timer, resets state, records cause, shuts down socket, wakes waiters, marks dead, and drops neighbour reference.

State and persistence: mutates all per-socket packet-layer queues, sequence variables, condition flags, LCI, state, error/shutdown, cause/diagnostic, call user data length, and neighbour reference.

Dependencies and integration: depends on facilities/address helpers, link transmit, timers, socket memory queues, and constants for standard versus extended sequence encodings.

Risks and test signals: frame encoding/decoding bugs can desynchronize peers. Tests should cover every control frame type, standard/extended RR/RNR/DATA sequence fields, invalid PLP frames, ACK wraparound, reset requeue ordering, disconnect neighbour put, receive-buffer busy clearing, and generated call request/accepted contents.
