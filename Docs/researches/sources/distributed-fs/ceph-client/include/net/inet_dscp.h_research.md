# sources/distributed-fs/ceph-client/include/net/inet_dscp.h

Purpose: defines a bitwise-distinct DSCP type and helpers for converting between IP DS fields and DSCP values.

Important APIs/types: `typedef u8 __bitwise dscp_t` prevents accidental mixing with raw bytes. `INET_DSCP_MASK` selects the upper six DS bits, while `INET_ECN_MASK` is provided externally in IP ECN headers. `INET_DSCP_LEGACY_TOS_MASK` covers legacy TOS precedence-style bits. `inet_dsfield_to_dscp()` masks a DS field into a DSCP, `inet_dscp_to_dsfield()` converts back to a byte with ECN cleared, and `inet_validate_dscp()` checks raw values.

Control flow and state: callers convert TOS/traffic-class values when storing flow keys or socket DSCP fields. There is no persistent state.

Dependencies and integration: depends on Linux types and is included by `flow.h`, `ip.h`, `inet_sock.h`, and QoS mapping code. It integrates with route lookup, socket TOS settings, tc classifiers, and ECN helpers.

Risks: DSCP and ECN bits share the same octet; callers must avoid losing ECN when only DSCP should change. Tests should cover all DSCP ranges, ECN-preserving callers, invalid raw values, bitwise type warnings, and flow/socket DSCP propagation.
