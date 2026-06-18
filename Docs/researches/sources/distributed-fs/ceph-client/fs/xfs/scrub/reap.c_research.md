# sources/distributed-fs/ceph-client/fs/xfs/scrub/reap.c

## Purpose
`reap.c` disposes of blocks that belonged to old or damaged metadata after online repair has rebuilt replacement structures. It decides whether to free extents, remove only reverse mappings for crosslinked blocks, invalidate incore buffers, manage AGFL returns, and keep deferred log intent chains within transaction reservation budgets.

## Important APIs, Types, And Functions
Public APIs are `xrep_reap_agblocks`, `xrep_reap_fsblocks`, `xrep_reap_rtblocks`, `xrep_reap_metadir_fsblocks`, `xrep_reap_ifork`, `xrep_bufscan_max_sectors`, and `xrep_bufscan_advance`. `struct xreap_state` carries scrub context, owner/reservation or inode/fork target, buffer invalidation counters, and deferred-op counters.

AG/free-space helpers include `xreap_agextent_select`, `xreap_agextent_iter`, `xreap_agextent_binval`, `xreap_put_freelist`, and limit configurators. File fork helpers include `xreap_bmapi_select`, `xreap_bmapi_binval`, `xrep_reap_bmapi_iter`, `xreap_ifork_extent`, and `xreap_configure_bmapi_limits`. Realtime paths are compiled under `CONFIG_XFS_RT`.

## Control Flow
For per-AG and fsblock bitmaps, the code walks bitmap extents, selects maximal subranges with the same crosslink status by querying rmapbt, invalidates buffers where safe, and either schedules rmap removal or deferred free operations. Crosslinked blocks are unmapped from the repaired owner but not freed. Non-crosslinked blocks are invalidated and freed or returned to AGFL depending on reservation type.

For file forks, `xrep_reap_ifork` walks real mappings, reads AGF state for the mapping's AG, chooses crosslinked subranges with offset-specific owner info, invalidates file buffers, schedules bmap removal, quota block-count adjustment, rmap removal, and free operations. It finishes deferred ops after each mapping. Realtime variants lock rtgroups and use rt rmap/refcount/free intent paths.

## State And Persistence Behavior
Persistent changes include rmap removal, refcount cleanup for CoW staging extents, bmap extent removal, quota block-count adjustments, AGFL insertion, and free-space updates. Incore buffer invalidation is transaction logged where possible, or stale-marked for unloggable large buffers. The code frequently rolls or finishes transactions based on computed log reservation limits.

## Dependencies And Integration Points
It depends on rmapbt, refcountbt, allocation, AG/rtgroup locking, bitmap walkers, deferred operation items, buffer cache APIs, quota accounting, bmap APIs, metadata reservation reset, and tracepoints. Many repair modules call it after rebuilding btrees or file forks.

## Risks And Edge Cases
Crosslinked metadata cannot always be fully fixed because buffer-cache aliasing can hide multi-block overlaps. The code deliberately avoids freeing blocks with other owners. Log reservation underestimation triggers shutdown to avoid unsafe continuation. Buffer invalidation limits can shorten an extent and force transaction rolls. AGFL blocks are handled one at a time. Realtime support is conditional.

## Test Signals
Tests should cover crosslinked and non-crosslinked old btree blocks, CoW staging extents, AGFL reaping, metadir fsblocks, file attr/data fork reaping, large remote xattr buffers, transaction roll thresholds, realtime bitmap paths, missing rmap records, and crash recovery with partially completed deferred frees.
