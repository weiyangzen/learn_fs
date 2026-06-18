## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaStats.cc

Purpose: Implements QuarkDB-backed quota nodes and the quota-node manager. It persists quota counters into two hashes per container/quota node: UID counters and GID counters.

Important APIs and control flow: `QuarkQuotaNode::addFile()` and `removeFile()` compute physical size through `IQuotaStats::getPhysicalSize()`, stage a single `HINCRBYMULTI` through `MetadataFlusher`, then update the local `QuotaNodeCore`. `meld()` scans another node's UID/GID hashes and increments this node's hashes before melding the cache. `updateFromBackend()` scans both hashes, parses `<id>:logical_size|physical_size|files` fields, populates core maps, and deletes zeroed fields. `replaceCore()` deletes both backend hashes and writes all counters from a replacement core. `updateCore()` partially overwrites backend fields from an update core. `QuarkQuotaStats` lazily loads nodes, registers new nodes, removes nodes, scans all quota IDs, and parses key names.

State and persistence: backend mutations are staged through `MetadataFlusher`, so immediate reads through `QClient` may lag unless synchronized elsewhere. `pNodeMap` caches loaded quota nodes. `updateFromBackend()` mutates `pCore` maps directly via friendship and cleans zero entries from QuarkDB.

Dependencies and integration: depends on quota interfaces, `QuotaNodeCore`, QuarkDB constants, `QHash`, `QScanner`, `MetadataFlusher`, and string tokenization. It is tied to `IContainerMD::id_t` as the quota-node ID.

Risks and test signals: there is no mutex around `pNodeMap`, so manager calls appear single-thread-assumed. `replaceCore()` stages `DEL` followed by many `HSET`s; a crash mid-flush can temporarily erase or partially rewrite quota state unless the background flusher replay guarantees cover it. `updateFromBackend()` does not clear existing core maps before scanning, so missing backend fields may leave stale in-memory fields unless entries become explicit zeroes. Tests should exercise key parsing, lazy load vs register collision, add/remove/meld persistence requests, zero cleanup, partial update semantics, and flusher synchronization expectations.
