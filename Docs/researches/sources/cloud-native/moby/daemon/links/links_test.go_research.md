## sources/cloud-native/moby/daemon/links/links_test.go

Purpose: Unit tests and benchmark for legacy link environment generation.

Important tests: `TestLinkNaming` validates alias derivation from `/db/docker-1` to `DOCKER_1`. `TestLinkNew` checks `NewLink` field population. `TestLinkEnv` verifies child env propagation. `TestSortPorts` protects TCP-first and port/protocol ordering. `TestLinkMultipleEnv` verifies mixed TCP/UDP output and continuous TCP range START/END variables. `BenchmarkLinkMultipleEnv` measures repeated env generation.

Control flow and state: Tests sort generated environment variables before comparison because map-derived port order is not semantically relevant after rendering. `cmpopts.EquateComparable(network.Port{})` handles comparable port structs.

Dependencies and integration points: Uses `api/types/network.PortSet` and `network.MustParsePort`. The tested output is consumed by container runtime environment setup for links.

Risks covered: Prevents regressions in legacy env names, skipped reserved child env vars, port range compaction, and protocol ordering. It does not cover malformed child env entries explicitly or unusual alias characters beyond hyphen replacement.
