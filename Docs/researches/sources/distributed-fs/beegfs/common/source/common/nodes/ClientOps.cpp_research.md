<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.cpp

### Purpose
`ClientOps.cpp` stores per-client or per-user operation counters, computes deltas between snapshots, and requests client operation statistics from remote nodes using old and v2 protocol messages.

### Important APIs, Types, And Functions
`ClientOps::addOpsList()` validates counter-list sizes, sums per-ID and total counters, and stores absolute values. `sumOpsListValues()` uses `std::transform` and `sum`. `getDiffOpsMap()` compares current counters against `oldIdOpsMap`. `getDiffSumOpsList()` subtracts `oldSumOpsList` from `sumOpsList`. `clear()` swaps current maps/lists into old snapshots. `ClientOpsRequestor::request()` loops over `GetClientStatsMsg` or `GetClientStatsV2Msg` responses until `moreData` is false, validates layout version, and converts old IPv4 client IDs into the new uint128 IP representation.

### Control Flow
The requestor starts with current ID `~0`, sends paged stats requests, parses vector metadata (`moreData`, layout version, number of ops), then groups each ID plus `numOps` counters into the result map. Per-user requests preserve numeric IDs; per-client old protocol requests convert IPv4 network-order IDs through `IPAddress`.

### State, Persistence, And Dependencies
`ClientOps` keeps current and previous snapshots in memory under `idOpsMapMutex`. It depends on `MessagingTk`, `GetClientStats*` messages, `NodeOpStats`, `IPAddress`, and `uint128`.

### Integration Points
Monitoring and management code use this to report client/user operation rates rather than raw cumulative counters.

### Risks
`getDiffSumOpsList()` assumes `oldSumOpsList` is at least as long as `sumOpsList`; calling it before a valid old snapshot can be unsafe. Vector parsing uses `.at()` for header fields but relies on correct vector shape for grouped data. Tests should cover first snapshot behavior, size mismatches, paging, layout mismatch, v1 IPv4 conversion, v2 uint128 IDs, per-user mode, and counter wrap/underflow semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.cpp -->
