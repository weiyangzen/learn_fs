# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_or.c

Purpose: validates atomic OR behavior with and without fetch, including source-register preservation without `BPF_FETCH`, old-value return with `BPF_FETCH`, 32-bit operation behavior, and upper-32-bit zeroing.

Important APIs/types/functions: uses `BPF_ATOMIC_OP` with `BPF_OR`, `BPF_OR | BPF_FETCH`, `BPF_DW`, and `BPF_W`; compares with `BPF_JMP_IMM` and `BPF_JMP32_IMM`.

Control flow: the no-fetch test ORs `0x011` into `0x110`, verifies memory becomes `0x111`, and verifies `R1` remains `0x011`. Fetch tests verify `R1` receives old value `0x110`, memory becomes `0x111`, and `R0` is not clobbered. The final test starts with all bits set and ensures a word-sized fetch OR returns `0x00000000ffffffff`.

State and persistence behavior: state is stack-local and register-local. The core verifier/runtime state signal is whether source register clobbering depends on `BPF_FETCH` and whether word atomics zero-extend returned values.

Dependencies and integration points: included in the verifier selftest atomic suite. No map or helper fixups are required.

Risks: JIT back ends can mishandle atomic fetch registers or clobber `R0`; this file explicitly guards that behavior. 32-bit zero-extension mistakes can leak stale high bits.

Test signals: all four entries accept; runtime exit codes distinguish wrong old value, wrong memory result, source clobbering, and `R0` clobbering.
