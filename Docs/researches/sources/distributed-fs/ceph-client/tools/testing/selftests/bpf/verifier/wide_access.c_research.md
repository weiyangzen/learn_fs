# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/wide_access.c

## Purpose

This verifier fixture checks 64-bit loads and stores against `struct bpf_sock_addr` IPv6 address fields. It ensures that aligned doubleword accesses are accepted and misaligned or out-of-range context accesses are rejected with precise offsets.

## Important APIs, Types, and Functions

The file defines two table-entry generator macros: `BPF_SOCK_ADDR_STORE(field, off, res, err, flgs)` and `BPF_SOCK_ADDR_LOAD(field, off, res, err, flgs)`. Generated programs use `BPF_STX_MEM(BPF_DW, ...)` or `BPF_LDX_MEM(BPF_DW, ...)` against `offsetof(struct bpf_sock_addr, field[off])`. Metadata targets `BPF_PROG_TYPE_CGROUP_SOCK_ADDR` with `BPF_CGROUP_UDP6_SENDMSG`, optional `F_NEEDS_EFFICIENT_UNALIGNED_ACCESS`, and expected error strings.

## Control Flow

The harness expands the macros into store and load cases for `user_ip6[]` and `msg_src_ip6[]`. Each program performs one context access and exits. The verifier checks the context offset/size alignment and field accessibility before accepting or rejecting.

## State and Persistence Behavior

The fixture owns no runtime state. The tested state is the verifier's context-access model for `bpf_sock_addr` field layout and architecture unaligned-access policy.

## Dependencies and Integration Points

It depends on UAPI layout for `struct bpf_sock_addr`, BPF context access validation, cgroup sock_addr attach semantics, and the verifier selftest error-matching harness.

## Risks and Test Signals

Risks include ABI layout changes, architecture-specific unaligned rules, and stale expected offset strings. Signals are acceptances for aligned slots and rejections at offsets 12, 20, 44, 52, and 56 according to the field/element combination.
