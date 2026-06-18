<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/utils.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/utils.go

Purpose: holds small OS-specific helpers for snapshotter filesystem preparation.

Important APIs: `getSupportsDType(dir string)` delegates to `continuity/fs.SupportsDType`; `lchown(target string, st os.FileInfo)` extracts UID/GID from `syscall.Stat_t` and calls `os.Lchown`.

Control flow and state: stateless wrappers. `NewSnapshotter` uses `getSupportsDType` to reject backing filesystems without d_type support. `createSnapshotWithRecovery` uses `lchown` to propagate parent ownership to new snapshot directories.

Dependencies/integration: depends on Linux/Unix stat data and containerd continuity fs helpers.

Risks and test signals: `lchown` assumes `st.Sys()` is `*syscall.Stat_t`, so it is platform-specific. No direct tests in this subset; behavior is indirectly relevant to snapshot creation tests/integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/utils.go -->
