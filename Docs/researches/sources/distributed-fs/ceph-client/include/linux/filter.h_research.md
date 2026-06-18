# sources/distributed-fs/ceph-client/include/linux/filter.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/filter.h` is a major kernel BPF/socket-filter interface header. It defines eBPF register aliases, instruction constructors, classic BPF conversion helpers, BPF runtime/JIT allocation and kallsyms interfaces, socket filter attachment APIs, SKB/XDP context helpers, redirect state, and SK_LOOKUP execution helpers. The source was read as a complete 1886-line file for this report.

## Important APIs, Types, and Functions

Important macros include BPF register aliases, internal opcodes such as `BPF_TAIL_CALL`, `BPF_PROBE_MEM*`, `BPF_NOSPEC`, instruction builders such as `BPF_ALU64_REG`, `BPF_MOV64_IMM`, `BPF_LD_IMM64`, `BPF_LDX_MEM`, `BPF_STX_MEM`, `BPF_ATOMIC_OP`, `BPF_JMP_*`, `BPF_CALL_REL`, `BPF_EMIT_CALL`, `BPF_CALL_KFUNC`, `BPF_EXIT_INSN`, BPF helper declaration macros `BPF_CALL_0` through `BPF_CALL_5`, and context-range macros. Important types include `struct compat_sock_fprog`, `struct sock_fprog_kern`, `struct bpf_binary_header`, `struct bpf_prog_stats`, `struct sk_filter`, `struct bpf_redirect_info`, `struct bpf_net_context`, `struct bpf_sock_addr_kern`, `struct bpf_sock_ops_kern`, `struct bpf_sysctl_kern`, `struct bpf_sockopt_kern`, and `struct bpf_sk_lookup_kern`. Key APIs include `bpf_prog_run`, `bpf_prog_run_pin_on_cpu`, `bpf_compute_data_pointers`, `bpf_prog_run_save_cb`, `sk_filter`, BPF program allocation/free/create/destroy APIs, socket attach/detach APIs, JIT runtime helpers, XDP redirect helpers, SK_LOOKUP runners, and packet load/store helpers.

## Control Flow

BPF programs are created from classic or eBPF instructions, verified/selected for interpreter or JIT runtime, optionally made read-only/executable, then run through dispatcher functions with migration constraints and optional stats accounting. SKB execution saves or clears `skb->cb` as needed, computes `data_meta` and `data_end`, and restores prior control-buffer state. XDP and redirect helpers store per-task redirect state in `current->bpf_net_context`, then flush devmap/cpumap/xskmap lists in matching CPU context. SK_LOOKUP macros iterate program arrays under RCU and aggregate selected sockets/drop decisions.

## State and Persistence Behavior

State includes refcounted `sk_filter` objects, `bpf_prog` memory and stats, JIT binary headers, per-task `bpf_net_context`, per-packet skb control-buffer overlays, redirect metadata, and socket lookup context. JIT code may be exposed through kallsyms depending on hardening and sysctl state.

## Dependencies and Integration Points

The header depends on BPF UAPI, networking/skbuff, workqueues, scheduler clocks, set_memory, kallsyms, VLAN, sockptr, u64 stats, and qdisc internals. It integrates with socket filters, seccomp/classic BPF conversion, verifier, BPF syscall, BPF JIT back ends, netfilter BTF access, tc, XDP, reuseport, cgroup sockopt/sysctl hooks, and inet/IPv6 socket lookup.

## Risks and Edge Cases

This header sits on hot and security-sensitive paths. Risks include instruction encoding drift, verifier/JIT disagreement, missing zero-extension or speculation barriers, unsafe skb cb leakage to unprivileged programs, per-task redirect state not initialized before use, JIT hardening/kallsyms exposure mistakes, and CPU-context mismatches between redirect and flush.

## Test Signals

BPF selftests for instruction encoding, verifier/JIT parity, socket filters, reuseport, SK_LOOKUP, cgroup sockopt/sysctl, XDP redirects, JIT hardening/kallsyms sysctls, classic-to-eBPF migration, skb cb access, packet load/store helpers, and CONFIG_BPF_JIT/CONFIG_BPF_SYSCALL disabled builds.
