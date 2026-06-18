# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/format.h

Defines the on-disk stripe value layout.

Key responsibilities:
- Defines packed `struct bch_stripe` with:
  - stripe sector count,
  - algorithm,
  - `needs_reconcile`,
  - 3-bit saturating `can_widen`,
  - block and redundancy counts,
  - checksum granularity/type,
  - disk label,
  - variable-length extent pointer array.
- Documents variable-length sections after pointers: per-block checksums and per-block sector counts.

Important interactions:
- `trigger.h` computes offsets into the variable-length checksum and block-count sections.
- `create.c` initializes geometry and `can_widen`.
- `io.c` uses checksum fields for per-block validation/recovery.

Notable concerns:
- Comment notes target IDs should eventually be 16-bit; current `disk_label` is 8-bit.
- Comment notes checksum layout makes block sector counts inaccessible if checksum type is unknown.
