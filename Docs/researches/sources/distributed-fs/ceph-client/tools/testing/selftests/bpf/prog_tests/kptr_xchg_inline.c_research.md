
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kptr_xchg_inline.c

## Purpose

`kptr_xchg_inline.c` verifies code generation for inline `bpf_kptr_xchg` by inspecting the loaded program instructions.

## Important APIs, Types, and Functions

The test uses `kptr_xchg_inline.skel.h`, `bpf_program__insns()`, `bpf_program__insn_cnt()`, and compares expected `struct bpf_insn` values generated with BPF instruction macros.

## Control Flow and Data Flow

It loads the skeleton, obtains the instruction stream for the relevant program, asserts instruction count/shape, and compares key instructions such as map-value pointer setup and `BPF_ATOMIC_OP(... BPF_XCHG ...)` against expected encodings.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is the libbpf-side loaded instruction array. Dependencies include compiler/codegen stability for the paired BPF source and kptr support. Integration is inline lowering of kptr exchange to atomic xchg instruction form. Risks are brittle instruction-index expectations when compiler output changes. Test signals are exact instruction-count and `memcmp` matches for expected mov/xchg instructions.
