<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.c

## Purpose

`intel-tpebs.c` implements perf stat support for Intel TPEBS retirement-latency events. It runs a hidden `perf record` process for the selected latency events, reads sampled `weight3` values from the record stream, summarizes them, and feeds the chosen mean/min/max/last latency back into the evsel count slot used by perf stat metrics.

## Important APIs, Types, and Functions

Global controls are `tpebs_recording` and `tpebs_mode`. `struct tpebs_retire_lat` links each retire-latency evsel to the generated event string, accumulated `struct stats`, last observed value, and started flag. Public functions are `evsel__tpebs_open()`, `evsel__tpebs_read()`, and `evsel__tpebs_close()`. Internal flow uses `evsel__tpebs_prepare()`, `evsel__tpebs_event()`, `evsel__tpebs_start_perf_record()`, `__sample_reader()`, `process_sample_event()`, `tpebs_send_record_cmd()`, and `tpebs_stop()`.

## Control Flow

Opening a retire-latency evsel prepares all matching evsels in the evlist, creates control and ack pipes, starts `perf record -W --synth=no --control=fd:... -o -` with generated `name=tpebs_event_<evsel>` event aliases, starts a reader thread, and enables recording through the control channel. The reader creates a read-mode perf session over the child stdout and updates per-event stats for samples that belong to the measured workload or inherited children. Reads ping the record process before the first result, select a latency value according to `tpebs_mode`, and write it into the first CPU/thread count cell. Close removes the event and stops the child/reader when the last TPEBS event is gone.

## State and Persistence Behavior

State is process-local and protected by a lazily initialized mutex: the global results list, child process descriptor, pipe file descriptors, and reader thread. No data is persisted to disk because the child writes perf data to stdout. Counts are synthetic and accumulate into `evsel->counts` and optionally `prev_raw_counts`.

## Dependencies and Integration Points

It depends on perf run-command control protocol tags, perf session reading, evlist/evsel metadata, workload pid/inherit state, procfs parent traversal, `struct stats`, CPU map formatting, mutex annotations, and perf stat count storage. It integrates with `evsel__open/read/close` paths for retire-latency events.

## Risks and Edge Cases

The code is concurrency-sensitive: `tpebs_send_record_cmd()` temporarily drops the mutex to avoid starving the reader. Ack timeouts, early child exit, pipe setup failure, thread creation failure, and evlist purge races are handled but remain high-risk. The event-string conversion assumes an `R` modifier and slash/colon layout in `evsel->name`. Child-process filtering through `/proc/<pid>/status` can race with process exit. If no samples arrive, the code falls back to precomputed latency values and warns once.

## Test Signals

Tests should cover multiple retire-latency evsels, CPU list propagation, workload pid filtering with and without inherit, child exit before ack, no-sample fallback for all modes, evlist purge/close races, and first-cell-only count updates. Integration smoke tests should verify that perf stat metrics change when TPEBS samples are available and that hidden `perf record` exits cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-tpebs.c -->
