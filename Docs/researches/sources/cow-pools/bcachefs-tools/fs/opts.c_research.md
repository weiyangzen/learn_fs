# File Research: sources/cow-pools/bcachefs-tools/fs/opts.c

This file implements bcachefs option tables, parsing, formatting, superblock synchronization, mount parsing, and runtime option hooks.

Key responsibilities:
- Defines string tables for error actions, degraded actions, fsck fix modes, version upgrade modes, features, compat bits, btree IDs, checksum/compression/hash/data/member/reconcile/journal-scrub options, and dentry types.
- Provides bounds-checked print helpers for option-like enums.
- Implements the custom `fix_errors` option parser/printer.
- Builds `bch2_opt_table[]` from `BCH_OPTS()`.
- Provides option lookup, synonym lookup, validation, parsing, and text formatting.
- Applies option structs and generic get/set by option ID.
- Reads options from superblock/member/ext fields and writes options back to them.
- Parses mount option strings, including boolean `nofoo` negation and old mount option handling.
- Runs pre/post option hooks that trigger reconciliation scans, device state changes, feature checks, discard propagation, copygc/reconcile wakeups, and capacity recalculation.
- Builds inode I/O option snapshots and prints inode options.
- Provides option change locking with an odd/even cookie.

Important parsing behavior:
- Boolean options accept a local strict table: `0`, `1`, `false`, `no`, `true`, `yes`.
- Unsigned integer options reject missing values and negative strings.
- Human-readable integer options use `bch2_strtou64_h()`.
- String options use `match_string()` against choice tables.
- Bitfield options use `bch2_read_flag_list()`.
- Function-backed options delegate to option-specific parse/validate/text callbacks.
- Unknown mount options are ignored or rejected based on caller mode.
- Some options that require an open filesystem can be deferred into `parse_later`.

Important option hooks:
- I/O-affecting options bracket reconcile scans before/after changes.
- Metadata target/checksum/replica changes trigger metadata reconcile.
- Device durability changes can trigger pending and device reconcile scans.
- `state` changes call device state transition logic.
- Compression and erasure-code options check/set required feature state.
- `casefold_disabled` rejects mounts when casefolding is already in use.
- Runtime discard changes can propagate to member superblock fields.
- Incompatible `version_upgrade` triggers superblock upgrade logic.
- `read_only` wakes reconcile.

Important invariants:
- Options use paired `_defined` bits so partial option structs can override defaults selectively.
- Superblock storage transforms support sector shifts, ilog2 encoding, and one-biased values.
- Device option writes require an existing member slot.
- Runtime sysfs writability is represented through option flags and attribute mode.
- `bch2_io_opts_fixups()` disables compression/checksum/EC under nocow and caps EC replicas to RAID6-style limits.

Dependencies:
- Uses option definitions from `opts.h`, superblock/member/ext accessors, recovery pass names, allocation targets, compression parsing, reconcile/copygc hooks, and mount parser helpers.

Research notes:
- This is the central policy file for option side effects. Updating an option definition in `opts.h` without matching parse/hook implications here can silently miss required background repair work.
