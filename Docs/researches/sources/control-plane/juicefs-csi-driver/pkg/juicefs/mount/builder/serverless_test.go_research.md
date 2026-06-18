## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/serverless_test.go

### Purpose
`serverless_test.go` validates serverless cache-volume behavior, especially generic ephemeral cache support without hostPath output.

### Important APIs, Types, And Functions
`Test_serverless_getCacheDirVolumes_ephemeral` constructs a `ServerlessBuilder` with a `JfsSetting` containing one `CacheEphemeral` entry. It calls `genCacheDirVolumes()` and inspects returned volumes and mounts.

### Control Flow
The test scans returned `cacheVolumes` for `cachedir-ephemeral-0`, checks the `Ephemeral.VolumeClaimTemplate`, storage class, storage quantity, access modes, and mount path, then verifies no returned volume has a hostPath source.

### State, Persistence, And Dependencies
No state persists beyond local structs. The test depends on Kubernetes core APIs and resource quantity parsing.

### Integration Points
It protects the serverless builder contract that cache dirs must not require host filesystem access. This matters for app pod mutation and provider compatibility.

### Risks
The test covers cache generation only; it does not exercise `NewMountSidecar`, shared PVC volume discovery, lifecycle hooks, `JFS_NO_UMOUNT`, or overwrite hooks. It also does not test PVC, emptyDir, or inline CSI cache variants.

### Test Signals
Failures point to serverless cache regression, especially accidental hostPath emission or broken generic ephemeral PVC template fields.
