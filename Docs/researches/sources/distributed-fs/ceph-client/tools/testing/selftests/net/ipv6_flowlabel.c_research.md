# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel.c

Purpose: Datapath test for IPv6 flowlabel send and receive control messages, including explicit labels, auto flowlabels, ping sockets, and `IPV6_FLOWINFO_SEND`.

Important APIs and types: Uses IPv6 UDP or ICMPv6 datagram sockets, `IPV6_FLOWLABEL_MGR`, `IPV6_FLOWINFO`, `IPV6_FLOWINFO_SEND`, `struct in6_flowlabel_req`, `sendmsg`/`recvmsg` cmsgs, `/proc/sys/net/ipv6/auto_flowlabels`, and optional ping socket sysctls configured by the wrapper.

Control flow: Options select label, ping socket mode, and flowinfo-send mode. The test opens transmit and receive sockets, connects/binds loopback, creates an exclusive flowlabel for a non-any destination, enables flowinfo reception, sends once without an explicit label and validates either no label or wildcard auto label based on sysctl, then sends with the configured label either via cmsg or `sin6_flowinfo` plus `IPV6_FLOWINFO_SEND`, and validates the received cmsg.

State and persistence: Per-socket flowlabel manager state and the global auto-flowlabel sysctl read-only observation. No persistent file writes.

Dependencies and integration: Run inside `in_netns.sh` by `ipv6_flowlabel.sh` with sysctls adjusted for each scenario.

Risks: Ping socket mode uses the same socket for send/receive and skips payload validation. Auto flowlabels are wildcard-checked because the kernel chooses the value.

Test signals: Successful runs prove flowinfo cmsgs are delivered or absent as expected and explicit labels round-trip through send/receive paths.
