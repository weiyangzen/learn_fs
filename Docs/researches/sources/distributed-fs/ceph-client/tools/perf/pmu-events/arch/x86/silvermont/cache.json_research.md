# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/cache.json

## Purpose
Defines Silvermont cache, memory-uop, offcore-response, queue-rejection, and related core PMU aliases for perf. The 77-entry JSON array gives users named events for L1/L2 behavior, load/store retirement, cross-core HITM, instruction-cache fill stalls, offcore response filters, and REHABQ activity.

## Important APIs, Types, And Event Groups
The file uses perf's event JSON schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and optional `PEBS`, `MSRIndex`, and `MSRValue`. It does not specify `Unit`, so aliases target the Silvermont core PMU. `SampleAfterValue` is present on all entries, and `PEBS` appears on memory-uop events that support precise sampling.

Major groups are `LONGEST_LAT_CACHE.*`, `MEM_UOPS_RETIRED.*`, `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`, `CORE_REJECT_L2Q.ALL`, `L2_REJECT_XQ.ALL`, `REHABQ.*`, and a large `OFFCORE_RESPONSE.*` family. Offcore-response aliases share event code `0xB7` and umask `0x1` but use `MSRIndex` and `MSRValue` to program the dedicated offcore response MSR with request and response filters.

## Control Flow
Control flow is declarative but has an important offcore programming path. Perf parses each JSON object into an alias; for normal aliases it programs event select and umask fields. For offcore aliases, perf must also write the encoded `MSRValue` to the specified `MSRIndex` so the hardware filters request type and response class correctly. Runtime measurement flow depends on whether the selected alias is simple, PEBS-capable, or offcore-MSR-backed.

## State And Persistence
The file persists static alias metadata. Runtime state includes programmed core PMU counters and, for offcore events, dedicated MSR filter state associated with the event. PEBS-capable aliases may produce precise sample records in perf sampling mode. No results are written back to the JSON.

## Dependencies And Integration Points
This catalog depends on Silvermont core PMU support, perf's PMU alias parser, and perf/kernel support for offcore response MSR programming. It integrates with the `counter.json` file because Silvermont has only two generic counters, making scheduling conflicts likely when many cache/offcore events are requested together. It also interacts with PEBS sampling paths for precise retired memory-uop events.

## Risks
The dense offcore family is high risk because many aliases differ only by `MSRValue`; a single wrong bit changes the request or response filter while leaving the alias syntactically valid. Offcore events also need compatible counter/MSR handling, so multiplexing and unsupported combinations can surprise users. PEBS flags need to match hardware capability. Count semantics vary: references, misses, retired uops, queue rejects, and cycles should not be combined without normalization.

## Test Signals
Use `jq empty` and perf table-generation tests for syntax/schema coverage. `perf list` should show the aliases, including offcore variants. Runtime smoke tests should open a simple cache event, a PEBS memory-uop event, and an offcore response event; offcore tests should confirm that perf accepts the MSR-backed alias and does not fall back to an unfiltered raw event. Workloads with cache misses and cross-core sharing can validate directional behavior.
