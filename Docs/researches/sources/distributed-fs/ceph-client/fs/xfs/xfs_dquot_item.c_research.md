# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item.c

Purpose: Implements the XFS dquot log item used to journal individual dquot updates and coordinate pinning, transaction release, AIL push, precommit buffer attachment, and debug validation.

Important APIs, types, and functions: Provides `xfs_qm_dquot_logitem_init()` and item ops for size, format, pin, unpin, release, committing, precommit, and push. Includes `xfs_qm_dqunpin_wait()` and DEBUG_EXPENSIVE dquot verification.

Control flow: Formatting emits a `xfs_dq_logformat` plus serialized `xfs_disk_dquot`. Pin/unpin adjust `q_pincount`. Release unlocks the dquot at transaction completion. Precommit verifies and attaches the backing buffer. AIL push skips pinned or locked dquots, obtains qlock and dqflock, uses the attached buffer, flushes the dquot, and queues the buffer for delwri.

State and persistence: The log item records dquot id, block, offset, length, and full disk dquot contents. Dirty and attached-buffer state are protected by `qli_lock`.

Dependencies and integration points: Depends on dquot conversion/verification, XFS log item framework, AIL push protocol, attached-buffer helpers, and log force for unpin waits.

Risks and test signals: Risks are flushing without an attached buffer, dirty-state loss after relogging, lock ordering bugs, reclaim races, and corrupt quota records. Test quota updates under reclaim, concurrent relog/dqflush, shutdown after commit, DEBUG_EXPENSIVE verification, and pinned dquot log-force behavior.
