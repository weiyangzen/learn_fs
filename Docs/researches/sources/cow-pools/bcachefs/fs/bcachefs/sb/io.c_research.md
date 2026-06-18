# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/io.c

This file implements bcachefs superblock layout documentation, validation, read fallback, write replication, version management, field dispatch, and text rendering.

Key responsibilities:
- Documents superblock layout, redundancy, threat model, fixed fields, variable fields, versioning, and recovery behavior.
- Converts metadata versions to text and computes latest compatible versions within a major version.
- Enforces incompatible feature/version enablement through `bch2_set_version_incompat()`.
- Gets, resizes, deletes, and reallocates variable-length superblock fields.
- Validates superblock layout sector, version compatibility, UUIDs, offset, member count/index, time precision, feature bits, field bounds, member sections, and all typed superblock fields.
- Copies shared superblock state between filesystem-wide and per-device handles.
- Updates in-memory `c->sb` CPU fields from the on-disk superblock, including ext recovery passes, silent errors, and lost-data btree bitmap.
- Reads the primary superblock, embedded/standalone layout, and all backup copies, selecting the highest valid sequence number.
- Falls back to buffered IO in userspace if direct IO is incompatible with device block size.
- Writes superblocks to all online member devices and all configured superblock slots.
- Reads back primary superblocks before write to detect silent dropped writes or external modification.
- Marks clean/dirty as needed, serializes counters/members/errors/downgrade/extent-type state, validates before write, and refuses unsafe writes.
- Determines whether enough devices were successfully written to keep the filesystem mountable.
- Handles feature setting, compatible/incompatible upgrade, version downgrade, and async recovery pass scheduling.
- Provides generic superblock field validation/text dispatch and full superblock text rendering.

Important invariants:
- The highest valid sequence-number superblock copy is authoritative.
- Backup copy selection scans every configured backup, not only on primary failure.
- Superblock field resizing must also ensure online member devices have enough buffer space.
- Members are validated before other fields because other fields may depend on member metadata.
- Writes are skipped before initialization and in `nochanges` mode.
- A superblock write is fatal if no device was written or the set of written devices is insufficient to mount with current degraded policy.
- `bch2_write_super()` updates in-memory visible options only after persistence succeeds or the write path exits.

Dependencies include checksum helpers, journal superblock state, journal sequence blacklist, quota, device open/write refs, replicas, disk groups, member metadata, counters, errors, downgrade policy, clean section handling, recovery pass mapping, and block-layer bio IO.
