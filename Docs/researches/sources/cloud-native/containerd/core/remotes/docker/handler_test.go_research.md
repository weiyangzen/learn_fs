<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/handler_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/handler_test.go

## Purpose
Tests the Docker distribution-source label helpers used for cross-repository mount optimization.

## Important APIs, Types, And Functions
- `TestAppendDistributionLabel` validates empty values, duplicate removal, insertion sorting, and empty-repo filtering.
- `TestDistributionSourceLabelKey` asserts the `labels.LabelDistributionSource + "." + source` format.
- `TestCommonPrefixComponents` checks prefix scoring.
- `TestSelectRepositoryMountCandidate` verifies candidate choice from source labels.

## Control Flow
The tests are table-driven and call unexported helpers directly. They construct small `reference.Spec` and label maps rather than exercising a real content store.

## State And Persistence
No persistent state. The tests validate pure string and map transformations.

## Dependencies And Integration Points
Depends on the label prefix constant and reference spec shape. It protects behavior relied on by `AppendDistributionSourceLabel` and `dockerPusher.push`.

## Risks And Edge Cases
Tests capture duplicate source entries and target-repository exclusion behavior, but they do not cover the content-manager update path or label validation overflow.

## Test Signals
Strong unit signal for deterministic label formatting and repository candidate scoring.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/handler_test.go -->
