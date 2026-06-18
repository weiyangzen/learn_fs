# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_reg_equal.c

## Purpose
This file tests when equality/range information from 32-bit subregister operations may be propagated to full 64-bit registers.

## Important APIs, Types, And Functions
It has two socket naked programs using `bpf_ktime_get_ns`, stack spill/reload, `w3 = w2`, and conditional branches.

## Control Flow
The first test stores a helper result to stack and reloads only 32 bits, proving the upper half of `r2` is zero; a `w2 < 9` comparison can safely refine `r3`. The second copies a full 64-bit helper result into `r2`, so `w3 = w2` must not imply full-register equality; an illegal `r1` read remains reachable.

## State And Persistence
No persistent state exists. Verifier state tracks subregister definitions, upper-32 zero knowledge, register IDs, and branch range propagation.

## Dependencies And Integration Points
It integrates with verifier scalar equality and subregister tracking.

## Risks
Incorrect full-register equality from 32-bit operations can make unsafe paths appear unreachable. Overly conservative handling rejects useful compiler-generated code.

## Test Signals
The first program succeeds. The second expects failure `R1 !read_ok`.
