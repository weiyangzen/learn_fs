# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_netfilter_ctx.c

## Purpose
This file validates `SEC("netfilter")` BPF context access rules for `struct bpf_nf_ctx`, including valid reads, invalid short/past-end accesses, forbidden writes, and practical skb/state usage.

## Important APIs, Types, And Functions
It uses `struct bpf_nf_ctx`, `struct nf_hook_state`, `struct __sk_buff`, dynptr helpers `bpf_dynptr_from_skb` and `bpf_dynptr_slice`, `bpf_htons`, and local `NF_DROP`/`NF_ACCEPT` constants.

## Control Flow
Naked negative tests read too-small fields, read past the context, or write to context memory. The C test `with_invalid_ctx_access_test5` reads `state` then writes `state->sk`, which must be rejected. The valid test checks skb length, creates a dynptr, slices IP/TCP headers, checks protocol family, and returns accept/drop based on destination port.

## State And Persistence
No state persists beyond helper calls. Verifier state tracks read-only context fields, trusted state pointers, skb dynptr lifetime, packet slice nullability, and return-code bounds.

## Dependencies And Integration Points
It depends on netfilter BPF program support, context metadata, dynptr helper semantics, and network header BTF/layout definitions.

## Risks
Invalid context writes could mutate kernel hook state. Incorrect dynptr or context typing could permit invalid skb access or reject valid netfilter programs.

## Test Signals
Failures assert `invalid bpf_context access` or `only read is supported`; the valid program expects `__retval(0)` and is marked unprivileged failure.
