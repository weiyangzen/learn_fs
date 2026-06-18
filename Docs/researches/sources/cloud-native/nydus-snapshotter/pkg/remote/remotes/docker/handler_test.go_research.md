# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/handler_test.go

## Purpose
Tests distribution-source label manipulation and blob mount candidate selection helpers.

## Important APIs, Types, And Functions
`TestAppendDistributionLabel`, `TestDistributionSourceLabelKey`, `TestCommonPrefixComponents`, and `TestSelectRepositoryMountCandidate`.

## Control Flow
The tests assert that label values are deduplicated and sorted, empty repo entries are removed, generated keys include the source host suffix, prefix matching counts path components, and mount candidate selection ignores the target repo while choosing the best available alternate source.

## State And Persistence
No persistent state; all inputs are in-memory strings and reference specs.

## Dependencies And Integration Points
Uses containerd label constants and reference specs. These helpers are consumed by pull labeling and pusher cross-repository mount attempts.

## Risks And Edge Cases
The tested candidate selection is intentionally simple and string-based; it does not verify repository existence or permissions.

## Test Signals
Direct coverage for helper behavior that affects performance and bandwidth during pushes but not content correctness.
