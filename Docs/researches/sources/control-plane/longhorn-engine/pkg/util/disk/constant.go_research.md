## sources/control-plane/longhorn-engine/pkg/util/disk/constant.go

### Purpose
`constant.go` defines the canonical disk filename patterns, suffixes, labels, and sector sizes used by Longhorn engine snapshot/head/backing-image utilities.

### Important APIs, Types, And Functions
Constants include `VolumeHeadDiskPrefix`, `VolumeHeadDiskSuffix`, formatted `VolumeHeadDiskName`, `SnapshotDiskPrefix`, `SnapshotDiskSuffix`, formatted `SnapshotDiskName`, delta disk naming, metadata and checksum suffixes, temporary snapshot suffix, expansion snapshot name infix, replica expansion label key, and sector sizes for volumes, replicas, and backing images.

### Control Flow
There is no control flow. Other helpers format and parse names using these constants.

### State, Persistence, And Dependencies
The constants define on-disk persistent filenames such as `volume-snap-<name>.img`, `volume-delta-<name>.img`, `.meta`, and `.checksum`. The file has no imports.

### Integration Points
Disk utility functions, sync-agent restore/purge/clone code, replica metadata, backup code, and controller snapshot flows all rely on these naming contracts.

### Risks
Any naming change can make existing replicas unreadable or make parsers reject valid disk files. Sector-size constants affect low-level volume geometry assumptions and must match backend/front-end expectations.

### Test Signals
Unit tests should assert generated names, parser compatibility, and sector-size usage in backend initialization paths.
