# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_fetch.c

Purpose: validates atomic fetch operations that both update memory and return the old value into the source register. It covers pointer-leak handling for fetch-and with map pointers and a macro-generated matrix for add, and, or, xor, and xchg fetch semantics across register pairs.

Important APIs/types/functions: key macros are `BPF_LD_MAP_FD`, `BPF_LD_IMM64`, `BPF_STX_MEM`, `BPF_ATOMIC_OP`, `BPF_EMIT_CALL(BPF_FUNC_map_lookup_elem)`, and `__ATOMIC_FETCH_OP_TEST`. It uses map fixups via `.fixup_map_array_48b` and operations `BPF_ADD | BPF_FETCH`, `BPF_AND | BPF_FETCH`, `BPF_OR | BPF_FETCH`, `BPF_XOR | BPF_FETCH`, and `BPF_XCHG`.

Control flow: the first four explicit tests store a map pointer on the stack, atomically mask it with `-1`, retrieve either the stack slot or the returned source register, then attempt to store that value into a map element. The macro-generated tests write an operand to a stack slot, run an atomic fetch op through a selected destination pointer and source register, assert the source register contains the old value, and assert memory contains the expected result.

State and persistence behavior: state is limited to stack slots, register metadata, and harness-created array maps. The important verifier state transition is whether pointer identity survives an atomic fetch and whether unprivileged mode rejects leaking that pointer.

Dependencies and integration points: relies on verifier harness fixups for array maps and on map lookup helper semantics. It is a fragment consumed by the upstream selftest table rather than a standalone C module.

Risks: regressions here usually indicate incorrect source-register clobbering, wrong old-value return semantics, pointer-leak bypasses, or mishandled 32-bit fetch into a 64-bit typed slot. Error-string drift matters because the selftest checks exact verifier diagnostics.

Test signals: privileged 64-bit pointer fetch tests accept while unprivileged mode rejects with `leaking pointer from stack off -8`; 32-bit pointer fetch variants reject with `invalid size of register fill`; all macro-generated arithmetic/bitwise/xchg fetch tests accept with expected old and final values.
