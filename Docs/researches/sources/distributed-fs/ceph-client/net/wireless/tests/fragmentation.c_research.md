# sources/distributed-fs/ceph-client/net/wireless/tests/fragmentation.c

## Purpose
`fragmentation.c` tests `cfg80211_defragment_element()` for normal and fragmented 802.11 elements, with emphasis on EHT Multi-Link extension elements and trailing fragment handling.

## Important APIs, Types, And Functions
The suite defines `defragment_0()`, `defragment_1()`, `defragment_2()`, and `defragment_at_end()`, registered as KUnit suite `cfg80211-element-defragmentation`. The production API under test is `cfg80211_defragment_element()` from `scan.c`.

## Control Flow
Each test builds a static IE byte stream, optionally counts elements with `for_each_element()`, first calls the helper with `data == NULL` to get the required output length, then calls again with an allocated buffer and validates copied payload bytes. The cases cover no fragmentation, one used fragment with a later unused fragment, two used fragments with a later unused fragment, and a used fragment at the end of the stream.

## State And Persistence
The suite has no persistent state; KUnit allocates temporary output buffers per test.

## Dependencies And Integration Points
The tests depend on Linux 802.11 element constants, cfg80211's exported defragment helper, KUnit allocation/assertion APIs, and normal IE iteration macros.

## Risks And Edge Cases
Fragment handling is security-sensitive because malformed management frames are untrusted. The tests assert that an extension element skips the extension ID byte, that only 255-byte elements continue into fragments, that short fragments terminate defragmentation, and that later fragment elements are ignored once the current fragmented element is complete.

## Test Signals
Passing tests show correct length calculation and byte-for-byte reconstruction for unfragmented, singly fragmented, multiply fragmented, and end-of-buffer fragmented elements, including correct refusal to consume unrelated later fragments.
