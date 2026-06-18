# sources/cloud-native/moby/integration/service/swarm_test.go

## Purpose
Regression coverage for Swarm CA fingerprint validation during node join.

## Important APIs, Types, And Functions
- `TestSwarmCAHash` mutates the CA hash segment of a valid worker join token and attempts `SwarmJoin` from a second daemon.
- Uses `d1.JoinTokens(t).Worker`, `d2.SwarmListenAddr`, and `client.SwarmJoinOptions`.

## Control Flow
The test skips nftables firewall backends, starts a manager Swarm and a second standalone daemon, replaces token field 2 with a bogus hash, then verifies join fails with the expected fingerprint mismatch message.

## State And Persistence
Only temporary daemon and Swarm state are created. The second daemon never joins because validation fails.

## Dependencies And Integration Points
Integrates Swarm token parsing, CA fingerprint validation, daemon Swarm join API, and daemon helper methods.

## Risks And Edge Cases
The test assumes the token format remains hyphen-delimited with the CA hash at index 2. It is skipped for nftables backends because Swarm is unavailable there.

## Test Signals
The expected signal is an error containing `remote CA does not match fingerprint`.
