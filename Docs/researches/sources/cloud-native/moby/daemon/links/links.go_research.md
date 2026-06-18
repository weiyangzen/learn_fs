## sources/cloud-native/moby/daemon/links/links.go

Purpose: Generates legacy Docker link environment variables describing a linked child container's address, exposed ports, name, and selected environment variables.

Important APIs and types: `Link` stores parent IP, child IP, link name, child environment, and exposed ports. `EnvVars` is the one-shot helper, `NewLink` constructs a `Link` from a `network.PortSet`, `(*Link).ToEnv` renders environment variables, and `withTCPPriority` sorts ports with TCP first, then by port/protocol.

Control flow and state: `ToEnv` derives the alias from the basename of the link name, uppercases it, and replaces hyphens with underscores. It sorts ports, emits a primary `<ALIAS>_PORT` for the first port, emits per-port URL/address/port/proto variables for every port, detects consecutive same-protocol ranges and emits START/END variables, appends `<ALIAS>_NAME`, then copies child env vars except malformed entries and `HOME`/`PATH`.

Dependencies and integration points: Uses `api/types/network.Port`, Go `maps` and `slices`, and is consumed by daemon legacy link setup to populate container startup environments.

Risks: Environment output is legacy compatibility surface and order-sensitive enough that tests sort before comparison. Alias normalization only replaces hyphens, so other unusual name characters are preserved. The first primary port depends on the TCP-priority sort.

Test signals: `links_test.go` covers naming, constructor output, child env propagation, port sorting, continuous TCP ranges, mixed protocols, and includes a benchmark for multi-port env generation.
