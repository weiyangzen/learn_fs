
# sources/distributed-fs/ceph-client/tools/perf/util/off_cpu.h

Purpose: defines the public off-CPU profiling interface and constants used when BPF skeleton support is available.

Important APIs/types/functions: `OFFCPU_EVENT` is the synthetic event name `"offcpu-time"`. `OFFCPU_SAMPLE_TYPES` declares required sample fields: identifier, IP, TID, time, ID, CPU, period, raw data, and cgroup. `OFFCPU_THRESH` is a 500,000,000 ns threshold. When `HAVE_BPF_SKEL` is set, `off_cpu_prepare` and `off_cpu_write` are declared; otherwise inline stubs return `-1`.

Control flow: no runtime logic in supported builds beyond declarations. Unsupported builds fail fast through stubs so callers can disable or reject off-CPU mode.

State and persistence: no state is stored here. The eventual implementation prepares evlists/record options and writes data into a perf session.

Dependencies: Linux perf event sample flags and forward-declared perf `evlist`, `target`, `perf_session`, and `record_opts`.

Integration points: included by perf record/session code for off-CPU sampling. The event name and sample type constants are shared contracts between command-line setup, BPF collection, and data writing.

Risks: stale sample-type bits would break decoder expectations for raw off-CPU records. Stubs returning `-1` require callers to present useful diagnostics. Test signals include build coverage with and without `HAVE_BPF_SKEL`, off-CPU record smoke tests, and perf data decode checks for expected sample fields.
