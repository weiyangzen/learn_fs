# sources/distributed-fs/ceph-client/lib/errname.c

## Purpose
Maps Linux errno values to symbolic names such as `"-EIO"` or `"EIO"`, providing a small exported helper for diagnostics that need stable errno names without open-coded tables.

## Important APIs, Types, and Functions
The public API is `const char *errname(int err)`, exported with `EXPORT_SYMBOL`. Internally, `__errname(unsigned err)` searches two sparse static string tables: `names_0[]` for normal errno values up to 300 and `names_512[]` for kernel-internal restart/probe/NFS-style errors in the 512-550 range.

## Control Flow
`errname()` calls `__errname(abs(err))`. If no table entry exists, it returns `NULL`. For positive errno inputs, it strips the leading minus sign from the stored table string; for negative inputs, it returns the stored `"-EXXX"` spelling. The table macros use `BUILD_BUG_ON_ZERO()` to keep entries in expected numeric ranges.

## State and Persistence
The file has only compile-time static const tables. There is no mutable state, allocation, locking, or persistence.

## Dependencies and Integration Points
Depends on architecture errno definitions, `linux/errname.h`, `linux/errno.h`, `BUILD_BUG_ON_ZERO`, and `static_assert`. Architecture-specific aliases and gaps are handled with preprocessor guards, including MIPS `EDQUOT` as a special high-numbered errno and parisc aliases.

## Risks
Coverage depends on maintaining the tables as errno definitions evolve. Unknown or architecture-specific errors return `NULL`, so callers must handle absence. The `abs(err)` conversion relies on normal errno-sized integers rather than arbitrary `INT_MIN`-style inputs. Large table bounds are intentionally limited to avoid huge sparse arrays.

## Test Signals
Validate negative and positive inputs, aliases (`EAGAIN`/`EWOULDBLOCK`, parisc aliases when present), internal 512-range errors, MIPS `EDQUOT`, unknown values, and zero. Build coverage across architectures is important because conditional entries differ.
