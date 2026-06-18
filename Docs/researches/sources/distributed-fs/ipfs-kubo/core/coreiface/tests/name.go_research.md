# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/name.go

## Purpose
Conformance tests for IPNS publish and resolve behavior.

## Important APIs, Types, and Functions
Defines deterministic random source `rnd`, helper `addTestObject`, and tests `TestPublishResolve`, `TestBasicPublishResolveKey`, and `TestBasicPublishResolveTimeout`.

## Control Flow and State
Tests create online swarms, add UnixFS objects, publish under self or a generated key, resolve direct and suffixed names with cache on/off, and verify record expiry by publishing with one-second validity then resolving after a delay.

## Dependencies and Integration Points
Depends on Unixfs, Name, Key, IPNS, path options, and multi-node provider setup.

## Risks and Test Signals
Signals include self-key mapping, generated-key publishing, suffix preservation, cache disabled resolution, and expiry. Timing sleeps make expiry tests slow and somewhat timing-sensitive; routing propagation relies on provider setup.
