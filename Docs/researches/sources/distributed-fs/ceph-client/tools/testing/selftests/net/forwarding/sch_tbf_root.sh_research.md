# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_root.sh

Purpose: tests a standalone root TBF qdisc on `$swp2` using the shared TBF topology and measurement helpers. It verifies a single 400 Mbit shaping rate.

Important functions are `tbf_test_one` and `tbf_test`. The script sources `sch_tbf_core.sh`, optionally calls `sch_tbf_pre_hook`, installs `tc qdisc replace dev $swp2 root handle 108: tbf rate 400Mbit burst 128K limit 1M`, defers cleanup, and calls `do_tbf_test 10 400`.

Control flow is inherited setup, wait, ping, `tbf_test`, cleanup. State is the root TBF qdisc plus inherited VLAN/bridge topology, counters, traffic processes, and MTUs. Risks include rate measurement variance, insufficient traffic saturation, and optional pre-hook altering environment. Test signals are successful ping over VLANs and a measured VLAN 10 ingress byte rate within +/-5% of 400 Mbit, logged as `TC 0: TBF rate 400Mbit`.
