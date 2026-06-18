# File Research: sources/cow-pools/bcachefs/fs/bcachefs/errcode.h

Defines the bcachefs extended error namespace and helpers for matching, classifying, and converting error types.

Key elements:
- `BLK_STS_REMOVED` reserves a custom block status value.
- `BLK_ERRS()` and `ZSTD_ERRS()` list block-layer and ZSTD errors that are wrapped as bcachefs errors.
- `BCH_ERRCODES()` is the central macro table for extended errors, including memory allocation sites, ENOSPC variants, lookup errors, transaction restart causes, fsck outcomes, recovery, device/state validation, ioctl validation, topology repair, EOPNOTSUPP cases, read-only/shutdown states, operation blocking, invalid superblocks, btree/data/journal IO errors, decompression/read/write errors, nocow failures, and shutdown-with-errors states.
- `enum bch_errcode` starts at `BCH_ERR_START = 2048` and expands the macro table to `BCH_ERR_MAX`.
- `bch2_err_matches()` requires a compile-time constant class and tests hierarchical error membership.
- `bch2_err_class()` converts negative extended errors to their top-level class.

Core mechanics:
- Each macro entry has a parent/class and a leaf error name. Parents may be standard errno values, zero-class control groups, or other bcachefs errors.
- The same table drives string generation, parent lookup, and enum values in `errcode.c`.
- Inline helpers preserve normal positive return values and only classify negative errors.

Important invariants:
- New errors must be added to `BCH_ERRCODES()` with the correct parent class, or matching/classification semantics become wrong.
- Error classes used with `bch2_err_matches()` must be constants so the build-time assertion works.
- Header guard closing comment contains a typo, but the actual guard macro is `_BCACHEFS_ERRCODE_H`.

Filesystem relevance:
- This file is the error taxonomy for bcachefs. It lets internal paths distinguish fine-grained causes while external APIs can still report stable errno classes.
