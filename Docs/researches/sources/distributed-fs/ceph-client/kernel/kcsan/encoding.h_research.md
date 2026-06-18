# sources/distributed-fs/ceph-client/kernel/kcsan/encoding.h

## Purpose
Defines how KCSAN encodes a watched access into one atomic long and maps addresses to watchpoint slots.

## Important APIs, Types, and Functions
Key constants are `SLOT_RANGE`, `INVALID_WATCHPOINT`, `CONSUMED_WATCHPOINT`, `MAX_ENCODABLE_SIZE`, address/size/write bit masks, and `WATCHPOINT_ADDR_BITS`. Inline helpers are `check_encodable`, `encode_watchpoint`, `decode_watchpoint`, `watchpoint_slot`, and `matching_access`.

## Control Flow
`core.c` calls `check_encodable` before installing a watchpoint, stores the encoded address/size/write bit with `encode_watchpoint`, later decodes candidate slots, and uses `matching_access` to check overlap. `report.c` also uses `matching_access` to reject encoding false positives.

## State and Persistence
No state is stored in the header. It defines the bit layout used by atomic watchpoint slots in `core.c`.

## Dependencies and Integration Points
Depends on page size, bit helpers, log2 helpers, and `NUM_SLOTS` from `kcsan.h`. The layout assumes enough unused virtual-address bits on common architectures and deliberately masks high address bits.

## Risks
Encoding truncates addresses, so two different addresses can map to the same encoded address and slot. The reporting path must filter actual address mismatches. `MAX_ENCODABLE_SIZE` bounds what KCSAN can watch precisely.

## Test Signals
`kcsan/selftest.c` repeatedly randomizes addresses, sizes, and write bits to ensure encode/decode round-trips and that invalid/consumed sentinels are rejected.
