<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_bounds.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_bounds.c

## Purpose
This verifier fragment tests bounds propagation through `BPF_ATOMIC_ADD | BPF_FETCH` from memory to register, ensuring the verifier can prove an apparent infinite loop is unreachable after fetching a known zero.

## Important APIs, Types, And Functions
- The single `struct bpf_test` initializer is named `BPF_ATOMIC bounds propagation, mem->reg`.
- Instructions initialize a stack slot to zero using register store, perform atomic fetch-add of one, branch backward if fetched value is nonzero, and exit.
- Expected privileged result is `ACCEPT`; expected unprivileged result is `REJECT` with log substring `back-edge`.

## Control Flow
At runtime, the fetched old value should be zero, so the `if (b) while(true)` back edge is unreachable. The privileged verifier should propagate bounds precisely enough to accept the program; the unprivileged path rejects due to back-edge policy.

## State And Persistence
State is limited to BPF registers and one stack slot. No maps or external resources are used.

## Dependencies And Integration Points
The fragment is included by verifier generated tests and executed by `test_verifier.c` in privileged and unprivileged modes.

## Risks And Edge Cases
The comment notes that immediate stack stores do not set stack slot type as needed, so changing initialization to a single `BPF_ST_MEM` can invalidate the test. Verifier precision around atomics and loop reachability is the core behavior under test.

## Test Signals
Privileged load should accept and runtime exit zero. Unprivileged load should reject with `back-edge`; a different message or acceptance indicates verifier policy/analysis drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_bounds.c -->
