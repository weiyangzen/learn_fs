# sources/distributed-fs/ceph-client/tools/testing/selftests/locking/ww_mutex.sh

Purpose: loads the kernel `test-ww_mutex` module to run in-kernel wait/wound mutex API tests.

Important APIs/types/functions: uses `/sbin/modprobe -q -n test-ww_mutex` for availability probing, `modprobe test-ww_mutex` to execute module init tests, and `modprobe -r` for cleanup.

Control flow: if the module is unavailable, prints skip and exits `4`. If load succeeds, unloads it and reports ok. If load fails, reports failure and exits `1`.

State and persistence: temporarily loads a kernel test module and removes it on success.

Dependencies and integration points: kernel built with `test-ww_mutex` module, root/module-loading permissions, modprobe path.

Risks: module init contains the actual assertions; this shell wrapper cannot distinguish individual subtest failures. Cleanup only happens on successful load.

Test signals: module availability skip, successful load/unload pass, load failure fail.
