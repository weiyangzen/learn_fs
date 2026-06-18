# File Research: sources/block-storage/libcryptsetup-rs/src/tests/loopback.rs

Provides loopback-backed test fixture utilities.

Key helpers:
- `setup_backing_file`
- `use_loopback`

Behavior:
- Creates a random-named backing file in `TEST_DIR` or `/tmp`.
- Fills it with zeroes or random bytes.
- Requires effective UID root.
- Uses `loopdev::LoopControl` to attach the file to a free loop device.
- Runs a caller-provided closure with loop device path and backing file path.
- Detaches and deletes backing file when cleanup is enabled.
- Captures panics around test closure so cleanup can run before re-raising.

Research notes:
- `FORMAT_WITH_ZEROS` and `DO_CLEANUP` are controlled in `tests/mod.rs`.
- Backing file names use URL-safe base64 of random bytes.
