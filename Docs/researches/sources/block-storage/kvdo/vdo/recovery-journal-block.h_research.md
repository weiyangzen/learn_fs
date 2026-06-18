# File Research: sources/block-storage/kvdo/vdo/recovery-journal-block.h

Read completely: 128 lines.

This header defines `struct recovery_journal_block`, the in-memory state for a recovery journal tail block. Fields include list and write-waiter nodes, owning journal, packed block buffer, active sector pointer, metadata VIO, sequence/block numbers, commit flags, entry counters, and wait queues for entries and commit completion.

It provides inline helpers to recover a block from its list entry and test whether a block is dirty, empty, or full. Public functions cover allocation, free, initialization, entry enqueue, block commit, dumping, and commit-readiness checks.

Dependencies: packed recovery journal block format, `struct recovery_journal`, VIO/data VIO forward declarations through included headers, Linux bio callback type, wait queues, and VDO types.

Security/reliability notes: `vdo_is_recovery_block_full(NULL)` returns true, letting callers treat absent active blocks as needing advancement.
