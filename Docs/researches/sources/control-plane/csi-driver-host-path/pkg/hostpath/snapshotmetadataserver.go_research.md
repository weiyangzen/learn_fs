## sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadataserver.go

Purpose: implements CSI SnapshotMetadata streaming APIs for the hostpath driver. `GetMetadataAllocated` returns allocated blocks for one ready block-mode snapshot; `GetMetadataDelta` returns changed blocks between two ready snapshots of the same source volume.

Control flow validates IDs, fetches snapshots and volume records from `hp.state`, enforces `ReadyToUse` and `state.BlockAccess`, defaults `MaxResults` to 256, initializes a file block reader with snapshot paths, seeks to `StartingOffset`, then streams response pages until EOF. Cancellation and deadlines are treated as clean early exits; EOF sends any final partial block list; other reader errors become `Internal`.

State is read-only driver state plus snapshot files under `hp.getSnapshotPath`. Persistence is delegated to the state package and file snapshots. Dependencies include CSI generated interfaces, gRPC status codes, klog, and hostpath state constants. Risks include returning raw `GetVolumeByID` errors without normalizing codes, no explicit validation of negative `MaxResults`, suppressed cancellation as success, and block metadata correctness depending on the file reader. Test signal is mostly through `snapshotmetadata_test.go`, which covers lower-level scanning rather than server argument/status paths.
