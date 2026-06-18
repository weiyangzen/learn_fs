# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/sch_tbf_core.sh

Purpose: shared topology and measurement code for TBF shaper tests. It builds two VLAN streams through bridge VLANs and measures received bytes at H2 to validate configured shaping rates.

Important functions are `ipaddr`, `host_create`, `h1_create`, `h2_create`, `switch_create`, `setup_prepare`, `ping_ipv4`, `tbf_get_counter`, `__tbf_test`, and `do_tbf_test`. H2 installs clsact and flower filters for VLAN IDs 10 and 11 so per-stream ingress byte counters can be sampled. The switch creates `br10` and `br11`, VLAN uppers on `$swp1/$swp2`, and priority mappings.

Control flow sets up hosts, VLANs, qdisc counters, and bridges; driver scripts install actual TBF/qdisc hierarchies; `do_tbf_test` starts traffic, waits for burst drain, computes rate over 10 seconds, and requires measured rate within +/-5%. State is qdisc state supplied by drivers, VLAN/bridge topology, counters, MTUs, and background traffic. Risks include rate measurement noise, slow system xfails, and needing sufficient traffic saturation. Test signals are ping reachability and `log_test "TC ... TBF rate ..."` with failure details from `check_err`.
