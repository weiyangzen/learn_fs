# sources/distributed-fs/ceph-client/net/netfilter/xt_HL.c

Purpose: `TTL`/`HL` mangle targets change IPv4 TTL or IPv6 hop-limit by set, increment, or decrement.

Important APIs/types/functions: `ttl_tg()`, `hl_tg6()`, `ttl_tg_check()`, `hl_tg6_check()`, and `csum_replace2()` for IPv4 checksum adjustment.

Control flow: target ensures the header is writable, computes saturated new TTL/hop-limit according to mode, updates header, adjusts IPv4 checksum when needed, and continues.

State and persistence: no module state; modified hop count persists through routing. Dependencies include x_tables, mangle table, IPv4/IPv6 headers, and checksum helpers. Risks: decrement can produce zero, invalid zero inc/dec is rejected only at load, and IPv4 checksum must match TTL update. Test signals: set/inc/dec boundaries, invalid mode/zero operand, write failure, IPv4 checksum delta, and IPv6 hop-limit update.
