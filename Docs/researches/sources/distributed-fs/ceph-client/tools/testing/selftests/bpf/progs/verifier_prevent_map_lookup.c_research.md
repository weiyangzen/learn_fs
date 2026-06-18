# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_prevent_map_lookup.c

## Purpose
This file ensures `bpf_map_lookup_elem` rejects map types that are not lookup-able through that helper: stack trace maps and program arrays.

## Important APIs, Types, And Functions
It defines `map_stacktrace` as `BPF_MAP_TYPE_STACK_TRACE` and `map_prog2_socket` as `BPF_MAP_TYPE_PROG_ARRAY`, then calls `bpf_map_lookup_elem` on each.

## Control Flow
Each test initializes a zero key on the stack, passes the relevant map pointer to `bpf_map_lookup_elem`, and exits. The helper call itself must be rejected by map type.

## State And Persistence
Maps are static fixtures. Verifier state tracks map type IDs and helper compatibility.

## Dependencies And Integration Points
It integrates with BPF map helper dispatch rules and program-array semantics used for tail calls rather than lookup.

## Risks
Allowing lookup on these map types would violate helper contracts and could expose unsupported kernel data or confuse program-array control-flow assumptions.

## Test Signals
Expected failures are `cannot pass map_type 7 into func bpf_map_lookup_elem` and `cannot pass map_type 3 into func bpf_map_lookup_elem`.
