# File Research: sources/cow-pools/bcachefs-tools/raid/raid.c

This is the central RAID parity generation and data-recovery dispatcher for the bundled bcachefs-tools RAID library. It implements GF(2^8)-based erasure coding using either the default Cauchy matrix mode, supporting up to 6 parity blocks and 251 data blocks, or Vandermonde/triple-parity mode for CPUs without fast SSSE3/AVX2 support.

Key responsibilities:
- Maintains `raid_gfgen`, `raid_gen_ptr[]`, `raid_gen3_ptr`, and `raid_genz_ptr` dispatch state.
- Exposes `raid_mode()` to switch Cauchy vs Vandermonde behavior.
- Exposes `raid_zero()` for the zero-filled recovery scratch block required by recovery paths.
- Validates block size and parity count in `raid_gen()`, then calls the selected generator.
- Implements `raid_invert()` for small GF matrix inversion used by recovery.
- Implements `raid_delta_gen()`, which recomputes parity over surviving data while temporarily replacing missing data with the zero block.
- Implements optimized one- and two-data-block recovery helpers: `raid_rec1of1()` and `raid_rec2of2_int8()`.
- Implements public recovery dispatch with `raid_rec()` and `raid_data()`.

Important behavior:
- `size` must be a multiple of 64 bytes.
- Failure index arrays must be sorted.
- `raid_rec()` handles mixed data/parity failures: data is reconstructed first, then bad parity blocks are regenerated up to the highest failed parity.
- Parity functions are assumed to write parity blocks in order; `raid_delta_gen()` relies on that to protect unused parity buffers.

Dependencies:
- `internal.h` for dispatch declarations, macros, and helper prototypes.
- `gf.h` for GF arithmetic tables/functions such as `mul`, `inv`, `pow2`, and `table`.
- Architecture-specific implementations live outside this file, especially in `x86.c` and `x86z.c`.

Notes:
- Public APIs `raid_init()`, `raid_selftest()`, `raid_check()`, and `raid_scan()` are declared in `raid.h` but implemented in other RAID files, not here.
