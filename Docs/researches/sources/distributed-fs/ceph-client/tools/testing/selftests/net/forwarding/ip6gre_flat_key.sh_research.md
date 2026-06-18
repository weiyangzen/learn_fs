
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_flat_key.sh

Purpose: Flat IPv6-underlay GRE tunnel selftest with a shared GRE `key 233`. It confirms keyed tunnel lookup still forwards IPv4 and IPv6 payloads and survives MTU and endpoint changes.

Important APIs/functions: same driver shape as `ip6gre_flat.sh`, but `setup_prepare` calls `sw1_flat_create $ol1 $ul1 key 233` and `sw2_flat_create $ol2 $ul2 key 233`. Test functions are `gre_flat`, `gre_mtu_change`, and `gre_flat_remote_change`.

Control flow: after interface assignment and common VRF/forwarding setup, both tunnel endpoints are created with identical input/output keys. The traffic tests use `test_traffic_ip4ip6` and `test_traffic_ip6ip6`; remote-change temporarily rewrites local/remote tunnel addresses and routing through `flat_remote_change`/`flat_remote_restore`.

State/persistence: creates keyed `ip6gre` devices, VLAN underlay links, overlay routes, and temporary tc counters. Global sysctls and route rules are saved/restored by `lib.sh` helpers.

Dependencies/integration: depends on `ip6gre_lib.sh` supporting opaque extra tunnel arguments and on kernel keyed GRE-over-IPv6 behavior. Uses `tests_run` from kselftest forwarding `lib.sh`.

Risks: asymmetric or missing key support in hardware/software paths can blackhole traffic while unkeyed variants pass. Counter timing and neighbor state remain shared risks with the flat base test.

Test signals: both IPv4-in-IPv6 and IPv6-in-IPv6 packet counters must increment with keyed tunnel devices before and after endpoint changes; MTU test must fail before and pass after raising topology MTUs.
