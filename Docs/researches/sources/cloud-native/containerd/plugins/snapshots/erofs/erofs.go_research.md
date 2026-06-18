# sources/cloud-native/containerd/plugins/snapshots/erofs/erofs.go

## Purpose
`erofs.go` implements an EROFS plus overlayfs snapshotter, with optional fs-verity, immutable layer files, block-mode writable layers, idmapped mount support, merged fsmeta handling, and dm-verity mount policy.

## Important APIs, Types, And Functions
`SnapshotterConfig` controls overlay options, fsverity, immutable flag, default writable size, ID remapping, and dm-verity mode. Options include `WithOvlOptions`, `WithFsverity`, `WithImmutable`, `WithDmverityMode`, `WithDefaultSize`, and `WithRemapIDs`. The `snapshotter` implements `Prepare`, `View`, `Commit`, `Mounts`, `Remove`, `Stat`, `Update`, `Walk`, `Usage`, and `Close`. Important helpers include path builders, `writableSize`, `prepareDirectory`, `mountFsMeta`, `applyDmverityPolicy`, `createErofsMount`, `mounts`, `createSnapshot`, `commitBlock`, `getCleanupDirectories`, and `verifyFsverity`.

## Control Flow
Initialization validates dm-verity mode, checks compatibility when not in block mode, optionally checks fsverity support, opens metadata, and creates a snapshots directory. Prepare/View create a temp snapshot directory, create `fs` and optional `work`, write `.erofslayer` for active snapshots, create metadata, apply ownership remapping, rename into place, and build mounts. Mount construction returns direct EROFS mounts for committed layers, bind mounts for single no-parent directories, or formatted overlay mount chains across parent EROFS layers. Commit converts an upperdir or block writable layer to `layer.erofs` when needed, enables fsverity/immutable flags if configured, and commits metadata with disk usage. Remove clears immutable flags for committed layers, removes metadata, unmounts upper paths, and deletes orphan snapshot directories.

## State And Persistence
Snapshot metadata persists in `metadata.db`. Per-snapshot files live under `<root>/snapshots/<id>/`, including `fs`, `work`, `rwlayer.img`, `layer.erofs`, and optional `fsmeta.erofs` or `.dmverity` metadata. Active usage scans upper directories; committed usage is stored metadata.

## Dependencies And Integration Points
It integrates storage metadata, mount formatter conventions, EROFS conversion utilities, dm-verity metadata helpers, fsverity helpers, user namespace ID maps, continuity disk usage, and snapshot label contracts.

## Risks
Mount option templates such as `{{ mount 0 }}` depend on containerd mount handler support. dm-verity `on` mode rejects old layers without metadata. Block mode changes active writable semantics. Cleanup after metadata removal is best effort. `setImmutable` failures are warnings on commit but errors when clearing during remove except not implemented.

## Test Signals
No EROFS tests are in this requested subset, though related `erofs_linux_test.go` exists outside it. Required coverage should include dm-verity modes, fsverity, block mode, ID mapping, fsmeta merging, and cleanup behavior.
