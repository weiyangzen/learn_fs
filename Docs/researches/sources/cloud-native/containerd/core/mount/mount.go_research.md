<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount.go -->
# sources/cloud-native/containerd/core/mount/mount.go

Purpose: defines the core `Mount` data structure and platform-neutral helpers for mounting arrays, unmounting arrays, canonical paths, read-only conversion, and protobuf conversion.

Important APIs/types/functions: `Mount`, `HasBindMounts`, `All`, `UnmountMounts`, `CanonicalizePath`, `(*Mount).ReadOnly`, `(*Mount).Mount`, `readonlyMounts`, `readonlyOverlay`, `isSkippedReadonlyOption`, `ToProto`, and `FromProto`.

Control flow: `All` mounts entries in order. `UnmountMounts` unmounts in reverse order using `fs.RootPath` for subtargets and returns the last mount error only when the top-level unmount fails. `Mount` resolves target under a root with `fs.RootPath` and delegates to platform-specific `m.mount`. Read-only conversion strips `rw`/duplicate `ro` for normal mounts and rewrites overlay mounts by removing `workdir`, `upperdir`, uid/gid idmap options, and prepending the old upperdir to lowerdir.

State and persistence: no persistent state. Helpers modify slices in place for read-only conversion, while proto conversion allocates new slices.

Dependencies and integration points: `Mount` is the common mount descriptor across snapshots, runtimes, mount manager, RPC proxy, and API protobufs. Uses continuity `fs.RootPath` to avoid unsafe target joins.

Risks: `readonlyMounts` mutates the input slice and nested options slices, so callers must copy if they need originals. `readonlyOverlay` only updates an existing `lowerdir=` option if one exists. `FromProto` assumes non-nil protobuf mount entries.

Test signals: `mount_test.go` validates overlay read-only rewriting, normal mount `ro` normalization, and volatile option copy behavior in adjacent temp helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount.go -->
