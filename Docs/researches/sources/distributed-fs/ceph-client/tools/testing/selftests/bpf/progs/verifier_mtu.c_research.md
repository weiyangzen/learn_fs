# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_mtu.c

## Purpose
This small tc ingress test validates stack initialization behavior around `bpf_check_mtu`.

## Important APIs, Types, And Functions
The main function `tc_uninit_mtu` declares a stack `__u32 mtu`, passes its address to `bpf_check_mtu(ctx, 0, &mtu, 0, 0)`, and returns success. It uses `SEC("tc/ingress")` and unprivileged failure annotation.

## Control Flow
The program gives a helper a pointer to a stack variable intended to be written by the helper. Privileged verification succeeds; unprivileged mode rejects invalid stack reads according to the annotation.

## State And Persistence
There is no persistent state. The verifier tracks stack slot initialization and helper write semantics for the output MTU pointer.

## Dependencies And Integration Points
It depends on tc program context `struct __sk_buff`, `bpf_check_mtu`, and helper argument metadata.

## Risks
Incorrect helper modeling can either expose uninitialized stack data or reject valid helper output-parameter patterns.

## Test Signals
The expected signal is privileged `__success` with unprivileged failure message `invalid read from stack`.
