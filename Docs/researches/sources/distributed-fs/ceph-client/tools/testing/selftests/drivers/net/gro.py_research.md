# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/gro.py

Purpose: Python kselftest driver for Generic Receive Offload conformance across software GRO, hardware GRO, and LRO modes, with protocol correctness and capacity coverage.

Important APIs/functions: `NetDrvEpEnv`, `NetdevFamily`, `EthtoolFamily`, `ksft_variants`, `KsftNamedVariant`, `_resolve_dmac()`, `_write_defer_restore()`, `_set_mtu_restore()`, `_set_ethtool_feat()`, `_get_queue_stats()`, `_setup_isolated_queue()`, `_setup_queue_count()`, `_run_gro_bin()`, `_setup()`, `_gro_variants()`, `test()`, `_capacity_variants()`, `test_gro_capacity()`, and `main()`.

Control flow: `main()` creates a local/remote endpoint environment, attaches Netlink families, and runs variant-expanded tests. `_setup()` toggles ethtool features for `sw`, `hw`, or `lro`, adjusts MTU for large tests, and may install generic XDP as a workaround when HW GRO is coupled to SW GRO. `_run_gro_bin()` deploys/runs the compiled `gro` helper as RX locally and TX remotely. Protocol variants cover IPv4, IPv6, IP-in-IP, and IPv6-in-IPv6 with many coalescing/non-coalescing cases. Capacity variants isolate or resize queues and grow flow counts while parsing `STATS` output and queue stats.

State and persistence: Mutates sysfs GRO defer settings, MTU, ethtool features, RSS weights, ntuple filters, channel counts, XDP attachment, and deployed remote helper binaries. Cleanup uses `defer()`.

Dependencies and integration points: Requires net selftest Python library, compiled `gro` helper, ethtool Netlink, netdev qstats, remote endpoint, offload support, RSS/ntuple/channel features for capacity variants, and optional netdevsim handling.

Risks and test signals: Timing/coalescing is flaky, so main tests retry six times. Failures identify GRO protocol correctness, HW feature toggling, qstats reporting, queue steering, or capacity regressions.
