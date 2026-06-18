
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_irc.c

Purpose: NAT helper for IRC DCC messages. It rewrites embedded IPv4 address and port text in IRC control traffic and sets expectations for related DCC connections.

Important APIs and functions: `help()` is installed via `nf_nat_irc_hook`, uses `nf_nat_exp_find_port()`, formats `"<addr_as_u32> <port>"`, calls `nf_nat_mangle_tcp_packet()`, and sets `nf_nat_follow_master()` as the expectation callback.

Control flow: The helper uses the reply-direction destination address as the externally visible address, saves the expected TCP port, forces expectation direction to reply, reserves a port, rewrites the matched DCC payload span, and accepts. On port or mangle failure it logs, unexpects if needed, and drops.

State and persistence: Static NAT helper registration, RCU hook pointer, and a warning-only legacy `ports` module parameter. Expectations live in conntrack.

Dependencies and integration: Depends on IRC conntrack parser, TCP payload mangle/seqadj helper, conntrack expectations, and NAT core.

Risks: The helper only handles IPv4 numeric DCC address syntax, so parser/helper alignment is important. Other risks are payload buffer sizing, sequence adjustment after replacement, expectation direction, and RCU hook teardown. Test signals include DCC CHAT/SEND variants, changed port allocation, port exhaustion, checksum/seqadj validation, and module unload while parser references the hook.
