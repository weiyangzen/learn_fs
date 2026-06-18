# sources/distributed-fs/ceph-client/include/net/pptp.h

Purpose: defines PPTP GRE header layout and sequence/window constants used by PPTP tunneling.

Important APIs and types: constants define PPP LCP echo request/reply codes, receive status bit mask, missing window size, sequence wrap detection macro, and header overhead. `struct pptp_gre_header` packs a GRE base header plus payload length, call ID, sequence, and acknowledgment fields.

Control flow: PPTP data paths parse GRE headers, track sequence/ack windows, detect wraparound, and account encapsulation overhead.

State and persistence: no state is stored here; tunnel/session implementations maintain sequence state.

Dependencies and integration points: depends on `net/gre.h` and Linux types; integrates PPTP with GRE and PPP handling.

Risks and test signals: risks include packed header alignment, sequence wrap edge cases, missing-window handling, and overhead miscalculation. Test GRE/PPTP packet parsing, sequence wrap from `0xffffffxx` to zero, LCP echo traffic, and malformed header lengths.
