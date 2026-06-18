# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/ptdump.h

## Purpose
This header defines the local data contract between the generic PowerPC ptdump walker and MMU-specific flag table providers.

## Important APIs, Types, And Functions
`struct flag_info` describes a bit mask, expected value, string when set or clear, optional value-style formatting, and shift. `struct ptdump_pg_level` describes one page-table level with a flag table, name, count, and aggregate mask. It declares `pg_level[5]` and `pt_dump_size()`.

## Control Flow
There is no runtime control flow in the header. Providers initialize `pg_level[]`; `ptdump.c` computes masks and uses these descriptors when walking page tables.

## State And Persistence
The persistent state is the externally defined `pg_level[]` array. Its `.mask` fields are filled during ptdump init.

## Dependencies And Integration Points
It depends on `linux/types.h` and `seq_file`. It is included by all ptdump providers and by the main walker.

## Risks And Test Signals
Risks include ABI drift between providers and walker, too-small `name[4]` for future level names, and incorrect `is_val`/`shift` interpretation. Build coverage across all ptdump providers is the main signal; runtime debugfs output confirms table decoding.
