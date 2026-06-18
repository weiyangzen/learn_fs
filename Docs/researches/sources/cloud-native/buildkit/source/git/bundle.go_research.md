# sources/cloud-native/buildkit/source/git/bundle.go

## Purpose
This file implements git bundle import and checkout-bundle support. Bundle import lets a git source fetch commits from a digest-addressed blob rather than the remote repository. Checkout-bundle mode emits a single `bundle` file instead of a worktree.

## Important APIs
Constants define `bundleFileName`, transient import filename, and fallback ref. `bundleTargetRef` normalizes user refs for emitted bundles. `detectBundleSHA256` probes bundle object format. `stageBundle`, `ensureStagedBundle`, and `releaseStagedBundle` manage temporary imported bundle repos. `downloadBundleToFile` and `openBundleBlob` fetch and verify bundle blobs. `resolveBundleMetadata` handles metadata lookup in bundle mode. `checkoutAsBundle` and `writeBundleToMount` create the output bundle snapshot safely.

## Control Flow
Import flow parses the bundle locator, creates a temp directory, downloads the blob through `blobfetch`, verifies SHA256 digest, detects object format via `git ls-remote`, initializes a temp bare repo, fetches all refs from the bundle, and checks the pinned commit exists. `ensureStagedBundle` caches the staged file URL and registers idempotent cleanup with `JobContext.Cleanup` when available. Metadata resolution skips staging for empty/SHA refs because the checksum already pins the commit.

Checkout-bundle flow creates a mutable cache ref, mounts it, builds an isolated temp bare repo, fetches the pinned commit from the shared repo, updates a natural target ref, runs `git bundle create`, and copies the staged bundle into the mount through `os.OpenRoot`.

## State and Persistence
Temporary bundle repos live under OS temp directories and are cleaned by job cleanup or explicit handler release. Checkout-bundle persists a committed cache snapshot containing one file named `bundle`.

## Dependencies and Integration Points
It integrates with solver job cleanup, BuildKit cache/snapshot/session, git CLI helpers, `blobfetch`, source type schemes, and git source handler fields such as registry hosts, session manager, cache, and SHA256 object-format state.

## Risks
Cleanup registration is critical; staging without a job context relies on later handler teardown. Blob fetch can stream large bundles to disk. Security-sensitive writes use `os.OpenRoot` and temp staging to avoid symlink escape. Only SHA256 bundle blob digests are accepted, matching the verification hasher.

## Test Signals
`identifier_test.go` covers static bundle locator and checkout-bundle validation. Runtime staging, import, cleanup, and checkout-bundle materialization require integration tests with git and blob stores.
