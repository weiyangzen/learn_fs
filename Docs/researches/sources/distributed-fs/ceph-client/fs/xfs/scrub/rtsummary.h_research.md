# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtsummary.h

## Purpose
`rtsummary.h` defines the shared state and small API surface for realtime summary scrub and repair. It keeps geometry, xfile copy position, rtalloc buffer arguments, repair exchange state, and a flexible comparison buffer in one structure.

## Important APIs, types, and functions
The central type is `struct xchk_rtsummary`, with optional `xrep_tempexch`, `xfs_rtalloc_args`, computed `rextents`, `rbmblocks`, `rsumblocks`, `rsumlevels`, repair reservation `resblks`, `prep_wordoff`, and flexible `words[]`. It declares `xfsum_copyout` for reading computed xfile summary words and `xrep_setup_rtsummary` or a no-op stub.

## Control flow
`xchk_setup_rtsummary` allocates this structure with a block-sized `words[]` buffer. Scrub uses the geometry and buffer for compute/compare. Repair setup can add reservation and temporary exchange state before the common scrub setup allocates a transaction.

## State and persistence
The header defines in-memory scrub/repair state only. Persistent changes are made by implementation files that use this structure to compare or replace rtsummary contents.

## Dependencies and integration points
It depends on realtime allocation argument structures, online repair Kconfig, `xrep_tempexch`, and the xfile summary format used by `rtsummary.c` and its repair counterpart. It links scrub and repair code without exposing internal xfile helper functions broadly.

## Risks and test signals
Risks include flexible array sizing mismatches, stale geometry fields after growfs races, incorrect `prep_wordoff` use during repair copyout, and no-repair builds accidentally depending on repair state. Tests should compile repair and no-repair configurations, exercise block-size-sized buffers, large summary files, rtgroup and legacy formats, and early setup failures.
