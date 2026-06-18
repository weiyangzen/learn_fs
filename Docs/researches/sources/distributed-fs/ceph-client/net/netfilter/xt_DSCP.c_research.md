# sources/distributed-fs/ceph-client/net/netfilter/xt_DSCP.c

Purpose: mangle-table DSCP/TOS target modifies IPv4 DS field and IPv6 traffic class.

Important APIs/types/functions: `dscp_tg()`, `dscp_tg6()`, `tos_tg()`, `tos_tg6()`, `dscp_tg_check()`, and DS field helpers.

Control flow: runtime compares current field to desired result, makes the network header writable, updates DSCP preserving ECN for DSCP mode or applies TOS mask/xor semantics, then continues or drops on write failure.

State and persistence: no module state; packet header changes persist. Dependencies include x_tables, mangle table, IPv4/IPv6 DS helpers, and skb writability. Risks: write failures drop, ECN preservation differs by mode, and IPv6 write-size assumptions deserve coverage. Test signals: DSCP bound check, unchanged fast path, IPv4 checksum update, IPv6 traffic class update, TOS masks, and cloned skb write failure.
