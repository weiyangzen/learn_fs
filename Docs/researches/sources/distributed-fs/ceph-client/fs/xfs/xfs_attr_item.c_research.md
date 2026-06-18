<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.c

Purpose: Implements logged extended-attribute deferred operations using ATTRI intent and ATTRD done log items, including parent pointer variants, name/value buffer lifetime management, recovery validation, replay, and relogging.

Important APIs and functions: `xfs_attr_defer_add` creates deferred attr work and maps high-level set/remove/replace operations to log op flags. `xfs_attr_create_intent`, `xfs_attr_create_done`, `xfs_attr_finish_item`, `xfs_attr_abort_intent`, `xfs_attr_cancel_item`, `xfs_attr_recover_work`, and `xfs_attr_relog_intent` implement `xfs_attr_defer_type`. ATTRI/ATTRD item ops format, size, release, match, and connect done items back to intent items. Recovery entry points are `xlog_recover_attri_commit_pass2` and `xlog_recover_attrd_commit_pass2`.

Control flow: Deferred attr work captures a `struct xfs_da_args` and an operation state machine. For logged operations, the create-intent path allocates a refcounted contiguous name/value object, initializes an ATTRI with an intent id, fills inode/op/filter/length fields, and logs format plus name/new-name/value/new-value iovecs as needed. Finish calls `xfs_attr_set_iter`; if the delayed attr state is not done, it returns `-EAGAIN` so defer processing rolls transactions. Done items release the ATTRI reference. Recovery validates format, op/filter namespace, iovec counts and lengths, parent pointer values, inode numbers, feature flags, and attr names before reconstructing `xfs_attr_intent` and replaying it under a recovery transaction.

State and persistence: ATTRI records describe unfinished xattr mutations in the log; ATTRD records cancel completed intents. The refcounted name/value object is shared by deferred work and log items to avoid repeated allocation/copying. Replay persists attr fork changes and parent pointer updates through normal attr state machines and transactions.

Dependencies and integration: Integrates with XFS defer ops, xlog recovery intent framework, attr state machine, parent pointer validation, inode recovery iget, transaction reservations, attr geometry, log iovec formatting, AIL reference lifetime, and error injection.

Risks: Log validation is security-critical because recovery allocates and replays operations from disk log data. Parent pointer ops require generation checks and exact value sizes. Refcount ordering between committed/unpinned ATTRI and ATTRD release is subtle. Returning `-EAGAIN` incorrectly can livelock or lose multi-transaction attr progress.

Test signals: Logged xattr set/remove/replace, parent pointer set/remove/replace, crash after ATTRI before ATTRD, relogging long-running intents, malformed log iovec counts/lengths/names/filters, inode generation mismatch, LARP error injection, and memory lifetime checks for shared name/value buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_attr_item.c -->
