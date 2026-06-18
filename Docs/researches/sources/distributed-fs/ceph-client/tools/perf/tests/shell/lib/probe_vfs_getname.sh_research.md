## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe_vfs_getname.sh

Purpose: shared shell library for tests that need a `probe:vfs_getname` kernel probe on `getname_flags` to expose filename/pathname data to `perf record`, `perf script`, and `perf trace`.
Important functions: `cleanup_probe_vfs_getname`, `add_probe_vfs_getname`, `skip_if_no_debuginfo`, and `skip_no_probe_record_support`. The library snapshots whether the probe already existed in `had_vfs_getname`, avoids deleting preexisting probes, and tries several source-line regexes for old and new kernel layouts.
Control flow: probe addition lists `getname_flags`, extracts a line containing `initname`, `result->uptr`, or `result->aname`, then attempts a typed `pathname=result->name:string` probe before falling back to `filename:ustring`.
State and persistence: it mutates global kernel perf probe state only when the probe was absent at startup, then removes `probe:vfs_getname*` on cleanup.
Dependencies and integration: requires `perf probe`, kernel debuginfo for line probes, optional libtraceevent support for recording probe events, and is sourced by probe, record/script, and trace tests.
Risks: regexes are kernel-source-layout sensitive; failure codes distinguish unsupported debuginfo (`2`) from actual probe failure (`1`). Existing user probes must not be removed.
Test signals: successful return from `add_probe_vfs_getname`, skip detection in debuginfo/libtraceevent checks, and later consumers seeing `probe:vfs_getname` events.
