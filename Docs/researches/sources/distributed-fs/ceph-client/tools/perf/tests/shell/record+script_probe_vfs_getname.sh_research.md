## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+script_probe_vfs_getname.sh

Purpose: verifies that `perf record` captures the shared `vfs_getname` probe and `perf script` exposes the touched pathname argument.
Important functions: `record_open_file` and `perf_script_filenames`.
Control flow: adds the probe, creates temp perf.data and target file, records `touch $file` with `-e probe:vfs_getname*`, then greps `perf script` for a `touch` event with `pathname="$file"`.
State and persistence: temporary files and the added probe are cleaned up.
Dependencies and integration: requires root, perf probe, kernel debuginfo or existing probe, and libtraceevent support.
Risks: event name suffixes, pathname quoting, and kernel symbol argument naming can break the regex.
Test signals: successful probe addition, record support check, and matching perf script line.
