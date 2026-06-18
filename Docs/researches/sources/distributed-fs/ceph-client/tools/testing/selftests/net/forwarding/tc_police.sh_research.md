# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_police.sh

Purpose: tests tc `police` action for bit-rate, shared policer index, mirroring after policing, packet-rate policing, and MTU policing in ingress and egress directions.

Important functions are `police_common_test`, `police_rx_test`, `police_tx_test`, `police_shared_test`, `police_mirror_common_test`, `police_pps_common_test`, `police_mtu_common_test`, and wrappers for rx/tx variants. Setup creates a three-interface router and three hosts, clsact on router `$rp1/$rp2` and destination hosts H2/H3, and forwarding routes from H1 to H2/H3.

Control flow installs police filters at router ingress or egress, sends continuous mausezahn UDP traffic, samples H2/H3 tc counters for 10 seconds, computes rates with +/-10% tolerance, and validates overlimits for MTU policing. Shared policer tests reuse `index 10` across rx and tx filters. State is tc filters/actions, clsact qdiscs, routes, forwarding, background traffic, and counters. Risks include timing/rate noise, process cleanup via `kill_process %%`, offload variation, and policing semantics for `drop/pipe` plus mirror. Test signals are measured bit rates, packet rates, mirror rates, overlimit counts, and expected conform packet counts.
