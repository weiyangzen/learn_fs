# sources/distributed-fs/ceph-client/fs/xfs/xfs_fsmap.c

## Purpose
`xfs_fsmap.c` implements `GETFSMAP` for XFS. It translates user fsmap keys into data/log/realtime device queries, enumerates reverse mappings or free-space records, fabricates gaps, reports sharing, and copies results back to userspace.

## Important APIs, types, and functions
The public entry point is `xfs_ioc_getfsmap`. Internal types are `struct xfs_getfsmap_info` for query state and `struct xfs_getfsmap_dev` for per-device handlers. Important helpers convert fsmap units/owners, validate keys/devices, format results, check shared extents, query data-device rmapbt or bnobt, query external log, query realtime bitmap or realtime rmapbt under `CONFIG_XFS_RT`, and run the top-level `xfs_getfsmap` device loop.

## Control flow
The ioctl copies and validates the header/reserved fields, allocates an internal buffer up to 128 KiB with page fallback, converts the two keys to internal basic-block units, and loops until the user buffer fills or the query finishes. `xfs_getfsmap` validates flags/devices/key ordering, enables rmap ownership only when rmapbt exists and the caller has `CAP_SYS_ADMIN`, installs data/log/rt handlers, sorts by device id, and calls handlers inside empty transactions for recursive buffer-lock protection. Data handlers convert low/high physical keys to AG-local rmap keys and iterate perags. Rmapbt handlers enumerate ownership; bnobt fallback enumerates free extents and reports unknown gaps. Realtime handlers perform analogous rtbitmap or rtrmapbt scans and handle zoned internal-rt synthetic regions. `xfs_getfsmap_helper` filters continuation records, emits gap records, converts owners/flags, checks refcount btrees for shared file data, and stops with `-ECANCELED` when the internal buffer is full.

## State and persistence
The code is read-only with respect to filesystem metadata. Runtime state tracks continuation low keys, next expected disk address, end address, current group, AGF buffer, and output counters. It does not persist state; userspace resumes by feeding the last returned record as the next low key.

## Dependencies and integration points
It integrates Linux `fsmap` ioctl ABI, XFS rmap/refcount/free-space btrees, realtime bitmap/rmap/refcount btrees, perag and rtgroup iterators, transaction buffer recursion, device encoding, capability checks, tracepoints, and ioctl dispatch.

## Risks and test signals
Risks include off-by-one continuation semantics, unit conversion between bytes/basic blocks/fsblocks/rtblocks, owner mapping of special owners, unprivileged fallback leaking too little or too much, synthetic gap correctness, shared-flag false positives/negatives, device ordering with internal realtime volumes, and memory buffer refill loops. Test signals include count-only mode, small user buffers forcing `-ECANCELED` refill, low key with nonzero length, CAP_SYS_ADMIN versus unprivileged output, filesystems with and without rmapbt/reflink/realtime/external log/zoned rt, invalid reserved fields, malformed owner/flag keys, and fatal signal interruption during long scans.
