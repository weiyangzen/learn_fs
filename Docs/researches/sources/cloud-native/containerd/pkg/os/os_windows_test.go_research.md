<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os_windows_test.go -->
# sources/cloud-native/containerd/pkg/os/os_windows_test.go

## Purpose
Windows-only integration tests for pkg/os path resolution, especially resolving local drive paths, UNC paths, symlinks, VHD volumes, and mounted volumes into stable final paths usable by EvalSymlinks.

## Important APIs, Types, And Functions
getWindowsBuildNumber reads the registry for CurrentBuild; setupVHDVolume creates, attaches, formats, and discovers a VHD volume; mountVolume binds a volume path to a mount point; TestResolvePath drives resolvePath through local, UNC, symlink, and VHD cases.

## Control Flow
The test prepares C: volume identity, temp symlinks, two formatted VHDs, and a volume mount point, then checks resolvePath output and verifies EvalSymlinks of the resolved output remains equivalent case-insensitively.

## State And Persistence
Persists only temporary VHD and mount-point state for the test lifetime and registers cleanups to close handles, detach disks, remove mount points, and delete temp paths.

## Dependencies And Integration Points
Depends on Windows registry APIs, go-winio/vhd, hcsshim computestorage, osversion build gates, and internal Windows path helpers from pkg/os.

## Risks And Edge Cases
High privilege and Windows storage APIs make this environment-sensitive. Build-number handling must match HcsFormatWritableLayerVhd handle expectations before and after 19H1. Cleanup failures can leave attached VHDs or mount points.

## Test Signals
Direct test coverage is TestResolvePath on Windows; it validates local/UNC preservation, symlink expansion, VHD volume path behavior, and compatibility with filepath.EvalSymlinks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os_windows_test.go -->
