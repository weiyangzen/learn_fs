## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_pfm.sh

Purpose: exercises all libpfm4 events exposed through `perf list --raw-dump pfm`.
Important behavior: skips entirely if `HAVE_LIBPFM` is off, skips uncore events and invalid/missing unit mask messages, and runs `perf stat --pfm-events`.
Control flow: first tries `true`, then a longer synthesize benchmark if supported output did not include the event.
State and persistence: no files.
Dependencies and integration: requires libpfm4 build support and PMU/event availability.
Risks: broad hardware-dependent coverage; uncore events are intentionally excluded because they may need extra options.
Test signals: event name appears in stat output or is recognized as not supported/invalid unit mask.
