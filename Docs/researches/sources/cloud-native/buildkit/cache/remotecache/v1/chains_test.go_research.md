# sources/cloud-native/buildkit/cache/remotecache/v1/chains_test.go

## Purpose

This file tests the basic v1 cache-chain marshal and parse behavior.

## Important APIs, Types, and Functions

- `TestSimpleMarshal` is the sole test. It builds a cache graph, marshals it, verifies structural fields, repeats adds for idempotency, roundtrips through JSON and `Parse`, and verifies adding an extra root record changes record count.
- `dgst` is a helper that creates canonical digests from test strings.

## Control Flow and State

The test creates two root records using `outputKey`, then creates a dependent `baz` record with two inputs: one unselected link to `foo` and one selected link to `bar`. It attaches a two-descriptor remote result and a timestamp. After marshal, it checks that the two layer descriptors are serialized as a parent chain, the dependent record contains two input groups and one result, and link indexes/selectors point at the expected records. It then calls the same add sequence again and verifies the config remains identical. Finally, it marshals the config to JSON, parses it into new chains, and checks the original config remains stable.

## Dependencies and Integration Points

The test uses the public `CacheChains.Add`, `Marshal`, `Parse`, `outputKey`, `solver.Remote`, and OCI descriptors. It is the nearest direct test signal for the v1 graph implementation used by all remote cache backends.

## Risks and Edge Cases

The test assumes a deterministic record order for the simple fixture. It does not assert the newly parsed chain's marshaled config; it calls `cc.Marshal` after parsing into `newChains`, so it mainly checks that parsing did not error rather than full roundtrip equality on the new graph. Broader graph cases are untested.

## Test Signals

This test confirms the simple cache config shape and idempotency of repeated adds. Missing coverage includes candidate merging, chained results, missing providers, invalid loops, compression filtering, and storage loading.
