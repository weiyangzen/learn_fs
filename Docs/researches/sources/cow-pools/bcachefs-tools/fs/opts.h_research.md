# File Research: sources/cow-pools/bcachefs-tools/fs/opts.h

This header defines the bcachefs option schema and public option APIs.

Key responsibilities:
- Declares option string tables and enum-print helpers.
- Defines option flags, option types, function-backed option callbacks, and `struct bch_option`.
- Defines `BCH_FIX_ERRORS_OPTS()` and `enum fsck_err_opts`.
- Defines `BCH_OPTS()`, the central macro table for all filesystem, inode, mount, runtime, format, and device options.
- Generates:
  - `enum bch_opt_id`
  - `struct bch_opts_mask`
  - `struct bch_opts`
  - `struct bch_inode_opts`
- Declares parse, validate, formatting, superblock get/set, mount parse, hook, and inode option APIs.
- Provides `opt_defined()`, `opt_get()`, `opt_set()`, and `bch2_opts_empty()`.
- Defines `bch2_io_opts_fixups()` and an `opt_change_lock` guard.

Major option categories:
- Filesystem geometry and metadata: block size, btree node size, metadata replicas/checksum/target.
- Data I/O policy: data replicas, checksum, compression, targets, erasure coding, nocow.
- Directory/security features: str_hash, casefold, ACLs, quotas.
- Mount/recovery behavior: degraded, fsck, fix_errors, norecovery, journal rewind, recovery pass controls.
- Journal behavior: flush delay, reclaim delay, flush disabled, scrub recent journal entries.
- Background work: copygc, reconcile, auto snapshot deletion.
- Device options: state, bucket size, durability, data allowed, discard, rotational.
- Tool/test options: direct I/O, no data I/O, stdio pointer, retain/read journal controls.

Important invariants:
- Undefined option values fall back to `bch2_opts_default`.
- `BCH_OPTS()` is the single source for option IDs, struct fields, table entries, default values, flags, help, and superblock binding.
- `BCH_INODE_OPTS()` determines which options are inherited into inode I/O policy.
- `bch2_io_opts_fixups()` normalizes background target/compression and disables incompatible data features under nocow.
- Options with `OPT_SB_FIELD_SECTORS`, `OPT_SB_FIELD_ILOG2`, or `OPT_SB_FIELD_ONE_BIAS` require transforms when reading/writing superblock fields.

Dependencies:
- Includes bcachefs on-disk format definitions, Linux sysfs/log2/sizes helpers, and option-specific callback declarations provided elsewhere.

Research notes:
- This header is effectively the option ABI definition for format, mount, sysfs, and inherited inode behavior.
- The macro table approach reduces duplication but makes option changes high impact.
