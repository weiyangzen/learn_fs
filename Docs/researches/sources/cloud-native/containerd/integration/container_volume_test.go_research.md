# sources/cloud-native/containerd/integration/container_volume_test.go

## Purpose

This cross-platform test verifies that host volume paths involving symlinks are resolved/mounted so the container reads the expected target file. It covers symlinked files, files inside symlinked directories, and symlinked files that point through symlinked directories.

## Important APIs, Types, And Functions

- `createRegularFile` creates the baseline target file.
- `fileInSymlinkedFolder`, `symlinkedFile`, and `symlinkedFileInSymlinkedFolder` construct host path variants.
- `TestContainerSymlinkVolumes` runs the table and validates container log output.

## Control Flow

Each subtest creates temporary log and volume directories, writes `regular/foo.txt`, creates one of the symlink path variants, creates a sandbox with a log directory, ensures BusyBox exists, and starts a container that runs `cat` on the mounted path. After the container exits, the test reads the CRI log and checks it contains the target content. On Windows, the mount path is normalized as a `C:` path.

## State And Persistence Behavior

State is limited to temporary host files/symlinks and the container log. The test checks volume resolution behavior but does not persist any containerd metadata beyond normal lifecycle state.

## Dependencies And Integration Points

It integrates CRI host-path mounts, symlink handling, platform path normalization, BusyBox `cat`, and CRI logging.

## Risks And Edge Cases

Host filesystem symlink permissions or Windows symlink support can affect setup. The test reads log output rather than directly inspecting mount metadata, so failures reflect effective data access but not the exact bind source used.

## Test Signals

Passing means CRI volume mount handling follows symlink paths sufficiently for containers to access the intended file content.
