# sources/cloud-native/containerd/internal/cri/util/references_test.go

## Purpose
Validates CRI image reference parsing and repo digest/tag construction.

## Important APIs, Types, And Functions
`TestParseImageReferences` feeds canonical, tagged, digest-only, and arbitrary refs. `TestGetRepoDigestAndTag` parses Docker refs and checks returned repo digest and tag.

## Control Flow
Tests compare exact returned slices and strings after invoking the helpers.

## State And Persistence
No state beyond test vectors.

## Dependencies And Integration Points
Uses `testify/assert`, `distribution/reference`, and `opencontainers/go-digest`.

## Risks
The test vectors are narrow and do not cover multiple tags, ports, default registry normalization, uppercase rejection, or malformed digest algorithms.

## Test Signals
Good regression coverage for the core branch decisions: canonical versus tagged versus invalid.
