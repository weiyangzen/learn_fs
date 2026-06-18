# sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/config

This config fragment requests the kernel modules needed by the kmod selftest: `CONFIG_TEST_KMOD=m` and `CONFIG_TEST_LKM=m`.

There is no control flow. The fragment is consumed by kselftest config tooling. `CONFIG_TEST_KMOD` provides the sysfs-driven test driver, and `CONFIG_TEST_LKM` provides the loadable test module used by request-module tests.

Dependencies are module build and install support. Risks are runtime naming or built-in/module mismatches with `kmod.sh` assumptions. Pass signal is `test_kmod` exposing `/sys/devices/virtual/misc/test_kmod0/` after `modprobe`.
