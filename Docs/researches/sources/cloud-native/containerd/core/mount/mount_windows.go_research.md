<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_windows.go -->
# sources/cloud-native/containerd/core/mount/mount_windows.go

Purpose: Windows layer mount implementation using HCSShim layer activation/preparation and bind filter links.

Important APIs/types/functions: `(*Mount).mount` handles `windows-layer`; helper methods parse parent paths from options and manage bindfilter links; constants include an alternate data stream name for recording source paths.

Control flow: validates mount type, splits source into home/layer ID, computes parent layer paths, activates and prepares the layer with cleanup defers, obtains the layer mount path, and either links base layer `Files` or uses bindfilter for mounted layers. Cleanup deactivates/unprepares on failure.

State and persistence: modifies Windows container layer state through hcsshim and creates filesystem links/bindfilter state at target. It may write/read source metadata through alternate streams for cleanup support.

Dependencies and integration points: selected on Windows; integrates `hcsshim`, `go-winio` bindfilter, Windows syscall package, and containerd logging. It is the platform implementation behind `Mount.Mount` for Windows snapshot/layer mounts.

Risks: highly dependent on Windows container layer invariants and hcsshim behavior. Failure cleanup must unwind activation/preparation in the correct order; base-layer handling differs from child-layer handling.

Test signals: no Windows tests in this subset; coverage is platform-specific elsewhere or by integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_windows.go -->
