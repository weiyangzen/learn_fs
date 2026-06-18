# sources/distributed-fs/openafs/src/WINNT/afsd/krb_prot.h

Purpose: defines Kerberos v4 wire-protocol constants and packet-field access macros used by the legacy Kerberos compatibility header.

Important APIs/types/functions: constants include `KRB_PORT`, `KRB_PROT_VERSION`, `MAX_PKT_LEN`, `MAX_TXT_LEN`, and `TICKET_GRANTING_TICKET`. Macros such as `pkt_version`, `pkt_msg_type`, `pkt_a_name`, `pkt_a_inst`, `pkt_a_realm`, `pkt_time_ws`, `pkt_no_req`, `pkt_x_date`, `pkt_err_code`, and `pkt_err_text` compute offsets inside a `KTEXT` packet. It declares legacy packet constructors/readers `create_auth_reply`, `create_death_packet`, and `pkt_cipher`, and defines Kerberos v4 message and error constants.

Control flow: no direct control flow. Consumers use pointer arithmetic macros to walk variable-length NUL-terminated fields inside a Kerberos v4 packet.

State/persistence: no state. It defines fixed packet layouts and message type values that must match the v4 wire protocol.

Dependencies/integration: expects `KTEXT` from `krb.h` and standard C string semantics. It is part of OpenAFS's Windows compatibility layer for old Kerberos/AFS token handling.

Risks: macros perform unchecked pointer arithmetic and `strlen` over packet data, so malformed or unterminated packets can read outside packet bounds if callers do not validate first. Function declarations omit prototypes/return types in old C style. The protocol itself is obsolete and should not be expanded.

Test signals: fuzz or negative-test packet parsing callers with truncated and unterminated packets, and compile under strict prototype warnings.
