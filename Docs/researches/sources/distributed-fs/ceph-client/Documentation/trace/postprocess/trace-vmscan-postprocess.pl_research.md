<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/trace/postprocess/trace-vmscan-postprocess.pl -->
# sources/distributed-fs/ceph-client/Documentation/trace/postprocess/trace-vmscan-postprocess.pl

## Purpose
Perl trace postprocessor for Linux page reclaim/vmscan activity. It summarizes direct reclaim, kswapd wake/sleep, LRU scanning/reclaim, writeback, latency, and per-order reclaim pressure from ftrace text streams.

## Important APIs, Types, And Functions
- Constants identify vmscan tracepoints, per-order buckets, state fields, and derived high-level metrics.
- Options: `--ignore-pid` and `--read-procstat`.
- `generate_traceevent_regex()` derives field regexes from tracefs event format files for direct reclaim, kswapd, LRU isolate/shrink, and writepage events.
- `timestamp_to_ms()` converts ftrace timestamps for latency measurement.
- `process_events()` updates `%perprocesspid` and process-name cache state.
- `dump_stats()` prints latency lines, direct reclaim table, kswapd table, and global summaries.
- `aggregate_perprocesspid()` merges process-PID rows by process name.

## Control Flow
Startup builds regexes from `/sys/kernel/tracing/events/vmscan/.../format` with defaults when unavailable. The main loop parses ftrace lines including optional flags between CPU and timestamp. Begin/end tracepoints set and consume timestamps to derive direct reclaim and kswapd awake latencies. LRU isolate and shrink events contribute scanned/reclaimed file/anon counts. Writepage events classify sync/async and file/anon I/O from reclaim flags.

## State And Persistence
Metrics live in Perl hashes keyed by process/PID and in global total counters. Per-order counts use array slots up to order 19. `%last_procmap` remembers process names for trace lines that omit them. The script writes no files and prints reports at EOF or delayed SIGINT.

## Dependencies And Integration Points
Depends on Perl, tracefs vmscan event format files, `/proc` for optional process-name lookup, and ftrace text streams. It is meant for live use with `trace_pipe` or offline trace captures.

## Risks And Edge Cases
The parser is sensitive to tracepoint format and has known proof-of-concept accuracy limits. Some printf format strings include more arguments than column headers, so display alignment should be tested when fields change. Aggregation has a likely typo assigning `MM_VMSCAN_DIRECT_RECLAIM_END` after aggregating kswapd latencies. Unmatched details are skipped with warnings, so totals can undercount when trace formats drift.

## Test Signals
Run with synthetic traces covering begin/end pairing, missing process names, kswapd rewake, inactive file/anon scanning, reclaim writeback flags, malformed detail fields, `--ignore-pid`, and SIGINT report paths. Validate total summaries against known input counts and latencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/trace/postprocess/trace-vmscan-postprocess.pl -->
