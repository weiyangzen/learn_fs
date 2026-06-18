## sources/distributed-fs/ceph-client/tools/perf/tests/shell/probe_vfs_getname.sh

Purpose: exclusive smoke test that adds and removes the shared `probe:vfs_getname` probe.
Important behavior: sources `lib/probe.sh` and `lib/probe_vfs_getname.sh`, requires perf probe support and root, then calls `add_probe_vfs_getname`.
Control flow: if adding the probe returns `1`, it calls `skip_if_no_debuginfo` to convert missing kernel debuginfo into skip code `2`; cleanup runs before exit.
State and persistence: may add a kernel probe and removes it only if absent at startup.
Dependencies and integration: validates the common probe library before record/trace consumers rely on it.
Risks: kernel source-line matching and debuginfo availability dominate outcomes; incorrect `had_vfs_getname` handling could delete user-created probes.
Test signals: final exit code from add/skip path and clean probe removal.
