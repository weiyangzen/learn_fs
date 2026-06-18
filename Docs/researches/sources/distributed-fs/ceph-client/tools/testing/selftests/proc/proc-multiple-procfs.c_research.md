# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-multiple-procfs.c

Purpose: verifies that separately mounted procfs instances with different `hidepid` options are distinct superblocks/devices.

Important APIs and functions: uses `mkdtemp`, `mount("proc", ..., "hidepid=1")`, `mount("proc", ..., "hidepid=2")`, `stat`, `umount`, and `snprintf`.

Control flow: create two temporary directories, mount procfs with two hidepid modes, stat each mount's `meminfo`, unmount both, and assert the `st_dev` values differ.

State and persistence: creates temporary directories under `/tmp` and mounts procfs instances. The directories are not removed by this test, but mounts are unmounted.

Dependencies and integration: requires mount privilege and procfs. It is a simple assertion test rather than kselftest harness based.

Risks and test signals: may fail in unprivileged environments or when `/tmp` restrictions prevent mount points. A semantic failure means procfs option-specific mounts are incorrectly shared.
