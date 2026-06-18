# File Research: sources/cow-pools/bcachefs-tools/fs/sb/io.c

Implements bcachefs superblock IO, validation, version handling, optional-field management, and human-readable dumping. It owns metadata-version name lookup, compatible/latest-compatible version helpers, incompatible-version request handling, and the persistent feature upgrade path.

Core logic includes `bch2_sb_field_get_id()`, resize/delete helpers for variable-length superblock sections, `bch2_sb_realloc()`, `validate_sb_layout()`, and `bch2_sb_validate()`. Validation checks magic/layout consistency, feature/version compatibility, UUIDs, offsets, device counts, time precision, member fields, and per-field validators.

Read path opens the block device according to mount/tool options, reads primary and backup superblocks, validates checksum and size, and chooses the highest valid sequence-number copy. If the primary cannot be used, it reads the standalone layout sector and scans backups. It also retries with buffered IO when direct IO is incompatible with the device block size in userspace builds.

Write path updates clean/dirty state, sequence numbers, per-member sequence fields, timestamps, counters, members, downgrade info, and extent-type metadata, then validates each online device superblock before writing every configured superblock slot. It reads back the primary slot before writing to detect dropped writes or concurrent modification, tracks per-device/per-offset write failures, and forces emergency read-only if the resulting set of written devices could not safely mount the filesystem.

The file registers optional-field ops for the `ext` section, dispatches field validation/text rendering by type, and prints full superblock details including UUIDs, versions, layout, options, features, compat bits, and selected sections.
