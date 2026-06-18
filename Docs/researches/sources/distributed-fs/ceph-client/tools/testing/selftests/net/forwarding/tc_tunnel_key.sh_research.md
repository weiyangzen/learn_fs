# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_tunnel_key.sh

Purpose: tests `tc action tunnel_key ... nofrag` on VXLAN external tunnel egress. It verifies packets smaller than MTU are encapsulated and oversized packets are not fragmented when `nofrag` is set, but do fragment when the flag is cleared.

Important functions are `h1_create`, `switch_create`, and `tunnel_key_nofrag_test`. H1 creates external VXLAN `h1-et`, adds clsact, adjusts MTUs so 930-byte inner packets fit and 931-byte packets exceed the tunnel MTU, and checks iproute2 support for `nofrag`.

Control flow installs flower filters on `$swp1` ingress for UDP encapsulated packets with `ip_flags nofrag`, `firstfrag`, and `nofirstfrag`. It adds a matchall egress filter on `h1-et` with tunnel_key set and `nofrag index 10`, sends packets, checks counters, changes the action to remove `nofrag`, sends again, and validates fragmentation counters. State is tunnel device, qdiscs, tc action index 10, MTUs, forwarding, and modified switch-port MACs. Risks include MTU arithmetic, feature support, double spaces in some counter IDs, and cleanup after action mutation. Test signals are exact tc counters for nofrag vs first/non-first fragments.
