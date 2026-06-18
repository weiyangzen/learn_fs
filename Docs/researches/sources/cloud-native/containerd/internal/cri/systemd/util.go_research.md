# sources/cloud-native/containerd/internal/cri/systemd/util.go

## Purpose
Provides Linux-only detection of whether the host booted with systemd. The CRI plugin can use this to decide whether systemd-specific integration paths are available.

## Important APIs, Types, And Functions
`IsRunningSystemd` checks `/run/systemd/system` once and caches the result in package globals `runningSystemd` and `detectSystemd`.

## Control Flow
The first call runs `os.Lstat`; success plus `IsDir()` sets the cached boolean. Later calls return the cached value without touching the filesystem.

## State And Persistence
State is process-local and immutable after first detection. It does not monitor changes to `/run/systemd/system`.

## Dependencies And Integration Points
Uses `os` and `sync`. It mirrors the behavior of systemd's `sd_booted(3)` and CoreOS go-systemd utility logic.

## Risks
The once-only cache can be stale in unusual test or chroot scenarios. The file has a Linux build tag, so non-Linux callers need alternate build paths.

## Test Signals
No direct tests in this subset. Testability is limited by the hard-coded host path and `sync.Once` global cache.
