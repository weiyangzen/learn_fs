# sources/distributed-fs/ceph-client/net/batman-adv/bitarray.c

## Purpose
`bitarray.c` implements sequence-number receive-window movement for BATMAN IV. It tracks which recent OGMs were seen so duplicate detection and packet-count-based TQ calculations can work.

## Important Functions
- `batadv_bitmap_shift_left`: shifts a bitmap by a positive in-window delta.
- `batadv_bit_get_packet`: updates a sequence bitmap based on `seq_num_diff` and optionally marks the received packet.

## Control Flow
Slightly older packets within the local window are marked without moving the window. Slightly newer packets shift the window and mark bit zero. Much newer packets clear the window, log missed packets, and mark the new head. Much older packets or values outside expected range are treated as likely peer restart: the window is cleared and the new packet can be marked.

## State and Persistence
The file owns no global state. It mutates caller-owned bitmaps, typically per-neighbor/per-originator BATMAN IV receive windows. Debug logging uses the passed `bat_priv`.

## Dependencies and Integration
Used heavily by `bat_iv_ogm.c` for real receive windows and own-broadcast windows. Depends on bitmap helpers, BATMAN window constants, and debug logging.

## Risks and Test Signals
Risks include signed sequence-difference wrap behavior, off-by-one window shifts, and restart/missed-packet classification. Test signals include unit-style checks for older/newer/much-newer/much-older diffs, duplicate detection through `batadv_test_bit`, and BATMAN IV route behavior under reordered or skipped OGMs.
