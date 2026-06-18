<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/goreleaser.sh -->
# sources/cloud-native/nydus/goreleaser.sh

## Purpose

This script generates a `.goreleaser.yml` for packaging static Nydus binaries for the host Go OS/architecture.

## Important APIs, Types, and Functions

It reads `GOOS` and `GOARCH`, defaults `GOARCH` from `go env`, and writes a GoReleaser version 2 configuration. Builds include `nydusify`, `nydus-overlayfs`, `nydus-image`, `nydusctl`, and `nydusd`, all using `contrib/goreleaser/main.go`, `CGO_ENABLED=0`, and post-build copying from `nydus-static`. It configures zip archives, checksums, snapshot versions, changelog filters, and deb/rpm nfpm packaging.

## Control Flow

The script is linear: detect environment, emit a heredoc to `.goreleaser.yml`, and exit. GoReleaser later executes hooks and package creation.

## State and Persistence Behavior

It overwrites `.goreleaser.yml` in the current directory. The generated release config creates `dist` artifacts and packages when GoReleaser runs.

## Dependencies and Integration Points

It depends on `go env`, GoReleaser, nfpm support, and a preexisting `nydus-static` directory containing binaries/configs. It is part of release automation rather than runtime code.

## Risks and Test Signals

The generated builds all point to the same main package and rely on binary names to select outputs, so release behavior depends on `contrib/goreleaser/main.go`. Host-only GOOS/GOARCH limits cross-platform output. There is no direct test; release validation is by running GoReleaser.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/goreleaser.sh -->
