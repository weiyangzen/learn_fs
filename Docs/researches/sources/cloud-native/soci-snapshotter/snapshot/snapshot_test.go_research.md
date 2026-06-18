# sources/cloud-native/soci-snapshotter/snapshot/snapshot_test.go

Purpose: this file verifies the snapshotter's remote-layer behavior and its compatibility with overlayfs snapshotter expectations.

Important APIs and helpers: `prepareWithTarget` simulates containerd prepare requests carrying `containerd.io/snapshot.ref`; it expects the snapshotter to internally commit and return an already-exists error. `bindFs` is a test `FileSystem` that bind-mounts a temporary directory into snapshot mountpoints and can mark mountpoints as broken. `dummyFs` makes normal overlay tests independent of remote filesystem behavior. `getBasePath` and `getParents` inspect snapshot metadata to build expected paths.

Control flow: remote tests require root because they perform real mount operations. `TestRemotePrepare` confirms a target-labeled prepare creates a committed remote snapshot with the right labels. `TestRemoteOverlay` checks active overlay mounts built on a remote parent include workdir, upperdir, and lowerdir pointing into the snapshot tree. `TestRemoteCommit` writes through an overlay mount and verifies commit/readback. `TestFailureDetection` builds chains of remote layers and optional overlay layers, toggles the fake filesystem's check failures, and validates `Prepare`/`Mounts` return unavailable errors for broken remote ancestors.

State and persistence behavior tested: tests create real metadata DBs and snapshot directories in `t.TempDir()`. Remote bind mounts are unmounted during cleanup. `bindFs.broken` tracks per-mountpoint failure state in memory.

Dependencies and integration points: uses containerd snapshot testsuite, namespaces, mount helpers, overlayutils, and errdefs. The tests exercise the public `snapshots.Snapshotter` interface rather than private methods where possible.

Risks and gaps: the root-required tests are likely skipped or unavailable in unprivileged CI. There are no tests in this file for parallel pull fallback, min-layer-size skip, `ErrNoIndex` deferral, restart restoration, invalid restart mount tolerance, or idmapped mount behavior. `TestOverlayView` mutates a lower path directly instead of mounting the active top layer, which checks mount composition but not full copy-up behavior.

Test signal quality: strong for basic remote and overlay compatibility paths; weaker for newer fallback modes and restart recovery.
