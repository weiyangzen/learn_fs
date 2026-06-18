# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_iptunnel_common.h

## Research

This header defines shared constants, protocol structures, and map declarations for BPF IP tunnel selftests. It is included by BPF programs and/or user-space harness code that need common tunnel metadata layout.

The central types are `struct geneve_opt`, `struct vxlan_metadata`, and `struct bpf_fou_encap`, which model tunnel option and encapsulation metadata. The header defines tunnel port constants for VXLAN, GENEVE, FOU, and GUE, plus `PROTO_IPIP` and `PROTO_IPV6`. It also declares BPF maps using libbpf-style SEC annotations: `rxcnt` as a one-entry array of packet counters, `vip2tnl` as a hash from a virtual IP key to tunnel endpoint data, and `jmp_table` as a program array with two entries for tail calls or dispatch.

Control flow is absent; map definitions become ELF map metadata at compile time. Runtime state is the kernel map content once a BPF object using this header is loaded. The maps integrate with selftest loaders that populate tunnel endpoint data, read packet counters, and attach/dispatch programs through the program array.

Dependencies include BPF helper headers, `struct vip`, `struct iptnl_info`, `struct geneve_opt`, and `struct bpf_fou_encap` consumers matching the same ABI layout. Risks are structure layout drift, endian/packing assumptions for tunnel metadata, and mismatched `max_entries` or key/value sizes between BPF programs and user-space tests. Test signals are successful object load, successful map population, tail-call behavior through `jmp_table`, and expected RX counter updates after tunnel traffic.
