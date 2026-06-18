# sources/control-plane/ceph-csi/internal/cephfs/util/mountinfo.go

Purpose: persists enough node-stage mount information to restore CephFS mounts, especially ceph-fuse mounts, after process or node-plugin restarts. Records live under `/csi/mountinfo`.

Important APIs/types/functions: `NodeStageMountinfo` holds a CSI `VolumeCapability`, secrets, and mount options. `nodeStageMountinfoRecord` is the JSON-friendly wire format containing protojson for the capability. Public helpers are `WriteNodeStageMountinfo()`, `GetNodeStageMountinfo()`, and `RemoveNodeStageMountinfo()`. Internal helpers are `fmtNodeStageMountinfoFilename()`, `toNodeStageMountinfoRecord()`, and `toNodeStageMountinfo()`.

Control flow: writes marshal the CSI capability through `protojson`, embed it in a JSON record with secrets and mount options, then write `nodestage-<volID>.json` with mode `0600`. Reads reverse the process and return `(nil, nil)` for missing files. Removes treat missing files as success.

State and persistence: durable node-local state includes volume capability, mount options, and secrets. The file uses a fixed absolute directory (`/csi/mountinfo`) and does not create it; if the directory is missing, `WriteNodeStageMountinfo()` currently returns nil for `os.IsNotExist(err)`, which means failed persistence is silently ignored when the directory is absent. Secrets are protected by file mode but still exist at rest on the node.

Dependencies and integration points: depends on CSI protobufs, older `github.com/golang/protobuf/proto` bridging, `protojson`, JSON, and OS file APIs. NodeStage/restore logic in CephFS node paths consumes these records.

Risks: silent success on missing directory can hide restore-data loss. JSON corruption, protojson incompatibility, or permission problems surface on read/write. Volume IDs are placed in filenames; callers must ensure IDs are already safe and validated. Secret persistence increases node compromise impact.

Test signals: no tests in this work item. Useful coverage would include write/read/remove round-trips, missing directory behavior, malformed JSON/protojson, file permissions, and secret retention expectations.
