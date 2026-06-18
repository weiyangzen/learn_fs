# sources/cloud-native/buildkit/frontend/gateway/gateway_test.go

## Purpose

This file tests gateway frontend source allowlist behavior.

## Important APIs, Types, And Functions

- `TestCheckSourceIsAllowed` constructs gateway frontends with different allowed repositories and calls `checkSourceIsAllowed`.

## Control Flow

The test first verifies an empty allowlist permits any source. It then creates an allowlist with a fully tagged repository, confirms the same tagless repository and another tag are accepted because comparison trims tags, and confirms a different repository is rejected. Finally it verifies Docker Hub normalization makes `alpine`, `library/alpine`, and `docker.io/library/alpine` equivalent.

## State And Persistence Behavior

Only in-memory gateway frontend structs are created. No external state is modified.

## Dependencies And Integration Points

It uses `NewGatewayFrontend`, the concrete `gatewayFrontend`, distribution reference normalization indirectly, and `testify/require`.

## Risks And Edge Cases

The test covers tag-insensitive matching and Docker Hub normalization. It does not cover invalid allowlist entries, invalid source strings, digested sources, or registry case/normalization edge cases.

## Test Signals

This is the direct regression signal for repository allowlist behavior used before launching external gateway frontends.
