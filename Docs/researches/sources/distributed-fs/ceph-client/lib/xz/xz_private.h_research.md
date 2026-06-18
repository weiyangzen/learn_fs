# sources/distributed-fs/ceph-client/lib/xz/xz_private.h

## Purpose
Adapts the XZ decoder sources to kernel, preboot, and userspace-style builds. It maps Kconfig symbols to internal feature macros, defines decoder-mode predicates, selects generic BCJ support, and declares internal LZMA2/BCJ APIs.

## APIs and control flow
Important macros include `memeq`, `memzero`, `get_le32`, `DEC_IS_SINGLE`, `DEC_IS_PREALLOC`, `DEC_IS_DYNALLOC`, and `DEC_IS_MULTI`. In kernel non-preboot builds it includes allocation/string helpers and maps `CONFIG_XZ_DEC_*` to `XZ_DEC_*`. If no decode mode is explicitly selected, it enables single, preallocated, and dynamic allocation modes. It derives `XZ_DEC_BCJ` when any architecture BCJ filter is selected.

## State, dependencies, and integration
No runtime state. The header integrates public `linux/xz.h`, Kconfig, allocation helpers, unaligned access, and internal source declarations consumed by stream, LZMA2, BCJ, and CRC files.

## Risks and test signals
Bad macro mapping can remove modes or filters silently. Mode predicates are intended for compile-time dead-code elimination and must remain side-effect free. Test by building kernel/preboot-style variants, BCJ on/off, MicroLZMA on/off, and all decode modes.
