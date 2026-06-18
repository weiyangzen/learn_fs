# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtbitmap.h

## Purpose
`rtbitmap.h` defines the shared scrub/repair state for realtime bitmap checks and repairs. It also defines word-offset types for xfile-backed bitmap reconstruction and the buffer sizing helper used by setup.

## Important APIs, types, and functions
It defines `xrep_wordoff_t`, `xrep_wordcnt_t`, `XREP_RTBMP_WORDMASK`, and `struct xchk_rtbitmap`. The state structure stores scrub context, computed geometry (`rextents`, `rbmblocks`, `rextslog`), block reservation, scan cursors (`next_free_rgbno`, `next_rgbno`), rtgroup lock flags, xfile write position, optional repair `xfs_rtalloc_args` and `xrep_tempexch`, and flexible `words[]` storage. It declares `xrep_setup_rtbitmap` or a stub and defines `xchk_rtbitmap_wordcnt`.

## Control flow
`xchk_setup_rtbitmap` allocates this structure with a flexible array sized by `xchk_rtbitmap_wordcnt`. Scrub uses the geometry and `next_free_rgbno`; repair uses the xfile word buffer, copy position, temporary exchange state, and rt allocation arguments.

## State and persistence
The header defines transient state only. Persistent bitmap repairs occur through the implementation in `rtbitmap_repair.c`, which uses this structure to stage and exchange file contents.

## Dependencies and integration points
It depends on realtime bitmap word sizing, scrub context types, online repair Kconfig, and `xrep_tempexch`. It is included by both realtime bitmap scrub and repair code to keep their shared layout consistent.

## Risks and test signals
Risks include allocating an undersized `words[]` buffer, mismatching xfile word offsets with on-disk bitmap headers, and stale fields when setup exits early. Tests should cover repair and no-repair builds, block-size-dependent word counts, large bitmap files, rtgroup-enabled versus legacy raw word formats, and setup error unwinding.
