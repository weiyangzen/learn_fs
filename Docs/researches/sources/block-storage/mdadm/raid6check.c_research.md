# File Research: sources/block-storage/mdadm/raid6check.c

Purpose: standalone RAID6 consistency checker and repair utility, based on mdadm restriping logic.

Main flow:
- `main()` opens an md device, reads sysfs metadata, requires RAID6 and non-degraded state, prints geometry and component devices, opens component devices with `O_RDWR | O_DIRECT`, then calls `check_stripes()`.
- Supports normal check mode: `md_device start_stripe length_stripes [autorepair]`.
- Supports manual repair mode: `md_device repair stripe failed_slot_1 failed_slot_2`.

Core checking:
- `check_stripes()` locks each stripe by writing `suspend_lo`/`suspend_hi`, reads one chunk from every member, maps P/Q/data slots using `geo_map()`, calculates P and Q via `qsyndrome()`, classifies mismatch bytes with `raid6_collect()`, summarizes per 4 KiB page with `raid6_stats()`, and reports likely failed slots.
- DDF layouts are handled differently from native md layouts: DDF syndrome order follows raid disk numbers with zeroes for P/Q, while md syndrome order starts after Q and skips P.

Repair paths:
- `autorepair()` repairs pages only when the suspected role maps to a real block index. It handles Q-only mismatches by recomputing Q and data/P mismatches by XOR recovery.
- `manual_repair()` accepts two user-specified failed slots and uses RAID6 recovery helpers for D+P, D+D, or Q-involved repairs.
- Writes are done directly to member devices at `offset + start * chunk_size`.

Dependencies:
- Prototypes functions implemented in `restripe.c`: `geo_map`, `is_ddf`, `qsyndrome`, `make_tables`, `raid6_datap_recov`, `raid6_2data_recov`, `xor_blocks`.
- Uses mdadm sysfs helpers, `xmalloc`, RAID layout constants, and Linux direct IO behavior.

Safety properties:
- Locks stripes and ignores termination signals during critical read/repair windows.
- Refuses degraded arrays at startup.
- Restores suspend sysfs values and signal handlers via `unlock_all_stripes()`.

Risks and edge cases:
- Direct writes do not retry partial writes beyond checking aggregate byte count.
- `int disk[chunk_size >> CHECK_PAGE_BITS]` and similar VLAs depend on chunk size and stack availability.
- `autorepair()` indexes `block_index_for_slot[disk[j]]` after accepting `disk[j] >= -2`; the code relies on pointer biasing (`block_index_for_slot += 2`) being correct.
- Manual repair trusts operator-provided failed slots.
