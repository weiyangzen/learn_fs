# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/NextInodeProvider.cc

Purpose: Implements monotonic inode allocation backed by a QDB hash field, with local block reservation to reduce backend round trips.
Important APIs/types/functions: `InodeBlock::{reserve,getFirstFreeID,empty,blacklistBelow}`; `NextInodeProvider::{configure,getFirstFreeId,reserve,blacklistBelow}`; private `getDBValue`, `allocateInodeBlock`, and `blacklistDBThreshold`.
Control flow: `reserve()` first consumes the current `InodeBlock`; when empty, `allocateInodeBlock()` atomically advances `pHash[pField]` with `hincrby`, creates a local range, then returns the first value. `getFirstFreeId()` peeks local state or returns `getDBValue()+1`.
State/persistence: local state is `mInodeBlock` and growing `mStepIncrease`; durable high-water mark is the QDB hash value. Block size grows by one until just over 5000, trading restart waste for fewer QDB writes.
Dependencies/integration: uses `qclient::QHash`, EOS assertions/logging, and service constants through callers such as `UnifiedInodeProvider`.
Risks: `configure()` must precede use; `std::stoull` over signed storage and unchecked buffer format can throw; blacklisting only updates QDB when the local block is exhausted, so high-water mark can lag until needed.
Test signals: `NextInodeProviderTest` covers sequential allocation, restart continuation with tolerated gaps, blacklisting, off-by-one around `2^32`, negative thresholds, and multiple resets.
