
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/mirror_gre_lib.sh

Purpose: GRE-specific mirror assertion library layered on `mirror_lib.sh`. It standardizes tests against H3-side `h3-<tundev>` decapsulation devices.

Important APIs/functions: `quick_test_span_gre_dir_ips`, `fail_test_span_gre_dir_ips`, `test_span_gre_dir_ips`, `full_test_span_gre_dir_ips`, `full_test_span_gre_dir_vlan_ips`, `quick_test_span_gre_dir`, `fail_test_span_gre_dir`, `full_test_span_gre_dir`, `full_test_span_gre_dir_vlan`, `full_test_span_gre_stp_ips`, `full_test_span_gre_stp`.

Control flow: helpers install mirrors on `$swp1`, call generic span direction tests against `h3-$tundev`, optionally install VLAN capture filters on `$h3`, exercise traffic, uninstall mirrors, and log test names.

State/persistence: creates/removes tc mirror filters and capture filters; STP helper temporarily changes bridge port state disabled/forwarding.

Dependencies/integration: sources `mirror_lib.sh` via `$net_forwarding_dir`, expects globals `$swp1`, `$h1`, `$h2`, `$h3`, and tunnel names from topology scripts.

Risks: helpers assume mirror source is `$swp1` and H3 tunnel device naming convention `h3-<tundev>`. STP tests use sleeps and can be timing-sensitive.

Test signals: packet counter expectations from generic mirror helpers, VLAN capture counter expectations, and fail/pass transitions around STP state changes.
