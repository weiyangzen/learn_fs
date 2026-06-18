# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-common.sh

Purpose: Shared shell helper for netdevsim ethtool tests.

Important APIs/functions: Defines counters `num_passes` and `num_errors`; `check` compares a command status/current value/expected value tuple and reports errors; `make_netdev` loads netdevsim if needed, writes a random id plus optional arguments to `/sys/bus/netdevsim/new_device`, waits for udev, and returns the interface name from the new device's `net/` directory. Cleanup removes the simulated device with `del_device`.

Control flow: Test scripts source the file, call `make_netdev`, then use `check` for assertions. The helper snapshots `/sys/class/net` before adding a port to detect the newly-created netdev.

State and persistence: Creates `/sys/bus/netdevsim/devices/netdevsim*` state and a netdevsim port. The installed `trap cleanup EXIT` removes it with `del_device`; it does not unload the module.

Dependencies and integration: Requires `modprobe`, `/sys/bus/netdevsim`, debugfs/sysfs availability, and root. It is used by coalesce, feature, FEC, pause, and qdisc visibility scripts.

Risks: New-netdev detection by set difference can be confused by unrelated interface churn. `modprobe -r netdevsim` may fail if other tests/devices hold the module. Helper-global counters require sourcing scripts not to redefine them unexpectedly.

Test signals: A caller receives a usable netdev name, cleanup removes the device, and `check` counts and reports pass/fail totals consistently.
