# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_const_or.c

## Purpose

`verifier_const_or.c` is a small verifier regression test for scalar constant tracking across bitwise OR operations. It ensures that OR-ing constant registers preserves enough constant information for later bounds checks while not letting a wide constant-derived size bypass stack access validation.

## Important APIs, Types, and Functions

The file includes core BPF helper headers and `bpf_misc.h`. It exposes four `SEC("tracepoint")` naked assembly programs: two success cases where `|=` preserves a constant type, and two failure cases where the resulting constant is used as a helper memory size that exceeds stack bounds. The expected failure diagnostic is `invalid write to stack R1 off=-48 size=58`.

## Control Flow

The success programs build constants with immediate-to-register moves and register-to-register ORs, then return. The negative programs initialize a stack pointer around `fp - 48`, produce a constant 58-byte size through immediate or register OR, and call a helper-style memory access that should be rejected because it would write beyond the verified stack slot.

## State and Persistence Behavior

No persistent runtime state is declared. The meaningful state is verifier scalar metadata: constant value, unknown bits, stack pointer offset, and helper memory-size reasoning. The tests require the verifier to retain constant precision after bitwise OR but still apply the normal stack boundary rules.

## Dependencies and Integration Points

This file integrates with the generic verifier scalar tnum/range engine and stack access validator. It is independent of maps or runtime helpers beyond the verifier's interpretation of helper memory arguments in inline assembly.

## Risks and Test Signals

Risks include scalar precision regressions, treating constants as unknown after OR, or treating constant precision as proof of memory safety without range checking. Test signals are two accepted constant-preservation programs and two rejected oversized stack writes with the same stack-boundary diagnostic.
