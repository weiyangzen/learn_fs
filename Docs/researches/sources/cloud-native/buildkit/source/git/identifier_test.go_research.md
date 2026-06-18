# sources/cloud-native/buildkit/source/git/identifier_test.go

## Purpose
This file tests git identifier URL parsing and bundle/checkout-bundle attribute validation. It is the main local test signal for the identifier logic introduced around git bundle support.

## Important Tests
`TestNewGitIdentifier` covers SSH URLs, git protocol URLs, scp-style GitHub URLs, bare host paths that default to HTTPS, refs, subdirs, URL-encoded users, and unsafe subdir cleanup such as `../../escape` and absolute paths. `TestIdentifierBundleValidation` covers valid registry and OCI-layout bundle locators, missing checksum, unsupported HTTPS locator scheme, unsupported SHA512 digest, checkout-bundle incompatibility with keep-git-dir and subdir, standalone checkout-bundle, bundle plus checkout-bundle, and checksum/ref SHA mismatch or match.

## Control Flow
The URL tests table-drive `NewGitIdentifier` and compare the resulting struct. Bundle validation creates a `Source{}` and calls its `Identifier("git", url, attrs, nil)` path so it tests production attribute parsing plus validation rather than calling helpers directly.

## State and Persistence
No persistent state. Each case creates fresh identifiers and attribute maps.

## Dependencies and Integration Points
It imports solver protobuf attribute constants and `testify/require`. It indirectly depends on the git source `Source.Identifier` implementation and `gitutil.ParseURL` subdir normalization.

## Risks Covered
The suite catches dangerous or unsupported bundle configurations before runtime: bundle without checksum, digest algorithm mismatch, unsupported scheme, checkout-bundle with worktree-only options, and contradictory ref/checksum pins. It does not test actual bundle download, staging, git import, or checkout-bundle snapshot creation.

## Test Signals
Strong unit-level signal for parsing and static validation. Runtime behavior still requires integration coverage with git CLI and blob/OCI content sources.
