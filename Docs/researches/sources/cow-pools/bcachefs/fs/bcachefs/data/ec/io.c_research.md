# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/ec/io.c

Implements EC stripe buffer allocation, parity generation/recovery, checksum validation, block IO, and reconstruct-read path.

Key entry points:
- `bch2_ec_stripe_buf_init()` and `bch2_ec_stripe_buf_exit()` manage per-stripe block buffers under a memory limit.
- `bch2_ec_generate_ec()` and `bch2_ec_generate_checksums()` compute parity and per-block checksums.
- `bch2_stripe_buf_validate_msg()` validates checksums and reports recoverability.
- `bch2_ec_block_io_range()` submits EC block read/write bios.
- `bch2_ec_read_extent()` reconstructs a failed EC-backed extent read.

Important details:
- Kernel builds use RAID5/RAID6 xor/pq helpers; non-kernel builds include userspace RAID helpers.
- Buffer ranges are rounded to checksum granularity.
- Validation records pre- and post-recovery per-block errors; checksum failures update device IO error accounting.
- Reconstruction requires failures not exceed redundancy and validates recovered data checksums.
- Read reconstruction checks stale stripe pointers while btree locks are still held, then releases locks before allocation/IO.

Dependencies and interactions:
- Uses checksum helpers, EC trigger stripe layout accessors, read path structs, device io refs, bioset from EC init.
