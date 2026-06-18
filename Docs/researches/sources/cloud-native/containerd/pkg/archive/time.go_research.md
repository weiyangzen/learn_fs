<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time.go -->
# sources/cloud-native/containerd/pkg/archive/time.go

Purpose: common time helpers for archive extraction timestamp restoration.

Important APIs and functions: `boundTime`, `latestTime`, and platform hook `chtimes`.

Control flow and state: `latestTime` chooses the newer of two `time.Time` values for access-time restoration; `boundTime` likely clamps out-of-range times for syscall compatibility before `chtimes` applies them.

Dependencies and integration: called from `createTarFile` and delayed directory mtime restoration in `tar.go`. Platform files implement the actual timestamp syscall.

Risks and test signals: timestamp bounds are important for old dates, zero times, and platform-specific syscall ranges. Source-date behavior is tested in `tar_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time.go -->
