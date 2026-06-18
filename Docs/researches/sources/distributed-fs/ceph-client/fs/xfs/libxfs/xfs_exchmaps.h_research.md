# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_exchmaps.h

## Purpose
`xfs_exchmaps.h` declares the in-core request and intent interfaces for XFS mapping exchange. It defines the state carried across deferred exchange transactions, request parameters used by callers and estimators, internal flags, fork selection helpers, and public entry points implemented by `xfs_exchmaps.c`.

## Important APIs, Types, and Macros
`struct xfs_exchmaps_intent` stores the deferred operation state: list linkage, participating inodes, current offsets in both files, remaining block count, optional final sizes, and flags. `struct xfs_exchmaps_req` is the caller-facing request plus estimator outputs: source inodes, start offsets, block count, operation flags, affected data/rt block counts per inode, reserved blocks, and estimated number of exchange steps.

The internal flag `__XFS_EXCHMAPS_INO2_SHORTFORM` requests post-op conversion of inode2 back to local/shortform format where possible. `XFS_EXCHMAPS_INTERNAL_FLAGS` separates internal-only flags from logged/user-visible flags. `XFS_EXCHMAPS_PARAMS` limits flags accepted by estimation to attr fork selection, size setting, and inode1-written optimization. Inline helpers `xfs_exchmaps_whichfork` and `xfs_exchmaps_reqfork` select data or attr fork from intent/request flags.

## Control Flow and Integration
The header exposes the lifecycle used by higher-level code: estimate via `xfs_exchmaps_estimate` or `xfs_exchmaps_estimate_overhead`, initialize/destroy the slab cache, allocate an intent, precondition reflink and extent-count state in a transaction, finish one deferred step, validate forks, and schedule the exchange with `xfs_exchange_mappings`. The declarations decouple callers and log item code from implementation details in `xfs_exchmaps.c`.

## State and Persistence
The request is mostly transient, but its estimator fields drive transaction reservation and quota reservation decisions. The intent becomes deferred operation state and is eventually represented by exchange-map intent log items, making the operation recoverable across crashes. Negative `xmi_isize*` values mean no size update is required; otherwise the finish path uses them to keep on-disk sizes coherent while moving mappings.

## Dependencies and Integration Points
The header depends on XFS inode, transaction, fork, and flag definitions from surrounding libxfs headers. It is included by exchange-map implementation, log item/deferred-op code, and higher-level exchange-range callers that need estimates and scheduling.

## Risks and Test Signals
Risks include mixing internal flags into logged/public flags, passing unsupported flags to estimation, or failing to initialize the estimator-output fields before use. Fork selection must match both estimator and executor behavior, especially for attr-fork exchanges where size swapping is invalid. Test signals include compile-time checks for flag separation, exchange-range reservation tests, attr/data fork coverage, slab cache init/destroy paths, and crash recovery with partially completed intents.
