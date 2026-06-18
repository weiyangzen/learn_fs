<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/nodeserver_test.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/nodeserver_test.go

Purpose: This is the main unit/regression test suite for the SMB CSI node service paths. It validates `NodeStageVolume`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeUnstageVolume`, `NodeGetInfo`, `NodeGetCapabilities`, `NodeGetVolumeStats`, mount-point helpers, Kerberos cache helpers, and group-permission mount flag mutation.

Important APIs and fixtures: The file uses CSI request/response types from `github.com/container-storage-interface/spec/lib/go/csi`, gRPC status/codes, `testutil.TestError`, and the package fake mounter returned by `NewFakeMounter`. `matchFlakyWindowsError` allows Windows CSI proxy failures to be compared by stable substrings. Test cases build `VolumeCapability` variants for standard mounts, `VolumeMountGroup`, explicit `file_mode`/`dir_mode`, and access-mode-driven read-only behavior.

Control flow and coverage: `TestNodeStageVolume` table-drives validation errors, missing `source`, failed mkdir, in-progress lock rejection, fake mount failure, special-character passwords, metadata-substituted sources, `VolumeMountGroup`, and directory traversal rejection. `TestNodePublishVolume` covers missing fields, bind mount failures, idempotent already-mounted behavior, ephemeral publish dispatching through `NodeStageVolume`, read-only propagation from request flags, CSI access modes, and mount flags. The unpublish/unstage tests check argument validation and cleanup calls. Later tests isolate helper behavior for mount-point creation, statfs volume metrics, Kerberos option parsing, cache file naming, cache extraction, atomic symlink replacement, concurrent cache writes, idempotent bind mounts, and mode-bit widening.

State and persistence behavior: Tests create temporary directories and files under test work dirs or `/tmp`, mutate the driver's in-memory `volumeLocks`, and create Kerberos cache files/symlinks in temporary directories. The concurrent Kerberos test is a significant persistence signal because it asserts multiple volume-specific cache files can race on one `krb5cc_<uid>` symlink without `EEXIST` failures and with a valid final symlink.

Dependencies and integration points: The suite depends on OS behavior, especially Linux mount listing and symlink semantics, and conditionally skips or relaxes assertions for Windows. It verifies integration with `mount.SafeFormatAndMount`, `k8s.io/mount-utils`, CSI proxy semantics indirectly through platform-specific expected errors, and Kubernetes volume metrics via `volume.NewMetricsStatFS`.

Risks: Several assertions are platform-sensitive and encode exact error strings, which can drift across Go, Windows, CSI proxy, and mount-utils versions. Some tests use real filesystem paths and root-only mount behavior; `TestNodePublishVolumeIdempotentMount` only runs when root on non-Windows. Kerberos tests assume the process can `chown` cache files to `os.Getuid()`.

Test signals: This file is itself the highest-value node-server test signal. It includes regression coverage for directory traversal prevention, read-only bind propagation, nil mount capability handling, Kerberos atomic symlink races, and group RWX escalation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/nodeserver_test.go -->
