<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bpf.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bpf.h

## Purpose
`nf_conntrack_bpf.h` declares BTF/BPF registration hooks that expose conntrack and NAT kernel functions/types to BPF when supported.

## Important APIs, types, and functions
It defines wrapper `struct nf_conn___init` and conditional `register_nf_conntrack_bpf`, `cleanup_nf_conntrack_bpf`, and `register_nf_nat_bpf` declarations or no-op stubs.

## Control flow
Conntrack/NAT module init paths register BPF kfunc/type metadata only when the module or built-in configuration also has the required BTF debug info.

## State and persistence
Registration state is in BPF/kfunc implementation; the header has no state.

## Dependencies and integration points
It depends on Kconfig predicates, conntrack, NAT, BTF debug info, and BPF syscall support. It integrates conntrack/NAT with BPF programs.

## Risks and test signals
Risks include configuration matrix mistakes, module-vs-built-in BTF differences, and callers assuming registration happened. Tests should build builtin/module/no-BTF combinations and load BPF programs using conntrack kfuncs.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bpf.h` completely for this pass (46 lines, 899 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_bpf.h -->
