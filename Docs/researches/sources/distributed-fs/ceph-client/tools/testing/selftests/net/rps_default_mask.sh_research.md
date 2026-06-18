<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rps_default_mask.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/rps_default_mask.sh

## Purpose

`rps_default_mask.sh` verifies propagation rules for `net.core.rps_default_mask`. It checks that the sysctl affects newly created devices in the namespace where it is set, does not retroactively change existing devices, and defaults to zero in child namespaces.

## Important APIs, Types, and Functions

The script defines `setup`, `cleanup`, and `chk_rps`. It reads `/proc/sys/net/core/rps_default_mask`, creates temporary netns and veth devices, writes the sysctl in init and child namespaces, and reads `/sys/class/net/<dev>/queues/rx-0/rps_cpus`. It normalizes comma-separated CPU masks before integer comparison.

## Control Flow

The script skips unless more than two CPUs are available. It saves the initial mask, tests a zero default in a child namespace, restores, sets init namespace mask to 1 and later 3, verifies existing lo devices are unchanged, creates veth peers and verifies only the new init-namespace device inherits 3, recreates the child namespace, sets child mask to 1, creates another veth pair, and verifies inheritance is local to the child namespace. It exits with accumulated `ret`.

## State and Persistence Behavior

It mutates `/proc/sys/net/core/rps_default_mask` in the init namespace and child namespace, creates and deletes a temporary namespace and veth device, and reads sysfs RPS masks. The EXIT trap restores the initial init-namespace mask and deletes the namespace.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include root/CAP_NET_ADMIN, RPS sysctl support, veth, namespaces, and at least three CPUs. Integration points are RPS default mask inheritance and sysfs `rps_cpus` initialization. Risks include numeric comparison of large hex masks, CPU masks with commas, namespace cleanup already done before EXIT, and skip on small systems. Signals are `[ ok ]` lines for each `chk_rps` case and exit status zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/rps_default_mask.sh -->
