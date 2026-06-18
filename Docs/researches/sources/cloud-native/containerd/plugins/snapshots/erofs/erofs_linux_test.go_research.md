<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux_test.go -->
# sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux_test.go

## Purpose
Linux-only integration and unit tests for the EROFS snapshotter, its writable sizing, fsverity, dm-verity, tar-index differ integration, and fsmeta mount construction. The file is the main behavioral safety net for EROFS-specific storage paths.

## Important APIs, Types, And Functions
Key helpers are `newSnapshotter`, `testMount`, `createTestTarContent`, `createDmverityMetadata`, and `createTestLayerBlob`. Test entry points include `TestErofs`, `TestErofsWithQuota`, `TestWritableSize`, `TestErofsFsverity`, `TestErofsDifferWithTarIndexMode`, `TestCreateErofsMount`, `TestDmverityEndToEnd`, `TestDmverityModeValidation`, `TestApplyDmverityPolicy`, and `TestMountFsMeta`.

## Control Flow
The generic snapshotter suite is run against EROFS only when root, `mkfs.erofs`, and kernel EROFS support are available. The tar-index and dm-verity tests build tar content, write it into a local content store, apply it with the EROFS differ, commit the snapshotter layer, then mount a view and verify files. dm-verity end-to-end routes view mounts through the mount manager and EROFS mount handler because the snapshotter only emits metadata-bearing mount options.

## State And Persistence
Tests create temporary snapshot roots, content stores, bbolt mount-manager DBs, snapshot metadata stores, layer blobs, `.dmverity` metadata files, and fsmeta files. Cleanup is handled with `t.Cleanup`, deferred `Close`, and explicit `Remove` calls in end-to-end paths.

## Dependencies And Integration Points
Depends on containerd content, mount, mount manager, snapshots storage/testsuite, local content store, EROFS differ, EROFS mount handler, `dmverity`, `erofsutils`, `fsverity`, tartest, namespaces, bbolt, and root/kernel/external-tool availability.

## Risks And Edge Cases
Most tests are environment-sensitive and skip when kernel support, mkfs features, fsverity, dm-verity, or root privileges are absent. The dm-verity policy tests protect the strict `"on"` mode from silently accepting old layers without metadata. `TestMountFsMeta` verifies that merged fsmeta device ordering follows reverse parent order, which is easy to regress.

## Test Signals
This file itself signals EROFS correctness: generic snapshotter behavior, configured/default writable size labels, fsverity immutability, differ-created layer existence, dm-verity activation through the mount manager, mode validation, and fsmeta mount options.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux_test.go -->
