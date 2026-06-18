# sources/distributed-fs/ceph-client/net/batman-adv/bitarray.h

## Purpose
`bitarray.h` declares and partly implements bitmap helpers for BATMAN IV sequence tracking.

## Important APIs
- `batadv_test_bit`: returns whether `curr_seqno` is present in a receive window anchored at `last_seqno`, rejecting future or too-old values.
- `batadv_set_bit`: marks a relative sequence position if it is inside the local window.
- `batadv_bit_get_packet`: declared implementation for moving/marking windows.

## Control Flow and State
The inline helpers operate on caller-owned `unsigned long` bitmaps. They use signed differences to map sequence numbers to bit positions and silently ignore invalid relative positions.

## Dependencies and Integration
Used by BATMAN IV OGM duplicate detection and TQ packet-count logic. Depends on `BATADV_TQ_LOCAL_WINDOW_SIZE`, Linux bitops, and integer types.

## Risks and Test Signals
Risks include wraparound semantics and callers passing unprotected bitmaps without the relevant originator lock. Test signals include boundary tests for diff `-1`, `0`, `BATADV_TQ_LOCAL_WINDOW_SIZE - 1`, and out-of-window values, plus BATMAN IV duplicate suppression tests.
