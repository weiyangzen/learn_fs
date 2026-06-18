# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/network_helpers.h

Purpose: public interface and inline checksum helpers for network-oriented BPF selftests.

Important APIs/types/functions: defines constants `MAGIC_VAL`, `NUM_ITER`, `VIP_NUM`, and `MAGIC_BYTES`; `struct network_helper_opts`; packed IPv4/IPv6 packet fixtures; prototypes for socket, namespace, TUN/TAP, ethtool, data transfer, TC attach, and traffic monitor helpers. Inline checksum routines are `csum_fold`, `csum_partial`, `build_ip_csum`, `csum_tcpudp_magic`, `csum_ipv6_magic`, `build_udp_v4_csum`, and `build_udp_v6_csum`.

Control flow: header-only inline logic computes simple Internet checksums by accumulating 16-bit words, adding pseudo-header fields, and folding to a `__sum16`. Traffic monitor APIs become no-op inline stubs when `TRAFFIC_MONITOR` is not enabled.

State and persistence behavior: declares exported packet globals and opaque `struct nstoken`/`struct tmonitor_ctx`. No owned state in the header.

Dependencies and integration points: includes Linux packet/IP/TUN/ethtool headers, TCP/UDP headers, libbpf endian helpers, and `net/if.h`. Used broadly by BPF selftests that need stable socket helpers and packet fixtures.

Risks: checksum helpers assume even-length handling suitable for the constructed tests and do not perform full generic checksum validation. `append_tid` reserves a fixed seven-digit field, so very large TIDs or small buffers fail. Stubbed traffic monitor functions silently do nothing when not compiled in.

Test signals: indirect; consumers use helpers to build valid packets, attach TC programs, or orchestrate network namespaces. Compile-time interface mismatches would surface across many selftests.
