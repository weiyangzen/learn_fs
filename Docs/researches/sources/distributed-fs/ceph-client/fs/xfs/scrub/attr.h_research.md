# sources/distributed-fs/ceph-client/fs/xfs/scrub/attr.h

## Purpose
This header declares the temporary buffer shared by extended attribute scrub and repair. It centralizes the in-memory maps and scratch buffers required to validate attr block layout, retrieve values, and salvage names/values during repair.

## Important APIs, types, and functions
`struct xchk_xattr_buf` contains `usedmap`, `freemap`, `name`, `value`, and `value_sz`. `xchk_xattr_set_map` marks byte ranges in leaf or shortform buffers. `xchk_setup_xattr_buf` allocates or resizes the scratch storage.

## Control flow and state
The buffer is owned through `sc->buf` and cleaned through `sc->buf_cleanup`. `usedmap` is mandatory for structural validation; `freemap` is allocated only when deep checking is needed or leaf blocks may exist. `name` is allocated when repair may need to reconstruct attributes. `value` grows on demand and contents are not preserved across resize.

## Persistence and integration
All state is temporary. The header is consumed by `attr.c` for validation and by `attr_repair.c` for salvage and reinsertion into temporary files. The structure deliberately avoids embedding filesystem metadata ownership; callers derive all context from `xfs_scrub`.

## Risks and test signals
The main risks are buffer reuse after resize, cleanup omissions, and callers assuming `freemap` or `name` exists without satisfying setup conditions. Tests should exercise repeated setup calls with increasing value sizes, repair versus no-repair allocation paths, try-harder allocation of maximum attr size, and cleanup after partial allocation failure.
