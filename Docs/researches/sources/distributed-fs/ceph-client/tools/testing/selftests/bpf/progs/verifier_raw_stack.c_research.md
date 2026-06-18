# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_raw_stack.c

## Purpose
This file validates raw stack initialization and bounds rules around `bpf_skb_load_bytes`, including helper writes into stack memory and later reads from those bytes.

## Important APIs, Types, And Functions
It uses socket and tc sections, `bpf_skb_load_bytes`, stack pointers derived from `r10`, and annotations for strict/unprivileged behavior.

## Control Flow
Tests cover reading stack without helper initialization, negative/zero/unbounded lengths, helper-initialized reads, initialized stack before helper calls, spilled register corruption around helper writes, invalid stack destination offsets, and large but bounded stack writes.

## State And Persistence
No durable state exists. Verifier state tracks stack byte initialization, spilled register metadata versus raw data, helper write ranges, and stack bounds relative to the 512-byte BPF stack.

## Dependencies And Integration Points
It depends on tc skb helper metadata and verifier stack-state modeling. It is a regression suite for helper functions that initialize stack memory.

## Risks
A helper write that fails to clear spilled-register metadata can create type confusion. Weak length/bounds checks can allow writes outside the BPF stack or reads from uninitialized memory.

## Test Signals
Expected signals include success for valid helper-initialized reads and failures such as `R4 min value is negative`, `invalid zero-sized read`, `invalid write to stack`, unbounded memory access guidance, and scalar invalid memory access.
