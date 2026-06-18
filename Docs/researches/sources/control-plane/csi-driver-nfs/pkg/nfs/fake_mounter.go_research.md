# sources/control-plane/csi-driver-nfs/pkg/nfs/fake_mounter.go

Purpose: provides a test-only fake mount implementation for node and controller tests that need mount operations without touching real NFS mounts.

Important APIs and types: `fakeMounter` embeds `mount.FakeMounter` and overrides `Mount`, `MountSensitive`, and `IsLikelyNotMountPoint`. `NewFakeMounter` returns a `*mount.SafeFormatAndMount` with the fake as its `Interface`.

Control flow: `Mount` returns deterministic errors when the source or target contains `error_mount`. `MountSensitive` does the same for `error_mount_sens`. `IsLikelyNotMountPoint` returns an error for `error_is_likely`, returns mounted (`false, nil`) for `false_is_likely`, and otherwise returns not mounted (`true, nil`).

State and persistence behavior: no persistent state is maintained beyond the embedded fake type. The behavior is driven by string sentinels in the requested source, target, or file path.

Dependencies and integration points: integrates with `NodeServer` tests through Kubernetes `k8s.io/mount-utils` interfaces. It allows `NodePublishVolume`, `NodeUnpublishVolume`, and controller internal mount flows to be tested through the same interface shape as production mount code.

Risks: because it does not record mount tables unless the embedded fake behavior is used through other paths, it can miss real mount lifecycle issues. Sentinel substring matching can accidentally trigger if test names include those tokens.

Test signals: paired with `fake_mounter_test.go`, it validates deterministic mount, sensitive mount, and mountpoint error paths used by higher-level tests.
