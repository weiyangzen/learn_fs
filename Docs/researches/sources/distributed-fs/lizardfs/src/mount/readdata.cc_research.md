## sources/distributed-fs/lizardfs/src/mount/readdata.cc

Purpose: implements high-level file read handling for mounted files, combining chunk-location/reading, connection pooling, retry/backoff, cache lookup/fill, and adaptive read-ahead.

Important APIs/types: internal `readrec` owns `ChunkReader`, `ReadCache`, `ReadaheadAdviser`, inode, refresh counter, and expiry flag. Public functions include timeout getters, `read_data_init`, `read_data_new`, `read_data`, `read_data_end`, `read_inode_ops`, and `read_data_term`.

Control flow: init configures atomics, source IP, tweaks, connector timeouts, and starts `read_data_delayed_ops`, which cleans connection pool state and removes expired read records. `read_data_new` creates per-open read records. `read_data` feeds the adviser, queries cache, computes a request size at least as large as the asked range or read-ahead window, then calls `read_to_buffer`. `read_to_buffer` prepares chunk locations as needed, reads chunk segments with configured timeouts and XOR prefetch setting, handles EOF short reads, retries recoverable exceptions with exponential sleep, and maps ENOENT to EBADF.

State and persistence: global atomics store retry, timeout, cache, read-ahead, and prefetch settings. Active read records live in an unordered multimap protected by `gMutex`; `read_data_end` only marks expiry, and the delayed thread deletes records later. Data cache is per-readrec and memory-only.

Dependencies and integration: uses `ConnectionPool`, `ChunkConnectorUsingPool`, `ChunkReader`, `ReadPlanExecutor`, `mastercomm` for source IP, `Tweaks` for runtime configuration, and `ReadCache` for buffered slices. Called by `LizardClient::read`.

Risks: `read_data_freebuff` is declared in the header but not implemented here. Active record lifetime depends on delayed cleanup; callers must not use a record after `read_data_end`. The retry loop permits `try_counter > maxRetries`, so total attempts deserve precise validation. Cache and record operations are partially synchronized; per-record cache is otherwise used by the owning file handle.

Test signals: no direct unit test in this subset. Exercise cache hits/misses, inode refresh, chunk boundary reads, EOF, recoverable and unrecoverable chunk errors, tweak mutation, and termination cleanup.
