
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/node/ping.go

- Purpose: implements `node ping` through a mounted BeeGFS client module.
- Important APIs: `newPingCmd` and `runPingCmd`.
- Control flow/state: validates count, interprets args as a node type or explicit entity IDs, calls `node.PingNodes`, consumes result/error channels, prints per-ping timing plus average/median/min/max, and returns partial success when some nodes fail.
- Dependencies/integration: uses backend `PingConfig`, BeeGFS entity parsers, global worker count for parallel mode, logging, and CTL partial-success errors.
- Risks/tests: median indexing uses `cfg.Count` rather than actual successful sample count, which may panic or misreport if some pings fail within a result. No direct tests found.
