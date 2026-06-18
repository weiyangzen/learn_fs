# sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/client.go

Purpose: implements client and user statistics commands that show per-client or per-user BeeGFS operation counters over time.

Important APIs/types/functions: `clientStats_Config`; `newGenericClientStatsCmd`; `newClientStatsCmd`; `newUserStatsCmd`; `runClientStatsCmd`; `printOps`; `userIDToString`; `clientIPToString`; `printOpsRow`; `printOpsRetro`.

Control flow: optional node argument is parsed as meta/storage entity ID. Each interval fetches current stats for one node or node type, diffs against previous counters, computes a sum, prints the time index, then prints rows filtered by name, nonzero/all, limit, and output style. The loop stops when interval is nonpositive or context is canceled.

State and persistence: read-only. Keeps in-memory previous stats to calculate interval deltas. `--names` performs host/user lookups but does not cache them here.

Dependencies and integration points: uses backend `ctl/pkg/ctl/stats`, BeeGFS entity parsing, `cmdfmt.Printomatic`, unit conversion, Viper raw formatting, OS user lookup, reverse DNS, and protobuf `msg.Uint128` IDs.

Risks: `limit` is applied before `filter`, so a filtered client beyond the limit will not show. `sum[0] > 1` controls summary printing, which may skip summaries with exactly one operation unless `--all`. Native-endian decoding of client IP IDs assumes the server encoding matches local behavior. DNS/user lookup can block or fail silently.

Test signals: no direct tests. Useful tests would isolate IP/user formatting, filter/limit behavior, raw-vs-formatted read/write values, interval cancellation, and retro output.
