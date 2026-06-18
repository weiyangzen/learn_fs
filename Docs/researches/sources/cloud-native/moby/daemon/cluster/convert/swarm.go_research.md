# sources/cloud-native/moby/daemon/cluster/convert/swarm.go

## Purpose
Converts swarmkit cluster specs and cluster state to Docker API swarm objects and merges API swarm spec updates into existing swarmkit specs.

## Important APIs, Types, And Functions
Exports `SwarmFromGRPC`, `SwarmSpecToGRPC`, and `MergeSwarmSpecToGRPC`.

## Control Flow
`SwarmFromGRPC` copies cluster info, orchestration, raft, encryption, CA config minus signing cert/key, TLS trust root/issuer, default address pools, VXLAN port, join tokens, dispatcher heartbeat, external CAs, metadata, and annotations. `MergeSwarmSpecToGRPC` only overwrites fields when API values are nonzero/non-nil except force rotate and autolock, validates external CA protocols, and propagates signing CA material for update requests.

## State And Persistence
No local state. It controls how swarm spec updates preserve existing raft state and which sensitive CA fields are redacted from read responses.

## Dependencies And Integration Points
Used by swarm init/update/inspect flows. Depends on swarmkit CA issuer parsing, gogo durations, netip prefix parsing, and shared annotation conversion.

## Risks And Test Signals
Zero-value merge semantics mean users cannot clear some fields through this path unless represented by pointers. External CA protocol validation can reject updates. Tests are outside this subset.
