# sources/cloud-native/moby/daemon/libnetwork/networkdb/cluster_test.go

## Purpose
Property and statistical tests for NetworkDB random peer sampling.

## Important APIs, Types, And Functions
`TestMRandomNodes` exercises `mRandomNodes`. Helpers `assertUniqueElements`, `kpermutations`, and `distributionStats` validate uniqueness, possible permutation counts, and distribution metrics.

## Control Flow
The test handles empty and local-only slices, then uses rapid-generated node slices containing the local node at random positions. It checks sample length, local-node exclusion, uniqueness, small permutation coverage, repeated-sample variation, and count distribution across repeated trials.

## State And Persistence
Uses a `newNetworkDB(DefaultConfig())` instance without starting memberlist. The random generator is process-local.

## Dependencies And Integration Points
Depends on `pgregory.net/rapid`, `gotest.tools`, iterators, math/bits, and map/slice helpers. Protects `cluster.go` gossip and bulk sync peer selection.

## Risks
Statistical checks can theoretically flake, so the test tolerates some outlier trials. Saturating permutation math avoids overflow for large generated sets.

## Test Signals
Strong signal that local node is excluded, selected peers are unique, sample size is bounded, and selection is not obviously biased.
