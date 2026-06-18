# sources/distributed-fs/ipfs-kubo/test/cli/harness/pbinspect.go

Purpose: low-level UnixFS and DAG-PB inspection helpers for tests that need to assert internal block structure rather than CLI text.

Important APIs/types/functions: `UnixFSDataType`, `UnixFSHAMTFanout`, `InspectPBNode`, and JSON structs `PBHash`, `PBLink`, `PBData`, `PBNode`.

Control flow: data-type and fanout helpers run `ipfs block get`, parse the dag-pb bytes with `merkledag.DecodeProtobuf`, then parse UnixFS data with `FSNodeFromBytes`. `InspectPBNode` runs `ipfs dag get --output-codec=dag-json`, unmarshals logical DAG-PB JSON, and returns a typed view of links/data.

State and persistence: read-only against the node blockstore. It uses buffers but does not mutate the repo.

Dependencies/integration: depends on Boxo merkledag/unixfs packages, protobuf UnixFS enums, JSON, and the harness runner.

Risks: `MustRun` panics before returned errors can be inspected. The JSON struct mirrors a specific dag-json logical shape, so codec output changes may break callers. Test signals are UnixFS type enum, HAMT fanout, link CIDs/names/sizes, and data bytes.
