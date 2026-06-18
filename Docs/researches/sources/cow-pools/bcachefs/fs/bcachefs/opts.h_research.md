# File Research: sources/cow-pools/bcachefs/fs/bcachefs/opts.h

This header is the central option schema for bcachefs.

Key responsibilities:
- Declares option string tables and print helpers for enums used across diagnostics.
- Defines option flags for filesystem/device/inode scope, format/mount/runtime availability, human-readable parsing, superblock field transforms, hidden/legacy/doc behavior, and validation constraints.
- Defines option types: bool, uint, string, bitfield, and custom function.
- Defines the `BCH_OPTS()` macro list that creates every option’s enum ID, in-memory field, default, persistence accessor, flags, parser type, hint, and help text.
- Defines `struct bch_opts`, `struct bch_option`, masks, parse staging, and option get/set helpers.
- Declares parsing, formatting, pre/post hook, superblock serialization, and inode-option APIs.
- Defines `struct bch_inode_opts` and `bch2_io_opts_fixups()`.

Major option categories:
- Format and metadata geometry: block size, B-tree node size, extent size.
- Error/fsck/recovery policy: errors, fsck, fix_errors, recovery passes, journal rewind/scrub.
- Data placement and redundancy: metadata/data replicas, foreground/background/promote targets, durability, data_allowed.
- Integrity and encoding: metadata/data checksum, compression, background compression, string hash, EC, nocow.
- Runtime services: journal delays, copygc, reconcile, auto snapshot deletion, writeback, discard.
- Mount-only/debug behavior: degraded, noexcl, read_only, nochanges, norecovery, no_data_io.
- Device attributes: state, bucket size, rotational, readahead, discard.

Important invariants:
- `struct bch_opts` stores each option as a value plus a defined bit so partial option sets can be merged.
- `bch2_io_opts_fixups()` normalizes inherited policy: background target/compression default to foreground/compression, single replica disables EC, nocow disables checksum/compression/EC, and EC caps replicas to RAID6-style limits.
- Superblock field flags describe how values are encoded on disk; callers must use the conversion helpers instead of writing fields directly.
