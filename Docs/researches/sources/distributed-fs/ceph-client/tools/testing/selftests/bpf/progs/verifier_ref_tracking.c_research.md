# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_ref_tracking.c

## Purpose
This large suite verifies BPF reference tracking for sockets, sock_common, key references, ringbuf reservations, tail calls, LD_ABS/LD_IND, subprograms, spills, branches, and use-after-release cases.

## Important APIs, Types, And Functions
It defines `BPF_SK_LOOKUP`, kfunc declarations `bpf_key_put`, `bpf_lookup_system_key`, and `bpf_lookup_user_key`, map fixtures (`map_array_48b`, `map_ringbuf`, `map_prog1_tc`), dummy tail-call programs, and many tc/LSM/socket naked tests. Helper families include `bpf_sk_lookup_tcp`, `bpf_skc_lookup_tcp`, `bpf_sk_release`, socket conversion helpers, `bpf_tail_call`, `bpf_ringbuf_reserve`, and `bpf_ringbuf_discard`.

## Control Flow
Tests acquire nullable references, branch on null checks, spill references to stack, copy/zero them, release in same frame or subprograms, leak them over exits or tail calls, try double release, perform LD_ABS/IND with and without held references, access socket members before and after release, and check kfunc key release rules.

## State And Persistence
Maps and program arrays are fixtures. Verifier state is reference IDs, ownership, nullable-to-non-null refinement, stack spill reference metadata, release invalidation, subprogram transfer of ownership, and prohibited operations while refs are live.

## Dependencies And Integration Points
It integrates with socket lookup helpers, key kfunc BTF records, ringbuf reference-like reservation semantics, and tail-call verifier rules. The `__kfunc_btf_root` function ensures BTF FUNC records are emitted for kfunc linking.

## Risks
Reference tracking bugs cause leaks, double frees, use-after-release, or unsafely retained refs across tail calls and packet access instructions. Conversely, false positives can block valid release-in-subprogram patterns.

## Test Signals
Expected logs include `Unreleased reference`, `type=... expected=sock`, `BPF_LD_[ABS|IND] would lead to reference leak`, `tail_call would lead to reference leak`, `pointer arithmetic on sock prohibited`, invalid member access, and success for correctly released references.
