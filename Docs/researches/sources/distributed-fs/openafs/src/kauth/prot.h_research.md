## sources/distributed-fs/openafs/src/kauth/prot.h

Purpose: `prot.h` defines Kerberos v4 protocol constants, packet field macros, default ports, maximum packet/text lengths, message type values, and public Kerberos error codes used by kauth UDP compatibility code.

Important types and macros: it defines `KRB_PORT` 750, `KRB5_PORT` 88, `KRB_PROT_VERSION` 4, `MAX_PKT_LEN`/`MAX_TXT_LEN` 1000, and packet access macros such as `pkt_version`, `pkt_msg_type`, `pkt_a_name`, `pkt_a_inst`, `pkt_a_realm`, `pkt_time_ws`, `pkt_x_date`, `pkt_err_code`, and `pkt_err_text`. Message constants leave the low bit for byte order. Error constants range from `KERB_ERR_OK` to `KERB_ERR_NULL_KEY`, with `KERB_ERR_MAXIMUM` set to 10.

Control flow and integration: this header has no runtime control flow, but it is central to `krb_udp.c` and `user_nt.c` packet construction/parsing. The macros encode wire layout assumptions directly as pointer offsets based on null-terminated strings.

State and persistence: none.

Dependencies: no external includes beyond its guard, but callers must provide packet-like objects with a `dat` member for the macros.

Risks: macros do not perform bounds checking and use repeated `strlen` on packet contents. Any caller must validate packet length before using them on untrusted network data. Operator precedence in message constants relies on C precedence of shift vs bitwise operations; current usage is consistent but not self-documenting.

Test signals: packet layout is indirectly exercised by UDP authentication tests and by the Windows client-side implementation in `user_nt.c`, which uses these constants/macros to parse replies.
