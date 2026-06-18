# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_search_pruning.c

## Purpose
`verifier_search_pruning.c` tests verifier state pruning, liveness screening, parent-chain preservation, precision tracking, and bounded search behavior. The fixtures are designed to catch cases where the verifier incorrectly treats two states as equivalent and skips a branch that should still be checked.

## Important APIs, Types, and Functions
The file declares `struct test_val`, `map_hash_48b`, and `map_hash_8b` hash maps. It uses helpers `bpf_map_lookup_elem`, `bpf_ktime_get_ns`, and `bpf_get_prandom_u32`, exact inline assembly, and low-level filter instruction encoding via `BPF_JMP_IMM` for the short-loop stress case. Test annotations include `BPF_F_ANY_ALIGNMENT`, `BPF_F_TEST_STATE_FREQ`, `__failure_unpriv`, `__msg_unpriv`, and log-level matching.

## Control Flow
Pointer/scalar confusion tests merge a stack pointer path with a scalar-loaded map value path and check that privileged and unprivileged return leakage behavior is correct. Branch coverage tests use map values and random helper calls to create pruning points before invalid memory or stack accesses. Precision tests spill 32-bit values and reload them as 32- or 64-bit values so the verifier must avoid assuming stale precision. The final kprobe case builds a small backward loop that should be rejected as too large rather than taking excessive verification time.

## State and Persistence
Persistent state is limited to two hash map definitions used as verifier-visible map-value sources. The important mutable state is verifier abstract state: pointer type versus scalar type, initialized stack bytes, precision marks, branch parent chains, and allocated stack tracking.

## Dependencies and Integration Points
The source integrates with socket, lwt, tracepoint, and kprobe program-type verifier rules. It depends on stack initialization policy differences between privileged and unprivileged modes and on the selftest runner's ability to match failure messages such as `R0 unbounded memory access`, `invalid read from stack`, and `BPF program is too large`.

## Risks and Test Signals
The primary risk is unsound pruning: a verifier bug could accept pointer leaks, skip invalid branches, or lose initialized-stack provenance after partial writes. Performance risk is also covered by the loop test, which guards against unbounded verifier exploration. Strong test signals are explicit expected failures, unprivileged-only failures, processed-instruction counts, forced checkpointing with `BPF_F_TEST_STATE_FREQ`, and branch-specific verifier messages.
