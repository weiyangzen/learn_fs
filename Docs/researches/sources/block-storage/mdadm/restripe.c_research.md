# File Research: sources/block-storage/mdadm/restripe.c

Purpose: shared RAID geometry, parity/syndrome, recovery, save, restore, and optional test logic used for reshaping/restriping arrays.

Geometry:
- `geo_map(block, stripe, raid_disks, level, layout)` maps logical data/P/Q roles to physical disk numbers for RAID0/4/5/6, including native md and DDF-style RAID6 algorithms.
- `is_ddf(layout)` identifies DDF rotating RAID6 layouts.

Parity and RAID6 math:
- `xor_blocks()` computes P parity byte by byte.
- `qsyndrome()` computes RAID6 P and Q.
- `make_tables()` builds GF multiplication, exponent, inverse, and log tables.
- `raid6_2data_recov()` and `raid6_datap_recov()` are adapted from Linux RAID6 recovery logic.

Stripe movement:
- `save_stripes()` reads data chunks from an old geometry into a buffer or backup file. It can reconstruct missing data using parity or RAID6 recovery if enough members are readable.
- `restore_stripes()` reads saved data from a file or buffer, rebuilds parity/Q for the destination geometry, and writes complete stripes to member devices.
- Both functions require stripe-aligned lengths.

Optional test harness:
- Under `#ifdef MAIN`, provides `test_stripes()`, `getnum()`, and a CLI `main()` for save/restore/test operations against explicit device files.

Dependencies:
- Includes `mdadm.h`, `xmalloc.h`, and `<stdint.h>`.
- Shares symbols with `raid6check.c`.

Risks and notes:
- Comments explicitly call `xor_blocks()` inefficient.
- IO paths generally treat short read/write as failure, with limited retry behavior.
- The code uses global RAID6 tables and global `zero` buffer, so it is not designed as isolated thread-safe library state.
