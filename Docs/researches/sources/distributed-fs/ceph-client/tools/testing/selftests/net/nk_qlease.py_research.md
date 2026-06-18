<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nk_qlease.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/nk_qlease.py

## Purpose
This Python kselftest exercises the netdev generic-netlink queue leasing API with netkit virtual devices and netdevsim physical devices. It validates successful leases, rejection paths, cleanup on device or namespace removal, channel resizing interactions, cross-namespace references, and lease persistence across link state and namespace movement.

## Important APIs, Types, And Functions
Helpers include `wait_until()`, `create_netkit()`, and `create_netkit_single()`. The test matrix uses `NetNS`, `NetNSEnter`, `NetdevFamily.queue_create()`, `queue_get()`, `bind_rx()`, `EthtoolFamily.channels_set()`, `RtnlFamily.newlink()`, `NetdevSimDev`, `cmd()`, `defer()`, `ip()`, and kselftest assertions/errors from `lib.py`. `main()` runs 45 named test functions.

## Control Flow
Each test creates isolated netdevsim and/or netkit devices, often moves the netkit guest into a test namespace, brings devices up or down, performs queue lease operations from the relevant namespace, and validates returned queue IDs or expected `NlError` errno values. The matrix covers duplicate leases, invalid lessors/lessees, queue range/type errors, physical and virtual deletion order, link flaps, multiple leases, l3/single netkit modes, netns ID validation, guest/physical namespace moves, channel shrink/grow cases, bind-rx rejection on leased queues, and capacity exhaustion.

## State, Persistence, And Dependencies
State includes temporary network namespaces, netkit pairs, netdevsim devices, NAPI/queue state, queue lease relationships, ethtool channel counts, netns IDs, and deferred cleanup callbacks. It depends on the Python netlink helpers in `lib.py`, kernel netdev-genl queue APIs, netkit, netdevsim, ethtool netlink, and sufficient privileges.

## Integration Points
This is deep integration coverage for queue leasing across generic netlink, rtnetlink-created netkit devices, simulated physical NIC queues, ethtool channel management, and netns lifetime rules. It also validates what lease information is visible from the physical side versus virtual side.

## Risks
The file is broad and newer-kernel dependent; missing netkit, netdevsim, or netdev-genl features will cause skips/failures outside the logic being tested. Many tests depend on ifindex values captured before netns moves, so kernel semantics around ifindex preservation matter. Deferred cleanup order is important for devices moved between namespaces.

## Test Signals
`ksft_run()` reports each function result. Strong signals are exact returned queue IDs, presence or absence of `lease` in `queue_get()`, expected errno values such as `EINVAL`, `EBUSY`, `EOPNOTSUPP`, `ERANGE`, and successful cleanup after deleting devices or namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nk_qlease.py -->
