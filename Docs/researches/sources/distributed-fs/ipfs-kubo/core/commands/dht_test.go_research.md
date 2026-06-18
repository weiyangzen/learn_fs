<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dht_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dht_test.go

## Purpose

Tests DHT key translation behavior for public key and IPNS routing keys.

## Important APIs, Types, and Functions

`TestKeyTranslation` generates a random peer ID, computes expected namesys public-key routing key and IPNS routing key, and compares them to `escapeDhtKey` outputs.

## Control Flow

The test builds `/pk/<peer>` and `/ipns/<peer>` paths, passes them to `escapeDhtKey`, fails on errors, and compares exact strings.

## State and Persistence Behavior

Pure test; no repo or network state.

## Dependencies and Integration Points

Uses boxo namesys, IPNS name routing keys, and libp2p test peer generation. `escapeDhtKey` is defined outside the listed source but is exercised by this test file.

## Risks and Edge Cases

The test is focused on two key namespaces and does not cover invalid keys or the deprecated query command in `dht.go`.

## Test Signals

Strong signal that DHT key escaping remains compatible with namesys/IPNS routing expectations. Limited signal for command runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dht_test.go -->
