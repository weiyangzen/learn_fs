# File Research: sources/cow-pools/bcachefs/fs/bcachefs/errcode.c

Implements bcachefs-specific error stringification, error-class matching, top-level errno class conversion, and block/ZSTD error mapping.

Key entry points:
- `bch2_err_str()` returns a printable string for standard errno values, bcachefs extended errors, zero, and invalid codes.
- `__bch2_err_matches()` walks the parent chain of a bcachefs extended error to test membership in an error class.
- `__bch2_err_class()` maps an extended negative error to its top-level standard errno-style class.
- `bch2_blk_status_to_str()` special-cases `BLK_STS_REMOVED` and otherwise delegates to block-layer status strings.
- `blk_status_to_bch_err()` maps block status values into typed bcachefs errors.
- `zstd_err_to_bch_err()` maps ZSTD error codes into typed bcachefs errors.

Core mechanics:
- `BCH_ERRCODES()` generates parallel name and parent arrays.
- Extended error codes live at `BCH_ERR_START` and form parent-child chains ending in standard errno classes or zero-class internal control errors.
- Public sysfs/ioctl paths can call `bch2_err_class()` to avoid leaking internal error identities where only standard errno should be returned.

Important invariants:
- Parent arrays and string arrays must remain generated from the same macro list.
- Callers pass negative errors to matching/class helpers; helpers normalize with `abs()` internally where appropriate.
- `BUG_ON()` guards assume invalid codes are programming errors.

Filesystem relevance:
- Provides consistent diagnostics and errno classification across bcachefs metadata, IO, recovery, fsck, compression, device, journal, and ioctl paths.
