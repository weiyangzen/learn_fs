# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ynl_nsim_lib.sh

Purpose: shared shell helper for YNL C test wrappers that need a deterministic netdevsim device.

Important functions/state: globals define `NSIM_ID=1337`, `NSIM_DEV`, and `KSFT_SKIP=4`. `nsim_cleanup()` writes the ID to `/sys/bus/netdevsim/del_device` and ignores failures. `nsim_setup()` loads netdevsim, verifies `/sys/bus/netdevsim/new_device`, installs cleanup trap, creates one port, waits for udev, discovers the netdev name, renames it to `nsim0`, brings it up, and assigns IPv4 `192.168.1.1/24` plus IPv6 `2001:db8::1/64 nodad`.

Dependencies/integration: sourced by `devlink.sh`, `ethtool.sh`, `rt-addr.sh`, and `rt-route.sh`. Requires root privileges, `modprobe`, `udevadm`, `ip`, netdevsim, IPv4, and IPv6.

Risks/test signals: fixed global ID can conflict with parallel tests or stale devices. Cleanup is best effort. It does not create a separate network namespace, so tests run in the caller namespace. Successful setup is a prerequisite for address/route/devlink/ethtool tests.
