# sources/distributed-fs/ceph-client/net/netfilter/xt_connbytes.c

Purpose: `connbytes` match tests conntrack packet counts, byte counts, or average packet size.

Important APIs/types/functions: `connbytes_mt()`, `connbytes_mt_check()`, `connbytes_mt_destroy()`, nf_conntrack accounting APIs, and atomic64 counter reads.

Control flow: check validates mode and direction, pins conntrack, and enables accounting if disabled. Runtime requires conntrack and accounting extension, reads original/reply/both counters, computes average if requested, and applies inclusive or inverted range semantics.

State and persistence: counters live in conntrack accounting; rule holds conntrack ref and may enable accounting namespace-wide. Dependencies include nf_conntrack_acct, x_tables, atomics, and conntrack. Risks: existing flows may lack accounting extension, global accounting side effect, divide-by-zero average behavior, and inverted range semantics. Test signals: packets/bytes/avg, directions, inverted ranges, no conntrack, accounting enable warning, and destroy put.
