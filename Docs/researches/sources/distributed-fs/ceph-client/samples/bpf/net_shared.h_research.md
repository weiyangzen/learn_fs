# sources/distributed-fs/ceph-client/samples/bpf/net_shared.h

Purpose: provides small network protocol constants and byte-order helpers for BPF samples without pulling full userspace/kernel networking headers.

Important APIs/types/functions: defines address families, Ethernet protocol values, VLAN/MPLS-related constants, ICMPv6 protocol number, tc action codes, `IFNAMSIZ`, and `bpf_ntohs`/`bpf_htons` endian macros.

Control flow: no runtime flow; compile-time constants and macros only.

State and persistence: no state.

Dependencies and integration: included by networking BPF samples that need stable constants across kernel and userspace compile modes.

Risks: constants can become stale relative to kernel headers. Byte-order macros depend on `__BYTE_ORDER__` and only cover 16-bit conversions.

Test signals: networking samples compile without conflicting header definitions and protocol comparisons match expected packet types.
