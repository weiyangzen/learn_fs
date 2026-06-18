# File Research: sources/block-storage/util-linux/sys-utils/fallocate.c

## Scope

Implements `fallocate`, a file space allocation/deallocation utility using `fallocate(2)`, `posix_fallocate(3)`, and sparse-file hole detection/punching.

## Public And Internal APIs Covered

- Main command-line entry point.
- Allocation wrappers: `xfallocate()`, `xposix_fallocate()`.
- Number parsing: `cvtnum()`.
- Hole detection/reporting: `dig_holes()`, `is_nul()`, `update_holestat()`, `summary_holestat()`.

## Control Flow And Behavior

- Supports range operations:
  - allocate default range,
  - keep size,
  - punch hole,
  - collapse range,
  - insert range,
  - zero range,
  - write zeroes,
  - POSIX fallocate.
- Supports sparse-file analysis:
  - `--dig-holes` scans data extents and punches zero-filled regions into sparse holes.
  - `--report-holes` reports filesystem holes and zero-filled data holes without modifying the file.
- Uses option-exclusion rules to prevent incompatible modes.
- Requires `--length` for normal allocation/deallocation operations, while dig/report default to the whole file when no length is supplied.
- Validates range overflow against `off_t`.
- Opens with `O_CREAT` only for default allocation or write-zeroes-style allocation, not destructive/special range modes.
- `dig_holes()` uses `SEEK_DATA` / `SEEK_HOLE` to skip existing holes, reads data extents in filesystem block-sized chunks, detects all-zero buffers with a sentinel word scan, and optionally punches those ranges using `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`.
- Uses `posix_fadvise()` when available to mark sequential access and drop cache chunks during scanning.

## Dependencies

- Linux fallocate flags, with fallback definitions when libc headers lack newer constants.
- POSIX `fallocate`, `posix_fallocate`, `lseek(SEEK_DATA/SEEK_HOLE)`, `pread`, `fstat`, and close/write-error handling.
- util-linux parsing, option exclusion, allocation, human size, and i18n helpers.

## Risks And Invariants

- `FALLOC_FL_PUNCH_HOLE` implies `FALLOC_FL_KEEP_SIZE`.
- Zero-length normal fallocate is rejected; dig/report use length zero as whole-file sentinel.
- `is_nul()` requires the caller to allocate extra sentinel space after the buffer.
- Hole punching near extent ends may enlarge allocation size to meet block boundaries while reporting the true zero-data size.
- Close errors are treated as write failures.
