# sources/distributed-fs/ceph-client/fs/quota/quotaio_v2.h

Purpose: Defines the v2 quota file on-disk ABI: magic/version headers, v2r0 and v2r1 disk dquot records, info header fields, and fixed offsets/block sizing.

Important APIs, types, and functions: Defines `V2_INITQMAGICS`, `V2_INITQVERSIONS`, `struct v2_disk_dqheader`, `struct v2r0_disk_dqblk`, `struct v2r1_disk_dqblk`, `struct v2_disk_dqinfo`, `V2_DQINFOOFF`, and `V2_DQBLKSIZE_BITS`.

Control flow: `quota_v2.c` uses the header to validate file type and version, then reads the info structure at `V2_DQINFOOFF`. The quota tree uses 1 KiB logical blocks and leaf records with layouts selected by version.

State and persistence: Stores per-type quota file magic, supported version, grace times, flags, total quota-tree blocks, first free block, first block with a free entry, and per-id quota limits/usage. v2r1 widens most counters to 64 bits while retaining a 32-bit id.

Dependencies and integration points: Included by v2 quota format code and paired with `quota_tree.h`. It depends on little-endian integer types and quota type constants.

Risks and test signals: Risks are ABI drift, endian conversion errors, magic/version mismatch, and counter width truncation. Test header validation for all quota types, v2r0/v2r1 conversion, large limits, and malformed info headers.
