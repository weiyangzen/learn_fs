# sources/distributed-fs/ipfs-kubo/core/commands/update_github_test.go

Purpose: unit tests for the GitHub/update helper layer that protects `ipfs update install` from malformed metadata, failed downloads, and checksum mismatches.

Important APIs/types/functions: tests cover `verifySHA512`, `downloadAndVerifySHA512`, `githubGet`, `githubListReleases`, `githubLatestRelease`, `findReleaseAsset`, `downloadAsset`, `extractBinaryFromArchive`, `assetNameForPlatformTag`, `trimVPrefix`, `normalizeVersion`, and `isNewerVersion`. `makeTarGz` builds in-memory archives.

Control flow: most tests use `httptest.Server`; tests that override package-level `githubReleaseFmt` are intentionally not parallel and restore the var with `t.Cleanup`. Other tests use `t.Parallel`. Assertions verify both happy paths and clear error messages.

State and persistence behavior: no durable state. Temporary HTTP servers and package variable overrides are cleaned up. Archive data is in-memory.

Dependencies and integration points: validates `update_github.go` and parts of `update.go` archive/version helpers. Uses runtime OS/arch to assert platform-dependent asset names.

Risks: tests do not cover real GitHub pagination, redirects, proxy behavior, auth token presence, zip extraction, permission fallback, actual binary replacement, or daemon lock behavior. Package global override requires non-parallel grouping for affected tests.

Test signals: strong local signal for integrity checks and API error mapping. A failure likely indicates a direct regression in update safety or release metadata assumptions.
