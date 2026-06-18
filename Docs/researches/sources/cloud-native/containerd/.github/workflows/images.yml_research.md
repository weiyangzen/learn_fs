# sources/cloud-native/containerd/.github/workflows/images.yml

## Purpose
This manual workflow mirrors an upstream test image into `ghcr.io/containerd` or a caller-provided target name.

## Important APIs, Types, And Functions
It accepts workflow inputs `upstream` and optional `image`, installs containerd dependencies, builds containerd with `GO_BUILDTAGS="no_btrfs"`, runs containerd, uses `ctr content fetch --all-platforms`, and pushes with `ctr images push` using `GITHUB_TOKEN`.

## Control Flow
The job checks out code, installs Go, sets GOPATH/PATH, installs `gperf` and seccomp, builds and installs containerd, starts `containerd` in the background, computes the mirror target, fetches all platforms from upstream, pushes to GHCR, and kills the daemon.

## State And Persistence
Persistent output is a GHCR package image. Runner state includes installed containerd binaries and a temporary daemon.

## Dependencies And Integration Points
It depends on GHCR package write permission, upstream registry availability, `ctr`, and containerd build/install scripts.

## Risks
The final `kill` is not guarded by `always()`, so failures before cleanup may leave a daemon running until runner teardown. Target naming is string-based and should be reviewed for unexpected upstream names.

## Test Signals
Manual run success and pullability of the mirrored GHCR image validate behavior.
