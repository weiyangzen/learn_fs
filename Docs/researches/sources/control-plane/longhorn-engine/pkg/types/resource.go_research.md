## sources/control-plane/longhorn-engine/pkg/types/resource.go

### Purpose
`resource.go` defines JSON-serializable resource DTOs exchanged by Longhorn engine controller, replica, and sync APIs.

### Important APIs, Types, And Functions
`ReplicaInfo` reports replica state, disk chain, revision counters, backing file, snapshot usage, unmap setting, and file timing/size data. `DiskInfo` describes one snapshot/head disk with parent, children, removal flag, user-created flag, creation time, size, and labels. `PrepareRemoveAction` encodes disk operations such as coalesce/remove/replace/prune. `VolumeInfo` reports engine volume metadata and expansion/snapshot limit state. `ControllerReplicaInfo` records address and mode. `SyncFileInfo` maps source and target filenames plus actual allocated size.

### Control Flow
There is no runtime control flow. These structs are populated by replica/controller services, serialized to JSON, and transformed into gRPC response structs or higher-level sync plans.

### State, Persistence, And Dependencies
The file has no imports and no persistence. The struct tags define the external JSON contract; fields represent state persisted elsewhere in replica metadata files or controller memory.

### Integration Points
`sync.go`, `rpc/server.go`, replica clients, controller clients, and CLI output use these DTOs. Disk-chain conversion code maps Longhorn disk filenames into `DiskInfo` snapshots, and rebuild sync maps controller-prepared file lists into `SyncFileInfo`.

### Risks
Changing JSON field names is an API compatibility risk. `VolumeInfo.SnapshotMaxSize` uses the tag `json:"SnapshotMaxSize"` with an uppercase key, which callers may already depend on. Several numeric fields are strings in JSON for historical compatibility.

### Test Signals
Useful checks include JSON marshal/unmarshal compatibility, disk-chain child/parent shape preservation, and rebuild file-list conversion retaining `ActualSize`.
