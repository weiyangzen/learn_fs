# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_movsx.c

## Purpose
This file tests sign-extension move instructions for BPF CPU v4-style semantics, including 8-, 16-, and 32-bit sign extension into 32- and 64-bit destinations and their effect on range analysis.

## Important APIs, Types, And Functions
It uses socket tests with `__success_unpriv`, explicit `__retval`, and inline assembly mnemonics for sign-extension moves. A fallback `dummy_test` is compiled when CPUv4 support is unavailable.

## Control Flow
Initial tests validate concrete sign-extension results. Range-check tests compare sign-extended values to expected signed bounds. Negative cases attempt sign-extending `r10` frame pointer or create problematic variable-offset loop reasoning.

## State And Persistence
No persistent state exists. Verifier state tracks subregister bounds, sign-bit propagation, pointer/scalar separation, var_off, and loop detection after sign extension.

## Dependencies And Integration Points
It depends on compiler/JIT support for the relevant BPF ISA version. It integrates with verifier ALU and pointer-protection logic for sign-extending moves.

## Risks
Incorrect MOVSX semantics can corrupt verifier ranges and permit unsafe pointer arithmetic or reject valid signed-bound code. Sign-extending pointers must stay forbidden.

## Test Signals
Expected signals include precise return values (`0x23`, negative values, `1`, `0`), pointer sign-extension rejection, `infinite loop detected`, and unprivileged diagnostics for pointer handling.
