# sources/distributed-fs/ceph-client/block/badblocks.c

## Purpose
`badblocks.c` implements a compact in-kernel bad-sector range table for block devices and related subsystems. It tracks acknowledged and unacknowledged bad ranges, supports querying, adding, clearing, acknowledging, and sysfs text import/export.

## Important APIs, types, and functions
The exported API is `badblocks_check`, `badblocks_set`, `badblocks_clear`, `ack_all_badblocks`, `badblocks_show`, `badblocks_store`, `badblocks_init`, `devm_init_badblocks`, and `badblocks_exit`. Internal helpers operate on packed 64-bit table entries through macros from `linux/badblocks.h`: start offset, length, and ACK bit are encoded in one word. Important helpers include `prev_badblocks`, `can_merge_front`, `front_merge`, `can_combine_front`, `front_combine`, `overlap_front`, `overlap_behind`, `can_front_overwrite`, `front_overwrite`, `insert_at`, `try_adjacent_combine`, `_badblocks_set`, `_badblocks_clear`, and `_badblocks_check`.

## Control flow
`badblocks_set` delegates to `_badblocks_set`, which validates enablement and length, rounds by `bb->shift`, takes the seqlock for writing, then iterates from the requested start to end. Each loop uses `prev_badblocks` with a hint to find the prior range, then chooses among insertion before all ranges, front combination, same-ack merge, acknowledged overwrite of unacknowledged ranges, overlap skipping, or insertion before the next range. Large operations are deliberately split into smaller pieces to handle maximum range length and table-full cases.

`badblocks_clear` delegates to `_badblocks_clear`, rounds conservatively, then walks the range. It treats clearing non-bad sectors as success, removes whole entries, shrinks entries from front or tail, and splits an entry only when table space permits. `badblocks_check` reads under a seqlock retry loop and returns `0` for no bad blocks, `1` for only acknowledged bad blocks, and `-1` if any unacknowledged bad block overlaps. `ack_all_badblocks` marks all entries acknowledged only when `changed` is clear, then merges adjacent compatible ranges.

## State and persistence behavior
`struct badblocks` owns a single page table, a count, a shift, a seqlock, and flags such as `changed` and `unacked_exist`. The in-memory table is sorted by sector range. Persistence is external: users such as MD or device drivers must store metadata and use `ack_all_badblocks` after metadata catches up. `badblocks_show` and `badblocks_store` provide sysfs-facing text serialization and insertion.

## Dependencies and integration points
The implementation depends on `linux/badblocks.h`, seqlocks, kernel allocation, device-managed allocation, and block-sector types. It is compiled unconditionally by the block Makefile and exported GPL symbols are available to block drivers and MD-like components that need bad-sector accounting.

## Risks
The packed entry format has a hard `MAX_BADBLOCKS` page-sized table and `BB_MAX_LEN` range length; very fragmented media can exhaust space. Partial progress in `_badblocks_set` can return failure when the original range is not fully represented. Overwrite semantics only allow acknowledged ranges to replace unacknowledged ones, so caller intent must be clear. Rounding via `bb->shift` differs for set and clear to avoid false negatives, which can surprise callers expecting exact sector removal. The code uses memmove-heavy table updates under a write seqlock, so large fragmented operations can hold interrupts disabled.

## Test signals
Strong tests include range insertion permutations, adjacent merges, ack/unack overwrite behavior, table-full cases, split-on-clear, shift rounding, sysfs parse failures, seqlock retry under concurrent readers, and `ack_all_badblocks` behavior when `changed` is set or clear. Build/link tests should also verify all exported symbols under module consumers.
