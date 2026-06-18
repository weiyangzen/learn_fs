# File Research: sources/cow-pools/bcachefs-tools/src/util.rs

Provides shared Rust utility helpers for aligned I/O buffers, human-readable formatting, file sizing, flag parsing, and TUI setup.

Key utilities:
- `AlignedBuf` allocates zeroed 4096-byte-aligned memory and exposes it as `[u8]`.
- `parse_human_size` delegates to C `bch2_strtoull_h`.
- `fmt_bytes_human`, `fmt_sectors_human`, and `fmt_num_human` format byte/sector/count values.
- `file_size` returns regular file size or block device size via `BLKGETSIZE64`.
- `read_flag_list` delegates C flag-list parsing and returns a Rust error on unknown flags.
- `run_tui` enables raw mode, enters the alternate screen, hides cursor, runs a closure, then restores terminal state.

Potential concerns:
- `AlignedBuf::new` asserts allocation success and does not handle zero-size layouts specially.
- `run_tui` restores terminal state after the closure returns, but panics inside the closure would skip restoration.
