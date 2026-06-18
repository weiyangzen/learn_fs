# File Research: sources/cow-pools/bcachefs/fs/bcachefs/opts.c

This file implements bcachefs option tables, parsing, formatting, superblock/member serialization, runtime hooks, and inode-option extraction.

Key responsibilities:
- Materializes string tables for errors, degraded policy, fsck fixes, upgrade policy, features, btree IDs, checksum/compression/hash/data/member/reconcile/journal options, and d_types.
- Builds `bch2_opt_table[]` from the macro schema in `opts.h`, including sysfs attributes, type, flags, bounds, help text, and superblock/member/ext accessors.
- Parses booleans, unsigned integers, string choices, bitfields, and custom option functions.
- Validates bounds, sector alignment, power-of-two requirements, and custom validators.
- Formats single options, changed option sets, and inode IO options.
- Applies defined values from one `bch_opts` to another and gets/sets options by enum ID.
- Parses mount option lists, including `no<opt>` boolean negation and synonyms such as `quota=usrquota` and degraded bool aliases.
- Converts options to/from superblock, member, and extension fields with sector, ilog2, and one-bias transforms.
- Runs pre/post option hooks for feature enablement, compression availability, casefold constraints, device state changes, reconciliation scans, copygc/reconcile wakeups, discard persistence, durability updates, and incompatible version upgrade.
- Maintains an option-change cookie under a mutex for readers that need to detect changed IO policy.

Important invariants:
- Undefined options are represented by separate `<name>_defined` bits; default fallback is handled by `opt_get()`.
- `OPT_MOUNT_OLD` options are parsed but rejected for modern mount-time setting with a warning.
- Runtime IO-affecting option changes are bracketed by reconciliation scan setup before and after the change.
- Superblock updates are protected by `sb_lock` and persisted with `bch2_write_super()` only when the encoded value changes.
- Metadata inode options override user-data policy: metadata uses metadata target/replicas/checksum and disables compression/EC.

Dependencies include fs parser constants, disk-group target parsing, compression helpers, reconciliation work scheduling, copygc wakeups, device state changes, feature/version upgrade helpers, and superblock IO.
