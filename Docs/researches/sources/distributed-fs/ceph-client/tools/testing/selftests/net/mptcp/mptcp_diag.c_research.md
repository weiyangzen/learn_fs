# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_diag.c

## Purpose
`mptcp_diag.c` is a diagnostic helper that queries Linux sock_diag netlink for MPTCP socket information by token or TCP subflow tuple and prints selected MPTCP info/subflow attributes.

## Important APIs and Functions
`parse_opts` accepts `-t <token>` and `-s "<saddr>:<sport> <daddr>:<dport>"`. `get_mptcpinfo` builds an `inet_diag_req_v2` for an MPTCP token, requesting `INET_DIAG_INFO` and passing `INET_DIAG_REQ_PROTOCOL=IPPROTO_MPTCP`. `get_subflow_info` parses an IPv4 TCP tuple and requests TCP diag/ULP info. Netlink helpers include `send_query`, `recv_nlmsg`, `parse_rtattr_flags`, `parse_nlmsg`, `print_info_msg`, and `print_subflow_info`.

## Control Flow and State
The program opens a `NETLINK_SOCK_DIAG` socket, sends one query for each requested mode, receives netlink responses, parses rtattrs, and prints human-readable fields. For older kernels with shorter `mptcp_info`, `parse_nlmsg` copies payload into a zero-filled full struct. State is process-local query parameters and receive buffers.

## Dependencies and Integration
It depends on Linux inet_diag/sock_diag UAPI, MPTCP diag kernel support, and IPv4 tuple parsing for subflow mode. `diag.sh` compares its token and subflow output against `ss`.

## Risks and Test Signals
Subflow mode only parses IPv4-style `addr:port` pairs with `sscanf`, so IPv6 subflows are outside this helper's current path. Netlink errors are printed but not deeply classified. Useful signals are printed `token:`, flags, checksum, sequence/counter fields, and subflow `token:` data matching `ss`.
