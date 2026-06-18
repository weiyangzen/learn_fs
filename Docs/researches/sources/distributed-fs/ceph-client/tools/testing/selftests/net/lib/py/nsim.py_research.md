# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/py/nsim.py

## Purpose
This module wraps Linux `netdevsim` devices and ports for Python networking selftests.

## Important APIs and Types
`NetdevSimDev` represents a bus device. It can `ctrl_write` under `/sys/bus/netdevsim`, `dfs_write` under debugfs, create a random-address device with port and queue counts, reload it into a namespace, collect ifnames, wait for port netdevices, remove the device, and remove individual ports. `NetdevSim` represents one port, verifies udev-provided names against port index when applicable, reads detailed JSON link state, records `ifindex`, and writes per-port debugfs attributes.

## Control Flow and State
Construction loads `netdevsim` if needed, writes `new_device`, waits for the expected netdevices, optionally moves the devlink device to a namespace, settles udev, and creates `NetdevSim` port objects. Kernel state persists until `remove()` or context exit writes `del_device`. Object state records bus address, debugfs directories, namespace, port list, and removal status.

## Dependencies and Integration
It depends on `/sys/bus/netdevsim`, `/sys/kernel/debug/netdevsim`, `modprobe`, `devlink`, `udevadm`, `ip -d -j`, and helpers from `utils.py`. It integrates with tests needing synthetic NICs and debugfs-controllable behavior.

## Risks and Test Signals
Random address selection handles `ENOSPC` collisions but still assumes sysfs/debugfs availability and mounted debugfs. `wait_for_netdevs` busy-waits for up to five seconds without sleep, which may be CPU-heavy. A successful signal is a populated `nsims` list with JSON link metadata and valid ifindexes.
