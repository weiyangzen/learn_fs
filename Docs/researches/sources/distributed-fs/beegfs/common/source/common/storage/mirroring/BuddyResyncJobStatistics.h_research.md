<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/mirroring/BuddyResyncJobStatistics.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/mirroring/BuddyResyncJobStatistics.h

Purpose: Defines serializable resync progress/status records for buddy mirror jobs. `BuddyResyncJobState` captures lifecycle states from not started through success, interruption, failure, and completed-with-errors.

Important APIs/types: `BuddyResyncJobStatistics` stores state/start/end timestamps. `StorageBuddyResyncJobStatistics` adds discovered, matched, synced, and error counters for files and directories. `MetaBuddyResyncJobStatistics` adds metadata-specific counters for directory gather/sync, file sync, sessions, modification objects, and errors. Each class exposes a static `serialize` function for BeeGFS serdes integration and simple getters.

Control flow/state/persistence: This header has no active control flow beyond construction and serialization. State is value-owned and persisted only when callers serialize these records into messages, stores, or status files.

Dependencies/integration: Depends on `common/Common.h` and BeeGFS serialization helpers. Integrated with storage and metadata buddy resync reporting paths and any management/ctl message that transports job statistics.

Risks/test signals: Wire compatibility depends on field order and enum integer values. Tests should round-trip default and populated storage/meta statistics, verify old/new readers agree on ordering, and cover all terminal states plus error counter combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/mirroring/BuddyResyncJobStatistics.h -->
