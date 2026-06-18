# sources/distributed-fs/ceph-client/net/lapb/lapb_subr.c

## Purpose
`lapb_subr.c` contains shared LAPB helpers for queue cleanup, acknowledgement processing, sequence validation, frame decoding, control-frame construction, and FRMR generation.

## Important APIs, Types, and Functions
Important helpers include `lapb_clear_queues()`, `lapb_frames_acked()`, `lapb_requeue_frames()`, `lapb_validate_nr()`, `lapb_decode()`, `lapb_send_control()`, and `lapb_transmit_frmr()`.

## Control Flow
Acknowledgment helpers remove acked skbs from `ack_queue` while advancing `va`, or requeue all unacknowledged frames back to `write_queue` in order for retransmission. `lapb_validate_nr()` walks the circular sequence interval from `va` to `vs`. `lapb_decode()` pulls address and control bytes from the skb, determines command/response direction based on DCE/DTE and MLP modes, and fills `struct lapb_frame` for normal or extended I/S/U formats. Control send helpers allocate small skbs, encode S/U control fields, and pass them to `lapb_transmit_buffer()`.

## State and Persistence
State changes are limited to queue contents, `va`, and skb data pointers. FRMR construction uses `lapb->frmr_data`, `frmr_type`, `vs`, and `vr` captured by the input state machine.

## Dependencies and Integration Points
The file underpins both receive and timer paths. It depends on `pskb_may_pull()` for safe header access, skbuff queue operations, LAPB constants from `net/lapb.h`, and `lapb_transmit_buffer()` from the output path.

## Risks and Edge Cases
Decode must not read beyond skb linear data, and it must pull the correct number of bytes for normal versus extended formats. Command/response derivation is mode-sensitive and affects protocol legality. Circular sequence validation is central to avoiding false FRMR or missed acknowledgments. Requeue ordering must preserve retransmit order.

## Test Signals
Unit-style frame decode tests should cover all address modes, normal/extended I/S/U frames, short skbs, invalid controls, and command/response classification. Queue tests should validate ack removal and retransmit requeue order across sequence wrap.
