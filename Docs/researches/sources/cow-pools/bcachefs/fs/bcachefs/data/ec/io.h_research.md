# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/io.h

Declares EC IO structures and APIs.

Key contents:
- `struct ec_bio` wraps a bio with device, stripe buffer, block index, direction, and submit time.
- `struct ec_stripe_buf` stores stripe key, data buffers, errors, stale bitmap, checksum diagnostics, and IO closure.
- `ec_nr_failed()` counts block failures for pre/post recovery phases.
- Declares stripe buffer lifecycle, EC generation/checksum APIs, block IO, stripe read, and reconstruct extent read.

Dependencies and interactions:
- Included by EC create, repair, and read paths.
