# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/io.c

Implements EC stripe buffer allocation, RAID parity generation/recovery, per-block checksum handling, block I/O, and reconstruct reads.

Key responsibilities:
- Wraps kernel RAID5/6 helpers, including an older-kernel `xor_gen()` shim.
- Implements RAID5/6 parity generation and recovery for up to two failures.
- Allocates bounded stripe buffers with `bch2_ec_stripe_buf_init()`, honoring `ec_stripe_buf_limit` and optional closure wait.
- Releases stripe buffers, memory accounting, and closure state.
- Computes per-block checksums with `bch2_checksum()` and writes them into stripe keys.
- Validates stripe block checksums, records good/bad checksums, and reports device checksum errors.
- Reconstructs failed data blocks if failure count does not exceed redundancy.
- Distinguishes spurious stale-pointer races for unpinned stripes from pinned-stripe allocator inconsistencies.
- Logs detailed pre/post-recovery errors and successful reconstruction messages.
- Issues per-block bio reads/writes with device iorefs, stale pointer detection, per-device IO accounting, and closure completion.
- Implements `bch2_ec_read_extent()`:
  - Relocks transaction to inspect original extent and stripe key.
  - Verifies extent stripe pointer matches stripe key.
  - Checks stale pointers while key is still live/locked.
  - Allocates a partial stripe buffer for the read range.
  - Reads stripe blocks, validates/reconstructs, and copies recovered data into caller bio.

Important interactions:
- Uses checksum helpers, EC trigger layout helpers, read path structures, block bioset from `init.c`, and RAID helpers.
- `create.c` uses the same buffer and parity/checksum routines when creating stripes.

Notable concerns:
- `bch2_ec_read_extent()` has a typo in an error string: “read is biffer than stripe”.
- Recovery returns stale-race-specific errors so the upper read path can retry appropriately.
