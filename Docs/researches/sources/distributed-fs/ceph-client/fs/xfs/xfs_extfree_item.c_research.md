# sources/distributed-fs/ceph-client/fs/xfs/xfs_extfree_item.c

## Purpose
`xfs_extfree_item.c` implements extent-free intent/done log items and deferred operation types for freeing data, AGFL, and realtime extents. It guarantees that extent frees either complete or are replayed after crash recovery.

## Important APIs, types, and functions
It defines `xfs_efi_cache`, `xfs_efd_cache`, EFI/EFD item ops, log-space helpers, and defer op types `xfs_extent_free_defer_type`, `xfs_agfl_free_defer_type`, and `xfs_rtextent_free_defer_type`. Core routines allocate/format/release EFI and EFD log items, copy recovered 32/64/native log formats, add extents to intents/dones, finish normal and AGFL frees, process realtime frees, recover EFI work, relog intents, and consume recovered EFDs.

## Control flow
`xfs_extent_free_defer_add` computes and holds the destination group from the encoded startblock, selects the correct defer op, traces, and queues the item. Defer processing logs an EFI containing all extents, creates an EFD linked to the EFI, and processes each item. Normal frees call `__xfs_free_extent`, AGFL frees read AGF and call `xfs_free_ag_extent`, and realtime frees lock the rtgroup and call zoned or bitmap free helpers. Each successful or cancelled item is copied into the EFD and released. If a free returns `-EAGAIN`, the code copies the entire EFI into the EFD so the current intent is cancelled safely while a new intent is logged. Recovery reconstructs in-core EFIs from log records, validates each extent, queues deferred work, allocates a recovery transaction, finishes intents, and captures follow-on defer work.

## State and persistence
EFI items are persistent redo intents with two references: one for AIL insertion and one held until EFD completion. EFD items are persistent completion records that release matching EFI intents during recovery. Runtime state includes atomic next-extent slots, EFI reference counts, held group-intent references, defer pending lists, and optional rtgroup lock state. Recovered bad extents are treated as log corruption.

## Dependencies and integration points
The file connects the deferred-operation framework, transaction/log item machinery, AIL, log recovery, allocation btrees, reverse mapping owner info, busy extent insertion through lower free routines, realtime bitmap/rmap/refcount code, zoned allocator, and trace/error reporting. Transaction reservation code uses the exported log-space helpers.

## Risks and test signals
Risks include EFI/EFD reference imbalance, incomplete EFD cancellation during transaction roll, cross-architecture log format conversion, invalid recovered extent validation, mixing realtime and non-realtime intents, AGFL accounting differences, and CONFIG_XFS_RT disabled handling of realtime log items. Test signals include crash recovery between EFI and EFD, large extent counts beyond fast caches, `-EAGAIN` transaction roll, AGFL single-block frees, realtime bitmap and zoned frees, corrupt log item lengths, and relogging to push the log tail.
