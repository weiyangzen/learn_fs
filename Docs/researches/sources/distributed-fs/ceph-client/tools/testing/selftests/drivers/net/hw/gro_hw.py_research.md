# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/gro_hw.py

Purpose: Hardware GRO selftest focused on device machinery, queue stats, and ordering rather than full protocol conformance.

Important APIs/functions: `NetDrvEpEnv`, `NetdevFamily`, `_get_queue_stats()`, `_resolve_dmac()`, `_setup_isolated_queue()`, `_run_gro_test()`, `_require_hw_gro_stats()`, `_set_ethtool_feat()`, `_setup_hw_gro()`, `_check_gro_stats()`, `test_gro_stats_single()`, `test_gro_stats_full()`, variant `test_gro_order()`, and `ksft_run`.

Control flow: Setup enables HW GRO while disabling SW GRO/LRO, possibly attaching generic XDP if the driver couples features. Tests isolate queue 1 with RSS weights and ntuple steering, require qstats fields, run the `gro` helper, and compare qstats deltas against expected RX/GRO/wire-packet counts. Ordering variants send increasing flow counts with order checking.

State and persistence: Mutates ethtool features, RSS context, ntuple filters, and optional XDP program, restored through `defer()`.

Dependencies and integration points: Requires HW GRO support, netdev queue stats including `rx-hw-gro-*`, compiled `gro` helper, remote endpoint, and ntuple/RSS control.

Risks and test signals: Failures indicate qstats inaccuracies, HW GRO counter semantics, ordering problems, or feature toggling regressions.
