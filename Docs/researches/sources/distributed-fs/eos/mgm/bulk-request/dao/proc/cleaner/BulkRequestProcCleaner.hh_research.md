## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleaner.hh

Purpose: declares the proc bulk-request cleaner thread wrapper. It owns an `AssistedThread`, references the proc location schema, and owns immutable cleaner configuration.

Important APIs: constructor, `Start()`, `Stop()`, `backgroundThread(ThreadAssistant&)`, and destructor. The documented behavior is deletion of requests not queried for longer than the configured threshold.

Integration: tied to MGM startup/configuration and global `gOFS` in implementation. Risks include non-owning location reference lifetime, `const unique_ptr` config preventing reconfiguration, and join semantics if `Stop()` is called before start depending on `AssistedThread`. Test signals should validate construction lifetime and thread termination behavior with a fake assistant where possible.
