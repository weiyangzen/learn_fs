# sources/cloud-native/moby/integration/system/disk_usage_test.go

## Purpose
Validates daemon disk-usage API accounting for images, containers, volumes, and build cache across an empty daemon, after loading busybox, and after running a container. It also verifies option filtering for every supported resource-type combination.

## Important APIs, Types, And Functions
- `TestDiskUsage` starts an isolated daemon, runs staged state transitions, calls `apiClient.DiskUsage`, and compares `client.DiskUsageResult` structures.
- `adjustedExpectedUsage` tolerates a one-block drift for rootless snapshotter environments.
- Comparisons ignore container `Status` and equate `netip` comparable values.

## Control Flow
The test skips Windows, runs in parallel, starts a daemon with iptables disabled, then executes three sequential steps: empty daemon, after `LoadBusybox`, and after `container.Run`. After each step it runs subtests for container-only, image-only, volume-only, build-cache-only, and mixed option combinations to ensure omitted types are zero.

## State And Persistence
State is accumulated in the test daemon: initially empty storage, a loaded busybox image, then a running container. `stepDU` carries the expected snapshot from one stage into filter assertions. Daemon cleanup removes storage after the test.

## Dependencies And Integration Points
Uses daemon helpers, image loading, container helpers, disk-usage client APIs, and Moby API result types. It integrates daemon storage accounting, image/container metadata, and API response filtering.

## Risks And Edge Cases
Disk usage can vary by snapshotter/rootless filesystem block behavior. The test assumes no build cache or volumes are created by the staged operations. It intentionally avoids parallel subtests for disk usage options due to an outstanding TODO.

## Test Signals
Signals include zeroed empty daemon usage, one loaded busybox image with positive size and no active containers, one active container linked to the image, `ImageManifestDescriptor` absent from container disk-usage summaries, and exact resource-type filtering.
