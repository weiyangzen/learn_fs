# sources/cloud-native/buildkit/source/git/source_test.go

## Purpose
Provides comprehensive integration-style tests for the Git source implementation across SHA1/SHA256 object formats, ref kinds, cache reuse, mutation races, submodules, signature verification, bundle handling, mtime normalization, and compatibility file modes.

## Important APIs, Types, And Functions
- Test helpers: `setupGitSource`, `setupGitRepo`, `serveGitRepo`, `runShell`, `runShellEnv`, `logProgressStreams`, `gitSnapshotMode`, and `gitRevParse`.
- Fixture types: `gitRepoFixture` and `testJobContext`.
- Major test families cover repeated fetch, fetch-by-SHA, fetch-by-commit, tags/refs/branches, race scenarios, multiple repos/tags, metadata objects, signatures, subdirs, bundle detection, mtimes, and compatibility modes.

## Control Flow
Tests build temporary Git repositories, often served through `git http-backend` via `httptest`. They construct `GitIdentifier` values, call `Resolve`, `CacheKey`, and `Snapshot`, mount resulting refs, and assert content, cache keys, pins, file modes, mtimes, and `.git` state. Race tests mutate remote refs after cache-key calculation and verify snapshot still uses the pinned commit or returns explicit errors if the pinned commit becomes unreachable.

## State And Persistence
Each test creates an isolated containerd/native snapshot cache and metadata DB. Temporary repos include branches, tags, annotated tags, signed commits/tags when fixture env is set, submodules, special refs, and generated bundles. Tests release refs and close snapshot/cache stores via cleanup.

## Dependencies And Integration Points
Exercises containerd metadata/content stores, native snapshotter, BuildKit cache manager, lease manager, progress logging, git CLI, CGI smart HTTP serving, signature fixtures (`BUILDKIT_TEST_SIGN_FIXTURES`), and solver compatibility versions.

## Risks And Edge Cases
Many tests are skipped on Windows due to missing bind-mount support. Signature tests are fixture-dependent. CGI smart HTTP tests depend on local `git` supporting requested object formats and bundle commands. Some assertions use exact cache-key strings and request counts, which catch regressions but can require updates when serialization changes intentionally.

## Test Signals
This file is itself the main signal for `source.go`: it validates deterministic cache reuse, mutation race protection, tag/branch ambiguity handling, fetch-by-commit semantics, credential redaction, submodule removal, signature policy behavior, bundle ref shape and SHA256 detection, mtime reset, and v0.13/v0.14 file-mode compatibility.
