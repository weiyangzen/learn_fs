<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time_unix.go -->
# sources/cloud-native/containerd/pkg/archive/time_unix.go

Purpose: Unix implementation of archive timestamp application.

Important APIs and functions: `chtimes(path string, atime, mtime time.Time) error` uses nanosecond timespecs and no-follow semantics where available.

Control flow and state: converts Go times into Unix syscall structures and updates timestamps on the target path as part of extraction.

Dependencies and integration: used by `tar.go` after file creation and again after all directory children are unpacked.

Risks and test signals: symlink and directory mtime behavior can differ by OS; delayed directory updates in `tar.go` are the main integration safeguard.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time_unix.go -->
