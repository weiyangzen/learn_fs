<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/filesystem.go -->
# sources/cloud-native/cri-o/utils/filesystem.go

Purpose: filesystem utility functions for disk usage and directory validation.

Important APIs: `GetDiskUsageStats` walks a path without following symlinks and sums `FileInfo.Size()` plus one inode count per visited entry. `IsDirectory` follows symlinks with `os.Stat` and returns a `PathError` with `ENOTDIR` for existing non-directories, matching `os.Stat`-style errors.

State and integration: reads filesystem metadata only. Risks include expensive recursive walks on large trees, size values not matching block usage, no context/cancellation, and symlink-follow behavior differing between the two functions. Test signal is `filesystem_test.go`, which covers current directory, missing paths, directory success, file failure, and missing path failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/filesystem.go -->
