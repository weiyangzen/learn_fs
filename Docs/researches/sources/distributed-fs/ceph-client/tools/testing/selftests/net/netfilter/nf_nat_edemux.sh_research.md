## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nf_nat_edemux.sh

Purpose: tests NAT source-port clash resolution and early demux behavior when local port range is constrained and multiple redirected connections target the same backend service.

Important APIs and tools: requires `socat`, `iptables`, `conntrack`, namespace helpers, `ip_local_port_range`, DNAT in OUTPUT, REDIRECT in PREROUTING, `ss`, and `conntrack --get`.

Control flow: creates two namespaces on one subnet, starts a TCP server in ns1, restricts ns2 ephemeral ports to exactly 10000, adds ns2 OUTPUT DNAT from virtual 10.96.0.1:443 to ns1:5201, and opens a persistent direct connection consuming source port 10000. It then connects to the DNAT address, expecting NAT to reallocate source port rather than fail. Next it adds ns1 PREROUTING redirects from ports 5202 and 5203 to 5201, opens two simultaneous connections, waits for them established, and validates conntrack entries for both original destination ports.

State and persistence: temporary namespaces, iptables NAT rules, conntrack entries, socat processes; cleanup kills server and deletes namespaces. Dependencies include NAT clash handling and conntrack CLI. Risks include fixed port range affecting namespace only, timing around established detection, and process cleanup if connection setup fails. Test signals are PASS/FAIL lines and final `ret`.
