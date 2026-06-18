# sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/rebalancing.go

Purpose: implements `beegfs stats rebalance`, presenting chunk-balancer/rebalancing job statistics from metadata or storage nodes.

Important APIs/types/functions: `RebalanceStatsCfg`; `newRebalancingStatsCmd`; `runRebalanceStatsCommand`; `cbStatsSingleNode`; `cbStatsMultiNode`; `printCBData`.

Control flow: optional node argument selects single-node mode; otherwise the command queries all nodes of a node type. Debug enables the hidden worker count and UID columns. Each interval collects statuses, sorts multi-node rows by node type and numeric ID, prints status/start/end/work/error/locked/migrated data, then repeats until interval is nonpositive or context is canceled.

State and persistence: read-only. It displays active/cumulative server-side rebalancing job counters.

Dependencies and integration points: uses backend `ctl/pkg/ctl/stats` chunk-balance APIs, BeeGFS entity parsing, go slices sorting, `cmdfmt`, Viper debug flag, and BeeMsg version metadata in help text.

Risks: interval defaults to continuous output, so scripts should set `--interval=0` when a one-shot is needed. Error rows are embedded in the last unnamed column instead of aborting per offline node. `locked_inodes` is only meaningful for meta nodes.

Test signals: no direct tests. Useful coverage would check single vs multi selection, sort order, debug columns, error row formatting, timestamp zero handling, and interval cancellation.
