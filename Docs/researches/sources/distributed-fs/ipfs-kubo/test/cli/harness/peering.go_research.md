# sources/distributed-fs/ipfs-kubo/test/cli/harness/peering.go

Purpose: helpers for constructing peered node topologies with deterministic local listen ports.

Important APIs/types/functions: `Peering{From, To}` describes config-level peering edges. `NewRandPort` allocates unique TCP ports with a process-wide map and mutex. `CreatePeerNodes` creates a harness, initializes nodes, disables routing, assigns local swarm ports, and applies peering config edges.

Control flow: port allocation first asks the OS for an available port, records it, and falls back to random ports in the 30000-39999 range. Node config updates run in parallel, then requested `PeerWith` relationships are applied.

State and persistence: global `allocatedPorts` tracks ports for the test process. Node configs persist routing type, swarm addresses, and peering entries in repo config files.

Dependencies/integration: uses Go networking, Kubo config structs, `testing.T`, and harness `Node` configuration helpers.

Risks: a port can be allocated then taken by another process before daemon bind. The global map never releases ports, acceptable for tests but long-lived. Test signals are successful daemon startup and expected peering behavior.
