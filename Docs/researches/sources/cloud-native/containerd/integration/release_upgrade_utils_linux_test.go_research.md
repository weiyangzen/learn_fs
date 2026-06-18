# sources/cloud-native/containerd/integration/release_upgrade_utils_linux_test.go

## Purpose

`release_upgrade_utils_linux_test.go` supplies Linux-only helper functions used by the release-upgrade tests to discover and download previous containerd release binaries.

## Important APIs, Types, and Functions

- `downloadPreviousLatestReleaseBinary` resolves the latest tag for a requested release line and downloads it.
- `downloadReleaseBinary` builds the GitHub release tarball URL for `linux-$GOARCH`, performs an HTTP GET, gzip-decodes the body, and unpacks it into the target directory with containerd archive apply logic.
- `previousReleaseVersion` lists remote tags matching `refs/tags/v<line>.*`, semver-sorts them, and returns the newest.
- `gitLsRemoteCtrdTags` shells out to `git ls-remote --tags --exit-code`, parses tag refs, and skips peeled `^{}` entries.

## Control Flow

Upgrade tests call `downloadPreviousLatestReleaseBinary`, which calls `previousReleaseVersion`, then `downloadReleaseBinary`. The tag query returns all matching release tags, the helper normalizes the `refs/tags/` prefix, semver-sorts, and downloads the selected tarball.

## State and Persistence Behavior

The helpers write unpacked release binaries into a caller-provided temporary directory. They do not cache downloads or persist global state.

## Dependencies and Integration Points

The file depends on GitHub releases, `git`, Go HTTP, gzip, runtime architecture detection, `golang.org/x/mod/semver`, and `github.com/containerd/containerd/v2/pkg/archive`. It is tightly coupled to containerd release asset naming.

## Risks and Edge Cases

Network failures, GitHub rate limits, missing tags, unsupported architectures, non-200 responses, corrupt gzip streams, and release asset naming changes will fail the upgrade suite before daemon behavior is tested. The HTTP call is intentionally marked with `nolint:gosec` because it fetches a fixed public release URL.

## Test Signals

These helpers are not separately tested; their signal comes from `TestUpgrade`, which fails if tag discovery, download, or unpacking breaks.
