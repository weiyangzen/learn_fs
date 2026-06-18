# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_router.sh

Purpose: tests flower `indev` matching on router egress, ensuring a filter on the outgoing router port can match the original ingress interface after routing.

Important functions are `h1_create`, `h2_create`, `h3_create`, `router_create`, and `match_indev_egress_test`. The router has three interfaces, clsact on `$rp3`, and forwarding enabled. Hosts have VRFs and routes so H1 and H2 both send routed traffic to H3 through `$rp3`.

Control flow installs two egress filters on `$rp3`: one matching `indev $rp1`, one matching `indev $rp2`, sends traffic from H1 and H2, and checks that only the filter corresponding to the actual ingress router port increments. State is routes, VRFs, clsact, tc filters, and cached MACs. Risks include offload-only execution: after setup the script calls `tc_offload_check` and only runs tests when offload is available, so software-only environments skip behavior. Test signals are tc counters for handles 101/102 under `skip_sw` and a log entry for indev egress matching.
