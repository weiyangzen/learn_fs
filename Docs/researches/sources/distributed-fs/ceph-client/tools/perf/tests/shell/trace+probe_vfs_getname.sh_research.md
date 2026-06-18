## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace+probe_vfs_getname.sh

Purpose: validates `perf trace` uses the `vfs_getname` probe to beautify open filename arguments.
Important function: `trace_open_vfs_getname`.
Control flow: requires perf probe/trace and root, adds the shared probe, builds an event list from available open/openat tracepoints, disables user perf config, runs `perf trace -e events touch $file`, and greps for a formatted open call containing the temp filename and flags.
State and persistence: temp file and added probe are cleaned.
Dependencies and integration: `lib/probe.sh`, `lib/probe_vfs_getname.sh`, syscall tracepoints, and perf trace argument beautifier.
Risks: output formatting and flag names are strict; available syscall tracepoint names vary by kernel.
Test signals: matching open/openat trace line with correct filename and mode/flags.
