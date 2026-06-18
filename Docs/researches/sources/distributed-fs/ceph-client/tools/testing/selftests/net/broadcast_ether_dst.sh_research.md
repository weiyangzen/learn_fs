# sources/distributed-fs/ceph-client/tools/testing/selftests/net/broadcast_ether_dst.sh

Purpose: Ensures IPv4 broadcast packets are emitted with Ethernet destination `ff:ff:ff:ff:ff:ff`.

Important APIs/types/functions: Uses two namespaces with a veth pair, static ARP entry, `tcpdump` capture/readback, broadcast `ping -b`, and `lib.sh` helpers.

Control flow: Setup creates client/server namespaces, configures client IPv4 address and default route through a synthetic gateway MAC. The test starts tcpdump in the client namespace, sends one broadcast ping to `255.255.255.255`, waits for capture, reads Ethernet destination from the pcap, and compares it to the broadcast MAC.

State and persistence behavior: Creates temporary namespaces, veths, temp capture/output files, route and ARP entry. Cleanup removes files, link, and namespaces.

Dependencies and integration points: Requires `tcpdump`, root, ping, veth, and kselftest lib.

Risks: Capture timing uses a 2-second timeout and `slowwait` for tcpdump readiness. Temp filenames are generated with `mktemp -u`, which is race-prone but scoped to test usage.

Test signals: `[ OK ]` indicates captured Ethernet destination matched broadcast MAC.
