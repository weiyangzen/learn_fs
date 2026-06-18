# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_actions.sh

Purpose: broad tc action coverage for flower/matchall classifiers, including `gact`, `mirred`, `trap`, connection tracking/NAT with egress-to-ingress redirect, and VLAN push chains. It runs once in software (`skip_hw`) and again in hardware-offload mode (`skip_sw`) when available.

Important functions are `mirred_egress_test`, `gact_drop_and_ok_test`, `gact_trap_test`, `mirred_egress_to_ingress_test`, `mirred_egress_to_ingress_tcp_test`, `ingress_2nd_vlan_push`, and `egress_2nd_vlan_push`. It requires `ncat`, sources `tc_common.sh`, and manipulates MAC addresses on switch ports so redirected frames are accepted by hosts.

Control flow creates two host VRFs and two switch-facing simple interfaces with clsact, installs filters, generates packets with `$MZ` or `ncat`, checks counters, deletes filters, then repeats after `tc_offload_check`. State is tc filters/actions, temporary sparse files for TCP test, conntrack NAT state, qdiscs, and modified port MACs. Risks include offload support variance, temp-file cleanup, NAT/ct module availability, and exact counter timing. Test signals are tc rule counters, `cmp` of TCP payload, expected drop/pass behavior, and double-VLAN chain matches.
