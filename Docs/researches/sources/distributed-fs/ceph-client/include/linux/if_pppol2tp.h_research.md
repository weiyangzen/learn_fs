# `sources/distributed-fs/ceph-client/include/linux/if_pppol2tp.h`

Purpose: PPP over L2TP kernel include wrapper that supplies IPv4/IPv6 address types and UAPI PPPoL2TP socket definitions to the L2TP PPP driver.

Important APIs/types/functions: no new structs or functions beyond including `linux/in.h`, `linux/in6.h`, and UAPI `if_pppol2tp.h`.

Control flow and state: none in this header.

Dependencies/integration: used by `l2tp_ppp.c` and PPPoL2TP socket code that needs both kernel IP types and user-facing sockaddr definitions.

Risks: include-order and ABI compatibility with UAPI structures; functionality lives in PPP/L2TP implementation files.

Test signals: PPPoL2TP socket build, IPv4/IPv6 tunnel setup, and UAPI sockaddr compatibility tests.
