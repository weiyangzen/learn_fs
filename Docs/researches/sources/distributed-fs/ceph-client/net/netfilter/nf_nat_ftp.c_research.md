
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_ftp.c

Purpose: NAT helper for FTP control channels. It rewrites PORT/PASV/EPRT/EPSV address and port payloads and sets conntrack expectations for related FTP data channels.

Important APIs and functions: `nf_nat_ftp()` is installed in `nf_nat_ftp_hook`. `nf_nat_ftp_fmt_cmd()` formats replacement payloads for classic IPv4 comma syntax, EPRT IPv4/IPv6, and EPSV. The helper uses `nf_nat_exp_find_port()`, `nf_nat_mangle_tcp_packet()`, and `nf_nat_follow_master()`.

Control flow: Given a parsed FTP command/reply span and expectation, it chooses the address from the packet destination in the opposite direction, saves the expected port, sets expectation direction and follow-master callback, tries to reserve a port, formats the replacement command, rewrites the TCP payload with sequence adjustment, and accepts. On failure it logs, removes the expectation, and drops.

State and persistence: Static NAT helper registration plus the RCU hook pointer. A legacy `ports` module parameter only emits an informational warning.

Dependencies and integration: Depends on FTP conntrack parsing, generic NAT helper payload mangle/seqadj, conntrack expectation handling, and NAT core.

Risks: Risks include replacement size and sequence adjustment correctness, IPv6 EPRT formatting, expectation direction for active/passive modes, helper cleanup on mangle failure, and preserving compatibility with legacy module parameters. Test signals include active FTP PORT, passive PASV/EPSV, EPRT for IPv4/IPv6, altered port allocation, checksum/seqadj validation, and unload under traffic.
