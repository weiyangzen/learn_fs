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
