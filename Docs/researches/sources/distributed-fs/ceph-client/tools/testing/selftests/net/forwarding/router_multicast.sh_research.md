# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_multicast.sh

Purpose: tests IPv4/IPv6 multicast routing, reverse path forwarding enforcement, and unresolved multicast route queueing with userspace multicast daemon integration.

Important functions are `create_mcast_sg`, `delete_mcast_sg`, `mcast_v4`, `mcast_v6`, `rpf_v4`, `rpf_v6`, `unres_v4`, and `unres_v6`. Setup calls `adf_mcd_start`, creates three host VRFs with routes, router interfaces `$rp1-$rp3`, ingress qdiscs on hosts and `$rp3`, and enables forwarding. `mc_cli` adds/removes `(S,G)` or `(*,G)` multicast routes.

Control flow installs tc flower counters/drops, emits multicast packets with proper L2 multicast destinations via `$MZ`, checks receiver counters, deletes routes and verifies no further delivery, tests wrong-ingress RPF drops/traps, and tests unresolved queue notifications that cause userspace route installation. State is multicast daemon state, kernel multicast forwarding cache, VRFs, routes, tc filters, and forwarding. Risks include daemon startup, route convergence, skip/offload behavior, and timing around unresolved queue processing. Test signals are exact tc packet counts on H2/H3 and `$rp3`, plus `log_test` entries for multicast delivery, RPF, and unresolved queue behavior.
