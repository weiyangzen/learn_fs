# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_load_acquire.c

## Purpose
This file verifies BPF load-acquire atomic instruction validation. It confirms supported stack loads for byte, halfword, word, and doubleword widths, then rejects invalid source registers, pointer classes, alignment, and invalid register encodings.

## Important APIs, Types, And Functions
The tests are guarded by `CAN_USE_LOAD_ACQ_STORE_REL`. They emit raw encoded instructions with `__imm_insn(load_acquire_insn, BPF_ATOMIC_OP(... BPF_LOAD_ACQ ...))`. Program types include socket, XDP, flow dissector, and sk_reuseport.

## Control Flow
Positive tests write known values to the stack and use load-acquire to read them back, returning zero on equality. Negative tests attempt load-acquire from unreadable registers, scalars, misaligned stack offsets, context pointers, packet pointers, flow keys, sock pointers, and an invalid register number.

## State And Persistence
No persistent state is used. The relevant state is verifier register type, stack initialization, pointer provenance, access width, and alignment.

## Dependencies And Integration Points
It includes `filter.h` for BPF instruction encoding helpers and depends on architecture/compiler support for load-acquire/store-release. It integrates with verifier atomic memory access checks.

## Risks
Atomic load-acquire incorrectly allowed on packet, context, sock, or flow-key memory would bypass normal helper/prog-type access rules. Incorrect rejection of stack loads would break supported atomic semantics.

## Test Signals
Success cases expect `__retval(0)` including unprivileged success. Rejections assert messages like `!read_ok`, `invalid mem access 'scalar'`, `misaligned stack access`, and `BPF_ATOMIC loads from ... is not allowed`.
