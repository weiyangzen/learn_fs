# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/MiniDFSCluster.java

## Purpose
`MiniDFSCluster` is the central in-process HDFS test harness. It builds one or more NameNodes plus a configurable set of DataNodes inside a single JVM, manages temporary name/data directories, exposes client handles, and offers fault-injection helpers used by many HDFS tests.

## Important APIs, Types, and Functions
- `MiniDFSCluster.Builder` is the primary API. It configures NameNode ports, DataNode counts, storage types/capacities, format/restart behavior, HA/federation topology, host/rack mappings, DN config overlays, fsync skipping, and address binding checks before calling `build()`.
- `DataNodeProperties` captures a stopped/restartable DN: `DataNode`, saved `Configuration`, startup args, secure resources, and IPC port.
- `NameNodeInfo` tracks each NN instance with its nameservice ID, NN ID, startup option, and NN-specific configuration.
- `initMiniDFSCluster(...)` is the constructor core: disables `System.exit`, enables symlinks, chooses base/data dirs, normalizes test config, formats/starts NameNodes, starts DataNodes, waits for activity, and refreshes proxy-user config.
- `configureNameNodes`, `configureNameService`, `initNameNodeConf`, `createNameNode`, and `copyNameDirs` translate `MiniDFSNNTopology` into HDFS config keys, shared edits directories, formatted storage, and live NameNode instances.
- `startDataNodes(...)` overloads create per-DN configs, storage directories, simulated datasets, static rack mappings, secure resources, and daemon threads.
- Lifecycle helpers include `shutdown`, `shutdownDataNodes`, `shutdownNameNode`, `restartNameNode`, `restartDataNode`, `restartDataNodes`, `waitClusterUp`, `waitActive`, and `waitFirstBRCompleted`.
- Fault helpers include `corruptBlockOnDataNodes`, `corruptBlockOnDataNodesByDeletingBlockFile`, `corruptReplica`, `corruptMeta`, `deleteMeta`, `truncateMeta`, `changeGenStampOfBlock`, `setDataNodeDead`, and `injectBlocks`.
- Inspection helpers expose NameNode RPCs, namesystems, block reports, materialized replicas, block/metadata file paths, filesystem clients, NameNode ports, HTTP URIs, storage directories, and lease/recovery knobs.
- Security/provided-storage helpers are `setupNamenodeProvidedConfiguration` and `setupKerberosConfiguration`.

## Control Flow
The builder fills defaults, including scanner shutdown timeout, disabled load-aware redundancy selection, default dataset factory storage count, and round-robin volume policy spacing. The protected builder constructor fills a simple single-NN topology if absent, duplicates 1D storage type/capacity inputs across DataNodes, then delegates to `initMiniDFSCluster`.

`initMiniDFSCluster` wraps startup in a success guard. It mutates the supplied configuration for replication, maintenance replication, safemode extension, decommission interval, topology mapping, HA checkpoint/log-roll behavior, and edit-log fsync behavior. It configures and starts NameNodes first. If formatting is requested, it deletes stale DataNode data. It returns early for `StartupOption.RECOVER`; otherwise it starts DataNodes and waits for the cluster to become active. Any startup failure triggers `shutdown`.

NameNode setup is topology-driven. `configureNameNodes` writes nameservice and HA keys globally. `configureNameService` formats the first NN in an HA nameservice, copies its name dirs to later NNs to preserve cluster/block-pool IDs, starts each NN with an NN-specific config, and writes actual bound ports back to both NN and global configs.

DataNode startup validates array lengths, chooses hostnames, applies per-DN overlays, creates managed storage directories when requested, optionally configures simulated capacity, registers host/rack static mappings, handles secure DN resources, retries KDC/SASL replay-prone starts, starts the daemon, records `DataNodeProperties`, waits for all NNs to become active, and optionally applies per-volume test capacities.

Shutdown closes tracked filesystem handles, stops DNs, stops and joins NNs, clears shutdown hooks, and either deletes or schedules deletion of the cluster base dir. Restart paths remove nodes from internal lists, optionally preserve ports, recreate daemons from saved configs, and restore capacity overrides.

## State and Persistence Behavior
The class owns mutable cluster state in `conf`, `namenodes`, `dataNodes`, `numDataNodes`, `base_dir`, `data_dir`, `waitSafeMode`, `federation`, `fileSystems`, and `storageCap`. It also increments a static `instanceCount` to disambiguate clusters in a single JVM.

Persistent state is intentionally test-local. NameNode name dirs live under `name-<ns>-<slot>`; secondary/checkpoint dirs under `namesecondary-*`; shared HA edits under `shared-edits-<min>-through-<max>`; DN data under `data/data<N>`. Formatting deletes those dirs; HA formatting copies the first NN dirs; shutdown may delete the base dir immediately or on JVM exit. Block corruption helpers directly mutate block and metadata files through `FsDatasetTestUtils.MaterializedReplica`.

The class also mutates global/static test state: `ExitUtil.disableSystemExit`, `FileSystem.enableSymlinks`, `DefaultMetricsSystem.setMiniClusterMode`, `StaticMapping`, `NetUtils` static resolution, `EditLogFileOutputStream` fsync behavior, `ShutdownHookManager`, proxy-user configuration, and optional `SimulatedFSDataset` factory. Tests that reuse JVM state can be affected by these global changes.

## Dependencies and Integration Points
This harness integrates with `NameNode`, `DataNode`, `FSNamesystem`, `DFSClient`, `DFSAdmin`, `DFSTestUtil`, `NameNodeAdapter`, `DataNodeTestUtils`, `BlockManagerTestUtil`, `FsDatasetTestUtils`, `SimulatedFSDataset`, `StaticMapping`, security/Kerberos utilities, SSL test utilities, and HDFS configuration key families. `MiniDFSNNTopology` is the main input model for HA/federation. Many tests consume this class through `Builder`, `getFileSystem`, `getNamesystem`, restart helpers, and corruption helpers.

## Risks and Edge Cases
- The class heavily mutates caller-supplied `Configuration` objects and several process-wide singletons; test ordering can matter if cleanup is incomplete.
- Array-length validation and index use are critical for storage types, storage capacities, overlays, ports, racks, and hosts.
- Several waits use polling and fixed timeouts, so slow CI or asynchronous block reports can cause flakes.
- `getNN(int)` returns `null` for invalid indexes, which can become later `NullPointerException`s rather than immediate argument errors.
- `getBlockFile(int, ...)` and `getBlockMetadataFile(int, ...)` loop over storage dirs `0..1`, while the configurable `storagesPerDatanode` can differ from two.
- Direct block-file corruption bypasses normal HDFS invariants by design; callers must ensure they target materialized local replicas, not simulated datasets unless supported.
- `shutdownNameNode` clears fields inside `NameNodeInfo`; restart relies on saved `conf` and `startOpt` remaining valid.
- Security startup has retry logic only around SASL replay symptoms; other secure-resource failures are printed and may surface later.

## Test Signals
The file is itself test infrastructure. Strong signals are its assertions/preconditions, exceptions on invalid topology/storage config, startup/shutdown success, `waitActive` registration checks, restart paths, and failure-injection helpers. Downstream tests validate it indirectly by successfully creating clusters, simulating HA/federation, corrupting replicas, injecting simulated blocks, triggering reports, and restarting nodes.
