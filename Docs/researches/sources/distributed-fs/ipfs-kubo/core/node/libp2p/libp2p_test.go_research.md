# sources/distributed-fs/ipfs-kubo/core/node/libp2p/libp2p_test.go

Purpose: tests option priority sorting. Important test is `TestPrioritize`.

Control flow: the test creates libp2p options that encode their identity as TCP listen ports, applies `prioritizeOptions`, extracts port numbers from the resulting config, and checks ordering with default priorities and custom priorities.

State and persistence: no external state.

Dependencies/integration: libp2p config application, multiaddr parsing, testify. It protects the shared priority mechanism used by security and other configurable libp2p option groups.

Risks signaled: a sorting regression would silently change protocol preference order; this test makes the behavior explicit.
