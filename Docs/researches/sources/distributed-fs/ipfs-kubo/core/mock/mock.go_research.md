# sources/distributed-fs/ipfs-kubo/core/mock/mock.go

## Purpose
Provides helpers for constructing mock Kubo nodes and command contexts in tests.

## Important APIs, Types, and Functions
Exports `NewMockNode`, `MockHostOption`, `MockCmdsCtx`, and `MockPublicNode`.

## Control Flow and State
`NewMockNode` creates an online node using a mocknet host. `MockHostOption` adapts mocknet to Kubo's libp2p host option, applying listen addresses to the peerstore because mocknet does not consume libp2p options. `MockCmdsCtx` builds a mock repo/node and returns a command context. `MockPublicNode` initializes config, assigns deterministic public-looking swarm addresses based on mocknet peer count, and creates an online DHT server node.

## Dependencies and Integration Points
Depends on Kubo core/build config, repo mocks, command context, datastore, config initialization, libp2p mocknet/testing identity, peerstore, and host options. Used by tests needing lightweight nodes.

## Risks and Test Signals
Risks include mocknet behavior diverging from real libp2p, missing private key in some mock configs, address collisions from peer-count mapping, and tests accidentally depending on public-looking addresses. Signals are compile/test use across command/core tests.
