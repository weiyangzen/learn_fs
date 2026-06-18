# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/xsk.c

## Purpose

AF_XDP namespace test harness. It creates a veth pair, configures TX/RX interface objects, initializes packet streams and UMEM parameters, and runs each `test_xsk` scenario in SKB and DRV modes. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`setup_veth()`, `delete_veth()`, `configure_ifobj()`, `ifobject_create/delete()`, `init_iface()`, `test_init()`, `pkt_stream_generate/delete/restore_default()`, hardware ring-size helpers, procfs reads for cacheline/max frags, and `xsk_xdp_progs` skeleton cleanup.

## Control Flow

`test_ns_xsk_skb()` and `test_ns_xsk_drv()` create veths, iterate the global `tests[]` table, and call `test_xsk()` per subtest. `test_xsk()` creates ifobjects, populates ifindexes and tailroom, initializes RX/TX interfaces, creates default packet streams, runs the selected test function in the requested mode, restores defaults and hardware ring sizes, then destroys resources.

## State and Persistence Behavior

Transient veth pair, optional busy-poll sysfs values, ifobject/UMEM/socket state managed by the shared XSK helpers, packet streams, and XDP skeletons. `delete_veth()` removes interfaces after each mode suite.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It depends heavily on `test_xsk.h` shared helpers, AF_XDP, veth, procfs/sysfs tunables, and optional ethtool ring-size support.

## Risks and Edge Cases

Many behaviors are delegated to shared XSK helpers. Hardware ring-size and busy-poll support are environment-dependent. Cleanup must reset ring size when supported and delete both veth names.

## Test Signals

Each `tests[]` entry either returns `TEST_SKIP` or `0`; assertion coverage includes veth setup, ifobject initialization, packet stream generation, and cleanup without leaked XDP programs.
