# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/AlluxioMasterRestServiceHandlerTest.java

Purpose: tests selected REST handler behavior for master info assembly, mount URI matching, and web UI log listing.

Important APIs/types/functions: uses `AlluxioMasterRestServiceHandler`, `AlluxioMasterProcess`, `MasterRegistry`, `MetricsMaster`, `BlockMaster`, `FileSystemMaster`, `NoopJournalSystem`, `UnderFileSystemFactoryRegistry`, `AlluxioMasterInfo`, `Capacity`, `WorkerInfo`, `MasterWebUILogs`, and `UIFileInfo`.

Control flow: setup creates a mocked master process and servlet context, starts a real registry with metrics, block, and file-system masters, registers a mock UFS factory for `test://test/`, registers two workers with tiered total/used bytes, and clears a pinned-files metric. `getMasterInfo` stubs RPC address, start/uptime, and a metric gauge, calls `getInfo(false)`, and validates configuration, metrics, version, capacity, UFS capacity, and worker IDs. `isMounted` stubs a mount table with an S3 URI and verifies only metric-escaped normalized variants match. `testGetWebUILogsByRegex` creates wanted and unwanted log file names, sets `LOGS_DIR`, and verifies web UI logs include only matching master log/out/txt/gc/exit-metrics files.

State and persistence behavior: uses in-memory masters with no-op journal plus real temporary log files. Metrics are global registry state.

Dependencies and integration points: integrates REST handler with servlet context lookup, master process facade, block worker registration, UFS capacity reporting, metric escaping, and UI log filtering.

Risks: PowerMock and global UFS factory/metric registry state can leak if cleanup changes. Only success responses are covered.

Test signals: useful integration signal for REST data aggregation and web log filename filtering.
