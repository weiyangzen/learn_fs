<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_windows.go -->
# sources/cloud-native/containerd/integration/client/helpers_windows.go

## Purpose
Provides Windows-specific cleanup for containerd test roots containing WCOW snapshot layers, plus a temporary host-version skip predicate.

## APIs, Types, And Functions
The file defines `forceRemoveAll`, `cleanupWCOWLayers`, `cleanupWCOWLayer`, and `SkipTestOnHost`. It depends on `hcsshim`, `osversion`, and Windows syscall errors.

## Control Flow And State
`forceRemoveAll` detects the Windows snapshotter directory under a containerd root and calls `cleanupWCOWLayers` before `os.RemoveAll`. Layer directories and `rm-*` directories are collected, sorted descending, and each layer is unprepared, deactivated, and destroyed through HCS driver APIs. Some unprepare errors are tolerated because layers may already be unprepared or only activated.

## Persistence And Integration Points
This helper mutates Windows container layers under `io.containerd.snapshotter.v1.windows/snapshots`. It integrates test cleanup with hcsshim's layer lifecycle and skips selected tests on Windows Server 2025 via `osversion.Build() == osversion.LTSC2025`.

## Risks And Test Signals
Wrong deletion order or ignored HCS states can leave mounted layers that block directory removal. Overly broad path traversal could affect unrelated directories if callers pass the wrong root. Test signal comes from Windows integration cleanup reliability and host-specific skips.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/helpers_windows.go -->
