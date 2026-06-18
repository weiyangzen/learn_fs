# subset-b-008146 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/SCMThroughputBenchmark.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/SCMThroughputBenchmark.java

Purpose: picocli/ServiceLoader Freon Vapor subcommand `scm-throughput-benchmark` (`stb`) for measuring SCM throughput for block allocation, container allocation, and container-report processing. It creates fake datanodes against a real SCM, forces pipelines and safe mode state where needed, and drives SCM client RPCs.

Important APIs/types/functions: `SCMThroughputBenchmark.call`, `createBenchmark`, `initSCMClients`, `registerFakeDatanodes`, `activatePipelines`, `exitSafeMode`; nested `ThroughputBenchmark`, `BlockBenchmark`, `ContainerBenchmark`, `ReportBenchmark`, and `FakeDatanode`; enum `BenchmarkType`. It uses `StorageContainerDatanodeProtocol`, `StorageContainerLocationProtocol`, and `ScmBlockLocationProtocol`.

Control flow: command options pick a benchmark. Cluster setup creates RPC clients, registers fake datanodes, optionally waits for SCM-created RATIS pipelines and force-opens them, then exits safe mode. The benchmark base queues one runnable per configured thread, starts them in a fixed executor, polls counters, shuts down, and prints throughput. Block and container benchmarks run concurrent allocation loops. Report benchmark first allocates containers, distributes reports among fake datanodes, snapshots SCM Prometheus counters, sends heartbeats, and polls metrics until processed counts reach target.

State/persistence: no durable local state. It mutates SCM state by registering synthetic datanodes, allocating containers/blocks, activating pipelines, and changing safe mode. Fake reports contain synthetic storage and container-replica metadata.

Dependencies/integration: Ozone Freon, picocli, `@MetaInfServices(VaporSubcommand.class)`, Hadoop RPC, SCM HAUtils clients, SCM Prometheus endpoint, Ozone protocol protobufs, Apache HttpClient, and replication options.

Risks: `BenchmarkType.valueOf` is case-sensitive; `ReportBenchmark.prepare` indexes `datanodes.get(i)` for `numThreads`, so `numThreads > numDatanodes` can fail. Metrics parsing assumes a space-delimited Prometheus value. Fixed port/default HTTP bind port assumptions and a 60 second pipeline wait make runs environment-sensitive. Fake datanodes ignore SCM commands and can leave benchmark artifacts in a real SCM.

Test signals: no direct test file in this subset. Useful tests would cover option validation, metric parsing, fake report construction, and `numThreads`/`numDatanodes` bounds.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/SCMThroughputBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/StreamingGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/StreamingGenerator.java

Purpose: Freon Vapor subcommand `strmg`/`streaming-generator` that builds a per-thread test directory and repeatedly streams a subdirectory from a local `StreamingServer` to a `StreamingClient`.

Important APIs/types/functions: `StreamingGenerator.call`, `generateBaseData`, `copyDir`, `threadRootDir`, `deleteDirRecursive`; uses `BaseFreonGenerator.runTests`, Dropwizard `Timer`, `ContentGenerator`, `DirectoryServerSource`, `DirectoryServerDestination`, `StreamingServer`, and `StreamingClient`.

Control flow: `call` initializes Freon metrics and executes `copyDir` for each generated index. On first use per thread, `copyDir` calls `generateBaseData`, which deletes the thread root, creates `streaming-0/dir1`, and writes `numberOfFiles` files of `fileSize`. Each iteration starts a server for the current source directory, streams `dir1` to the next destination directory, times the client stream, then deletes the previous source.

State/persistence: stores generated test data under `--root-dir` with child directories named after Java thread names and generation indexes. The `ThreadLocal<Integer>` counter is the per-thread state machine. Cleanup is recursive and destructive for the generated source path.

Dependencies/integration: picocli `@Command`, `@MetaInfServices(VaporSubcommand.class)`, Ozone container streaming package, Commons IO `FileUtils`, and Freon metrics.

Risks: port selection `1234 + (l % 64000)` can collide with existing processes or parallel workers. Recursive delete of `testRoot/threadName` requires safe `--root-dir` use. `ThreadLocal` state is never removed but command lifetime is short. Any stream failure leaves destination/source directories for manual inspection or cleanup.

Test signals: no direct tests in this subset. Tests should simulate one copy round with a temporary root and assert generated files move from `streaming-N` to `streaming-N+1`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/StreamingGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/Vapor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/Vapor.java

Purpose: command root for `ozone vapor`, a Freon-derived load generator that uses Ozone server components.

Important APIs/types/functions: class `Vapor extends Freon`, `subcommandType`, and `main`. The `@Command` annotation configures picocli name, help, version provider, and description.

Control flow: `main` constructs `Vapor` and delegates to `Freon.run(args)`. `subcommandType` returns `VaporSubcommand.class`, allowing Freon to discover/register only subcommands that implement this marker.

State/persistence: no state beyond inherited Freon command state and Ozone configuration handling.

Dependencies/integration: picocli, `HddsVersionProvider`, `Freon`, and Java service registration via marker subcommands such as `SCMThroughputBenchmark`, `StreamingGenerator`, and container generators.

Risks: because command discovery is marker-interface based, missing `@MetaInfServices(VaporSubcommand.class)` or wrong marker implementation in a subcommand makes it invisible under `ozone vapor`.

Test signals: no local test in this subset. A command-discovery smoke test should verify expected Vapor subcommands appear.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/Vapor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/VaporSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/VaporSubcommand.java

Purpose: marker interface used to identify subcommands belonging to `ozone vapor`.

Important APIs/types/functions: empty interface `VaporSubcommand`.

Control flow: no runtime logic. `Vapor.subcommandType()` returns this interface, and subcommands use `@MetaInfServices(VaporSubcommand.class)` so service discovery can find them.

State/persistence: none.

Dependencies/integration: integrates Freon command loading with the `org.kohsuke.MetaInfServices` service-generation pattern used by Vapor subcommands.

Risks: marker interfaces have no compile-time behavior contract; command classes must separately implement `Callable`/picocli annotations correctly.

Test signals: indirect command-discovery tests are the useful coverage; no direct test needed beyond compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/VaporSubcommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/BaseGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/BaseGenerator.java

Purpose: shared base for offline Ozone container metadata/data generators.

Important APIs/types/functions: `BaseGenerator extends BaseFreonGenerator implements Callable<Void>, VaporSubcommand`; options `--user`, `--key-size`, `--size`, and `--from`; getters `getUserId`, `getKeysPerContainer`, `getContainerIdOffset`, `getContainerSize`, and `getKeySize`.

Control flow: subclasses call getters during generation. `getContainerSize` uses explicit `--size` when supplied, otherwise reads `ozone.scm.container.size` from `ConfigurationSource` with SCM defaults. `getKeysPerContainer` integer-divides container size by key size.

State/persistence: no direct writes. It centralizes generation parameters, including a static user id shared by subclass commands in the JVM.

Dependencies/integration: Ozone Freon base class, HDDS configuration APIs, SCM container-size config, picocli options, and `VaporSubcommand`.

Risks: `userId` is static, so multiple generator instances in one JVM could share/overwrite it. `getKeysPerContainer` truncates remainders and can return zero if key size exceeds container size. No validation prevents zero/negative key sizes or offsets.

Test signals: no direct test. Subclass tests should cover default container-size resolution and key-count boundary cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/BaseGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorDatanode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorDatanode.java

Purpose: offline generator for Ozone datanode container files and block/chunk metadata.

Important APIs/types/functions: command `cgdn`; options `--datanodes`, `--index`, `--zero`, `--overlap`; `call`, `getScmIdFromStoragePath`, static `getPlacement`, `generateData`, `generatedRandomData`, `createContainer`, and `writeChunk`.

Control flow: `call` initializes Ozone config, block/chunk managers, storage dirs, VERSION metadata, `MutableVolumeSet`, checksum settings, and Freon timer, then runs `generateData`. For each requested container id, `getPlacement` decides whether the current datanode index stores it. Selected containers are created as `KeyValueContainer`s. For each block/key, the generator writes chunks up to `--key-size`, computes checksum before buffer consumption, writes the data and commit stages through `ChunkManager`, persists block metadata, and closes the container.

State/persistence: writes actual datanode container data/metadata under configured datanode storage volumes. Reads existing `hdds/VERSION` and SCM-specific directory names and uses persisted cluster/datanode IDs. `logCounter` simulates Ratis log indexes.

Dependencies/integration: Ozone container key-value implementation, chunk/block managers, storage-volume utilities, checksum config, HDDS storage dirs, Freon metrics, and the placement test.

Risks: intended for stopped/offline clusters; running against active datanode volumes could corrupt or conflict. `getPlacement` divides by `maxDatanodes / 3`, so fewer than three datanodes can divide by zero. `overlap` is not validated. Random-data generation comment says 4 bit but shifts bytes. Reusing `ByteBuffer` across write stages depends on chunk manager semantics.

Test signals: `TestGeneratorDatanode` verifies placement for 3 and 10 datanode layouts, including overlap 2. It does not cover storage writes, checksum/chunk persistence, invalid datanode counts, or overlap bounds.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorDatanode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorOm.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorOm.java

Purpose: offline generator for Ozone Manager RocksDB metadata representing a volume, bucket, directory hierarchy, keys, and block locations.

Important APIs/types/functions: command `cgom`; options `--volume` and `--bucket`; `call`, `writeOmKeys`, `writeOmBucketVolume`, `addDirectoryKey`, `writeOmData`, and `commitAndResetOMKeyTableBatchOperation`.

Control flow: `call` forces single-thread Freon execution, opens the OM DB from `OMStorage.getOmDbDir`, creates/updates volume, user, and bucket rows, opens the key table, and runs `writeOmKeys`. Each container index maps to a container id, then the generator writes `getKeysPerContainer` key records in one batch. `writeOmData` builds one block location per key, derives L1/L2/L3 pseudo-directories from the local id, conditionally writes directory keys, and writes the file key.

State/persistence: directly mutates OM metadata tables (`VOLUME`, `USER`, `BUCKET`, `KEY`) through `OMDBDefinition`. The key path constant is hard-coded as `/vol1/bucket1/...` even though fields use `volumeName` and `bucketName`.

Dependencies/integration: OM DB definitions/codecs, `DBStoreBuilder`, `BatchOperation`, OM helper types, Ozone ACLs, replication configs, and Freon metrics.

Risks: offline-only DB writer; concurrent OM access would be unsafe. Hard-coded `keyName` prefix ignores non-default `--volume`/`--bucket` and can write inconsistent rows. Volume quota is fixed to 100 bytes, which may not reflect generated data. Replication metadata uses standalone factor three for keys while datanode placement is synthetic.

Test signals: no direct test in this subset. Useful tests should cover custom volume/bucket names, generated directory keys, batch contents, and DB reopen compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorOm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorScm.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorScm.java

Purpose: offline generator for Storage Container Manager metadata rows.

Important APIs/types/functions: command `cgscm`; `call` opens the SCM DB and container table; `writeScmData` writes one `ContainerInfo` per requested index.

Control flow: Freon initialization creates Ozone config and SCM DBStore, gets `SCMDBDefinition.CONTAINERS`, times `writeScmData`, then closes DB. `writeScmData` adds `getContainerIdOffset() + index` as a closed standalone replication-factor-three container owned by `BaseGenerator.getUserId()`.

State/persistence: directly writes SCM RocksDB container metadata. No pipeline, replica, or datanode placement rows are written in this file.

Dependencies/integration: HDDS SCM DB definitions, `ContainerID`, `ContainerInfo`, standalone replication config, Freon metrics, and Vapor service registration.

Risks: must be run offline against a compatible SCM DB. It creates minimal closed container metadata, so other SCM subsystems may require separately generated datanode/OM state to be consistent. Existing container IDs can be overwritten depending on table semantics.

Test signals: no direct test. Integration validation should reopen SCM DB and verify generated `ContainerInfo` state/owner/replication fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/GeneratorScm.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/package-info.java

Purpose: package documentation for `org.apache.hadoop.ozone.freon.containergenerator`.

Important APIs/types/functions: no executable API; declares the package and describes it as container data/metadata generator components.

Control flow: none.

State/persistence: none directly. The package contains offline writers for datanode, OM, and SCM metadata.

Dependencies/integration: Java package-level documentation consumed by Javadocs and IDEs.

Risks: the short description is accurate but does not warn that the generator commands directly mutate offline storage/metadata.

Test signals: compile/package documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/containergenerator/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/package-info.java

Purpose: package documentation for `org.apache.hadoop.ozone.freon`.

Important APIs/types/functions: no executable API; describes the package as classes for testing and benchmarking an Ozone cluster.

Control flow: none.

State/persistence: none.

Dependencies/integration: Javadoc/IDE package metadata for the Vapor/Freon command package.

Risks: wording is broad and does not distinguish live-cluster benchmarks from offline metadata generators.

Test signals: compile/package documentation only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/test/java/org/apache/hadoop/ozone/freon/containergenerator/TestGeneratorDatanode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/test/java/org/apache/hadoop/ozone/freon/containergenerator/TestGeneratorDatanode.java

Purpose: JUnit test coverage for `GeneratorDatanode.getPlacement`.

Important APIs/types/functions: test methods `testPlacementSinglePipeline`, `testPlacement10Nodes`, `testPlacement10NodesOverlap`, and helper `compare`.

Control flow: each test invokes `compare`, which builds a `HashSet` from expected datanode indexes and asserts equality with the set returned by `getPlacement(containerId, maxDatanodes, overlap)`.

State/persistence: none.

Dependencies/integration: JUnit Jupiter assertions and `GeneratorDatanode`.

Risks: covers representative happy paths only. It does not validate invalid `maxDatanodes`, overlap values outside documented bounds, modulo behavior for larger ids, or actual datanode container file generation.

Test signals: confirms one-based datanode placement for 3-node single pipeline, repeated grouping for 10 nodes with overlap 1, and shifted overlapping groups for overlap 2.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/vapor/src/test/java/org/apache/hadoop/ozone/freon/containergenerator/TestGeneratorDatanode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/cli.c -->
# sources/object-store/daos/src/container/cli.c

Purpose: libdaos container client implementation. It implements DAOS container API task handlers for create, destroy, open, close, query, properties, ACLs, OID allocation, attributes, snapshots, epoch operations, handle serialization, and helper lookups.

Important APIs/types/functions: exported `dc_cont_init/fini`, `dc_cont_create/destroy/open/close/query/set_prop/update_acl/delete_acl/alloc_oids`, local/global handle conversion, attr APIs, snapshot APIs, `dc_cont_hdl2*` helpers, and `dc_cont_mark_all_slave`. Internal infrastructure includes `cont_task_priv`, `cont_rsvc_client_complete_rpc`, `cont_task_reinit`, `cont_req_prepare`, `cont_req_complete`, `dc_cont_alloc`, `dc_cont_props_init`, and `dc_cont_glob`.

Control flow: initialization queries supported container RPC protocol version and registers v8 or v9 formats. Most operations validate handles/arguments, choose the pool service rank, build a container RPC through `dc_cont_req_create`, attach operation-specific payload/bulk handles, register a completion callback, and send asynchronously. Completion callbacks run replicated-service leader handling, may reinitialize delayed tasks on retry/rechoose, copy results into user buffers, and release RPC/pool/container refs. Open creates a client `dc_cont`, refreshes pool map if needed, links into pool/container handle tables, initializes checksum/dedup/compression/encryption properties, and returns a handle. Close refuses open objects and unlinks handles.

State/persistence: client state lives in handle hash entries (`dc_cont`), pool container lists, checksummers, and global handle buffers. Persistent container metadata is owned by servers; client operations mutate it through RPC. `dc_cont_local2global` serializes handle UUIDs/capabilities/properties/min map version for cross-process use, while `global2local` reconstructs a slave handle.

Dependencies/integration: DAOS task scheduler, CART RPC/bulk, rsvc client, pool client/map refresh, ACL/prop helpers, checksum/dedup/compress/encrypt config, object OID generation, and `rpc.c` protocol definitions.

Risks: repeated async cleanup paths are reference-count sensitive. Attribute get/set/del duplicate names/values to avoid bad memory registration, but allocation callback ordering must remain correct. `dc_cont_set_prop` forbids immutable props and rewrites status pm_ver. `dc_cont_alloc_oids` talks to random UPIN targets and has separate stale-map retry logic. Unsupported rollback/subscribe/named snapshots return `-DER_NOSYS`. Protocol skew is handled only for current and previous versions.

Test signals: no tests in this subset. High-value tests include open/close refcount behavior, retry/rechoose callbacks, global handle round trips, attr bulk validation, immutable property rejection, stale map OID retry, and snapshot error cases.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/cli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/cli_internal.h -->
# sources/object-store/daos/src/container/cli_internal.h

Purpose: private client-side declarations shared inside DAOS container client code.

Important APIs/types/functions: `dc_cont_hdl_link`, `dc_cont_hdl_unlink`, `dc_cont_alloc`, and `dc_cont_put`.

Control flow: no implementation here. The functions are implemented/used by `cli.c` for handle hash lifecycle and reference management.

State/persistence: declares operations over `struct dc_cont` handle objects. These are in-memory client handles, not durable container metadata.

Dependencies/integration: included by container client modules that need internal handle lifecycle access without exposing it through public DAOS headers.

Risks: header is intentionally small; callers must honor reference-count conventions from the implementation.

Test signals: indirect via container open/close/global-handle tests.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/cli_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/container_iv.c -->
# sources/object-store/daos/src/container/container_iv.c

Purpose: server-side container IV cache implementation for distributing container snapshots, capabilities, properties, and tracked epoch boundaries across ranks/xstreams.

Important APIs/types/functions: IV ops `cont_iv_ops`; fetch/update helpers `cont_iv_fetch`, `cont_iv_update`; snapshot APIs `cont_iv_snapshots_fetch/update/refresh`, `ds_cont_fetch_snaps`, `ds_cont_revoke_snaps`; property APIs `cont_iv_prop_update/fetch`, `ds_cont_fetch_prop`; capability APIs `cont_iv_capability_update/invalidate`, `ds_cont_find_hdl`; epoch APIs `cont_iv_track_eph_update/refresh`, `ds_cont_fetch_ec_agg_boundary`; lifecycle `ds_cont_iv_init/fini`.

Control flow: each IV namespace entry owns a dbtree root handle storing per-container entries. Fetch checks the local tree, and if missing on the master lazily creates entries from RDB/container service state, then copies into caller buffers. Update applies local side effects such as opening/closing target container handles, refreshing target properties/snapshots, propagating tracked epoch reports to the leader, and updating the dbtree. Non-xstream-0 callers use Argobots ULT/eventual wrappers to run fetches on xstream 0.

State/persistence: IV cache is in-memory and dbtree-backed per namespace. It reflects persistent RDB/container state (`ds_cont_get_snapshots`, `ds_cont_get_prop`, handle lookup, EC aggregation boundary lookup) and pushes refreshed state into target-local container caches. Invalidation removes snapshot/property/capability/epoch entries and also invalidates OID IV entries.

Dependencies/integration: DAOS server IV layer, CART IV modes, Argobots, dbtree, pool/container server internals, security/ACL property conversion, OID IV, DTX/EC aggregation helpers.

Risks: many functions assert xstream 0, so wrong-call-context bugs can abort. Snapshot fetch uses a sentinel `snap_cnt == -1` to trigger caller buffer resize. Property IV entries require full property sets and assert required fields. Capability fetch can recurse through invalidation/retry when local handle state is stale. `cont_iv_snapshot_fetch_non_sys` assigns `snapshots = arg.snapshots` instead of `*snapshots`, which looks suspicious if caller expects the allocated pointer.

Test signals: no direct test in this subset. Tests should exercise missing-entry lazy creation, non-xstream fetch wrappers, property l2g/g2l round trips including ACLs/roots, snapshot resize sentinel, capability stale-handle recovery, and epoch report forwarding.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/container_iv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/oid_iv.c -->
# sources/object-store/daos/src/container/oid_iv.c

Purpose: server-side IV cache for reserving object ID ranges per container and pool.

Important APIs/types/functions: structs `oid_iv_key`, `oid_iv_entry`, `oid_iv_priv`; IV callbacks `oid_iv_key_cmp`, `oid_iv_ent_update`, `oid_iv_ent_refresh`, `oid_iv_ent_get/put/init/destroy`, `oid_iv_alloc`; exported `oid_iv_reserve`, `oid_iv_invalidate`, `ds_oid_iv_init`, and `ds_oid_iv_fini`.

Control flow: callers pass an `oid_iv_range` in an SGL to `oid_iv_reserve`. The IV update callback locks the per-entry mutex, satisfies requests from locally cached available IDs when possible, or forwards to the root/master. On the master, it calls `ds_cont_oid_fetch_add` to atomically advance persistent max OID. If forwarded, refresh updates local available range, reserves the originally requested count, writes the returned start OID into the caller's range, and unlocks.

State/persistence: local IV entries cache a range (`oid`, `num_oids`) plus current request identity to detect duplicate callbacks while locked. Persistent OID high-water state is updated only at the master through container service storage. Invalidations mark/delete the IV entry for a pool/container key.

Dependencies/integration: DAOS server IV framework, Argobots mutexes, container service `ds_cont_oid_fetch_add`, pool/container UUID keys, and `oid_iv_range`.

Risks: lock release is split across update and refresh for forwarded requests, so callback pairing is critical. `oid_iv_ent_fetch` asserts unreachable. Allocation batching uses `OID_BLOCK` and can over-reserve to reduce root traffic. Busy duplicate handling depends on `req_rank` and `req_ptr` identity.

Test signals: no direct test in this subset. Useful tests should cover local cached allocation, root fetch-add path, forwarded refresh, duplicate request handling, invalidation, and concurrent reservation contention.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/oid_iv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/container/rpc.c -->
# sources/object-store/daos/src/container/rpc.c

Purpose: DAOS container RPC serialization and protocol-format registration definitions.

Important APIs/types/functions: custom serializers `crt_proc_struct_rsvc_hint`, `crt_proc_daos_epoch_range_t`, `crt_proc_daos_obj_id_t`, wrappers for `cont_op` inputs/outputs, many `CRT_RPC_DEFINE` declarations for v8/v9 container operations, and exported `cont_proto_fmt_v8`/`cont_proto_fmt_v9`.

Control flow: CART serialization macros generate encode/decode routines for container RPC request/reply structs. The `X` macro populates protocol RPC format arrays from `CONT_PROTO_CLI_RPC_LIST(version)` and `CONT_PROTO_SRV_RPC_LIST`. `cli.c` selects and registers one of the exported protocol formats during `dc_cont_init`.

State/persistence: no persistent state. It defines wire schemas and static protocol format arrays for the container module.

Dependencies/integration: `daos/rpc.h`, `rpc.h` sequence macros, CART protocol registration, DAOS container module opcode base, and client/server RPC list macros.

Risks: protocol compatibility depends on keeping v8/v9 sequence macros and RPC list ordering consistent with server handlers. Serializer helper failures map to `-DER_HG`, so field additions must be reflected in sequence macros and helpers.

Test signals: no direct test. Compatibility tests should verify mixed-version client/server RPC registration, encode/decode of changed fields, and every operation in the protocol list.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/container/rpc.c -->
