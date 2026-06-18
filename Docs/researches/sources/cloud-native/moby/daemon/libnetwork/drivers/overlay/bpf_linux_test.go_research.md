# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf_linux_test.go

Purpose: Linux integration test for the VNI-matching cBPF program using raw IPv4 UDP loopback traffic.

Important APIs and functions: `TestVNIMatchBPF` reserves a UDP port, opens a raw IPv4 UDP socket, attaches `vniMatchBPF`, sends VXLAN-like payloads, and verifies only matching VNIs pass. Helpers build VXLAN headers, attach filters, drain sockets, read matching UDP packets, and parse IPv4/UDP headers.

Control flow: skips when raw socket creation returns `EPERM`. For each tested VNI, it sends multiple vector VNIs and compares receipt to equality with the filter VNI.

State and persistence: attaches socket filters to a temporary raw socket only.

Dependencies and integration points: depends on Linux raw sockets, `ipv4.PacketConn.SetBPF`, and BPF helper output from `bpf.go`.

Risks: requires `CAP_NET_RAW`; loopback traffic from unrelated processes is filtered but can add noise. It covers IPv4 raw socket behavior, not iptables xt_bpf or IPv6 directly.

Test signals: strong practical signal that the bytecode selects the expected VXLAN VNI values.
