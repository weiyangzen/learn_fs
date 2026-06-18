# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_log_recover.h

Purpose: Declares the internal recovery item dispatch interface and core recovery data structures.

Important APIs and types: `enum xlog_recover_reorder` selects replay ordering queues; `struct xlog_recover_item_ops` defines per-log-item callbacks for reorder, readahead, pass1, and pass2; `struct xlog_recover_item` stores recovered item regions; `struct xlog_recover` tracks partial transactions by transaction id. Extern ops cover icreate, buffers, inodes, dquots, quotaoff, bmap/rmap/refcount/extent intents and done items, attr intents, mapping exchange, and realtime variants.

Control flow: recovery reads log operations into `xlog_recover_item` structures, associates each with item ops, optionally reorders them, performs pass1 bookkeeping, then pass2 replay. Intent items reconstruct in-core intent items and insert them into the AIL; done items find corresponding intents and release them. `xlog_recover_resv` adapts normal transaction reservations for intent replay by forcing logcount to one.

State and persistence: recovery consumes persistent log regions and creates transient transaction/item queues. It also manages the buffer cancel table and recovered intent lifecycle so replay does not redo canceled buffers or completed deferred operations.

Dependencies and integration: depends on log item type codes from `xfs_log_format.h`, transaction reservations, buffer cache readahead/cancel logic, inode lookup helpers, AIL intent handling, and deferred operation types.

Risks and test signals: replay ordering and intent lifetime are correctness-critical. Tests should cover canceled buffer replay, inode-buffer ordering, partial continued transactions, recovered intents with tight log grant space, and failures during pass2 cleanup.
