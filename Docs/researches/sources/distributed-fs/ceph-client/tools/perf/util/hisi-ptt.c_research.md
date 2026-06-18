<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.c

## Purpose
`hisi-ptt.c` plugs HiSilicon PCIe Trace and Tuning AUX trace data into perf session processing. It registers an `auxtrace` handler from `PERF_RECORD_AUXTRACE_INFO`, reads AUXTRACE payloads, and dumps decoded PTT packets when trace dumping is enabled.

## Important APIs, types, and functions
The public function is `hisi_ptt_process_auxtrace_info`. Internal `struct hisi_ptt` embeds `struct auxtrace` and records auxtrace type, session, host machine, and PMU type. Key callbacks are `hisi_ptt_process_auxtrace_event`, `hisi_ptt_process_event`, `hisi_ptt_flush`, `hisi_ptt_free_events`, `hisi_ptt_free`, and `hisi_ptt_evsel_is_auxtrace`.

## Control flow
`hisi_ptt_process_auxtrace_info` validates private data size, allocates a handler, extracts the PMU type from `auxtrace_info->priv[0]`, fills callback slots, installs it into `session->auxtrace`, and optionally prints info. Later, `hisi_ptt_process_auxtrace_event` mallocs a buffer sized by `event->auxtrace.size`, reads that many bytes from the perf data fd, and calls `hisi_ptt_dump_event` under `dump_trace`. Dumping determines packet type from the first dword, rounds the whole buffer down to that packet size, and iterates packet descriptions.

## State and persistence
State is session-scoped and freed by the auxtrace `free` callback. The implementation does not persist decoded events; it only consumes/dumps raw AUXTRACE data. `hisi_ptt_process_event`, flush, and free-events callbacks are placeholders returning success/no-op.

## Dependencies and integration points
It integrates with perf AUX trace, perf session data fds, `evsel` PMU typing, host machine state, `dump_trace`, color output, and the PTT packet decoder.

## Risks
`event->auxtrace.size` is stored in an `int`, so very large payload sizes risk truncation before allocation/read. The code computes `data_offset` for non-pipe input but does not use it after reading. Packet type is inferred once from the first packet, so mixed packet streams would be decoded incorrectly. Normal analysis support is minimal: non-dump processing currently drops data after reading.

## Test signals
Tests should cover AUXTRACE_INFO private-size validation, PMU type matching, pipe and file-backed AUXTRACE reads, `dump_trace` packet output for 4DW/8DW fixtures, zero/truncated payloads, large-size rejection behavior if added, and cleanup through session auxtrace free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hisi-ptt.c -->
