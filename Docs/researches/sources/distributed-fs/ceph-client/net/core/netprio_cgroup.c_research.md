<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netprio_cgroup.c -->
# sources/distributed-fs/ceph-client/net/core/netprio_cgroup.c

## Purpose
Legacy cgroup subsystem that assigns per-cgroup, per-netdevice packet priority indexes and propagates a task's cgroup priority index into already-open sockets on attach.

## APIs, Types, and Functions
The subsystem object is `net_prio_cgrp_subsys`. Core helpers are `extend_netdev_table()`, `netprio_prio()`, `netprio_set_prio()`, cgroup callbacks `cgrp_css_alloc()`, `cgrp_css_online()`, `cgrp_css_free()`, `net_prio_attach()`, cftype handlers `read_prioidx()`, `read_priomap()`, `write_priomap()`, and device notifier `netprio_device_event()`.

## Control Flow, State, and Persistence
Each netdev may own an RCU-replaced `struct netprio_map` indexed by cgroup CSS ID. Online child cgroups inherit parent priorities for all init-net devices under RTNL. Writes to `ifpriomap` parse `ifname priority`, grow the device table only for nonzero writes or existing entries, and store the priority. Attach iterates each task's open files under task lock and updates socket cgroup priority metadata. Netdev unregister clears and RCU-frees the priomap.

## Dependencies and Integration
Depends on the legacy cgroup API, init network namespace devices, RTNL, RCU, socket cgroup data, fdtable iteration, and netdevice notifier registration at `subsys_initcall()`.

## Risks and Test Signals
Risks include init-net-only behavior, large CSS ID table growth up to `USHRT_MAX`, attach-time races with file table changes, and legacy interface semantics. Test signals are inherited parent priority on child online, zero writes avoiding allocation, readback via `prioidx` and `ifpriomap`, socket priority update after cgroup attach, and priomap cleanup on device unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netprio_cgroup.c -->
