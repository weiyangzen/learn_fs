# sources/distributed-fs/ipfs-kubo/core/commands/stat.go

Purpose: defines the `ipfs stats` command tree and implements bandwidth statistics under `ipfs stats bw`.

Important APIs/types/functions: `StatsCmd` wires `bw`, `repo`, `bitswap`, `dht`, `provide`, and `reprovide`. `statBwCmd` supports `--peer`, `--proto`, `--poll`, and `--interval`; `printStats` formats totals/rates.

Control flow: `statBwCmd` requires an online node and non-nil bandwidth reporter. It rejects simultaneous peer and protocol filters, decodes peer IDs, parses polling intervals, then emits either peer, protocol, or total bandwidth stats. In polling mode it loops until the request context is canceled, sleeping for the configured interval.

State and persistence behavior: read-only. It reads in-memory libp2p bandwidth counters and does not mutate repo or network state.

Dependencies and integration points: uses `cmdenv.GetNode`, libp2p metrics, peer/protocol types, command post-run CLI formatting, and `humanize` for byte output.

Risks: polling writes carriage-return terminal output and can run indefinitely until cancellation. Reporter-disabled configs return an error. Protocol/peer strings are not cross-validated against active connections.

Test signals: no direct tests here; command-tree validation covers schema. Runtime behavior depends on libp2p metrics reporter tests elsewhere.
