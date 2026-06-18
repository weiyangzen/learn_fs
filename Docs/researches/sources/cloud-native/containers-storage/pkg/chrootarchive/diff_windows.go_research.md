<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_windows.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/diff_windows.go

Purpose: Windows `applyLayerHandler` implementation without chroot sandboxing.

Important APIs/types/functions: `applyLayerHandler`.

Control flow: cleans destination, prefixes it with `longpath.AddPrefix`, optionally decompresses, creates a temp extraction directory under `os.Getenv("temp")`, calls `archive.UnpackLayer(dest, layer, nil)`, removes temp dir, and returns size or wrapped error.

State/persistence: mutates destination and creates/removes temp directory.

Dependencies/integration: uses `archive.DecompressStream`, `archive.UnpackLayer`, and Windows long path handling.

Risks: the function ignores its `options` parameter and always passes nil to `UnpackLayer`, so caller-provided tar options are lost on Windows. No chroot isolation exists. Error formatting uses string interpolation instead of wrapping in one path.

Test signals: Windows coverage is limited; many layer/link tests skip Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_windows.go -->
