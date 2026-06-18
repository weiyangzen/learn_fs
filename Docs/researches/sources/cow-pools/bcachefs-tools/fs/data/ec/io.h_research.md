# File Research: sources/cow-pools/bcachefs-tools/fs/data/ec/io.h

Defines EC bio and stripe-buffer state plus EC I/O interfaces.

Key responsibilities:
- Defines `struct ec_bio` wrapper containing device, stripe buffer, block index, direction, submit time, and embedded bio.
- Defines pre/post recovery error slots.
- Defines `struct ec_stripe_buf` with closure, fs pointer, buffered range, per-block errors, data buffers, stale bitmap, checksum diagnostics, and stripe key.
- Provides `ec_nr_failed()` helper.
- Declares stripe buffer init/exit, auto-free cleanup, EC generation/checksum, validation, block I/O, full-stripe read, and reconstruct-read APIs.

Important interactions:
- Shared by EC creation, repair, and read recovery paths.
