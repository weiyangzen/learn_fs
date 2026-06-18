# sources/distributed-fs/ceph/src/mds/RecoveryQueue.cc

Purpose: implements an in-memory MDS file recovery queue that probes object sizes/mtimes for authoritative inodes needing max-size recovery after client writes or failover.

Important APIs and control flow: `enqueue()` clears `STATE_NEEDSRECOVER`, sets `STATE_RECOVERING`, auth-pins the inode, increments counters, and puts it on the normal queue if not already queued. `prioritize()` moves a queued inode to the front queue. `advance()` starts work from the priority queue first while below `mds_max_file_recover`. `_start()` checks projected inode client ranges and max size, starts `Filer::probe()` for new work, or marks active work for restart. `_recovered()` handles probe result, respawns on blocklist, marks MDS damaged on other OSD read errors, clears/restarts state, updates max size through `Locker::check_inode_max_size()`, evaluates the file lock, unpins, and advances more work.

State and persistence: no durable queue exists; recovery state is represented by inode state bits, auth pins, elist membership, and `file_recovering` restart flags. If the MDS dies, recovery candidates must be rediscovered from metadata/open-file state.

Dependencies and integration: depends on `CInode`, `MDCache`, `MDSRank`, `Locker`, `Filer`, perf counters, and config `mds_max_file_recover`. It is owned by `MDCache` and invoked when inodes require file size recovery.

Risks and test signals: risks include dangling queue list membership, double enqueue/prioritize, restart while a probe is in flight, and correctly clearing auth pins on skip/error paths. Tests should cover priority ordering, max concurrency, no max-size skip, restart flag behavior, blocklist respawn, and logger counter updates.
