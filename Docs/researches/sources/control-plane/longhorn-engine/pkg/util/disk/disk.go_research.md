## sources/control-plane/longhorn-engine/pkg/util/disk/disk.go

### Purpose
`disk.go` provides small helpers for generating and parsing Longhorn snapshot, delta, temporary, checksum, metadata, expansion, and head disk names.

### Important APIs, Types, And Functions
Functions include `GenerateSnapshotDiskName`, `GenerateSnapshotDiskChecksumName`, `GenerateSnapshotDiskMetaName`, `GenerateDeltaFileName`, `GenerateSnapTempFileName`, `GetSnapshotNameFromTempFileName`, `GetSnapshotNameFromDiskName`, `GenerateExpansionSnapshotName`, `GenerateExpansionSnapshotLabels`, and `IsHeadDisk`.

### Control Flow
Generation functions format strings from constants. Parser functions validate required prefixes/suffixes before trimming them; invalid names return errors. `IsHeadDisk` checks the head prefix and suffix.

### State, Persistence, And Dependencies
The helpers do not persist state, but their return values are persistent on-disk filenames and labels. Dependencies are `fmt`, `strconv`, and `strings`.

### Integration Points
`sync.go`, `rpc/server.go`, backup restore, snapshot purge, and replica disk-chain code use these helpers to avoid open-coded filename manipulation.

### Risks
The parsers are intentionally strict; callers passing a temp name to `GetSnapshotNameFromDiskName` or a disk name without the standard prefix will fail. Expansion labels use an unexported key, so external code should not recreate it by hand.

### Test Signals
Tests should cover valid/invalid snapshot disk names, temp-name round trips, head detection, checksum/meta suffix generation, and expansion snapshot labels.
