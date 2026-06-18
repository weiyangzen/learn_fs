# sources/distributed-fs/glusterfs/xlators/features/read-only/src/read-only-common.h

## Purpose
`read-only-common.h` declares the shared read-only FOP wrappers used by both the `read-only` and `worm` translators.

## Important APIs and Types
- `is_readonly_or_worm_enabled()` declares the common policy check.
- Declarations cover mutating FOP wrappers for xattrop, locks, setattr, truncate, creation/removal, rename/link, open, xattrs, fsyncdir, writev, and fallocate.

## Control Flow
This header has no executable flow. It ensures both module implementation files can register the common wrappers in their `struct xlator_fops`.

## State and Persistence
No state is defined here. The declarations operate on `read_only_priv_t` stored in `this->private` by including modules.

## Dependencies and Integration Points
It includes `<glusterfs/defaults.h>` for core FOP types and macros. It is consumed by `read-only.c`, `worm.c`, and `read-only-common.c`.

## Risks
Prototype drift from GlusterFS FOP signatures will produce compile errors or, worse, incorrect callback wiring if manually cast elsewhere. New mutating FOPs added to GlusterFS need matching declarations and wrappers to keep read-only semantics complete.

## Test Signals
Compile coverage catches signature mismatches. Functional tests should map every registered FOP in both translators to a declared/implemented wrapper.
