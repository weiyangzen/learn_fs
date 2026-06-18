# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/stats.py

Purpose: Tests standard netdevice statistics APIs, qstats consistency, pause/FEC statistic availability, and race resilience under procfs reads and interface reconfiguration.

Important APIs/functions: Uses `EthtoolFamily.pause_get/fec_get/channels_get`, `NetdevFamily.qstats_get`, `RtnlFamily.getlink`, `ip`, `cmd`, and ksft helpers. Tests include `check_pause`, `check_fec`, `check_fec_hist`, `pkt_byte_sum`, `qstat_by_ifindex`, disruptive `check_down`, `procfs_hammer`, and `procfs_downup_hammer`.

Control flow: Main creates a high-queue-count `NetDrvEnv` and runs tests. It checks stat presence for devices that support pause/FEC config, compares qstats with RTNL stats monotonicity, validates qstats dumps by ifindex and per-queue key continuity, verifies stats do not regress across ifdown, and hammers `/proc/net/dev` while flipping link/channel state.

State and persistence: Mutates interface up/down state and ethtool channel count in disruptive tests. Spawns background shell loops reading procfs and toggling link/queues, killed via deferred cleanup.

Dependencies and integration: Requires ethtool/netdev/RTNL netlink wrappers, `/proc/net/dev`, ethtool channels, and root. Some tests skip when optional stat families are unsupported.

Risks: Monotonic comparisons allow growth but reject decreases and huge jumps; very active devices could make timing noisy. Procfs hammer is crash/race oriented and may expose driver sleeping-in-RCU bugs rather than deterministic assertion failures.

Test signals: PASS means supported drivers report required stats, qstats and RTNL stats are coherent and monotonic, invalid ifindex errors include expected extack fields, per-queue dumps have contiguous unique ids, and procfs/link churn does not crash or regress counters.
