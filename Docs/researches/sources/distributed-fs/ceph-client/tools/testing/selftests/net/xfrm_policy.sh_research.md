# sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_policy.sh

Purpose: XFRM policy resolution regression test covering overlapping policy tree merges, direct exceptions, wildcard/dummy policies, hthresh changes, policy lookup stability, and packet matching through an IPsec tunnel.

Important APIs/functions: builds ns1/ns2 hosts and ns3/ns4 IPsec gateways. `do_esp()` and `do_esp_policy()` install ESP states and out/fwd policies. `do_exception()` installs higher-priority direct tunnel and allow-bypass policies. `do_overlap()` creates overlapping block policies to stress inexact policy tree merges. `check_xfrm()` uses ping plus iptables `-m policy` FORWARD counters to detect whether traffic used IPsec. `check_hthresh_repeat()` and `check_random_order()` stress policy hash threshold transitions and insertion ordering.

Control flow: after root/ip/iptables checks, creates topology, configures IPv4/IPv6 addresses/routes/forwarding, installs iptables counters, installs ESP policies/states for both directions/families, adds dummy policies, validates `ip xfrm policy get`, verifies default IPsec match, adds exceptions, rechecks behavior before/after overlap policies, changes hthresh values, flushes/readds policies, tests repeated hthresh updates and random insertion lookup, then cleans namespaces.

State and persistence: temporary namespaces, veths, XFRM policy/state DBs, iptables rules/counters, and routes. No persistent files.

Dependencies and integration: requires root, XFRM/ESP crypto support, iproute2 xfrm, iptables policy match, ping, and `lib.sh`.

Risks: uses random addresses/order for stress, so failures may be intermittent but should expose tree bugs. iptables counter parsing is brittle but direct. Heavy policy insertion can take time.

Test signals: printed PASS/FAIL for policy-before-exception, exception behavior, hthresh changes, repeat updates, and random-order lookup. Final exit status `ret` captures failures.
