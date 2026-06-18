# sources/distributed-fs/ceph-client/net/netfilter/xt_TCPOPTSTRIP.c

Purpose: `TCPOPTSTRIP` target removes selected TCP options by replacing option bytes with NOPs.

Important APIs/types/functions: `tcpoptstrip_mangle_packet()`, `tcpoptstrip_tg4()`, `tcpoptstrip_tg6()`, option length helper, bitmap test helper, and checksum replacement.

Control flow: runtime skips fragments, validates TCP header, ensures option area writable, iterates options with finite progress for malformed zero lengths, replaces selected option bytes with `TCPOPT_NOP`, updates checksum per byte, and continues or drops on malformed/unwritable input.

State and persistence: no module state; TCP option bytes mutate. Dependencies include x_tables, mangle table, TCP parsing, IPv6 extension skipping, and checksum helpers. Risks: malformed option bounds, odd/even checksum replacement, IPv6 parse failure, and fragment handling. Test signals: selected option stripping, unselected no-op, malformed lengths, checksum validation, IPv4/IPv6 paths, fragments, and write failure.
