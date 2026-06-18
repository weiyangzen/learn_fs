# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/vivid-rds-gen.h

Purpose: defines RDS generator constants, state, and public generator APIs for Vivid radio.

Important APIs and types: constants define 57 groups, four blocks per group, total block count, and nanoseconds per block for a roughly five-second cycle. `struct vivid_rds_gen` stores generated block data and source PI/PTY/flags/PS/radiotext fields. APIs are `vivid_rds_gen_fill` and `vivid_rds_generate`.

Control flow: callers fill source fields, then generate the block array, then radio read/write paths stream blocks according to `VIVID_RDS_NSEC_PER_BLK`.

State and persistence: the structure is the persistent per-device RDS buffer until regenerated or overwritten.

Dependencies and integration points: depends on `struct v4l2_rds_data`, Linux time constants, and radio common code.

Risks: PS name and radiotext fixed array sizes match RDS limits; callers must provide NUL-terminated strings or use bounded copies.

Test signals: compile coverage and userspace RDS block stream decoding validate the header contract.
