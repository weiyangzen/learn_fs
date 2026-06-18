# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/bats.c

## Purpose
This file exposes Book3S 32-bit Block Address Translation register contents through debugfs. It decodes instruction and data BAT upper/lower SPR pairs into virtual ranges, physical base addresses, size, privilege scope, permissions, and cache attributes.

## Important APIs, Types, And Functions
Important functions are `bat_show_603()`, `bats_show()`, and `bats_init()`. The `BAT_SHOW_603` macro reads SPR pairs and dispatches to the decoder. `DEFINE_SHOW_ATTRIBUTE(bats)` creates the seq-file file operations.

## Control Flow
`bats_init()` creates `arch_debugfs_dir/block_address_translation`. Reading the file calls `bats_show()`, which prints instruction BATs 0-3, optional high BATs 4-7 when `MMU_FTR_USE_HIGH_BATS` is present, then data BATs in the same pattern. `bat_show_603()` treats `k == 0` as invalid, computes BEPI, block length, BRPN, range size, permission text, and WIMG attributes.

## State And Persistence
No state is persisted beyond debugfs registration. Output reflects live SPR values at read time.

## Dependencies And Integration Points
It depends on debugfs, seq_file, BAT SPR definitions, `PHYS_BAT_ADDR()`, `pt_dump_size()`, `arch_debugfs_dir`, and MMU feature detection. It is built only for Book3S32 ptdump debugfs.

## Risks And Test Signals
Risks include incorrect size/range decoding, format mismatch for 64-bit physical addresses, and reading unsupported high BAT SPRs. Test signals include debugfs output on 603-style and high-BAT CPUs and cross-checking ranges against early block mappings.
