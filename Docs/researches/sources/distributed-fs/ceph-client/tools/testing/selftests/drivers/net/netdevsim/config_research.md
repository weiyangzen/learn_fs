# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/config

Purpose: Documents kernel configuration options needed for the netdevsim selftests.

Important entries: Requires `CONFIG_NETDEVSIM=m`, `CONFIG_DUMMY=y`, IPv6, scheduler qdiscs (`MQPRIO`, `MULTIQ`, `PRIO`), `CONFIG_PSAMPLE=y`, tunnel modules (`VXLAN`, `GENEVE`), `CONFIG_MACSEC=m`, and `CONFIG_PTP_1588_CLOCK_MOCK=y`.

Control flow: No executable flow. Kselftest config tooling can merge these symbols into a test kernel configuration.

State and persistence: No runtime state. It influences whether modules and kernel subsystems are available when tests run.

Dependencies and integration: Directly supports scripts in the same directory. Devlink, FIB, nexthop, ethtool, psample, UDP tunnel NIC, and qdisc tests all assume these kernel facilities are present.

Risks: Some scripts also require userspace tools (`ip`, `devlink`, `ethtool`, `jq`, `tc`, `socat`, `udevadm`) that are not represented here. A built-in/module mismatch can matter when scripts expect `modprobe` and `modprobe -r` to work.

Test signals: A suitable kernel should expose `/sys/bus/netdevsim`, debugfs netdevsim controls, PSAMPLE netlink, qdisc kinds, and tunnel device creation.
