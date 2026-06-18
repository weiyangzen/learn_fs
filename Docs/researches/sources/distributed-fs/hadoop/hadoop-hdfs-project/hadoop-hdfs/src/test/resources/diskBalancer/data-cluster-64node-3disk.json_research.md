# Research: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/diskBalancer/data-cluster-64node-3disk.json

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007566`: lines 1-6709, `Docs/researches/chunks/subset-b-007566_research.md`
- `subset-b-007567`: lines 6710-9484, `Docs/researches/chunks/subset-b-007567_research.md`

## Chunk Research

### subset-b-007566: lines 1-6709

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/diskBalancer/data-cluster-64node-3disk.json lines 1-6709

## Scope

This chunk covers the beginning of a Hadoop HDFS DiskBalancer JSON cluster fixture. The full file is a 9,483-line JSON document; this chunk includes the top-level cluster lists, 45 complete `nodes` entries, and the start of the 46th node through its `DISK` volume set. The chunk boundary falls inside the 46th node, so later chunks are required to finish that node, close the `nodes` array, and validate whole-file JSON structure.

## Purpose

The file is test data for DiskBalancer command and datamodel tests. It represents a synthetic 64-node cluster whose DataNodes each have multiple volumes grouped by storage type. `TestDiskBalancerCommand#setUp` loads `/diskBalancer/data-cluster-64node-3disk.json` as `clusterJson`, and `testReadClusterFromJson` asserts that `DiskBalancerCluster.readClusterInfo()` returns 64 nodes. Other command tests use the same fixture to exercise planning and node-list selection against stable DataNode UUIDs, including `a87654a9-54c7-4693-8dd9-c9c7021dc340`.

Within this chunk, the data supplies realistic imbalance inputs: each node has a precomputed `nodeDataDensity`, storage-type-specific volume sets, per-volume capacities and usage values, and per-volume `volumeDataDensity` deltas. The values are not executable logic, but they are the serialized API contract consumed by DiskBalancer's Jackson-backed datamodel.

## Data Schema And Important Types

Top-level object:

- `exclusionList`: empty array in this chunk. Jackson maps it to `DiskBalancerCluster.exclusionList`.
- `inclusionList`: empty array in this chunk. Jackson maps it to `DiskBalancerCluster.inclusionList`.
- `nodes`: array of DataNode objects. The full file has 64 nodes; this chunk contains 45 complete node UUID records plus a partial next node.

Node object shape maps to `DiskBalancerDataNode`:

- `nodeDataDensity`: numeric imbalance score used by `DiskBalancerDataNode.compareTo` and by planner/report behavior.
- `volumeSets`: map keyed by storage type string. This chunk consistently uses `DISK`, `RAM_DISK`, and `SSD`.
- `dataNodeUUID`: stable node identifier. In this fixture, IP and DNS fields are usually `null`, so UUID is the main lookup key used by `DiskBalancerCluster.readClusterInfo()`.
- `dataNodeIP`, `dataNodeName`: `null` in the visible nodes, meaning the cluster lookup maps for IP and hostname are intentionally sparse.
- `dataNodePort`: `0` in the visible nodes, because the fixture is not modeling live IPC endpoints.
- `volumeCount`: `9` for every complete node in this chunk.

Volume set shape maps to `DiskBalancerVolumeSet`:

- `volumes`: array of `DiskBalancerVolume` objects.
- `storageType`: repeats the map key and must match each contained volume's `storageType`.
- `setID`: stable UUID-like identifier for the serialized set.
- `transient`: `true` for `RAM_DISK`, `false` for `DISK` and `SSD`. `DiskBalancerVolumeSet.addVolume()` enforces that volume and set transient flags match when built programmatically; this fixture encodes that invariant for Jackson reads.

Volume shape maps to `DiskBalancerVolume`:

- `path`: synthetic `/tmp/disk/...` path.
- `capacity`, `used`, `reserved`: byte counts used by density calculations and planning.
- `storageType`: one of `DISK`, `RAM_DISK`, `SSD`.
- `uuid`: unique volume identifier used by volume equality and hash code.
- `failed`, `skip`, `readOnly`: all `false` in this chunk. This keeps all visible volumes eligible for normal balancing calculations.
- `volumeDataDensity`: precomputed density delta. Negative values indicate volumes above the ideal used ratio; positive values indicate volumes below it.
- `transient`: matches the storage type group, with `RAM_DISK` true and persistent storage false.

## Control Flow And Integration Points

The fixture enters DiskBalancer through `JsonNodeConnector`. `ConnectorFactory.getCluster(clusterJson, conf)` builds a connector for the resource URL. `JsonNodeConnector.getNodes()` reads the file path with a Jackson `ObjectReader` for `DiskBalancerCluster`, then returns `cluster.getNodes()`.

`DiskBalancerCluster.readClusterInfo()` copies the connector result into the cluster, then builds lookup maps by IP, hostname, and UUID. Because this fixture's visible nodes have null IP and hostname fields, UUID lookup is the meaningful integration path. Command tests use that behavior when selecting a fixed UUID for `-plan` and when `ReportCommand.getNodes()` resolves comma-separated UUIDs.

Planning uses this deserialized state through `DiskBalancerCluster.computePlan()`, which creates a planner per selected node. The planner consumes each `DiskBalancerDataNode`'s `volumeSets`, and each `DiskBalancerVolumeSet` exposes its volumes and density state. The JSON therefore acts as a persisted planning snapshot rather than a live cluster query.

This chunk also demonstrates the fixture's repeated pattern: every complete node has three storage-type sets with three volumes each. That gives nine volumes per DataNode and lets tests cover mixed storage-type balancing while avoiding failed, skipped, read-only, or negative effective-capacity cases in this fixture.

## State And Persistence Behavior

The source file itself is static test resource state. It is persisted under `src/test/resources`, loaded from the test classpath, and not mutated by tests. Runtime code may serialize similar structures via `DiskBalancerCluster.toJson()` or `createSnapshot()`, but this fixture is consumed read-only.

Jackson deserialization preserves the serialized density fields in the JSON. Programmatic `addVolume()` paths can recompute `volumeDataDensity` and `nodeDataDensity`, but simple fixture loading does not require the test to reconstruct the values from raw capacity and used bytes. That makes the fixture sensitive to field names and numeric representation: changing names such as `nodeDataDensity`, `volumeSets`, `volumeDataDensity`, or `transient` would break the datamodel mapping or alter planner inputs.

Chunk-local counts and invariants:

- Complete `dataNodeUUID` entries through line 6709: 45.
- `nodeDataDensity` entries through line 6709: 46, because the next node begins at line 6669.
- Complete `volumeCount` entries through line 6709: 45.
- Whole-file parse check: 64 nodes and 576 volumes.
- No `failed:true`, `skip:true`, or `readOnly:true` values are present in the whole fixture or in this chunk.

## Dependencies

Runtime dependencies implied by this resource:

- Jackson databind for mapping JSON fields into `DiskBalancerCluster`, `DiskBalancerDataNode`, `DiskBalancerVolumeSet`, and `DiskBalancerVolume`.
- Hadoop HDFS DiskBalancer connector and command stack: `JsonNodeConnector`, `ConnectorFactory`, `DiskBalancerCluster`, planner implementations, and command classes such as `ReportCommand`.
- Test classpath resource loading via JUnit tests under `src/test/java/org/apache/hadoop/hdfs/server/diskbalancer`.

The JSON values use Hadoop storage type strings. Any change in accepted storage type names or transient-storage expectations would affect whether this fixture remains representative.

## Risks And Edge Cases

The chunk boundary is mid-object, after the third `DISK` volume of the 46th node and before that node's `RAM_DISK`, `SSD`, UUID, and `volumeCount` fields. This chunk cannot independently validate balanced braces or the final node count; merge/reconciliation must combine later chunks before treating the per-file report as complete.

The fixture relies on precomputed density fields. If production code changes to recompute densities on read, this fixture's current `nodeDataDensity` and `volumeDataDensity` values would become less authoritative and tests might need to assert recomputed values instead.

All visible operational flags are false. This is useful for happy-path planning, but it does not test failed-volume, skipped-volume, read-only-volume, or misconfigured reserved-capacity behavior. Those scenarios must be covered by other fixtures or generated test clusters.

The use of null IP/name and port `0` makes the fixture good for UUID-oriented command paths but weak for host/IP resolution behavior. Tests depending on hostnames should not infer coverage from this fixture.

Because this is large static JSON, accidental edits can be hard to review manually. Structural validation with `jq`, node-count checks, and targeted UUID assertions are important guardrails.

## Test Signals

Relevant existing signals tied to this fixture include:

- `TestDiskBalancerCommand.testReadClusterFromJson` expects `DiskBalancerCluster.getNodes().size()` to be `64` after loading this JSON.
- `TestDiskBalancerCommand.testPlanJsonNode` selects UUID `a87654a9-54c7-4693-8dd9-c9c7021dc340`, which appears in this chunk, and runs `hdfs diskbalancer -out <path> -plan <uuid>`.
- `TestDiskBalancerCommand.testGetNodeList` loads the fixture, takes the first five UUIDs from the deserialized node list, and expects `ReportCommand.getNodes()` to resolve all five.

Useful validation commands for this fixture are `jq '.nodes | length'` and a volume-count scan confirming 64 nodes x 9 volumes = 576 volumes. Chunk-specific validation should additionally note that line 6709 is not a safe JSON boundary.

### subset-b-007567: lines 6710-9484

# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/diskBalancer/data-cluster-64node-3disk.json lines 6710-9484

## Chunk Scope

This chunk is the final segment of the Hadoop HDFS DiskBalancer JSON fixture `data-cluster-64node-3disk.json`. The assigned span starts in the closing fields of the `DISK` volume set for DataNode index 45 and then covers the remainder of DataNodes 45 through 63, followed by the cluster-level tail fields:

- `nodes[45]` remainder, including `RAM_DISK`, `SSD`, and node metadata for UUID `c3c0ce3d-cd92-4d2e-9ffe-af0cf8df38aa`.
- Complete node objects for indices 46 through 63.
- Final cluster fields `outPutPath:null` and `threshold:0.0`.

The full fixture contains 64 nodes and 576 volumes. In this chunk, the complete node range `nodes[45:]` contains 19 nodes and 171 volumes. Every complete node in this range has three `volumeSets` keyed by `DISK`, `RAM_DISK`, and `SSD`, with three volumes in each set and `volumeCount:9`.

## Purpose

The file is a persisted synthetic DiskBalancer cluster model used by tests, not executable code. It exercises Jackson deserialization of a large HDFS DiskBalancer cluster snapshot and gives command/planner tests a stable, non-live cluster topology. The structure maps onto the DiskBalancer datamodel:

- Cluster object -> `DiskBalancerCluster`
- Node object -> `DiskBalancerDataNode`
- Storage-type group -> `DiskBalancerVolumeSet`
- Volume object -> `DiskBalancerVolume`

The fixture is referenced by `TestDiskBalancerCommand`, whose setup resolves `/diskBalancer/data-cluster-64node-3disk.json` as a classpath resource. DiskBalancer command code can then read the fixture through `JsonNodeConnector`, which maps the JSON into `DiskBalancerCluster` and returns its nodes.

## Important Data Shape And APIs

The chunk preserves the public JSON property contract consumed by Jackson:

- Cluster fields: `exclusionList`, `inclusionList`, `nodes`, `outPutPath`, `threshold`.
- Node fields: `nodeDataDensity`, `volumeSets`, `dataNodeUUID`, `dataNodeIP`, `dataNodePort`, `dataNodeName`, `volumeCount`.
- Volume set fields: `volumes`, `storageType`, `setID`, `transient`.
- Volume fields: `path`, `capacity`, `storageType`, `used`, `reserved`, `uuid`, `failed`, `volumeDataDensity`, `skip`, `readOnly`, `transient`.

Relevant reader and model APIs:

- `JsonNodeConnector.getNodes()` reads the JSON file with an `ObjectReader` for `DiskBalancerCluster`, logs the node count, and returns `cluster.getNodes()`.
- `DiskBalancerCluster.parseJson(String)` and `DiskBalancerCluster.toJson()` provide the equivalent string round-trip path.
- `DiskBalancerCluster.readClusterInfo()` uses a `ClusterConnector`, stores the returned nodes, and builds lookup maps by IP, hostname, and UUID. In this fixture chunk, `dataNodeIP` and `dataNodeName` are `null`, so UUID lookup is the meaningful node index.
- `DiskBalancerCluster.computePlan(double)` builds one planner per selected node and delegates to `PlannerFactory.getPlanner(...).plan(node)`.
- `DiskBalancerDataNode.computeNodeDensity()` recomputes `nodeDataDensity` as the sum of absolute `volumeDataDensity` values across all volumes and updates `volumeCount`.
- `DiskBalancerVolumeSet.computeVolumeDataDensity()` recomputes per-volume density from effective capacity (`capacity - reserved`) and `used`, ignoring failed or skipped volumes.
- `DiskBalancerVolume.computeEffectiveCapacity()` and `setUsed(long)` are important validation behaviors behind this fixture; `used` greater than `capacity` would be clamped during setter use, and `reserved` greater than `capacity` causes a volume to be skipped during density computation.

## Control Flow Represented By The Fixture

The normal test/control path is:

1. A test resolves the classpath resource URL for `data-cluster-64node-3disk.json`.
2. A `JsonNodeConnector` opens the file path behind that URL.
3. Jackson deserializes the top-level object into `DiskBalancerCluster`.
4. The connector returns `cluster.getNodes()` to `DiskBalancerCluster.readClusterInfo()`.
5. `readClusterInfo()` builds node lookup maps. This fixture only supports UUID lookup because IP/name fields are null.
6. Commands such as `PlanCommand` or report logic choose nodes to process, call `setNodesToProcess(...)`, and invoke `computePlan(threshold)`.
7. The planner evaluates each node's three storage-type sets independently, using volume densities, capacity, reserved space, `skip`, `failed`, `readOnly`, and `transient` state as part of eligibility and move planning.

Within this chunk, the data maintains a uniform topology for each complete node: `DISK`, `RAM_DISK`, and `SSD` sets each contain exactly three volumes. The `RAM_DISK` set and its volumes consistently use `transient:true`; `DISK` and `SSD` sets and volumes use `transient:false`.

## State And Persistence Behavior

This JSON is persisted test state. It does not mutate itself, but it is loaded into mutable Java objects:

- `DiskBalancerCluster.nodes` becomes the in-memory node list.
- `DiskBalancerCluster.threshold` maps from the top-level `threshold` field; here it is `0.0`, the most aggressive allowed value according to `DiskBalancerCluster.setThreshold(float)` which accepts `0.0` through `100.0`.
- The top-level output field appears in JSON as `outPutPath:null`, while `DiskBalancerCluster` exposes `getOutput()`/`setOutput(String)` for `outputpath`. This fixture tail therefore documents the serialized property spelling emitted or accepted by the code path in this branch.
- `inclusionList` and `exclusionList` are empty at the file head, so the loaded cluster means "all nodes unless later command-line filters replace the node set."
- The fixture has no runtime persistence writes. If command tests request snapshots, `DiskBalancerCluster.createSnapshot(...)` serializes the in-memory cluster to the configured output directory, not back to this resource.

State invariants visible in the assigned span:

- Node indices 45 through 63 all have `volumeCount:9`.
- The chunk's complete node range has 57 `DISK`, 57 `RAM_DISK`, and 57 `SSD` volumes.
- There are no `failed:true`, `skip:true`, or `readOnly:true` volumes in this chunk.
- The chunk contains capacities from `100000000000` through `9000000000000`.
- `volumeDataDensity` values in `nodes[45:]` range roughly from `-0.93388224` to `0.73030096`, giving tests both overloaded and underloaded volume examples.

## Dependencies And Integration Points

The fixture depends on Jackson property binding rather than a hand-written parser. Field names must continue matching JavaBean accessors or annotations in:

- `org.apache.hadoop.hdfs.server.diskbalancer.datamodel.DiskBalancerCluster`
- `org.apache.hadoop.hdfs.server.diskbalancer.datamodel.DiskBalancerDataNode`
- `org.apache.hadoop.hdfs.server.diskbalancer.datamodel.DiskBalancerVolumeSet`
- `org.apache.hadoop.hdfs.server.diskbalancer.datamodel.DiskBalancerVolume`
- `org.apache.hadoop.hdfs.server.diskbalancer.connectors.JsonNodeConnector`

The storage type strings integrate with HDFS storage categories. The fixture uses `DISK`, `RAM_DISK`, and `SSD` only. Any change to storage type spelling, transient semantics, or set grouping would affect planning behavior because `DiskBalancerDataNode.addVolume(...)` groups volumes by `volume.getStorageType()` and enforces that a set's transient flag matches each member volume.

The fixture also integrates with DiskBalancer command tests. `TestDiskBalancerCommand` initializes a MiniDFSCluster but uses this separate 64-node JSON resource as command input, so the file provides scale and deterministic topology without requiring 64 live DataNodes.

## Risks And Edge Cases

- The assigned chunk begins mid-object at line 6710. A chunk merge lane must combine this with earlier chunks before presenting whole-file JSON structure; by itself, the first two lines are the tail of a volume object.
- The file ends at line 9484 while `wc -l` reports 9483 newline-terminated lines, so line 9484 is the final `}` without a trailing newline. Consumers are fine with this, but chunk tooling should avoid assuming every displayed line has a terminating newline.
- The serialized top-level property is `outPutPath`, not the Java field spelling `outputpath` or accessor name `output`. Renaming this fixture key could break compatibility with existing serialized snapshots or command expectations.
- Because all volumes in this chunk have `failed:false`, `skip:false`, and `readOnly:false`, this segment does not exercise failure, skip, or read-only planning branches. Tests that need those branches must use other fixtures or construct nodes in Java.
- The fixture includes null `dataNodeIP` and `dataNodeName`. Code paths selecting nodes by IP or hostname cannot use these node entries unless tests populate those fields elsewhere.
- Density values are stored rather than recomputed during JSON read. If any capacity, reserved, or used number changes without updating `volumeDataDensity` and `nodeDataDensity`, planner ordering and report output can become inconsistent with `computeVolumeDataDensity()` semantics.
- Several volumes are close to full or have high reserved fractions. This is useful for planning pressure but raises a fixture maintenance risk: `reserved > capacity` or `used > capacity` would trigger skip/clamp logic and alter expected planner behavior.

## Test Signals

Positive signals from this chunk:

- The cluster tail is syntactically valid JSON and closes the `nodes` array and top-level object.
- It preserves the 64-node fixture contract: the full file has 64 nodes, the sum of `volumeCount` is 576, and every node uses the same `DISK,RAM_DISK,SSD` set keys.
- Complete nodes in this chunk maintain 3 volumes per storage type and consistent `transient` flags.
- `threshold:0.0` at the tail explicitly tests the datamodel's acceptance of zero-percent threshold, distinct from the HDFS balancer CLI threshold rules.
- Heterogeneous capacity and density values provide realistic planner input rather than a trivial balanced fixture.

Coverage gaps:

- This chunk does not test parsing of non-null node IP/name/port values beyond `dataNodePort:0`.
- It does not cover excluded or included node filtering because the cluster lists are empty.
- It does not cover skipped, failed, read-only, or misconfigured volumes.
- It is a resource consumed by tests; correctness depends on tests such as `TestDiskBalancerCommand` continuing to load it and on datamodel JSON compatibility, not on local assertions embedded in the file itself.
