<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/compops.cc -->
# sources/distributed-fs/coda/coda-src/resolution/compops.cc

Purpose: computes compensating operations for directory resolution by comparing local and remote resolution logs for a specific `ViceFid`.

Important APIs/control flow: exported `ComputeCompOps(olist *AllLogs, ViceFid *Fid)` extracts the local host log with `ExtractLog(ThisHostAddr, Fid)`, extracts per-remote logs, sorts logs into `arrlist`s, finds each remote log's latest common non-resolution operation with the local log, collects entries after that common point as non-local operations, merges duplicate remote entries by `ViceStoreId`, removes operations already present locally, and sorts final compensating entries by host index and sequence number. `PrintCompOps` is the exported debug printer.

State/persistence: operates on in-memory parsed logs (`he`, `remoteloglist`, `rsle`) and returns an `arrlist` of existing `rsle *` pointers; it does not own or persist log entries.

Dependencies/integration: consumes log structures from `parselog.cc`, `rsle`, `resutil` host entries, global `ThisHostAddr`, `SrvDebugLevel`, and Coda container classes.

Risks/test signals: assumes sorted store IDs and uses pointer identity to locate common points in original remote lists. If no common point exists, resolution cannot proceed. Memory ownership is mixed: arrays are freed/deleted but returned entries belong to original logs. Test with multi-host logs containing duplicate store IDs, no common point, resolution opcodes interleaved with normal opcodes, and different sequence ordering per host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/compops.cc -->
