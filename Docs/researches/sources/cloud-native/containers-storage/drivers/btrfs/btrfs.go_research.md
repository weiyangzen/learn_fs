# sources/cloud-native/containers-storage/drivers/btrfs/btrfs.go

## Purpose
`btrfs.go` implements the Linux cgo Btrfs graphdriver. It registers `btrfs`, validates that the graph root is on Btrfs, manages layers as Btrfs subvolumes/snapshots, supports optional qgroup quota limits, and returns a `NaiveDiffDriver` wrapper for diff behavior.

## Important APIs, Types, And Functions
`btrfsOptions` tracks `minSpace` and per-layer `size`; `Driver` stores `home`, options, quota status, and a `sync.Once`. `Init`, `parseOptions`, `Create`, `CreateReadWrite`, `CreateFromTemplate`, `Remove`, `Get`, `Put`, `ReadWriteDiskUsage`, `Exists`, `ListLayers`, and `Cleanup` implement the graphdriver lifecycle. Low-level helpers wrap Btrfs ioctls: `subvolCreate`, `subvolSnapshot`, `subvolDelete`, `subvolLimitQgroup`, `qgroupStatus`, `subvolLookupQgroup`, and quota rescan/enabling methods.

## Control Flow
Initialization checks `GetFSMagic(home) == FsMagicBtrfs`, creates `subvolumes`, makes the graph root private, parses driver options, and enables quotas when requested. `Create` creates a new subvolume for base layers or snapshots the parent subvolume, then applies optional `size` storage options and SELinux relabeling. `Get` validates the subvolume and re-applies stored quota files when present. `Remove` deletes a quota sidecar, recursively destroys nested subvolumes, falls back to filesystem cleanup when quotas are disabled, and rescans quotas.

## State And Persistence
Layer data persists as Btrfs subvolumes under `subvolumes/<id>`. Per-layer quota values are stored in text files under `quotas/<id>`. The quota-enabled flag is cached after first status check, but persisted quota state lives in the filesystem qgroup tree. No runtime mounts are created per layer, so `Put` is a no-op.

## Dependencies And Integration Points
The file depends on cgo headers from btrfs-progs, Btrfs ioctl constants, `x/sys/unix`, graphdriver interfaces, `directory`, `fileutils`, `idtools`, `mount`, `parsers`, `system`, Docker units parsing, SELinux labels, and `NaiveLayerIDMapUpdater`.

## Risks
Btrfs behavior is kernel, filesystem, qgroup, and cgo-header dependent. Recursive subvolume deletion must correctly handle children disappearing during walks. Quota deletion logs errors but proceeds in some cases; quota rescan and qgroup lookup failures can affect cleanup. Unsupported mount options and invalid storage options fail early. `CreateFromTemplate` delegates to `Create(id, template, opts)`, so template semantics depend on snapshotting the template layer.

## Test Signals
`btrfs_test.go` runs shared graphdriver contract tests and validates nested subvolume removal. Version tests validate btrfs library version exposure. Full coverage requires Linux, cgo, btrfs headers, Btrfs backing filesystem, and sufficient privileges.
