
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_flower.sh

Purpose: Tests flower ACL-triggered mirroring to gretap/ip6gretap rather than matchall mirroring.

Important APIs/functions: `test_span_gre_dir_acl`, `fail_test_span_gre_dir_acl`, `full_test_span_gre_dir_acl`, `test_gretap`, `test_ip6gretap`.

Control flow: standard GRE topology plus secondary IPv4 addresses on H1/H2. Installs a mirror on `$swp1` with `protocol ip flower dst_ip <match>`, verifies default H1/H2 traffic is not mirrored, verifies traffic to the matched secondary address is mirrored, then uninstalls and verifies mirroring stops.

State/persistence: adds secondary host addresses, underlay addresses, tc flower mirror filters, and capture filters on H3 tunnel endpoints.

Dependencies/integration: depends on `tc flower dst_ip` matching, mirror helper libraries, and MZ-generated ICMP.

Risks: the test only matches IPv4 ACLs even for ip6gretap transport; this is intentional because payload is IPv4. Address overlap with baseline topology must be cleaned up.

Test signals: zero counters for unmatched traffic, positive counters for matched secondary-address traffic, and zero counters after mirror uninstall.
