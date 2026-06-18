<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/sanity/fake_juicefs_provider.go -->
## sources/control-plane/juicefs-csi-driver/tests/sanity/fake_juicefs_provider.go

### Purpose
`fake_juicefs_provider.go` implements a minimal fake `juicefs.Interface` and fake filesystem object for CSI sanity tests without a real JuiceFS backend.

### Important APIs, Types, And Functions
`fakeJfsProvider` embeds `mount.FakeMounter`, stores fake filesystems and snapshot mappings, and implements provider methods such as `CreateSnapshot`, `DeleteSnapshot`, `RestoreSnapshot`, `CreateTarget`, `Settings`, `JfsCreateVol`, `JfsDeleteVol`, `JfsMount`, `JfsCleanupMountPoint`, `AuthFs`, `JfsUnmount`, `SetQuota`, `GetSubPath`, and `Status`. `fakeJfs` implements `CreateVol`, `GetBasePath`, `GetSetting`, and `BindTarget`.

### Control Flow
Snapshot creation records `snapshotID -> sourceVolumeID` and rejects the same snapshot ID for a different source. Restore checks snapshot existence. `CreateTarget` creates a directory if missing. `JfsMount` returns an existing fake filesystem named `fake` or creates one with base path `/jfs/fake`. `JfsUnmount` removes the target path if it exists. Several mount.Interface methods intentionally panic because the sanity path should not call them.

### State, Persistence, And Dependencies
Persistent test state is in-memory maps plus temporary directories created/removed under requested paths. Dependencies include `k8s.io/utils/mount`, project config, and JuiceFS interfaces. It does not contact Kubernetes or external storage.

### Integration Points
`sanity_test.go` passes this fake provider into `driver.NewFakeDriver`, allowing Kubernetes CSI sanity tests to exercise controller/node logic without a real JuiceFS mount.

### Risks
Panic stubs make unsupported call paths fail loudly, but they can obscure intended fake behavior if the driver starts using embedded `FakeMounter` methods. The fake returns empty/default settings and no-op quota/delete behavior, so it cannot catch many real backend errors. Snapshot state is not synchronized for parallel tests.

### Test Signals
Signals include idempotent create-volume behavior, snapshot create/delete/restore semantics, target directory creation/removal, status/auth no-ops, and no unexpected calls to panic-stubbed mount methods.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/sanity/fake_juicefs_provider.go -->
