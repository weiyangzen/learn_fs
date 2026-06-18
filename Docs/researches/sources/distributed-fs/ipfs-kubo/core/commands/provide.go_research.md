# sources/distributed-fs/ipfs-kubo/core/commands/provide.go

## Purpose

`provide.go` implements experimental commands for controlling and observing content providing. It can clear the provide queue, queue immediate provider-record announcements, and render detailed statistics for sweep or legacy provider systems.

## Important APIs, Types, and Functions

`ProvideCmd` registers `clear`, `once`, and `stat`. `ProvideOnceEvent` reports queued CIDs. `provideStats` carries either sweep stats or legacy reprovider stats. Helpers include `extractSweepingProvider`, human formatting functions, and `provideCIDSync`. Stats output supports sections for connectivity, queues, schedule, timings, network, operations, and workers.

## Control Flow

`provide clear` obtains the node and calls `n.Provider.Clear`, optionally suppressing output. `provide once` requires an online node, `Provide.Enabled`, and either peers or HTTP provider config. It deduplicates argument and stdin CIDs with an auto-growing bloom tracker, validates each CID exists locally, and either announces only roots or recursively walks reachable DAG blocks. Each announced CID calls `nd.Provider.ProvideOnce(c.Hash())` and emits a queued event. CLI post-run gives TTY-friendly running counters in text mode and forwards JSON/XML streams unchanged. `provide stat` requires online mode, handles legacy provider stats separately, unwraps sweep providers from dual/buffered wrappers, fetches stats, and text-encodes either a brief summary, selected sections, all sections, or compact two-column output.

## State and Persistence Behavior

`clear` mutates in-memory provider queues. `once` queues immediate provider announcements but explicitly does not add CIDs to the periodic reprovide schedule. Recursive walking reads local DAG blocks. Stats are read-only. Provider records are network-visible routing state after worker processing.

## Dependencies and Integration Points

Dependencies include Boxo DAG walker/merkledag/provider stats, Kubo config and cmdenv, libp2p DHT provider implementations, routing interfaces, terminal detection, humanize formatting, and DHT key formatting. It integrates with import fast-provide paths in pin/add and with node provider configuration.

## Risks and Test Signals

Risks include bloom false positives skipping rare CIDs, recursive walks over huge DAGs, no connected peers causing failures unless HTTP providers exist, distinction between queueing and actual network completion, and complex stats formatting. Tests should cover queue clear nil provider, provide-once local-missing blocks, stdin/argument dedup, recursive cancellation on announce error, text TTY/non-TTY post-run, JSON pass-through, disabled provide config, legacy versus sweep stats, LAN selection errors, compact requires all, closed provider output, and worker warning thresholds.
