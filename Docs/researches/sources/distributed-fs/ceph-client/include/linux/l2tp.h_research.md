# sources/distributed-fs/ceph-client/include/linux/l2tp.h

Purpose: provides the internal kernel wrapper for L2TP-over-IP socket definitions by including IPv4/IPv6 address headers and the L2TP UAPI.

Important APIs and types: this header does not define new functions or structs; it exposes the UAPI definitions from `<uapi/linux/l2tp.h>` to kernel users with `linux/in.h` and `linux/in6.h` available.

Control flow: L2TP core and socket code include this header when they need tunnel/session constants or socket option definitions.

State and persistence: no state is stored here. Runtime state lives in the L2TP networking subsystem.

Dependencies and integration points: integrates UAPI L2TP definitions with kernel networking address types. It is relevant to L2TPv3 over IPv4/IPv6 socket code.

Risks and test signals: risk is header dependency drift rather than algorithmic behavior. Test by building L2TP IPv4/IPv6 configurations and exercising L2TP tunnel creation via netlink/socket options.
