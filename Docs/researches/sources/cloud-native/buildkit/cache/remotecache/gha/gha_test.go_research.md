# sources/cloud-native/buildkit/cache/remotecache/gha/gha_test.go

## Purpose

This file defines the integration test for the GitHub Actions cache backend. It validates that a BuildKit solve can export cache records to the GitHub Actions cache service, prune all local cache state, and then import the remote cache to reproduce the same build outputs.

## Important APIs, Types, and Functions

- `TestGhaCacheIntegration` registers the single integration scenario and mirrors `busybox:latest`.
- `testBasicGhaCacheImportExportExtraTimeout` builds a two-step LLB state, exports local output and `gha` cache, prunes local cache, then rebuilds with `gha` cache import.
- `ensurePruneAll` retries `client.Prune(..., client.PruneAll)` until `DiskUsage` reports no entries.
- `requiresLinux` skips the scenario outside Linux.

## Control Flow and State

The test initializes OCI/containerd or dockerd workers in `init`, then creates a BuildKit client for the sandbox. It constructs a state rooted in scratch with two files: a constant file and a generated random checksum. It gathers GitHub Actions cache attributes from `ACTIONS_RUNTIME_TOKEN`, `ACTIONS_CACHE_URL`, `ACTIONS_RESULTS_URL`, and `ACTIONS_CACHE_SERVICE_V2`; if the environment is incomplete, the test skips. The scope includes the test name and branch/tag/pull-request suffix from `GITHUB_REF` to avoid broad key collisions.

The first solve exports the filesystem locally and writes `mode=max` remote cache to `gha`. After confirming the files exist, the test prunes all local cache. The second solve uses the same definition with `CacheImports` from the same scope. It then verifies the constant file and generated checksum match the original output, proving the remote cache restored the previously generated layer content.

## Dependencies and Integration Points

The test uses the public `client.Solve` API, `llb` state construction, integration sandbox helpers, worker feature gates for cache import/export and `FeatureCacheBackendGha`, and GitHub-hosted runner environment variables. It exercises the actual remote cache resolver indirectly through cache option type `gha`.

## Risks and Edge Cases

The test is environment-sensitive and skips unless GitHub runtime cache variables are available. GitHub Cache Service v2 is noted as not immediately consistent, so the test sleeps for three seconds before import. `ensurePruneAll` is retry-based and can fail if a worker holds cache references longer than expected. The test does not cover signed cache indexes, REST key-map optimization, malformed attributes, or multiple readable scopes.

## Test Signals

This is the primary test signal for `gha.go`: successful export, local prune, and import with identical output content. It also validates v2 URL selection when `ACTIONS_CACHE_SERVICE_V2` is true.
