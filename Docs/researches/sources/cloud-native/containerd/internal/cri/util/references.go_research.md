# sources/cloud-native/containerd/internal/cri/util/references.go

## Purpose
Normalizes and classifies image references for CRI image status and metadata reporting.

## Important APIs, Types, And Functions
`ParseImageReferences` parses arbitrary strings with `distribution/reference.ParseAnyReference`, returning separate repo tag and repo digest slices. `GetRepoDigestAndTag` derives a repo digest from a named reference plus OCI digest and preserves a tag when the original reference was tagged.

## Control Flow
Invalid references are skipped. Canonical references become digests, tagged references become tags, and digest-only references without a repository are not reported as repo digests.

## State And Persistence
No internal state. Returned strings can be stored in CRI image status fields.

## Dependencies And Integration Points
Uses `github.com/distribution/reference` and `github.com/opencontainers/go-digest`. It integrates CRI image reporting with Docker/reference parsing rules.

## Risks
Silently skipping parse failures can hide malformed input unless callers log elsewhere. Reference normalization follows upstream parser behavior and may differ from user-provided spelling.

## Test Signals
`references_test.go` covers tagged, canonical, digest-only, invalid, and tag-plus-digest derivation cases.
