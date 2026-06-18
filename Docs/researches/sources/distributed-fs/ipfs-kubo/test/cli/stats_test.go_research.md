# sources/distributed-fs/ipfs-kubo/test/cli/stats_test.go

Purpose: a small smoke test for `ipfs stats dht`.

Important APIs and functions: `TestStats` starts two initialized daemons, connects them, runs `node1.IPFS("stats", "dht")`, and checks command result fields through testify assertions.

Control flow: the single subtest requires no stderr, a successful command error state, and non-empty stdout lines. The nodes are stopped through deferred cleanup.

State and persistence: no persistent state is asserted. DHT stats are read from live online daemon state after a two-node connection.

Dependencies and integration points: exercises the `stats dht` CLI command, DHT subsystem, daemon connectivity, and harness result buffering.

Risks and test signals: because it checks only non-empty output, it is a broad availability signal rather than a strict contract test. Failure indicates the command errored, wrote unexpected stderr, or stopped emitting any DHT stats.
