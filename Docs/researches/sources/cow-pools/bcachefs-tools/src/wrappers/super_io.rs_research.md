# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/super_io.rs

Implements Rust superblock read/write helpers compatible with C expectations.

Core functions:
- `die` prints an error and exits.
- `borrowed_file` wraps a raw fd in `ManuallyDrop<File>` so it is not closed.
- `vstruct_bytes_sb` computes fixed superblock size plus variable u64 payload.
- `bch2_super_write` writes the superblock to every layout offset, handling the special default offset/layout co-write case for large physical block sizes, then fsyncs.
- `__bch2_super_read` reads and validates a superblock at a sector offset, allocates with `libc::malloc`, and returns a C-freeable pointer.
- `sb_layout_init` initializes primary/backup superblock layout positions.

Layout details:
- Uses bcachefs magic constants for legacy bcache and bcachefs.
- Default superblock size is 2048 sectors.
- Adds an end-of-device backup superblock only for default superblock start and when `no_sb_at_end` is false.
- Aligns non-default positions to block-size sectors.

Potential concerns:
- Many errors terminate the process instead of returning `Result`, matching C behavior but limiting composability.
- `round_up` assumes power-of-two alignment.
- `__bch2_super_read` trusts `u64s` after the initial magic check to allocate the variable-sized structure.
