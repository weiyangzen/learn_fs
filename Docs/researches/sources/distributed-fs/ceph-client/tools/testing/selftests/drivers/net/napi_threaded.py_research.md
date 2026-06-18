<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_threaded.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_threaded.py

Purpose: Python netdev selftest for persistent NAPI threaded state across device-level toggles and queue count changes.

Important functions/APIs: assertions `_assert_napi_threaded_enabled/disabled`, `_set_threaded_state`, `_setup_deferred_cleanup`, tests `napi_init`, `enable_dev_threaded_disable_napi_threaded`, `change_num_queues`, and `main`. Uses `NetDrvEnv`, `NetdevFamily` netlink, `ethtool -L`, sysfs `/sys/class/net/$ifname/threaded`, and ksft assertions.

Control flow: each test records current combined queue count and threaded sysfs state for deferred restore, toggles device threaded mode, changes queue count down and back up, then dumps NAPI netlink objects and checks `threaded` state and pid presence.

State/dependencies: mutates queue count and sysfs threaded flag, restored through `defer`. Requires at least two combined queues and NAPI netlink support. Risks include hardware that cannot change queues, sysfs state formatting, netlink schema changes, and persistent threaded state not scoped per test if cleanup fails. Test signals are ksft equality/non-equality/ge assertions on NAPI objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/napi_threaded.py -->
