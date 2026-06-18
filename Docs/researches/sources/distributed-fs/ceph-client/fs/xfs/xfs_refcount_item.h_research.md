# sources/distributed-fs/ceph-client/fs/xfs/xfs_refcount_item.h

Purpose: Declares the in-core CUI/CUD log item structures and public helpers for deferred refcount update logging.

Important APIs and types: `struct xfs_cui_log_item` wraps a generic log item, CUI reference count, next extent index, and variable-sized `xfs_cui_log_format`. `struct xfs_cud_log_item` wraps a done log item, pointer to the associated CUI, and `xfs_cud_log_format`. `XFS_CUI_MAX_FAST_EXTENTS` controls cache-backed versus dynamic allocation. `xfs_cui_log_item_sizeof` computes allocation size for variable extent counts. Public functions include `xfs_refcount_defer_add`, `xfs_cui_log_space`, and `xfs_cud_log_space`.

Control flow and integration: Refcount users allocate an `xfs_refcount_intent` and add it through `xfs_refcount_defer_add`; the implementation creates CUI/CUD log items as part of deferred transaction processing. Log reservation code calls the log-space helpers. The structures mirror on-disk log formats defined in log format headers.

State and persistence: CUI stores redo intent state until matching CUD completion releases it. The header defines only in-core wrappers; persistence is performed by item formatting in `xfs_refcount_item.c`.

Dependencies and integration points: Depends on `xfs_log_item`, `xfs_cui_log_format`, `xfs_cud_log_format`, dyanmic-sized log formats, and slab caches created elsewhere. It is used by reflink, COW, and refcount btree update paths.

Risks and invariants: The fast-extent threshold must stay compatible with the cache object size. CUI/CUD lifetime is tied to reference counts and log recovery, so structure changes require matching format, recovery, and reservation updates. The header comment states the core crash invariant: intent in the first rolled transaction, done item in the transaction that performs refcountbt updates.

Test signals: Build-time structure sizing, log reservation calculations for extent counts above and below the fast path, and crash tests proving CUI without CUD replays while CUD cancels the intent.
