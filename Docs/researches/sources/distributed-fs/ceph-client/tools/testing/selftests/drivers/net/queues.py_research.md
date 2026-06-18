# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/queues.py

Purpose: Tests the netdev generic netlink queue/NAPI APIs against sysfs and ethtool channel changes, including AF_XDP queue annotation.

Important APIs/functions: Uses `NetdevFamily.queue_get`, `napi_get`, `EthtoolFamily.channels_get`, `xdp_helper`, and sysfs `/sys/class/net/<ifname>/queues`. Test functions are `get_queues`, `addremove_queues`, `check_down`, and `check_xsk`.

Control flow: Main creates a `NetDrvEnv` with many queues, then runs queue count comparison, channel decrement/restore, down-state checks, and AF_XDP annotation checks. `check_xsk` first probes AF_XDP support, runs `xdp_helper` bound to queue 0, and validates only queue 0 reports `xsk`.

State and persistence: Mutates channel count with `ethtool -L`, interface up/down state, and creates a temporary AF_XDP socket via helper process. Defers restore link state where needed.

Dependencies and integration: Requires netdev generic netlink queue support, ethtool channels, xdp_helper from net selftests, sysfs queue folders, and root.

Risks: Queue count changes may not be supported or can be disruptive. AF_XDP support probing distinguishes unsupported from helper failure by return code. Queue/NAPI ids disappear when the interface is down, which is expected.

Test signals: PASS means netlink queue counts equal sysfs, queue counts track ethtool channel changes, downed devices return ENOENT for queue/NAPI lookups, and AF_XDP annotation appears only on the configured queue.
