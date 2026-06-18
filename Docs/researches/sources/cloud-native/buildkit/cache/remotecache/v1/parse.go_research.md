# sources/cloud-native/buildkit/cache/remotecache/v1/parse.go

## Purpose

This file parses serialized v1 cache config JSON back into a `solver.CacheExporterTarget`, reconstructing cache records, input links, and remote result chains.

## Important APIs, Types, and Functions

- `Parse` unmarshals JSON into `cacheimporttypes.CacheConfig` and delegates to `ParseConfig`.
- `ParseConfig` iterates cache records and recursively parses each one.
- `parseRecord` validates record indexes, detects loops, reconstructs input links, resolves compact and chained remote results, and calls target `Add`.
- `getRemoteChain` resolves a parent-linked layer chain into a `solver.Remote` with a multi-provider.

## Control Flow and State

Parsing uses a map from record index to already parsed record; a nil value is a recursion sentinel for loop detection. For each record, inputs are parsed first so dependency links point at concrete exporter records. Compact `Results` use `getRemoteChain`, which recursively follows `ParentIndex` through the `Layers` array and builds a remote descriptor list from parent to child. `ChainedResults` directly append listed layer descriptors in the declared order and use a multi-provider over all descriptors. Results whose provider descriptors are missing are skipped instead of failing. The reconstructed record is added to the target.

All state is in-memory and scoped to a single parse call.

## Dependencies and Integration Points

The parser depends on `cache/remotecache/v1/types`, solver cache exporter target APIs, content multi-provider helpers, and OCI descriptors. Backend importers call this parser after reading cache config from registry, local, S3, GHA, or inline image config.

## Risks and Edge Cases

Invalid record or layer indexes fail. Looping records and looping layer parent chains fail. Empty input groups are invalid. Missing providers silently remove affected results, allowing partial cache import. `getRemoteChain` mutates the returned remote while unwinding recursion and wraps prior providers in a new multi-provider for each child. Chained results do not use parent relationships and rely entirely on explicit layer order.

## Test Signals

`chains_test.go` exercises successful parsing of a simple compact result but does not assert a newly parsed graph's output. There are no tests here for invalid loops, chained results, missing providers, or malformed indexes.
